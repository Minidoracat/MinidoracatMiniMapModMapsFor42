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

## pin 是怎麼得出來的（人工核准過的五條規則，生成時逐筆強制驗）

1. **rect-outline → 中心線**（只有 Daisy County 44/44 條）：4 點、軸對齊、四角互異
   的閉合矩形，短邊 <= max(width*1.5, 16)、長邊 >= 短邊*3。作者把街道畫成輪廓矩形，
   而 `width` 本來就表達寬度 ⇒ 引擎在兩條長邊各畫一次路名（玩家看到上下兩行），
   NavRoute 也把四邊都當路段。壓成中心線後視覺與路網都對，width 保留 ⇒ 粗細不變。
   方環／L 形折線一律不套（`rect_centerline` 判定會自己擋掉）。
2. **exact-copy → 隱藏路名**：本圖某條街的原始點列與 vanilla 全域街道表某條**逐點
   相同**。引擎兩份都畫 ⇒ 同座標疊字。官方那份動不了，所以隱藏我方這份。
3. **gap-bridge → 端點接線**（2026-09-27 使用者核准；Camden County 3 條）：作者的街
   停在路口前幾十格，實際路面連到隔壁街，但距離超過導航吸附容差 ⇒ 整段變成到不了的
   孤島。`replacementPoints` 必須是「原點列一個不動、只在頭或尾多接最多 4 點」，接出的
   長度 <= 48 格，並用 `bridgeTo` 寫明接到同圖哪一條街（0-based index）。接線的新端點
   要落在該街 1 格內——這條要讀上游，由 verify 對本機副本檢查。沿實際路面走（路面
   取樣比例）的證據寫在 reason，那是核准時人看過的東西，generator 不重算。
4. **drop-vertex → 移除轉折點**（2026-10-01 使用者核准內點；Raven Creek）：作者的街在
   路口旁有個內點，落在主 MOD NavCore T 字路口吸附容差內，被拖到隔壁街上，相鄰路段
   因此離開路面。`dropVertex` 寫明移除哪些點（0-based 點序，單一整數或互異點序陣列，
   至少留 2 點），`replacementPoints` 必須逐點等於「expectedPoints 拿掉那些點」。
   **頭尾端點**（2026-10-06 擴充，待使用者核准）：作者的街尾在路口內多畫一小段斜穿
   隔壁街，NavCore 在 2 格內切出兩個交點、路線走成 Z 字。移除端點必須寫 `trimTo`
   （同圖哪一條街，0-based index），且一次只准移除頭或尾其中一個端點、不可連同它的
   相鄰點——只剪掉一段；新端點要落在 `trimTo` 街的半寬內（仍接得上），由 verify 讀
   上游檢查。實機／離線證據寫在 reason，generator 不重算。
5. **width-fix → 換路寬**（2026-10-17 使用者核准；Camden County Brooklawn Blvd）：作者把
   分隔林蔭大道畫成單中線、路寬只標一條車道，AutoDrive 照路寬算靠右落點、車身壓上
   分隔島。點列不動，只寫 `replacementWidth`（整數），不可與 `replacementPoints`／
   `hideLabel` 並用（例外：同一條街另有 drop-vertex 時可以一起寫，證據照原點列量）；證據 `widthEvidence` 是 `pzmap road-surfaces` 的橫截面
   （`sections` 每個是水平或垂直的 `from`／`to` 兩端路面格，含中間的分隔島），每個量到的
   總寬都要等於 `replacementWidth`、中線要穿過橫截面且離路面中心 <= `_WIDTH_MAX_OFFSET`
   格（路寬以中線對稱展開，偏心就會整邊溢出）。橫截面座標是量測結果，generator 只驗
   一致性、不重跑 road-surfaces。路寬不能分段：沒有分隔島的段落會一起變寬，寫在 reason。
6. **median-split → 分隔路拆成兩條車道線**（2026-10-26 使用者核准；德克丹 Map Fix ND11）：作者把
   分隔路只畫一條中線、線落在中央分隔帶上，AutoDrive 照線走就壓分隔帶的樹籬。本筆的
   `replacementPoints` 改成**一側車道**的中線、同時帶 `replacementWidth`（車道寬）與
   `widthEvidence`（橫截面量的是這條車道、要被新線穿過）；**對向車道**由補充道路提供，
   `medianSplit.pair` 寫明是哪個 dataset 的幾號路（主 MOD 一條修正只能換一條折線）。新線與
   pair 每個點都要在原路半寬內、兩端各離原端點 <= 原路半寬（路口吸附語義不變），兩條線
   分在原線兩側；`medianSplit.medianEvidence` 是原中線取樣不在車道鋪面上的數量（分隔帶的草、土、碎石、樹；>= 一半，證明
   原線真的在分隔帶上）。原版雙線公路（KY-841）就是兩條平行線，NavCore 沒有單向概念。
7. **trim-detach → 端點退出吸附距離**（2026-10-26 使用者核准；德克丹 Map Fix ND5）：作者的街
   尾穿過圍籬接到隔壁街，主 MOD NavCore 端點吸附（兩路半寬和＋`ATTACH_SLACK`）讓兩街在
   圖上相通，實際過不去。`replacementPoints` 必須是 expectedPoints 從頭或尾**沿原線截短**
   （新端點落在原線某段上，其餘點不動），截掉長度 <= gap-bridge 上限；`detachFrom` 寫明
   退離哪一條街。verify 讀上游檢查：原端點本來在吸附距離內（真的有接）、新端點在
   吸附距離＋`_DETACH_MARGIN` 外、新線不和那條街相交。
8. **no-junction → 兩條街不建路口**（2026-10-26 使用者核准 ND5–ND7 連同主 MOD 吸附規則一起處理，採 ATTACH_SLACK 審查建議 B；德克丹 ND6／ND7；
   主 MOD 0.51.0 之後的下一版起認得 `noJunction`／`navCut`）：兩條街在 NavCore 相交或端點在吸附距離內、中間卻隔著圍籬／
   樹籬分隔帶。`noJunction` 寫同圖另一條街的 0-based 序號（1–16 條、互異、不含自己），主 MOD 建圖時這兩條街
   不切交點、不互相吸附；地圖上照作者畫的顯示。可以單獨一筆，也可以和其他規則並用。資料要**對稱**：列出的
   街也要有一筆修正、`noJunction` 列回本筆（主 MOD 要兩條街都有相符的修正才生效，對方的 pin 防止上游改序號
   指到別條街）。證據 `noJunctionEvidence.blockers` 是擋在兩街之間的地圖物件（`x`、`y`、`object`）。verify
   讀上游：兩條街本來真的相通（相交或端點在吸附距離內），否則只警告（多餘的筆）。
9. **median-cut → 穿過硬分隔帶的那一小段只從導航拿掉**（同上核准；德克丹 ND6 Main Ave、同一道圍籬的
   Cedar Ave）：作者的街直直穿過另一條路的分隔圍籬，自己的線就是一條穿越路線，`noJunction` 拿不掉。
   `replacementPoints` 必須是 expectedPoints 在**同一段**內插入兩個共線點（其餘點不動、地圖上同一條線），
   `navCut` 寫兩點之間那一段的 0-based 段序（只一段、長度 <= `_CUT_MAX_LEN`），主 MOD 只從導航拿掉它；
   必須同時帶 `noJunction`（列被穿過的那條街，否則兩截各自又吸回去）。verify 讀上游：拿掉的那段要和
   `noJunction` 列的街相交，否則只警告。
10. **center-shift → 中線平移到實測路面中心**（2026-10-26 使用者核准；大熊湖 KY-38、德克丹 US Highway 13／Newport Road／
   Colonial Dr）：作者的中線偏離實際路面中心 1–幾格（常見於路寬也標太寬），AutoDrive 照線＋路寬算靠右落點，一側車身
   出路面。`replacementPoints` 必須和 expectedPoints **點數相同、逐點平移**：每點移動 <= 原路半寬（線留在作者標的
   路面帶內）、至少一點移動 >= `_SHIFT_MIN`（否則只是換路寬，用 width-fix）、各段方向不反轉；可以帶 `replacementWidth`
   （比原路窄的整數）。證據 `centerShift`：`sections` 是 road-surfaces 的水平／垂直橫截面（`from`／`to` 兩端路面格），
   新線要近乎垂直地穿過每一個、交點離路面中心 <= `_SHIFT_CENTER_TOL`，且以交點為中心的新路寬帶整條在截面內；
   `lanes.before`／`lanes.after` 是修前（原線＋原路寬）／修後靠右落點車身（兩個行駛方向各算一次）在路面上的取樣數，
   修後比例 >= `_SHIFT_MIN_ON_ROAD` 且比修前高。verify 讀上游：原本相接（相交或端點在吸附距離內）的街，套用本包
   全部修正後仍要相接，否則**錯誤**（路口斷了不是上游漂移，是這份資料錯）。

`replacementPoints` 必須等於 `rect_centerline(expectedPoints, expectedWidth)`、合法的
gap-bridge 延伸、合法的 drop-vertex、median-split、trim-detach、median-cut 或 center-shift，`hideLabel` 的
`reference.points` 必須等於 `expectedPoints`：其他手繪新幾何、或沒有逐點相同證據的隱藏，
一律 fail-closed。要走新規則就先有人核准，同時改這支的判定。

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
# gap-bridge：接線只准短短一段、點數也少——長的補路不是「修正作者的街」，是新增道路
_BRIDGE_MAX_LEN = 48.0
_BRIDGE_MAX_ADDED = 4
_BRIDGE_SNAP = 1.0  # 新端點離目標街的最大距離（格）；verify 讀上游時檢查
# width-fix：主 MOD validWidth 上限（MAX_WIDTH）；至少兩個橫截面；中線離路面中心的上限（格）；
# 橫截面要和街近乎垂直（街段沿截面方向的分量 <= 長度×此比例），斜交量出的寬會偏大
_WIDTH_MAX = 64
_WIDTH_MIN_SECTIONS = 2
_WIDTH_MAX_OFFSET = 1.0
_WIDTH_MAX_SKEW = 0.2
# median-split：原中線取樣至少這個比例不在車道鋪面上才算「線在分隔帶上」；取樣數下限
_SPLIT_MIN_OFF_ROAD = 0.5
_SPLIT_MIN_SAMPLES = 10
# median-split：兩條車道線各自的平均橫向位置至少離原線這麼遠（格），才算分在兩側
_SPLIT_MIN_SIDE = 1.0
# trim-detach：主 MOD MinidoracatMiniMap_NavRoute.lua 的 ATTACH_SLACK（端點吸附＝兩路半寬和＋此值），
# 新端點要再多退 _DETACH_MARGIN 格；主 MOD 改了 ATTACH_SLACK 這裡要跟著改
_DETACH_SLACK = 4.5
_DETACH_MARGIN = 1.0
# 新端點要落在原線上（float32 量化誤差內）
_ON_LINE_TOL = 0.01
# no-junction：一筆最多列幾條街（主 MOD 同上限）；median-cut：拿掉的那段最長幾格（只跨分隔帶，不是刪路）
_NOJ_MAX = 16
_CUT_MAX_LEN = 8.0
# center-shift：至少一點要移這麼多（格）才算平移；新線離截面路面中心的上限（格）；修後靠右車身在路面上的比例下限
_SHIFT_MIN = 0.5
_SHIFT_CENTER_TOL = 0.5
_SHIFT_MIN_ON_ROAD = 0.9

# operations[] 認得的欄位；多打一個字（replacmentPoints）不該變成靜默的空修正
_OP_KEYS = {
    "index",
    "name",
    "expectedWidth",
    "expectedPoints",
    "replacementPoints",
    "hideLabel",
    "reference",
    "bridgeTo",
    "dropVertex",
    "trimTo",
    "replacementWidth",
    "widthEvidence",
    "medianSplit",
    "detachFrom",
    "noJunction",
    "noJunctionEvidence",
    "navCut",
    "centerShift",
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


def bridge_extension(exp: list[float], rep: list[float]) -> tuple[str, list[float]] | None:
    """gap-bridge 判定：rep 是否為 exp 原封不動、只在一端多接點。

    → (端別 "start"|"end", 接線折線 flat：含原端點，從原端點走到新端點)；不符回 None。
    """
    n, m = len(exp), len(rep)
    added = (m - n) // 2
    if m <= n or (m - n) % 2 or added > _BRIDGE_MAX_ADDED:
        return None
    if rep[m - n:] == exp:
        # 頭端延伸：rep = 新點… + exp；接線從 exp 起點倒著走到 rep[0]
        seg = rep[: m - n + 2]
        pts = [(seg[i], seg[i + 1]) for i in range(0, len(seg), 2)][::-1]
        return "start", [c for p in pts for c in p]
    if rep[:n] == exp:
        return "end", rep[n - 2:]
    return None


def drop_vertices(exp: list[float], ks: list[int]) -> list[float] | None:
    """drop-vertex：exp 拿掉 ks 這些點（0-based）。

    點序要互異、在範圍內、至少留 2 點；頭尾端點最多移一個，且不可連同它的相鄰點
    （只剪一段）。不符回 None。是否移了端點由呼叫端用 `drops_endpoint` 判斷。"""
    n = len(exp) // 2
    if not ks or len(set(ks)) != len(ks) or any(not 0 <= k < n for k in ks) or n - len(ks) < 2:
        return None
    if (0 in ks and n - 1 in ks) or (0 in ks and 1 in ks) or (n - 1 in ks and n - 2 in ks):
        return None
    return [c for i in range(n) if i not in ks for c in exp[2 * i:2 * i + 2]]


def drops_endpoint(exp: list[float], ks: tuple[int, ...]) -> bool:
    return 0 in ks or len(exp) // 2 - 1 in ks


def polyline_length(flat: list[float]) -> float:
    return sum(
        ((flat[i + 2] - flat[i]) ** 2 + (flat[i + 3] - flat[i + 1]) ** 2) ** 0.5
        for i in range(0, len(flat) - 2, 2)
    )


def point_polyline_distance(x: float, y: float, flat: list[float]) -> float:
    best = float("inf")
    for i in range(0, len(flat) - 2, 2):
        ax, ay, bx, by = flat[i], flat[i + 1], flat[i + 2], flat[i + 3]
        dx, dy = bx - ax, by - ay
        ll = dx * dx + dy * dy
        t = 0.0 if ll == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / ll))
        best = min(best, ((x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2) ** 0.5)
    return best


def _tile(v: object) -> bool:
    return (isinstance(v, list) and len(v) == 2
            and all(isinstance(c, int) and not isinstance(c, bool) for c in v))


def _section_crossings(line: list[float], s: object) -> tuple[int, float, list[float]] | str:
    """水平或垂直橫截面（from／to 兩端路面格）→ (量到的格數, 路面中心, line 近乎垂直穿過它的交點)；不合法回錯誤字串。"""
    a, b = (s.get("from"), s.get("to")) if isinstance(s, dict) else (None, None)
    if not (_tile(a) and _tile(b)):
        return "的 from／to 必須是 [x, y] 整數格"
    horiz = a[1] == b[1]
    if a == b or (not horiz and a[0] != b[0]):
        return "必須是水平或垂直的橫截面"
    lo, hi = sorted((a[0], b[0]) if horiz else (a[1], b[1]))
    at, mid = (a[1] if horiz else a[0]) + 0.5, (lo + hi + 1) / 2
    hits = []
    for i in range(0, len(line) - 3, 2):
        # 一律換成「截面是 v=at 這條線」：u 沿截面、v 垂直截面
        u0, v0, u1, v1 = line[i:i + 4] if horiz else (line[i + 1], line[i], line[i + 3], line[i + 2])
        if v0 != v1 and min(v0, v1) <= at <= max(v0, v1) and abs(u1 - u0) <= _WIDTH_MAX_SKEW * abs(v1 - v0):
            hits.append(u0 + (u1 - u0) * (at - v0) / (v1 - v0))
    return hi - lo + 1, mid, hits


def width_evidence_error(exp: list[float], new_width: int, ev: object) -> str | None:
    """width-fix 證據：每個橫截面（水平或垂直、from／to 是兩端路面格）量到的總寬等於
    new_width，中線近乎垂直地穿過它、交點離路面中心 <= _WIDTH_MAX_OFFSET 格。"""
    if not isinstance(ev, dict) or not isinstance(ev.get("source"), str) or not ev["source"].strip():
        return "必填，且要寫 source（量測工具與版本）"
    secs = ev.get("sections")
    if not isinstance(secs, list) or len(secs) < _WIDTH_MIN_SECTIONS:
        return f"sections 至少要 {_WIDTH_MIN_SECTIONS} 個橫截面"
    for n, s in enumerate(secs):
        got = _section_crossings(exp, s)
        if isinstance(got, str):
            return f"sections[{n}] {got}"
        wd, mid, hits = got
        if wd != new_width:
            return f"sections[{n}] 量到 {wd} 格，不等於 replacementWidth {new_width}"
        if not any(abs(u - mid) <= _WIDTH_MAX_OFFSET for u in hits):
            return (f"sections[{n}] 中線沒有近乎垂直地穿過、或離路面中心 {mid:g} 超過"
                    f" {_WIDTH_MAX_OFFSET:g} 格（交點 {[round(u, 2) for u in hits]}）")
    return None


def center_shift_error(exp: list[float], half: float, rep: list[float], new_width: float, ev: object) -> str | None:
    """center-shift：rep 是 exp 逐點平移（點數相同、每點 <= 原路半寬、至少一點 >= _SHIFT_MIN、各段不反向），
    證據 sections 每個都被新線近乎垂直穿過、交點離路面中心 <= _SHIFT_CENTER_TOL、新路寬帶整條在截面內；
    lanes 修後靠右車身在路面上的比例 >= _SHIFT_MIN_ON_ROAD 且比修前高。"""
    if len(rep) != len(exp):
        return "點數要和 expectedPoints 相同（逐點平移，不增刪點）"
    moves = [((rep[i] - exp[i]) ** 2 + (rep[i + 1] - exp[i + 1]) ** 2) ** 0.5 for i in range(0, len(exp), 2)]
    far = [k for k, m in enumerate(moves) if m > half]
    if far:
        return f"第 {far[:4]} 點平移超過原路半寬 {half:g}（最多 {max(moves):.2f} 格）"
    if max(moves) < _SHIFT_MIN:
        return f"每點平移都不到 {_SHIFT_MIN:g} 格（只換路寬請用 width-fix）"
    flip = [i // 2 for i in range(0, len(exp) - 2, 2)
            if (exp[i + 2] - exp[i]) * (rep[i + 2] - rep[i]) + (exp[i + 3] - exp[i + 1]) * (rep[i + 3] - rep[i + 1]) <= 0]
    if flip:
        return f"第 {flip[:4]} 段方向反了（平移不能把段翻過來）"
    if not isinstance(ev, dict) or not isinstance(ev.get("source"), str) or not ev["source"].strip():
        return "centerShift 必填，且要寫 source（量測工具與版本）"
    secs = ev.get("sections")
    if not isinstance(secs, list) or len(secs) < _WIDTH_MIN_SECTIONS:
        return f"centerShift.sections 至少要 {_WIDTH_MIN_SECTIONS} 個橫截面"
    for n, s in enumerate(secs):
        got = _section_crossings(rep, s)
        if isinstance(got, str):
            return f"centerShift.sections[{n}] {got}"
        wd, mid, hits = got
        if not any(abs(u - mid) <= _SHIFT_CENTER_TOL and abs(u - mid) + new_width / 2 <= wd / 2 for u in hits):
            return (f"centerShift.sections[{n}] 新線沒有近乎垂直地穿過、離路面中心 {mid:g} 超過 {_SHIFT_CENTER_TOL:g} 格、"
                    f"或路寬 {new_width:g} 的帶超出量到的 {wd} 格（交點 {[round(u, 2) for u in hits]}）")
    lanes = ev.get("lanes") if isinstance(ev.get("lanes"), dict) else {}
    counts = []
    for key in ("before", "after"):
        c = lanes.get(key) if isinstance(lanes.get(key), dict) else {}
        ns, on = c.get("samples"), c.get("onRoad")
        if not (type(ns) is int and type(on) is int and ns >= _SPLIT_MIN_SAMPLES and 0 <= on <= ns):
            return (f"centerShift.lanes.{key} 必填（靠右車身取樣數 samples >= {_SPLIT_MIN_SAMPLES}、"
                    "其中在路面上的 onRoad）")
        counts.append(on / ns)
    if counts[1] < _SHIFT_MIN_ON_ROAD or counts[1] <= counts[0]:
        return (f"centerShift.lanes 修後靠右車身在路面上 {counts[1]:.1%}（下限 {_SHIFT_MIN_ON_ROAD:.0%}，"
                f"且要比修前 {counts[0]:.1%} 高）")
    return None


def signed_side(flat: list[float], ref: list[float]) -> float:
    """flat 各段中點到 ref 折線的有號距離平均（左正右負，取最近段）——判斷一條線在原線哪一側。"""
    total, n = 0.0, 0
    for i in range(0, len(flat) - 2, 2):
        x, y = (flat[i] + flat[i + 2]) / 2, (flat[i + 1] + flat[i + 3]) / 2
        best = None
        for j in range(0, len(ref) - 2, 2):
            ax, ay, bx, by = ref[j:j + 4]
            dx, dy = bx - ax, by - ay
            ll = dx * dx + dy * dy
            if ll == 0:
                continue
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / ll))
            d = ((x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2) ** 0.5
            if best is None or d < best[0]:
                best = (d, d if dx * (y - ay) - dy * (x - ax) >= 0 else -d)
        if best is not None:
            total += best[1]
            n += 1
    return total / n if n else 0.0


def carriageway_error(exp: list[float], half: float, line: list[float]) -> str | None:
    """median-split 的一條車道線（本筆 replacement 或 pair 補充道路）：每點在原路半寬內、
    兩端各離原線某一端點 <= 半寬（頭尾可以反向畫）、平均橫向位置離原線 >= _SPLIT_MIN_SIDE。"""
    far = [i // 2 for i in range(0, len(line), 2) if point_polyline_distance(line[i], line[i + 1], exp) > half]
    if far:
        return f"第 {far[:4]} 點離原線超過原路半寬 {half:g}"
    ends = ((exp[0], exp[1]), (exp[-2], exp[-1]))
    near = [min(((line[k] - x) ** 2 + (line[k + 1] - y) ** 2) ** 0.5 for x, y in ends) for k in (0, len(line) - 2)]
    if max(near) > half:
        return f"兩端要各在原線端點 {half:g} 格內（路口吸附不變），得到 {[round(v, 2) for v in near]}"
    if abs(signed_side(line, exp)) < _SPLIT_MIN_SIDE:
        return f"平均橫向位置離原線不到 {_SPLIT_MIN_SIDE:g} 格（沒有移到單側車道）"
    return None


def trim_detach(exp: list[float], rep: list[float]) -> tuple[int, float] | None:
    """trim-detach 判定：rep 是否為 exp 從頭或尾沿原線截短（新端點落在原線某段上、其餘點不動）。

    → (被截的端：0＝頭、1＝尾, 截掉的長度)；不符回 None。"""
    n = len(exp) // 2
    if len(rep) < 4 or len(rep) % 2:
        return None
    for end in (0, 1):
        e = exp if end else [c for k in range(n - 1, -1, -1) for c in exp[2 * k:2 * k + 2]]
        r = rep if end else [c for k in range(len(rep) // 2 - 1, -1, -1) for c in rep[2 * k:2 * k + 2]]
        m = len(r) // 2  # 保留 e 的前 m-1 點，第 m 點是落在 e 第 m-1→m 段上的新端點
        if m > n or r[:-2] != e[:2 * (m - 1)]:
            continue
        ax, ay, bx, by = e[2 * (m - 2):2 * m]
        px, py = r[-2], r[-1]
        if (px, py) == (bx, by) or (px, py) == (ax, ay):
            continue
        if point_polyline_distance(px, py, [ax, ay, bx, by]) > _ON_LINE_TOL:
            continue
        cut = polyline_length([px, py] + e[2 * (m - 1):])
        return end, cut
    return None


def cut_insert(exp: list[float], rep: list[float]) -> tuple[int, float] | None:
    """median-cut 判定：rep 是否為 exp 在同一段內依序插入兩個共線點（其餘點不動）。

    → (兩新點之間那段在 rep 的 0-based 段序, 那段長度)；不符回 None。"""
    if len(rep) != len(exp) + 4:
        return None
    for s in range(0, len(exp) - 2, 2):
        if rep[:s + 2] != exp[:s + 2] or rep[s + 6:] != exp[s + 2:]:
            continue
        ax, ay, bx, by = exp[s:s + 4]
        dx, dy = bx - ax, by - ay
        ll = dx * dx + dy * dy
        if ll == 0:
            return None
        ts = []
        for px, py in (rep[s + 2:s + 4], rep[s + 4:s + 6]):
            if point_polyline_distance(px, py, [ax, ay, bx, by]) > _ON_LINE_TOL:
                return None
            ts.append(((px - ax) * dx + (py - ay) * dy) / ll)
        if not 0 < ts[0] < ts[1] < 1:
            return None
        return s // 2 + 1, polyline_length(rep[s + 2:s + 6])
    return None


def segments_cross(a: list[float], b: list[float]) -> bool:
    """兩條折線是否有任一對線段相交（含端點相觸）。"""
    def orient(px, py, qx, qy, rx, ry):
        v = (qx - px) * (ry - py) - (qy - py) * (rx - px)
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)

    for i in range(0, len(a) - 2, 2):
        p1, p2 = a[i:i + 2], a[i + 2:i + 4]
        for j in range(0, len(b) - 2, 2):
            q1, q2 = b[j:j + 2], b[j + 2:j + 4]
            o1, o2 = orient(*p1, *p2, *q1), orient(*p1, *p2, *q2)
            o3, o4 = orient(*q1, *q2, *p1), orient(*q1, *q2, *p2)
            if o1 != o2 and o3 != o4:
                return True
    return False


def linked(a: list[float], wa: float, b: list[float], wb: float) -> bool:
    """主 MOD NavCore 會不會把這兩條街接起來：線段相交，或任一端點離對方 <= 兩路半寬和＋_DETACH_SLACK。"""
    tol = wa / 2 + wb / 2 + _DETACH_SLACK
    ends = ((a[0], a[1], b), (a[-2], a[-1], b), (b[0], b[1], a), (b[-2], b[-1], a))
    return segments_cross(a, b) or any(point_polyline_distance(x, y, ln) <= tol for x, y, ln in ends)


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
    bridge_to: int | None = None
    drop_vertex: tuple[int, ...] | None = None
    trim_to: int | None = None
    replacement_width: int | None = None
    split_pair: tuple[str, int] | None = None  # median-split：對向車道的補充道路 (dataset, no)
    detach_from: int | None = None  # trim-detach：端點退離哪一條街（0-based index）
    no_junction: tuple[int, ...] | None = None  # no-junction：不和這幾條同圖街建路口（進執行期）
    nav_cut: int | None = None  # median-cut：只從導航拿掉的段序（0-based，進執行期）
    center_shift: bool = False  # center-shift：replacementPoints 是逐點平移（證據不進執行期）


KIND_RECT = "rect-centerline"
KIND_BRIDGE = "gap-bridge"
KIND_DROP = "drop-vertex"
KIND_WIDTH = "width-fix"
KIND_HIDE = "hide-label"
KIND_SPLIT = "median-split"
KIND_DETACH = "trim-detach"
KIND_CUT = "median-cut"
KIND_NOJ = "no-junction"
KIND_SHIFT = "center-shift"


def classify_op(op: Op) -> str:
    """已通過 `_load_op` 的修正 → 規則種類（公開道路資料清單依此分類計數）。
    noJunction 可以掛在任何一筆上；只有它、沒有改幾何／路寬時才算 no-junction。"""
    if op.hide_label:
        return KIND_HIDE
    if op.split_pair is not None:
        return KIND_SPLIT
    if op.detach_from is not None:
        return KIND_DETACH
    if op.nav_cut is not None:
        return KIND_CUT
    if op.center_shift:
        return KIND_SHIFT
    if op.replacement_width is not None:
        return KIND_WIDTH
    if op.drop_vertex is not None:
        return KIND_DROP
    if op.replacement_points is None:
        return KIND_NOJ
    return KIND_BRIDGE if op.bridge_to is not None else KIND_RECT


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
    bridge_to = None
    drop_k = None
    trim_to = None
    split_pair = None
    detach_from = None
    nav_cut = None
    center_shift = False
    if "replacementPoints" in raw:
        rep = _flat_points(errors, f"{where}.replacementPoints", raw["replacementPoints"])
        if rep is not None and len(rep) // 2 > MAX_REPLACEMENT_POINTS:
            errors.append(
                f"{where}.replacementPoints {len(rep) // 2} 點超過 native buffer 上限"
                f" {MAX_REPLACEMENT_POINTS}"
            )
            rep = None
        elif rep is not None and exp is not None and width is not None and "centerShift" in raw:
            rw = raw.get("replacementWidth")
            problem = center_shift_error(exp, width / 2, rep, rw if type(rw) is int else width, raw["centerShift"])
            if problem:
                errors.append(f"{where}.replacementPoints（center-shift）{problem}")
            else:
                center_shift = True
        elif rep is not None and exp is not None and width is not None and "dropVertex" in raw:
            k = raw["dropVertex"]
            ks = [k] if isinstance(k, int) else k if isinstance(k, list) else None
            dropped = None
            if ks and all(isinstance(v, int) and not isinstance(v, bool) for v in ks):
                dropped = drop_vertices(exp, ks)
            if dropped is None:
                errors.append(
                    f"{where}.dropVertex 必須是 0-based 點序或互異點序陣列（0..{len(exp) // 2 - 1}，"
                    f"至少留 2 點；頭尾端點最多移一個且不可連同相鄰點；得到 {k!r}）"
                )
            elif dropped != rep:
                errors.append(
                    f"{where}.replacementPoints 不等於 expectedPoints 拿掉第 {k} 點（drop-vertex 只准移除該點）"
                )
            else:
                drop_k = tuple(sorted(ks))
                target = raw.get("trimTo")
                if not drops_endpoint(exp, drop_k):
                    if "trimTo" in raw:
                        errors.append(f"{where}.trimTo 只用於移除頭尾端點（這筆只移內點）")
                else:
                    ti = target.get("index") if isinstance(target, dict) else None
                    if not isinstance(ti, int) or isinstance(ti, bool) or ti < 0:
                        errors.append(f"{where}.trimTo.index 必填（移除頭尾端點後接在同圖哪一條街，0-based）")
                    elif ti == idx:
                        errors.append(f"{where}.trimTo 不能指向自己")
                    else:
                        trim_to = ti
            if "bridgeTo" in raw:
                errors.append(f"{where}.bridgeTo 只用於 gap-bridge（這筆是 drop-vertex）")
        elif rep is not None and exp is not None and width is not None and "medianSplit" in raw:
            ms = raw["medianSplit"] if isinstance(raw["medianSplit"], dict) else {}
            problem = carriageway_error(exp, width / 2, rep)
            if problem:
                errors.append(f"{where}.replacementPoints（median-split 車道線）{problem}")
            pair = ms.get("pair") if isinstance(ms.get("pair"), dict) else {}
            pds, pno = pair.get("supplement"), pair.get("no")
            pair_ok = (isinstance(pds, str) and bool(pds.strip())
                       and isinstance(pno, int) and not isinstance(pno, bool) and pno >= 1)
            if not pair_ok:
                errors.append(f"{where}.medianSplit.pair 必填（對向車道的補充道路 {{supplement: dataset, no: 號碼}}）")
            ev = ms.get("medianEvidence") if isinstance(ms.get("medianEvidence"), dict) else {}
            ns, off = ev.get("samples"), ev.get("offCarriageway")
            if not (isinstance(ns, int) and isinstance(off, int) and not isinstance(ns, bool)
                    and not isinstance(off, bool) and ns >= _SPLIT_MIN_SAMPLES and 0 <= off <= ns):
                errors.append(
                    f"{where}.medianSplit.medianEvidence 必填（原中線取樣數 samples >= {_SPLIT_MIN_SAMPLES}"
                    "、其中不在車道鋪面上的 offCarriageway）"
                )
            elif off / ns < _SPLIT_MIN_OFF_ROAD:
                errors.append(
                    f"{where} 原中線只有 {off}/{ns} 不在車道鋪面上（下限 {_SPLIT_MIN_OFF_ROAD:.0%}），"
                    "不是「線畫在分隔帶上」，不准拆線"
                )
            if "replacementWidth" not in raw:
                errors.append(f"{where}.medianSplit 必須搭配 replacementWidth（車道寬）")
            for key in ("bridgeTo", "detachFrom"):
                if key in raw:
                    errors.append(f"{where}.{key} 不能和 medianSplit 並用")
            if pair_ok and not problem:
                split_pair = (pds, pno)
        elif rep is not None and exp is not None and width is not None and "detachFrom" in raw:
            cut = trim_detach(exp, rep)
            if cut is None:
                errors.append(
                    f"{where}.replacementPoints 不是 expectedPoints 從頭或尾沿原線截短"
                    "（trim-detach 的新端點要落在原線上、其餘點不動）"
                )
            elif cut[1] > _BRIDGE_MAX_LEN:
                errors.append(f"{where} trim-detach 截掉 {cut[1]:.1f} 格超過上限 {_BRIDGE_MAX_LEN:g}")
            target = raw.get("detachFrom")
            ti = target.get("index") if isinstance(target, dict) else None
            if not isinstance(ti, int) or isinstance(ti, bool) or ti < 0:
                errors.append(f"{where}.detachFrom.index 必填（端點退離同圖哪一條街，0-based）")
            elif ti == idx:
                errors.append(f"{where}.detachFrom 不能指向自己")
            elif cut is not None and cut[1] <= _BRIDGE_MAX_LEN:
                detach_from = ti
            if "bridgeTo" in raw:
                errors.append(f"{where}.bridgeTo 只用於 gap-bridge（這筆是 trim-detach）")
        elif rep is not None and exp is not None and width is not None and "navCut" in raw:
            cut = cut_insert(exp, rep)
            nc = raw["navCut"]
            if cut is None:
                errors.append(
                    f"{where}.replacementPoints 不是 expectedPoints 在同一段內依序插入兩個共線點"
                    "（median-cut 地圖上要是同一條線、其餘點不動）"
                )
            elif not (isinstance(nc, list) and len(nc) == 1 and type(nc[0]) is int and nc[0] == cut[0]):
                errors.append(f"{where}.navCut 必須是 [{cut[0]}]（只拿掉兩個插入點之間那一段，得到 {nc!r}）")
            elif cut[1] > _CUT_MAX_LEN:
                errors.append(f"{where} median-cut 拿掉 {cut[1]:.1f} 格超過上限 {_CUT_MAX_LEN:g}（只跨分隔帶，不是刪路）")
            elif "noJunction" not in raw:
                errors.append(f"{where}.navCut 必須搭配 noJunction（列被穿過的那條街，兩截才不會各自吸回去）")
            else:
                nav_cut = cut[0]
            if "bridgeTo" in raw:
                errors.append(f"{where}.bridgeTo 只用於 gap-bridge（這筆是 median-cut）")
        elif rep is not None and exp is not None and width is not None:
            # 只認核准過的規則：rect-outline → 中心線、gap-bridge 端點接線；其餘 fail-closed
            if rect_centerline(exp, width) == rep:
                if "bridgeTo" in raw:
                    errors.append(f"{where}.bridgeTo 只用於 gap-bridge（這筆是 rect-outline 中心線）")
            else:
                bridge = bridge_extension(exp, rep)
                if bridge is None:
                    errors.append(
                        f"{where}.replacementPoints 不是 rect-outline 中心線，也不是只在一端接"
                        f" <= {_BRIDGE_MAX_ADDED} 點的 gap-bridge（移除內點要寫 dropVertex；"
                        "新規則要先人工核准並改 gen_street_repairs.py 的判定）"
                    )
                else:
                    length = polyline_length(bridge[1])
                    if length > _BRIDGE_MAX_LEN:
                        errors.append(
                            f"{where} gap-bridge 接線長 {length:.1f} 格超過上限 {_BRIDGE_MAX_LEN:g}"
                            "（長路段是新增道路，不是修正作者的街）"
                        )
                    target = raw.get("bridgeTo")
                    ti = target.get("index") if isinstance(target, dict) else None
                    if not isinstance(ti, int) or isinstance(ti, bool) or ti < 0:
                        errors.append(f"{where}.bridgeTo.index 必填（接到同圖哪一條街，0-based）")
                    elif ti == idx:
                        errors.append(f"{where}.bridgeTo 不能接回自己")
                    else:
                        bridge_to = ti

    hide = raw.get("hideLabel", False)
    if hide is not True and hide is not False:
        errors.append(f"{where}.hideLabel 只能是 true 或省略")
        hide = False
    new_width = None
    if "replacementWidth" in raw:
        rw = raw["replacementWidth"]
        if not isinstance(rw, int) or isinstance(rw, bool) or not 1 <= rw <= _WIDTH_MAX:
            errors.append(f"{where}.replacementWidth 必須是 1..{_WIDTH_MAX} 的整數（主 MOD 只收整數路寬）")
        elif hide or ("replacementPoints" in raw and not any(k in raw for k in ("medianSplit", "dropVertex", "centerShift"))):
            errors.append(
                f"{where}.replacementWidth 只能單獨使用（width-fix 點列不動、不隱藏路名；"
                "只有 median-split、drop-vertex、center-shift 可以和 replacementPoints 並用）"
            )
        elif width is not None and rw == width:
            errors.append(f"{where}.replacementWidth 等於 expectedWidth＝空修正")
        elif ("medianSplit" in raw or "centerShift" in raw) and width is not None and rw >= width:
            errors.append(f"{where}.replacementWidth 要比原路寬 {width:g} 窄（median-split 是車道寬、center-shift 只准收窄）")
        elif "centerShift" in raw:
            new_width = rw if center_shift else None  # 證據在 centerShift.sections，上面已驗
        elif exp is not None:
            line = rep if "medianSplit" in raw else exp
            problem = width_evidence_error(line, rw, raw.get("widthEvidence")) if line else "車道線不合法"
            if problem:
                errors.append(f"{where}.widthEvidence {problem}")
            else:
                new_width = rw
    elif "widthEvidence" in raw:
        errors.append(f"{where}.widthEvidence 只用於 width-fix／median-split（這筆沒有 replacementWidth）")
    if not hide and rep is None and "replacementWidth" not in raw and "noJunction" not in raw:
        errors.append(f"{where} 既不改幾何也不隱藏路名＝空修正，請刪除")
    if "bridgeTo" in raw and rep is None:
        errors.append(f"{where}.bridgeTo 只用於 gap-bridge（這筆沒有 replacementPoints）")
    if "dropVertex" in raw and rep is None:
        errors.append(f"{where}.dropVertex 必須搭配 replacementPoints")
    if "trimTo" in raw and "dropVertex" not in raw:
        errors.append(f"{where}.trimTo 只用於 drop-vertex 移除頭尾端點")
    for key in ("medianSplit", "detachFrom", "navCut", "centerShift"):
        if key in raw and rep is None:
            errors.append(f"{where}.{key} 必須搭配 replacementPoints")
    if "navCut" in raw and any(k in raw for k in ("dropVertex", "medianSplit", "detachFrom")):
        errors.append(f"{where}.navCut 不能和 dropVertex／medianSplit／detachFrom 並用（median-cut 只插兩點）")
    clash = [k for k in ("dropVertex", "trimTo", "bridgeTo", "medianSplit", "detachFrom", "navCut", "hideLabel",
                         "widthEvidence") if k in raw]
    if "centerShift" in raw and clash:
        errors.append(f"{where}.centerShift 不能和 {clash} 並用（center-shift 只逐點平移，路寬證據寫在 centerShift）")
    no_junction = None
    if "noJunction" in raw:
        nj = raw["noJunction"]
        if (not isinstance(nj, list) or not 1 <= len(nj) <= _NOJ_MAX
                or not all(type(v) is int and v >= 0 for v in nj) or len(set(nj)) != len(nj) or idx in nj):
            errors.append(f"{where}.noJunction 必須是 1..{_NOJ_MAX} 個互異、>= 0、不含自己的同圖街道序號（得到 {nj!r}）")
        else:
            ev = raw.get("noJunctionEvidence")
            blockers = ev.get("blockers") if isinstance(ev, dict) else None
            if not (isinstance(blockers, list) and blockers and all(
                    isinstance(b, dict) and all(type(b.get(k)) in (int, float) for k in ("x", "y"))
                    and isinstance(b.get("object"), str) and b["object"].strip() for b in blockers)):
                errors.append(f"{where}.noJunctionEvidence.blockers 必填（擋在兩街之間的地圖物件，每個寫 x、y、object）")
            else:
                no_junction = tuple(nj)
    elif "noJunctionEvidence" in raw:
        errors.append(f"{where}.noJunctionEvidence 只用於 noJunction")

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
        bridge_to,
        drop_k,
        trim_to,
        new_width,
        split_pair,
        detach_from,
        no_junction,
        nav_cut,
        center_shift,
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
    # no-junction 寫成對稱：主 MOD 要兩條街都有相符的修正才生效，列回本筆讓兩筆互相作證
    by_index = {o.index: o for o in ops}
    for o in ops:
        for t in o.no_junction or ():
            other = by_index.get(t)
            if other is None or o.index not in (other.no_junction or ()):
                errors.append(
                    f"{path.name} #{o.index}.noJunction 列了 #{t}，但 #{t} 沒有一筆 noJunction 列回 #{o.index} 的修正"
                    "（資料要對稱：主 MOD 要兩條街都有相符的修正才生效）"
                )
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
    kinds = [classify_op(o) for p in pins_by_ds.values() for o in p.ops]
    lines = [
        f"-- {REPAIR_TABLE_REL.name}（生成檔，勿手編）",
        f"-- 由 scripts/gen_street_repairs.py 從 {REPAIRS_DIR_NAME}/*.json 編譯",
        f"-- {len(pins_by_ds)} 個 dataset／{total} 筆修正（中心線 {kinds.count(KIND_RECT)}、"
        f"接線 {kinds.count(KIND_BRIDGE)}、移除轉折點 {kinds.count(KIND_DROP)}、"
        f"換路寬 {kinds.count(KIND_WIDTH)}、中線平移 {kinds.count(KIND_SHIFT)}、分隔路拆線 {kinds.count(KIND_SPLIT)}、"
        f"端點退離 {kinds.count(KIND_DETACH)}、拿掉穿越分隔帶的段 {kinds.count(KIND_CUT)}、"
        f"不建路口 {kinds.count(KIND_NOJ)}、隱藏標籤候選 {kinds.count(KIND_HIDE)}）",
        "--",
        "-- 執行期契約：逐值比對 expectedWidth／expectedPoints，不符就略過該筆並 log",
        "-- （上游改版＝安全退回原樣，不擋同圖其他修正、也不擋新道路）。",
        "-- replacementWidth 只換路寬、點列不動；主 MOD 42.21.0-0.46.0 及更早版本不認得它，",
        "-- 該筆當空修正略過（log 一次），照作者路寬。",
        "-- noJunction（不和這幾條同圖街建路口）／navCut（只從導航拿掉這幾段）：主 MOD 0.51.0 及更早版本",
        "-- 不認得——只帶 noJunction 的筆當空修正略過（log 一次），navCut 的筆只套插了共線點的點列，照舊相通。",
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
            f"-- 逐筆理由（rect-outline／gap-bridge／drop-vertex／width-fix／center-shift／median-split／trim-detach／"
            f"median-cut／no-junction／exact-copy）在 {REPAIRS_DIR_NAME}/{ds}.json 的 reason；"
            "有 replacementPoints＝改幾何，有 replacementWidth＝換路寬，有 hideLabel＝藏重複路名，"
            "有 navCut／noJunction＝只改導航路網"
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
            if o.replacement_width is not None:
                parts.append(f"replacementWidth = {o.replacement_width}")
            if o.replacement_points:
                parts.append(f"replacementPoints = {_fmt_flat(o.replacement_points)}")
            if o.hide_label:
                parts.append("hideLabel = true")
                parts.append(
                    "reference = { index = %d, width = %s, points = %s }"
                    % (o.ref_index, _fmt_num(o.ref_width), _fmt_flat(o.ref_points))
                )
            if o.nav_cut is not None:
                parts.append(f"navCut = {{ {o.nav_cut} }}")
            if o.no_junction:
                parts.append("noJunction = { " + ", ".join(str(v) for v in o.no_junction) + " }")
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
) -> tuple[list[str], list[str]]:
    """比對本機上游／vanilla 副本，回報 pin 已對不上的筆數。→ (warnings, errors)

    漂移只回報（warnings）。pin 是人工核准的資料，generator 不得覆蓋或抹掉——執行期本來就會逐值
    比對後安全略過，漂移的代價是「該筆修正失效」，不是壞掉。只有 center-shift 讓原本相接的街斷開是
    errors：那是這份資料自己錯（上游沒變也會斷）。
    """
    warnings: list[str] = []
    errors: list[str] = []
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
            # 幾何一律用執行期真的會套的：相符的筆換成修正後的點列與路寬，漂移的筆照上游
            ops_by = {o.index: o for o in p.ops if o.index not in stale}

            def applied(o: Op) -> tuple[list[float], float]:
                return o.replacement_points or o.expected_points, o.replacement_width or o.expected_width

            def street_now(j: int) -> tuple[list[float], float]:
                return applied(ops_by[j]) if j in ops_by else (up[j].flat, up[j].width or 0)

            # gap-bridge 的新端點必須落在目標街上：目標街被上游改動、或被本包平移時接線就懸空了
            loose = []
            for o in p.ops:
                if o.bridge_to is None or o.index in stale:
                    continue
                _end, seg = bridge_extension(o.expected_points, o.replacement_points)
                if (o.bridge_to >= len(up) or point_polyline_distance(
                        seg[-2], seg[-1], street_now(o.bridge_to)[0]) > _BRIDGE_SNAP):
                    loose.append(o.index)
            if loose:
                warnings.append(
                    f"{ds} {len(loose)} 筆 gap-bridge 的新端點不在目標街 {_BRIDGE_SNAP:g} 格內"
                    f"（須人工覆核）：index {loose[:8]}"
                )
            # drop-vertex 剪掉頭尾端點：新端點要落在 trimTo 街半寬內，否則路口就斷了
            cut = []
            for o in p.ops:
                if o.trim_to is None or o.index in stale:
                    continue
                rep = o.replacement_points
                end = rep[:2] if 0 in o.drop_vertex else rep[-2:]
                t = up[o.trim_to] if o.trim_to < len(up) else None
                if t is None or not t.width or point_polyline_distance(*end, t.flat) > t.width / 2:
                    cut.append(o.index)
            if cut:
                warnings.append(
                    f"{ds} {len(cut)} 筆 drop-vertex 剪掉端點後新端點不在 trimTo 街半寬內"
                    f"（路口會斷，須人工覆核）：index {cut[:8]}"
                )
            # trim-detach：原端點本來在吸附距離內、新端點退到吸附距離外、新線不碰那條街
            stuck = []
            for o in p.ops:
                if o.detach_from is None or o.index in stale:
                    continue
                end, _cut = trim_detach(o.expected_points, o.replacement_points)
                old = o.expected_points[-2:] if end else o.expected_points[:2]
                new = o.replacement_points[-2:] if end else o.replacement_points[:2]
                t = up[o.detach_from] if o.detach_from < len(up) else None
                tol = o.expected_width / 2 + (t.width or 0) / 2 + _DETACH_SLACK if t else 0
                if (t is None or not t.width
                        or point_polyline_distance(*old, t.flat) > tol
                        or point_polyline_distance(*new, t.flat) <= tol + _DETACH_MARGIN
                        or segments_cross(o.replacement_points, t.flat)):
                    stuck.append(o.index)
            if stuck:
                warnings.append(
                    f"{ds} {len(stuck)} 筆 trim-detach 原端點不在 detachFrom 街吸附距離內、或新端點仍在"
                    f"吸附距離＋{_DETACH_MARGIN:g} 格內、或新線碰到那條街（須人工覆核）：index {stuck[:8]}"
                )
            # center-shift：原本相接（相交或端點在吸附距離內）的街，套用本包全部修正後仍要相接。
            # 刻意斷開的（trim-detach 退離它、noJunction 列了它）不算
            broken = []
            for o in p.ops:
                if not o.center_shift or o.index in stale:
                    continue
                a, wa = applied(o)
                xs, ys = o.expected_points[0::2], o.expected_points[1::2]
                for j, st in enumerate(up):
                    if j == o.index or len(st.flat) < 4 or not st.width or j in (o.no_junction or ()):
                        continue
                    other = ops_by.get(j)
                    if other is not None and (other.detach_from == o.index or o.index in (other.no_junction or ())):
                        continue
                    m = o.expected_width / 2 + st.width / 2 + _DETACH_SLACK
                    if (max(st.flat[0::2]) < min(xs) - m or min(st.flat[0::2]) > max(xs) + m
                            or max(st.flat[1::2]) < min(ys) - m or min(st.flat[1::2]) > max(ys) + m):
                        continue
                    if linked(o.expected_points, o.expected_width, st.flat, st.width) and not linked(a, wa, *street_now(j)):
                        broken.append((o.index, j))
            if broken:
                errors.append(
                    f"{ds} {len(broken)} 對 center-shift 平移後原本相接的街斷開了（路口要用 gap-bridge 接回或少移一點）"
                    f"：{broken[:8]}"
                )
            # no-junction：兩條街在 NavCore 本來真的相通（相交或某一端點在吸附距離內），否則這對是多餘的；
            # median-cut 拿掉的那段要穿過 noJunction 列的街。每對從序號小的那筆看一次，幾何用套用後的點列與路寬
            idle, uncut = [], []
            for o in p.ops:
                if not o.no_junction or o.index in stale:
                    continue
                a, wa = applied(o)
                for t in o.no_junction:
                    if t < o.index or t not in ops_by:
                        continue
                    if not linked(a, wa, *applied(ops_by[t])):
                        idle.append((o.index, t))
                if o.nav_cut is not None:
                    seg = a[2 * o.nav_cut:2 * o.nav_cut + 4]
                    if not any(segments_cross(seg, applied(ops_by[t])[0]) for t in o.no_junction if t in ops_by):
                        uncut.append(o.index)
            if idle:
                warnings.append(
                    f"{ds} {len(idle)} 對 noJunction 的兩條街本來就不相交、端點也不在吸附距離內（多餘，須人工覆核）"
                    f"：{idle[:8]}"
                )
            if uncut:
                warnings.append(
                    f"{ds} {len(uncut)} 筆 median-cut 拿掉的段沒有穿過 noJunction 列的街（切錯地方，須人工覆核）"
                    f"：index {uncut[:8]}"
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
                f"{ds} {len(bad)} 筆 reference 與 vanilla 不符（執行期不會隱藏路名；"
                f"主 MOD RoadPatches 的 patch.legacy 收錄該上一版官方幾何者除外）"
                f"：index {bad[:8]}{' …' if len(bad) > 8 else ''}"
            )
    return warnings, errors


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
        errors.extend(split_pair_errors(project_root, pins_by_ds))
    return pins_by_ds, errors, warnings


# 與 gen_road_supplements.SUPPLEMENTS_DIR_NAME 同一個目錄（那支 import 本檔，不能反向 import）
SUPPLEMENTS_DIR_NAME = "road-supplements"


def split_pair_errors(project_root: Path, pins_by_ds: dict[str, Pins]) -> list[str]:
    """median-split 的對向車道：pair 指到的補充道路要存在、符合車道線規則、和本筆分在原線兩側。"""
    errors: list[str] = []
    cache: dict[str, dict | None] = {}
    for ds in sorted(pins_by_ds):
        p = pins_by_ds[ds]
        for o in p.ops:
            if o.split_pair is None:
                continue
            sds, no = o.split_pair
            if sds not in cache:
                try:
                    data = json.loads((project_root / SUPPLEMENTS_DIR_NAME / f"{sds}.json").read_text(encoding="utf-8-sig"))
                    cache[sds] = {r.get("no"): r.get("points") for r in data.get("roads", []) if isinstance(r, dict)}
                except (OSError, json.JSONDecodeError, AttributeError):
                    cache[sds] = None
            where = f"{ds} #{o.index} median-split pair {sds} {no:02d}"
            raw = (cache[sds] or {}).get(no)
            if (not isinstance(raw, list) or len(raw) < 4 or len(raw) % 2
                    or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in raw)):
                errors.append(f"{where} 找不到這條補充道路（{SUPPLEMENTS_DIR_NAME}/{sds}.json）")
                continue
            pts = [float(v) for v in raw]
            problem = carriageway_error(o.expected_points, o.expected_width / 2, pts)
            if problem:
                errors.append(f"{where} {problem}")
            elif signed_side(pts, o.expected_points) * signed_side(o.replacement_points, o.expected_points) >= 0:
                errors.append(f"{where} 和本筆車道線在原線同一側（兩條車道線要分在原線兩側）")
    return errors


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
    warns, errs = survey_upstream(pins_by_ds, prefer=prefer, game_dir=game_dir)
    return Result(errors + errs, warnings + warns)


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
    '    <street name="Stub Rd" width="5">\n'
    '        <points><point x="200" y="300" /><point x="260" y="300" /></points>\n'
    "    </street>\n"
    '    <street name="Cross Ave" width="5">\n'
    '        <points><point x="190" y="250" /><point x="190" y="350" /></points>\n'
    "    </street>\n"
    '    <street name="Bend Ln" width="6">\n'
    "        <points>\n"
    '            <point x="300" y="500" /><point x="330" y="503" />\n'
    '            <point x="360" y="500" /><point x="390" y="500" />\n'
    "        </points>\n"
    "    </street>\n"
    '    <street name="Tail Rd" width="6">\n'
    "        <points>\n"
    '            <point x="400" y="600" /><point x="410" y="601" />\n'
    '            <point x="430" y="600" /><point x="440" y="604" />\n'
    "        </points>\n"
    "    </street>\n"
    '    <street name="Long Ave" width="10">\n'
    '        <points><point x="432" y="580" /><point x="432" y="700" /></points>\n'
    "    </street>\n"
    '    <street name="Wide Blvd" width="5">\n'
    '        <points><point x="500" y="700" /><point x="500.5" y="800" /></points>\n'
    "    </street>\n"
    '    <street name="Split Pike" width="18">\n'
    '        <points><point x="600" y="900" /><point x="800" y="900" /></points>\n'
    "    </street>\n"
    '    <street name="Dead End St" width="8">\n'
    '        <points><point x="700" y="1000" /><point x="700" y="1050" /><point x="700" y="1100" /></points>\n'
    "    </street>\n"
    '    <street name="Fence Ave" width="10">\n'
    '        <points><point x="650" y="1000" /><point x="750" y="1000" /></points>\n'
    "    </street>\n"
    '    <street name="Gate Rd" width="8">\n'
    '        <points><point x="800" y="1000" /><point x="900" y="1000" /></points>\n'
    "    </street>\n"
    '    <street name="Fence Way" width="10">\n'
    '        <points><point x="850" y="950" /><point x="850" y="1050" /></points>\n'
    "    </street>\n"
    # center-shift：作者線在 x 1000、實際路面 x 999–1004（中心 1002、寬 6）；Side St 端點離線 5 格（平移後 7）
    '    <street name="Shift Rd" width="10">\n'
    '        <points><point x="1000" y="100" /><point x="1000" y="200" /></points>\n'
    "    </street>\n"
    '    <street name="Side St" width="4">\n'
    '        <points><point x="980" y="150" /><point x="995" y="150" /></points>\n'
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
            {
                "index": 2,
                "name": "Stub Rd",
                "expectedWidth": 5,
                "expectedPoints": [200, 300, 260, 300],
                "replacementPoints": [190, 300, 200, 300, 260, 300],
                "bridgeTo": {"index": 3, "name": "Cross Ave"},
                "reason": "gap-bridge",
            },
            {
                "index": 4,
                "name": "Bend Ln",
                "expectedWidth": 6,
                "expectedPoints": [300, 500, 330, 503, 360, 500, 390, 500],
                "dropVertex": 1,
                "replacementPoints": [300, 500, 360, 500, 390, 500],
                "reason": "drop-vertex",
            },
            {
                "index": 5,
                "name": "Tail Rd",
                "expectedWidth": 6,
                "expectedPoints": [400, 600, 410, 601, 430, 600, 440, 604],
                "dropVertex": [1, 3],
                "trimTo": {"index": 6, "name": "Long Ave"},
                "replacementPoints": [400, 600, 430, 600],
                "reason": "drop-vertex（內點＋尾端點）",
            },
            {
                "index": 7,
                "name": "Wide Blvd",
                "expectedWidth": 5,
                "expectedPoints": [500, 700, 500.5, 800],
                "replacementWidth": 11,
                "widthEvidence": {
                    "source": "pzmap road-surfaces --pz-build 42.21",
                    "sections": [{"from": [495, 720], "to": [505, 720]}, {"from": [505, 780], "to": [495, 780]}],
                },
                "reason": "width-fix",
            },
            {
                "index": 8,
                "name": "Split Pike",
                "expectedWidth": 18,
                "expectedPoints": [600, 900, 800, 900],
                "replacementPoints": [600, 895, 800, 895],
                "replacementWidth": 6,
                "widthEvidence": {
                    "source": "pzmap road-surfaces --pz-build 42.21",
                    "sections": [{"from": [650, 892], "to": [650, 897]}, {"from": [750, 897], "to": [750, 892]}],
                },
                "medianSplit": {"pair": {"supplement": "demo", "no": 1},
                                "medianEvidence": {"samples": 50, "offCarriageway": 40}},
                "reason": "median-split",
            },
            {
                "index": 9,
                "name": "Dead End St",
                "expectedWidth": 8,
                "expectedPoints": [700, 1000, 700, 1050, 700, 1100],
                "replacementPoints": [700, 1015, 700, 1050, 700, 1100],
                "detachFrom": {"index": 10, "name": "Fence Ave"},
                "reason": "trim-detach",
            },
            {
                "index": 11,
                "name": "Gate Rd",
                "expectedWidth": 8,
                "expectedPoints": [800, 1000, 900, 1000],
                "replacementPoints": [800, 1000, 848, 1000, 852, 1000, 900, 1000],
                "navCut": [1],
                "noJunction": [12],
                "noJunctionEvidence": {"blockers": [{"x": 850, "y": 1000, "object": "fencing_01_0"}]},
                "reason": "median-cut",
            },
            {
                "index": 12,
                "name": "Fence Way",
                "expectedWidth": 10,
                "expectedPoints": [850, 950, 850, 1050],
                "noJunction": [11],
                "noJunctionEvidence": {"blockers": [{"x": 850, "y": 1000, "object": "fencing_01_0"}]},
                "reason": "no-junction",
            },
            {
                "index": 13,
                "name": "Shift Rd",
                "expectedWidth": 10,
                "expectedPoints": [1000, 100, 1000, 200],
                "replacementPoints": [1002, 100, 1002, 200],
                "replacementWidth": 6,
                "centerShift": {
                    "source": "pzmap road-surfaces --pz-build 42.21",
                    "sections": [{"from": [999, 120], "to": [1004, 120]}, {"from": [1004, 180], "to": [999, 180]}],
                    "lanes": {"before": {"samples": 100, "onRoad": 40}, "after": {"samples": 100, "onRoad": 98}},
                },
                "reason": "center-shift",
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
    sup = root / SUPPLEMENTS_DIR_NAME
    sup.mkdir(parents=True, exist_ok=True)
    # median-split 的 pair：1 號在原線另一側（y 905）、2 號在同一側（y 897）
    (sup / "demo.json").write_text(json.dumps({"roads": [
        {"no": 1, "points": [600, 905, 800, 905]}, {"no": 2, "points": [600, 897, 800, 897]}]}), encoding="utf-8")
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
    doc = _pin_doc(); doc["operations"][2]["replacementPoints"] = [100, 300, 200, 300, 260, 300]
    cases.append(("gap-bridge 接線過長", doc, "超過上限"))
    doc = _pin_doc(); doc["operations"][2].pop("bridgeTo")
    cases.append(("gap-bridge 缺 bridgeTo", doc, "bridgeTo.index 必填"))
    doc = _pin_doc(); doc["operations"][2]["bridgeTo"] = {"index": 2}
    cases.append(("gap-bridge 接回自己", doc, "接回自己"))
    doc = _pin_doc(); doc["operations"][2]["replacementPoints"] = [190, 300, 201, 300, 260, 300]
    cases.append(("gap-bridge 改到原點列", doc, "也不是只在一端接"))
    doc = _pin_doc(); doc["operations"][2]["replacementPoints"] = [
        170, 300, 175, 300, 180, 300, 185, 300, 190, 300, 200, 300, 260, 300]
    cases.append(("gap-bridge 接太多點", doc, "也不是只在一端接"))
    doc = _pin_doc(); doc["operations"][1]["bridgeTo"] = {"index": 3}
    cases.append(("bridgeTo 用在隱藏路名", doc, "只用於 gap-bridge"))
    doc = _pin_doc(); doc["operations"][0]["bridgeTo"] = {"index": 3}
    cases.append(("bridgeTo 用在中心線", doc, "只用於 gap-bridge"))
    doc = _pin_doc(); doc["operations"][3].update(dropVertex=0, replacementPoints=[330, 503, 360, 500, 390, 500])
    cases.append(("drop-vertex 移除頭端點沒寫 trimTo", doc, "trimTo.index 必填"))
    doc = _pin_doc(); doc["operations"][3].update(dropVertex=3, replacementPoints=[300, 500, 330, 503, 360, 500])
    cases.append(("drop-vertex 移除尾端點沒寫 trimTo", doc, "trimTo.index 必填"))
    doc = _pin_doc(); doc["operations"][3]["dropVertex"] = True
    cases.append(("drop-vertex 點序不是整數", doc, "必須是 0-based 點序"))
    doc = _pin_doc(); doc["operations"][4].update(dropVertex=[0, 3], replacementPoints=[410, 601, 430, 600])
    cases.append(("drop-vertex 頭尾端點一起移", doc, "頭尾端點最多移一個"))
    doc = _pin_doc(); doc["operations"][4].update(dropVertex=[2, 3], replacementPoints=[400, 600, 410, 601])
    cases.append(("drop-vertex 端點連同相鄰點", doc, "不可連同相鄰點"))
    doc = _pin_doc(); doc["operations"][4].update(dropVertex=[1, 1])
    cases.append(("drop-vertex 點序重複", doc, "互異點序陣列"))
    doc = _pin_doc(); doc["operations"][4].update(dropVertex=[1, 2], replacementPoints=[400, 600, 440, 604])
    cases.append(("trimTo 用在只移內點", doc, "trimTo 只用於移除頭尾端點"))
    doc = _pin_doc(); doc["operations"][4]["trimTo"] = {"index": 5}
    cases.append(("trimTo 指向自己", doc, "不能指向自己"))
    doc = _pin_doc(); doc["operations"][2]["trimTo"] = {"index": 3}
    cases.append(("trimTo 用在 gap-bridge", doc, "只用於 drop-vertex"))
    doc = _pin_doc(); doc["operations"][3]["dropVertex"] = 2
    cases.append(("drop-vertex 點序與 replacement 不符", doc, "拿掉第 2 點"))
    doc = _pin_doc(); doc["operations"][3]["replacementPoints"] = [300, 500, 361, 500, 390, 500]
    cases.append(("drop-vertex 順手改到其他點", doc, "拿掉第 1 點"))
    doc = _pin_doc(); doc["operations"][3]["expectedPoints"] = [300, 500, 330, 503, 360, 501, 390, 500]
    cases.append(("drop-vertex expectedPoints 不符", doc, "拿掉第 1 點"))
    doc = _pin_doc(); doc["operations"][3].pop("dropVertex")
    cases.append(("移除內點沒寫 dropVertex", doc, "移除內點要寫 dropVertex"))
    doc = _pin_doc(); doc["operations"][3].pop("replacementPoints")
    cases.append(("dropVertex 缺 replacementPoints", doc, "必須搭配 replacementPoints"))
    doc = _pin_doc(); doc["operations"][3]["bridgeTo"] = {"index": 3}
    cases.append(("bridgeTo 用在 drop-vertex", doc, "只用於 gap-bridge"))
    for bad in (10.5, 0, 65, True, "11"):
        doc = _pin_doc(); doc["operations"][5]["replacementWidth"] = bad
        cases.append((f"width-fix 路寬 {bad!r} 不合法", doc, "1..64 的整數"))
    doc = _pin_doc(); doc["operations"][5]["replacementWidth"] = 5
    cases.append(("width-fix 路寬沒變", doc, "等於 expectedWidth"))
    doc = _pin_doc(); doc["operations"][5]["replacementPoints"] = [500, 700, 500.5, 800]
    cases.append(("width-fix 搭配 replacementPoints", doc, "只能單獨使用"))
    doc = _pin_doc(); doc["operations"][5].update(hideLabel=True, reference={"index": 0, "width": 5, "points": [500, 700, 500.5, 800]})
    cases.append(("width-fix 搭配 hideLabel", doc, "只能單獨使用"))
    doc = _pin_doc(); doc["operations"][5].pop("widthEvidence")
    cases.append(("width-fix 缺證據", doc, "widthEvidence 必填"))
    doc = _pin_doc(); doc["operations"][5]["widthEvidence"]["sections"].pop()
    cases.append(("width-fix 只有一個橫截面", doc, "至少要 2 個"))
    doc = _pin_doc(); doc["operations"][5]["widthEvidence"]["sections"][1]["to"] = [494, 780]
    cases.append(("width-fix 橫截面量到的寬不符", doc, "量到 12 格"))
    doc = _pin_doc(); doc["operations"][5]["widthEvidence"]["sections"][0] = {"from": [498, 720], "to": [508, 720]}
    cases.append(("width-fix 中線偏離路面中心", doc, "離路面中心"))
    doc = _pin_doc(); doc["operations"][5]["widthEvidence"]["sections"][0] = {"from": [495, 650], "to": [505, 650]}
    cases.append(("width-fix 橫截面沒碰到這條街", doc, "沒有近乎垂直地穿過"))
    doc = _pin_doc(); doc["operations"][5]["widthEvidence"]["sections"][0] = {"from": [495, 715], "to": [505, 725]}
    cases.append(("width-fix 斜的橫截面", doc, "水平或垂直"))
    doc = _pin_doc(); doc["operations"][5]["widthEvidence"]["sections"][0] = {"from": [500, 695], "to": [500, 705]}
    cases.append(("width-fix 橫截面沿著街走", doc, "沒有近乎垂直地穿過"))
    doc = _pin_doc(); doc["operations"][5].update(expectedPoints=[480.5, 700, 520.5, 800], widthEvidence={
        "source": "x", "sections": [{"from": [495, 749], "to": [505, 749]}, {"from": [495, 750], "to": [505, 750]}]})
    cases.append(("width-fix 街斜交橫截面（量到的寬偏大）", doc, "沒有近乎垂直地穿過"))
    doc = _pin_doc(); doc["operations"][0]["widthEvidence"] = {"source": "x", "sections": []}
    cases.append(("widthEvidence 用在中心線", doc, "只用於 width-fix"))
    split, detach = 6, 7  # _pin_doc operations[] 的位置
    doc = _pin_doc(); doc["operations"][split]["replacementPoints"] = [600, 885, 800, 885]
    cases.append(("median-split 車道線離原線超過半寬", doc, "超過原路半寬"))
    doc = _pin_doc(); doc["operations"][split]["replacementPoints"] = [600, 899.5, 800, 899.5]
    cases.append(("median-split 車道線沒有移到單側", doc, "沒有移到單側車道"))
    doc = _pin_doc(); doc["operations"][split]["replacementWidth"] = 20
    cases.append(("median-split 車道寬沒有比原路窄", doc, "要比原路寬"))
    doc = _pin_doc(); doc["operations"][split].pop("replacementWidth")
    cases.append(("median-split 缺車道寬", doc, "必須搭配 replacementWidth"))
    doc = _pin_doc(); doc["operations"][split]["medianSplit"]["pair"]["no"] = 3
    cases.append(("median-split pair 補充道路不存在", doc, "找不到這條補充道路"))
    doc = _pin_doc(); doc["operations"][split]["medianSplit"]["pair"]["no"] = 2
    cases.append(("median-split pair 在同一側", doc, "同一側"))
    doc = _pin_doc(); doc["operations"][split]["medianSplit"].pop("pair")
    cases.append(("median-split 缺 pair", doc, "medianSplit.pair 必填"))
    doc = _pin_doc(); doc["operations"][split]["medianSplit"]["medianEvidence"]["offCarriageway"] = 10
    cases.append(("median-split 原中線多半在路面上", doc, "不准拆線"))
    doc = _pin_doc(); doc["operations"][split]["widthEvidence"]["sections"][0] = {"from": [650, 902], "to": [650, 907]}
    cases.append(("median-split 橫截面量的不是本筆車道", doc, "沒有近乎垂直地穿過"))
    doc = _pin_doc(); doc["operations"][detach]["replacementPoints"] = [701, 1015, 700, 1050, 700, 1100]
    cases.append(("trim-detach 新端點不在原線上", doc, "沿原線截短"))
    doc = _pin_doc(); doc["operations"][detach]["replacementPoints"] = [700, 1015, 700, 1051, 700, 1100]
    cases.append(("trim-detach 順手改到其他點", doc, "沿原線截短"))
    doc = _pin_doc(); doc["operations"][detach]["replacementPoints"] = [700, 1060, 700, 1100]
    cases.append(("trim-detach 截太長", doc, "trim-detach 截掉"))
    doc = _pin_doc(); doc["operations"][detach]["detachFrom"] = {"index": 9}
    cases.append(("trim-detach 指向自己", doc, "不能指向自己"))
    doc = _pin_doc(); doc["operations"][detach].pop("detachFrom")
    cases.append(("截短端點沒寫 detachFrom", doc, "也不是只在一端接"))
    doc = _pin_doc(); doc["operations"][detach].pop("replacementPoints")
    cases.append(("detachFrom 缺 replacementPoints", doc, "必須搭配 replacementPoints"))
    doc = _pin_doc(); doc["operations"][detach]["bridgeTo"] = {"index": 10}
    cases.append(("bridgeTo 用在 trim-detach", doc, "只用於 gap-bridge"))
    cut, noj = 8, 9
    doc = _pin_doc(); doc["operations"][noj]["noJunction"] = [12]
    cases.append(("noJunction 指向自己", doc, "不含自己"))
    for bad in ([11, 11], [-1], [True], list(range(13, 30)), [], "11"):
        doc = _pin_doc(); doc["operations"][noj]["noJunction"] = bad
        cases.append((f"noJunction 不合法 {bad!r}", doc, "noJunction 必須是"))
    doc = _pin_doc(); doc["operations"][noj]["noJunction"] = [10]
    cases.append(("noJunction 不對稱（對方沒列回）", doc, "列回"))
    doc = _pin_doc(); doc["operations"][noj].pop("noJunctionEvidence")
    cases.append(("noJunction 缺證據", doc, "blockers 必填"))
    doc = _pin_doc(); doc["operations"][noj]["noJunctionEvidence"] = {"blockers": [{"x": 850, "y": 1000, "object": " "}]}
    cases.append(("noJunction 證據沒寫物件", doc, "blockers 必填"))
    doc = _pin_doc(); doc["operations"][0]["noJunctionEvidence"] = {"blockers": []}
    cases.append(("noJunctionEvidence 單獨出現", doc, "只用於 noJunction"))
    doc = _pin_doc(); doc["operations"][cut]["replacementPoints"] = [800, 1000, 848, 1001, 852, 1000, 900, 1000]
    cases.append(("median-cut 插入點不共線", doc, "同一段內依序插入"))
    doc = _pin_doc(); doc["operations"][cut]["replacementPoints"] = [800, 1000, 852, 1000, 848, 1000, 900, 1000]
    cases.append(("median-cut 插入點順序反了", doc, "同一段內依序插入"))
    doc = _pin_doc(); doc["operations"][cut]["navCut"] = [2]
    cases.append(("median-cut 段序不是兩插入點之間", doc, "navCut 必須是 [1]"))
    doc = _pin_doc(); doc["operations"][cut]["replacementPoints"] = [800, 1000, 840, 1000, 860, 1000, 900, 1000]
    cases.append(("median-cut 拿掉太長", doc, "超過上限"))
    doc = _pin_doc(); doc["operations"][cut].pop("noJunction"); doc["operations"][cut].pop("noJunctionEvidence")
    cases.append(("median-cut 沒帶 noJunction", doc, "必須搭配 noJunction"))
    doc = _pin_doc(); doc["operations"][cut].pop("replacementPoints")
    cases.append(("navCut 缺 replacementPoints", doc, "必須搭配 replacementPoints"))
    doc = _pin_doc(); doc["operations"][cut]["dropVertex"] = 1
    cases.append(("navCut 和 dropVertex 並用", doc, "不能和"))
    shift = 10
    doc = _pin_doc(); doc["operations"][shift]["replacementPoints"] = [1002, 100, 1002, 150, 1002, 200]
    cases.append(("center-shift 增加點", doc, "點數要和"))
    doc = _pin_doc(); doc["operations"][shift]["replacementPoints"] = [1006, 100, 1006, 200]
    cases.append(("center-shift 平移超過原路半寬", doc, "超過原路半寬"))
    doc = _pin_doc(); doc["operations"][shift]["replacementPoints"] = [1000.25, 100, 1000.25, 200]
    cases.append(("center-shift 幾乎沒移（只換路寬）", doc, "每點平移都不到"))
    doc = _pin_doc(); doc["operations"][shift].update(expectedPoints=[1000, 100, 1000, 103], replacementPoints=[1002, 103, 1002, 100])
    cases.append(("center-shift 把段翻過來", doc, "方向反了"))
    doc = _pin_doc(); doc["operations"][shift]["centerShift"].pop("source")
    cases.append(("center-shift 證據沒寫 source", doc, "centerShift 必填"))
    doc = _pin_doc(); doc["operations"][shift]["centerShift"]["sections"].pop()
    cases.append(("center-shift 只有一個橫截面", doc, "至少要 2 個"))
    doc = _pin_doc(); doc["operations"][shift]["centerShift"]["sections"][0] = {"from": [997, 120], "to": [1002, 120]}
    cases.append(("center-shift 新線離截面路面中心太遠", doc, "超過 0.5 格"))
    doc = _pin_doc(); doc["operations"][shift]["centerShift"]["sections"][0] = {"from": [1000, 120], "to": [1004, 120]}
    cases.append(("center-shift 新路寬帶超出路面", doc, "的帶超出"))
    doc = _pin_doc(); doc["operations"][shift]["centerShift"]["sections"][0] = {"from": [999, 120], "to": [1004, 121]}
    cases.append(("center-shift 斜的橫截面", doc, "水平或垂直"))
    doc = _pin_doc(); doc["operations"][shift]["centerShift"]["lanes"]["after"]["onRoad"] = 85
    cases.append(("center-shift 修後靠右車身仍常出路面", doc, "下限 90%"))
    doc = _pin_doc(); doc["operations"][shift]["centerShift"]["lanes"]["before"]["onRoad"] = 99
    cases.append(("center-shift 沒比修前好", doc, "要比修前"))
    doc = _pin_doc(); doc["operations"][shift]["centerShift"].pop("lanes")
    cases.append(("center-shift 缺靠右取樣", doc, "lanes.before 必填"))
    doc = _pin_doc(); doc["operations"][shift]["replacementWidth"] = 12
    cases.append(("center-shift 路寬變寬", doc, "要比原路寬"))
    doc = _pin_doc(); doc["operations"][shift]["dropVertex"] = 0
    cases.append(("center-shift 和 dropVertex 並用", doc, "centerShift 不能和"))
    doc = _pin_doc(); doc["operations"][shift]["widthEvidence"] = {"source": "x", "sections": []}
    cases.append(("center-shift 另帶 widthEvidence", doc, "centerShift 不能和"))
    doc = _pin_doc(); doc["operations"][shift].pop("replacementPoints")
    cases.append(("centerShift 缺 replacementPoints", doc, "必須搭配 replacementPoints"))
    doc = _pin_doc(); doc["operations"][shift].pop("centerShift"); doc["operations"][shift].pop("replacementWidth")
    cases.append(("平移點列沒寫 centerShift（手繪新幾何）", doc, "rect-outline 中心線"))
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
        check(
            "gap-bridge 接線原樣落表、bridgeTo 不進執行期",
            "replacementPoints = { 190, 300, 200, 300, 260, 300 }" in lua and "bridgeTo" not in lua,
            lua,
        )
        check(
            "width-fix 原樣落表（整數路寬、不帶 replacementPoints）、widthEvidence 不進執行期",
            "ops[7] = { expectedWidth = 5, expectedPoints = { 500, 700, 500.5, 800 }, replacementWidth = 11 }" in lua
            and "widthEvidence" not in lua and "sections" not in lua,
            lua,
        )
        check(
            "drop-vertex 原樣落表、dropVertex／trimTo 不進執行期",
            "replacementPoints = { 300, 500, 360, 500, 390, 500 }" in lua
            and "replacementPoints = { 400, 600, 430, 600 }" in lua
            and "dropVertex" not in lua and "trimTo" not in lua,
            lua,
        )
        pins, _e, _w = load_pins(root / REPAIRS_DIR_NAME / "demo.json")
        check(
            "十種規則分類正確（剪端點仍屬 drop-vertex、只帶 noJunction 算 no-junction、平移＋路寬算 center-shift）",
            pins is not None
            and [classify_op(o) for o in pins.ops]
            == [KIND_RECT, KIND_HIDE, KIND_BRIDGE, KIND_DROP, KIND_DROP, KIND_WIDTH, KIND_SPLIT, KIND_DETACH,
                KIND_CUT, KIND_NOJ, KIND_SHIFT]
            and pins.ops[8].nav_cut == 1 and pins.ops[8].no_junction == (12,) and pins.ops[9].no_junction == (11,)
            and pins.ops[4].drop_vertex == (1, 3) and pins.ops[4].trim_to == 6
            and pins.ops[5].replacement_width == 11 and pins.ops[5].replacement_points is None
            and pins.ops[6].split_pair == ("demo", 1) and pins.ops[6].replacement_width == 6
            and pins.ops[7].detach_from == 10 and pins.ops[10].center_shift and pins.ops[10].replacement_width == 6,
        )
        check(
            "median-split 點列＋車道寬一起落表、trim-detach 截短點列落表、pair／detachFrom 不進執行期",
            "ops[8] = { expectedWidth = 18, expectedPoints = { 600, 900, 800, 900 }, replacementWidth = 6,"
            " replacementPoints = { 600, 895, 800, 895 } }" in lua
            and "replacementPoints = { 700, 1015, 700, 1050, 700, 1100 }" in lua
            and "medianSplit" not in lua and "detachFrom" not in lua,
            lua,
        )
        check(
            "median-cut 插點點列＋navCut、noJunction 落表（執行期要用），證據不進執行期",
            "ops[11] = { expectedWidth = 8, expectedPoints = { 800, 1000, 900, 1000 },"
            " replacementPoints = { 800, 1000, 848, 1000, 852, 1000, 900, 1000 }, navCut = { 1 }, noJunction = { 12 } }" in lua
            and "ops[12] = { expectedWidth = 10, expectedPoints = { 850, 950, 850, 1050 }, noJunction = { 11 } }" in lua
            and "noJunctionEvidence" not in lua and "blockers" not in lua,
            lua,
        )
        check(
            "center-shift 平移點列＋路寬一起落表、centerShift 證據不進執行期",
            "ops[13] = { expectedWidth = 10, expectedPoints = { 1000, 100, 1000, 200 }, replacementWidth = 6,"
            " replacementPoints = { 1002, 100, 1002, 200 } }" in lua
            and "centerShift" not in lua and "lanes" not in lua,
            lua,
        )
        res = _verify(root)
        check("verify 通過剛生成的檔",
              res.ok and not any(k in w for w in res.warnings
                                 for k in ("gap-bridge", "trimTo", "trim-detach", "noJunction", "median-cut", "center-shift")),
              str(res.errors + res.warnings))
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

    # gap-bridge 目標街被上游挪走：新端點懸空要回報
    with tempfile.TemporaryDirectory() as td:
        root = _fixture(Path(td) / "g", _pin_doc())
        gen(root)
        ws = root / "workshop" / "1" / "mods" / "demo" / "42" / "media" / "maps" / "Demo"
        (ws / "streets.xml").write_text(
            _XML.replace('x="190" y="250"', 'x="180" y="250"').replace('x="190" y="350"', 'x="180" y="350"'),
            encoding="utf-8",
        )
        res = _verify(root)
        check(
            "gap-bridge 目標街移動只警告",
            res.ok and any("不在目標街" in w for w in res.warnings),
            str(res.errors + res.warnings),
        )

    # trim-detach 新端點仍在吸附距離內（或原本就沒接）：只警告
    with tempfile.TemporaryDirectory() as td:
        doc = _pin_doc()
        doc["operations"][7]["replacementPoints"] = [700, 1012, 700, 1050, 700, 1100]
        root = _fixture(Path(td) / "t", doc)
        gen(root)
        res = _verify(root)
        check(
            "trim-detach 新端點仍在吸附距離內只警告",
            res.ok and any("trim-detach" in w for w in res.warnings),
            str(res.errors + res.warnings),
        )

    # 剪端點的 trimTo 街被上游挪走：新端點離開該街半寬＝路口斷了要回報
    with tempfile.TemporaryDirectory() as td:
        root = _fixture(Path(td) / "h", _pin_doc())
        gen(root)
        ws = root / "workshop" / "1" / "mods" / "demo" / "42" / "media" / "maps" / "Demo"
        (ws / "streets.xml").write_text(
            _XML.replace('x="432" y="580"', 'x="436" y="580"').replace('x="432" y="700"', 'x="436" y="700"'),
            encoding="utf-8",
        )
        res = _verify(root)
        check(
            "trimTo 街移出半寬只警告",
            res.ok and any("不在 trimTo 街半寬內" in w for w in res.warnings),
            str(res.errors + res.warnings),
        )

    # no-junction 列了兩條本來就不相通的街、median-cut 切的段沒穿過那條街：只警告
    with tempfile.TemporaryDirectory() as td:
        doc = _pin_doc()
        ev = {"blockers": [{"x": 850, "y": 1000, "object": "fencing_01_0"}]}
        doc["operations"].append({"index": 10, "name": "Fence Ave", "expectedWidth": 10,
                                  "expectedPoints": [650, 1000, 750, 1000], "noJunction": [12],
                                  "noJunctionEvidence": ev, "reason": "多餘"})
        doc["operations"][9]["noJunction"] = [11, 10]
        doc["operations"][8]["replacementPoints"] = [800, 1000, 820, 1000, 824, 1000, 900, 1000]
        root = _fixture(Path(td) / "j", doc)
        res, _ = gen(root)
        check("no-junction／median-cut 驗證資料本身合法", res.ok, str(res.errors))
        res = _verify(root)
        check(
            "noJunction 兩街本來不相通、median-cut 沒切到那條街：只警告",
            res.ok and any("多餘" in w and "(10, 12)" in w for w in res.warnings)
            and any("切錯地方" in w for w in res.warnings),
            str(res.errors + res.warnings),
        )

    # center-shift 讓原本相接的街斷開＝錯誤；用 gap-bridge 接到平移後的線就好（接線端點照套用後的幾何驗）
    with tempfile.TemporaryDirectory() as td:
        root = _fixture(Path(td) / "s", _pin_doc())
        ws = root / "workshop" / "1" / "mods" / "demo" / "42" / "media" / "maps" / "Demo"
        (ws / "streets.xml").write_text(_XML.replace('x="995" y="150"', 'x="991" y="150"'), encoding="utf-8")
        gen(root)
        res = _verify(root)
        check("center-shift 平移後 Side St 端點離線 11 格（吸附 9.5）＝錯誤",
              not res.ok and any("斷開" in e and "(13, 14)" in e for e in res.errors), str(res.errors + res.warnings))
        doc = _pin_doc()
        doc["operations"].append({"index": 14, "name": "Side St", "expectedWidth": 4,
                                  "expectedPoints": [980, 150, 991, 150], "replacementPoints": [980, 150, 991, 150, 1002, 150],
                                  "bridgeTo": {"index": 13, "name": "Shift Rd"}, "reason": "gap-bridge 接回平移後的線"})
        _fixture(root, doc)
        (ws / "streets.xml").write_text(_XML.replace('x="995" y="150"', 'x="991" y="150"'), encoding="utf-8")
        gen(root)
        res = _verify(root)
        check("gap-bridge 接到平移後的線：路口接回、接線端點照套用後的幾何（離原線 2 格不警告）",
              res.ok and not any("gap-bridge" in w for w in res.warnings), str(res.errors + res.warnings))

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
            kinds = [classify_op(o) for o in pins_by_ds[ds].ops]
            print(
                f"   {ds:24s} 中心線 {kinds.count(KIND_RECT):4d} 接線 {kinds.count(KIND_BRIDGE):4d}"
                f" 移除轉折點 {kinds.count(KIND_DROP):4d} 換路寬 {kinds.count(KIND_WIDTH):4d} 中線平移 {kinds.count(KIND_SHIFT):4d}"
                f" 分隔路拆線 {kinds.count(KIND_SPLIT):4d} 端點退離 {kinds.count(KIND_DETACH):4d}"
                f" 拿掉穿越段 {kinds.count(KIND_CUT):4d} 不建路口 {kinds.count(KIND_NOJ):4d}"
                f" 隱藏標籤候選 {kinds.count(KIND_HIDE):4d}"
            )
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
