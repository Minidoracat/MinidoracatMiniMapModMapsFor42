#!/usr/bin/env python3
"""支援地圖更新追蹤器（每日排程；架構沿用 MinidoracatModLangFor42 scripts/tracker.py）。

watchlist＝Steam「支援地圖收藏」3766382352（發現來源，發版流程本來就會維護），
排除自家項目（creator=OWN_CREATOR 者）；state 是附加式帳本（merge、永不 prune），
收藏瞬時異常不會毀基準。兩軸偵測：

MOD 軸（time_updated 變動）→ steamcmd 下載該項 → hash 圖資（media/maps/ 的
  .lotheader/.lotpack/.bin＋mod 自帶 texturepack/.tiles）→ 與基準比對 →
  issue 直接標「需重渲（哪些 mapDir、bounds 是否變動）」或「免重渲（僅腳本/loot）」。
  下架（API result=9）→ 開「[地圖下架]」issue 一次；自下輪起不再查詢（tombstone 保留），
  重新上架要恢復追蹤＝手動把 state 該項 removed 改回 false。
  首次見到（含 --bootstrap 首建）→ 靜默記基準，零 issue。
遊戲軸（public branch buildid 變動，steamcmd app_info_print）→ 開「[遊戲更新]」
  issue 提醒評估全量重渲（42.20 案例：主世界 950 cells 變更）。

CI 三 job（權限逐 job 最小化；diff 下載第三方內容故無 GitHub 寫權限，只靜態 hash 絕不執行）：
  check --out changed.json   查時間戳＋分類（contents:read）
  diff  --in --out --steamcmd  下載變更項＋hash 判定＋查遊戲 buildid（contents:read）
  issue --in mapdiff.json    冪等開/更 issue＋commit state（issues+contents:write）
本機：
  run --dry-run       查詢＋印計畫（零 issue、不寫 state）
  run --bootstrap     首建 timestamps 基準（零 issue）
  hash-baseline --steamcmd <exe> [--client-root <dir>]
                      對全部追蹤項建圖資基準（先自行 steamcmd 批次下載）；
                      給 --client-root 時同時報告新舊副本 drift（渲染來源過期偵測）
  self-test           零網路自我測試

state（tracker-state/timestamps.json＋mapdata_hashes.json）進版控；gh 任一步失敗即中止、
state 不推進，下一輪由 issue body marker 冪等自癒（不會重複開）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATE_JSON = PROJECT_ROOT / "tracker-state" / "timestamps.json"
MAPDATA_JSON = PROJECT_ROOT / "tracker-state" / "mapdata_hashes.json"

COLLECTION_ID = "3766382352"  # 支援地圖收藏（含全部地圖 MOD＋自家系列 MOD）
GAME_APPID = "108600"  # Project Zomboid
# Minidoracat 的 steamID64：排除收藏內自家項目用。寫死而非查本包 detail 推導——
# 否則本包被隱藏/暫下架時追蹤器天天死（自傷 kill switch）。日後多帳號改 set 即可。
OWN_CREATOR = "76561198033176898"

COLLECTION_API = "https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/"
DETAILS_API = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
RESULT_OK = 1
RESULT_NOT_FOUND = 9  # 已下架 / 隱藏 / 無效 ID

# 圖資判定：只 hash 會影響 pyramid 渲染的檔案
RENDER_EXTS = {".lotheader", ".lotpack", ".bin"}  # media/maps/<dir>/ 底下的 cell 圖資
ASSET_EXTS = {".pack", ".tiles"}  # mod 自帶材質/tiles（變了＝該 mod 全部地圖要重渲）
_CELL_RE = re.compile(r"^(\d+)_(\d+)\.lotheader$", re.IGNORECASE)

# issue 冪等：單一共通 label + body 首個 HTML marker（只認第一個，防上游字串偽造）
ISSUE_LABEL = "tracker"
TYPE_UPDATE = "update"
TYPE_REMOVED = "removed"
TYPE_GAME = "game"
_MARKER_RE = re.compile(
    r"<!--\s*map-tracker:type=(?P<type>[^;]+);id=(?P<id>[^;]+);hash=(?P<hash>[^;\s]+)\s*-->"
)


def make_marker(issue_type: str, workshop_id: str, content_hash: str) -> str:
    return f"<!-- map-tracker:type={issue_type};id={workshop_id};hash={content_hash} -->"


def parse_marker(body: str) -> tuple[str, str, str] | None:
    m = _MARKER_RE.search(body)
    return (m["type"], m["id"], m["hash"]) if m else None


def neutralize(text: str) -> str:
    """中和上游字串（地圖標題、mapDir 等）：HTML comment 邊界（防偽 marker）＋換行摺疊
    （防多行 title/log 注入）＋backtick 逸出（供 body 以 code span 包覆防 markdown 注入）。"""
    text = text.replace("<!--", "<!ˍ--").replace("-->", "--ˍ>")
    text = " ".join(text.split())
    return text.replace("`", "ˋ")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fmt_ts(epoch) -> str:
    if not epoch:
        return "（未知）"
    utc = datetime.fromtimestamp(int(epoch), timezone.utc)
    tw = utc.astimezone(timezone(timedelta(hours=8)))
    return f"{utc:%Y-%m-%d %H:%M} UTC（台灣 {tw:%m-%d %H:%M}）"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict) -> None:
    """原子寫出：同目錄暫存檔再 os.replace（Windows 目標被占用時短重試）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8", newline="\n")
        for attempt in range(3):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                if attempt == 2:
                    raise
                time.sleep(0.3)
    finally:
        tmp.unlink(missing_ok=True)


# ============================================================
# Steam Web API（免 key、批次、429/5xx 退避）
# ============================================================
def _post_form(url: str, params: list[tuple[str, str]], timeout: float = 30.0) -> dict:
    data = urlencode(params).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "minimap-map-tracker/1"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post_with_retry(
    url: str,
    params: list[tuple[str, str]],
    *,
    max_retries: int = 5,
    base_delay: float = 1.0,
    jitter: float = 0.5,
    sleep: Callable[[float], None] = time.sleep,
) -> dict:
    """429/5xx 用 Retry-After + 指數退避 + jitter 重試；其他錯誤直接拋。"""
    for attempt in range(max_retries + 1):
        try:
            return _post_form(url, params)
        except urllib.error.HTTPError as exc:
            retryable = exc.code == 429 or 500 <= exc.code < 600
            if not retryable or attempt >= max_retries:
                raise
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            if retry_after and retry_after.strip().isdigit():
                delay = float(retry_after.strip())
            else:
                delay = base_delay * (2**attempt)
            sleep(delay + random.uniform(0.0, jitter))
        except OSError:  # URLError 之外還有裸 TimeoutError/ConnectionResetError（皆 OSError）
            if attempt >= max_retries:
                raise
            sleep(base_delay * (2**attempt) + random.uniform(0.0, jitter))
    raise RuntimeError("unreachable")  # pragma: no cover


def fetch_collection_children() -> list[str]:
    """查收藏子項目 ID（依 sortorder；只收一般項目 filetype=0）。失敗/空清單即中止。"""
    params = [("collectioncount", "1"), ("publishedfileids[0]", COLLECTION_ID)]
    resp = _post_with_retry(COLLECTION_API, params)
    colls = resp.get("response", {}).get("collectiondetails", [])
    if not colls or int(colls[0].get("result", 0)) != RESULT_OK:
        print("❌ 收藏查詢失敗（result != 1），中止。", file=sys.stderr)
        sys.exit(1)
    children = colls[0].get("children") or []
    ids = [
        str(c["publishedfileid"])
        for c in sorted(children, key=lambda c: int(c.get("sortorder", 0)))
        if int(c.get("filetype", 0)) == 0 and str(c.get("publishedfileid", "")).isdigit()
    ]
    if not ids:
        print("❌ 收藏子項目為空（疑似 API 異常或收藏被清空），中止。", file=sys.stderr)
        sys.exit(1)
    return ids


def _details_from_response(resp: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for detail in resp.get("response", {}).get("publishedfiledetails", []):
        pid = str(detail.get("publishedfileid", ""))
        if pid:
            out[pid] = detail
    return out


def _fetch_batch(ids: list[str]) -> dict[str, dict]:
    params: list[tuple[str, str]] = [("itemcount", str(len(ids)))]
    for i, wid in enumerate(ids):
        params.append((f"publishedfileids[{i}]", wid))
    return _details_from_response(_post_with_retry(DETAILS_API, params))


def fetch_details(ids: list[str], *, batch: int = 18) -> dict[str, dict]:
    """批次查全部 ID → 缺漏 ID 逐項重試一次。回傳 {id: detail}。"""
    result: dict[str, dict] = {}
    for start in range(0, len(ids), batch):
        result.update(_fetch_batch(ids[start : start + batch]))
    for wid in [w for w in ids if w not in result]:
        try:
            result.update(_fetch_batch([wid]))
        except OSError as exc:  # 含 HTTPError/URLError/TimeoutError
            print(f"  ⚠️ 缺漏重試失敗 {wid}: {exc}", file=sys.stderr)
    return result


def coverage_guard(ids: list[str], details: dict[str, dict]) -> None:
    """API 覆蓋率檢查：有效回應（result=1/9）全空或缺 >50% 視為 API 異常 → 非零退出
    （避免把 rate-limit 之類的系統性怪 result 誤判為「全數無變更」而綠燈失效）。"""
    total = len(ids)
    if total == 0:
        return
    got = sum(
        1 for wid in ids
        if int(details.get(wid, {}).get("result", 0)) in (RESULT_OK, RESULT_NOT_FOUND)
    )
    print(f"  查得 {got}/{total} 筆有效 API 回應")
    if got < total:
        # GitHub Actions annotation：浮上 run summary，排程綠燈也看得到
        print(f"::warning::Steam API 有效回應缺 {total - got}/{total} 筆（缺項 state 不推進，下輪重試）")
    if got == 0:
        print("❌ ids 非空但有效 API 回應全空，中止（疑似 API 故障/封鎖）。", file=sys.stderr)
        sys.exit(1)
    if (total - got) / total > 0.5:
        print("❌ API 有效回應缺項比例 > 50%，中止（疑似 API 異常）。", file=sys.stderr)
        sys.exit(1)


# ============================================================
# 圖資 hash（重渲需求精準判定）
# ============================================================
def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_mod_mapdata(root: Path) -> dict:
    """workshop item 根目錄 → {"maps": {mapDir: {"hash", "bounds"}}, "assets": <hash>}。
    maps 只含 RENDER_EXTS（cell 圖資，僅靜態 hash、絕不執行）；bounds 由 lotheader
    檔名 cell 座標推（×256、右/下排他，同 Lua 註冊表約定）。同名 mapDir 跨
    42/42.x/common 版本資料夾時合併計算。"""
    per_map: dict[str, list] = {}
    cells: dict[str, list] = {}
    assets: list = []
    for f in sorted(root.rglob("*")):
        if not f.is_file():
            continue
        suffix = f.suffix.lower()
        rel_parts = f.relative_to(root).parts
        rel = "/".join(rel_parts).lower()
        if suffix in ASSET_EXTS:
            assets.append((rel, _file_sha256(f)))
            continue
        if suffix not in RENDER_EXTS:
            continue
        low = [p.lower() for p in rel_parts]
        try:
            i = low.index("maps")
        except ValueError:
            continue
        # 需為 .../media/maps/<mapDir>/<file...> 結構
        if i == 0 or low[i - 1] != "media" or i + 1 >= len(rel_parts) - 1:
            continue
        map_dir = rel_parts[i + 1]
        per_map.setdefault(map_dir, []).append((rel, _file_sha256(f)))
        m = _CELL_RE.match(f.name)
        if m:
            cells.setdefault(map_dir, []).append((int(m.group(1)), int(m.group(2))))
    maps = {}
    for name, entries in per_map.items():
        digest = hashlib.sha256(json.dumps(sorted(entries)).encode("utf-8")).hexdigest()
        box = None
        if cells.get(name):
            xs = [c[0] for c in cells[name]]
            ys = [c[1] for c in cells[name]]
            box = [min(xs) * 256, min(ys) * 256, (max(xs) + 1) * 256, (max(ys) + 1) * 256]
        maps[name] = {"hash": digest, "bounds": box}
    assets_hash = hashlib.sha256(json.dumps(sorted(assets)).encode("utf-8")).hexdigest()
    return {"maps": maps, "assets": assets_hash}


def build_verdict(old: dict | None, new: dict) -> dict:
    """新舊圖資 hash → 重渲判定。"""
    if old is None:
        return {"status": "no_baseline", "changed_maps": sorted(new["maps"]), "bounds_changed": {}}
    old_maps, new_maps = old.get("maps", {}), new["maps"]
    changed = sorted(
        d for d in set(old_maps) | set(new_maps)
        if old_maps.get(d, {}).get("hash") != new_maps.get(d, {}).get("hash")
    )
    bounds_changed = {}
    for d in changed:
        ob = old_maps.get(d, {}).get("bounds")
        nb = new_maps.get(d, {}).get("bounds")
        if ob and nb and ob != nb:
            bounds_changed[d] = [ob, nb]
    if old.get("assets") != new["assets"]:
        status = "assets"
    elif changed:
        status = "maps"
    else:
        status = "none"
    return {"status": status, "changed_maps": changed, "bounds_changed": bounds_changed}


def verdict_section(verdict: dict | None) -> list[str]:
    """issue body 的「圖資判定」段（mapDir 名屬上游可控字串 → neutralize＋code span）。"""
    if verdict is None:
        return []
    lines = ["", "### 圖資判定（自動）", ""]
    status = verdict.get("status")
    names = "、".join(f"`{neutralize(str(d))}`" for d in verdict.get("changed_maps", []))
    if status == "none":
        lines.append("- ✅ **免重渲**：本次更新未動地圖圖資／材質（僅腳本、loot 等）。可直接關閉本 issue。")
    elif status == "maps":
        lines.append(f"- 🔴 **需重渲**：圖資變更 mapDir {names}")
    elif status == "assets":
        lines.append("- 🔴 **需重渲（該 MOD 全部地圖）**：mod 自帶材質/tiles 變更"
                     + (f"；圖資亦變更 {names}" if names else ""))
    elif status == "no_baseline":
        lines.append("- ⚠️ **無基準（本次已建立）**：無法比對，建議重渲以保險。")
    else:
        note = neutralize(str(verdict.get("note", "")))
        lines.append(f"- ⚠️ **無法判定**：{note}——請依 Workshop 更新紀錄人工判斷。")
    for d, pair in sorted(verdict.get("bounds_changed", {}).items()):
        lines.append(f"- ⚠️ bounds 變動 `{neutralize(str(d))}`：{pair[0]} → {pair[1]}（**記得同步 Lua 註冊表**）")
    return lines


# ============================================================
# steamcmd（匿名下載 Workshop 內容＋查遊戲 buildid；內容只靜態 hash、絕不執行）
# ============================================================
def steamcmd_run(exe: str, args: list[str], *, timeout: float = 900.0) -> tuple[int, str]:
    proc = subprocess.run(
        [exe, "+login", "anonymous", *args, "+quit"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def find_workshop_item(exe: str, wid: str) -> Path | None:
    """steamcmd 下載內容落點（Windows：exe 同層；Linux：家目錄 Steam 變體）。"""
    exe_dir = Path(exe).resolve().parent
    home = Path.home()
    for base in (exe_dir, home / "Steam", home / ".steam" / "steam", home / ".local" / "share" / "Steam"):
        p = base / "steamapps" / "workshop" / "content" / GAME_APPID / wid
        if p.is_dir():
            return p
    return None


def steamcmd_download(exe: str, wid: str, *, retries: int = 1) -> Path | None:
    """下載單一 Workshop 項目，回傳內容根目錄；失敗回 None（單項失敗不拖垮整輪）。"""
    for _attempt in range(retries + 1):
        try:
            rc, out = steamcmd_run(exe, ["+workshop_download_item", GAME_APPID, wid])
        except subprocess.TimeoutExpired:
            continue
        if rc == 0 and f"Downloaded item {wid}" in out:
            root = find_workshop_item(exe, wid)
            if root is not None:
                return root
    return None


def fetch_game_build(exe: str) -> str | None:
    """PZ public branch buildid；失敗回 None（遊戲軸缺席一輪無妨，下輪再試）。"""
    try:
        _rc, out = steamcmd_run(
            exe, ["+app_info_update", "1", "+app_info_print", GAME_APPID], timeout=300.0
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    m = re.search(r'"public"\s*\{\s*"buildid"\s*"(\d+)"', out)
    return m.group(1) if m else None


# ============================================================
# 變更分類與 issue plan
# ============================================================
def classify(
    map_ids: list[str], details: dict[str, dict], state_items: dict
) -> tuple[list[dict], dict[str, dict], int]:
    """回傳 (issue plans, 每 id 的新 state entry, 本輪新基準數)。
    首次見到的 id（不在 state）一律靜默記基準、零 issue——--bootstrap 首建與日後
    收藏新增地圖走同一條路。"""
    plans: list[dict] = []
    meta: dict[str, dict] = {}
    baselined = 0
    for wid in map_ids:
        prev = state_items.get(wid)
        first_seen = prev is None
        prev = prev or {}
        detail = details.get(wid)
        title = (detail or {}).get("title") or prev.get("title") or wid
        # 不記 last_attempt/last_success：只寫不讀的欄位會讓每日排程產生純噪音 commit
        entry = {
            "title": title,
            "time_updated": prev.get("time_updated"),
            "last_result": prev.get("last_result"),
            "removed": prev.get("removed", False),
            "removed_at": prev.get("removed_at"),
        }
        if detail is None:
            if first_seen:
                continue  # 首見＋查無回應：不入 state，下輪仍視為首見（避免假「更新」issue）
            meta[wid] = entry
            continue  # 查無回應：state 不推進，下輪再試
        meta[wid] = entry
        result = int(detail.get("result", 0))
        entry["last_result"] = result
        if result == RESULT_NOT_FOUND:
            if not prev.get("removed") and not first_seen:
                plans.append(build_removed_plan(wid, title))
            entry["removed"] = True
            entry["removed_at"] = entry["removed_at"] or now_iso()
            if first_seen:
                baselined += 1
            continue
        if result != RESULT_OK:
            print(f"::warning::非預期 Steam API result={result}（id={wid}），本輪略過")
            if first_seen:
                meta.pop(wid)  # 無有效基準可記，下輪仍視為首見
            continue
        new_tu = detail.get("time_updated")
        if not isinstance(new_tu, int) or new_tu <= 0:
            # result=1 但欄位缺失/無效：不得以 0 入庫（會造成假更新 issue 反覆震盪）
            print(f"::warning::time_updated 無效（id={wid}），本輪略過")
            if first_seen:
                meta.pop(wid)
            continue
        old_tu = prev.get("time_updated")
        entry["removed"] = False
        entry["removed_at"] = None  # 重新上架 → 自動恢復追蹤
        entry["time_updated"] = new_tu
        if first_seen:
            baselined += 1
        elif old_tu != new_tu:
            plans.append(build_update_plan(wid, title, old_tu, new_tu))
    return plans, meta, baselined


def build_update_plan(wid: str, title: str, old_tu, new_tu: int) -> dict:
    label = neutralize(title)
    content_hash = hashlib.sha256(f"update|{wid}|{new_tu}".encode("utf-8")).hexdigest()
    body = "\n".join([
        make_marker(TYPE_UPDATE, wid, content_hash),
        f"## 地圖更新：`{label}`（Workshop {wid}）",
        "",
        "追蹤器偵測到上游地圖 MOD 發布了新版本：",
        "",
        f"- 上次記錄：{fmt_ts(old_tu)}",
        f"- 本次更新：{fmt_ts(new_tu)}",
        f"- [Workshop 頁面](https://steamcommunity.com/sharedfiles/filedetails/?id={wid})"
        f"｜[更新紀錄](https://steamcommunity.com/sharedfiles/filedetails/changelog/{wid})",
        "",
        "**處置**（見下方自動圖資判定；免重渲可直接關閉）：",
        "",
        "- [ ] pzmap Studio 或 `scripts/rebuild_pyramids.py --only <zip名>` 重渲該地圖",
        "- [ ] bounds 若變動，同步 `MinidoracatMiniMapModMaps.lua`",
        "- [ ] 地圖名稱／`mapDir` 若變動，同步 Lua 註冊與 `Translate/*/UI.json`",
        "- [ ] `python scripts/verify_mod.py` 通過後照常發版",
    ])
    return {
        "type": TYPE_UPDATE,
        "workshop_id": wid,
        "content_hash": content_hash,
        "title": f"[地圖更新] {label}（{wid}）",
        "body": body,
        "comment": f"追蹤器偵測到再次更新：{fmt_ts(new_tu)}（上次記錄 {fmt_ts(old_tu)}）。",
    }


def build_removed_plan(wid: str, title: str) -> dict:
    label = neutralize(title)
    content_hash = hashlib.sha256(f"removed|{wid}".encode("utf-8")).hexdigest()
    body = "\n".join([
        make_marker(TYPE_REMOVED, wid, content_hash),
        f"## 地圖下架：`{label}`（Workshop {wid}）",
        "",
        "每日檢查發現此 Workshop 項目已無法存取（Steam API result=9），",
        "可能為作者隱藏／移除，或遭 Steam 下架。",
        "",
        "**處置**（現行政策：下架即移除支援，見 README「已下架地圖」表）：",
        "",
        "- [ ] 自 `media/minimap/` 刪 pyramid zip、刪 Lua 註冊條目與四語翻譯鍵",
        "- [ ] README 收錄表移除該列、補進「已下架地圖」表；三語 Steam 描述與許願串數字同步",
        f"- [ ] 自[支援地圖收藏](https://steamcommunity.com/sharedfiles/filedetails/?id={COLLECTION_ID})移除該項目",
        "- 自下輪起本項目**停止每日查詢**（記錄保留於 tracker-state）；處置完關閉本 issue 即可。",
        "- 若日後重新上架且要恢復支援：`tracker-state/timestamps.json` 該項 `removed` 改回 `false`，重渲補回註冊。",
    ])
    return {
        "type": TYPE_REMOVED,
        "workshop_id": wid,
        "content_hash": content_hash,
        "title": f"[地圖下架] {label} 已無法存取（{wid}）",
        "body": body,
        "comment": "追蹤器再次確認此項目仍不可存取。",
    }


def build_game_plan(old_build: str, new_build: str) -> dict:
    content_hash = hashlib.sha256(f"game|{new_build}".encode("utf-8")).hexdigest()
    body = "\n".join([
        make_marker(TYPE_GAME, GAME_APPID, content_hash),
        f"## Project Zomboid 本體更新：build {old_build} → {new_build}",
        "",
        "追蹤器偵測到遊戲 public branch buildid 變更。本體更新若動到世界 cell／tiles，",
        "MOD 未覆蓋處會透出新 vanilla 基底（42.20 案例：主世界 950 cells 變更 → 全量重渲）。",
        "",
        "**處置**：",
        "",
        "- [ ] 看官方更新說明是否含地圖／世界／tiles 變更（純平衡性、修 bug 可直接關閉）",
        "- [ ] 確認渲染工具（MinidoracatMapRendering）與新版相容（42.20 案例：Atlas 需補載新分支）",
        "- [ ] 需要重渲時：steamcmd 同步訂閱內容 → `python scripts/rebuild_pyramids.py --prefer <steamcmd content 根>`",
        "- [ ] `python scripts/verify_mod.py` 通過後照常發版",
    ])
    return {
        "type": TYPE_GAME,
        "workshop_id": GAME_APPID,
        "content_hash": content_hash,
        "title": f"[遊戲更新] PZ build {old_build} → {new_build}：評估是否需要重渲",
        "body": body,
        "comment": f"追蹤器偵測到再次更新：build → {new_build}。",
    }


# ============================================================
# GitHub issue（gh CLI；冪等開/更）
# ============================================================
class GhClient:
    """真實 GitHub CLI 客戶端（GITHUB_TOKEN 由環境提供）。任一失敗即 raise 中止本輪
    → state 不推進、下輪由 marker 冪等自癒（fail-closed，不會重複開 issue）。"""

    # ponytail: 只查 open issue——若「issue 已開、state commit 失敗、人於下輪前關掉 issue」
    # 三事齊發會重複開一張；屆時升級為 state=all + hash 命中 skip / 不同則 reopen
    def list_tracker_issues(self) -> list[dict]:
        proc = subprocess.run(
            [
                "gh", "api", "--paginate",
                f"repos/:owner/:repo/issues?labels={ISSUE_LABEL}&state=open",
                "--jq", ".[] | {number, body, title}",
            ],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if proc.returncode != 0:
            raise RuntimeError(f"gh api 列 tracker issue 失敗：{proc.stderr.strip()}")
        return [json.loads(s) for s in (line.strip() for line in proc.stdout.splitlines()) if s]

    def ensure_label(self) -> None:
        """確保『tracker』label 存在（冪等；缺 label 時 create_issue 會直接失敗）。"""
        proc = subprocess.run(
            [
                "gh", "label", "create", ISSUE_LABEL,
                "--description", "地圖更新追蹤器自動 issue（地圖更新/下架/遊戲更新）",
                "--color", "1D76DB",
            ],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if proc.returncode != 0 and "already exists" not in (proc.stderr + proc.stdout):
            raise RuntimeError(f"gh label create 失敗：{proc.stderr}")

    def create_issue(self, title: str, body: str) -> int:
        proc = subprocess.run(
            ["gh", "issue", "create", "--label", ISSUE_LABEL, "--title", title, "--body", body],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if proc.returncode != 0:
            raise RuntimeError(f"gh issue create 失敗：{proc.stderr}")
        m = re.search(r"/issues/(\d+)", proc.stdout)
        if not m:
            # issue 已建立但取不到編號：中止（下輪 marker 冪等 skip，不會重複開）
            raise RuntimeError(f"gh issue create 成功但無法解析 issue 編號：{proc.stdout!r}")
        return int(m.group(1))

    def add_comment(self, number: int, body: str) -> None:
        proc = subprocess.run(
            ["gh", "issue", "comment", str(number), "--body", body],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if proc.returncode != 0:
            raise RuntimeError(f"gh issue comment 失敗：{proc.stderr.strip()}")

    def update_body(self, number: int, body: str) -> None:
        proc = subprocess.run(
            ["gh", "issue", "edit", str(number), "--body", body],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if proc.returncode != 0:
            raise RuntimeError(f"gh issue edit 失敗：{proc.stderr.strip()}")


def index_issues(issues: list[dict]) -> dict[tuple[str, str], dict]:
    """open issue 清單 → {(類型, workshop_id): {number, hash}}。"""
    index: dict[tuple[str, str], dict] = {}
    for issue in issues:
        parsed = parse_marker(issue.get("body", ""))
        if parsed:
            issue_type, wid, content_hash = parsed
            index[(issue_type, wid)] = {"number": issue["number"], "hash": content_hash}
    return index


def apply_issue_plan(
    plan: dict, index: dict[tuple[str, str], dict], gh, *, dry_run: bool
) -> str:
    """依 (類型,id) 索引決定 skip / comment / new。回傳實際動作。"""
    ident = (plan["type"], plan["workshop_id"])
    existing = index.get(ident)
    if existing is None:
        action = "new"
    elif existing["hash"] == plan["content_hash"]:
        action = "skip"  # 同 (類型,id) 同 hash → 無事
    else:
        action = "comment"  # 同 (類型,id) 新 hash → 追加 comment + 更新 body
    if dry_run:
        return action
    if action == "new":
        number = gh.create_issue(plan["title"], plan["body"])
        index[ident] = {"number": number, "hash": plan["content_hash"]}
    elif action == "comment":
        assert existing is not None  # action==comment 僅在索引命中時成立
        # comment→edit 非原子：edit 失敗時下輪會重複 comment（有界：每日至多一則、
        # edit 成功即止）。對調順序則變成「靜默丟 comment」，取捨選噪音不選丟信息
        gh.add_comment(existing["number"], plan["comment"])
        gh.update_body(existing["number"], plan["body"])
        index[ident] = {"number": existing["number"], "hash": plan["content_hash"]}
    return action


# ============================================================
# git state commit（fetch → rebase → push；只對可 rebase 解的拒絕重試）
# ============================================================
GitRunner = Callable[[list[str]], tuple[int, str, str]]


def _real_git(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(["git", *args], capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    return proc.returncode, proc.stdout, proc.stderr


COMMIT_OK = "committed"
COMMIT_NOCHANGE = "nochange"
COMMIT_FAILED = "failed"


def _is_non_fast_forward(stderr: str) -> bool:
    """只認可靠 rebase 重推解決的拒絕；裸 'rejected' 太寬（protected branch 等
    不可恢復拒絕會被無效重試 3 次），刻意不收。"""
    s = stderr.lower()
    return "non-fast-forward" in s or "fetch first" in s


def commit_state_with_retry(
    add_paths: list[str],
    message: str,
    *,
    branch: str | None = None,
    max_retries: int = 3,
    git: GitRunner = _real_git,
    sleep: Callable[[float], None] = time.sleep,
) -> str:
    if branch is None:
        branch = os.environ.get("TRACKER_BRANCH") or "main"
    rc, _out, err = git(["add", *add_paths])
    if rc != 0:
        print(f"  ⚠️ git add 失敗：{err.strip()}", file=sys.stderr)
        return COMMIT_FAILED
    rc, _out, _err = git(["diff", "--cached", "--quiet"])
    if rc == 0:
        return COMMIT_NOCHANGE
    rc, _out, err = git(["commit", "-m", message])
    if rc != 0:
        print(f"  ⚠️ git commit 失敗：{err.strip()}", file=sys.stderr)
        return COMMIT_FAILED
    for attempt in range(max_retries + 1):
        rc, _out, err = git(["fetch", "origin", branch])
        if rc != 0:
            print(f"  ⚠️ git fetch 失敗：{err.strip()}", file=sys.stderr)
            return COMMIT_FAILED
        rc, _out, err = git(["rebase", f"origin/{branch}"])
        if rc != 0:
            print(f"  ⚠️ git rebase 失敗，abort 復原：{err.strip()}", file=sys.stderr)
            git(["rebase", "--abort"])
            return COMMIT_FAILED
        prc, _po, perr = git(["push", "origin", f"HEAD:{branch}"])
        if prc == 0:
            return COMMIT_OK
        if not _is_non_fast_forward(perr):
            print(f"  ⚠️ git push 失敗（非 non-fast-forward，不重試）：{perr.strip()}", file=sys.stderr)
            return COMMIT_FAILED
        if attempt < max_retries:
            sleep(1.0 + random.uniform(0.0, 0.5))
    print("  ⚠️ git push 重試耗盡仍為 non-fast-forward。", file=sys.stderr)
    return COMMIT_FAILED


# ============================================================
# 主流程
# ============================================================
def ci_baseline_guard(*, bootstrap: bool = False) -> bool:
    """CI（TRACKER_CI=1）缺 baseline fail-fast。回傳 True＝通過。"""
    if bootstrap or os.environ.get("TRACKER_CI") != "1":
        return True
    missing = [p.name for p in (STATE_JSON, MAPDATA_JSON) if not p.exists()]
    if missing:
        print(
            f"❌ CI baseline 缺失（{ '、'.join(missing) }）。須先於本機執行 "
            "`run --bootstrap` 與 `hash-baseline` 建立並 commit。",
            file=sys.stderr,
        )
        return False
    return True


def collect() -> dict:
    """共用前段：state → 收藏 → details → classify → plans（check 與 run 共用）。"""
    state = load_json(STATE_JSON) if STATE_JSON.exists() else {"items": {}}
    old_items = state.get("items", {})

    print("🔎 查詢支援地圖收藏…")
    children = fetch_collection_children()
    # 已標記下架的項目：記錄保留（tombstone）、每日追蹤不再查詢。
    # 重新上架要恢復追蹤＝把 state 該項 removed 改回 false（或刪該 entry）
    skipped_removed = [wid for wid in children if old_items.get(wid, {}).get("removed")]
    if skipped_removed:
        print(f"  ℹ️ 已下架、不查詢：{', '.join(skipped_removed)}")
    query_ids = [wid for wid in children if wid not in skipped_removed]
    details = fetch_details(query_ids)

    # creator 缺失（下架項目不回 creator）→ 當作外人保留追蹤：第三方地圖要下架 issue；
    # 自家項目誤中只是可關閉的噪音，方向刻意 fail-open
    map_ids = [
        wid for wid in query_ids
        if details.get(wid, {}).get("creator") != OWN_CREATOR
    ]
    print(f"  收藏 {len(children)} 項 → 追蹤地圖 {len(map_ids)} 項"
          f"（排除自家 {len(query_ids) - len(map_ids)} 項、已下架 {len(skipped_removed)} 項）")
    if len(map_ids) < 10:
        print("❌ 追蹤地圖項目 < 10（疑似 API 異常或收藏被清空），中止。", file=sys.stderr)
        sys.exit(1)
    coverage_guard(map_ids, details)

    dropped = sorted(set(old_items) - set(map_ids) - set(skipped_removed))
    if dropped:
        print(f"  ℹ️ 本輪不在收藏（基準保留、暫停查詢）：{', '.join(dropped)}")
    plans, meta, baselined = classify(map_ids, details, old_items)
    plans.sort(key=lambda p: (p["type"], int(p["workshop_id"])))
    print(f"  計畫：更新 {sum(1 for p in plans if p['type'] == TYPE_UPDATE)} 筆、"
          f"下架 {sum(1 for p in plans if p['type'] == TYPE_REMOVED)} 筆、新基準 {baselined} 筆")
    for plan in plans:
        print(f"    - {plan['title']}")
    # 首見且非下架的 id → diff job 建圖資基準（零 issue）
    baseline_new = [w for w in meta if w not in old_items and not meta[w].get("removed")]
    return {"plans": plans, "meta": meta, "baseline_new": baseline_new}


def cmd_run(args) -> int:
    if not ci_baseline_guard(bootstrap=args.bootstrap):
        return 1
    data = collect()
    if args.dry_run:
        print("✅ dry-run 完成（零 issue、state 未寫入；圖資判定由 CI diff job 執行）。")
        return 0
    if args.bootstrap:
        state = load_json(STATE_JSON) if STATE_JSON.exists() else {"items": {}}
        # state＝附加式帳本：merge、永不 prune——收藏瞬時異常（誤刪/API 抖動）不毀基準
        new_items = {**state.get("items", {}), **data["meta"]}
        dead = sorted(wid for wid, e in new_items.items() if e.get("removed"))
        if dead:
            print(f"  ⚠️ 基準內含已下架項目（收藏仍列但 Workshop 已無法存取）：{', '.join(dead)}")
        out = {"items": new_items, "generated_at": now_iso()}
        if state.get("game"):
            out["game"] = state["game"]
        write_json(STATE_JSON, out)
        print(f"✅ bootstrap 完成：基準 {len(new_items)} 項寫入 {STATE_JSON.relative_to(PROJECT_ROOT)}"
              "（零 issue；請 commit 該檔）。")
        return 0
    print("ℹ️ 本機真跑請走 CI（check → diff → issue），或依序執行三個子命令。", file=sys.stderr)
    return 2


def cmd_check(args) -> int:
    if not ci_baseline_guard():
        return 1
    data = collect()
    write_json(Path(args.out), data)
    print(f"✅ check 完成 → {args.out}")
    return 0


def cmd_diff(args) -> int:
    data = load_json(Path(args.infile))
    update_ids = [p["workshop_id"] for p in data.get("plans", []) if p.get("type") == TYPE_UPDATE]
    todo = list(dict.fromkeys(update_ids + data.get("baseline_new", [])))
    baseline = load_json(MAPDATA_JSON) if MAPDATA_JSON.exists() else {"items": {}}
    verdicts: dict[str, dict] = {}
    new_hashes: dict[str, dict] = {}
    for wid in todo:
        if not str(wid).isdigit():  # artifact 防禦：id 必為數字才進 argv
            print(f"::warning::非法 workshop id（{wid!r}），略過")
            continue
        print(f"  ⬇️ steamcmd 下載 {wid}…", flush=True)
        root = steamcmd_download(args.steamcmd, str(wid))
        if root is None:
            verdicts[wid] = {"status": "unknown", "note": "steamcmd 下載失敗",
                             "changed_maps": [], "bounds_changed": {}}
            print("    下載失敗（本輪以無法判定處理，基準不推進）")
            continue
        new = hash_mod_mapdata(root)
        verdicts[wid] = build_verdict(baseline.get("items", {}).get(wid), new)
        new_hashes[wid] = new
        print(f"    判定：{verdicts[wid]['status']}"
              + (f"（{ '、'.join(verdicts[wid]['changed_maps']) }）" if verdicts[wid]["changed_maps"] else ""))
    game_build = fetch_game_build(args.steamcmd)
    if game_build is None:
        print("::warning::取得遊戲 buildid 失敗（本輪略過遊戲軸，下輪再試）")
    data["verdicts"] = verdicts
    data["new_hashes"] = new_hashes
    data["game_build"] = game_build
    write_json(Path(args.out), data)
    print(f"✅ diff 完成：判定 {len(verdicts)} 項、遊戲 build {game_build or '（未知）'} → {args.out}")
    return 0


def cmd_issue(args) -> int:
    data = load_json(Path(args.infile))
    plans = list(data.get("plans", []))
    verdicts = data.get("verdicts", {})
    meta = data.get("meta", {})

    state = load_json(STATE_JSON) if STATE_JSON.exists() else {"items": {}}
    old_items = state.get("items", {})
    old_game = state.get("game") or {}

    # 遊戲軸：build 變更 → plan；首見（無基準）靜默記錄
    game_state = old_game
    new_build = data.get("game_build")
    if new_build:
        prev_build = old_game.get("build")
        if prev_build and prev_build != new_build:
            plans.append(build_game_plan(prev_build, new_build))
        if prev_build != new_build:
            game_state = {"build": new_build, "detected_at": now_iso()}

    # MOD 軸 update plan 附加圖資判定段
    for plan in plans:
        if plan.get("type") == TYPE_UPDATE:
            v = verdicts.get(plan["workshop_id"])
            if v:
                plan["body"] = plan["body"] + "\n" + "\n".join(verdict_section(v))

    gh = GhClient()
    gh.ensure_label()
    index = index_issues(gh.list_tracker_issues())
    for plan in plans:
        action = apply_issue_plan(plan, index, gh, dry_run=False)
        print(f"    {action}: {plan['title']}")

    # 持久化：timestamps merge＋game；mapdata 只推進成功判定子集（下載失敗者保留舊基準）
    new_items = {**old_items, **meta}
    mapdata = load_json(MAPDATA_JSON) if MAPDATA_JSON.exists() else {"items": {}}
    md_items = {**mapdata.get("items", {}), **data.get("new_hashes", {})}

    paths: list[str] = []
    if new_items != old_items or game_state != old_game:
        out = {"items": new_items, "generated_at": now_iso()}
        if game_state:
            out["game"] = game_state
        write_json(STATE_JSON, out)
        paths.append(str(STATE_JSON.relative_to(PROJECT_ROOT)).replace("\\", "/"))
    if md_items != mapdata.get("items", {}):
        write_json(MAPDATA_JSON, {"items": md_items, "generated_at": now_iso()})
        paths.append(str(MAPDATA_JSON.relative_to(PROJECT_ROOT)).replace("\\", "/"))
    if not paths:
        print("✅ 完成（state 無變更、不 commit——排程停用風險見 workflow 註解）。")
        return 0
    if os.environ.get("TRACKER_CI") == "1":
        status = commit_state_with_retry(
            paths,
            f"chore(tracker): 地圖追蹤 state 更新（{datetime.now(timezone.utc):%Y-%m-%d}）",
        )
        print(f"  state commit: {status}")
        if status == COMMIT_FAILED:
            return 1
    else:
        print("  ℹ️ 本機模式：state 已寫入，請自行 commit。")
    print("✅ 完成。")
    return 0


def cmd_hash_baseline(args) -> int:
    """本機建圖資基準：對 state 內全部追蹤項 hash 圖資寫 MAPDATA_JSON
    （內容請先自行 steamcmd 批次下載）。給 --client-root 時同時比對 Steam 客戶端
    副本，報告 drift（渲染來源過期偵測）。"""
    state = load_json(STATE_JSON)
    wids = [w for w, e in sorted(state.get("items", {}).items()) if not e.get("removed")]
    client_root = Path(args.client_root) if args.client_root else None
    items: dict[str, dict] = {}
    drift: list[tuple[str, dict]] = []
    missing: list[str] = []
    for i, wid in enumerate(wids, 1):
        root = find_workshop_item(args.steamcmd, wid)
        if root is None:
            # steamcmd 無副本 → 退用客戶端副本（基準仍可建，但無 drift 比對意義）
            root = client_root / wid if client_root and (client_root / wid).is_dir() else None
        if root is None:
            missing.append(wid)
            print(f"  ⚠️ [{i}/{len(wids)}] {wid} 無本機副本，跳過")
            continue
        new = hash_mod_mapdata(root)
        items[wid] = new
        if client_root and str(root).startswith(str(Path(args.steamcmd).resolve().parent)):
            c = client_root / wid
            if c.is_dir():
                v = build_verdict(hash_mod_mapdata(c), new)
                if v["status"] != "none":
                    drift.append((wid, v))
        print(f"  [{i}/{len(wids)}] {wid} maps={len(new['maps'])}")
    write_json(MAPDATA_JSON, {"items": items, "generated_at": now_iso()})
    print(f"✅ 基準寫入 {MAPDATA_JSON.relative_to(PROJECT_ROOT)}：{len(items)}/{len(wids)} 項"
          + (f"（缺 {', '.join(missing)}）" if missing else ""))
    if drift:
        print("⚠️ steamcmd 新副本與客戶端副本不一致（該圖渲染來源可能過期，建議 --prefer 重渲）：")
        for wid, v in drift:
            print(f"  {wid}: {v['status']} {'、'.join(v['changed_maps'])}")
    return 0 if not missing else 1


# ============================================================
# self-test（零網路、零 gh、零 git：注入假物件驗證核心邏輯）
# ============================================================
class _FakeGh:
    def __init__(self):
        self.created: list[str] = []
        self.comments: list[tuple[int, str]] = []
        self.edited: list[int] = []
        self._next = 100

    def create_issue(self, title, body):
        self.created.append(title)
        self._next += 1
        return self._next

    def add_comment(self, number, body):
        self.comments.append((number, body))

    def update_body(self, number, body):
        self.edited.append(number)


def cmd_self_test() -> int:
    import tempfile

    # 1) marker roundtrip＋注入中和
    marker = make_marker(TYPE_UPDATE, "111", "abc")
    assert parse_marker(f"{marker}\nbody") == (TYPE_UPDATE, "111", "abc")
    evil = neutralize("t --> <!-- map-tracker:type=removed;id=999;hash=x -->")
    assert parse_marker(f"{make_marker(TYPE_UPDATE, '111', 'abc')}\n{evil}") == (TYPE_UPDATE, "111", "abc")
    assert parse_marker(evil) is None

    # 2) classify：首見基準 / 變更 / 下架（首偵測才開）/ 重新上架
    details = {
        "1": {"result": 1, "time_updated": 100, "title": "A"},
        "2": {"result": 1, "time_updated": 200, "title": "B"},
        "3": {"result": 9},
        "4": {"result": 1, "time_updated": 400, "title": "D"},
    }
    state = {
        "2": {"time_updated": 150, "title": "B"},
        "3": {"time_updated": 300, "title": "C"},
        "4": {"time_updated": 400, "title": "D", "removed": True, "removed_at": "x"},
    }
    plans, meta, baselined = classify(["1", "2", "3", "4"], details, state)
    assert baselined == 1 and meta["1"]["time_updated"] == 100  # 首見靜默基準
    types = {(p["type"], p["workshop_id"]) for p in plans}
    assert types == {(TYPE_UPDATE, "2"), (TYPE_REMOVED, "3")}
    assert meta["3"]["removed"] and meta["3"]["removed_at"]
    assert not meta["4"]["removed"] and meta["4"]["removed_at"] is None  # 重新上架自動恢復
    # 已標記下架者再次 result=9 → 不再開新 plan
    plans2, _meta2, _ = classify(["3"], {"3": {"result": 9}}, {"3": dict(meta["3"])})
    assert plans2 == []
    # 首見＋查無回應 → 不入 state（下輪仍視為首見，避免假「更新」issue）
    plans3, meta3, base3 = classify(["5"], {}, {})
    assert plans3 == [] and meta3 == {} and base3 == 0
    # result=1 但 time_updated 缺失/無效 → 不推進；首見不入 state、既有基準不污染
    plans4, meta4, _ = classify(["6"], {"6": {"result": 1, "title": "F"}}, {})
    assert plans4 == [] and meta4 == {}
    plans5, meta5, _ = classify(
        ["2"], {"2": {"result": 1, "title": "B"}}, {"2": {"time_updated": 150, "title": "B"}}
    )
    assert plans5 == [] and meta5["2"]["time_updated"] == 150

    # 3) apply_issue_plan：new / skip / comment
    gh = _FakeGh()
    plan = build_update_plan("2", "B", 150, 200)
    index: dict = {}
    assert apply_issue_plan(plan, index, gh, dry_run=False) == "new"
    assert apply_issue_plan(plan, index, gh, dry_run=False) == "skip"
    plan_newer = build_update_plan("2", "B", 200, 250)
    assert apply_issue_plan(plan_newer, index, gh, dry_run=False) == "comment"
    assert len(gh.created) == 1 and len(gh.comments) == 1

    # 4) coverage_guard：全空中止
    try:
        coverage_guard(["1"], {})
        raise AssertionError("coverage_guard 未中止")
    except SystemExit:
        pass

    # 5) commit_state_with_retry：無變更 / non-fast-forward 重試後成功
    def git_nochange(args):
        return (0, "", "")  # add ok；diff --cached --quiet rc=0 → 無變更

    assert commit_state_with_retry(["x"], "m", git=git_nochange, sleep=lambda _s: None) == COMMIT_NOCHANGE

    pushes = {"n": 0}

    def git_race(args):
        if args[0] == "diff":
            return (1, "", "")  # 有 staged 變更
        if args[0] == "push":
            pushes["n"] += 1
            return (1, "", "rejected (fetch first)") if pushes["n"] == 1 else (0, "", "")
        return (0, "", "")

    assert commit_state_with_retry(["x"], "m", git=git_race, sleep=lambda _s: None) == COMMIT_OK
    assert pushes["n"] == 2
    # 不可恢復拒絕（protected branch 等）不得誤判為可重試
    assert not _is_non_fast_forward("! [rejected] protected branch hook declined")

    # 6) 圖資 hash：檔案過濾、bounds 推導、變更/免重渲/材質/無基準判定
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        mp = root / "42" / "media" / "maps" / "TestTown"
        mp.mkdir(parents=True)
        (mp / "10_20.lotheader").write_bytes(b"H1")
        (mp / "10_20.lotpack").write_bytes(b"P1")
        (mp / "11_20.lotheader").write_bytes(b"H2")
        (mp / "spawnpoints.lua").write_bytes(b"L1")  # 非圖資：不參與 hash
        tp = root / "42" / "media" / "texturepacks"
        tp.mkdir(parents=True)
        (tp / "x.pack").write_bytes(b"T1")
        base = hash_mod_mapdata(root)
        assert set(base["maps"]) == {"TestTown"}
        assert base["maps"]["TestTown"]["bounds"] == [2560, 5120, 3072, 5376]
        # 改 .lua → 免重渲；改 .lotpack → maps；改 .pack → assets；無基準 → no_baseline
        (mp / "spawnpoints.lua").write_bytes(b"L2")
        assert build_verdict(base, hash_mod_mapdata(root))["status"] == "none"
        (mp / "10_20.lotpack").write_bytes(b"P2")
        v = build_verdict(base, hash_mod_mapdata(root))
        assert v["status"] == "maps" and v["changed_maps"] == ["TestTown"] and not v["bounds_changed"]
        (tp / "x.pack").write_bytes(b"T2")
        assert build_verdict(base, hash_mod_mapdata(root))["status"] == "assets"
        assert build_verdict(None, base)["status"] == "no_baseline"
        # bounds 變動偵測：新增 cell
        (mp / "12_20.lotheader").write_bytes(b"H3")
        v2 = build_verdict(base, hash_mod_mapdata(root))
        assert v2["bounds_changed"]["TestTown"][1] == [2560, 5120, 3328, 5376]

    # 7) verdict_section：惡意 mapDir 不得偽造 marker；游戲 plan hash 冪等
    evil_v = {"status": "maps", "changed_maps": ["X --> <!-- map-tracker:type=game;id=1;hash=z -->"],
              "bounds_changed": {}}
    body = "\n".join([make_marker(TYPE_UPDATE, "7", "h7"), *verdict_section(evil_v)])
    assert parse_marker(body) == (TYPE_UPDATE, "7", "h7")
    g1, g2 = build_game_plan("1", "2"), build_game_plan("9", "2")
    assert g1["content_hash"] == g2["content_hash"]  # 只綁新 build → 冪等

    print("✅ self-test 全數通過")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="本機：dry-run 印計畫 / bootstrap 首建 timestamps 基準")
    run.add_argument("--dry-run", action="store_true", help="只印計畫，零 issue、不寫 state")
    run.add_argument("--bootstrap", action="store_true", help="首建基準：寫 state、零 issue")
    check = sub.add_parser("check", help="CI：查時間戳＋分類 → changed.json")
    check.add_argument("--out", required=True)
    diff = sub.add_parser("diff", help="CI：steamcmd 下載變更項＋圖資 hash 判定＋遊戲 buildid")
    diff.add_argument("--in", dest="infile", required=True)
    diff.add_argument("--out", required=True)
    diff.add_argument("--steamcmd", required=True)
    issue = sub.add_parser("issue", help="CI：冪等開/更 issue＋commit state")
    issue.add_argument("--in", dest="infile", required=True)
    hb = sub.add_parser("hash-baseline", help="本機：對全部追蹤項建圖資基準（先 steamcmd 下載）")
    hb.add_argument("--steamcmd", required=True)
    hb.add_argument("--client-root", default="", help="Steam 客戶端 workshop content 根（供 drift 比對）")
    sub.add_parser("self-test", help="零網路自我測試")
    args = parser.parse_args()
    dispatch = {
        "run": cmd_run,
        "check": cmd_check,
        "diff": cmd_diff,
        "issue": cmd_issue,
        "hash-baseline": cmd_hash_baseline,
    }
    if args.cmd == "self-test":
        sys.exit(cmd_self_test())
    sys.exit(dispatch[args.cmd](args))


if __name__ == "__main__":
    main()
