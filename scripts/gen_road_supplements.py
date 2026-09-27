#!/usr/bin/env python3
"""補充道路（street supplements）生成器：road-supplements/*.json → 遊戲讀的三份生成物。

作者沒放進 `streets.xml` 的路（整張圖都沒有道路資料，或只缺幾區）由本包補上，讓小地圖
能顯示路名、搜尋，導航與自動駕駛也能走。與另外兩條資料線分開：

- `gen_streets_i18n.py`：作者原路名 → 翻譯。不碰幾何。
- `gen_street_repairs.py`：修正作者已有的街（依 XML 序號比對原點列）。不新增路。
- 本檔：新增作者沒有的路。路名是我們取的，明確標示「小地圖補」，作者更新就退場。

## 資料來源

`road-supplements/<dataset>.json`（schema 見 `load_supplement`）由
`scripts/derive_road_supplements.py` 從作者自己的 `worldmap.xml` 道路面推導、人工看過
疊圖後寫入。本檔**只編譯**，不推導、不讀上游幾何；上游只拿來回報漂移。

## 生成物

1. `42/media/minimap/streets/<dataset>.xml`：與 `streets.xml` 同格式，路名是英文原名。
   主 MOD 在該地圖目錄載入時用 `addStreetData` 掛進地圖（顯示、hover、搜尋、導航共用）。
2. `42/media/lua/shared/MinidoracatMiniMapModMapsStreetSupplements.lua`：每個 dataset 的
   `{ schemaVersion, mapMod, mapDir, file, upstreamStreetCount, roadCount, names }`，
   註冊清單以 `streetSupplement = StreetSupplements["<dataset>"]` 引用。
3. 四語 `UI.json` 的 `UI_MinidoracatMiniMapModMaps_Road_<dataset>_<NN>` 鍵。

路名格式（使用者 2026-09-27 選定）：EN `Constown Rd 07 (MiniMap)`、CH `康斯鎮 07 號路（小地圖補）`、
CN `康斯镇 07 号路（小地图补）`、JP `コンスタウン 07号線（ミニマップ補完）`。號碼一經發出就固定，
路被移除時記進 `retired`，不再重用——玩家記住的「07 號路」不能換成另一條。

## 作者更新時自動退場

`source.upstream_street_count` 是推導當時該地圖 `streets.xml` 的街道數（沒有檔案＝0）。
主 MOD 執行期數到的數目不同就整份停用，改回作者資料。數目相同但內容改了抓不到，
由追蹤器比對 sha256 開 issue（`source.streets_xml_sha256`／`worldmap_xml_sha256`）。

## 用法

    python scripts/gen_road_supplements.py gen        # 產生三份生成物
    python scripts/gen_road_supplements.py verify     # 驗 schema ＋ 生成物同步 ＋ 上游漂移（只警告）
    python scripts/gen_road_supplements.py --selftest # 零外部依賴自我測試
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple
from xml.sax.saxutils import quoteattr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_streets_i18n as gsi  # noqa: E402  只取純 helper：import 本身無副作用
import gen_street_repairs as gsr  # noqa: E402  float32／點數上限與修正線同一套規則

PROJECT_ROOT = gsi.PROJECT_ROOT
Result = gsi.Result

SUPPLEMENTS_DIR_NAME = "road-supplements"
SCHEMA_VERSION = 1
# 全域表名沿用 MinidoracatMiniMapModMaps 前綴（沒有 For42 尾綴）：與註冊清單、主 MOD 的接線契約
TABLE_GLOBAL = "MinidoracatMiniMapModMapsStreetSupplements"
TABLE_REL = gsi.STREET_TABLE_REL.with_name(f"{TABLE_GLOBAL}.lua")
MEDIA_REL = gsi.STREET_TABLE_REL.parents[2]  # .../42/media
XML_DIR_REL = MEDIA_REL / "minimap" / "streets"
REGISTRY_REL = gsi.REGISTRY_REL
# 本生成器獨佔的 UI 鍵命名空間。gen_streets_i18n 每次把 `_Street_` 鍵整批移到檔尾，
# 本檔把 `_Road_` 鍵插在 `_Street_` 區塊之前——兩支各自的輸出都不會打亂對方（不互相乒乓）
UI_KEY_PREFIX = "UI_MinidoracatMiniMapModMaps_Road_"
LANGS = ("en", "ch", "cn", "jp")
UI_LANG = {"EN": "en", "CH": "ch", "CN": "cn", "JP": "jp"}
MIN_ON_ROAD = 0.9  # 每條路中線取樣至少九成落在實際路面：推導錯的路不准出貨
MAX_WIDTH = 64.0
MAX_NO = 999

_DATASET_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_REGISTRY_RE = re.compile(r'streetSupplement\s*=\s*[\w.]+\s*\[\s*"([^"]+)"\s*\]')


def runtime_file(dataset: str) -> str:
    """主 MOD `addStreetData` 用的相對路徑（MOD 內 42/ 之下）。"""
    return f"media/minimap/streets/{dataset}.xml"


def ui_key(dataset: str, no: int) -> str:
    return f"{UI_KEY_PREFIX}{dataset}_{no:02d}"


def road_name(label: dict[str, str], no: int, lang: str) -> str:
    """路名唯一格式來源（生成物、公開清單都用這支）。"""
    n = f"{no:02d}"
    if lang == "en":
        return f"{label['en']} Rd {n} (MiniMap)"
    if lang == "ch":
        return f"{label['ch']} {n} 號路（小地圖補）"
    if lang == "cn":
        return f"{label['cn']} {n} 号路（小地图补）"
    if lang == "jp":
        return f"{label['jp']} {n}号線（ミニマップ補完）"
    raise ValueError(lang)


class Road(NamedTuple):
    no: int
    width: float
    points: list[float]


class Supplement(NamedTuple):
    dataset: str
    workshop_id: str
    map_mod: str
    map_dir: str
    streets_sha: str | None
    upstream_count: int
    worldmap_sha: str | None
    label: dict[str, str]
    roads: list[Road]
    retired: list[int]


# ============================================================
# 讀取與驗證
# ============================================================
def _str(errors: list[str], where: str, val: object) -> str | None:
    if not isinstance(val, str) or not val.strip() or any(ord(c) < 0x20 for c in val):
        errors.append(f"{where} 必須是非空、無控制字元的字串")
        return None
    return val


def _sha(errors: list[str], where: str, val: object) -> str | None:
    if val is None:
        return None
    if not isinstance(val, str) or not _SHA_RE.match(val):
        errors.append(f"{where} 必須是 64 位小寫 hex 或 null")
    return val if isinstance(val, str) else None


def _count(errors: list[str], where: str, val: object, lo: int, hi: int) -> int | None:
    if isinstance(val, bool) or not isinstance(val, int) or not lo <= val <= hi:
        errors.append(f"{where} 必須是 {lo}–{hi} 的整數（得到 {val!r}）")
        return None
    return val


def _road(errors: list[str], where: str, raw: object) -> Road | None:
    if not isinstance(raw, dict):
        errors.append(f"{where} 必須是物件")
        return None
    unknown = sorted(set(raw) - {"no", "width", "points", "evidence"})
    if unknown:
        errors.append(f"{where} 有未知欄位 {unknown}")
    no = _count(errors, f"{where}.no", raw.get("no"), 1, MAX_NO)
    width = gsr._num(errors, f"{where}.width", raw.get("width"), positive=True)
    if width is not None and width > MAX_WIDTH:
        errors.append(f"{where}.width {width:g} 超過 {MAX_WIDTH:g}")
    pts = gsr._flat_points(errors, f"{where}.points", raw.get("points"))
    if pts is not None:
        if len(pts) // 2 > gsr.MAX_REPLACEMENT_POINTS:
            errors.append(f"{where}.points {len(pts) // 2} 點超過 native buffer 上限 {gsr.MAX_REPLACEMENT_POINTS}")
        if not any(pts[i] != pts[i + 2] or pts[i + 1] != pts[i + 3] for i in range(0, len(pts) - 2, 2)):
            errors.append(f"{where}.points 沒有任何非零長度的路段")
        if any(v < 0 or v > 100000 for v in pts):
            errors.append(f"{where}.points 超出世界座標範圍")
    ev = raw.get("evidence")
    if not isinstance(ev, dict):
        errors.append(f"{where}.evidence 必填（中線取樣與落在路面的數量）")
    else:
        samples = _count(errors, f"{where}.evidence.samples", ev.get("samples"), 1, 10**7)
        on_road = _count(errors, f"{where}.evidence.on_road", ev.get("on_road"), 0, 10**7)
        if samples and on_road is not None:
            if on_road > samples:
                errors.append(f"{where}.evidence.on_road 大於 samples")
            elif on_road / samples < MIN_ON_ROAD:
                errors.append(
                    f"{where} 中線只有 {on_road}/{samples} 落在路面（下限 {MIN_ON_ROAD:.0%}）"
                )
    if no is None or width is None or pts is None:
        return None
    return Road(no, width, pts)


def load_supplement(path: Path) -> tuple[Supplement | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        return None, [f"{path.name} 讀取失敗：{e}"], warnings
    if not isinstance(data, dict):
        return None, [f"{path.name} 頂層必須是物件"], warnings
    ds = data.get("dataset")
    if not isinstance(ds, str) or not _DATASET_RE.match(ds) or ds != path.stem:
        errors.append(f"{path.name} dataset 必須是小寫英數連字號且等於檔名")
        ds = path.stem
    if data.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"{path.name} schemaVersion 必須是 {SCHEMA_VERSION}")
    src = data.get("source") if isinstance(data.get("source"), dict) else {}
    if not src:
        errors.append(f"{path.name} 缺 source")
    wid = _str(errors, f"{path.name} source.workshop_id", src.get("workshop_id"))
    if wid is not None and not wid.isdigit():
        errors.append(f"{path.name} source.workshop_id 必須是數字字串")
    map_mod = _str(errors, f"{path.name} source.map_mod", src.get("map_mod"))
    map_dir = _str(errors, f"{path.name} source.map_dir", src.get("map_dir"))
    streets_sha = _sha(errors, f"{path.name} source.streets_xml_sha256", src.get("streets_xml_sha256"))
    upstream = _count(errors, f"{path.name} source.upstream_street_count",
                      src.get("upstream_street_count"), 0, 65535)
    if upstream is not None and (upstream == 0) != (src.get("streets_xml_sha256") is None):
        errors.append(f"{path.name} source.upstream_street_count 為 0 ⇔ streets_xml_sha256 為 null（作者沒有道路資料）")
    worldmap_sha = _sha(errors, f"{path.name} source.worldmap_xml_sha256", src.get("worldmap_xml_sha256"))
    label_raw = data.get("label") if isinstance(data.get("label"), dict) else {}
    label: dict[str, str] = {}
    for lang in LANGS:
        v = _str(errors, f"{path.name} label.{lang}", label_raw.get(lang))
        if v is not None:
            label[lang] = v
    retired_raw = data.get("retired", [])
    retired: list[int] = []
    if not isinstance(retired_raw, list):
        errors.append(f"{path.name} retired 必須是陣列")
    else:
        for i, n in enumerate(retired_raw):
            v = _count(errors, f"{path.name} retired[{i}]", n, 1, MAX_NO)
            if v is not None:
                retired.append(v)
    raw_roads = data.get("roads")
    if not isinstance(raw_roads, list) or not raw_roads:
        errors.append(f"{path.name} roads 必須是非空陣列")
        raw_roads = []
    roads: list[Road] = []
    seen: set[int] = set()
    for i, raw in enumerate(raw_roads):
        road = _road(errors, f"{path.name} roads[{i}]", raw)
        if road is None:
            continue
        if road.no in seen:
            errors.append(f"{path.name} roads[{i}].no={road.no} 重複")
        elif road.no in retired:
            errors.append(f"{path.name} roads[{i}].no={road.no} 已退役，號碼不得重用")
        seen.add(road.no)
        roads.append(road)
    if errors:
        return None, errors, warnings
    return (
        Supplement(ds, wid, map_mod, map_dir, streets_sha, upstream, worldmap_sha, label,
                   sorted(roads, key=lambda r: r.no), sorted(set(retired))),
        errors,
        warnings,
    )


def load_all(project_root: Path) -> tuple[dict[str, Supplement], list[str], list[str]]:
    out: dict[str, Supplement] = {}
    errors: list[str] = []
    warnings: list[str] = []
    for f in sorted((project_root / SUPPLEMENTS_DIR_NAME).glob("*.json")):
        sup, errs, warns = load_supplement(f)
        errors.extend(errs)
        warnings.extend(warns)
        if sup is not None:
            out[sup.dataset] = sup
    reg = project_root / REGISTRY_REL
    if not reg.is_file():
        errors.append(f"缺註冊清單 {REGISTRY_REL}")
    else:
        refs = _REGISTRY_RE.findall(reg.read_text(encoding="utf-8"))
        errors += [f"註冊清單引用 streetSupplement[{d!r}]，但缺 {SUPPLEMENTS_DIR_NAME}/{d}.json"
                   for d in refs if d not in out]
        warnings += [f"{d} 有補充道路但註冊清單未引用 streetSupplement（不會生效）"
                     for d in sorted(out) if d not in refs]
    return out, errors, warnings


# ============================================================
# 生成
# ============================================================
def _fmt(v: float) -> str:
    return f"{v:.1f}" if float(v).is_integer() else repr(float(v))


def render_xml(sup: Supplement) -> bytes:
    lines = ['<streets version="1">']
    for r in sup.roads:
        width = str(int(r.width)) if float(r.width).is_integer() else repr(float(r.width))
        lines.append(f"    <street name={quoteattr(road_name(sup.label, r.no, 'en'))} width=\"{width}\">")
        lines.append("        <points>")
        for i in range(0, len(r.points), 2):
            lines.append(f'            <point x="{_fmt(r.points[i])}" y="{_fmt(r.points[i + 1])}"/>')
        lines.append("        </points>")
        lines.append("    </street>")
    lines.append("</streets>")
    return ("\n".join(lines) + "\n").encode("utf-8")


def render_table(sups: dict[str, Supplement]) -> bytes:
    s = gsi._lua_str
    lines = [
        f"-- {TABLE_REL.name}（生成檔，勿手編）",
        f"-- 由 scripts/gen_road_supplements.py 從 {SUPPLEMENTS_DIR_NAME}/*.json 編譯",
        f"-- {len(sups)} 個 dataset／{sum(len(x.roads) for x in sups.values())} 條補充道路",
        "--",
        "-- 作者沒放進 streets.xml 的路由本包補上；路名帶「(MiniMap)」＝不是作者取的名字。",
        "-- 執行期（主 MOD）：地圖目錄自己的 streets.xml 街道數 ≠ upstreamStreetCount 就整份停用，",
        "-- 載入的 file 街道數 ≠ roadCount 也停用。names＝英文原名 → UI 翻譯鍵。",
        "",
        f"{TABLE_GLOBAL} = {TABLE_GLOBAL} or {{}}",
        f"local Supplements = {TABLE_GLOBAL}",
        "",
    ]
    for ds in sorted(sups):
        x = sups[ds]
        lines.append(f"-- ==== {ds} ({x.map_mod} / {x.map_dir}) ====")
        lines.append(f"Supplements[{s(ds)}] = {{")
        lines.append(f"    schemaVersion = {SCHEMA_VERSION}, mapMod = {s(x.map_mod)}, mapDir = {s(x.map_dir)},")
        lines.append(f"    file = {s(runtime_file(ds))}, upstreamStreetCount = {x.upstream_count},"
                     f" roadCount = {len(x.roads)},")
        lines.append("    names = {")
        for r in x.roads:
            lines.append(f"        [{s(road_name(x.label, r.no, 'en'))}] = {s(ui_key(ds, r.no))},")
        lines.append("    },")
        lines.append("}")
        lines.append("")
    return ("\n".join(lines)).encode("utf-8")


def render_ui_json(existing: dict[str, str], sups: dict[str, Supplement], lang: str) -> bytes:
    own = {ui_key(ds, r.no): gsi._escape_pct(road_name(sups[ds].label, r.no, UI_LANG[lang]))
           for ds in sorted(sups) for r in sups[ds].roads}
    out: dict[str, str] = {}
    placed = False
    for k, v in existing.items():
        if str(k).startswith(UI_KEY_PREFIX):
            continue
        if not placed and str(k).startswith(gsi.UI_KEY_PREFIX):
            out.update(own)
            placed = True
        out[k] = v
    if not placed:
        out.update(own)
    return json.dumps(out, ensure_ascii=False, indent=4).encode("utf-8")


def render_all(project_root: Path, sups: dict[str, Supplement]) -> tuple[dict[Path, bytes], list[str]]:
    errors: list[str] = []
    out: dict[Path, bytes] = {project_root / TABLE_REL: render_table(sups)}
    for ds, sup in sups.items():
        out[project_root / XML_DIR_REL / f"{ds}.xml"] = render_xml(sup)
    for lang in gsi.UI_LANGS:
        path = gsi.ui_json_path(project_root, lang)
        existing, err = gsi.load_ui_json(path)
        if existing is None:
            errors.append(err or f"{path} 無法讀取")
            continue
        out[path] = render_ui_json(existing, sups, lang)
    return out, errors


def _stale_xml(project_root: Path, sups: dict[str, Supplement]) -> list[Path]:
    d = project_root / XML_DIR_REL
    return sorted(p for p in d.glob("*.xml") if p.stem not in sups) if d.is_dir() else []


def gen(project_root: Path) -> tuple[Result, dict[str, Supplement]]:
    sups, errors, warnings = load_all(project_root)
    if errors:
        return Result(errors, warnings), {}
    files, errs = render_all(project_root, sups)
    if errs:
        return Result(errs, warnings), {}
    for path, data in files.items():
        gsi.write_bytes_atomic(path, data)
    for p in _stale_xml(project_root, sups):
        p.unlink()
    return Result([], warnings), sups


# ============================================================
# 上游漂移（只讀、只警告）
# ============================================================
def _find_map_file(roots: list[Path], wid: str, map_dir: str, name: str) -> Path | None:
    found = gsi.find_streets_xml(roots, wid, map_dir)
    if found is not None:
        cand = found.with_name(name)
        return cand if cand.is_file() else None
    for root in roots:
        for p in sorted((root / wid).glob(f"mods/*/*/media/maps/{map_dir}/{name}")):
            return p
    return None


def survey_upstream(sups: dict[str, Supplement], *, prefer: list[str]) -> list[str]:
    warnings: list[str] = []
    roots = gsi.iter_workshop_roots(prefer)
    for ds in sorted(sups):
        x = sups[ds]
        if not any((r / x.workshop_id).is_dir() for r in roots):
            warnings.append(f"{ds} 找不到本機上游副本，跳過漂移檢查")
            continue
        streets = _find_map_file(roots, x.workshop_id, x.map_dir, "streets.xml")
        now = gsi.file_sha256(streets) if streets else None
        if now != x.streets_sha:
            warnings.append(
                f"{ds} 作者的 streets.xml 已變（{'新增' if x.streets_sha is None else '變更'}）："
                "執行期街道數不符時補充道路會自動停用，請評估改用作者資料"
            )
        wm = _find_map_file(roots, x.workshop_id, x.map_dir, "worldmap.xml")
        if x.worldmap_sha and (wm is None or gsi.file_sha256(wm) != x.worldmap_sha):
            warnings.append(f"{ds} worldmap.xml 已變（補充道路的推導來源）：重跑 derive 比對")
    return warnings


def verify(project_root: Path, *, prefer: list[str]) -> Result:
    sups, errors, warnings = load_all(project_root)
    if errors:
        return Result(errors, warnings)
    files, errs = render_all(project_root, sups)
    errors.extend(errs)
    for path, data in files.items():
        rel = path.relative_to(project_root)
        if not path.is_file():
            errors.append(f"缺生成檔 {rel}（跑 gen）")
        elif path.read_bytes() != data:
            errors.append(f"{rel} 與 {SUPPLEMENTS_DIR_NAME}/ 不同步（跑 gen）")
    errors += [f"殘留無來源的補充道路檔 {p.relative_to(project_root)}（跑 gen 清除）"
               for p in _stale_xml(project_root, sups)]
    warnings.extend(survey_upstream(sups, prefer=prefer))
    return Result(errors, warnings)


def _print_result(label: str, result: Result) -> None:
    for w in result.warnings:
        gsi.warn(f"{label} {w}")
    if result.ok:
        print(f"✅ {label}")
        return
    for e in result.errors:
        print(f"  ❌ {e}")
    print(f"❌ {label}")


# ============================================================
# selftest（自造 fixture，不依賴真資料／真 workshop）
# ============================================================
def _doc(**over: object) -> dict:
    doc: dict = {
        "dataset": "demo",
        "schemaVersion": 1,
        "source": {
            "workshop_id": "1", "map_mod": "DemoMod", "map_dir": "Demo Town",
            "streets_xml_sha256": None, "upstream_street_count": 0,
            "worldmap_xml_sha256": None, "captured": "2026-09-27", "method": "fixture",
        },
        "label": {"en": "Demo", "ch": "示範鎮", "cn": "示范镇", "jp": "デモ"},
        "roads": [
            {"no": 2, "width": 6, "points": [100, 100, 200, 100.5],
             "evidence": {"samples": 10, "on_road": 10}},
            {"no": 1, "width": 8, "points": [100, 100, 100, 180],
             "evidence": {"samples": 10, "on_road": 9}},
        ],
        "retired": [3],
    }
    doc.update(over)
    return doc


def _fixture(root: Path, doc: dict | None, *, registry: bool = True) -> Path:
    (root / SUPPLEMENTS_DIR_NAME).mkdir(parents=True, exist_ok=True)
    if doc is not None:
        (root / SUPPLEMENTS_DIR_NAME / "demo.json").write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    reg = root / REGISTRY_REL
    reg.parent.mkdir(parents=True, exist_ok=True)
    body = 'streetSupplement = StreetSupplements["demo"]' if registry else "-- none"
    reg.write_text(f"-- registry\n{body}\n", encoding="utf-8")
    for lang in gsi.UI_LANGS:
        p = gsi.ui_json_path(root, lang)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"UI_Other": "x", f"{gsi.UI_KEY_PREFIX}demo_0": "s"}, indent=4), encoding="utf-8")
    return root


def cmd_selftest() -> int:
    n_ok = n_all = 0

    def check(label: str, cond: bool, detail: str = "") -> None:
        nonlocal n_ok, n_all
        n_all += 1
        n_ok += bool(cond)
        print(f"  {'✅' if cond else '❌'} {label}{'' if cond else ' ' + detail}")

    with tempfile.TemporaryDirectory() as td:
        root = _fixture(Path(td) / "a", _doc())
        res, sups = gen(root)
        check("gen 乾淨資料", res.ok, str(res.errors))
        xml = (root / XML_DIR_REL / "demo.xml").read_text(encoding="utf-8")
        check("XML 依號碼排序、英文原名、同 streets.xml 格式",
              xml.startswith('<streets version="1">\n    <street name="Demo Rd 01 (MiniMap)" width="8">')
              and '<point x="200.0" y="100.5"/>' in xml and "\r" not in xml, xml)
        lua = (root / TABLE_REL).read_text(encoding="utf-8")
        check("Lua 表帶 file／upstreamStreetCount／roadCount／names",
              'file = "media/minimap/streets/demo.xml", upstreamStreetCount = 0, roadCount = 2,' in lua
              and '["Demo Rd 02 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_demo_02",' in lua, lua)
        ch = json.loads(gsi.ui_json_path(root, "CH").read_text(encoding="utf-8"))
        keys = list(ch)
        check("四語名稱格式與 UI 鍵位置（插在 _Street_ 區塊前）",
              ch.get(ui_key("demo", 1)) == "示範鎮 01 號路（小地圖補）"
              and keys.index(ui_key("demo", 2)) < keys.index(f"{gsi.UI_KEY_PREFIX}demo_0"), str(keys))
        jp = json.loads(gsi.ui_json_path(root, "JP").read_text(encoding="utf-8"))
        check("日文格式", jp.get(ui_key("demo", 2)) == "デモ 02号線（ミニマップ補完）", str(jp))
        check("verify 通過剛生成的檔", verify(root, prefer=[]).ok)
        # 模擬 gen_streets_i18n 重出：_Street_ 鍵移到檔尾，_Road_ 鍵留在原位 ⇒ 本檔 verify 仍通過
        p = gsi.ui_json_path(root, "EN")
        d = json.loads(p.read_text(encoding="utf-8"))
        street = {k: v for k, v in d.items() if k.startswith(gsi.UI_KEY_PREFIX)}
        rest = {k: v for k, v in d.items() if not k.startswith(gsi.UI_KEY_PREFIX)}
        p.write_bytes(json.dumps({**rest, **street}, ensure_ascii=False, indent=4).encode("utf-8"))
        check("與街名生成器交替執行不乒乓", verify(root, prefer=[]).ok)
        (root / XML_DIR_REL / "demo.xml").write_bytes(b"tampered")
        res = verify(root, prefer=[])
        check("verify 抓到 XML 不同步", not res.ok and any("不同步" in e for e in res.errors), str(res.errors))
        (root / XML_DIR_REL / "gone.xml").write_text("x", encoding="utf-8")
        res = verify(root, prefer=[])
        check("verify 抓到殘留 XML", any("殘留" in e for e in res.errors), str(res.errors))
        gen(root)
        check("gen 清掉殘留 XML", not (root / XML_DIR_REL / "gone.xml").exists())

    def bad(label: str, doc: dict, needle: str) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _fixture(Path(td) / "x", doc)
            res, _ = gen(root)
            check(f"拒收：{label}", not res.ok and any(needle in e for e in res.errors)
                  and not (root / TABLE_REL).exists(), str(res.errors))

    bad("dataset 與檔名不符", _doc(dataset="other"), "等於檔名")
    bad("schemaVersion", _doc(schemaVersion=2), "schemaVersion")
    doc = _doc(); doc["roads"][0]["no"] = 1
    bad("號碼重複", doc, "重複")
    doc = _doc(); doc["roads"][0]["no"] = 3
    bad("重用退役號碼", doc, "不得重用")
    doc = _doc(); doc["roads"][0]["evidence"]["on_road"] = 8
    bad("路面取樣低於下限", doc, "落在路面")
    doc = _doc(); doc["roads"][0]["points"] = [100, 100, 100.1, 100]
    bad("非 float32 座標", doc, "float32")
    doc = _doc(); doc["roads"][0]["points"] = [100, 100, 100, 100]
    bad("零長度道路", doc, "非零長度")
    doc = _doc(); doc["roads"][0]["points"] = [float(i) for i in range(768)]
    bad("超過 native 點數", doc, "native buffer")
    doc = _doc(); doc["source"]["upstream_street_count"] = 3
    bad("街道數與 sha 不一致", doc, "upstream_street_count")
    doc = _doc(); doc["label"].pop("jp")
    bad("缺日文標籤", doc, "label.jp")
    doc = _doc(); doc["roads"][0]["surface"] = "paved"
    bad("未知欄位", doc, "未知欄位")
    with tempfile.TemporaryDirectory() as td:
        root = _fixture(Path(td) / "r", _doc(), registry=False)
        res, _ = gen(root)
        check("註冊清單未引用只警告", res.ok and any("未引用" in w for w in res.warnings), str(res.warnings))
    with tempfile.TemporaryDirectory() as td:
        root = _fixture(Path(td) / "m", None)
        res, _ = gen(root)
        check("註冊清單引用但缺資料＝錯誤", not res.ok and any("但缺" in e for e in res.errors), str(res.errors))
    with tempfile.TemporaryDirectory() as td:
        root = _fixture(Path(td) / "u", _doc())
        gen(root)
        ws = root / "workshop" / "1" / "mods" / "demo" / "42" / "media" / "maps" / "Demo Town"
        ws.mkdir(parents=True)
        (ws / "streets.xml").write_text('<streets version="1"></streets>', encoding="utf-8")
        res = verify(root, prefer=[str(root / "workshop")])
        check("作者新增 streets.xml 只警告", res.ok and any("新增" in w for w in res.warnings), str(res.warnings))

    print(f"\n{'✅' if n_ok == n_all else '❌'} selftest {n_ok}/{n_all}")
    return 0 if n_ok == n_all else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--selftest", action="store_true", help="自我測試（零外部依賴）")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("gen", help=f"{SUPPLEMENTS_DIR_NAME}/*.json → XML＋shared 表＋四語 UI.json")
    v = sub.add_parser("verify", help="驗 schema、生成物同步、上游漂移")
    v.add_argument("--prefer", action="append", help="額外 workshop content 根（可重複）")
    args = parser.parse_args(argv)
    if args.selftest:
        return cmd_selftest()
    if args.cmd == "gen":
        result, sups = gen(PROJECT_ROOT)
        _print_result("gen 補充道路", result)
        for ds in sorted(sups):
            print(f"   {ds:24s} {len(sups[ds].roads):4d} 條（{sups[ds].map_dir}）")
        return 0 if result.ok else 1
    if args.cmd == "verify":
        result = verify(PROJECT_ROOT, prefer=args.prefer or [])
        _print_result("verify 補充道路資料", result)
        return 0 if result.ok else 1
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
