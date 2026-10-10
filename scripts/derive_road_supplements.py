# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "scipy", "scikit-image", "opencv-python-headless", "pillow"]
# ///
"""補充道路推導：作者自己的 worldmap.xml 道路面 → road-supplements/<dataset>.json 候選。

作者的 `worldmap.xml`（遊戲世界地圖 M 鍵畫路用的那份）通常有完整的道路多邊形，只是沒放進
`streets.xml`（導航與路名只讀這份）。本工具把道路多邊形骨架化成中心線，路口處把最直的兩段
接成同一條路，量寬度、對實際路面取樣當證據，寫成 `gen_road_supplements.py` 吃的 JSON。

這是**人工核准前的候選**：跑完要看 `--preview` 疊圖，確認路線貼著實際道路才 `--write`
並 commit。之後由 `gen_road_supplements.py gen` 編譯成遊戲讀的檔案。

    uv run scripts/derive_road_supplements.py constown --workshop-id 3480990544 \\
        --map-mod Constown42 --map-dir "Constown, KY" \\
        --label-en Constown --label-ch 康斯鎮 --label-cn 康斯镇 --label-jp コンスタウン \\
        --preview output/constown-roads.png            # 先看疊圖
    uv run scripts/derive_road_supplements.py constown --write   # 既有 JSON：沿用 source／label／號碼

重跑時沿用既有號碼：新推導的路與舊路幾何重疊就用舊號碼，沒對上的舊號碼記進 retired
（不再重用），新路接在最大號碼後面。
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from datetime import date
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_road_supplements as grs  # noqa: E402
import gen_streets_i18n as gsi  # noqa: E402

PROJECT_ROOT = grs.PROJECT_ROOT
DEFAULT_PZMAP = PROJECT_ROOT.parent / "MinidoracatMapRendering" / "target" / "release" / "pzmap.exe"
DEFAULT_GAME = Path(r"D:\SteamLibrary\steamapps\common\ProjectZomboid")
MINIMAP_REL = grs.MEDIA_REL / "minimap"
METHOD = "worldmap-highway-skeleton-v1"

SPUR_MIN = 12.0        # 死路短枝（車道、停車位口）短於此長度就剪
STRAIGHT_MAX_DEG = 35  # 路口兩段方向差在此角度內才接成同一條路
DP_EPSILON = 1.0       # 折線簡化容差（格）
ROW_BAND = 40          # 編號：由北到南分列、列內由西到東
# 原版校準（Muldraugh 市區 72 條街）：多邊形量到的寬度 ≈ streets.xml width + 2
WIDTH_OFFSET = 2
ON_ROAD_CLASSES = {"paved", "gravel", "dirt-edge"}
MATCH_DIST = 3.0       # 重跑沿用號碼：新路取樣點落在舊路此距離內的比例
MATCH_RATIO = 0.6


# ============================================================
# 上游定位
# ============================================================
def find_map_dir(roots: list[Path], wid: str, map_dir: str) -> Path | None:
    """有 lotheader 的地圖目錄；版本資料夾優先於 common（同 find_streets_xml）。"""
    for root in roots:
        base = root / wid / "mods"
        if not base.is_dir():
            continue
        for mod in sorted(p for p in base.iterdir() if p.is_dir()):
            buckets = sorted((p for p in mod.iterdir() if p.is_dir()),
                             key=lambda p: (0 if gsi._VERSION_DIR_RE.match(p.name) else 1, p.name))
            for bucket in buckets:
                cand = bucket / "media" / "maps" / map_dir
                if any(cand.glob("*.lotheader")):
                    return cand
    return None


def lot_bounds(map_path: Path) -> tuple[int, int, int, int]:
    cells = [tuple(map(int, p.stem.split("_"))) for p in map_path.glob("*.lotheader")]
    xs, ys = [c[0] for c in cells], [c[1] for c in cells]
    return min(xs) * 256, min(ys) * 256, (max(xs) + 1) * 256, (max(ys) + 1) * 256


def street_count(xml_path: Path | None) -> int:
    return 0 if xml_path is None else len(ET.parse(xml_path).getroot().findall("street"))


# ============================================================
# 道路面與路面證據
# ============================================================
def highway_mask(wm_path: Path, bounds: tuple[int, int, int, int], exclude: set[str]) -> np.ndarray:
    """worldmap.xml 的 highway 多邊形 → 布林遮罩。cell 大小（B41 300／B42 256）以哪種
    換算後與 lotheader 範圍重疊最多決定。每個 feature 內多個環以 even-odd 疊（洞＝街區）。"""
    x0, y0, x1, y1 = bounds
    root = ET.parse(wm_path).getroot()
    cells = root.findall("cell")

    def overlap(cs: int) -> int:
        xs = [int(c.get("x")) * cs for c in cells]
        ys = [int(c.get("y")) * cs for c in cells]
        return max(0, min(max(xs) + cs, x1) - max(min(xs), x0)) * max(0, min(max(ys) + cs, y1) - max(min(ys), y0))

    cs = max((300, 256), key=overlap)
    mask = np.zeros((y1 - y0, x1 - x0), np.uint8)
    for cell in cells:
        cx, cy = int(cell.get("x")) * cs - x0, int(cell.get("y")) * cs - y0
        for f in cell.findall("feature"):
            props = {p.get("name"): p.get("value") for p in f.iter("property")}
            kind = props.get("highway")
            if kind is None or kind in exclude:
                continue
            feat = np.zeros_like(mask)
            for ring in f.find("geometry").findall("coordinates"):
                pts = np.array([[cx + float(p.get("x")), cy + float(p.get("y"))] for p in ring.findall("point")])
                if len(pts) < 3:
                    continue
                m = np.zeros_like(mask)
                cv2.fillPoly(m, [np.round(pts).astype(np.int32)], 1)
                feat ^= m
            mask |= feat
    return mask.astype(bool)


def road_surfaces(pzmap: Path, game: Path, mod_root: Path, map_dir: str,
                  bounds: tuple[int, int, int, int]) -> tuple[np.ndarray, list[str]]:
    """MapRendering `pzmap road-surfaces` → 每格路面類別 raster（證據用）。"""
    x0, y0, x1, y1 = bounds
    region = f"{x0 // 256},{y0 // 256},{x1 // 256 - 1},{y1 // 256 - 1}"
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "surfaces.json"
        subprocess.run([str(pzmap), "road-surfaces", "--game", str(game), "--pz-build", "42.20.4",
                        "--mod", str(mod_root), "--map", map_dir, "--region", region, "--out", str(out)],
                       check=True, capture_output=True, text=True)
        data = json.loads(out.read_text(encoding="utf-8"))
    raster = np.full((y1 - y0, x1 - x0), 255, np.uint8)
    for c in data["cells"]:
        flat = np.empty(65536, np.uint8)
        for start, length, cls in c["runs"]:
            flat[start:start + length] = cls
        oy, ox = c["y"] * 256 - y0, c["x"] * 256 - x0
        raster[oy:oy + 256, ox:ox + 256] = flat.reshape(256, 256)
    return raster, data["classes"]


# ============================================================
# 骨架 → 路段圖 → 道路
# ============================================================
_NBRS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def skeleton_edges(mask: np.ndarray) -> list[dict]:
    """骨架化後拆成「節點（端點／路口像素群）之間」的像素路徑。"""
    sk = skeletonize(mask)
    deg = ndi.convolve(sk.astype(np.uint8), np.ones((3, 3), np.uint8), mode="constant") - sk
    node = sk & (deg != 2)
    labels, _n = ndi.label(node, structure=np.ones((3, 3)))
    h, w = sk.shape
    visited = np.zeros_like(sk, bool)
    edges: list[dict] = []

    def trace(start: tuple[int, int], first: tuple[int, int]) -> list[tuple[int, int]]:
        path = [start, first]
        prev, cur = start, first
        while not node[cur]:
            visited[cur] = True
            nxt = None
            for dy, dx in _NBRS:
                y, x = cur[0] + dy, cur[1] + dx
                if 0 <= y < h and 0 <= x < w and sk[y, x] and (y, x) != prev and (y, x) not in path[-3:]:
                    if node[y, x] or not visited[y, x]:
                        nxt = (y, x)
                        if node[y, x]:
                            break
            if nxt is None:
                break
            prev, cur = cur, nxt
            path.append(cur)
        return path

    for y, x in zip(*np.nonzero(node)):
        for dy, dx in _NBRS:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and sk[ny, nx] and not node[ny, nx] and not visited[ny, nx]:
                path = trace((y, x), (ny, nx))
                a, b = path[0], path[-1]
                edges.append({"pts": path, "na": int(labels[a]), "nb": int(labels[b]) if node[b] else 0})
    return edges


def _length(pts: list[tuple[int, int]]) -> float:
    return sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))


def prune_spurs(edges: list[dict]) -> list[dict]:
    # 路口像素群內部的極短自環（骨架在路口打結）先丟，免得被接進道路變成折返
    edges = [e for e in edges if not (e["na"] == e["nb"] and _length(e["pts"]) < SPUR_MIN)]
    while True:
        inc: dict[int, int] = {}
        for e in edges:
            inc[e["na"]] = inc.get(e["na"], 0) + 1
            inc[e["nb"]] = inc.get(e["nb"], 0) + 1
        keep = [e for e in edges
                if not (_length(e["pts"]) < SPUR_MIN and (inc[e["na"]] == 1 or inc[e["nb"]] == 1 or e["nb"] == 0)
                        and not (inc[e["na"]] == 1 and inc[e["nb"]] == 1))]
        if len(keep) == len(edges):
            return edges
        edges = keep


def _direction(pts: list[tuple[int, int]], at_start: bool) -> tuple[float, float]:
    k = min(8, len(pts) - 1)
    a, b = (pts[0], pts[k]) if at_start else (pts[-1], pts[-1 - k])
    dy, dx = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def chain_roads(edges: list[dict]) -> list[list[tuple[int, int]]]:
    """路口處把方向最直的兩段接起來（偏差 <= STRAIGHT_MAX_DEG），得到一條條道路的像素路徑。"""
    ends: dict[int, list[tuple[int, bool]]] = {}
    for i, e in enumerate(edges):
        ends.setdefault(e["na"], []).append((i, True))
        if e["nb"]:
            ends.setdefault(e["nb"], []).append((i, False))
    pair: dict[tuple[int, bool], tuple[int, bool]] = {}
    limit = math.cos(math.radians(180 - STRAIGHT_MAX_DEG))
    for n in sorted(ends):
        items = ends[n]
        cands = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i][0] == items[j][0]:
                    continue
                da = _direction(edges[items[i][0]]["pts"], items[i][1])
                db = _direction(edges[items[j][0]]["pts"], items[j][1])
                dot = da[0] * db[0] + da[1] * db[1]
                if dot <= limit:  # 夾角接近 180°＝直行
                    cands.append((dot, items[i], items[j]))
        for _dot, a, b in sorted(cands):
            if a not in pair and b not in pair:
                pair[a], pair[b] = b, a
        # 路口間的極短碎段（骨架在相鄰路口間留下的幾格）不該自成一條要取名的路：
        # 不論角度，併進該路口剩下最順的一端
        for a in items:
            if a in pair or _length(edges[a[0]]["pts"]) >= SPUR_MIN:
                continue
            da = _direction(edges[a[0]]["pts"], a[1])
            rest = [(da[0] * db[0] + da[1] * db[1], b) for b in items
                    if b not in pair and b[0] != a[0]
                    for db in [_direction(edges[b[0]]["pts"], b[1])]]
            if rest:
                b = min(rest)[1]
                pair[a], pair[b] = b, a
    used = [False] * len(edges)
    roads: list[list[tuple[int, int]]] = []

    def walk(i: int, from_start: bool) -> list[tuple[int, int]]:
        path: list[tuple[int, int]] = []
        while True:
            used[i] = True
            pts = edges[i]["pts"] if from_start else edges[i]["pts"][::-1]
            path.extend(pts if not path else pts[1:])
            nxt = pair.get((i, not from_start))
            if nxt is None or used[nxt[0]]:
                return path
            i, from_start = nxt[0], nxt[1]

    for i in range(len(edges)):
        if used[i]:
            continue
        # 從鏈的一端開始走：先往回找到沒有接續的那一端
        j, start = i, True
        seen = {i}
        while (j, start) in pair and pair[(j, start)][0] not in seen:
            k, kstart = pair[(j, start)]
            seen.add(k)
            j, start = k, not kstart
        roads.append(walk(j, start))
    return roads


def to_world(path: list[tuple[int, int]], x0: int, y0: int) -> list[float]:
    arr = np.array([[x, y] for y, x in path], np.float32).reshape(-1, 1, 2)
    simp = cv2.approxPolyDP(arr, DP_EPSILON, False).reshape(-1, 2)
    return [float(v) for x, y in simp for v in (x0 + x + 0.5, y0 + y + 0.5)]


def samples(flat: list[float]) -> list[tuple[float, float]]:
    out = []
    for i in range(0, len(flat) - 2, 2):
        a, b = (flat[i], flat[i + 1]), (flat[i + 2], flat[i + 3])
        n = max(1, int(math.dist(a, b)))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    out.append((flat[-2], flat[-1]))
    return out


def split_points(flat: list[float]) -> list[list[float]]:
    """超過 native 點數上限就切段（共用切點）；實務上 DP 後很少發生。"""
    cap = grs.gsr.MAX_REPLACEMENT_POINTS
    pts = [flat[i:i + 2] for i in range(0, len(flat), 2)]
    if len(pts) <= cap:
        return [flat]
    out = []
    for s in range(0, len(pts) - 1, cap - 1):
        chunk = pts[s:s + cap]
        out.append([v for p in chunk for v in p])
    return out


# ============================================================
# 號碼
# ============================================================
def _dist_to(flat: list[float], x: float, y: float) -> float:
    return grs.gsr.point_polyline_distance(x, y, flat)


def assign_numbers(roads: list[list[float]], old: dict | None) -> tuple[list[int], list[int]]:
    """→ (每條路的號碼, retired)。重疊舊路沿用號碼；新路接在最大號碼後；對不上的舊號退役。"""
    old_roads = {r["no"]: r["points"] for r in (old or {}).get("roads", [])}
    retired = set((old or {}).get("retired", []))
    nos: list[int | None] = [None] * len(roads)
    taken: set[int] = set()
    for i, flat in enumerate(roads):
        best = None
        for no, prev in sorted(old_roads.items()):
            if no in taken:
                continue
            s = samples(flat)
            ratio = sum(_dist_to(prev, x, y) <= MATCH_DIST for x, y in s) / len(s)
            back = samples(prev)
            ratio_back = sum(_dist_to(flat, x, y) <= MATCH_DIST for x, y in back) / len(back)
            score = min(ratio, ratio_back)
            if score >= MATCH_RATIO and (best is None or score > best[0]):
                best = (score, no)
        if best:
            nos[i] = best[1]
            taken.add(best[1])
    nxt = max([0, *old_roads, *retired]) + 1

    def order(i: int) -> tuple[int, float]:
        s = samples(roads[i])
        mx, my = s[len(s) // 2]
        return round(my / ROW_BAND), mx

    for i in sorted((i for i in range(len(roads)) if nos[i] is None), key=order):
        nos[i] = nxt
        nxt += 1
    retired |= set(old_roads) - taken
    return [int(n) for n in nos], sorted(retired)


# ============================================================
# 預覽
# ============================================================
def preview(path: Path, roads: list[tuple[int, list[float]]], bounds: tuple[int, int, int, int],
            dataset_zip: Path | None, mask: np.ndarray) -> None:
    x0, y0, x1, y1 = bounds
    if dataset_zip and dataset_zip.is_file():
        z = zipfile.ZipFile(dataset_zip)
        meta = dict(l.split("=", 1) for l in z.read("pyramid.txt").decode().splitlines() if "=" in l)
        bx, by, _, _ = map(int, meta["bounds"].split())
        im = Image.new("RGB", (x1 - x0, y1 - y0))
        for name in z.namelist():
            if name.startswith("0/tile"):
                tx, ty = map(int, name[6:-4].split("x"))
                im.paste(Image.open(io.BytesIO(z.read(name))).convert("RGB"), (bx + tx * 256 - x0, by + ty * 256 - y0))
    else:
        im = Image.fromarray((mask * 120).astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(im)
    for no, flat in roads:
        d.line([(flat[i] - x0, flat[i + 1] - y0) for i in range(0, len(flat), 2)], fill=(0, 255, 255), width=2)
        d.text((flat[0] - x0 + 2, flat[1] - y0 + 2), f"{no:02d}", fill=(255, 255, 0))
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


def registry_zip(map_mod: str, map_dir: str) -> Path | None:
    text = (PROJECT_ROOT / grs.REGISTRY_REL).read_text(encoding="utf-8")
    for line in text.splitlines():
        if f"mapMod = {gsi._lua_str(map_mod)}" in line and 'zip = "' in line:  # 註冊表非 ASCII 寫成 \ddd
            name = line.split('zip = "', 1)[1].split('"', 1)[0]
            return PROJECT_ROOT / MINIMAP_REL / name
    cand = PROJECT_ROOT / MINIMAP_REL / f"{map_dir}.pyramid.zip"
    return cand if cand.is_file() else None


# ============================================================
# 主流程
# ============================================================
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset")
    ap.add_argument("--workshop-id")
    ap.add_argument("--map-mod")
    ap.add_argument("--map-dir")
    for lang in grs.LANGS:
        ap.add_argument(f"--label-{lang}")
    ap.add_argument("--prefer", action="append", default=[], help="額外 workshop content 根（可重複）")
    ap.add_argument("--pzmap", default=str(DEFAULT_PZMAP))
    ap.add_argument("--game", default=str(DEFAULT_GAME))
    ap.add_argument("--exclude-kind", action="append", default=["trail"],
                    help="不推導的 highway 種類（預設 trail：土徑路面訊號弱，證據門檻過不了）")
    ap.add_argument("--preview", help="輸出疊圖 PNG（核准前必看）")
    ap.add_argument("--write", action="store_true", help=f"寫入 {grs.SUPPLEMENTS_DIR_NAME}/<dataset>.json")
    args = ap.parse_args(argv)

    out_path = PROJECT_ROOT / grs.SUPPLEMENTS_DIR_NAME / f"{args.dataset}.json"
    old = json.loads(out_path.read_text(encoding="utf-8")) if out_path.is_file() else None
    src_old = (old or {}).get("source", {})
    wid = args.workshop_id or src_old.get("workshop_id")
    map_mod = args.map_mod or src_old.get("map_mod")
    map_dir = args.map_dir or src_old.get("map_dir")
    label = {lang: getattr(args, f"label_{lang}") or (old or {}).get("label", {}).get(lang) for lang in grs.LANGS}
    missing = [k for k, v in {"--workshop-id": wid, "--map-mod": map_mod, "--map-dir": map_dir,
                              **{f"--label-{k}": v for k, v in label.items()}}.items() if not v]
    if missing:
        print(f"❌ 新 dataset 需要：{' '.join(missing)}", file=sys.stderr)
        return 2

    roots = gsi.iter_workshop_roots(args.prefer)
    map_path = find_map_dir(roots, wid, map_dir)
    if map_path is None:
        print(f"❌ 找不到本機上游 {wid}/{map_dir}（--prefer 指向 steamcmd content 根）", file=sys.stderr)
        return 1
    wm_path = map_path / "worldmap.xml"
    if not wm_path.is_file():
        print(f"❌ {map_path} 沒有 worldmap.xml，無從推導", file=sys.stderr)
        return 1
    streets_path = map_path / "streets.xml"
    streets_path = streets_path if streets_path.is_file() else None
    bounds = lot_bounds(map_path)
    x0, y0 = bounds[0], bounds[1]

    mask = highway_mask(wm_path, bounds, set(args.exclude_kind))
    if streets_path is not None:
        # 作者已有的街不重複補：扣掉其路寬＋2 格範圍，接點交給導航吸附
        cover = np.zeros(mask.shape, np.uint8)
        for st in ET.parse(streets_path).getroot().findall("street"):
            pts = np.array([[float(p.get("x")) - x0, float(p.get("y")) - y0] for p in st.iter("point")])
            if len(pts) >= 2:
                cv2.polylines(cover, [np.round(pts).astype(np.int32)], False, 1,
                              thickness=max(1, int(round(float(st.get("width") or 5) + 4))))
        mask &= ~cover.astype(bool)
    dist = ndi.distance_transform_edt(mask)
    edges = prune_spurs(skeleton_edges(mask))
    paths = chain_roads(edges)

    mod_root = map_path.parents[3] if map_path.parents[2].name.lower() in {"common"} or \
        gsi._VERSION_DIR_RE.match(map_path.parents[2].name) else map_path.parents[2]
    raster, classes = road_surfaces(Path(args.pzmap), Path(args.game), mod_root, map_dir, bounds)
    on_ids = {classes.index(c) for c in ON_ROAD_CLASSES}

    roads: list[tuple[list[float], float, int, int]] = []
    dropped = []
    for path in paths:
        # 路口殘渣（幾格長、兩端都在路口裡）不取名：導航吸附容差本來就會把兩側接起來
        if len(path) < 2 or _length(path) < SPUR_MIN / 2:
            continue
        widths = [dist[y, x] * 2 for y, x in path]
        width = float(max(3, min(20, int(round(float(np.median(widths)))) - WIDTH_OFFSET)))
        for flat in split_points(to_world(path, x0, y0)):
            if len(flat) < 4:
                continue
            s = samples(flat)
            on = sum(1 for x, y in s if raster[int(y - y0), int(x - x0)] in on_ids)
            if on / len(s) < grs.MIN_ON_ROAD:
                dropped.append((round(on / len(s), 2), flat[:2], len(s)))
                continue
            roads.append((flat, width, len(s), on))
    nos, retired = assign_numbers([r[0] for r in roads], old)

    doc = {
        "dataset": args.dataset,
        "schemaVersion": grs.SCHEMA_VERSION,
        "source": {
            "workshop_id": wid,
            "map_mod": map_mod,
            "map_dir": map_dir,
            "streets_xml_sha256": gsi.file_sha256(streets_path) if streets_path else None,
            "upstream_street_count": street_count(streets_path),
            "worldmap_xml_sha256": gsi.file_sha256(wm_path),
            "captured": date.today().isoformat(),
            "method": METHOD,
        },
        "label": label,
        "roads": [
            {"no": no, "width": int(w) if float(w).is_integer() else w, "points": [
                int(v) if float(v).is_integer() else v for v in flat],
             "evidence": {"samples": n, "on_road": on}}
            for no, (flat, w, n, on) in sorted(zip(nos, roads), key=lambda t: t[0])
        ],
        "retired": retired,
    }
    total = sum(r[2] for r in roads)
    print(f"{args.dataset}: {len(roads)} 條道路、約 {total} 格、中線落在路面 "
          f"{sum(r[3] for r in roads) / max(total, 1):.1%}；剔除 {len(dropped)} 段（路面證據不足）")
    for ratio, head, n in dropped:
        print(f"   剔除 起點 ({head[0]:.1f},{head[1]:.1f}) 取樣 {n} 路面 {ratio:.0%}")
    if retired:
        print(f"   退役號碼：{retired}")
    if args.preview:
        preview(Path(args.preview), [(no, r[0]) for no, r in zip(nos, roads)], bounds,
                registry_zip(map_mod, map_dir), mask)
        print(f"   疊圖：{args.preview}")
    if args.write:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"✅ 寫入 {out_path.relative_to(PROJECT_ROOT)}（下一步：gen_road_supplements.py gen → verify）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
