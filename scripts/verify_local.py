# -*- coding: utf-8 -*-
"""ModMaps 專屬檢查：scripts/verify_mod.py（家族模板副本）第 19 項會呼叫；單獨跑 `python scripts/verify_local.py`。
2026-11-26 verify_mod.py 換成家族模板時，從舊副本原樣搬來模板沒有的檢查：
  - 翻譯鍵集一致（街名版）— 街名／補路鍵（_Street_／_Road_）只在 EN/CH/CN/JP，其他語系不得有
  - 街名翻譯、獨立道路修正、補充道路、地圖資源點生成物 verify／check，與 gen_map_resources.py --selftest
  - 道路資料狀態與公開清單（tracker-state/road_status.json、docs/road-data.md）
"""
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

passed, failed, skipped = [], [], []


def ok(label):
    passed.append(label)
    print(f"  PASS  {label}")


def fail(label, details=None):
    # 不讀 verify_ignore.txt，verify_mod.py 第 19 項也不對本檔輸出套用豁免：要豁免就在本檔處理
    details = details or []
    failed.append(label)
    print(f"  FAIL  {label}")
    for d in details:
        print(f"        {d}")


def skip(label, why):
    skipped.append(label)
    print(f"  SKIP  {label} — {why}")


def find_media():
    hits = []
    mod_root = os.path.join(REPO, "MOD")
    if os.path.isdir(mod_root):
        for folder in os.listdir(mod_root):
            p = os.path.join(mod_root, folder, "Contents", "mods")
            if not os.path.isdir(p):
                continue
            for inner in os.listdir(p):
                media = os.path.join(p, inner, "42", "media")
                if os.path.isdir(media):
                    hits.append(media)
    return hits


MEDIA_DIRS = find_media()
if not MEDIA_DIRS:
    print("找不到 MOD/*/Contents/mods/*/42/media，中止")
    sys.exit(2)

# ---- 翻譯鍵集一致（街名版）----
# 模板第 3 項以第一個語系為基準要求所有語系鍵集相同；本 repo 的街名／補路鍵只在 EN/CH/CN/JP，
# 那一項對 UI.json 的這四語報不一致，已在 scripts/verify_ignore.txt 豁免，真正的鍵集檢查在這裡。
# 街名／補路鍵只在 EN/CH/CN/JP：主 MOD 只在 CH/CN/JP 套用街名譯名，其他語言顯示上游英文原名，
# 和原版街名一致（MinidoracatMiniMapFor42 MinidoracatMiniMap_StreetData.lua 的 currentTranslation）。
# 其他語系比對時排除這些鍵，多放也算不一致；產生器 gen_streets_i18n.py／gen_road_supplements.py 只寫這四語。
# JSON 解析失敗由模板第 3 項「翻譯 JSON 可解析」回報，這裡略過那個檔。
STREET_ONLY_PREFIXES = ("UI_MinidoracatMiniMapModMaps_Street_", "UI_MinidoracatMiniMapModMaps_Road_")
STREET_LANGS = ("EN", "CH", "CN", "JP")

for m in MEDIA_DIRS:
    troot = os.path.join(m, "lua", "shared", "Translate")
    if not os.path.isdir(troot):
        continue
    langs = sorted(d for d in os.listdir(troot) if os.path.isdir(os.path.join(troot, d)))
    names = sorted({n for l in langs for n in os.listdir(os.path.join(troot, l)) if n.endswith(".json")})
    mismatch = []
    for n in names:
        keysets = {}
        for l in langs:
            p = os.path.join(troot, l, n)
            if not os.path.isfile(p):
                mismatch.append(f"{n}: {l} 缺檔")
                continue
            try:
                with open(p, encoding="utf-8") as fh:
                    data = json.load(fh)
            except Exception:
                continue
            keysets[l] = set(data)
        if len(keysets) > 1:
            full = [l for l in STREET_LANGS if l in keysets]
            base = keysets[full[0]] if full else next(iter(keysets.values()))
            core = {k for k in base if not k.startswith(STREET_ONLY_PREFIXES)}
            for l, ks in keysets.items():
                want = base if l in STREET_LANGS else core
                if ks != want:
                    street = sum(k.startswith(STREET_ONLY_PREFIXES) for k in ks - want)
                    note = f"，含 {street} 個只該在 {'/'.join(STREET_LANGS)} 的街名／補路鍵" if street else ""
                    mismatch.append(f"{n}: {l} 鍵集不一致（差 {len(ks ^ want)} 鍵{note}）")
    fail("翻譯鍵集一致", mismatch) if mismatch else ok(
        f"翻譯鍵集一致（{'/'.join(langs)}；街名／補路鍵只在 {'/'.join(STREET_LANGS)}）")

# ---- 名稱、獨立道路修正、補充道路、地圖資源點資料 ----
for script, sub, label in (
    ("gen_streets_i18n.py", "verify", "街名翻譯生成物"),
    ("gen_street_repairs.py", "verify", "獨立道路修正生成物"),
    ("gen_road_supplements.py", "verify", "補充道路生成物"),
    ("gen_map_resources.py", "check", "地圖資源點與房名別名生成物"),
    ("gen_map_resources.py", "--selftest", "地圖資源點 generator 自我測試"),
):
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(REPO, "scripts", script), sub],
            cwd=REPO, capture_output=True, text=True, encoding="utf-8", timeout=60,
        )
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.returncode:
            fail(label, [result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"])
        else:
            ok(label)
    except (OSError, subprocess.TimeoutExpired) as error:
        fail(label, [str(error)])

# ---- 道路資料狀態與公開清單（tracker-state/road_status.json、docs/road-data.md） ----
try:
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import road_status
    from pathlib import Path

    road_problems = road_status.verify(Path(REPO))
except (OSError, ValueError) as error:
    road_problems = [str(error)]
fail("道路資料狀態與公開清單", road_problems) if road_problems \
    else ok("道路資料狀態與公開清單（涵蓋全部註冊地圖、docs/road-data.md 同步）")

print()
print(f"PASS {len(passed)} / FAIL {len(failed)} / SKIP {len(skipped)}")
sys.exit(1 if failed else 0)
