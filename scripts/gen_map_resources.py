#!/usr/bin/env python3
"""地圖包資源點（POI）與停車場生成器：每張註冊地圖的資源點、停車場、300 格擁有清單與房名別名。

主 MOD 的資源點與停車場只烘了原版地圖；地圖 MOD 的建築與停車場由本檔離線烘好，經主 MOD 的
`MinidoracatMiniMapResourceAPI.registerMapResources`（resourceApiVersion 2 起讀 poi，3 起另讀 parking）
交給主 MOD。分類與判定規則**只有一份**：直接匯入主 MOD `scripts/gen_poi_data.py`（類別房名、優先序、
住宅門檻、附屬房 10%、整棟合併、cells300 規則都在那裡）與 `scripts/gen_parking_data.py`（停車場），
本檔不複製任何規則。

## 資料流

1. `pzmap poi --maps-dir <地圖目錄>` → 該圖全部建築與房間（同主 MOD poi_raw.json 格式）。
2. 房名審查：不在類別房名、也不在原版房名（主 MOD poi_raw.json）的自訂房名，若在該地圖
   MOD 自己的 Lua 裡以整個字出現（＝作者替它寫了 loot 表），就必須在 `room-aliases.json`
   該 zip 底下審過：`aliases`（改名成某個類別房名後再分類）或 `ignored`（不算資源點）。
   沒有 loot 表的自訂房名自動略過、不必審。有沒審過的名字 → bake 整批不寫檔、exit 1。
3. 套別名 → `gen_poi_data.build_entries`；停車場 → `gen_parking_data.bake(use_roads=False)`（地圖 MOD 的
   worldmap.xml 把停車場也畫成道路，不做貼路排除）→ `map-resources/<zip 主檔名>.json`（進版控的
   唯一來源：zip、mapDir、rawRecords、cells300、aliases、entries、parking）。
4. `render` 從全部 json＋註冊清單產生 shared
   `MinidoracatMiniMapModMapsResources.lua`（每個註冊條目 zip＋mapMod 一次註冊）。

## 用法

    uv run scripts/gen_map_resources.py bake [--only 子字串] [--prefer 根 ...]
    uv run scripts/gen_map_resources.py candidates [--only] [--prefer] --out temp/room-review/candidates.json
    uv run scripts/gen_map_resources.py parking [--only] [--prefer]   # 只重算停車場，資源點不動
    uv run scripts/gen_map_resources.py render      # map-resources/*.json → Lua
    uv run scripts/gen_map_resources.py check       # 離線閘門（不需 Workshop 副本）
    uv run scripts/gen_map_resources.py --selftest  # 合成資料自我測試
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_streets_i18n as gsi  # noqa: E402  只取純 helper：_lua_str、write_bytes_atomic、路徑常數
import rebuild_pyramids as rp  # noqa: E402  註冊表解析、workshop 索引、地圖目錄定位共用同一套

PROJECT_ROOT = gsi.PROJECT_ROOT
OWNER_MOD_ID = gsi.OWNER_MOD_ID
MAIN_SCRIPTS = PROJECT_ROOT.parent / "MinidoracatMiniMapFor42" / "scripts"
RES_DIR_NAME = "map-resources"
ALIASES_NAME = "room-aliases.json"
LUA_REL = gsi.STREET_TABLE_REL.with_name("MinidoracatMiniMapModMapsResources.lua")
POI_TEMP = PROJECT_ROOT / "temp" / "map-resources"
RESOURCE_API_VERSION = 2
CONTEXT_CHARS = 1500  # candidates 每個名字給審查者看的 Lua 片段上限
CONTEXT_LINES = 10
MAX_FILES = 5


def _main_module(name: str):
    """主 MOD scripts/ 的模組（規則唯一來源，不複製）。"""
    if str(MAIN_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MAIN_SCRIPTS))
    try:
        return __import__(name)
    except ImportError as error:
        raise SystemExit(f"❌ 匯入主 MOD {MAIN_SCRIPTS / (name + '.py')} 失敗：{error}")


def _poi():
    """主 MOD 的分類規則模組（唯一來源，不複製）。"""
    return _main_module("gen_poi_data")


def _parking():
    """主 MOD 的停車場判定模組（唯一來源，不複製）。"""
    return _main_module("gen_parking_data")


def category_rooms(poi) -> frozenset[str]:
    return frozenset().union(*(rooms for _, rooms in poi.parse_categories(poi.DEFAULT_CATEGORIES_LUA)))


def vanilla_rooms(poi) -> frozenset[str]:
    raw = json.loads(poi.DEFAULT_RAW.read_text(encoding="utf-8"))
    return frozenset(r["name"] for b in raw for r in b.get("rooms") or () if r.get("name"))


def stem(zip_name: str) -> str:
    return zip_name.removesuffix(".pyramid.zip")


# ============================================================
# 純函式（selftest 涵蓋）
# ============================================================
def loot_files(name: str, lua_texts: dict[str, str]) -> list[str]:
    """名字以整個字出現的 Lua 檔（相對路徑），loot 表檔優先。"""
    pat = re.compile(rf"(?<![\w]){re.escape(name)}(?![\w])")
    hits = [rel for rel, text in lua_texts.items() if name in text and pat.search(text)]
    return sorted(hits, key=lambda rel: (_loot_rank(rel, lua_texts[rel]), rel))


def _loot_rank(rel: str, text: str) -> int:
    if "distribut" in rel.lower():
        return 0
    return 1 if "Distribution" in text else 2


def room_counts(raw: list[dict]) -> dict[str, tuple[int, int]]:
    """房名 → (房間數, 含它的紀錄數)。"""
    rooms: dict[str, int] = {}
    records: dict[str, int] = {}
    for b in raw:
        names = [r["name"] for r in b.get("rooms") or () if r.get("name")]
        for n in names:
            rooms[n] = rooms.get(n, 0) + 1
        for n in set(names):
            records[n] = records.get(n, 0) + 1
    return {n: (rooms[n], records[n]) for n in rooms}


def unreviewed(raw: list[dict], lua_texts: dict[str, str], review: dict,
               cat_rooms: frozenset[str], van_rooms: frozenset[str]) -> list[tuple[str, int, int, list[str]]]:
    """沒審過的 loot 房名：[(name, rooms, records, files)]，依名字排序。"""
    reviewed = set(review.get("aliases", {})) | set(review.get("ignored", []))
    out = []
    for name, (n_rooms, n_records) in sorted(room_counts(raw).items()):
        if name in cat_rooms or name in van_rooms or name in reviewed:
            continue
        files = loot_files(name, lua_texts)
        if files:
            out.append((name, n_rooms, n_records, files))
    return out


def apply_aliases(raw: list[dict], aliases: dict[str, str]) -> list[dict]:
    """房名換成別名目標（新物件，不改輸入）。"""
    return [{**b, "rooms": [{**r, "name": aliases.get(r.get("name"), r.get("name"))}
                            for r in b.get("rooms") or ()]} for b in raw]


def validate_aliases(doc: object, registry_zips: set[str], cat_rooms: frozenset[str]) -> list[str]:
    if not isinstance(doc, dict):
        return [f"{ALIASES_NAME} 頂層必須是物件"]
    errors = []
    for zip_name, item in sorted(doc.items()):
        where = f"{ALIASES_NAME} [{zip_name}]"
        if zip_name not in registry_zips:
            errors.append(f"{where} 不是註冊清單裡的 zip")
        if not isinstance(item, dict):
            errors.append(f"{where} 必須是物件")
            continue
        extra = set(item) - {"aliases", "ignored"}
        if extra:
            errors.append(f"{where} 未知欄位：{', '.join(sorted(extra))}")
        aliases = item.get("aliases", {})
        ignored = item.get("ignored", [])
        if not isinstance(ignored, list) or not all(isinstance(x, str) for x in ignored):
            errors.append(f"{where}.ignored 必須是字串陣列")
            ignored = []
        if not isinstance(aliases, dict):
            errors.append(f"{where}.aliases 必須是物件")
            continue
        for key, target in sorted(aliases.items()):
            if not isinstance(target, str) or target not in cat_rooms:
                errors.append(f"{where}.aliases[{key!r}] 的目標 {target!r} 不是類別房名")
            if key in cat_rooms:
                errors.append(f"{where}.aliases[{key!r}] 本身就是類別房名，不需要別名")
            if key in ignored:
                errors.append(f"{where} {key!r} 同時在 aliases 與 ignored")
    return errors


def plan_bake(scans: list[dict], aliases_doc: dict, cat_rooms: frozenset[str],
              van_rooms: frozenset[str], build_entries, categories) -> tuple[dict, dict]:
    """→ (blocked {zip: unreviewed}, docs {zip: doc})；blocked 非空時 docs 為空（整批不寫）。"""
    blocked = {}
    for s in scans:
        left = unreviewed(s["raw"], s["lua"], aliases_doc.get(s["zip"], {}), cat_rooms, van_rooms)
        if left:
            blocked[s["zip"]] = left
    if blocked:
        return blocked, {}
    docs = {}
    for s in scans:
        aliases = dict(sorted(aliases_doc.get(s["zip"], {}).get("aliases", {}).items()))
        entries, _stats, _dup = build_entries(apply_aliases(s["raw"], aliases), categories)
        docs[s["zip"]] = {
            "zip": s["zip"], "mapDir": s["mapDir"], "rawRecords": len(s["raw"]),
            "cells300": [list(c) for c in s["cells300"]], "aliases": aliases,
            "entries": [{"cat": e["cat"], "rects": [list(r) for r in e["rects"]],
                         "bbox": list(e["bbox"]) if e["bbox"] else None,
                         "underground": bool(e["underground"])} for e in entries],
            "parking": parking_rows(s.get("parking", [])),
        }
    return {}, docs


def parking_rows(areas: list[dict]) -> list[dict]:
    """主 MOD gen_parking_data.bake 的停車區 → json 列（rects、box、icon＝這區帶整座停車場的 P）。"""
    return [{"rects": [list(r) for r in a["rects"]], "box": list(a["box"]), "icon": bool(a.get("icon"))}
            for a in areas]


def dump_resource(doc: dict) -> str:
    """確定性 JSON：一筆 entry／一區停車場一行，diff 看得懂。"""
    dump = lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True)  # noqa: E731
    lines = ["{"]
    for key in ("zip", "mapDir", "rawRecords", "aliases", "cells300"):
        lines.append(f"  {dump(key)}: {dump(doc[key])},")

    def rows(key: str) -> str:
        items = [f"    {json.dumps(x, ensure_ascii=False, separators=(', ', ': '))}" for x in doc.get(key, [])]
        return f'  "{key}": [' + ("\n" + ",\n".join(items) + "\n  ]" if items else "]")

    lines.append(rows("entries") + ",")
    lines.append(rows("parking"))
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_lua(entries: list[dict], resources: dict[str, dict], render_entry,
               render_parking=None) -> tuple[str, list[str]]:
    """註冊條目＋各 zip 的 json → (Lua 文字, 沒有 json 而略過的 zip)。"""
    s = gsi._lua_str
    regs = sorted({(e["zip"], e["mapMod"]): e for e in entries}.values(),
                  key=lambda e: (e["zip"], e["mapMod"]))
    body, skipped = [], []
    for e in regs:
        doc = resources.get(e["zip"])
        if doc is None:
            skipped.append(e["zip"])
            continue
        flat = [n for c in doc["cells300"] for n in c]
        body += ["", f"R.registerMapResources({s(OWNER_MOD_ID)}, {{",
                 f"    mapMod = {s(e['mapMod'])}, mapDir = {s(e['mapDir'] or doc['mapDir'])},",
                 "    cells300 = {"]
        body += ["        " + ", ".join(map(str, flat[i:i + 32])) + "," for i in range(0, len(flat), 32)]
        body += ["    },", "    poi = {"]
        body += [f"        {render_entry(x)}," for x in doc["entries"]]
        body += [f"        count = {len(doc['entries'])},", "    },"]
        if doc.get("parking"):
            body.append("    parking = {")
            body += [f"        {render_parking(x)}," for x in doc["parking"]]
            body += [f"        count = {len(doc['parking'])},", "    },"]
        if doc["aliases"]:
            body.append("    aliases = {")
            body += [f"        [{s(k)}] = {s(v)}," for k, v in sorted(doc["aliases"].items())]
            body.append("    },")
        body.append("})")
    head = [
        f"-- {LUA_REL.name}（生成檔，勿手編）",
        f"-- 由 scripts/gen_map_resources.py render 從 {RES_DIR_NAME}/*.json＋註冊清單產生；",
        f"-- 資料用 bake 重烘，房名別名改 {ALIASES_NAME}。分類規則在主 MOD scripts/gen_poi_data.py，",
        "-- 停車場判定在主 MOD scripts/gen_parking_data.py（只重算停車場用 parking 子命令）。",
        f"-- {len(regs) - len(skipped)} 個註冊（zip＋mapMod）；poi 條目格式同 MinidoracatMiniMapPOIData，",
        "-- parking 條目格式同 MinidoracatMiniMapParkingData（resourceApiVersion 3 起才讀，舊版主 MOD 不讀）。",
        "",
        "local R = MinidoracatMiniMapResourceAPI",
        "if not (R and type(R.registerMapResources) == \"function\"",
        f"        and (tonumber(R.resourceApiVersion) or 0) >= {RESOURCE_API_VERSION}) then",
        f"    print(\"[MinidoracatMiniMapModMaps] MiniMap resourceApiVersion < {RESOURCE_API_VERSION};"
        " map resource points off\")",
        "    return",
        "end",
    ]
    return "\n".join(head + body) + "\n", skipped


# ============================================================
# 檔案層
# ============================================================
def load_registry(root: Path) -> list[dict]:
    return rp.parse_registrations((root / gsi.REGISTRY_REL).read_text(encoding="utf-8"))


def load_aliases(root: Path) -> dict:
    return json.loads((root / ALIASES_NAME).read_text(encoding="utf-8"))


def load_resources(root: Path) -> dict[str, dict]:
    docs = {}
    for p in sorted((root / RES_DIR_NAME).glob("*.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        docs[doc["zip"]] = doc
    return docs


def render(root: Path, render_entry) -> tuple[bytes, list[str]]:
    text, skipped = render_lua(load_registry(root), load_resources(root), render_entry, _parking().render_entry)
    return text.encode("utf-8"), skipped


def check(root: Path, poi) -> list[str]:
    registry = load_registry(root)
    zips = {e["zip"] for e in registry}
    try:
        aliases_doc = load_aliases(root)
    except (OSError, ValueError) as error:
        return [f"{ALIASES_NAME} 讀取失敗：{error}"]
    errors = validate_aliases(aliases_doc, zips, category_rooms(poi))
    if not isinstance(aliases_doc, dict):
        return errors
    for p in sorted((root / RES_DIR_NAME).glob("*.json")):
        rel = f"{RES_DIR_NAME}/{p.name}"
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
            zip_name, applied = doc["zip"], doc["aliases"]
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append(f"{rel} 讀取失敗：{error}")
            continue
        if zip_name not in zips or p.stem != stem(zip_name):
            errors.append(f"{rel} 對不到註冊清單的 zip（zip={zip_name!r}）")
        want = (aliases_doc.get(zip_name) or {}).get("aliases", {})
        if applied != want:
            errors.append(f'{rel} 烘焙時的別名與 {ALIASES_NAME} 不同，重跑 bake --only "{stem(zip_name)}"')
    if errors:
        return errors
    lua = root / LUA_REL
    data, skipped = render(root, poi.render_entry)
    # 註冊了卻沒有資源點資料＝玩家選「依主要用途」時這張圖沒有資源點：新增地圖忘了 bake 要在這裡擋下
    errors += [f'{z} 在註冊清單裡但沒有 {RES_DIR_NAME} 資料，跑 bake --only "{stem(z)}"' for z in dict.fromkeys(skipped)]
    if not lua.is_file() or lua.read_bytes() != data:
        errors.append(f"{LUA_REL.as_posix()} 與 render 結果不同，重跑 render")
    return errors


def map_dir_path(mod_root: Path, name: str) -> Path | None:
    """B42 優先序：版本資料夾（新→舊）、common、mod 根；取第一個有 lotheader 的。"""
    subs = [p for p in mod_root.iterdir() if p.is_dir()]
    versions = sorted((p for p in subs if rp.VERSION_DIR.match(p.name)),
                      key=lambda p: tuple(int(x) for x in p.name.split(".")), reverse=True)
    common = [p for p in subs if p.name.lower() == "common"]
    for base in (*versions, *common, mod_root):
        d = base / "media" / "maps" / name
        if d.is_dir() and any(d.glob("*.lotheader")):
            return d
    return None


def locate(entries: list[dict], only: str, prefer: list[str]) -> tuple[list[dict], list[str]]:
    """選到的 zip → [{zip, entry, root, mapDir, path}]；本機找不到的 zip 另列。"""
    idx, _req = rp.index_workshop([Path(p) for p in prefer])
    found, missing = [], []
    for zip_name in dict.fromkeys(e["zip"] for e in entries):
        if only and only.lower() not in zip_name.lower():
            continue
        hit = None
        # alias 條目（互斥變體共用同 zip）：依序換用同 zip 其他 mapMod，同 rebuild_pyramids
        for e in (x for x in entries if x["zip"] == zip_name):
            root = idx.get(e["mapMod"])
            name = rp.find_map_dir(root, e["mapDir"], stem(zip_name), e["mapMod"]) if root else None
            path = map_dir_path(root, name) if name else None
            if path:
                hit = {"zip": zip_name, "entry": e, "root": root, "mapDir": name, "path": path}
                break
        if hit:
            found.append(hit)
        else:
            missing.append(zip_name)
    return found, missing


_lua_cache: dict[Path, dict[str, str]] = {}


def mod_lua_texts(mod_root: Path) -> dict[str, str]:
    if mod_root not in _lua_cache:
        _lua_cache[mod_root] = {p.relative_to(mod_root).as_posix(): p.read_text(encoding="utf-8", errors="replace")
                                for p in sorted(mod_root.rglob("*.lua"))}
    return _lua_cache[mod_root]


def scan(hit: dict, poi) -> dict:
    POI_TEMP.mkdir(parents=True, exist_ok=True)
    out = POI_TEMP / f"{stem(hit['zip'])}.poi.json"
    r = subprocess.run([str(rp.PZMAP), "poi", "--maps-dir", str(hit["path"]), "--out", str(out)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"❌ pzmap poi 失敗（{hit['zip']}）：{(r.stderr or r.stdout).strip()[-300:]}")
    return {**hit, "raw": json.loads(out.read_text(encoding="utf-8")),
            "lua": mod_lua_texts(hit["root"]), "cells300": poi.cells300(hit["path"]),
            # 地圖 MOD 的 worldmap.xml 把停車場也畫成道路，不做貼路排除（見主 MOD gen_parking_data.py 檔頭）
            "parking": _parking().bake(hit["path"], rp.PZMAP, use_roads=False)[0]}


def _scan_selected(args, poi) -> tuple[list[dict], list[str]]:
    hits, missing = locate(load_registry(PROJECT_ROOT), args.only, args.prefer)
    if not hits and not missing:
        raise SystemExit(f"❌ 沒有 zip 名含 {args.only!r} 的註冊條目")
    scans = []
    for i, hit in enumerate(hits, 1):
        print(f"[{i}/{len(hits)}] {hit['zip']} ← {hit['path']}", flush=True)
        scans.append(scan(hit, poi))
    return scans, missing


def _print_missing(missing: list[str]) -> None:
    if missing:
        print(f"⚠️ {len(missing)} 張在本機找不到地圖 MOD 或含 lotheader 的地圖目錄（略過）：")
        for z in missing:
            print(f"     {z}")


def _write_lua(poi) -> None:
    data, skipped = render(PROJECT_ROOT, poi.render_entry)
    gsi.write_bytes_atomic(PROJECT_ROOT / LUA_REL, data)
    print(f"✅ {LUA_REL.as_posix()}（{len(load_resources(PROJECT_ROOT))} 份資料；"
          f"{len(skipped)} 個註冊條目還沒有 {RES_DIR_NAME} 資料，略過）")


def cmd_bake(args) -> int:
    poi = _poi()
    registry = load_registry(PROJECT_ROOT)
    cats = poi.parse_categories(poi.DEFAULT_CATEGORIES_LUA)
    cat_rooms = frozenset().union(*(r for _, r in cats))
    aliases_doc = load_aliases(PROJECT_ROOT)
    errors = validate_aliases(aliases_doc, {e["zip"] for e in registry}, cat_rooms)
    if errors:
        print("\n".join(f"  ❌ {e}" for e in errors))
        return 1
    scans, missing = _scan_selected(args, poi)
    blocked, docs = plan_bake(scans, aliases_doc, cat_rooms, vanilla_rooms(poi), poi.build_entries, cats)
    _print_missing(missing)
    if blocked:
        print(f"❌ {len(blocked)} 張地圖有沒審過的 loot 房名，整批不寫檔。每個名字在 {ALIASES_NAME} "
              "該 zip 底下加進 aliases（目標＝類別房名）或 ignored 後重跑：")
        for zip_name, left in sorted(blocked.items()):
            print(f"  {zip_name}")
            for name, n_rooms, n_records, files in left:
                print(f"     {name}（{n_rooms} 間／{n_records} 筆）← {', '.join(files[:MAX_FILES])}")
        return 1
    for zip_name, doc in sorted(docs.items()):
        gsi.write_bytes_atomic(PROJECT_ROOT / RES_DIR_NAME / f"{stem(zip_name)}.json",
                               dump_resource(doc).encode("utf-8"))
        print(f"   {zip_name:48s} {len(doc['entries']):5d} 個資源點／{len(doc['parking']):4d} 區停車場"
              f"／{len(doc['cells300']):3d} 格")
    _write_lua(poi)
    return 1 if missing else 0


def cmd_parking(args) -> int:
    """只重算停車場：選到的地圖跑主 MOD gen_parking_data.bake，寫回既有 json 的 parking，資源點不動。"""
    parking = _parking()
    hits, missing = locate(load_registry(PROJECT_ROOT), args.only, args.prefer)
    if not hits and not missing:
        raise SystemExit(f"❌ 沒有 zip 名含 {args.only!r} 的註冊條目")
    docs = load_resources(PROJECT_ROOT)
    no_doc = []
    for i, hit in enumerate(hits, 1):
        doc = docs.get(hit["zip"])
        if doc is None:
            no_doc.append(hit["zip"])
            continue
        areas, stats = parking.bake(hit["path"], rp.PZMAP, use_roads=False)
        doc["parking"] = parking_rows(areas)
        gsi.write_bytes_atomic(PROJECT_ROOT / RES_DIR_NAME / f"{stem(hit['zip'])}.json",
                               dump_resource(doc).encode("utf-8"))
        print(f"[{i}/{len(hits)}] {hit['zip']:48s} {stats['kept']:4d} 區停車場"
              f"（車位區 {stats['stalls']}、能停 2 台以上 {stats['areas']}、排除草地 {stats['grass']}）", flush=True)
    _print_missing(missing)
    if no_doc:
        print(f"⚠️ {len(no_doc)} 張還沒有 {RES_DIR_NAME} 資料，先跑 bake：{', '.join(no_doc)}")
    _write_lua(_poi())
    return 1 if missing or no_doc else 0


def lua_context(name: str, files: list[str], lua_texts: dict[str, str]) -> str:
    pat = re.compile(rf"(?<![\w]){re.escape(name)}(?![\w])")
    parts, used = [], 0
    for rel in files:  # loot 表檔排前；每檔只取第一處，留空間給其他檔
        if used >= CONTEXT_CHARS:
            break
        lines = lua_texts[rel].splitlines()
        i = next((n for n, line in enumerate(lines) if pat.search(line)), None)
        if i is None:
            continue
        chunk = f"-- {rel}:{i + 1}\n" + "\n".join(lines[max(0, i - CONTEXT_LINES):i + CONTEXT_LINES + 1])
        parts.append(chunk)
        used += len(chunk) + 1
    return "\n".join(parts)[:CONTEXT_CHARS]


def cmd_candidates(args) -> int:
    poi = _poi()
    cat_rooms = category_rooms(poi)
    van_rooms = vanilla_rooms(poi)
    aliases_doc = load_aliases(PROJECT_ROOT)
    scans, missing = _scan_selected(args, poi)
    items = []
    for s in scans:
        for name, n_rooms, n_records, files in unreviewed(s["raw"], s["lua"], aliases_doc.get(s["zip"], {}),
                                                          cat_rooms, van_rooms):
            items.append({"zip": s["zip"], "mapDir": s["mapDir"], "mapMod": s["entry"]["mapMod"],
                          "name": name, "rooms": n_rooms, "records": n_records,
                          "files": files[:MAX_FILES], "context": lua_context(name, files, s["lua"])})
    out = Path(args.out)
    gsi.write_bytes_atomic(out, (json.dumps(items, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    _print_missing(missing)
    print(f"✅ {len(items)} 個沒審過的 loot 房名（{len({i['zip'] for i in items})} 張地圖）→ {out}")
    return 0


# ============================================================
# selftest（合成資料；分類規則用主 MOD 真模組）
# ============================================================
def _reg_text(rows: list[tuple[str, str, str | None]]) -> str:
    out = []
    for zip_name, mod, map_dir in rows:
        md = f' mapDir = "{map_dir}",' if map_dir else ""
        out.append(f'    {{ zip = "{zip_name}", mapMod = "{mod}",{md} bounds = {{ 0, 0, 256, 256 }}, nameKey = "x" }},')
    return "Maps = {\n" + "\n".join(out) + "\n}\n"


def cmd_selftest() -> int:
    poi = _poi()
    n_ok = n_all = 0

    def ok(label: str, cond: bool, detail: object = "") -> None:
        nonlocal n_ok, n_all
        n_all += 1
        n_ok += bool(cond)
        print(f"  {'✅' if cond else '❌'} {label}{'' if cond else ' ' + str(detail)}")

    texts = {"a/x.lua": 'rooms.FooRoom = {}\nlocal t = "Foo_Bar"\n', "media/Distributions.lua": '["FooRoom"] = {',
             "b.lua": "BigFooRoomX = 1\nShop2 = {}\n"}
    ok("整字比對：FooRoom 命中兩檔、loot 表檔排前", loot_files("FooRoom", texts) == ["media/Distributions.lua", "a/x.lua"],
       loot_files("FooRoom", texts))
    ok("整字比對：Foo 不吃 Foo_Bar／FooRoom", loot_files("Foo", texts) == [], loot_files("Foo", texts))
    ok("整字比對：Shop 不吃 Shop2", loot_files("Shop", texts) == [])

    cats = [("grocery", frozenset({"grocery"})), ("police", frozenset({"policestorage"}))]
    cat_rooms = frozenset({"grocery", "policestorage"})
    zips = {"A.pyramid.zip"}
    good = {"A.pyramid.zip": {"aliases": {"FooRoom": "grocery"}, "ignored": ["Junk"]}}
    ok("別名檔：合法", validate_aliases(good, zips, cat_rooms) == [], validate_aliases(good, zips, cat_rooms))
    for label, doc, needle in (
        ("未註冊 zip", {"B.pyramid.zip": {}}, "不是註冊清單"),
        ("目標不是類別房名", {"A.pyramid.zip": {"aliases": {"FooRoom": "kitchen"}}}, "不是類別房名"),
        ("鍵本身是類別房名", {"A.pyramid.zip": {"aliases": {"grocery": "grocery"}}}, "本身就是類別房名"),
        ("同時別名與忽略", {"A.pyramid.zip": {"aliases": {"FooRoom": "grocery"}, "ignored": ["FooRoom"]}}, "同時在"),
        ("ignored 不是字串陣列", {"A.pyramid.zip": {"ignored": "Junk"}}, "字串陣列"),
        ("未知欄位", {"A.pyramid.zip": {"alias": {}}}, "未知欄位"),
    ):
        errs = validate_aliases(doc, zips, cat_rooms)
        ok(f"別名檔拒收：{label}", any(needle in e for e in errs), errs)

    raw = [{"building_id": "1", "x": 10, "y": 10, "width": 10, "height": 10, "level": 0,
            "rooms": [{"name": "FooRoom", "level": 0, "rects": [[10, 10, 10, 10]]}]},
           {"building_id": "2", "x": 50, "y": 50, "width": 4, "height": 4, "level": 0,
            "rooms": [{"name": "NoLoot", "level": 0, "rects": [[50, 50, 4, 4]]},
                      {"name": "FooRoom", "level": 0, "rects": [[50, 50, 2, 2]]}]}]
    park = [{"rects": [(0, 0, 6, 5)], "box": (0, 0, 5, 4), "cap": 2, "icon": True}]  # gen_parking_data.bake 的一區
    scans = [{"zip": "A.pyramid.zip", "mapDir": "Town A", "raw": raw, "lua": texts, "cells300": [(1, 2)],
              "parking": park}]
    blocked, docs = plan_bake(scans, {}, cat_rooms, frozenset(), poi.build_entries, cats)
    ok("沒審過的 loot 房名擋下整批、不產資料",
       not docs and [x[:3] for x in blocked.get("A.pyramid.zip", [])] == [("FooRoom", 2, 2)], blocked)
    blocked, docs = plan_bake(scans, {"A.pyramid.zip": {"ignored": ["FooRoom"]}}, cat_rooms, frozenset(),
                              poi.build_entries, cats)
    ok("ignored 放行、沒有 loot 表的 NoLoot 不必審", not blocked and docs["A.pyramid.zip"]["entries"] == [], blocked)
    blocked, docs = plan_bake(scans, good, cat_rooms, frozenset(), poi.build_entries, cats)
    doc = docs.get("A.pyramid.zip", {})
    ok("別名套用後依類別分類", not blocked and [e["cat"] for e in doc.get("entries", [])] == ["grocery", "grocery"]
       and doc.get("aliases") == {"FooRoom": "grocery"} and raw[0]["rooms"][0]["name"] == "FooRoom", doc)
    ok("dump 可讀回且確定性", json.loads(dump_resource(doc)) == doc and dump_resource(doc) == dump_resource(doc))
    ok("停車區帶進 json（rects、box、icon）",
       doc.get("parking") == [{"rects": [[0, 0, 6, 5]], "box": [0, 0, 5, 4], "icon": True}], doc.get("parking"))

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        reg = root / gsi.REGISTRY_REL
        reg.parent.mkdir(parents=True)
        reg.write_text(_reg_text([("A.pyramid.zip", "ModA2", None), ("A.pyramid.zip", "ModA", None),
                                  ("hunter's_base.pyramid.zip", "Hunter'sBase", "回音河 base"),
                                  ("C.pyramid.zip", "ModC", None)]), encoding="utf-8")
        (root / ALIASES_NAME).write_text("{}", encoding="utf-8")
        (root / RES_DIR_NAME).mkdir()
        empty, skipped = render(root, poi.render_entry)
        ok("零份資料：只有守門、無註冊", b"registerMapResources(" not in empty and b"resourceApiVersion" in empty
           and len(skipped) == 4, empty)
        h_doc = {**doc, "zip": "hunter's_base.pyramid.zip", "mapDir": "x", "aliases": {}, "parking": []}
        (root / RES_DIR_NAME / "hunter's_base.json").write_text(dump_resource(h_doc), encoding="utf-8")
        (root / RES_DIR_NAME / "A.json").write_text(dump_resource({**doc, "aliases": {}}), encoding="utf-8")
        first, skipped = render(root, poi.render_entry)
        text = first.decode("utf-8")
        ok("render 確定性", first == render(root, poi.render_entry)[0])
        ok("每個 zip＋mapMod 一次註冊、依序排列、缺資料略過",
           text.count("R.registerMapResources(") == 3 and text.index('"ModA"') < text.index('"ModA2"')
           and skipped == ["C.pyramid.zip"], text)
        ok("字串跳脫：註冊 mapDir 優先、非 ASCII 走 \\ddd、純 ASCII",
           'mapMod = "Hunter\'sBase", mapDir = "\\229\\155\\158' in text
           and all(ord(c) < 128 for line in text.splitlines() if not line.startswith("--") for c in line), text)
        esc = rp.parse_registrations(_reg_text([("E.pyramid.zip", "S\\226\\128\\153 C", "D\\226\\128\\153")]))
        ok("註冊表 \\ddd 跳脫解回 Unicode（mod ID 含 ’）",
           (esc[0]["mapMod"], esc[0]["mapDir"]) == ("S\u2019 C", "D\u2019"), esc)
        ok("poi 帶 count、cells300、空別名不輸出",
           "count = 2," in text and "        1, 2," in text and "aliases" not in text.split("\nend\n", 1)[1], text)
        ok("parking 照主 MOD 格式輸出、沒有停車區的地圖不輸出",
           text.count("    parking = {") == 2 and "{ rn = 1, r = { { x = 0, y = 0, w = 6, h = 5 } }, "
           "b = { x = 0, y = 0, w = 6, h = 5 }, i = 1 }," in text
           and "parking" not in text.split("Hunter'sBase", 1)[1].split("})", 1)[0], text)
        ok("LF、無 CR", b"\r" not in first)
        (root / LUA_REL).parent.mkdir(parents=True)
        (root / LUA_REL).write_bytes(first)
        errs = check(root, poi)
        ok("check 抓到註冊了卻沒有資源點資料的地圖", errs == ['C.pyramid.zip 在註冊清單裡但沒有 '
           f'{RES_DIR_NAME} 資料，跑 bake --only "C"'], errs)
        (root / RES_DIR_NAME / "C.json").write_text(dump_resource({**doc, "zip": "C.pyramid.zip", "aliases": {}}),
                                                    encoding="utf-8")
        first, _ = render(root, poi.render_entry)
        (root / LUA_REL).write_bytes(first)
        ok("check 通過剛 render 的狀態", check(root, poi) == [], check(root, poi))
        (root / ALIASES_NAME).write_text(json.dumps({"A.pyramid.zip": {"aliases": {"FooRoom": "grocery"}}}),
                                         encoding="utf-8")
        errs = check(root, poi)
        ok("check 抓到別名改了沒重烘", any("重跑 bake" in e for e in errs), errs)
        (root / ALIASES_NAME).write_text("{}", encoding="utf-8")
        (root / LUA_REL).write_bytes(first + b"-- x\n")
        errs = check(root, poi)
        ok("check 抓到 Lua 與 render 不同", any("重跑 render" in e for e in errs), errs)
        (root / RES_DIR_NAME / "Z.json").write_text(dump_resource({**doc, "zip": "Z.pyramid.zip", "aliases": {}}),
                                                    encoding="utf-8")
        errs = check(root, poi)
        ok("check 抓到對不到註冊的 json", any("對不到註冊" in e for e in errs), errs)

    print(f"\n{'✅' if n_ok == n_all else '❌'} selftest {n_ok}/{n_all}")
    return 0 if n_ok == n_all else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--selftest", action="store_true", help="合成資料自我測試")
    sub = parser.add_subparsers(dest="cmd")
    pick = argparse.ArgumentParser(add_help=False)
    pick.add_argument("--only", default="", help="zip 名子字串過濾（不分大小寫）")
    pick.add_argument("--prefer", action="append", default=[], help="優先索引的額外 workshop content 根")
    sub.add_parser("bake", parents=[pick], help="重烘選到的地圖並重產 Lua（有沒審過的 loot 房名就整批不寫）")
    c = sub.add_parser("candidates", parents=[pick], help="列出沒審過的 loot 房名給審查（不會因此失敗）")
    c.add_argument("--out", required=True)
    sub.add_parser("parking", parents=[pick], help="只重算選到地圖的停車場，資源點不動，並重產 Lua")
    sub.add_parser("render", help=f"{RES_DIR_NAME}/*.json → {LUA_REL.name}")
    sub.add_parser("check", help="離線閘門：別名檔、json 與註冊、別名同步、Lua 同步")
    args = parser.parse_args(argv)
    if args.selftest:
        return cmd_selftest()
    if args.cmd == "bake":
        return cmd_bake(args)
    if args.cmd == "candidates":
        return cmd_candidates(args)
    if args.cmd == "parking":
        return cmd_parking(args)
    if args.cmd == "render":
        _write_lua(_poi())
        return 0
    if args.cmd == "check":
        errors = check(PROJECT_ROOT, _poi())
        for e in errors:
            print(f"  ❌ {e}")
        print("❌ 地圖資源點資料" if errors else "✅ 地圖資源點資料")
        return 1 if errors else 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
