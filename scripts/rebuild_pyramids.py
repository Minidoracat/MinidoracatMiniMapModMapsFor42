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
"""
import argparse, json, re, subprocess, sys, time, zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LUA = REPO / "MOD/MinidoracatMiniMapModMapsFor42/Contents/mods/MinidoracatMiniMapModMapsFor42/42/media/lua/client/MinidoracatMiniMapModMaps.lua"
OUT_DIR = REPO / "MOD/MinidoracatMiniMapModMapsFor42/Contents/mods/MinidoracatMiniMapModMapsFor42/42/media/minimap"
PZMAP = Path(r"D:\github\MinidoracatMapRendering\target\release\pzmap.exe")
GAME = Path(r"D:\SteamLibrary\steamapps\common\ProjectZomboid")
WORKSHOP = Path(r"D:\SteamLibrary\steamapps\workshop\content\108600")


def parse_registrations(text):
    entries = []
    # 每條目從 "{ zip =" 起、到 bounds 值結束；bounds 是唯一巢狀 {}。
    # zip/mapMod 之後到 bounds 之前的鍵一律寬鬆吃下（mapDir、streetI18n…）：
    # 逐一列舉的話，主 MOD 每加一個註冊欄位就會讓這裡靜默漏解析＝漏渲。
    # 字串值必須以 "…" 精確匹配——mapDir 值本身含逗號（"Megurigaoka City, Kanagawa"）。
    opt_key = r'\s*\w+\s*=\s*(?:"[^"]*"|[\w.+-]+)\s*,'
    pat = re.compile(
        r'\{\s*zip\s*=\s*"(?P<zip>[^"]+)"\s*,\s*mapMod\s*=\s*"(?P<mod>[^"]+)"\s*,'
        rf'(?P<opts>(?:{opt_key})*)'
        r'\s*bounds\s*=\s*\{\s*(?P<b0>\d+)\s*,\s*(?P<b1>\d+)\s*,\s*(?P<b2>\d+)\s*,\s*(?P<b3>\d+)\s*\}',
        re.S,
    )
    for m in pat.finditer(text):
        map_dir = re.search(r'mapDir\s*=\s*"([^"]+)"', m["opts"])
        entries.append({
            "zip": m["zip"], "mapMod": m["mod"],
            "mapDir": map_dir[1] if map_dir else None,
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
    """id -> mod 根目錄（mods/<name>/）；同 id 首見為準——extra_roots 先掃、優先勝出
    （steamcmd 下載的新鮮副本蓋過 Steam 客戶端的過期目錄）。"""
    idx, requires = {}, {}
    for ws in [*extra_roots, WORKSHOP]:
        for info in ws.glob("*/mods/*/mod.info"):
            _index_info(info, info.parent, idx, requires)
        for info in ws.glob("*/mods/*/*/mod.info"):
            sub = info.parent.name
            if sub.lower() == "common" or VERSION_DIR.match(sub):
                _index_info(info, info.parent.parent, idx, requires)
    return idx, requires


def _index_info(info, root, idx, requires):
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
    if mid and mid not in idx:
        idx[mid] = root
        requires[mid] = req or []


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="", help="zip 名子字串過濾")
    ap.add_argument("--prefer", action="append", default=[],
                    help="優先索引的額外 workshop content 根目錄（例：steamcmd 下載處）")
    ap.add_argument("--skip-fresh-min", type=int, default=0,
                    help="輸出 zip 在 N 分鐘內已更新者跳過（批次中斷後續跑用）")
    args = ap.parse_args()

    entries = parse_registrations(LUA.read_text(encoding="utf-8"))
    idx, requires = index_workshop([Path(p) for p in args.prefer])
    seen, plan, missing = set(), [], []
    for e in entries:
        if e["zip"] in seen or (args.only and args.only.lower() not in e["zip"].lower()):
            continue
        root = idx.get(e["mapMod"])
        if root is None:
            # alias 條目：換用同 zip 其他 mapMod 再試
            alt = next((x for x in entries if x["zip"] == e["zip"] and idx.get(x["mapMod"])), None)
            if alt is None:
                missing.append((e["zip"], e["mapMod"], "mod 不在本機 workshop"))
                seen.add(e["zip"])
                continue
            e, root = alt, idx[alt["mapMod"]]
        map_name = find_map_dir(root, e["mapDir"], e["zip"].removesuffix(".pyramid.zip"), e["mapMod"])
        if map_name is None:
            missing.append((e["zip"], e["mapMod"], f"media/maps 下找不到地圖目錄（mapDir={e['mapDir']}）"))
            seen.add(e["zip"])
            continue
        deps = [idx[r] for r in requires.get(e["mapMod"], []) if r in idx and idx[r] != root]
        b = e["bounds"]
        region = (b[0] // 256, b[1] // 256, b[2] // 256 - 1, b[3] // 256 - 1)
        plan.append({"zip": e["zip"], "mod_root": root, "map": map_name,
                     "deps": deps, "region": region, "bounds": b})
        seen.add(e["zip"])

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
        got = zip_bounds(out)
        if got != p["bounds"]:
            bad.append((p["zip"], f"bounds 不符：註冊 {p['bounds']} vs 輸出 {got}（Lua 註冊表需更新）"))
            print("  [警告] bounds 不符")
        ok += 1
    print(f"\n完成 {ok}/{len(plan)}；問題 {len(bad)} 張；缺 mod {len(missing)} 張")
    for z, why in bad:
        print(f"  [問題] {z}: {why}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
