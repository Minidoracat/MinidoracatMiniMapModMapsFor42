#!/usr/bin/env python3
"""道路資料狀態：map_tracker（本機 road-scan、CI diff/issue）與 verify_mod 共用的純函式。

三條本包道路資料線（各自 generator 擁有，這裡只讀）：
  street-names/<ds>/names.json   街名翻譯（gen_streets_i18n）
  road-repairs/<ds>.json         道路修正（gen_street_repairs）
  road-supplements/<ds>.json     補充道路（gen_road_supplements）

狀態檔 tracker-state/road_status.json：
  entries＝註冊 zip → 本機解析出的 workshop item 與地圖目錄（只由本機 road-scan --write 更新）
  items  ＝各相關 item 每個地圖目錄的作者道路資料現況（streets.xml sha256／街道數、
           worldmap.xml sha256）；本機 road-scan --write 與 CI 下載後都會更新
公開清單 docs/road-data.md 由 render_doc 生成：同一份資料永遠產出同一份位元組。

只用標準函式庫（CI 以 python3 執行）；上游內容只靜態讀檔，絕不執行。
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_road_supplements as grs  # noqa: E402
import gen_street_repairs as gsr  # noqa: E402
import gen_streets_i18n as gsi  # noqa: E402

STATUS_REL = Path("tracker-state") / "road_status.json"
DOC_REL = Path("docs") / "road-data.md"
DOC_COMMAND = "uv run scripts/map_tracker.py road-scan --prefer <steamcmd content 根> --write"

_STREET_RE = re.compile(rb"<street\b")
_ENTRY_RE = re.compile(r'\{\s*zip\s*=\s*"')


# ============================================================
# 掃描（作者道路資料現況）
# ============================================================
def scan_roads(bases: list[Path]) -> dict[str, dict]:
    """B42 有效內容基底（map_tracker._mod_content_bases 的輸出，順序即優先序）→
    {地圖目錄: {streets_sha256, street_count, worldmap_sha256}}。同名地圖目錄出現在
    多個基底時首見為準（版本資料夾先於 common，同 gen_streets_i18n.find_streets_xml）。"""
    # ponytail: 同 item 內多個 mod 有同名地圖目錄時取排序首見；互斥變體道路不同才需要分開記
    maps: dict[str, dict] = {}
    for base in bases:
        maps_dir = base / "media" / "maps"
        if not maps_dir.is_dir():
            continue
        for d in sorted(p for p in maps_dir.iterdir() if p.is_dir()):
            m = maps.setdefault(d.name, {"streets_sha256": None, "street_count": 0,
                                         "worldmap_sha256": None})
            streets = d / "streets.xml"
            if m["streets_sha256"] is None and streets.is_file():
                data = streets.read_bytes()
                m["streets_sha256"] = hashlib.sha256(data).hexdigest()
                m["street_count"] = len(_STREET_RE.findall(data))
            worldmap = d / "worldmap.xml"
            if m["worldmap_sha256"] is None and worldmap.is_file():
                m["worldmap_sha256"] = gsi.file_sha256(worldmap)
    return maps


def merge_items(old_items: dict, scanned: dict[str, dict], now: str) -> dict:
    """掃描結果併入 items：地圖現況沒變的 item 原樣保留（含 checked），只有變了或新增的
    才換成新紀錄——否則每次掃描都會製造只有時間戳的假 diff。未掃到的 item 不動。"""
    out = dict(old_items)
    for wid, maps in scanned.items():
        prev = old_items.get(wid)
        if not isinstance(prev, dict) or prev.get("maps") != maps:
            out[wid] = {"checked": now, "maps": maps}
    return out


def load_status(path: Path) -> tuple[dict, str | None]:
    """→ (狀態, 錯誤)。缺檔＝空狀態；壞檔回錯誤由呼叫端決定要不要中止。"""
    empty = {"entries": {}, "items": {}}
    if not path.is_file():
        return empty, None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        return empty, f"{path.name} 無法解析：{e}"
    if not isinstance(data, dict):
        return empty, f"{path.name} 頂層必須是物件"
    entries = data.get("entries") if isinstance(data.get("entries"), dict) else {}
    items = data.get("items") if isinstance(data.get("items"), dict) else {}
    return {**data, "entries": entries, "items": items}, None


def registered_dirs(status: dict) -> dict[str, set[str]]:
    """entries → {workshop_id: {註冊的地圖目錄}}。"""
    out: dict[str, set[str]] = {}
    for e in status.get("entries", {}).values():
        if isinstance(e, dict) and e.get("workshop_id") and e.get("map_dir"):
            out.setdefault(str(e["workshop_id"]), set()).add(str(e["map_dir"]))
    return out


# ============================================================
# 本包道路資料（三條資料線）
# ============================================================
def load_road_data(root: Path) -> tuple[dict, list[str]]:
    """→ ({"names": {ds: {workshop_id, map_dir, sha, count}}, "repairs": {ds: Pins},
    "supplements": {ds: Supplement}}, 錯誤)。任一檔讀不起來就列錯誤——少讀一份＝
    少判定一組 pin，必須看得見。"""
    errors: list[str] = []
    names: dict[str, dict] = {}
    for p in gsi.discover_names_files(root / "street-names", None):
        try:
            data = gsi.read_names_json(p)
        except (OSError, ValueError) as e:
            errors.append(f"street-names/{p.parent.name}/names.json 讀取失敗：{e}")
            continue
        src = data.get("source") if isinstance(data.get("source"), dict) else {}
        table = data.get("names") if isinstance(data.get("names"), dict) else {}
        names[p.parent.name] = {
            "workshop_id": str(src.get("workshop_id") or ""),
            "map_dir": str(src.get("map_dir") or ""),
            "sha": src.get("streets_xml_sha256") or None,
            "count": len(table),
        }
    repairs = {}
    for f in sorted((root / gsr.REPAIRS_DIR_NAME).glob("*.json")):
        pins, errs, _warns = gsr.load_pins(f)
        errors += errs
        if pins is not None:
            repairs[pins.dataset] = pins
    supplements = {}
    for f in sorted((root / grs.SUPPLEMENTS_DIR_NAME).glob("*.json")):
        sup, errs, _warns = grs.load_supplement(f)
        errors += errs
        if sup is not None:
            supplements[sup.dataset] = sup
    return {"names": names, "repairs": repairs, "supplements": supplements}, errors


def pin_index(data: dict) -> dict[tuple[str, str], dict[str, list]]:
    """→ {(workshop_id, map_dir): {"names": [(ds, sha)], "repairs": [(ds, sha)],
    "supplements": [(ds, streets_sha, upstream_count, worldmap_sha)]}}。"""
    idx: dict[tuple[str, str], dict[str, list]] = {}

    def slot(wid: str, map_dir: str) -> dict[str, list]:
        return idx.setdefault((wid, map_dir), {"names": [], "repairs": [], "supplements": []})

    for ds, n in sorted(data["names"].items()):
        slot(n["workshop_id"], n["map_dir"])["names"].append((ds, n["sha"]))
    for ds, p in sorted(data["repairs"].items()):
        slot(p.workshop_id, p.map_dir)["repairs"].append((ds, p.streets_sha or None))
    for ds, s in sorted(data["supplements"].items()):
        slot(s.workshop_id, s.map_dir)["supplements"].append(
            (ds, s.streets_sha, s.upstream_count, s.worldmap_sha))
    return idx


# ============================================================
# 判定（作者現況 vs 本包 pin／上次狀態）
# ============================================================
ACTION = "action"  # 需要人處理（issue 的 🛣️ 行，關閉前累積保留）
INFO = "info"      # 純資訊（本包沒資料的地圖作者移除道路，清單自動更新即可）


def judge(wid: str, old_maps: dict | None, new_maps: dict, pins: dict,
          registered: set[str]) -> list[dict]:
    """單一 workshop item 的道路判定。
    ACTION：本包 pin（街名翻譯／道路修正／補充道路）記的 sha 與作者現況不符；或本包沒有
            道路資料的註冊地圖，作者新增／變更了 streets.xml（路名沒人翻，中日文介面顯示英文，
            要有人決定補不補）。
    INFO  ：本包沒有道路資料的註冊地圖，作者移除了 streets.xml（沒有東西要翻）。
    old_maps 為 None＝沒有上次紀錄，無從比較，後兩類都不出。"""
    dirs = set(new_maps) | set(old_maps or {}) | {d for (w, d) in pins if w == wid}
    out: list[dict] = []
    for d in sorted(dirs):
        cur = new_maps.get(d) or {}
        sha, count = cur.get("streets_sha256"), int(cur.get("street_count") or 0)
        wm = cur.get("worldmap_sha256")
        p = pins.get((wid, d)) or {}
        base = {"map_dir": d, "street_count": count, "has_streets": sha is not None}
        for ds, pin in p.get("names", []):
            if pin != sha:
                out.append({**base, "level": ACTION, "kind": "names", "dataset": ds})
        for ds, pin in p.get("repairs", []):
            if pin != sha:
                out.append({**base, "level": ACTION, "kind": "repairs", "dataset": ds})
        for ds, pin, upstream, pin_wm in p.get("supplements", []):
            if pin != sha:
                out.append({**base, "level": ACTION, "kind": "supplement_streets", "dataset": ds,
                            "pin_had_streets": pin is not None, "upstream_count": upstream})
            if pin_wm and pin_wm != wm:
                out.append({**base, "level": ACTION, "kind": "supplement_worldmap", "dataset": ds})
        if any(p.values()) or d not in registered or old_maps is None:
            continue
        old = old_maps.get(d) or {}
        old_sha = old.get("streets_sha256")
        if old_sha != sha:
            kind = "author_added" if old_sha is None else "author_removed" if sha is None \
                else "author_changed"
            out.append({**base, "level": INFO if kind == "author_removed" else ACTION, "kind": kind,
                        "old_count": int(old.get("street_count") or 0)})
    return out


def describe(f: dict, quote) -> str:
    """判定 → 一行說明（不含 `- ` 前綴）。quote 負責把上游字串（地圖目錄）包成安全的
    code span——issue 用 map_tracker.neutralize，本機輸出同一套。"""
    d, ds = quote(f["map_dir"]), f.get("dataset", "")
    kind = f["kind"]
    if kind == "names":
        return (f"🛣️ **街名翻譯需補譯**：{d}（`street-names/{ds}`）作者 streets.xml 已變"
                f"（現 {f['street_count']} 條）→ `uv run scripts/gen_streets_i18n.py verify` "
                "會列出還沒翻的原名；補譯 names.json（刻意不翻列進 skip_names）後 "
                "`uv run scripts/gen_streets_i18n.py gen --update-hash`，verify 通過才算處理完")
    if kind == "repairs":
        return (f"🛣️ **道路修正需覆核**：{d}（`road-repairs/{ds}.json`）作者 streets.xml 已變，"
                "對不上的修正遊戲內會自動略過 → `uv run scripts/gen_street_repairs.py verify` "
                "看哪幾筆失效，覆核後更新 pin 再 `uv run scripts/gen_street_repairs.py gen`")
    if kind == "supplement_streets":
        verb = "變更" if f["pin_had_streets"] else "新增"
        if f["street_count"] != f["upstream_count"]:
            effect = "街道數不同，遊戲內已自動停用補充道路"
        else:
            effect = "街道數相同，遊戲內**不會**自動停用，須人工處理"
        return (f"🛣️ **補充道路評估退場**：{d}（`road-supplements/{ds}.json`）作者{verb}了"
                f"道路資料（現 {f['street_count']} 條，pin 記 {f['upstream_count']} 條）；{effect} → "
                "`uv run scripts/gen_road_supplements.py verify`，評估改用作者資料並移除補充道路")
    if kind == "supplement_worldmap":
        return (f"🛣️ **補充道路推導來源已變**：{d}（`road-supplements/{ds}.json`）worldmap.xml 已變 → "
                f"重跑 `uv run scripts/derive_road_supplements.py {ds} --preview output/{ds}-roads.png`"
                " 看疊圖，確認後加 `--write`（沿用號碼），再 "
                "`uv run scripts/gen_road_supplements.py gen` 與 `verify`")
    if kind == "author_removed":
        return (f"ℹ️ 作者移除道路資料（原 {f['old_count']} 條）：{d}"
                "（本包沒有此圖的道路資料；公開清單已自動更新）")
    what = (f"新增道路資料（{f['street_count']} 條）" if kind == "author_added"
            else f"變更道路資料（{f['old_count']} → {f['street_count']} 條）")
    return (f"🛣️ **路名沒有翻譯，評估補譯**：{d} 作者{what}，本包沒有這張圖的路名翻譯，"
            "中文／日文介面會顯示英文 → 作者自己取的路名就建 `street-names/<dataset>/names.json`"
            "並在註冊清單加 `streetNames`，再 `uv run scripts/gen_streets_i18n.py gen`；"
            "只是照抄官方路網可不翻。處理完跑 `road-scan --write`")


# ============================================================
# 註冊清單與顯示名稱
# ============================================================
def _ref(chunk: str, key: str) -> str | None:
    m = re.search(rf'\b{key}\s*=\s*[\w.]+\s*\[\s*"([^"]+)"\s*\]', chunk)
    return m[1] if m else None


def registry_maps(root: Path) -> list[dict]:
    """註冊清單 → 依 zip 去重（互斥變體 alias 合併）的地圖列，順序同註冊清單：
    {zip, name_key, names, repairs, supplement}（後三者＝引用的 dataset 或 None）。"""
    text = re.sub(r"--[^\n]*", "", (root / gsi.REGISTRY_REL).read_text(encoding="utf-8"))
    starts = [m.start() for m in _ENTRY_RE.finditer(text)]
    rows: dict[str, dict] = {}
    for a, b in zip(starts, starts[1:] + [len(text)]):
        chunk = text[a:b]
        zip_name = re.search(r'zip\s*=\s*"([^"]+)"', chunk)[1]
        key = re.search(r'nameKey\s*=\s*"([^"]+)"', chunk)
        row = rows.setdefault(zip_name, {"zip": zip_name, "name_key": key[1] if key else None,
                                         "names": None, "repairs": None, "supplement": None})
        for field, lua_key in (("names", "streetNames"), ("repairs", "streetRepairs"),
                               ("supplement", "streetSupplement")):
            row[field] = row[field] or _ref(chunk, lua_key)
    return list(rows.values())


def _ui(root: Path, lang: str) -> dict:
    return json.loads((root / gsi.TRANSLATE_REL / lang / "UI.json").read_text(encoding="utf-8-sig"))


# ============================================================
# 公開清單 docs/road-data.md
# ============================================================
_KIND_TEXT = {
    gsr.KIND_RECT: ("輪廓道路改中心線 {n} 條", "作者把路畫成外框，路名會上下各顯示一次；改成中心線後顯示與導航都正常"),
    gsr.KIND_BRIDGE: ("斷點接線 {n} 處", "作者的路停在路口前，導航／自動駕駛到不了；接回路網後可以走"),
    gsr.KIND_DROP: ("移除內部轉折點 {n} 處", "作者的路在路口旁有個轉折點，導航會把它拉到隔壁路上而偏離路面；拿掉這一點後沿實際路面走"),
    gsr.KIND_HIDE: ("重複路名隱藏 {n} 筆", "與官方地圖逐點相同的複本，只藏玩家地圖上重疊的路名，導航不受影響"),
}


def _cell(s: str) -> str:
    return s.replace("|", "\\|")


def _repair_counts(pins) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for op in pins.ops:
        k = gsr.classify_op(op)
        counts[k] = counts.get(k, 0) + 1
    return [(k, counts[k]) for k in _KIND_TEXT if k in counts]


def _supplement_note(sup, author: dict | None) -> str:
    """補充道路相對作者現況的狀態（執行期規則：作者街道數 ≠ pin 記的數目就整份停用）。"""
    if author is None or author.get("streets_sha256") == sup.streets_sha:
        return ""
    if int(author.get("street_count") or 0) != sup.upstream_count:
        return "作者已提供道路資料，遊戲內自動停用"
    return "作者道路資料已變更，待本包覆核"


def render_doc(root: Path, status: dict) -> str:
    """公開清單全文。只依資料決定（無時間戳）：資料沒變，位元組就不變。"""
    data, _errors = load_road_data(root)
    ui_ch, ui_en = _ui(root, "CH"), _ui(root, "EN")
    maps = registry_maps(root)
    entries, items = status.get("entries", {}), status.get("items", {})

    rows, fixed = [], []
    n_yes = n_no = n_unknown = n_names = n_repairs = n_sup = 0
    for m in maps:
        ch = ui_ch.get(m["name_key"] or "") or m["zip"].removesuffix(".pyramid.zip")
        en = ui_en.get(m["name_key"] or "") or ch
        title = ch if ch == en else f"{ch}<br>{en}"
        entry = entries.get(m["zip"]) or {}
        wid = str(entry.get("workshop_id") or "")
        author = ((items.get(wid) or {}).get("maps") or {}).get(entry.get("map_dir") or "")
        link = (f"[{wid}](https://steamcommunity.com/sharedfiles/filedetails/?id={wid})"
                if wid.isdigit() else "❔")
        if author is None:
            n_unknown += 1
            roads = "❔ 未確認"
        elif int(author.get("street_count") or 0):
            n_yes += 1
            roads = f"✅ {author['street_count']} 條"
        else:  # 沒有 streets.xml，或檔案裡沒有任何街道（有作者附空檔）
            n_no += 1
            roads = "❌ 無"
        names = data["names"].get(m["names"] or "")
        if names:
            n_names += 1
        pins = data["repairs"].get(m["repairs"] or "")
        counts = _repair_counts(pins) if pins else []
        if counts:
            n_repairs += 1
        sup = data["supplements"].get(m["supplement"] or "")
        sup_cell = "—"
        bullets = [_KIND_TEXT[k][0].format(n=n) + f"：{_KIND_TEXT[k][1]}" for k, n in counts]
        if sup:
            n_sup += 1
            note = _supplement_note(sup, author)
            sup_cell = f"✅ {len(sup.roads)} 條" + (f"（{note}）" if note else "")
            first, last = sup.roads[0].no, sup.roads[-1].no

            def span(lang: str) -> str:
                if first == last:
                    return f"`{grs.road_name(sup.label, first, lang)}`"
                return (f"`{grs.road_name(sup.label, first, lang)}`～"
                        f"`{grs.road_name(sup.label, last, lang)}`")

            bullets.append(f"補充道路 {len(sup.roads)} 條：作者沒放進道路資料的路由本包補上，"
                           f"路名 {span('ch')}（英文 {span('en')}）；作者日後提供道路資料時，"
                           "遊戲內自動改用作者的")
            if note:
                bullets.append(f"⚠️ {note}")
        if bullets:
            fixed.append((f"{ch}（{en}）" if ch != en else ch, bullets))
        names_cell = f"✅ {names['count']} 條" if names else "—"
        fixes_cell = "、".join(_KIND_TEXT[k][0].format(n=n) for k, n in counts) or "—"
        rows.append(f"| {_cell(title)} | {link} | {roads} | {names_cell} | {fixes_cell} | {sup_cell} |")

    out = [
        "<!-- 生成檔，請勿手改。重新生成：" + DOC_COMMAND + "（每日追蹤器也會在作者更新後自動更新） -->",
        "",
        "# 道路資料清單（Road data）",
        "",
        "地圖作者會在地圖 MOD 內附上道路資料（`streets.xml`）。小地圖的這些功能都靠它：",
        "",
        "- 地圖上的**路名**顯示與滑鼠移上去的**路名提示**",
        "- **路名搜尋**",
        "- **導航**與**自動駕駛**的路網",
        "",
        "作者沒附道路資料的地圖，圖像照常顯示，但該區域沒有路名、搜不到路，也無法導航。"
        "這不是本包漏做翻譯；本包會視情況補上道路資料（見下方「本包補過道路資料的地圖」）。",
        "",
        "## 圖例（Legend）",
        "",
        "| 標示 | 意思 |",
        "|------|------|",
        "| ✅ N 條 | 作者附有道路資料，共 N 條街（Author provides N streets） |",
        "| ❌ 無 | 作者沒有附道路資料（No road data from the author） |",
        "| ❔ 未確認 | 尚未取得作者目前版本的資料（Not checked yet） |",
        "| — | 本包沒有這項資料（None） |",
        "",
        "- **路名翻譯**：作者原本的英文路名，本包提供繁中／簡中／日文翻譯（英文與其他語言維持原名）。",
        "- **本包修正**：作者道路資料有問題的地方，本包另外修正；作者改版後對不上的修正會自動略過。",
        "- **本包補充道路**：作者沒放進道路資料的路，本包補上並標明「小地圖補」；"
        "作者日後提供道路資料時自動停用。",
        "",
        "## 統計（Summary）",
        "",
        f"- 收錄地圖（Maps）：**{len(maps)}** 張",
        f"- 作者附道路資料（Author road data）：**{n_yes}** 張；沒有 **{n_no}** 張"
        + (f"；未確認 **{n_unknown}** 張" if n_unknown else ""),
        f"- 本包路名翻譯（Translated names）：**{n_names}** 張",
        f"- 本包道路修正（Fixes）：**{n_repairs}** 張",
        f"- 本包補充道路（Added roads）：**{n_sup}** 張",
        "",
        "## 本包補過道路資料的地圖（Maps we fixed or extended）",
        "",
    ]
    if fixed:
        for title, bullets in fixed:
            out.append(f"- **{title}**")
            out += [f"  - {b}" for b in bullets]
    else:
        out.append("（目前沒有）")
    out += [
        "",
        "## 全部地圖（All maps）",
        "",
        "| 地圖 Map | Workshop | 作者道路資料<br>Author roads | 路名翻譯<br>Translated names "
        "| 本包修正<br>Fixes | 本包補充道路<br>Added roads |",
        "|---|---|---|---|---|---|",
        *rows,
        "",
    ]
    return "\n".join(out)


def verify(root: Path) -> list[str]:
    """發版閘門：狀態檔涵蓋每個註冊 zip、公開清單與 render 逐位元組一致。"""
    status, err = load_status(root / STATUS_REL)
    if err:
        return [err]
    problems = []
    missing = [m["zip"] for m in registry_maps(root) if m["zip"] not in status["entries"]]
    if missing:
        problems.append(f"{STATUS_REL.as_posix()} 缺 {len(missing)} 張註冊地圖："
                        + "、".join(missing) + f" → 跑 `{DOC_COMMAND}`")
    _data, errors = load_road_data(root)
    problems += errors
    doc = root / DOC_REL
    want = render_doc(root, status).encode("utf-8")
    if not doc.is_file() or doc.read_bytes() != want:
        problems.append(f"{DOC_REL.as_posix()} 與資料不同步 → 跑 `{DOC_COMMAND}`")
    return problems
