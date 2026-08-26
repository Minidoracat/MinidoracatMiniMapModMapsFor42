#!/usr/bin/env python3
"""地圖街名多語化生成器：上游 streets.xml 幾何 ＋ names.json 譯名 → 三語 XML。

單一真相是 street-names/<dataset-id>/names.json（本腳本只讀，除非 --update-hash
顯式接受新上游 sha256）。生成物進 git：

  MOD/.../42/media/minimapstreets/MinidoracatMiniMapModMapsFor42/<id>/streets_{CH,CN,JP}.xml

用法：
  python scripts/gen_streets_i18n.py gen [--dataset ID] [--prefer DIR]
      [--update-hash] [--allow-partial]
  python scripts/gen_streets_i18n.py verify [--dataset ID] [--prefer DIR]
  python scripts/gen_streets_i18n.py --selftest

閘門（fail-closed；任一 dataset 失敗不寫該組檔）：
  1. 與上游逐條一致（street 數／順序／width／points），只允許 name 屬性值不同
  2. 三語完整：每個 unique 英文名都有非空 ch/cn/jp（--allow-partial 僅本機預覽）
  3. 譯後撞名：同語言譯後 unique 數必須＝英文 unique 數
  4. UTF-8 無 BOM；換行符與上游一致

--prefer 與 map_tracker deps-scan 同語意：優先的 workshop content 根
（<root>/<workshop_id>/mods/…）；未給時追加預設 Steam workshop content 根。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OWNER_MOD_ID = "MinidoracatMiniMapModMapsFor42"
STREET_NAMES_DIR = PROJECT_ROOT / "street-names"
OUT_BASE = (
    PROJECT_ROOT
    / "MOD" / OWNER_MOD_ID / "Contents" / "mods" / OWNER_MOD_ID
    / "42" / "media" / "minimapstreets" / OWNER_MOD_ID
)
# 與 rebuild_pyramids.WORKSHOP／map_tracker --prefer 預設同一 workshop content 根
DEFAULT_WORKSHOP = Path(r"D:\SteamLibrary\steamapps\workshop\content\108600")
# 搜尋用英文原名表（append 進主 MOD 的同一張全域表；緣由見 bake_english_table）
EN_TABLE_REL = Path("42") / "media" / "lua" / "shared" / "MinidoracatMiniMapModMapsStreetNames.lua"
EN_TABLE_GLOBAL = "MinidoracatMiniMapStreetNames"
# vanilla 全域街道表：引擎每張官方地圖目錄都放同一份全世界街道（實測 Muldraugh/
# Riverside 皆 1098 條且逐條位置對齊），keep-scan 拿它當「官方已有」的比對基準。
DEFAULT_GAME_DIR = Path(r"D:\SteamLibrary\steamapps\common\ProjectZomboid")
VANILLA_STREETS_REL = Path("media") / "maps" / "Muldraugh, KY" / "streets.xml"
# registry（註冊清單）：keep-scan 由此取每個 dataset 的 streetI18n → bounds 對應
REGISTRY_REL = (
    Path("MOD") / OWNER_MOD_ID / "Contents" / "mods" / OWNER_MOD_ID
    / "42" / "media" / "lua" / "client" / "MinidoracatMiniMapModMaps.lua"
)
# keep-scan 判定門檻
_CLASH_AXIS_TOL = 2.0    # 共線容差（square）：作者常把 vanilla 路重畫差 1-2 格
_CLASH_MIN_OVERLAP = 24.0  # 重疊長度下限：短於此視為路口相交，非同一條路
_OOB_MIN_INSIDE = 0.5    # 過半點落在本圖 bounds 外＝上游全域表殘留，非本圖街道
# `overlay`（不分名字的共線）門檻用**比例**而非絕對長度：名字不同時幾何證據要更強。
# 實測雛菊郡 Ivy Road／Meadow Way 等 6 條是 100% 蓋在官方路上（該剔除），而
# Dahlia Court 33%、西點擴張 Hillcrest Ln 13% 只是路口接到官方路（不能剔）。
_OVERLAY_MIN_RATIO = 0.6

LANGS = ("CH", "CN", "JP")
LANG_KEYS = {"CH": "ch", "CN": "cn", "JP": "jp"}
_VERSION_DIR_RE = re.compile(r"^42(\.\d+)*$")
_STREET_OPEN_RE = re.compile(r"<street\b[^>]*>")
_NAME_ATTR_RE = re.compile(r'name="([^"]*)"')
_POINT_RE = re.compile(r'<point\s+x="([^"]*)"\s+y="([^"]*)"')
_WIDTH_ATTR_RE = re.compile(r'width="([^"]*)"')
_POINTS_RE = re.compile(r"<points>(.*?)</points>", re.DOTALL)
_STREET_BLOCK_RE = re.compile(r"<street\b.*?</street>", re.DOTALL)
# 剔除用：連前導換行＋縮排一起吃掉，避免移除 <street> block 後留下空行
_STREET_BLOCK_LEAD_RE = re.compile(r"(?:\r?\n[ \t]*)?<street\b.*?</street>", re.DOTALL)


class Result:
    def __init__(
        self,
        ok: bool,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        self.ok = ok
        self.errors = errors or []
        self.warnings = warnings or []


def warn(msg: str) -> None:
    on_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    print(f"::warning::{msg}" if on_ci else f"  ⚠️ {msg}")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_name(s: str) -> str:
    """多重空白折疊為單一空格＋trim（上游有 Forest  St 髒名）。"""
    return " ".join(s.split())


def xml_unescape(s: str) -> str:
    # 具名實體；&amp; 必須最後，避免 &amp;lt; 被提前拆開
    return (
        s.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&apos;", "'")
        .replace("&amp;", "&")
    )


def xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def iter_workshop_roots(
    prefer: list[str] | None, *, include_default: bool = True
) -> list[Path]:
    roots: list[Path] = []
    seen: set[str] = set()
    for p in prefer or []:
        path = Path(p)
        key = str(path.resolve()) if path.exists() else str(path)
        if key not in seen:
            seen.add(key)
            roots.append(path)
    if include_default and DEFAULT_WORKSHOP.is_dir():
        key = str(DEFAULT_WORKSHOP.resolve())
        if key not in seen:
            roots.append(DEFAULT_WORKSHOP)
    return roots


def find_streets_xml(
    roots: list[Path], workshop_id: str, map_dir: str
) -> Path | None:
    """<root>/<workshop_id>/mods/*/{common,42*}/media/maps/<map_dir>/streets.xml。

    版本資料夾優先於 common（同 map_tracker._mod_content_bases）；首個命中勝出。
    """
    if not workshop_id or not map_dir:
        return None
    for root in roots:
        mods = root / workshop_id / "mods"
        if not mods.is_dir():
            continue
        for mod in sorted(p for p in mods.iterdir() if p.is_dir()):
            vers = sorted(
                d for d in mod.iterdir()
                if d.is_dir() and _VERSION_DIR_RE.match(d.name)
            )
            bases = list(vers)
            common = mod / "common"
            if common.is_dir():
                bases.append(common)
            for base in bases:
                cand = base / "media" / "maps" / map_dir / "streets.xml"
                if cand.is_file():
                    return cand
    return None


def read_names_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_names_json(path: Path, data: dict) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def write_bytes_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_bytes(data)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def output_dir_for(project_root: Path, dataset_id: str) -> Path:
    return (
        project_root
        / "MOD" / OWNER_MOD_ID / "Contents" / "mods" / OWNER_MOD_ID
        / "42" / "media" / "minimapstreets" / OWNER_MOD_ID / dataset_id
    )


def discover_names_files(
    street_names_dir: Path, dataset: str | None
) -> list[Path]:
    if dataset:
        p = street_names_dir / dataset / "names.json"
        return [p]
    if not street_names_dir.is_dir():
        return []
    return sorted(
        p for p in street_names_dir.glob("*/names.json") if p.is_file()
    )


def _load_names_map(data: dict) -> tuple[dict[str, dict], list[str]]:
    """names.json → {正規化英文名: {ch,cn,jp}}；重複正規化鍵視為錯誤。"""
    errors: list[str] = []
    raw = data.get("names")
    if not isinstance(raw, dict):
        return {}, ["names.json 缺少 names 物件"]
    out: dict[str, dict] = {}
    for key, val in raw.items():
        nk = normalize_name(str(key))
        if not nk:
            errors.append("names.json 有空白鍵")
            continue
        if nk in out:
            errors.append(f"names.json 正規化後重複鍵：{nk!r}")
            continue
        if not isinstance(val, dict):
            errors.append(f"names.json[{nk!r}] 不是物件")
            continue
        out[nk] = val
    return out, errors


def _field(entry: dict, lang: str) -> str | None:
    key = LANG_KEYS[lang]
    if key not in entry:
        return None
    val = entry[key]
    if not isinstance(val, str):
        return None
    text = val.strip()
    return text if text else None


def extract_name_values(xml_text: str) -> list[str]:
    """依出現順序取出每個 <street> 的 name 屬性值（已 unescape、未正規化）。"""
    out: list[str] = []
    for tag in _STREET_OPEN_RE.findall(xml_text):
        m = _NAME_ATTR_RE.search(tag)
        out.append(xml_unescape(m.group(1)) if m else "")
    return out


def unique_normalized(names: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for n in names:
        k = normalize_name(n)
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def strip_name_attrs(text: str) -> str:
    """刪除 name="..." 屬性（含值），其餘字節保留——幾何比對用。"""
    def repl_tag(m: re.Match[str]) -> str:
        return _NAME_ATTR_RE.sub("", m.group(0))

    return _STREET_OPEN_RE.sub(repl_tag, text)


def parse_street_geometry(xml_text: str) -> list[tuple[str, str]]:
    """[(width, points_inner), ...] 依 street 出現順序。"""
    rows: list[tuple[str, str]] = []
    for block in _STREET_BLOCK_RE.findall(xml_text):
        wm = _WIDTH_ATTR_RE.search(block)
        pm = _POINTS_RE.search(block)
        rows.append((wm.group(1) if wm else "", pm.group(1) if pm else ""))
    return rows


def collision_groups(eng_to_tr: dict[str, str]) -> list[tuple[str, list[str]]]:
    inv: dict[str, list[str]] = {}
    for eng, tr in eng_to_tr.items():
        inv.setdefault(tr, []).append(eng)
    return [(tr, engs) for tr, engs in inv.items() if len(engs) > 1]


def _has_bom(data: bytes) -> bool:
    return data.startswith(b"\xef\xbb\xbf")


def _decode_xml_bytes(data: bytes) -> tuple[str | None, str | None]:
    if _has_bom(data):
        return None, "UTF-8 BOM（禁止）"
    try:
        return data.decode("utf-8"), None
    except UnicodeDecodeError as e:
        return None, f"非 UTF-8：{e}"


# 幾何正規化：4 點軸對齊「街道輪廓矩形」→ 2 點中心線。
#
# 為何要做：部分地圖作者（實測 Daisy County 44/44 條）把街道畫成矩形輪廓，而 width
# 屬性本來就表達寬度 ⇒ 重複表達。引擎沿折線繪製標籤時會在矩形的兩條長邊各畫一次，
# 玩家看到路名上下兩行；NavRoute 也會把兩條平行邊與兩條短邊都當成路段建圖。
# 壓成中心線後視覺與路網都正確，且 width 保留 ⇒ 街道粗細不變。
#
# 判定嚴格（誤判會破壞幾何）：必須是軸對齊、四角互異的閉合矩形，且
#   短邊 <= max(width * 1.5, MAX_SHORT)  ← 排除真的環形道路／廣場
#   長邊 >= 短邊 * MIN_RATIO             ← 排除方形環路
# 不符者原樣保留。實測：Daisy County 44/44 命中；其餘 19 個 dataset 命中 0
# （它們的 4 點街道是真 L 形折線），且轉換後無兩條街共用同一中心線。
_NORM_MAX_SHORT = 16.0
_NORM_MIN_RATIO = 3.0


def normalize_street_geometry(
    points: list[tuple[float, float]], width: float
) -> list[tuple[float, float]] | None:
    """→ 中心線 2 點；不符輪廓矩形判定回 None（呼叫端原樣保留）。"""
    if len(points) != 4:
        return None
    xs = sorted({p[0] for p in points})
    ys = sorted({p[1] for p in points})
    if len(xs) != 2 or len(ys) != 2:
        return None
    x0, x1 = xs
    y0, y1 = ys
    if set(points) != {(x0, y0), (x1, y0), (x1, y1), (x0, y1)}:
        return None
    if len(set(points)) != 4:
        return None
    w = x1 - x0
    h = y1 - y0
    short, long_ = min(w, h), max(w, h)
    if short <= 0 or short > max(width * 1.5, _NORM_MAX_SHORT):
        return None
    if long_ < short * _NORM_MIN_RATIO:
        return None
    if w >= h:
        cy = (y0 + y1) / 2
        return [(x0, cy), (x1, cy)]
    cx = (x0 + x1) / 2
    return [(cx, y0), (cx, y1)]


def _fmt_coord(v: float) -> str:
    """整數不留小數點（與上游整數座標風格一致）；非整數保留必要精度。"""
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


def _rewrite_points(block: str, new_points: list[tuple[float, float]]) -> str:
    """重寫 <points> 內容，沿用原 block 的換行與縮排風格。"""
    m = _POINTS_RE.search(block)
    if not m:
        return block
    inner = m.group(1)
    pm = re.search(r"(\r?\n)([ \t]*)<point", inner)
    nl, indent = (pm.group(1), pm.group(2)) if pm else ("\n", "")
    tm = re.search(r"(\r?\n)([ \t]*)$", inner)
    tail = tm.group(1) + tm.group(2) if tm else nl
    body = "".join(
        f'{nl}{indent}<point x="{_fmt_coord(x)}" y="{_fmt_coord(y)}"/>'
        for x, y in new_points
    )
    return block[: m.start(1)] + body + tail + block[m.end(1) :]


def _transform_xml(
    xml_text: str,
    mapping: dict[str, str] | None,
    *,
    allow_partial: bool,
    keep_geometry: set[str] | None = None,
) -> tuple[str | None, list[str], list[str], int]:
    """上游 XML → 目標語言 XML（確定性）：幾何正規化 ＋ name 替換。

    非 <street> 區域的字節（含換行、宣告、縮排）一律不動。回傳的第 4 項是被
    正規化的街道數（審計用）。這支函式是 gen 與 verify 的**唯一**轉換來源：
    verify 重跑它並與生成檔逐字節比對 ⇒ 契約＝可重現，沒有手改空間。
    """
    errors: list[str] = []
    warnings: list[str] = []
    normalized = 0

    def repl_name_in(tag: str) -> str:
        def repl_name(nm: re.Match[str]) -> str:
            raw = nm.group(1)
            key = normalize_name(xml_unescape(raw))
            if key in mapping:
                return f'name="{xml_escape(mapping[key])}"'
            if allow_partial:
                warnings.append(f"缺譯，保留英文原文：{key!r}")
                return nm.group(0)
            errors.append(f"缺譯：{key!r}")
            return nm.group(0)

        return _NAME_ATTR_RE.sub(repl_name, tag)

    def repl_block(m: re.Match[str]) -> str:
        nonlocal normalized
        block = m.group(0)
        pts = [
            (float(a), float(b))
            for a, b in _POINT_RE.findall(block)
        ]
        # 保留清單（幾何指紋，正規化前計算）：不在清單內的街道整條剔除（連前導換行）。
        # 用途＝上游圖與 vanilla 同座標重疊的街道，剔除後由本體漢化那份顯示。
        if keep_geometry is not None and pts:
            if _geom_key(pts) not in keep_geometry:
                return ""
        wm = _WIDTH_ATTR_RE.search(block)
        try:
            width = float(wm.group(1)) if wm else 5.0
        except ValueError:
            width = 5.0
        centerline = normalize_street_geometry(pts, width) if pts else None
        if centerline is not None:
            block = _rewrite_points(block, centerline)
            normalized += 1
        # mapping=None＝只做幾何正規化（gen/verify 的基準線用）
        if mapping is not None:
            # name 只在開標籤上；限定第一個 <street ...> 以免動到 points 內容
            om = _STREET_OPEN_RE.search(block)
            if om:
                block = block[: om.start()] + repl_name_in(om.group(0)) + block[om.end() :]
        return block

    out = _STREET_BLOCK_LEAD_RE.sub(repl_block, xml_text)
    if errors:
        return None, errors, warnings, normalized
    return out, errors, warnings, normalized


def _geom_key(points: list[tuple[float, float]]) -> str:
    """幾何指紋：points 序列的 sha1 前 12 hex。用於「保留清單」精確比對。

    為何不用「名稱白名單」：同一張圖可能有同名不同段的街（Muldraugh 1993 的 Main St
    既有獨有段、也有與官方幾何相同的段），按名稱過濾會把後者放過去、照樣疊字。
    指紋在**正規化前**計算（對上游原始座標），這樣 names.json 記的值與上游一一對應。
    """
    s = ";".join(f"{x:g},{y:g}" for x, y in points)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def _keep_geometry(data: dict) -> set[str] | None:
    """names.json 的 source.keep_geometry：只保留指紋在清單內的街道，其餘剔除。

    用於「上游圖與 vanilla 同座標重疊」：保留該圖獨有的街並翻譯，重疊的交給本體漢化
    顯示 ⇒ 不疊字也不漏路名。缺此欄位＝全部保留（一般 dataset 的行為）。
    """
    src = data.get("source") if isinstance(data.get("source"), dict) else {}
    raw = src.get("keep_geometry")
    if not isinstance(raw, list) or not raw:
        return None
    return {str(v).strip() for v in raw if str(v).strip()}


_SUFFIX_ALIASES = (
    ("road", "rd"), ("street", "st"), ("avenue", "ave"), ("drive", "dr"),
    ("court", "ct"), ("trail", "tr"), ("lane", "ln"), ("boulevard", "blvd"),
    ("place", "pl"), ("circle", "cir"), ("terrace", "ter"), ("parkway", "pkwy"),
)


def _match_key(name: str) -> str:
    """街名比對鍵：後綴縮寫等同、去標點與大小寫。

    上游作者常把官方 `Pony Trot Road` 抄成 `Pony Trot Rd`（實測 eds-auto-salvage、
    muldraugh-1993 的 W Garnettsville Rd）——那是同一條路，必須判為撞名。
    """
    s = name.lower().strip()
    for full, abbr in _SUFFIX_ALIASES:
        s = re.sub(rf"\b{full}\b", abbr, s)
    return re.sub(r"[^a-z0-9]+", "", s)


def _axis_segments(
    points: list[tuple[float, float]],
) -> list[tuple[str, float, float, float]]:
    """相鄰點構成的軸對齊線段 → (方向, 軸座標, 起, 迄)。斜段不參與共線判定。

    街名標籤沿折線繪製，共線重疊才會讓兩個標籤畫在同一條路上；斜段極少且
    判定易誤傷，一律略過（漏判會保留該街，屬安全側）。
    """
    out: list[tuple[str, float, float, float]] = []
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        if abs(y1 - y2) < 0.01 and abs(x1 - x2) > 0.01:
            out.append(("h", round(y1, 1), min(x1, x2), max(x1, x2)))
        elif abs(x1 - x2) < 0.01 and abs(y1 - y2) > 0.01:
            out.append(("v", round(x1, 1), min(y1, y2), max(y1, y2)))
    return out


def drawn_points(
    block: str, points: list[tuple[float, float]]
) -> list[tuple[float, float]]:
    """該街道實際被繪製的幾何＝套用確定性正規化後的點序列。

    共線／疊字判定一律要用這個：矩形輪廓的原始四邊各偏中心線 ±width/2，拿原始
    座標比對會漏判（同一條路被判成兩條不相干的路）。
    """
    wm = _WIDTH_ATTR_RE.search(block)
    try:
        width = float(wm.group(1)) if wm else 5.0
    except ValueError:
        width = 5.0
    return normalize_street_geometry(points, width) or points


class VanillaStreets:
    """vanilla 全域街道表索引，供 keep-scan 判定「官方已有這條路」。

    四種索引對應四道剔除規則：
    - `geoms`：幾何指紋集合（**原始座標**）→ 上游整條照抄官方
    - `by_name`：同名的點序列（原始座標）→ 上游微調過座標（端點差 1-2 格）
    - `segs`：軸對齊線段依比對鍵分組 → 上游重畫同一條路（同名、分段不同）
    - `segs_any`：軸對齊線段不分名字 → 上游把官方的路改名重畫

    線段索引一律用**正規化後**（＝實際繪製）的幾何：作者常把街道畫成矩形輪廓，
    原始四邊落在中心線 ±width/2，拿原始座標比會整批漏判（實測雛菊郡 `Ivy Road`
    輪廓在 y=7446/7456、中心線 y=7451 才與官方 `Raccoon Road` 重疊 300 square）。
    """

    def __init__(self, xml_text: str) -> None:
        self.geoms: set[tuple[tuple[float, float], ...]] = set()
        self.by_name: dict[str, list[tuple[tuple[float, float], ...]]] = {}
        self.segs: dict[tuple[str, str], list[tuple[float, float, float]]] = {}
        self.segs_any: dict[str, list[tuple[float, float, float]]] = {}
        for block in _STREET_BLOCK_RE.findall(xml_text):
            pts = [(float(a), float(b)) for a, b in _POINT_RE.findall(block)]
            if not pts:
                continue
            nm = _NAME_ATTR_RE.search(block)
            name = normalize_name(xml_unescape(nm.group(1))) if nm else ""
            rounded = tuple((round(x, 3), round(y, 3)) for x, y in pts)
            self.geoms.add(rounded)
            self.by_name.setdefault(name, []).append(rounded)
            mk = _match_key(name)
            for kind, axis, lo, hi in _axis_segments(drawn_points(block, pts)):
                self.segs.setdefault((kind, mk), []).append((axis, lo, hi))
                self.segs_any.setdefault(kind, []).append((axis, lo, hi))

    def __len__(self) -> int:
        return len(self.geoms)


def find_vanilla_streets(game_dir: Path | None) -> Path | None:
    """定位 vanilla 全域街道表；找不到回 None（呼叫端負責報錯）。"""
    for base in (game_dir, DEFAULT_GAME_DIR):
        if base is None:
            continue
        p = base / VANILLA_STREETS_REL
        if p.is_file():
            return p
    return None


def read_registry_bounds(project_root: Path) -> dict[str, list[int]]:
    """registry 的 `streetI18n = "<id>"` → 同一條目的 `bounds`（世界 square）。

    bounds 是該圖 pyramid 的圖像範圍＝它實際佔的世界區域，用來判「這條街是不是
    本圖的」。上游若把官方全域表整份抄走（實測 Muldraugh 1993），範圍外那些街
    根本不屬於本圖，翻了會在全世界各處與官方漢化打對台。
    """
    text = (project_root / REGISTRY_REL).read_text(encoding="utf-8")
    out: dict[str, list[int]] = {}
    for mid, raw in re.findall(
        r"\{ zip = \"[^\"]+\"(.*?)bounds = \{ ([^}]*) \}", text, re.DOTALL
    ):
        sm = re.search(r'streetI18n = "([^"]+)"', mid)
        if sm is None:
            continue
        try:
            vals = [int(v.strip()) for v in raw.split(",")]
        except ValueError:
            continue
        if len(vals) == 4:
            out[sm.group(1)] = vals
    return out


def scan_keep_geometry(
    xml_text: str,
    vanilla: VanillaStreets,
    bounds: list[int] | None,
) -> tuple[list[str], dict[str, int], list[tuple[str, str]]]:
    """掃出「本圖獨有、翻譯後不會與官方漢化打對台」的街道幾何指紋。

    四道剔除（順序即優先序，命中即停）：
      1. `same` 幾何與官方完全相同 → 上游整條照抄；翻了＝同座標同譯名疊畫。
      2. `near` 同名且僅 ≤2 點、位移 ≤2 square → 上游微調座標，視覺仍完全疊合。
      3. `clash` 比對鍵相同且共線重疊 ≥ 門檻 → 上游重畫同一條路（分段/縮寫不同）。
      4. `overlay` 不分名字的共線重疊 ≥ 門檻 → 上游把官方的路改名重畫；引擎兩份
         都畫 ⇒ 同一條路交錯出現兩個名字（實測雛菊郡 `Ivy Road` 蓋在官方
         `Raccoon Road` 上，玩家看到「浣熊路／常春藤路」交錯）。官方那份動不了，
         所以剔除我方這份，讓該路只顯示官方名。
      5. `oob` 過半點在本圖 bounds 外 → 上游全域表殘留，不屬本圖。

    共線比對一律用 `drawn_points`（正規化後＝實際繪製）的幾何，原因見 VanillaStreets。
    回傳 (保留的指紋清單, 各規則剔除計數, 撞名樣本)。樣本供人工覆核判定是否過寬。
    """
    keep: list[str] = []
    stats = {"same": 0, "near": 0, "clash": 0, "overlay": 0, "oob": 0, "keep": 0}
    samples: list[tuple[str, str]] = []
    for block in _STREET_BLOCK_RE.findall(xml_text):
        pts = [(float(a), float(b)) for a, b in _POINT_RE.findall(block)]
        if not pts:
            continue
        nm = _NAME_ATTR_RE.search(block)
        name = normalize_name(xml_unescape(nm.group(1))) if nm else ""
        rounded = tuple((round(x, 3), round(y, 3)) for x, y in pts)
        if rounded in vanilla.geoms:
            stats["same"] += 1
            continue
        hit_near = False
        for vp in vanilla.by_name.get(name, []):
            if len(vp) != len(rounded):
                continue
            diff = [(a, b) for a, b in zip(rounded, vp) if a != b]
            if diff and len(diff) <= 2 and max(
                max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a, b in diff
            ) <= _CLASH_AXIS_TOL:
                hit_near = True
                break
        if hit_near:
            stats["near"] += 1
            continue
        drawn = _axis_segments(drawn_points(block, pts))
        mk = _match_key(name)
        hit_clash = ""
        for kind, axis, lo, hi in drawn:
            for a2, lo2, hi2 in vanilla.segs.get((kind, mk), ()):
                if abs(axis - a2) <= _CLASH_AXIS_TOL and (
                    min(hi, hi2) - max(lo, lo2) >= _CLASH_MIN_OVERLAP
                ):
                    hit_clash = f"{kind}@{axis:g} 重疊 {min(hi, hi2) - max(lo, lo2):.0f}"
                    break
            if hit_clash:
                break
        if hit_clash:
            stats["clash"] += 1
            if len(samples) < 12:
                samples.append((f"{name} [撞名]", hit_clash))
            continue
        # overlay：累計「與官方任何街道共線的長度」佔本街道軸長的比例。
        # 逐段取最長重疊並夾在該段長度內，避免官方多條平行路把比例推爆。
        axis_len = sum(hi - lo for _, _, lo, hi in drawn)
        ov_len = 0.0
        for kind, axis, lo, hi in drawn:
            best = max(
                (
                    min(hi, hi2) - max(lo, lo2)
                    for a2, lo2, hi2 in vanilla.segs_any.get(kind, ())
                    if abs(axis - a2) <= _CLASH_AXIS_TOL
                ),
                default=0.0,
            )
            ov_len += max(0.0, min(best, hi - lo))
        ratio = ov_len / axis_len if axis_len else 0.0
        if ov_len >= _CLASH_MIN_OVERLAP and ratio >= _OVERLAY_MIN_RATIO:
            stats["overlay"] += 1
            if len(samples) < 12:
                samples.append(
                    (f"{name} [蓋在官方路上]", f"重疊 {ov_len:.0f}/{axis_len:.0f} = {ratio*100:.0f}%")
                )
            continue
        if bounds is not None:
            inside = sum(
                1 for x, y in pts
                if bounds[0] <= x < bounds[2] and bounds[1] <= y < bounds[3]
            )
            if inside / len(pts) < _OOB_MIN_INSIDE:
                stats["oob"] += 1
                continue
        keep.append(_geom_key(pts))
        stats["keep"] += 1
    return keep, stats, samples


def kept_unique_names(xml_text: str, keep: set[str] | None) -> list[str]:
    """保留清單過濾後的 unique 英文名（依出現順序）。keep=None → 全部街道。

    gen/verify 都用它算「需要翻譯的名字集合」：這樣被剔除的街不會被當成漏譯，
    而保留的街仍必須三語完整（保留清單不能變成偷偷漏譯的後門）。
    """
    out: list[str] = []
    seen: set[str] = set()
    for block in _STREET_BLOCK_RE.findall(xml_text):
        pts = [(float(a), float(b)) for a, b in _POINT_RE.findall(block)]
        if keep is not None and pts and _geom_key(pts) not in keep:
            continue
        nm = _NAME_ATTR_RE.search(block)
        if nm is None:
            continue
        n = normalize_name(xml_unescape(nm.group(1)))
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def _check_completeness(
    unique_en: list[str], names_map: dict[str, dict], *, allow_partial: bool
) -> tuple[dict[str, dict[str, str]], list[str], list[str]]:
    """→ ({lang: {en: translated}}, errors, warnings)。unique_en 由呼叫端先過濾。"""
    errors: list[str] = []
    warnings: list[str] = []
    per_lang: dict[str, dict[str, str]] = {lang: {} for lang in LANGS}
    for en in unique_en:
        entry = names_map.get(en)
        if entry is None:
            msg = f"names.json 無此 unique 名：{en!r}"
            if allow_partial:
                warnings.append(msg + "（填英文原文）")
                for lang in LANGS:
                    per_lang[lang][en] = en
            else:
                errors.append(msg)
            continue
        for lang in LANGS:
            val = _field(entry, lang)
            if val is None:
                msg = f"{en!r} 缺 {LANG_KEYS[lang]}"
                if allow_partial:
                    warnings.append(msg + "（填英文原文）")
                    per_lang[lang][en] = en
                else:
                    errors.append(msg)
            else:
                per_lang[lang][en] = val
    return per_lang, errors, warnings


def _check_collisions(
    unique_en: list[str], per_lang: dict[str, dict[str, str]]
) -> list[str]:
    errors: list[str] = []
    n = len(unique_en)
    for lang in LANGS:
        mapping = {en: per_lang[lang][en] for en in unique_en if en in per_lang[lang]}
        uniq = set(mapping.values())
        if len(mapping) != n:
            continue
        if len(uniq) != n:
            errors.append(
                f"{lang} 譯後 unique 數 {len(uniq)} ≠ 英文 unique 數 {n}"
            )
            for tr, engs in collision_groups(mapping):
                errors.append(f"  撞名 {lang} {tr!r} ← {', '.join(engs)}")
    return errors


def _source_meta(data: dict) -> tuple[str, str, str, str]:
    src = data.get("source") if isinstance(data.get("source"), dict) else {}
    return (
        str(src.get("workshop_id") or ""),
        str(src.get("map_mod") or ""),
        str(src.get("map_dir") or ""),
        str(src.get("streets_xml_sha256") or ""),
    )


def gen_dataset(
    names_path: Path,
    *,
    prefer: list[str],
    project_root: Path,
    update_hash: bool = False,
    allow_partial: bool = False,
    include_default_workshop: bool = True,
) -> Result:
    errors: list[str] = []
    warnings: list[str] = []
    if not names_path.is_file():
        return Result(False, [f"找不到 {names_path}"])
    try:
        data = read_names_json(names_path)
    except (OSError, json.JSONDecodeError) as e:
        return Result(False, [f"讀 names.json 失敗：{e}"])

    dataset_id = names_path.parent.name
    declared = data.get("dataset")
    if declared is not None and str(declared) != dataset_id:
        errors.append(
            f"dataset 欄位 {declared!r} 與目錄名 {dataset_id!r} 不符"
        )

    names_map, load_err = _load_names_map(data)
    errors.extend(load_err)
    wid, _map_mod, map_dir, recorded_sha = _source_meta(data)
    if not wid or not map_dir:
        errors.append("source.workshop_id / source.map_dir 缺失")
        return Result(False, errors)

    roots = iter_workshop_roots(prefer, include_default=include_default_workshop)
    xml_path = find_streets_xml(roots, wid, map_dir)
    if xml_path is None:
        return Result(
            False,
            errors + [
                f"找不到上游 streets.xml（workshop_id={wid} map_dir={map_dir!r}；"
                f"roots={roots}）"
            ],
        )

    raw = xml_path.read_bytes()
    xml_text, dec_err = _decode_xml_bytes(raw)
    if dec_err or xml_text is None:
        return Result(False, errors + [f"上游 XML {dec_err}"])

    current_sha = file_sha256(xml_path)
    keep = _keep_geometry(data)
    # unique_en 只含「保留下來」的街名：被剔除的街不算漏譯，added/removed 也才對得上
    unique_en = kept_unique_names(xml_text, keep)
    json_keys = set(names_map)
    added = [n for n in unique_en if n not in json_keys]
    removed = sorted(json_keys - set(unique_en))

    hash_mismatch = bool(recorded_sha) and recorded_sha != current_sha
    if hash_mismatch and not update_hash:
        errors.append(
            f"上游 sha256 不符（記錄 {recorded_sha}／現行 {current_sha}）"
        )
        if added:
            errors.append("新增 unique：" + "、".join(added))
        if removed:
            errors.append("移除 unique：" + "、".join(removed))
        if not added and not removed:
            errors.append("街名集合不變（僅幾何／空白變更）")
        errors.append(
            "補譯流程：更新 names.json 三語後以 gen --update-hash 接受新上游"
        )
        return Result(False, errors, warnings)

    if hash_mismatch and update_hash:
        data.setdefault("source", {})
        data["source"]["streets_xml_sha256"] = current_sha
        data["source"]["captured"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        write_names_json(names_path, data)
        warnings.append(f"已更新 source.streets_xml_sha256 → {current_sha}")
        if added:
            warnings.append("新增 unique：" + "、".join(added))
        if removed:
            warnings.append("移除 unique：" + "、".join(removed))

    if not recorded_sha and update_hash:
        data.setdefault("source", {})
        data["source"]["streets_xml_sha256"] = current_sha
        data["source"]["captured"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        write_names_json(names_path, data)

    per_lang, comp_err, comp_warn = _check_completeness(
        unique_en, names_map, allow_partial=allow_partial
    )
    errors.extend(comp_err)
    warnings.extend(comp_warn)
    errors.extend(_check_collisions(unique_en, per_lang))
    if errors:
        return Result(False, errors, warnings)

    out_dir = output_dir_for(project_root, dataset_id)
    generated: dict[str, str] = {}
    for lang in LANGS:
        text, t_err, t_warn, n_norm = _transform_xml(
            xml_text, per_lang[lang], allow_partial=allow_partial, keep_geometry=keep
        )
        warnings.extend(t_warn)
        if t_err or text is None:
            return Result(False, errors + t_err, warnings)
        generated[lang] = text
        norm_count = n_norm

    # 幾何閘門：基準線＝上游「只套幾何正規化＋同一份保留清單、不改名」的結果。
    # 契約＝「幾何等於上游套用確定性轉換後的結果」，verify 重跑同一支轉換即可完全複驗。
    baseline, b_err, _, _ = _transform_xml(
        xml_text, None, allow_partial=True, keep_geometry=keep
    )
    if b_err or baseline is None:
        return Result(False, errors + ["幾何基準線產生失敗"], warnings)
    base_stripped = strip_name_attrs(baseline)
    base_geom = parse_street_geometry(baseline)
    for lang, text in generated.items():
        if strip_name_attrs(text) != base_stripped:
            return Result(
                False,
                errors + [f"{lang} 生成檔 strip name 後與正規化基準線不等"],
                warnings,
            )
        geom = parse_street_geometry(text)
        if len(geom) != len(base_geom):
            return Result(
                False,
                errors + [f"{lang} street 數 {len(geom)} ≠ 基準線 {len(base_geom)}"],
                warnings,
            )
        for i, (a, b) in enumerate(zip(geom, base_geom)):
            if a != b:
                return Result(
                    False,
                    errors + [f"{lang} street[{i}] width/points 與基準線不符"],
                    warnings,
                )
        if _has_bom(text.encode("utf-8")):
            return Result(False, errors + [f"{lang} 編碼含 BOM"], warnings)

    for lang, text in generated.items():
        write_bytes_atomic(out_dir / f"streets_{lang}.xml", text.encode("utf-8"))
    return Result(True, [], warnings)


def _verify_self_consistency(
    names_map: dict[str, dict],
    xmls: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    unique_en = unique_normalized(list(names_map.keys()))
    per_lang, comp_err, _ = _check_completeness(
        unique_en, names_map, allow_partial=False
    )
    errors.extend(comp_err)
    errors.extend(_check_collisions(unique_en, per_lang))

    stripped = {lang: strip_name_attrs(xmls[lang]) for lang in LANGS}
    geom = {lang: parse_street_geometry(xmls[lang]) for lang in LANGS}
    if len({stripped[lang] for lang in LANGS}) != 1:
        errors.append("三檔 strip name 後幾何互不一致")
    counts = {lang: len(geom[lang]) for lang in LANGS}
    if len(set(counts.values())) != 1:
        errors.append(f"三檔 street 數不一致：{counts}")

    json_vals = {
        lang: {v for v in per_lang[lang].values()} for lang in LANGS
    }
    for lang in LANGS:
        got = unique_normalized(extract_name_values(xmls[lang]))
        # 允許譯名或（顯式等值英文）鍵本身
        allowed = json_vals[lang] | set(names_map)
        bad = [n for n in got if n not in allowed]
        if bad:
            errors.append(f"{lang} 生成名不在 names.json 譯名／鍵內：{bad[:8]}")
    return errors


def verify_dataset(
    names_path: Path,
    *,
    prefer: list[str],
    project_root: Path,
    include_default_workshop: bool = True,
) -> Result:
    errors: list[str] = []
    warnings: list[str] = []
    if not names_path.is_file():
        return Result(False, [f"找不到 {names_path}"])
    try:
        data = read_names_json(names_path)
    except (OSError, json.JSONDecodeError) as e:
        return Result(False, [f"讀 names.json 失敗：{e}"])

    dataset_id = names_path.parent.name
    names_map, load_err = _load_names_map(data)
    errors.extend(load_err)
    wid, _map_mod, map_dir, _sha = _source_meta(data)

    out_dir = output_dir_for(project_root, dataset_id)
    xml_bytes: dict[str, bytes] = {}
    xmls: dict[str, str] = {}
    for lang in LANGS:
        p = out_dir / f"streets_{lang}.xml"
        if not p.is_file():
            errors.append(f"缺生成檔 {p}")
            continue
        raw = p.read_bytes()
        text, dec_err = _decode_xml_bytes(raw)
        if dec_err or text is None:
            errors.append(f"{lang} {dec_err}")
            continue
        xml_bytes[lang] = raw
        xmls[lang] = text
    if len(xmls) != len(LANGS):
        return Result(False, errors, warnings)

    errors.extend(_verify_self_consistency(names_map, xmls))

    roots = iter_workshop_roots(prefer, include_default=include_default_workshop)
    xml_path = find_streets_xml(roots, wid, map_dir) if wid and map_dir else None
    if xml_path is None:
        warnings.append(
            "無上游副本，跳過上游比對（僅自洽：三語完整／撞名／BOM／三檔幾何互相一致）"
        )
        if errors:
            return Result(False, errors, warnings)
        return Result(True, [], warnings)

    raw_up = xml_path.read_bytes()
    up_text, dec_err = _decode_xml_bytes(raw_up)
    if dec_err or up_text is None:
        return Result(False, errors + [f"上游 XML {dec_err}"], warnings)

    keep = _keep_geometry(data)
    up_names = extract_name_values(up_text)
    unique_en = kept_unique_names(up_text, keep)
    per_lang, comp_err, _ = _check_completeness(
        unique_en, names_map, allow_partial=False
    )
    errors.extend(comp_err)
    errors.extend(_check_collisions(unique_en, per_lang))
    if errors:
        return Result(False, errors, warnings)

    # 最強驗證：重跑 gen 的同一支確定性轉換，與生成檔**逐字節**比對。
    # 這一次比對同時涵蓋幾何正規化、保留清單剔除、譯名、格式、換行、編碼。
    for lang in LANGS:
        expected, t_err, _, _ = _transform_xml(
            up_text, per_lang[lang], allow_partial=False, keep_geometry=keep
        )
        if t_err or expected is None:
            errors.append(f"{lang} 無法重現轉換：{'; '.join(t_err)}")
            continue
        if xmls[lang] != expected:
            # 逐項細分，讓失敗訊息可行動（而非只說「不一致」）
            base, _, _, _ = _transform_xml(
                up_text, None, allow_partial=True, keep_geometry=keep
            )
            if base is not None and strip_name_attrs(xmls[lang]) != strip_name_attrs(base):
                errors.append(f"{lang} 幾何與「上游套正規化（含剔除）」不符（檔案被手改？）")
            exp_names = extract_name_values(expected)
            got = extract_name_values(xmls[lang])
            if len(got) != len(exp_names):
                errors.append(f"{lang} street 數 {len(got)} ≠ 預期 {len(exp_names)}")
            else:
                for i, (exp_name, got_name) in enumerate(zip(exp_names, got)):
                    if got_name != exp_name:
                        errors.append(
                            f"{lang} street[{i}] 譯名 {got_name!r} ≠ 預期 {exp_name!r}"
                        )
            if not errors:
                errors.append(f"{lang} 與重跑轉換的結果逐字節不等（格式/換行差異？）")

    if errors:
        return Result(False, errors, warnings)
    return Result(True, [], warnings)


def extract_name_first_points(xml_text: str) -> list[tuple[str, int, int]]:
    """[(正規化英文名, x, y), ...] 依 street 出現順序；首點取第一個 <point>。

    座標整數化以對齊主 MOD MinidoracatMiniMapStreetNames 的既有格式
    （搜尋端用 math.floor(x)*100000+math.floor(y) 當去重鍵）。
    """
    out: list[tuple[str, int, int]] = []
    for block in _STREET_BLOCK_RE.findall(xml_text):
        nm = _NAME_ATTR_RE.search(block)
        pm = _POINT_RE.search(block)
        if not nm or not pm:
            continue
        name = normalize_name(xml_unescape(nm.group(1)))
        if not name:
            continue
        try:
            x = int(float(pm.group(1)))
            y = int(float(pm.group(2)))
        except ValueError:
            continue
        out.append((name, x, y))
    return out


def _lua_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def en_table_path(project_root: Path) -> Path:
    return (
        project_root
        / "MOD" / OWNER_MOD_ID / "Contents" / "mods" / OWNER_MOD_ID
        / EN_TABLE_REL
    )


def bake_english_table(
    files: list[Path],
    *,
    prefer: list[str],
    project_root: Path,
    include_default_workshop: bool = True,
) -> Result:
    """烘焙 MOD 地圖英文原名表（搜尋雙語用）。

    本包把 MOD 地圖街名整份替換成 CH/CN/JP 後，引擎街道索引只剩譯名——搜尋英文
    原名會無結果（主 MOD 對官方地圖早有同一問題，解法是 gen_street_names.py 烘焙
    MinidoracatMiniMapStreetNames）。本表補上 MOD 地圖那一段，格式與角色相同，
    直接 append 到主 MOD 的同一張全域表 → 主 MOD 搜尋端零改動。

    內容只依賴上游 streets.xml（英文原名＋首點），與翻譯完整性無關：某 dataset
    尚未譯完時該圖仍是英文，本表與引擎索引重複，由搜尋端首點去重處理。
    """
    roots = iter_workshop_roots(prefer, include_default=include_default_workshop)
    rows: list[tuple[str, int, int]] = []
    errors: list[str] = []
    warnings: list[str] = []
    used = 0
    for path in files:
        ds = path.parent.name
        try:
            data = read_names_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{ds}：names.json 無法讀取（{exc}）")
            continue
        workshop_id, _map_mod, map_dir, _sha = _source_meta(data)
        xml = (
            find_streets_xml(roots, workshop_id, map_dir)
            if workshop_id and map_dir
            else None
        )
        if xml is None:
            warnings.append(f"{ds}：找不到上游 streets.xml，英文原名表略過該組")
            continue
        text, err = _decode_xml_bytes(xml.read_bytes())
        if text is None:
            errors.append(f"{ds}：上游 streets.xml {err}")
            continue
        # 剔除清單要跟著套：被 keep_geometry 剔除的街不是本包替換的（它們維持由
        # 官方那份 streets.xml 顯示），主 MOD 的 MinidoracatMiniMapStreetNames 已含
        # 其英文原名 ⇒ 這裡再烘一次會讓同一街名在搜尋結果出現兩筆同座標條目。
        # 首點必須取「正規化後」的幾何：引擎索引裡的是替代檔（已正規化）的座標，
        # 用上游原始首點會讓搜尋跳轉位置偏掉，也讓搜尋端的首點去重鍵對不上。
        norm_text, n_err, _, _ = _transform_xml(
            text, None, allow_partial=True, keep_geometry=_keep_geometry(data)
        )
        if n_err or norm_text is None:
            errors.append(f"{ds}：幾何正規化失敗，英文原名表略過")
            continue
        rows.extend(extract_name_first_points(norm_text))
        used += 1
    if errors:
        return Result(False, errors, warnings)
    if not rows:
        warnings.append("英文原名表：沒有可烘焙的條目，跳過寫檔")
        return Result(True, [], warnings)
    lines = [
        "-- MinidoracatMiniMapModMapsStreetNames.lua（生成檔，勿手編）",
        "-- 由 scripts/gen_streets_i18n.py 烘焙自各地圖 MOD 上游 streets.xml 的英文原名。",
        "--",
        "-- 為何需要：本包把 MOD 地圖街名整份替換成 CH/CN/JP 後，引擎街道索引只剩譯名，",
        "-- 用英文原名搜尋會無結果（主 MOD 對官方地圖早有同一問題，解法是",
        "-- gen_street_names.py 烘焙 MinidoracatMiniMapStreetNames）。本表補 MOD 地圖那段，",
        f"-- 格式與角色相同，直接 append 到同一張全域表 {EN_TABLE_GLOBAL} → 搜尋端零改動。",
        "-- n=顯示名 l=預小寫 x/y=首點（與引擎索引同源）。",
        "--",
        "-- 載入序：mod.info require=MinidoracatMiniMapFor42 保證主 MOD 的表先定義（同",
        "-- registerMaps 依賴的同一個保證）；缺席時自建，不讓它變成 nil 索引錯誤。",
        f"-- 來源 {used} 個 dataset／{len(rows)} 條；上游變更時重跑生成器。",
        f'if type({EN_TABLE_GLOBAL}) ~= "table" then',
        f"    {EN_TABLE_GLOBAL} = {{}}",
        "end",
        f"local t = {EN_TABLE_GLOBAL}",
        "local function a(n, l, x, y) t[#t + 1] = { n = n, l = l, x = x, y = y } end",
    ]
    for name, x, y in rows:
        lines.append(f"a({_lua_str(name)}, {_lua_str(name.lower())}, {x}, {y})")
    out = en_table_path(project_root)
    write_bytes_atomic(out, ("\n".join(lines) + "\n").encode("utf-8"))
    return Result(True, [], warnings)


def _print_result(label: str, result: Result) -> None:
    for w in result.warnings:
        warn(f"{label} {w}")
    if result.ok:
        print(f"✅ {label}")
        return
    print(f"❌ {label}", file=sys.stderr)
    for e in result.errors:
        print(f"     {e}", file=sys.stderr)


def cmd_gen(args: argparse.Namespace, *, project_root: Path | None = None) -> int:
    root = project_root or PROJECT_ROOT
    street_names = root / "street-names"
    files = discover_names_files(street_names, args.dataset)
    if args.dataset and (not files or not files[0].is_file()):
        print(f"❌ 找不到 dataset {args.dataset!r} 的 names.json", file=sys.stderr)
        return 1
    if not files:
        print("無 dataset 可生成（street-names/*/names.json 不存在）")
        return 0
    rc = 0
    for path in files:
        ds = path.parent.name
        result = gen_dataset(
            path,
            prefer=args.prefer,
            project_root=root,
            update_hash=args.update_hash,
            allow_partial=args.allow_partial,
        )
        _print_result(f"gen {ds}", result)
        if result.ok:
            out = output_dir_for(root, ds)
            print(f"   → {out.relative_to(root) if out.is_relative_to(root) else out}")
        else:
            rc = 1
    # 英文原名表：只依賴上游 XML，個別 dataset 譯稿未完成不影響（見 bake_english_table）
    en = bake_english_table(files, prefer=args.prefer, project_root=root)
    _print_result("bake 英文原名表", en)
    if not en.ok:
        rc = 1
    return rc


def cmd_keep_scan(args: argparse.Namespace, *, project_root: Path | None = None) -> int:
    """比對 vanilla 全域街道表，重算各 dataset 的 `source.keep_geometry`。

    只有本命令需要遊戲安裝目錄；`gen`/`verify` 一律只讀 names.json 的指紋清單
    ⇒ CI 不必有 vanilla 參考檔。上游改街名後重跑本命令即可。
    """
    root = project_root or PROJECT_ROOT
    van_path = find_vanilla_streets(Path(args.game) if args.game else None)
    if van_path is None:
        print("❌ 找不到 vanilla streets.xml；用 --game 指定遊戲安裝目錄", file=sys.stderr)
        return 1
    van_text, err = _decode_xml_bytes(van_path.read_bytes())
    if van_text is None:
        print(f"❌ vanilla streets.xml {err}", file=sys.stderr)
        return 1
    vanilla = VanillaStreets(van_text)
    try:
        bounds_map = read_registry_bounds(root)
    except OSError as exc:
        print(f"❌ 讀不到 registry：{exc}", file=sys.stderr)
        return 1
    print(f"vanilla 基準 {len(vanilla)} 條（{van_path}）｜registry bounds {len(bounds_map)} 組")
    files = discover_names_files(root / "street-names", args.dataset)
    if args.dataset and (not files or not files[0].is_file()):
        print(f"❌ 找不到 dataset {args.dataset!r} 的 names.json", file=sys.stderr)
        return 1
    roots = iter_workshop_roots(args.prefer)
    rc, dead = 0, []
    for path in files:
        ds = path.parent.name
        try:
            data = read_names_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"❌ {ds}：names.json 無法讀取（{exc}）", file=sys.stderr)
            rc = 1
            continue
        workshop_id, _mm, map_dir, _sha = _source_meta(data)
        xml = find_streets_xml(roots, workshop_id, map_dir)
        if xml is None:
            warn(f"{ds} 找不到上游 streets.xml，略過（指紋不變）")
            continue
        text, err = _decode_xml_bytes(xml.read_bytes())
        if text is None:
            print(f"❌ {ds}：上游 streets.xml {err}", file=sys.stderr)
            rc = 1
            continue
        keep, stats, samples = scan_keep_geometry(text, vanilla, bounds_map.get(ds))
        total = sum(
            stats[k] for k in ("same", "near", "clash", "overlay", "oob", "keep")
        )
        print(
            f"  {ds:<24} 上游 {total:>4}｜幾何同 {stats['same']:>4}"
            f"｜近似 {stats['near']:>3}｜撞名 {stats['clash']:>3}"
            f"｜蓋官方路 {stats['overlay']:>3}｜範圍外 {stats['oob']:>4}"
            f"｜保留 {stats['keep']:>4}"
        )
        for nm, why in samples:
            print(f"       剔除: {nm} ({why})")
        if not keep:
            dead.append(ds)
            continue
        if args.write:
            src = data.setdefault("source", {})
            # 全部保留＝不需要清單；留著只會讓上游新增街道時 verify 誤報
            if stats["keep"] == total:
                src.pop("keep_geometry", None)
                needed = None
            else:
                src["keep_geometry"] = sorted(set(keep))
                needed = set(kept_unique_names(text, set(keep)))
            # 剔除後不再出現的譯名＝死資料。留著會讓「翻了幾條」失真，也讓下次
            # 覆核分不清哪些仍在用；譯稿本身在 git 歷史裡，需要時取回。
            if needed is not None:
                stale = [n for n in data.get("names", {}) if n not in needed]
                for n in stale:
                    data["names"].pop(n, None)
                if stale:
                    print(f"       清理不再需要的譯名 {len(stale)} 條")
            write_bytes_atomic(
                path, (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            )
    if dead:
        print(
            f"\n⚠ 下列 {len(dead)} 個 dataset 零獨有街道（整份都是官方街道的複本）"
            f"，應從 registry 與 street-names 移除：",
            file=sys.stderr,
        )
        for ds in dead:
            print(f"     {ds}", file=sys.stderr)
    if args.write:
        print("\n已寫回 names.json；接著跑 gen 重生並補齊新出現的譯名")
    else:
        print("\n（未加 --write：以上只是掃描結果）")
    return rc


def cmd_verify(args: argparse.Namespace, *, project_root: Path | None = None) -> int:
    root = project_root or PROJECT_ROOT
    street_names = root / "street-names"
    files = discover_names_files(street_names, args.dataset)
    if args.dataset and (not files or not files[0].is_file()):
        print(f"❌ 找不到 dataset {args.dataset!r} 的 names.json", file=sys.stderr)
        return 1
    if not files:
        print("無 dataset 可驗證（street-names/*/names.json 不存在）")
        return 0
    rc = 0
    for path in files:
        ds = path.parent.name
        result = verify_dataset(
            path,
            prefer=args.prefer,
            project_root=root,
        )
        _print_result(f"verify {ds}", result)
        if not result.ok:
            rc = 1
    # 英文原名表：搜尋雙語的另一半，缺檔＝英文原名搜不到（靜默功能缺口）
    table = en_table_path(root)
    if not table.is_file():
        print(f"❌ verify 英文原名表：缺檔 {table.name}"
              "（跑 gen 產生；否則 MOD 地圖無法用英文原名搜尋）", file=sys.stderr)
        rc = 1
    else:
        raw = table.read_bytes()
        n = raw.count(b"\na(")
        if _has_bom(raw):
            print("❌ verify 英文原名表：UTF-8 BOM（禁止）", file=sys.stderr)
            rc = 1
        elif n == 0:
            print("❌ verify 英文原名表：0 條", file=sys.stderr)
            rc = 1
        else:
            print(f"✅ verify 英文原名表（{n} 條）")
    return rc


# ============================================================
# selftest（自造迷你 fixture，不依賴真 names.json／真 workshop）
# ============================================================
_FIXTURE_XML = (
    '<streets version="1">\r\n'
    '    <street name="Forest  St" width="11">\r\n'
    "        <points>\r\n"
    '            <point x="1.0" y="2.0"/>\r\n'
    "        </points>\r\n"
    "    </street>\r\n"
    '    <street name="Foo &amp; Bar" width="8">\r\n'
    "        <points>\r\n"
    '            <point x="3.0" y="4.0"/>\r\n'
    "        </points>\r\n"
    "    </street>\r\n"
    '    <street name="Main St" width="5">\r\n'
    "        <points>\r\n"
    '            <point x="5.0" y="6.0"/>\r\n'
    "        </points>\r\n"
    "    </street>\r\n"
    '    <street name="Main St" width="6">\r\n'
    "        <points>\r\n"
    '            <point x="7.0" y="8.0"/>\r\n'
    "        </points>\r\n"
    "    </street>\r\n"
    "</streets>\r\n"
)

_FIXTURE_NAMES = {
    "Forest St": {"ch": "森林街", "cn": "森林街", "jp": "森通り"},
    "Foo & Bar": {"ch": "福與吧", "cn": "福与吧", "jp": "フー・アンド・バー"},
    "Main St": {"ch": "主街", "cn": "主街", "jp": "メイン通り"},
}


def _write_layout(
    root: Path,
    *,
    xml_text: str = _FIXTURE_XML,
    names: dict | None = None,
    dataset: str = "demo",
    workshop_id: str = "999",
    map_dir: str = "DemoMap",
    sha: str | None = None,
) -> tuple[Path, Path]:
    xml_path = (
        root / "workshop" / workshop_id / "mods" / "Demo" / "common"
        / "media" / "maps" / map_dir / "streets.xml"
    )
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    xml_path.write_bytes(xml_text.encode("utf-8"))
    computed = file_sha256(xml_path)
    names_path = root / "street-names" / dataset / "names.json"
    names_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "dataset": dataset,
        "source": {
            "workshop_id": workshop_id,
            "map_mod": "Demo",
            "map_dir": map_dir,
            "streets_xml_sha256": sha if sha is not None else computed,
            "captured": "2026-08-26",
        },
        "names": names if names is not None else dict(_FIXTURE_NAMES),
    }
    write_names_json(names_path, payload)
    return names_path, xml_path


def _gen(root: Path, names_path: Path, **kw) -> Result:
    return gen_dataset(
        names_path,
        prefer=[str(root / "workshop")],
        project_root=root,
        include_default_workshop=False,
        **kw,
    )


def _ver(root: Path, names_path: Path, **kw) -> Result:
    return verify_dataset(
        names_path,
        prefer=[str(root / "workshop")],
        project_root=root,
        include_default_workshop=False,
        **kw,
    )


def cmd_selftest() -> int:
    n_ok = 0
    n_all = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal n_ok, n_all
        n_all += 1
        if cond:
            n_ok += 1
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}" + (f"：{detail}" if detail else ""))

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)

        # 1) happy：多重空白、XML 轉義、重複名、CRLF、往返 verify
        happy = base / "happy"
        np, xp = _write_layout(happy)
        r = _gen(happy, np)
        check("happy gen", r.ok, "; ".join(r.errors))
        ch = (output_dir_for(happy, "demo") / "streets_CH.xml").read_bytes()
        check("happy 無 BOM", not _has_bom(ch))
        check("happy 保留 CRLF", ch.count(b"\r\n") == _FIXTURE_XML.encode().count(b"\r\n"))
        ch_text = ch.decode("utf-8")
        check("happy 髒名查表 Forest  St→森林街", 'name="森林街"' in ch_text)
        check("happy 重複名共用譯", ch_text.count('name="主街"') == 2)
        check("happy 未改 width", 'width="11"' in ch_text and 'width="6"' in ch_text)
        jp = (output_dir_for(happy, "demo") / "streets_JP.xml").read_text(encoding="utf-8")
        check("happy JP 片假名", "フー・アンド・バー" in jp)
        # 上游 &amp; 在英文側；譯名無特殊字元。另測譯名跳脫寫入：
        r2 = _ver(happy, np)
        check("happy verify", r2.ok, "; ".join(r2.errors))

        # 1b) 譯名含 & 與 " 的跳脫
        esc = base / "escape"
        names_esc = {
            **_FIXTURE_NAMES,
            "Foo & Bar": {"ch": '福&吧 "x"', "cn": "福与吧", "jp": "フー"},
        }
        np_e, _ = _write_layout(esc, names=names_esc)
        r = _gen(esc, np_e)
        check("escape gen", r.ok, "; ".join(r.errors))
        ch_e = (output_dir_for(esc, "demo") / "streets_CH.xml").read_text(encoding="utf-8")
        check(
            "escape 寫出 &amp; / &quot;",
            'name="福&amp;吧 &quot;x&quot;"' in ch_e,
            ch_e[ch_e.find("name=") : ch_e.find("name=") + 80] if "name=" in ch_e else ch_e[:80],
        )
        check("escape verify", _ver(esc, np_e).ok)

        # 2) 缺譯 → fail、不寫檔
        miss = base / "missing"
        names_m = {
            "Forest St": {"ch": "森林街", "cn": "森林街", "jp": "森通り"},
            "Foo & Bar": {"ch": "福與吧", "cn": "福与吧", "jp": "フー"},
            "Main St": {"ch": "主街", "cn": "主街"},  # 缺 jp
        }
        np_m, _ = _write_layout(miss, names=names_m)
        r = _gen(miss, np_m)
        out_m = output_dir_for(miss, "demo")
        check("缺譯 fail", not r.ok and any("缺 jp" in e for e in r.errors), "; ".join(r.errors))
        check("缺譯不寫檔", not (out_m / "streets_CH.xml").exists())

        # 3) --allow-partial 填英文＋warning、有寫檔
        r = _gen(miss, np_m, allow_partial=True)
        check("allow-partial gen", r.ok, "; ".join(r.errors))
        check("allow-partial warning", any("缺 jp" in w for w in r.warnings))
        ch_p = (out_m / "streets_CH.xml").read_text(encoding="utf-8")
        jp_p = (out_m / "streets_JP.xml").read_text(encoding="utf-8")
        check("allow-partial JP 填 Main St 原文", 'name="Main St"' in jp_p)
        check("allow-partial CH 仍有譯", 'name="主街"' in ch_p)

        # 4) 撞名
        col = base / "collide"
        names_c = {
            "Forest St": {"ch": "主街", "cn": "森林街", "jp": "森通り"},
            "Foo & Bar": {"ch": "福與吧", "cn": "福与吧", "jp": "フー"},
            "Main St": {"ch": "主街", "cn": "主街", "jp": "メイン通り"},
        }
        np_c, _ = _write_layout(col, names=names_c)
        r = _gen(col, np_c)
        check(
            "撞名 fail",
            not r.ok and any("撞名" in e for e in r.errors),
            "; ".join(r.errors),
        )
        check("撞名列出對", any("Forest St" in e and "Main St" in e for e in r.errors))

        # 5) sha256 不符 → fail、列 unique 差異
        badh = base / "badhash"
        np_h, xp_h = _write_layout(badh, sha="0" * 64)
        r = _gen(badh, np_h)
        check(
            "hash 不符 fail",
            not r.ok and any("sha256 不符" in e for e in r.errors),
            "; ".join(r.errors),
        )
        extra_xml = _FIXTURE_XML.replace(
            "</streets>",
            '    <street name="New Rd" width="3">\r\n'
            "        <points>\r\n"
            '            <point x="9.0" y="9.0"/>\r\n'
            "        </points>\r\n"
            "    </street>\r\n"
            "</streets>",
        )
        xp_h.write_bytes(extra_xml.encode("utf-8"))
        r = _gen(badh, np_h)
        check(
            "hash 不符列新增 unique",
            not r.ok and any("New Rd" in e for e in r.errors),
            "; ".join(r.errors),
        )

        # 6) --update-hash 接受新上游、寫回 metadata、缺譯仍 fail
        upd = base / "update"
        np_u, xp_u = _write_layout(upd, sha="0" * 64)
        r = _gen(upd, np_u, update_hash=True)
        check("update-hash 完整譯 gen", r.ok, "; ".join(r.errors))
        new_sha = json.loads(np_u.read_text(encoding="utf-8"))["source"]["streets_xml_sha256"]
        check("update-hash 寫回 sha", new_sha == file_sha256(xp_u) and new_sha != "0" * 64)

        names_u = {
            **_FIXTURE_NAMES,
            # 不包含即將新增的 New Rd
        }
        np_u2, xp_u2 = _write_layout(upd / "partial", names=names_u, sha="0" * 64)
        xp_u2.write_bytes(extra_xml.encode("utf-8"))
        r = _gen(upd / "partial", np_u2, update_hash=True)
        check(
            "update-hash 仍列缺譯",
            not r.ok and any("New Rd" in e for e in r.errors),
            "; ".join(r.errors),
        )
        written_sha = json.loads(np_u2.read_text(encoding="utf-8"))["source"]["streets_xml_sha256"]
        check("update-hash 缺譯仍寫回 sha", written_sha == file_sha256(xp_u2))

        # 7) verify 無上游：自洽通過並提示跳過
        no_up = base / "noupstream"
        np_n, _ = _write_layout(no_up)
        check("noupstream 先 gen", _gen(no_up, np_n).ok)
        # 拆掉 workshop 副本
        xml_gone = (
            no_up / "workshop" / "999" / "mods" / "Demo" / "common"
            / "media" / "maps" / "DemoMap" / "streets.xml"
        )
        xml_gone.unlink()
        r = _ver(no_up, np_n)
        check("verify 無上游 ok", r.ok, "; ".join(r.errors))
        check(
            "verify 無上游提示跳過",
            any("跳過上游比對" in w for w in r.warnings),
            "; ".join(r.warnings),
        )

        # 8) verify 幾何破壞
        geom = base / "geom"
        np_g, _ = _write_layout(geom)
        check("geom 先 gen", _gen(geom, np_g).ok)
        chp = output_dir_for(geom, "demo") / "streets_CH.xml"
        broken = chp.read_bytes().replace(b'width="11"', b'width="99"', 1)
        chp.write_bytes(broken)
        r = _ver(geom, np_g)
        check("verify 幾何失敗", not r.ok, "; ".join(r.errors))

        # 9) verify BOM
        bom = base / "bom"
        np_b, _ = _write_layout(bom)
        check("bom 先 gen", _gen(bom, np_b).ok)
        bp = output_dir_for(bom, "demo") / "streets_CN.xml"
        bp.write_bytes(b"\xef\xbb\xbf" + bp.read_bytes())
        r = _ver(bom, np_b)
        check(
            "verify BOM 失敗",
            not r.ok and any("BOM" in e for e in r.errors),
            "; ".join(r.errors),
        )

        # 10) 三檔互不一致（無上游時也要抓到）
        drift = base / "drift"
        np_d, _ = _write_layout(drift)
        check("drift 先 gen", _gen(drift, np_d).ok)
        jp_d = output_dir_for(drift, "demo") / "streets_JP.xml"
        jp_d.write_bytes(jp_d.read_bytes().replace(b'width="8"', b'width="7"', 1))
        xml_d = (
            drift / "workshop" / "999" / "mods" / "Demo" / "common"
            / "media" / "maps" / "DemoMap" / "streets.xml"
        )
        xml_d.unlink()
        r = _ver(drift, np_d)
        check("verify 三檔互不一致", not r.ok, "; ".join(r.errors))

        # 11) LF 上游換行符原樣保留（Daisy 風格）
        lf = base / "lf"
        xml_lf = _FIXTURE_XML.replace("\r\n", "\n")
        np_lf, _ = _write_layout(lf, xml_text=xml_lf)
        r = _gen(lf, np_lf)
        check("lf gen", r.ok, "; ".join(r.errors))
        lf_bytes = (output_dir_for(lf, "demo") / "streets_CH.xml").read_bytes()
        check("lf 無 CR", b"\r" not in lf_bytes and lf_bytes.count(b"\n") == xml_lf.encode().count(b"\n"))
        check("lf verify", _ver(lf, np_lf).ok)

        # 12) 定位：common 與 42*；prefer 優先
        loc = base / "locate"
        # 42.20 與 common 都放，42.20 應優先
        p42 = (
            loc / "wsA" / "111" / "mods" / "M" / "42.20" / "media" / "maps" / "X" / "streets.xml"
        )
        pco = (
            loc / "wsA" / "111" / "mods" / "M" / "common" / "media" / "maps" / "X" / "streets.xml"
        )
        p42.parent.mkdir(parents=True, exist_ok=True)
        pco.parent.mkdir(parents=True, exist_ok=True)
        p42.write_bytes(b"<streets version=\"1\">from42</streets>")
        pco.write_bytes(b"<streets version=\"1\">fromcommon</streets>")
        hit = find_streets_xml([loc / "wsA"], "111", "X")
        check("locate 42* 優先於 common", hit == p42, str(hit))
        p_pref = (
            loc / "wsB" / "111" / "mods" / "M" / "common" / "media" / "maps" / "X" / "streets.xml"
        )
        p_pref.parent.mkdir(parents=True, exist_ok=True)
        p_pref.write_bytes(b"<streets version=\"1\">prefer</streets>")
        hit2 = find_streets_xml([loc / "wsB", loc / "wsA"], "111", "X")
        check("locate --prefer 先掃者勝出", hit2 == p_pref, str(hit2))
        # Daisy 空格 map_dir
        daisy = (
            loc / "wsA" / "3390753141" / "mods" / "Daisy County B42 version"
            / "common" / "media" / "maps" / "Daisy County" / "streets.xml"
        )
        daisy.parent.mkdir(parents=True, exist_ok=True)
        daisy.write_bytes(b"<streets version=\"1\"/>")
        hit3 = find_streets_xml([loc / "wsA"], "3390753141", "Daisy County")
        check("locate 空格 map_dir", hit3 == daisy, str(hit3))

    # 英文原名表烘焙（搜尋雙語用）
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        names_path, _ = _write_layout(root)
        res = bake_english_table(
            [names_path],
            prefer=[str(root / "workshop")],
            project_root=root,
            include_default_workshop=False,
        )
        check("bake ok", res.ok, "; ".join(res.errors))
        out = en_table_path(root)
        check("bake 產檔", out.is_file())
        if out.is_file():
            raw = out.read_bytes()
            txt = raw.decode("utf-8")
            check("bake 無 BOM", not _has_bom(raw))
            check("bake append 樣板", f"local t = {EN_TABLE_GLOBAL}" in txt)
            check(
                "bake 名稱正規化＋座標整數化",
                'a("Forest St", "forest st", 1, 2)' in txt,
            )
            check(
                "bake XML unescape（&amp; → &）",
                'a("Foo & Bar", "foo & bar", 3, 4)' in txt,
            )
            check("bake 重複名各留一條", txt.count('a("Main St"') == 2)
            check("bake 首點對應各段", '"main st", 5, 6)' in txt and '"main st", 7, 8)' in txt)
        # 缺上游副本＝warning 不寫檔（不可靜默產半套表）
        with tempfile.TemporaryDirectory() as d2:
            root2 = Path(d2)
            np2, _ = _write_layout(root2)
            res2 = bake_english_table(
                [np2],
                prefer=[str(root2 / "nonexistent")],
                project_root=root2,
                include_default_workshop=False,
            )
            check("bake 缺上游→warning", res2.ok and bool(res2.warnings))
            check("bake 缺上游→不寫檔", not en_table_path(root2).is_file())

    # 幾何正規化（輪廓矩形 → 中心線）
    _RECT_XML = (
        '<streets version="1">\r\n'
        '    <street name="Rect Ave" width="10">\r\n'      # 200x10 細長 → 應轉
        "        <points>\r\n"
        '            <point x="100" y="50"/>\r\n'
        '            <point x="300" y="50"/>\r\n'
        '            <point x="300" y="60"/>\r\n'
        '            <point x="100" y="60"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        '    <street name="Ring Rd" width="10">\r\n'       # 100x100 方形 → 比例不足，不轉
        "        <points>\r\n"
        '            <point x="0" y="0"/>\r\n'
        '            <point x="100" y="0"/>\r\n'
        '            <point x="100" y="100"/>\r\n'
        '            <point x="0" y="100"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        '    <street name="Bend St" width="10">\r\n'       # L 形 4 點 → 非矩形，不轉
        "        <points>\r\n"
        '            <point x="0" y="0"/>\r\n'
        '            <point x="50" y="0"/>\r\n'
        '            <point x="50" y="50"/>\r\n'
        '            <point x="90" y="70"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        '    <street name="Wide Loop" width="10">\r\n'     # 短邊 40 > max(15,16) → 不轉
        "        <points>\r\n"
        '            <point x="0" y="200"/>\r\n'
        '            <point x="500" y="200"/>\r\n'
        '            <point x="500" y="240"/>\r\n'
        '            <point x="0" y="240"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        "</streets>\r\n"
    )
    _RECT_NAMES = {
        "Rect Ave": {"ch": "矩街", "cn": "矩街", "jp": "矩通り"},
        "Ring Rd": {"ch": "環路", "cn": "环路", "jp": "リング・ロード"},
        "Bend St": {"ch": "彎街", "cn": "弯街", "jp": "ベンド通り"},
        "Wide Loop": {"ch": "寬環", "cn": "宽环", "jp": "ワイド・ループ"},
    }
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        names_path, _ = _write_layout(root, xml_text=_RECT_XML, names=_RECT_NAMES)
        res = _gen(root, names_path)
        check("geom gen ok", res.ok, "; ".join(res.errors))
        out = output_dir_for(root, "demo") / "streets_CH.xml"
        if out.is_file():
            txt = out.read_text(encoding="utf-8")
            blocks = re.findall(r"<street\b.*?</street>", txt, re.S)
            pts_of = lambda b: _POINT_RE.findall(b)
            check("geom 矩形→中心線 2 點", len(pts_of(blocks[0])) == 2)
            check(
                "geom 中心線取短邊中點",
                pts_of(blocks[0]) == [("100", "55"), ("300", "55")],
                str(pts_of(blocks[0])),
            )
            check("geom 方形環路不動", len(pts_of(blocks[1])) == 4)
            check("geom L 形不動", len(pts_of(blocks[2])) == 4)
            check("geom 短邊過寬不動", len(pts_of(blocks[3])) == 4)
            check("geom 保留 width", 'width="10"' in blocks[0])
            # 用 bytes 驗：read_text 的 universal newlines 會把 \r\n 正規化成 \n
            check(
                "geom 保留 CRLF 與縮排",
                b'\r\n            <point x="100" y="55"/>' in out.read_bytes(),
            )
        check("geom verify ok", _ver(root, names_path).ok)
        # 逐字節比對：手改生成檔（改一個座標）必須被抓到
        if out.is_file():
            tampered = out.read_text(encoding="utf-8").replace('y="55"', 'y="56"', 1)
            out.write_bytes(tampered.encode("utf-8"))
            r_bad = _ver(root, names_path)
            check("geom verify 抓到手改幾何", not r_bad.ok, "; ".join(r_bad.errors))

    # keep-scan 四道剔除：拿一份「官方表」與一份「上游表」對打
    _VAN = (
        '<streets version="1">\r\n'
        '    <street name="Copy Road" width="5">\r\n'          # 1 same：整條照抄
        "        <points>\r\n"
        '            <point x="100" y="200"/>\r\n'
        '            <point x="400" y="200"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        '    <street name="Shift St" width="5">\r\n'           # 2 near：端點位移 1
        "        <points>\r\n"
        '            <point x="100" y="300"/>\r\n'
        '            <point x="400" y="300"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        '    <street name="Pony Trot Road" width="5">\r\n'     # 3 clash：後綴縮寫＋共線
        "        <points>\r\n"
        '            <point x="100" y="400"/>\r\n'
        '            <point x="400" y="400"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        "</streets>\r\n"
    )
    _UP = (
        '<streets version="1">\r\n'
        '    <street name="Copy Road" width="5">\r\n'
        "        <points>\r\n"
        '            <point x="100" y="200"/>\r\n'
        '            <point x="400" y="200"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        '    <street name="Shift St" width="5">\r\n'
        "        <points>\r\n"
        '            <point x="100" y="300"/>\r\n'
        '            <point x="400" y="301"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        '    <street name="Pony Trot Rd" width="5">\r\n'
        "        <points>\r\n"
        '            <point x="150" y="400"/>\r\n'
        '            <point x="380" y="400"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        '    <street name="Mine Ave" width="5">\r\n'           # 4 oob：本圖範圍外
        "        <points>\r\n"
        '            <point x="9000" y="9000"/>\r\n'
        '            <point x="9200" y="9000"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        '    <street name="Mine Own Way" width="5">\r\n'       # keep：作者自己畫的
        "        <points>\r\n"
        '            <point x="120" y="700"/>\r\n'
        '            <point x="360" y="700"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        "</streets>\r\n"
    )
    van_idx = VanillaStreets(_VAN)
    check("keep-scan vanilla 索引條數", len(van_idx) == 3)
    kg, st, samples = scan_keep_geometry(_UP, van_idx, [0, 0, 1000, 1000])
    check("keep-scan 幾何完全相同→same", st["same"] == 1, str(st))
    check("keep-scan 端點位移→near", st["near"] == 1, str(st))
    check("keep-scan 後綴縮寫共線→clash", st["clash"] == 1, str(st))
    check("keep-scan bounds 外→oob", st["oob"] == 1, str(st))
    check("keep-scan 只留作者自畫的", st["keep"] == 1 and len(kg) == 1, str(st))
    check("keep-scan 撞名樣本可讀", bool(samples) and samples[0][0].startswith("Pony Trot Rd"))
    # 指紋必須能餵回 _transform_xml 精確剔除
    only, errs, _, _ = _transform_xml(_UP, None, allow_partial=True, keep_geometry=set(kg))
    check("keep-scan 指紋餵回只剩 1 條", not errs and only.count("<street ") == 1, str(errs))
    check("keep-scan 留下的是 Mine Own Way", 'name="Mine Own Way"' in (only or ""))
    # 無 bounds＝不做空間閘門（bounds 缺席時不可誤剔）
    _, st2, _ = scan_keep_geometry(_UP, van_idx, None)
    check("keep-scan 無 bounds 不做空間剔除", st2["oob"] == 0 and st2["keep"] == 2, str(st2))
    check("_match_key 後綴縮寫等同", _match_key("Pony Trot Road") == _match_key("Pony Trot Rd"))
    check("_match_key 不同名不等同", _match_key("Ivy Road") != _match_key("Raccoon Road"))
    check(
        "_axis_segments 斜段不計入",
        _axis_segments([(0.0, 0.0), (10.0, 10.0)]) == [],
    )

    # overlay：不分名字的共線。判定用「重疊比例」而非絕對長度——
    # 100% 蓋住＝作者把官方路改名（剔除）；只有路口相接的短重疊＝作者新增的路（保留）。
    _VAN_OV = (
        '<streets version="1">\r\n'
        '    <street name="Official Road" width="5">\r\n'
        "        <points>\r\n"
        '            <point x="0" y="500"/>\r\n'
        '            <point x="1000" y="500"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        "</streets>\r\n"
    )
    _UP_OV = (
        '<streets version="1">\r\n'
        '    <street name="Renamed Ave" width="5">\r\n'        # 整條蓋在官方路上 → 剔
        "        <points>\r\n"
        '            <point x="200" y="500"/>\r\n'
        '            <point x="500" y="500"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        '    <street name="Junction Ln" width="5">\r\n'        # 只有路口 30/430 → 留
        "        <points>\r\n"
        '            <point x="600" y="500"/>\r\n'
        '            <point x="630" y="500"/>\r\n'
        '            <point x="630" y="900"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        '    <street name="Outline Blvd" width="20">\r\n'      # 矩形輪廓，中心線才共線 → 剔
        "        <points>\r\n"
        '            <point x="100" y="490"/>\r\n'
        '            <point x="400" y="490"/>\r\n'
        '            <point x="400" y="510"/>\r\n'
        '            <point x="100" y="510"/>\r\n'
        "        </points>\r\n"
        "    </street>\r\n"
        "</streets>\r\n"
    )
    ov_idx = VanillaStreets(_VAN_OV)
    kg_ov, st_ov, samp_ov = scan_keep_geometry(_UP_OV, ov_idx, None)
    check("overlay 整條蓋住→剔除", st_ov["overlay"] == 2, str(st_ov))
    check("overlay 只有路口→保留", st_ov["keep"] == 1, str(st_ov))
    only_ov, e_ov, _, _ = _transform_xml(
        _UP_OV, None, allow_partial=True, keep_geometry=set(kg_ov)
    )
    check("overlay 保留的是 Junction Ln", 'name="Junction Ln"' in (only_ov or ""), str(e_ov))
    check(
        "overlay 矩形輪廓靠中心線判定",
        any("Outline Blvd" in s[0] for s in samp_ov),
        str(samp_ov),
    )
    # drawn_points：矩形輪廓 → 中心線；非輪廓 → 原樣
    _rect = [(100.0, 490.0), (400.0, 490.0), (400.0, 510.0), (100.0, 510.0)]
    check(
        "drawn_points 輪廓轉中心線",
        drawn_points('<street width="20">', _rect) == [(100.0, 500.0), (400.0, 500.0)],
    )
    _line = [(0.0, 0.0), (10.0, 0.0)]
    check("drawn_points 非輪廓不動", drawn_points('<street width="5">', _line) == _line)

    print(f"✅ selftest {n_ok}/{n_all} 通過" if n_ok == n_all else f"❌ selftest {n_ok}/{n_all}")
    return 0 if n_ok == n_all else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="自造 fixture 零依賴自我測試")
    sub = parser.add_subparsers(dest="cmd")

    gen_p = sub.add_parser("gen", help="由 names.json＋上游 streets.xml 生成三語 XML")
    gen_p.add_argument("--dataset", default="", help="只處理此 dataset id")
    gen_p.add_argument(
        "--prefer", action="append", default=[],
        help="優先的 workshop content 根（可重複；先給者勝出）",
    )
    gen_p.add_argument(
        "--update-hash", action="store_true",
        help="接受新上游 sha256 並寫回 names.json metadata（仍列缺譯）",
    )
    gen_p.add_argument(
        "--allow-partial", action="store_true",
        help="缺譯填英文原文（僅本機預覽；出貨／CI 勿用）",
    )

    ver_p = sub.add_parser("verify", help="對已生成檔重跑全部閘門")
    ver_p.add_argument("--dataset", default="", help="只驗證此 dataset id")
    ver_p.add_argument(
        "--prefer", action="append", default=[],
        help="優先的 workshop content 根（可重複；先給者勝出）",
    )

    ks_p = sub.add_parser(
        "keep-scan",
        help="比對 vanilla 街道表重算 keep_geometry（唯一需要遊戲安裝目錄的命令）",
    )
    ks_p.add_argument("--dataset", default="", help="只掃此 dataset id")
    ks_p.add_argument(
        "--prefer", action="append", default=[],
        help="優先的 workshop content 根（可重複；先給者勝出）",
    )
    ks_p.add_argument("--game", default="", help="遊戲安裝目錄（預設用內建路徑）")
    ks_p.add_argument("--write", action="store_true", help="寫回 names.json（預設只顯示）")

    args = parser.parse_args(argv)
    if args.selftest:
        return cmd_selftest()
    if args.cmd == "gen":
        if not args.dataset:
            args.dataset = None
        return cmd_gen(args)
    if args.cmd == "verify":
        if not args.dataset:
            args.dataset = None
        return cmd_verify(args)
    if args.cmd == "keep-scan":
        if not args.dataset:
            args.dataset = None
        return cmd_keep_scan(args)
    parser.error("需要子命令 gen / verify / keep-scan，或 --selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
