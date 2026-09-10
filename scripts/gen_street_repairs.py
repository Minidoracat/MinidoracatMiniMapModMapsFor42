#!/usr/bin/env python3
"""道路修正（street repairs）生成器：road-repairs/*.json → shared 全域表。

與 `gen_streets_i18n.py`（純街名翻譯）分屬兩條資料線：那支只管名字，這支只管幾何與
重複標籤。共用的只有「怎麼找到本機上游 streets.xml」「Lua 字面值怎麼寫」這類純
helper——直接 import 那支，不另寫第二套同慣例。

## 這支在做什麼

`road-repairs/<dataset>.json` 是**顯式修正 pin**：每一筆都寫死「當前上游第 N 條街的
width 與完整點列長這樣」，以及要對它做什麼（壓成中心線／隱藏玩家地圖上的路名）。
本生成器**只編譯 pin**，不掃描上游、不自己批准新座標——上游改版後要不要新增修正，
是人看過再加 pin 的事，不是 generator 偷偷決定的事。

執行期契約（主 MOD 負責實作）：逐值比對 `expectedWidth` / `expectedPoints`，不符就
**略過該筆並 log**，不擋同一張圖的其他修正、也不擋新道路。隱藏路名必附 `reference`
（vanilla 對應街道的 index/width/points）當 canonical 重複證據，執行期還要確認那條
canonical 道路仍在、仍看得見，才真的隱藏。所以「上游漂移」與「官方路網改版」兩種
情況都退回原樣，不會把路弄丟。

## pin 是怎麼得出來的（人工核准過的兩條規則，生成時逐筆強制驗）

1. **rect-outline → 中心線**（只有 Daisy County 44/44 條）：4 點、軸對齊、四角互異
   的閉合矩形，短邊 <= max(width*1.5, 16)、長邊 >= 短邊*3。作者把街道畫成輪廓矩形，
   而 `width` 本來就表達寬度 ⇒ 引擎在兩條長邊各畫一次路名（玩家看到上下兩行），
   NavRoute 也把四邊都當路段。壓成中心線後視覺與路網都對，width 保留 ⇒ 粗細不變。
   方環／L 形折線一律不套（`rect_centerline` 判定會自己擋掉）。
2. **exact-copy → 隱藏路名**：本圖某條街的原始點列與 vanilla 全域街道表某條**逐點
   相同**。引擎兩份都畫 ⇒ 同座標疊字。官方那份動不了，所以隱藏我方這份。

`replacementPoints` 必須等於 `rect_centerline(expectedPoints, expectedWidth)`、
`hideLabel` 的 `reference.points` 必須等於 `expectedPoints`：手繪的新幾何、或沒有
逐點相同證據的隱藏，一律 fail-closed。要走新規則就先有人核准，同時改這支的判定。

**「整條共線落在單一官方路上」不是隱藏理由**（曾評估、已否決）：幾何 100% 被覆蓋
不等於玩家看得到另一份可見標籤——短路段的名字可能是那一段唯一顯示的名字，藏了
就變沒有路名。只有**逐點相同**才是「同一份標籤畫兩次」的鐵證。斜段、路口相交、
軸座標差 0.5～2 格、落在圖外的一律**不動**（舊版 near／60% overlay／
out-of-bounds 自動剔除已廢除：那些為了藏標籤砍掉整條路，判定又寬到會誤傷）。
殘餘疊字寧可回報，也不自動處理。

## 用法

    python scripts/gen_street_repairs.py gen        # 產生 shared 全域表
    python scripts/gen_street_repairs.py verify     # 驗 pin schema ＋ 生成物 ＋ 上游漂移
    python scripts/gen_street_repairs.py --selftest # 零外部依賴自我測試

`verify` 只讀不寫：schema 有錯或生成物過期＝失敗；上游／vanilla 漂移只**回報**
（執行期本來就會安全略過），絕不覆蓋或抹掉既有 pin。
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_streets_i18n as gsi  # noqa: E402  只取純 helper：import 本身無副作用

PROJECT_ROOT = gsi.PROJECT_ROOT
Result = gsi.Result

REPAIRS_DIR_NAME = "road-repairs"
# 全域表名沿用 MinidoracatMiniMapModMaps 前綴（**沒有** For42 尾綴）：與註冊清單、
# 主 MOD 的接線契約，勿由 mod id 推導。shared/ 早於 client/ 載入 ⇒ 引用時必已就緒。
REPAIR_TABLE_GLOBAL = "MinidoracatMiniMapModMapsStreetRepairs"
# 與街名表同一個 shared/ 目錄、同一份註冊清單（同一個 MOD 的兩張生成表）
REPAIR_TABLE_REL = gsi.STREET_TABLE_REL.with_name(f"{REPAIR_TABLE_GLOBAL}.lua")
REGISTRY_REL = gsi.REGISTRY_REL
SCHEMA_VERSION = 1

DEFAULT_GAME_DIR = Path(r"D:\SteamLibrary\steamapps\common\ProjectZomboid")
# vanilla 全域街道表：引擎每張官方地圖目錄都放同一份全世界街道，取 Muldraugh 那份即可
VANILLA_STREETS_REL = Path("media") / "maps" / "Muldraugh, KY" / "streets.xml"

# native 街道點列 buffer 3072 bytes ＝ 2 bytes header ＋ 每點 2×float32（8 bytes）
# ⇒ 單條街最多 (3072-2)//8 = 383 點。超過就寫爆 buffer，必須擋在生成前。
MAX_REPLACEMENT_POINTS = 383

# 幾何規則門檻（pin 就是照這條算出來的，改了這裡等於改核准規則）
_RECT_MAX_SHORT = 16.0
_RECT_MIN_RATIO = 3.0

# operations[] 認得的欄位；多打一個字（replacmentPoints）不該變成靜默的空修正
_OP_KEYS = {
    "index",
    "name",
    "expectedWidth",
    "expectedPoints",
    "replacementPoints",
    "hideLabel",
    "reference",
    "reason",
}
# 註冊清單引用形如 `streetRepairs = StreetRepairs["daisy-county"]`
_REGISTRY_REPAIRS_RE = re.compile(r'streetRepairs\s*=\s*[\w.]+\s*\[\s*"([^"]+)"\s*\]')


def f32(v: float) -> float:
    """float32 round-trip：引擎把 XML 座標讀成 float，執行期比對的是這個值。"""
    return struct.unpack("<f", struct.pack("<f", v))[0]


def rect_centerline(flat: list[float], width: float) -> list[float] | None:
    """4 點軸對齊細長輪廓矩形 → 2 點中心線；不符回 None（呼叫端原樣保留）。"""
    if len(flat) != 8:
        return None
    pts = {(flat[i], flat[i + 1]) for i in range(0, 8, 2)}
    xs = sorted({p[0] for p in pts})
    ys = sorted({p[1] for p in pts})
    if len(xs) != 2 or len(ys) != 2:
        return None
    x0, x1 = xs
    y0, y1 = ys
    if pts != {(x0, y0), (x1, y0), (x1, y1), (x0, y1)}:
        return None
    short, long_ = min(x1 - x0, y1 - y0), max(x1 - x0, y1 - y0)
    if short <= 0 or short > max(width * 1.5, _RECT_MAX_SHORT):
        return None
    if long_ < short * _RECT_MIN_RATIO:
        return None
    if x1 - x0 >= y1 - y0:
        cy = (y0 + y1) / 2
        return [x0, cy, x1, cy]
    cx = (x0 + x1) / 2
    return [cx, y0, cx, y1]


# ============================================================
# 上游 / vanilla streets.xml
# ============================================================
def find_vanilla_streets(game_dir: Path | None) -> Path | None:
    for base in (game_dir, DEFAULT_GAME_DIR):
        if base is None:
            continue
        p = base / VANILLA_STREETS_REL
        if p.is_file():
            return p
    return None


class Street(NamedTuple):
    width: float | None
    flat: list[float]  # [x0,y0,x1,y1,...]，已 float32 round-trip


def parse_streets(xml_bytes: bytes) -> list[Street]:
    """streets.xml → 依文件順序的 `<street>`（list 位置即 0-based raw street index）。"""
    root = ET.fromstring(xml_bytes.decode("utf-8"))
    out: list[Street] = []
    for st in root.findall("street"):
        flat: list[float] = []
        pts = st.find("points")
        if pts is not None:
            for p in pts.findall("point"):
                flat.append(f32(float(p.get("x", "0"))))
                flat.append(f32(float(p.get("y", "0"))))
        raw_w = st.get("width")
        out.append(Street(f32(float(raw_w)) if raw_w else None, flat))
    return out


# ============================================================
# pin 檔
# ============================================================
def _num(errors: list[str], where: str, val: object, *, positive: bool = False) -> float | None:
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        errors.append(f"{where} 必須是數字（得到 {val!r}）")
        return None
    v = float(val)
    if v != v or v in (float("inf"), float("-inf")):
        errors.append(f"{where} 必須是有限數字")
        return None
    if positive and v <= 0:
        errors.append(f"{where} 必須 > 0（得到 {v!r}）")
        return None
    if f32(v) != v:
        # pin 存的就是執行期會看到的 float32 值；存了無法 round-trip 的十進位值＝
        # 執行期逐值比對永遠不相等 ⇒ 該筆修正靜默失效，必須擋在生成前。
        errors.append(f"{where} 不是 float32 round-trip 精確值（{v!r} → {f32(v)!r}）")
        return None
    return v


def _flat_points(errors: list[str], where: str, val: object) -> list[float] | None:
    if not isinstance(val, list):
        errors.append(f"{where} 必須是扁平座標陣列")
        return None
    if len(val) < 4 or len(val) % 2:
        errors.append(f"{where} 長度必須是偶數且 >= 4（至少兩點，得到 {len(val)}）")
        return None
    out: list[float] = []
    for i, raw in enumerate(val):
        v = _num(errors, f"{where}[{i}]", raw)
        if v is None:
            return None
        out.append(v)
    return out


class Op(NamedTuple):
    index: int
    name: str
    expected_width: float
    expected_points: list[float]
    replacement_points: list[float] | None
    hide_label: bool
    ref_index: int | None
    ref_width: float | None
    ref_points: list[float] | None


class Pins(NamedTuple):
    dataset: str
    workshop_id: str
    map_mod: str
    map_dir: str
    streets_sha: str
    vanilla_sha: str
    ops: list[Op]


def _load_op(errors: list[str], warnings: list[str], where: str, raw: dict) -> Op | None:
    unknown = sorted(set(raw) - _OP_KEYS)
    if unknown:
        errors.append(f"{where} 有未知欄位 {unknown}（打錯字會變成靜默失效的修正）")
    idx = raw.get("index")
    if not isinstance(idx, int) or isinstance(idx, bool) or idx < 0:
        errors.append(f"{where}.index 必須是 >= 0 的整數（0-based raw street index）")
        return None
    width = _num(errors, f"{where}.expectedWidth", raw.get("expectedWidth"), positive=True)
    exp = _flat_points(errors, f"{where}.expectedPoints", raw.get("expectedPoints"))

    rep = None
    if "replacementPoints" in raw:
        rep = _flat_points(errors, f"{where}.replacementPoints", raw["replacementPoints"])
        if rep is not None and len(rep) // 2 > MAX_REPLACEMENT_POINTS:
            errors.append(
                f"{where}.replacementPoints {len(rep) // 2} 點超過 native buffer 上限"
                f" {MAX_REPLACEMENT_POINTS}"
            )
            rep = None
        elif rep is not None and exp is not None and width is not None:
            # 只認核准過的 rect-outline → 中心線；手繪幾何一律 fail-closed
            if rect_centerline(exp, width) != rep:
                errors.append(
                    f"{where}.replacementPoints 不是 expectedPoints 的 rect-outline 中心線"
                    "（新規則要先人工核准並改 gen_street_repairs.py 的判定）"
                )

    hide = raw.get("hideLabel", False)
    if hide is not True and hide is not False:
        errors.append(f"{where}.hideLabel 只能是 true 或省略")
        hide = False
    if not hide and rep is None:
        errors.append(f"{where} 既不改幾何也不隱藏路名＝空修正，請刪除")

    ref_index = ref_width = ref_points = None
    if hide:
        ref = raw.get("reference")
        if not isinstance(ref, dict):
            errors.append(f"{where}.reference 必填（隱藏路名的 canonical 重複證據）")
        else:
            ri = ref.get("index")
            if not isinstance(ri, int) or isinstance(ri, bool) or ri < 0:
                errors.append(f"{where}.reference.index 必須是 >= 0 的整數")
            else:
                ref_index = ri
            ref_width = _num(errors, f"{where}.reference.width", ref.get("width"), positive=True)
            ref_points = _flat_points(errors, f"{where}.reference.points", ref.get("points"))
            # exact-copy 才是「同一份標籤畫兩次」的鐵證：只被覆蓋不算（已否決）
            if ref_points is not None and exp is not None and ref_points != exp:
                errors.append(
                    f"{where}.reference.points 與 expectedPoints 不逐點相同"
                    "（只有 exact-copy 才准隱藏路名）"
                )
    elif "reference" in raw:
        warnings.append(f"{where} 沒有 hideLabel 卻帶 reference（執行期不會用到）")

    if width is None or exp is None:
        return None
    return Op(
        idx,
        raw.get("name") if isinstance(raw.get("name"), str) else "",
        width,
        exp,
        rep,
        bool(hide),
        ref_index,
        ref_width,
        ref_points,
    )


def load_pins(path: Path) -> tuple[Pins | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as e:
        return None, [f"{path.name} 讀取失敗：{e}"], warnings
    if not isinstance(data, dict):
        return None, [f"{path.name} 頂層必須是物件"], warnings

    ds = data.get("dataset")
    if not isinstance(ds, str) or not ds.strip():
        errors.append(f"{path.name} 缺 dataset")
        ds = path.stem
    elif ds != path.stem:
        errors.append(f"{path.name} dataset={ds!r} 與檔名不符")
    if data.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(
            f"{path.name} schemaVersion 必須是 {SCHEMA_VERSION}（得到 {data.get('schemaVersion')!r}）"
        )

    src = data.get("source")
    if not isinstance(src, dict):
        errors.append(f"{path.name} 缺 source")
        src = {}
    # workshop_id 是漂移檢查的定位鍵，map_mod/map_dir 是執行期甄別來源 MOD 的擁有者鍵
    for key in ("workshop_id", "map_mod", "map_dir"):
        if not isinstance(src.get(key), str) or not src[key].strip():
            errors.append(f"{path.name} source.{key} 必填")
    van = data.get("vanilla") if isinstance(data.get("vanilla"), dict) else {}

    raw_ops = data.get("operations")
    if not isinstance(raw_ops, list) or not raw_ops:
        errors.append(f"{path.name} operations 必須是非空陣列")
        raw_ops = []

    ops: list[Op] = []
    seen: set[int] = set()
    for n, raw in enumerate(raw_ops):
        where = f"{path.name} operations[{n}]"
        if not isinstance(raw, dict):
            errors.append(f"{where} 必須是物件")
            continue
        op = _load_op(errors, warnings, where, raw)
        if op is None:
            continue
        if op.index in seen:
            errors.append(f"{where}.index={op.index} 重複")
            continue
        seen.add(op.index)
        ops.append(op)
    if errors:
        return None, errors, warnings
    return (
        Pins(
            ds,
            str(src.get("workshop_id") or ""),
            str(src.get("map_mod")),
            str(src.get("map_dir")),
            str(src.get("streets_xml_sha256") or ""),
            str(van.get("streets_xml_sha256") or ""),
            sorted(ops, key=lambda o: o.index),
        ),
        errors,
        warnings,
    )


# ============================================================
# Lua 生成
# ============================================================
def _fmt_num(v: float) -> str:
    """整數不留小數點；其餘用 repr（最短 round-trip 十進位，Lua 讀回同一個 double）。"""
    return str(int(v)) if float(v).is_integer() else repr(float(v))


def _fmt_flat(vals: list[float]) -> str:
    return "{ " + ", ".join(_fmt_num(v) for v in vals) + " }"


def render_repair_table(pins_by_ds: dict[str, Pins]) -> bytes:
    total = sum(len(p.ops) for p in pins_by_ds.values())
    hides = sum(1 for p in pins_by_ds.values() for o in p.ops if o.hide_label)
    geoms = sum(1 for p in pins_by_ds.values() for o in p.ops if o.replacement_points)
    lines = [
        f"-- {REPAIR_TABLE_REL.name}（生成檔，勿手編）",
        f"-- 由 scripts/gen_street_repairs.py 從 {REPAIRS_DIR_NAME}/*.json 編譯",
        f"-- {len(pins_by_ds)} 個 dataset／{total} 筆修正（改幾何 {geoms}、隱藏標籤候選 {hides}）",
        "--",
        "-- 執行期契約：逐值比對 expectedWidth／expectedPoints，不符就略過該筆並 log",
        "-- （上游改版＝安全退回原樣，不擋同圖其他修正、也不擋新道路）。",
        "-- hideLabel 只影響玩家地圖上的路名顯示，**不從導航路網移除該道路**；",
        "-- reference 是 vanilla 對應街道的 index/width/points，執行期須確認那條",
        "-- canonical 道路仍在且看得見，才真的隱藏我方這份重複標籤。",
        "",
        f"{REPAIR_TABLE_GLOBAL} = {REPAIR_TABLE_GLOBAL} or {{}}",
        f"local Repairs = {REPAIR_TABLE_GLOBAL}",
        "",
    ]
    for ds in sorted(pins_by_ds):
        p = pins_by_ds[ds]
        lines.append(f"-- ==== {ds} ({p.map_mod} / {p.map_dir}) ====")
        lines.append(
            f"-- 逐筆理由（rect-outline／exact-copy）在"
            f" {REPAIRS_DIR_NAME}/{ds}.json 的 reason；"
            "有 replacementPoints＝改幾何，有 hideLabel＝藏重複路名"
        )
        lines.append("do")
        lines.append("    local ops = {}")
        for o in p.ops:
            head = f"#{o.index} {o.name}" if o.name else f"#{o.index}"
            lines.append(f"    -- {' '.join(head.split())}")
            parts = [
                f"expectedWidth = {_fmt_num(o.expected_width)}",
                f"expectedPoints = {_fmt_flat(o.expected_points)}",
            ]
            if o.replacement_points:
                parts.append(f"replacementPoints = {_fmt_flat(o.replacement_points)}")
            if o.hide_label:
                parts.append("hideLabel = true")
                parts.append(
                    "reference = { index = %d, width = %s, points = %s }"
                    % (o.ref_index, _fmt_num(o.ref_width), _fmt_flat(o.ref_points))
                )
            lines.append(f"    ops[{o.index}] = {{ " + ", ".join(parts) + " }")
        lines.append(
            "    Repairs[%s] = { schemaVersion = %d, mapMod = %s, mapDir = %s, operations = ops }"
            % (gsi._lua_str(ds), SCHEMA_VERSION, gsi._lua_str(p.map_mod), gsi._lua_str(p.map_dir))
        )
        lines.append("end")
        lines.append("")
    return ("\n".join(lines)).encode("utf-8")


# ============================================================
# 註冊清單交叉檢查
# ============================================================
def registry_check(project_root: Path, pins_by_ds: dict[str, Pins]) -> tuple[list[str], list[str]]:
    path = project_root / REGISTRY_REL
    if not path.is_file():
        return [f"缺註冊清單 {REGISTRY_REL}"], []
    refs = _REGISTRY_REPAIRS_RE.findall(path.read_text(encoding="utf-8"))
    errors = [
        f"註冊清單引用 streetRepairs[{ds!r}]，但缺 {REPAIRS_DIR_NAME}/{ds}.json"
        for ds in refs
        if ds not in pins_by_ds
    ]
    warnings = [
        f"{ds} 有修正資料但註冊清單未引用 streetRepairs（該圖修正不會生效）"
        for ds in sorted(pins_by_ds)
        if ds not in refs
    ]
    return errors, warnings


# ============================================================
# 上游漂移回報（只讀、只警告）
# ============================================================
def survey_upstream(
    pins_by_ds: dict[str, Pins],
    *,
    prefer: list[str],
    game_dir: Path | None,
) -> list[str]:
    """比對本機上游／vanilla 副本，回報 pin 已對不上的筆數。

    只回報。pin 是人工核准的資料，generator 不得覆蓋或抹掉——執行期本來就會逐值
    比對後安全略過，漂移的代價是「該筆修正失效」，不是壞掉。
    """
    warnings: list[str] = []
    roots = gsi.iter_workshop_roots(prefer)
    van_path = find_vanilla_streets(game_dir)
    van: list[Street] | None = None
    if van_path is None:
        warnings.append("找不到本機 vanilla streets.xml，跳過 reference 漂移檢查")
    else:
        van = parse_streets(van_path.read_bytes())
        van_sha = gsi.file_sha256(van_path)
        if any(p.vanilla_sha and p.vanilla_sha != van_sha for p in pins_by_ds.values()):
            warnings.append("vanilla streets.xml sha256 已變（本體改版，須人工覆核 reference）")
    for ds in sorted(pins_by_ds):
        p = pins_by_ds[ds]
        xml = gsi.find_streets_xml(roots, p.workshop_id, p.map_dir)
        if xml is None:
            warnings.append(f"{ds} 找不到本機上游副本，跳過漂移檢查")
        else:
            if p.streets_sha and gsi.file_sha256(xml) != p.streets_sha:
                warnings.append(f"{ds} 上游 streets.xml sha256 已變（須人工覆核 pin）")
            up = parse_streets(xml.read_bytes())
            stale = [
                o.index
                for o in p.ops
                if o.index >= len(up)
                or up[o.index].width != o.expected_width
                or up[o.index].flat != o.expected_points
            ]
            if stale:
                warnings.append(
                    f"{ds} {len(stale)}/{len(p.ops)} 筆 pin 與上游不符（執行期會安全略過）"
                    f"：index {stale[:8]}{' …' if len(stale) > 8 else ''}"
                )
        if van is None:
            continue
        bad = [
            o.index
            for o in p.ops
            if o.hide_label
            and (
                o.ref_index >= len(van)
                or van[o.ref_index].width != o.ref_width
                or van[o.ref_index].flat != o.ref_points
            )
        ]
        if bad:
            warnings.append(
                f"{ds} {len(bad)} 筆 reference 與 vanilla 不符（執行期不會隱藏路名）"
                f"：index {bad[:8]}{' …' if len(bad) > 8 else ''}"
            )
    return warnings


# ============================================================
# gen / verify
# ============================================================
def _load_all(project_root: Path) -> tuple[dict[str, Pins], list[str], list[str]]:
    pins_by_ds: dict[str, Pins] = {}
    errors: list[str] = []
    warnings: list[str] = []
    for f in sorted((project_root / REPAIRS_DIR_NAME).glob("*.json")):
        pins, errs, warns = load_pins(f)
        errors.extend(errs)
        warnings.extend(warns)
        if pins is not None:
            pins_by_ds[pins.dataset] = pins
    if not errors:
        errs, warns = registry_check(project_root, pins_by_ds)
        errors.extend(errs)
        warnings.extend(warns)
    return pins_by_ds, errors, warnings


def gen(project_root: Path) -> tuple[Result, dict[str, Pins]]:
    pins_by_ds, errors, warnings = _load_all(project_root)
    if errors:
        return Result(errors, warnings), {}
    gsi.write_bytes_atomic(project_root / REPAIR_TABLE_REL, render_repair_table(pins_by_ds))
    return Result(errors, warnings), pins_by_ds


def verify(project_root: Path, *, prefer: list[str], game_dir: Path | None) -> Result:
    pins_by_ds, errors, warnings = _load_all(project_root)
    if errors:
        return Result(errors, warnings)
    path = project_root / REPAIR_TABLE_REL
    if not path.is_file():
        errors.append(f"缺生成檔 {REPAIR_TABLE_REL}（跑 gen）")
    elif path.read_bytes() != render_repair_table(pins_by_ds):
        errors.append(f"{REPAIR_TABLE_REL} 與 {REPAIRS_DIR_NAME}/ 不同步（跑 gen）")
    warnings.extend(survey_upstream(pins_by_ds, prefer=prefer, game_dir=game_dir))
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
# selftest（自造迷你 fixture，不依賴真 pin／真 workshop）
# ============================================================
_XML = (
    '<streets version="1">\n'
    '    <street name="Outline Rd" width="10">\n'
    "        <points>\n"
    '            <point x="100" y="200" /><point x="110" y="200" />\n'
    '            <point x="110" y="400" /><point x="100" y="400" />\n'
    "        </points>\n"
    "    </street>\n"
    '    <street name="Copy St" width="8">\n'
    '        <points><point x="10" y="20" /><point x="60" y="20" /></points>\n'
    "    </street>\n"
    "</streets>\n"
)
_VAN_XML = (
    '<streets version="1">\n'
    '    <street name="Real St" width="8">\n'
    '        <points><point x="10" y="20" /><point x="60" y="20" /></points>\n'
    "    </street>\n"
    "</streets>\n"
)


def _pin_doc(**over: object) -> dict:
    doc: dict = {
        "dataset": "demo",
        "schemaVersion": 1,
        "source": {
            "workshop_id": "1",
            "map_mod": "DemoMod",
            "map_dir": "Demo",
            "streets_xml_sha256": "",
            "captured": "2026-09-10",
        },
        "vanilla": {"map_dir": "Muldraugh, KY", "streets_xml_sha256": ""},
        "operations": [
            {
                "index": 0,
                "name": "Outline Rd",
                "expectedWidth": 10,
                "expectedPoints": [100, 200, 110, 200, 110, 400, 100, 400],
                "replacementPoints": [105, 200, 105, 400],
                "reason": "rect-outline",
            },
            {
                "index": 1,
                "name": "Copy St",
                "expectedWidth": 8,
                "expectedPoints": [10, 20, 60, 20],
                "hideLabel": True,
                "reference": {"index": 0, "name": "Real St", "width": 8, "points": [10, 20, 60, 20]},
                "reason": "exact-copy",
            },
        ],
    }
    doc.update(over)
    return doc


def _fixture(root: Path, doc: dict | None, *, registry: bool = True) -> Path:
    (root / REPAIRS_DIR_NAME).mkdir(parents=True, exist_ok=True)
    if doc is not None:
        (root / REPAIRS_DIR_NAME / "demo.json").write_text(
            json.dumps(doc, ensure_ascii=False), encoding="utf-8"
        )
    reg = root / REGISTRY_REL
    reg.parent.mkdir(parents=True, exist_ok=True)
    body = 'streetRepairs = StreetRepairs["demo"]' if registry else "-- none"
    reg.write_text(f"-- registry\n{body}\n", encoding="utf-8")
    ws = root / "workshop" / "1" / "mods" / "demo" / "42" / "media" / "maps" / "Demo"
    ws.mkdir(parents=True, exist_ok=True)
    (ws / "streets.xml").write_text(_XML, encoding="utf-8")
    game = root / "game" / "media" / "maps" / "Muldraugh, KY"
    game.mkdir(parents=True, exist_ok=True)
    (game / "streets.xml").write_text(_VAN_XML, encoding="utf-8")
    return root


def _reject_cases() -> list[tuple[str, dict, str]]:
    """(標籤, 壞 pin, 錯誤訊息關鍵字)——每列各打一條 fail-closed 分支。"""
    cases: list[tuple[str, dict, str]] = [
        ("schemaVersion 不對", _pin_doc(schemaVersion=2), "schemaVersion"),
        ("dataset 與檔名不符", _pin_doc(dataset="other"), "與檔名不符"),
        ("operations 空", _pin_doc(operations=[]), "非空陣列"),
        ("缺 source.map_mod", _pin_doc(source={"workshop_id": "1", "map_dir": "Demo"}), "map_mod"),
    ]
    doc = _pin_doc(); doc["operations"][1].pop("reference")
    cases.append(("隱藏路名缺 reference", doc, "reference 必填"))
    doc = _pin_doc(); doc["operations"][1]["reference"]["points"] = [10, 20, 61, 20]
    cases.append(("reference 非逐點相同", doc, "不逐點相同"))
    doc = _pin_doc(); doc["operations"][0].pop("replacementPoints")
    cases.append(("空修正", doc, "空修正"))
    doc = _pin_doc(); doc["operations"][0]["replacementPoints"] = [1, 2, 3, 4]
    cases.append(("手繪 replacement 不是 rect 中心線", doc, "rect-outline 中心線"))
    doc = _pin_doc(); doc["operations"][0]["replacementPoints"] = [float(i) for i in range(768)]
    cases.append(("replacement 超過 native 點數上限", doc, "native buffer 上限"))
    doc = _pin_doc(); doc["operations"][0]["expectedPoints"] = [100, 200, 110]
    cases.append(("點列長度奇數", doc, "偶數"))
    doc = _pin_doc(); doc["operations"][0]["expectedPoints"] = [100, 200, 110.1, 200]
    cases.append(("非 float32 精確值", doc, "float32"))
    doc = _pin_doc(); doc["operations"][0]["expectedWidth"] = 0
    cases.append(("width 非正", doc, "> 0"))
    doc = _pin_doc(); doc["operations"][0]["index"] = -1
    cases.append(("index 不合法", doc, ">= 0"))
    doc = _pin_doc(); doc["operations"][1]["index"] = 0
    cases.append(("index 重複", doc, "重複"))
    doc = _pin_doc(); doc["operations"][0]["replacmentPoints"] = [1, 2, 3, 4]
    cases.append(("欄位打錯字", doc, "未知欄位"))
    return cases


def cmd_selftest() -> int:
    n_ok = n_all = 0

    def check(label: str, cond: bool, detail: str = "") -> None:
        nonlocal n_ok, n_all
        n_all += 1
        if cond:
            n_ok += 1
            print(f"  ✅ {label}")
        else:
            print(f"  ❌ {label} {detail}")

    def _verify(root: Path) -> Result:
        return verify(root, prefer=[str(root / "workshop")], game_dir=root / "game")

    with tempfile.TemporaryDirectory() as td:
        root = _fixture(Path(td) / "a", _pin_doc())
        res, _ = gen(root)
        check("gen 乾淨 pin", res.ok, str(res.errors))
        lua = (root / REPAIR_TABLE_REL).read_text(encoding="utf-8")
        check(
            "改幾何／隱藏標籤／0-based index 都原樣落表",
            "replacementPoints = { 105, 200, 105, 400 }" in lua
            and "hideLabel = true" in lua
            and "reference = { index = 0," in lua
            and "ops[0] = {" in lua
            and "ops[1] = {" in lua,
            lua,
        )
        check(
            "reason 留在 pin、生成物只留 index/name 註解",
            "    -- #0 Outline Rd\n" in lua and "reason =" not in lua,
            lua,
        )
        check("verify 通過剛生成的檔", _verify(root).ok)
        p = root / REPAIR_TABLE_REL
        p.write_bytes(p.read_bytes() + b"\n-- tampered\n")
        res = _verify(root)
        check("verify 抓到生成物不同步", not res.ok and any("不同步" in e for e in res.errors), str(res.errors))
        p.unlink()
        res = _verify(root)
        check("verify 抓到缺生成物", not res.ok and any("缺生成檔" in e for e in res.errors), str(res.errors))

    for label, doc, needle in _reject_cases():
        with tempfile.TemporaryDirectory() as td:
            root = _fixture(Path(td) / "x", doc)
            res, _ = gen(root)
            check(
                f"拒收：{label}",
                not res.ok
                and any(needle in e for e in res.errors)
                and not (root / REPAIR_TABLE_REL).is_file(),
                str(res.errors),
            )

    with tempfile.TemporaryDirectory() as td:
        root = _fixture(Path(td) / "d", _pin_doc(), registry=False)
        res, _ = gen(root)
        check(
            "註冊清單未引用只警告不失敗",
            res.ok and any("未引用" in w for w in res.warnings),
            str(res.errors + res.warnings),
        )
    with tempfile.TemporaryDirectory() as td:
        root = _fixture(Path(td) / "e", None)
        res, _ = gen(root)
        check(
            "註冊清單引用但缺 pin 檔＝錯誤",
            not res.ok and any("但缺" in e for e in res.errors),
            str(res.errors),
        )

    # 上游／vanilla 漂移：只警告，且絕不回頭改 pin
    with tempfile.TemporaryDirectory() as td:
        root = _fixture(Path(td) / "f", _pin_doc())
        gen(root)
        pin_path = root / REPAIRS_DIR_NAME / "demo.json"
        before = pin_path.read_bytes()
        ws = root / "workshop" / "1" / "mods" / "demo" / "42" / "media" / "maps" / "Demo"
        (ws / "streets.xml").write_text(_XML.replace('x="100" y="200"', 'x="101" y="200"'), encoding="utf-8")
        game = root / "game" / "media" / "maps" / "Muldraugh, KY" / "streets.xml"
        game.write_text(_VAN_XML.replace('x="60"', 'x="61"'), encoding="utf-8")
        res = _verify(root)
        check(
            "上游／vanilla 漂移只警告不失敗",
            res.ok
            and any("與上游不符" in w for w in res.warnings)
            and any("reference 與 vanilla 不符" in w for w in res.warnings),
            str(res.errors + res.warnings),
        )
        check("漂移不改動 pin", pin_path.read_bytes() == before)

    print(f"\n{'✅' if n_ok == n_all else '❌'} selftest {n_ok}/{n_all}")
    return 0 if n_ok == n_all else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="自我測試（零外部依賴）")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("gen", help="road-repairs/*.json → shared 全域表")
    v = sub.add_parser("verify", help="驗 pin schema、生成物同步、上游漂移")
    v.add_argument("--prefer", action="append", help="額外 workshop content 根（可重複）")
    v.add_argument("--game-dir", help="Project Zomboid 安裝目錄（找 vanilla streets.xml）")
    args = parser.parse_args(argv)

    if args.selftest:
        return cmd_selftest()
    if args.cmd == "gen":
        result, pins_by_ds = gen(PROJECT_ROOT)
        _print_result("gen 道路修正表", result)
        for ds in sorted(pins_by_ds):
            ops = pins_by_ds[ds].ops
            geom = sum(1 for o in ops if o.replacement_points)
            hide = sum(1 for o in ops if o.hide_label)
            print(f"   {ds:24s} 改幾何 {geom:4d} 隱藏標籤候選 {hide:4d}")
        return 0 if result.ok else 1
    if args.cmd == "verify":
        result = verify(
            PROJECT_ROOT,
            prefer=args.prefer or [],
            game_dir=Path(args.game_dir) if args.game_dir else None,
        )
        _print_result("verify 道路修正資料", result)
        return 0 if result.ok else 1
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
