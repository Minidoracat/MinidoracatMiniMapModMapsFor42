# -*- coding: utf-8 -*-
"""批次重渲地圖包 pyramid：讀 MinidoracatMiniMapModMaps.lua 註冊表，逐張以
pzmap render-minimap 重渲到 42/media/minimap/。

用法：
  python scripts/rebuild_pyramids.py --dry-run          # 只解析與定位，不渲染
  python scripts/rebuild_pyramids.py --only FireDept    # zip 名子字串過濾
  python scripts/rebuild_pyramids.py                    # 全量

每條註冊 = { zip, mapMod, [mapDir], bounds }：
  - mapMod 以 mod.info 的 id= 在 workshop 目錄索引定位 mod 根目錄
  - --region 由 bounds//256 還原（bounds 右/下排他 → x1 = maxX//256 - 1）
  - mod.info require= 一層解析成額外 --mod（tile packs），map mod 放最後（later wins）
  - 同 zip 的 alias 條目（互斥變體）只渲一次
渲後驗證：輸出 zip 的 pyramid.txt bounds 必須與註冊 bounds 一致（不一致=Lua 要跟著改，列警告）。
渲後處理：CLEAR 列的 zip 把指定範圍改成透明（內容互補的鄰圖）；不重渲只補做用 --clear-only。
"""
import argparse, json, re, subprocess, sys, time, zipfile
from pathlib import Path

from gen_streets_i18n import item_dirs

REPO = Path(__file__).resolve().parent.parent
LUA = REPO / "MOD/MinidoracatMiniMapModMapsFor42/Contents/mods/MinidoracatMiniMapModMapsFor42/42/media/lua/client/MinidoracatMiniMapModMaps.lua"
OUT_DIR = REPO / "MOD/MinidoracatMiniMapModMapsFor42/Contents/mods/MinidoracatMiniMapModMapsFor42/42/media/minimap"
PZMAP = Path(r"D:\github\MinidoracatMapRendering\target\release\pzmap.exe")
GAME = Path(r"D:\SteamLibrary\steamapps\common\ProjectZomboid")
WORKSHOP = Path(r"D:\SteamLibrary\steamapps\workshop\content\108600")

# 內容互補的鄰圖：兩張圖的 256 格外框重疊、內容各佔不同的 300 格（重疊 0）。pzmap 在本圖沒有內容的格畫原版，
# 疊在上面的那顆會用原版影像蓋掉鄰圖。這裡列「本圖沒有內容、鄰圖有內容」的範圍（世界座標，右下排他），
# 渲完改成透明讓下層（鄰圖或原版底圖）露出來。加一筆前先用 lotpack 確認本圖在範圍內 0 格有內容。
CLEAR = {
    # 路易斯維爾貨運港 × LV 國際機場（共用 49_17、49_18、50_18；港口的外框還含它沒有的 50_17）
    "lvharbor.pyramid.zip": [(12600, 4352, 13056, 4800)],
    "lvinternationalairport.pyramid.zip": [(12544, 4352, 12600, 4864), (12600, 4800, 13056, 4864)],
}


def lua_unescape(s):
    """註冊表字串值的 `\\ddd`（UTF-8 位元組十進位跳脫）還原成 Unicode。

    Lua 字面值只能 ASCII（verify_mod 4c）：含 ’ 等字元的 mod ID／目錄寫成 `\\226\\128\\153`，
    Kahlua 以 UTF-8 解回原字；這裡照做，否則工具拿跳脫字面去比 mod.info id= 會對不上。"""
    return re.sub(rb"\\(\d{1,3})", lambda m: bytes([int(m[1])]), s.encode()).decode()


def parse_registrations(text):
    entries = []
    # 每條目從 "{ zip =" 起、到 bounds 值結束；bounds 是唯一巢狀 {}。
    # zip/mapMod 之後到 bounds 之前的鍵一律寬鬆吃下（mapDir、streetNames…）：
    # 逐一列舉的話，主 MOD 每加一個註冊欄位就會讓這裡靜默漏解析＝漏渲。
    # 字串值必須以 "…" 精確匹配——mapDir 值本身含逗號（"Megurigaoka City, Kanagawa"）。
    # 第二個分支＝表索引值（streetNames = StreetNames["<dataset>"]）。
    opt_key = r'\s*\w+\s*=\s*(?:"[^"]*"|[\w.]+\s*\[\s*"[^"]*"\s*\]|[\w.+-]+)\s*,'
    pat = re.compile(
        r'\{\s*zip\s*=\s*"(?P<zip>[^"]+)"\s*,\s*mapMod\s*=\s*"(?P<mod>[^"]+)"\s*,'
        rf'(?P<opts>(?:{opt_key})*)'
        r'\s*bounds\s*=\s*\{\s*(?P<b0>\d+)\s*,\s*(?P<b1>\d+)\s*,\s*(?P<b2>\d+)\s*,\s*(?P<b3>\d+)\s*\}',
        re.S,
    )
    for m in pat.finditer(text):
        map_dir = re.search(r'mapDir\s*=\s*"([^"]+)"', m["opts"])
        entries.append({
            "zip": lua_unescape(m["zip"]), "mapMod": lua_unescape(m["mod"]),
            "mapDir": lua_unescape(map_dir[1]) if map_dir else None,
            "bounds": (int(m["b0"]), int(m["b1"]), int(m["b2"]), int(m["b3"])),
        })
    # fail-closed：漏解析不會壞掉，只會少渲／少追蹤一張圖且毫無跡象
    declared = len(re.findall(r'\{\s*zip\s*=\s*"', text))
    if len(entries) != declared:
        raise SystemExit(
            f"❌ 註冊表解析 {len(entries)}/{declared} 條——有條目格式未涵蓋，"
            "修 parse_registrations 再跑（漏解析＝靜默漏渲／漏追蹤）。"
        )
    return entries


VERSION_DIR = re.compile(r"^42(\.\d+)*$")  # B42 版本資料夾：42、42.0、42.13…


def index_workshop(extra_roots=()):
    """id -> mod 根目錄（mods/<name>/）。同一 Workshop 項目在多個 content 根都有副本時只看
    最新那份（item_dirs：acf timeupdated，同分照 extra_roots 在前）。不同項目宣告同一 id 時首見進 idx，
    其餘進 alts（Coryerdon 舊移植與 2026 移植版都是 CoryerdonB42），但只有根目錄 mod.info 的 B41 項目讓位給
    B42 那份（材質包依賴照 idx 取）；地圖條目一律經 entry_root 依 mapDir 挑。
    同一 mod 根目錄有多份 mod.info（根目錄、common、42*）時 require= 取聯集：根目錄先、只出現在 B42 那份的
    材質包接在後面（later wins）。LV 國際機場根目錄（B41）沒列、42/ 才列 Community Tile Pack。"""
    idx, requires, alts = {}, {}, {}
    roots = [*extra_roots, WORKSHOP]
    chosen = {}

    def fresh(item):
        if item.name not in chosen:
            chosen[item.name] = item_dirs(roots, item.name)[0]
        return chosen[item.name] == item

    for ws in roots:
        for info in ws.glob("*/mods/*/mod.info"):
            if fresh(info.parents[2]):
                _index_info(info, info.parent, idx, requires, alts)
        for info in ws.glob("*/mods/*/*/mod.info"):
            sub = info.parent.name
            if (sub.lower() == "common" or VERSION_DIR.match(sub)) and fresh(info.parents[3]):
                _index_info(info, info.parent.parent, idx, requires, alts)
    return idx, requires, alts


def _index_info(info, root, idx, requires, alts):
    try:
        text = info.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    mid = req = None
    for line in text.splitlines():
        if line.startswith("id="):
            mid = line[3:].strip()
        elif line.startswith("require="):
            # B42 mod.info 可寫 require=\Name（反斜線前綴），依 id 索引時要剝掉
            req = [r.strip().lstrip("\\") for r in line[8:].split(",") if r.strip().lstrip("\\")]
    if not mid:
        return
    if mid not in idx:
        idx[mid] = root
        requires[mid] = req or []
    elif root == idx[mid]:
        requires[mid] += [r for r in req or [] if r not in requires[mid]]
    else:
        alt = next((a for a in alts.get(mid, []) if a[0] == root), None)
        if alt:
            alt[1].extend(r for r in req or [] if r not in alt[1])
        else:
            alt = (root, list(req or []))
            alts.setdefault(mid, []).append(alt)
        # B42 只列有 common／版本資料夾 mod.info 的 MOD（ZomboidFileSystem.getAllModFoldersAux）：同一 id 有
        # B41 原版與 B42 移植版（Dylan's Tile Pack 2599752664 與 [B42] Dylan's tiles 3754850359）時，以 B42 那份為主
        if _is_b42(root) and not _is_b42(idx[mid]):
            alts[mid].remove(alt)
            alts[mid].insert(0, (idx[mid], requires[mid]))
            idx[mid], requires[mid] = alt


def _is_b42(root):
    return any((p / "mod.info").is_file() for p in root.iterdir()
               if p.is_dir() and (p.name.lower() == "common" or VERSION_DIR.match(p.name)))


def entry_root(idx, requires, alts, e):
    """註冊條目 → (mod 根目錄, 地圖目錄名, require= 清單)；本機找不到回 None。
    同一 id 有多份（alts）時依序試，取 media/maps 下有該地圖目錄的那份。"""
    mid = e["mapMod"]
    if mid not in idx:
        return None
    stem = e["zip"].removesuffix(".pyramid.zip")
    for root, req in [(idx[mid], requires[mid]), *alts.get(mid, [])]:
        name = find_map_dir(root, e["mapDir"], stem, mid)
        if name:
            return root, name, req
    return None


def find_map_dir(root, want, zip_stem, map_mod):
    bases = [root] + [p for p in root.iterdir()
                      if p.is_dir() and (p.name.lower() == "common" or VERSION_DIR.match(p.name))]
    dirs = []
    for base in bases:
        d = base / "media" / "maps"
        if d.is_dir():
            dirs += [p.name for p in d.iterdir() if p.is_dir()]
    dirs = list(dict.fromkeys(dirs))
    if want:
        return want if want in dirs else None
    if len(dirs) == 1:
        return dirs[0]
    # 多地圖目錄（主圖＋出生點圖）：用 zip 名或 mod id 精確配對
    for cand in (zip_stem, map_mod):
        if cand in dirs:
            return cand
    return None


def zip_bounds(path):
    with zipfile.ZipFile(path) as z:
        for line in z.read("pyramid.txt").decode().splitlines():
            if line.startswith("bounds="):
                return tuple(int(v) for v in line[7:].split())
    return None


def clear_rects(path, rects):
    """把 rects 在每一層的像素改成透明（像素中心落在範圍內才清），回傳改寫的 tile 數；已透明的不重寫，可重複執行。"""
    import io
    from PIL import Image  # 只有這一步要 pillow；gen_map_resources 匯入本檔時不需要

    bx, by = zip_bounds(path)[:2]
    with zipfile.ZipFile(path) as z:
        files = [(i, z.read(i.filename)) for i in z.infolist()]
    changed = 0
    for n, (info, data) in enumerate(files):
        m = re.fullmatch(r"(\d+)/tile(\d+)x(\d+)\.png", info.filename)
        if not m:
            continue
        scale, tx, ty = 2 ** int(m[1]), int(m[2]) * 256, int(m[3]) * 256
        im = Image.open(io.BytesIO(data)).convert("RGBA")
        dirty = False
        for x0, y0, x1, y1 in rects:
            # 像素 i 的中心是世界座標 b + (i + 0.5) * scale；第一個中心 ≥ v 的像素 = ceil((v - b) / scale - 0.5)
            box = [max(0, -((scale - 2 * (v - b)) // (2 * scale)) - t)
                   for v, b, t in ((x0, bx, tx), (y0, by, ty), (x1, bx, tx), (y1, by, ty))]
            box[2], box[3] = min(box[2], im.width), min(box[3], im.height)
            if box[0] < box[2] and box[1] < box[3] and im.crop(box).getchannel("A").getextrema() != (0, 0):
                im.paste((0, 0, 0, 0), tuple(box))
                dirty = True
        if dirty:
            buf = io.BytesIO()
            im.save(buf, "PNG")
            files[n] = (info, buf.getvalue())
            changed += 1
    if changed:
        tmp = path.with_suffix(".tmp")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_STORED) as z:
            for info, data in files:
                z.writestr(info.filename, data)
        tmp.replace(path)
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="", help="zip 名子字串過濾")
    ap.add_argument("--prefer", action="append", default=[],
                    help="額外的 workshop content 根目錄（例：steamcmd 下載處；同一項目多份副本取 acf 最新者）")
    ap.add_argument("--skip-fresh-min", type=int, default=0,
                    help="輸出 zip 在 N 分鐘內已更新者跳過（批次中斷後續跑用）")
    ap.add_argument("--clear-only", action="store_true",
                    help="不渲染，只對現有 zip 補做 CLEAR 的透明範圍（可配 --only）")
    args = ap.parse_args()

    if args.clear_only:
        for name, rects in CLEAR.items():
            if args.only.lower() in name.lower():
                print(f"{name}: 改寫 {clear_rects(OUT_DIR / name, rects)} 個 tile（0＝已經是透明）")
        return

    entries = parse_registrations(LUA.read_text(encoding="utf-8"))
    idx, requires, alts = index_workshop([Path(p) for p in args.prefer])
    seen, plan, missing = set(), [], []
    for e in entries:
        if e["zip"] in seen or (args.only and args.only.lower() not in e["zip"].lower()):
            continue
        seen.add(e["zip"])
        # alias 條目：同 zip 依序換用其他條目再試
        hit = next((h for x in entries if x["zip"] == e["zip"]
                    for h in [entry_root(idx, requires, alts, x)] if h), None)
        if hit is None:
            missing.append((e["zip"], e["mapMod"],
                            f"mod 不在本機 workshop，或 media/maps 下找不到地圖目錄（mapDir={e['mapDir']}）"))
            continue
        root, map_name, req = hit
        deps = [idx[r] for r in req if r in idx and idx[r] != root]
        b = e["bounds"]
        region = (b[0] // 256, b[1] // 256, b[2] // 256 - 1, b[3] // 256 - 1)
        plan.append({"zip": e["zip"], "mod_root": root, "map": map_name,
                     "deps": deps, "region": region, "bounds": b})

    print(f"註冊 {len(entries)} 條 → 待渲 {len(plan)} 張，無法定位 {len(missing)} 張")
    for z, m, why in missing:
        print(f"  [缺] {z} ({m}): {why}")
    if args.dry_run:
        for p in plan:
            print(f"  [計畫] {p['zip']} ← {p['map']} @ {p['mod_root'].name} region={p['region']} deps={len(p['deps'])}")
        return

    ok, bad = 0, []
    for i, p in enumerate(plan, 1):
        out = OUT_DIR / p["zip"]
        if (args.skip_fresh_min and out.exists()
                and time.time() - out.stat().st_mtime < args.skip_fresh_min * 60):
            print(f"[{i}/{len(plan)}] {p['zip']} 略過（{args.skip_fresh_min} 分鐘內已渲）", flush=True)
            ok += 1
            continue
        cmd = [str(PZMAP), "render-minimap", "--game", str(GAME)]
        for d in p["deps"]:
            cmd += ["--mod", str(d)]
        cmd += ["--mod", str(p["mod_root"]), "--map", p["map"],
                "--region", ",".join(map(str, p["region"])), "--out", str(out)]
        print(f"[{i}/{len(plan)}] {p['zip']} ...", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            bad.append((p["zip"], (r.stderr or r.stdout).strip()[-300:]))
            print(f"  [失敗] exit {r.returncode}")
            continue
        for line in (r.stderr or "").splitlines():  # pzmap 的 warn 區塊（含缺圖名稱；maps.md「已知坑」42.22 那條）
            if line.startswith(("warn:", "  ")):
                print(f"  {line}")
        got = zip_bounds(out)
        if got != p["bounds"]:
            bad.append((p["zip"], f"bounds 不符：註冊 {p['bounds']} vs 輸出 {got}（Lua 註冊表需更新）"))
            print("  [警告] bounds 不符")
        ok += 1
        if p["zip"] in CLEAR:
            print(f"  清成透明 {CLEAR[p['zip']]}：{clear_rects(out, CLEAR[p['zip']])} 個 tile")
    print(f"\n完成 {ok}/{len(plan)}；問題 {len(bad)} 張；缺 mod {len(missing)} 張")
    for z, why in bad:
        print(f"  [問題] {z}: {why}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
