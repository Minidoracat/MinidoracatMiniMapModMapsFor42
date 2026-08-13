#!/usr/bin/env python3
"""支援地圖更新追蹤器（每日排程；架構沿用 MinidoracatModLangFor42 scripts/tracker.py）。

watchlist＝Steam「支援地圖收藏」3766382352（發現來源，發版流程本來就會維護），
排除自家項目（creator=OWN_CREATOR 者）；state 是附加式帳本（merge、永不 prune），
收藏瞬時異常不會毀基準。兩軸偵測：

MOD 軸（time_updated 變動）→ steamcmd 下載該項 → hash 圖資（media/maps/ 的
  .lotheader/.lotpack/.bin＋mod 自帶 texturepack/.tiles）→ 與基準比對 →
  issue 直接標「需重渲（哪些 mapDir、bounds 是否變動）」或「免重渲（僅腳本/loot）」。
  材質包軸（同一條 MOD 軸，watchlist 多一組來源）：收藏只含地圖 MOD，地圖 require= 的
  tile pack 不在其中——材質包單獨更新時原本零 issue、圖靜默停在舊材質（2026-08-12
  Tikitown＋Drazion's Tilepack 同批更新實案）。清單由本機 `deps-scan` 由註冊表推導成
  tracker-state/tile_deps.json（進版控），命中者 issue 改標「需重渲受影響地圖（N 張）」。
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
  deps-scan [--prefer <dir>]
                      掃註冊地圖的材質包依賴 → tile_deps.json（新增/移除地圖後要重跑）
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
TILEDEPS_JSON = PROJECT_ROOT / "tracker-state" / "tile_deps.json"

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


def warn(msg: str) -> None:
    """GitHub Actions annotation（浮上 run summary）；本機與 self-test 退化為純文字，
    免得自測的故意觸發案例在 CI 變成 run 註記雜訊。"""
    on_ci = os.environ.get("GITHUB_ACTIONS") == "true" and not os.environ.get("TRACKER_SELF_TEST")
    print(f"::warning::{msg}" if on_ci else f"  ⚠️ {msg}")


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
        warn(f"Steam API 有效回應缺 {total - got}/{total} 筆（缺項 state 不推進，下輪重試）")
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


_VERSION_DIR_RE = re.compile(r"^42(\.\d+)*$")  # B42 版本資料夾：42、42.0、42.13…


def _mod_content_bases(root: Path) -> list[Path]:
    """B42 有效內容基底。mods/<name>/ 有 42* 版本資料夾 → 只取 42*＋common
    （排除 B41 根層副本——雙版本 mod 的根層 media/maps 是 B41 資料，混入會造成
    假「需重渲」與錯誤 bounds）；無版本資料夾 → 取該 mod 根。無 mods/ 佈局時
    以同一規則套用在 item 根（防禦性退路）。"""
    def bases_for(mod: Path) -> list[Path]:
        vers = sorted(d for d in mod.iterdir() if d.is_dir() and _VERSION_DIR_RE.match(d.name))
        if not vers:
            return [mod]
        common = mod / "common"
        return vers + ([common] if common.is_dir() else [])

    mods_dirs = sorted(d for d in root.glob("mods/*") if d.is_dir())
    if not mods_dirs:
        return bases_for(root)
    out: list[Path] = []
    for mod in mods_dirs:
        out += bases_for(mod)
    return out


def hash_mod_mapdata(root: Path) -> dict:
    """workshop item 根目錄 → {"maps": {mapDir: {"hash", "bounds"}}, "assets": <hash>}。
    只掃 B42 有效內容基底的 media/maps/（錨定固定路徑，不用啟發式找 "maps" 片段——
    上游資料夾名恰為 maps 時啟發式會讓整包圖資隱形）；maps 只含 RENDER_EXTS
    （cell 圖資，僅靜態 hash、絕不執行）；bounds 由 lotheader 檔名 cell 座標推
    （×256、右/下排他，同 Lua 註冊表約定）。路徑以基底為相對根（版本資料夾改名
    不影響 hash）。"""
    per_map: dict[str, list] = {}
    cells: dict[str, list] = {}
    assets: list = []
    for base in _mod_content_bases(root):
        maps_dir = base / "media" / "maps"
        if maps_dir.is_dir():
            for d in sorted(p for p in maps_dir.iterdir() if p.is_dir()):
                for f in sorted(d.rglob("*")):
                    if not f.is_file() or f.suffix.lower() not in RENDER_EXTS:
                        continue
                    rel = f.relative_to(base).as_posix().lower()
                    per_map.setdefault(d.name, []).append((rel, _file_sha256(f)))
                    m = _CELL_RE.match(f.name)
                    if m:
                        cells.setdefault(d.name, []).append((int(m.group(1)), int(m.group(2))))
        for f in sorted(base.rglob("*")):
            if f.is_file() and f.suffix.lower() in ASSET_EXTS:
                assets.append((f.relative_to(base).as_posix().lower(), _file_sha256(f)))
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
        if ob != nb:  # 含 None 側：新增/移除/無法解析的轉移也要浮出，不可靜默
            bounds_changed[d] = [ob, nb]
    if old.get("assets") != new["assets"]:
        status = "assets"
    elif changed:
        status = "maps"
    else:
        status = "none"
    return {"status": status, "changed_maps": changed, "bounds_changed": bounds_changed}


def verdict_section(verdict: dict | None, *, tilepack_used_by: list | None = None) -> list[str]:
    """issue body 的「圖資判定」段（mapDir 名屬上游可控字串 → neutralize＋code span）。
    tilepack_used_by 給定時＝材質包 issue：判定改以「受影響地圖」表述（材質包自己沒有
    media/maps，套用地圖用語會變成沒有地圖的「全部地圖」空指示）。"""
    if verdict is None:
        return []
    lines = ["", "### 圖資判定（自動）", ""]
    status = verdict.get("status")
    if tilepack_used_by is not None:
        # zip 名來自本 repo 註冊表（非上游），仍統一 neutralize：與地圖路徑同一防注入紀律
        zips = "、".join(f"`{neutralize(str(u.get('zip', '')))}`" for u in tilepack_used_by)
        if status == "none":
            lines.append("- ✅ **免重渲**：本次更新未動材質／tiles（僅腳本、說明等）。"
                         "若下方無「尚未處置的先前判定」即可關閉本 issue。")
        elif status == "no_baseline":
            lines.append(f"- ⚠️ **無基準（本次已建立）**：無法比對，建議重渲以保險 → {zips}")
        elif status in ("maps", "assets"):
            lines.append(f"- 🔴 **需重渲受影響地圖（{len(tilepack_used_by)} 張）**："
                         f"材質包內容變更 → {zips}")
        else:
            note = neutralize(str(verdict.get("note", "")))
            lines.append(f"- ⚠️ **無法判定**：{note}——請依 Workshop 更新紀錄人工判斷。")
        return lines
    names = "、".join(f"`{neutralize(str(d))}`" for d in verdict.get("changed_maps", []))
    if status == "none":
        lines.append("- ✅ **免重渲**：本次更新未動地圖圖資／材質（僅腳本、loot 等）。"
                     "若下方無「尚未處置的先前判定」即可關閉本 issue。")
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
        ob = pair[0] if pair[0] else "（無法解析）"
        nb = pair[1] if pair[1] else "（無法解析）"
        lines.append(f"- ⚠️ bounds 變動 `{neutralize(str(d))}`：{ob} → {nb}（**記得同步 Lua 註冊表**）")
    return lines


_CARRY_LINE_RE = re.compile(r"^- (🔴|⚠️ bounds 變動)")


def finalize_update_plan(plan: dict, verdict: dict | None, prev_body: str = "") -> dict:
    """圖資判定併入 update plan。content_hash 綁 (tu, status, carry 集合)——
    判定從 unknown 解決、或 carry 集合變動時 hash 變 → comment 路徑會更新 body。
    carry＝既有 open issue body 內的 🔴/bounds 行（未處置的先前判定）：後續
    「免重渲」增量不得覆寫掉還沒做的重渲工作，關閉 issue 才清空。"""
    if verdict is None:
        return plan
    status = verdict.get("status", "unknown")
    # 材質包 plan 帶 used_by → 判定段改用「受影響地圖」表述（見 verdict_section）
    section = verdict_section(verdict, tilepack_used_by=plan.get("tilepack_used_by"))
    current = {ln for ln in section if _CARRY_LINE_RE.match(ln)}
    carried = sorted(
        ln for ln in prev_body.split("\n")
        if _CARRY_LINE_RE.match(ln) and ln not in current
    )
    new_hash = hashlib.sha256(
        f"update|{plan['workshop_id']}|{plan['new_tu']}|{status}|{'|'.join(carried)}".encode("utf-8")
    ).hexdigest()
    lines = plan["body"].split("\n")
    lines[0] = make_marker(TYPE_UPDATE, plan["workshop_id"], new_hash)
    body_lines = lines + section
    if carried:
        body_lines += ["", "### 尚未處置的先前判定（處理完成後關閉本 issue）", "", *carried]
    comment = plan["comment"] + f"（圖資判定：{status}" + (
        f"；另有 {len(carried)} 項先前判定未處置）" if carried else "）")
    return {**plan, "content_hash": new_hash, "body": "\n".join(body_lines), "comment": comment}


def apply_verdict_state(old_items: dict, meta: dict, verdicts: dict) -> dict:
    """unknown 判定（下載/hash 失敗）→ 撤回該項 timestamp 推進，明日 classify 重新
    偵測到同一更新 → diff 重試（否則 unknown 成終局、失敗項永不重試）。
    首見＋失敗 → 整項撤回（下輪仍視為首見）。"""
    out = dict(meta)
    for wid, v in verdicts.items():
        if v.get("status") != "unknown":
            continue
        if wid not in old_items:
            out.pop(wid, None)
        elif wid in out:
            out[wid] = {**out[wid], "time_updated": old_items[wid].get("time_updated")}
    return out


# ============================================================
# 材質包依賴（地圖 require= 的 tile pack）
# ============================================================
def _workshop_id_of(root: Path) -> str | None:
    """mod 根目錄（<content>/108600/<wid>/mods/<name>）→ workshop id；認不出回 None。
    錨定 appid 的下一層而非固定往上數幾層——同一 mod 可能來自
    `<wid>/mods/<name>` 或 `<wid>/mods/<name>/42` 兩種深度。"""
    for parent in root.parents:
        if parent.name.isdigit() and parent.parent.name == GAME_APPID:
            return parent.name
    return None


def build_tile_deps(
    entries: list[dict], idx: dict, requires: dict
) -> tuple[dict[str, dict], list[str], list[str]]:
    """註冊表 entries＋workshop 索引 →
    ({tile pack workshop id: {mod_ids, used_by}}, 本機找不到的 zip, 推不出 workshop id 的依賴)。

    追蹤範圍刻意等同「渲染時實際餵給 pzmap 的 --mod 集合」（rebuild_pyramids 的
    deps 解析同一份 requires/idx），追蹤器與渲染器才不會對「什麼會影響輸出」有兩套看法。
    同一 Workshop 項目內的 mod 不另外追蹤（本體更新時本來就會偵測到）。
    純函式、不碰檔案系統：workshop id 由路徑推導，故 self-test 可直接餵假 Path。"""
    items: dict[str, dict] = {}
    seen_zip: set[str] = set()
    unresolved: list[str] = []
    unlocatable: set[str] = set()
    for entry in entries:
        zip_name = entry["zip"]
        if zip_name in seen_zip:
            continue
        root = idx.get(entry["mapMod"])
        if root is None:
            # alias 條目（互斥變體共用同 zip）：換用同 zip 其他 mapMod 再試，同 rebuild_pyramids
            alt = next(
                (x for x in entries if x["zip"] == zip_name and idx.get(x["mapMod"])), None
            )
            if alt is None:
                # 本機沒有該地圖副本 → 它的材質包依賴這輪看不到。必須浮上來：
                # 靜默略過會讓 tile_deps.json 在缺副本的機器上「掃出較少項目」而砍掉追蹤覆蓋
                unresolved.append(zip_name)
                seen_zip.add(zip_name)
                continue
            entry, root = alt, idx[alt["mapMod"]]
        seen_zip.add(zip_name)
        map_wid = _workshop_id_of(root)
        for dep_mod in requires.get(entry["mapMod"], []):
            dep_root = idx.get(dep_mod)
            if dep_root is None or dep_root == root:
                continue
            dep_wid = _workshop_id_of(dep_root)
            if dep_wid is None:
                # 依賴存在於本機但不在 workshop 佈局下（手動安裝／--prefer 指到怪路徑）：
                # 無 workshop id 就無法追蹤，但靜默略過＝清單無聲少一項，必須回報
                unlocatable.add(dep_mod)
                continue
            if dep_wid == map_wid:
                continue
            item = items.setdefault(dep_wid, {"mod_ids": [], "used_by": []})
            if dep_mod not in item["mod_ids"]:
                item["mod_ids"].append(dep_mod)
            item["used_by"].append(
                {"zip": zip_name, "map_mod": entry["mapMod"], "workshop_id": map_wid or ""}
            )
    # 排序穩定化：掃描順序不得造成 state 假 diff（每日 commit 噪音）
    for item in items.values():
        item["mod_ids"].sort()
        item["used_by"].sort(key=lambda u: (u["zip"], u["map_mod"]))
    return items, sorted(unresolved), sorted(unlocatable)


def load_tile_deps() -> dict[str, dict]:
    """壞檔/讀不到一律降級為「無材質包追蹤」而非拋出：材質包軸是加值，不該讓一個
    壞掉的附屬 state 檔把整個地圖追蹤軸一起打死（warn 會浮上 CI run summary）。"""
    if not TILEDEPS_JSON.exists():
        return {}
    try:
        items = load_json(TILEDEPS_JSON).get("items", {})
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        warn(f"tile_deps.json 無法解析（{exc}）——本輪材質包不追蹤，地圖軸照常")
        return {}
    return items if isinstance(items, dict) else {}


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


def steamcmd_download(exe: str, wid: str, *, retries: int = 1, timeout: float = 900.0) -> Path | None:
    """下載單一 Workshop 項目，回傳內容根目錄；失敗回 None（單項失敗不拖垮整輪）。
    逾時/exe 異常皆吞為 None——CI runner 是拋棄式 VM，逾時遺留的孤兒 steamcmd
    隨 job 結束消滅，不做 process-group 清理。"""
    for _attempt in range(retries + 1):
        try:
            rc, out = steamcmd_run(exe, ["+workshop_download_item", GAME_APPID, wid],
                                   timeout=timeout)
        except (subprocess.TimeoutExpired, OSError):
            time.sleep(5)  # 逾時後殘留行程可能還握著鎖，稍候再試
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
    map_ids: list[str], details: dict[str, dict], state_items: dict,
    *, tilepack_deps: dict[str, dict] | None = None,
) -> tuple[list[dict], dict[str, dict], int]:
    """回傳 (issue plans, 每 id 的新 state entry, 本輪新基準數)。
    首次見到的 id（不在 state）一律靜默記基準、零 issue——--bootstrap 首建與日後
    收藏新增地圖走同一條路。
    tilepack_deps＝{材質包 workshop id: {mod_ids, used_by}}：命中的 id 改走材質包
    plan（時間戳追蹤邏輯完全相同，只有 issue 用語與處置不同）。不給＝行為與原本一致。"""
    plans: list[dict] = []
    meta: dict[str, dict] = {}
    baselined = 0
    for wid in map_ids:
        used_by = (tilepack_deps or {}).get(wid, {}).get("used_by")
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
                plans.append(build_removed_plan(wid, title, tilepack_used_by=used_by))
            entry["removed"] = True
            entry["removed_at"] = entry["removed_at"] or now_iso()
            if first_seen:
                baselined += 1
            continue
        if result != RESULT_OK:
            warn(f"非預期 Steam API result={result}（id={wid}），本輪略過")
            if first_seen:
                meta.pop(wid)  # 無有效基準可記，下輪仍視為首見
            continue
        new_tu = detail.get("time_updated")
        if not isinstance(new_tu, int) or new_tu <= 0:
            # result=1 但欄位缺失/無效：不得以 0 入庫（會造成假更新 issue 反覆震盪）
            warn(f"time_updated 無效（id={wid}），本輪略過")
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
            plans.append(build_update_plan(wid, title, old_tu, new_tu, tilepack_used_by=used_by))
    return plans, meta, baselined


def _affected_lines(used_by: list) -> list[str]:
    """材質包 issue 的「受影響地圖」清單（zip 名＋該地圖 Workshop 連結）。"""
    lines = [f"**受影響地圖（{len(used_by)} 張）**：", ""]
    for u in used_by:
        zip_name = neutralize(str(u.get("zip", "")))
        map_wid = str(u.get("workshop_id", ""))
        link = (f"（[Workshop {map_wid}]"
                f"(https://steamcommunity.com/sharedfiles/filedetails/?id={map_wid})）"
                if map_wid.isdigit() else "")
        lines.append(f"- `{zip_name}`{link}")
    return lines


def build_update_plan(wid: str, title: str, old_tu, new_tu: int,
                      *, tilepack_used_by: list | None = None) -> dict:
    """地圖更新 plan；tilepack_used_by 給定時改產「材質包更新」plan（受影響地圖需重渲）。"""
    label = neutralize(title)
    content_hash = hashlib.sha256(f"update|{wid}|{new_tu}".encode("utf-8")).hexdigest()
    common = [
        f"- 上次記錄：{fmt_ts(old_tu)}",
        f"- 本次更新：{fmt_ts(new_tu)}",
        f"- [Workshop 頁面](https://steamcommunity.com/sharedfiles/filedetails/?id={wid})"
        f"｜[更新紀錄](https://steamcommunity.com/sharedfiles/filedetails/changelog/{wid})",
        "",
    ]
    if tilepack_used_by is not None:
        head = [
            f"## 材質包更新：`{label}`（Workshop {wid}）",
            "",
            "追蹤器偵測到**地圖所依賴的材質包**發布了新版本。材質包內容直接影響貼圖渲染結果，",
            "依賴它的地圖必須在**同步新版材質包之後**重渲，否則會拿舊材質渲出錯誤圖磚",
            "（外觀正常但內容過期，靜態驗證抓不到）。",
            "",
            *common,
            *_affected_lines(tilepack_used_by),
            "",
            "**處置**（見下方自動判定；免重渲可直接關閉）：",
            "",
            f"- [ ] 先同步材質包新版：`steamcmd +workshop_download_item {GAME_APPID} {wid}`",
            "- [ ] 再重渲受影響地圖："
            "`python scripts/rebuild_pyramids.py --prefer <steamcmd content 根> --only <zip名>`",
            "- [ ] `python scripts/verify_mod.py` 通過後照常發版",
        ]
        issue_title = f"[材質包更新] {label}（{wid}）"
    else:
        head = [
            f"## 地圖更新：`{label}`（Workshop {wid}）",
            "",
            "追蹤器偵測到上游地圖 MOD 發布了新版本：",
            "",
            *common,
            "**處置**（見下方自動圖資判定；免重渲可直接關閉）：",
            "",
            "- [ ] pzmap Studio 或 `scripts/rebuild_pyramids.py --only <zip名>` 重渲該地圖",
            "- [ ] bounds 若變動，同步 `MinidoracatMiniMapModMaps.lua`",
            "- [ ] 地圖名稱／`mapDir` 若變動，同步 Lua 註冊與 `Translate/*/UI.json`",
            "- [ ] `python scripts/verify_mod.py` 通過後照常發版",
        ]
        issue_title = f"[地圖更新] {label}（{wid}）"
    plan = {
        "type": TYPE_UPDATE,
        "workshop_id": wid,
        "content_hash": content_hash,
        "new_tu": new_tu,
        "title": issue_title,
        "body": "\n".join([make_marker(TYPE_UPDATE, wid, content_hash), *head]),
        "comment": f"追蹤器偵測到再次更新：{fmt_ts(new_tu)}（上次記錄 {fmt_ts(old_tu)}）。",
    }
    if tilepack_used_by is not None:
        # 隨 artifact 過到 diff/issue job：判定段要靠它切換用語（見 finalize_update_plan）
        plan["tilepack_used_by"] = tilepack_used_by
    return plan


def build_removed_plan(wid: str, title: str, *, tilepack_used_by: list | None = None) -> dict:
    """地圖下架 plan；tilepack_used_by 給定時改產「材質包下架」plan——處置完全不同：
    材質包下架不必刪任何註冊（已渲圖像不受影響），但受影響地圖從此無法忠實重渲。"""
    label = neutralize(title)
    content_hash = hashlib.sha256(f"removed|{wid}".encode("utf-8")).hexdigest()
    if tilepack_used_by is not None:
        head = [
            f"## 材質包下架：`{label}`（Workshop {wid}）",
            "",
            "每日檢查發現**地圖所依賴的材質包**已無法存取（Steam API result=9）。",
            "**已渲好的 pyramid 圖像不受影響**（圖像是成品，不會回頭讀材質包），",
            "但受影響地圖自此無法再忠實重渲——上游地圖日後更新時會渲不出正確貼圖。",
            "",
            *_affected_lines(tilepack_used_by),
            "",
            "**處置**：",
            "",
            "- [ ] 保留現有 pyramid zip 與註冊條目（**不要**比照地圖下架去刪）",
            "- [ ] 保留一份材質包本機副本備援（本機 workshop 目錄若還在，勿清）",
            "- [ ] 受影響地圖日後若更新：評估用備援副本重渲，或該圖轉為停止追新",
            "- 自下輪起本項目**停止每日查詢**（記錄保留於 tracker-state）；處置完關閉本 issue 即可。",
        ]
        issue_title = f"[材質包下架] {label} 已無法存取（{wid}）"
    else:
        head = [
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
        ]
        issue_title = f"[地圖下架] {label} 已無法存取（{wid}）"
    return {
        "type": TYPE_REMOVED,
        "workshop_id": wid,
        "content_hash": content_hash,
        "title": issue_title,
        "body": "\n".join([make_marker(TYPE_REMOVED, wid, content_hash), *head]),
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
    """open issue 清單 → {(類型, workshop_id): {number, hash, body}}。
    body 供 finalize_update_plan 萃取未處置的先前判定（carry）。"""
    index: dict[tuple[str, str], dict] = {}
    for issue in issues:
        parsed = parse_marker(issue.get("body", ""))
        if parsed:
            issue_type, wid, content_hash = parsed
            index[(issue_type, wid)] = {
                "number": issue["number"], "hash": content_hash, "body": issue.get("body", ""),
            }
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
        # --autostash：CI checkout 可能因行尾正規化出現幻影未暫存變更（實案：workshop.txt
        # CRLF blob），不能讓它擋掉 state commit；拋棄式 runner 上 autostash 無副作用
        rc, _out, err = git(["rebase", "--autostash", f"origin/{branch}"])
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
    # 材質包軸：收藏只含地圖 MOD，地圖 require= 的 tile pack 不在其中——材質包單獨更新
    # （地圖沒動）追蹤器原本完全看不見，圖會靜默停在舊材質。清單由本機 deps-scan 產出。
    tile_deps = load_tile_deps()
    if not tile_deps:
        warn("tile_deps.json 缺失或為空——地圖依賴的材質包未納入追蹤"
             "（本機跑 `python scripts/map_tracker.py deps-scan` 重建並 commit）")
    # 已標記下架的項目：記錄保留（tombstone）、每日追蹤不再查詢。
    # 重新上架要恢復追蹤＝把 state 該項 removed 改回 false（或刪該 entry）
    tracked = list(children) + [w for w in sorted(tile_deps) if w not in children]
    skipped_removed = [wid for wid in tracked if old_items.get(wid, {}).get("removed")]
    if skipped_removed:
        print(f"  ℹ️ 已下架、不查詢：{', '.join(skipped_removed)}")
    query_ids = [wid for wid in children if wid not in skipped_removed]
    tile_ids = [wid for wid in tracked if wid not in children and wid not in skipped_removed]
    details = fetch_details(query_ids + tile_ids)

    # creator 缺失（下架項目不回 creator）→ 當作外人保留追蹤：第三方地圖要下架 issue；
    # 自家項目誤中只是可關閉的噪音，方向刻意 fail-open
    map_ids = [
        wid for wid in query_ids
        if details.get(wid, {}).get("creator") != OWN_CREATOR
    ]
    print(f"  收藏 {len(children)} 項 → 追蹤地圖 {len(map_ids)} 項"
          f"（排除自家 {len(query_ids) - len(map_ids)} 項、已下架 {len(skipped_removed)} 項）"
          f"＋材質包 {len(tile_ids)} 項")
    # < 10 的健全性檢查只看地圖：材質包數量本來就少，混入會讓收藏被清空的異常漏網
    if len(map_ids) < 10:
        print("❌ 追蹤地圖項目 < 10（疑似 API 異常或收藏被清空），中止。", file=sys.stderr)
        sys.exit(1)
    track_ids = map_ids + tile_ids
    coverage_guard(track_ids, details)

    dropped = sorted(set(old_items) - set(track_ids) - set(skipped_removed))
    if dropped:
        print(f"  ℹ️ 本輪不在收藏（基準保留、暫停查詢）：{', '.join(dropped)}")
    # 同時是收藏內地圖、又被別的地圖當材質包依賴的項目：一律以「地圖」語意開單——
    # 地圖處置（重渲該圖＋bounds/翻譯同步）是必要的，材質包用語會把它整段換掉。
    # 目前無實例；出現時 warn 提醒人工確認其他受影響地圖也要一起重渲。
    both = sorted(set(tile_deps) & set(map_ids))
    if both:
        warn(f"下列項目同時是收錄地圖與材質包依賴，以地圖語意開單："
             f"{', '.join(both)}——請一併確認依賴它的其他地圖是否要重渲")
    plans, meta, baselined = classify(
        track_ids, details, old_items,
        tilepack_deps={k: v for k, v in tile_deps.items() if k not in set(map_ids)},
    )
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


ARTIFACT_SCHEMA = 3  # check→diff→issue 的 artifact 契約版本；不符即 fail-closed
# v3：update plan 可帶 tilepack_used_by（材質包 issue 的受影響地圖清單）


def _schema_guard(data: dict, stage: str) -> bool:
    if data.get("schema") != ARTIFACT_SCHEMA:
        print(f"❌ {stage}：artifact schema {data.get('schema')!r} != {ARTIFACT_SCHEMA}"
              "（producer/consumer 版本錯配，中止）。", file=sys.stderr)
        return False
    return True


def cmd_check(args) -> int:
    if not ci_baseline_guard():
        return 1
    data = collect()
    data["schema"] = ARTIFACT_SCHEMA
    data["source_sha"] = os.environ.get("GITHUB_SHA", "")
    write_json(Path(args.out), data)
    print(f"✅ check 完成 → {args.out}")
    return 0


def cmd_diff(args) -> int:
    data = load_json(Path(args.infile))
    if not _schema_guard(data, "diff"):
        return 1
    # 遊戲軸先跑：不受後面 MOD 項目吃光時間預算影響
    game_build = fetch_game_build(args.steamcmd)
    if game_build is None:
        warn("取得遊戲 buildid 失敗（本輪略過遊戲軸，下輪再試）")

    update_ids = [p["workshop_id"] for p in data.get("plans", []) if p.get("type") == TYPE_UPDATE]
    todo = list(dict.fromkeys(update_ids + data.get("baseline_new", [])))
    random.shuffle(todo)  # 每輪隨機序：單一慢項不會永久餓死其他項（unknown 明日重試）
    baseline = load_json(MAPDATA_JSON) if MAPDATA_JSON.exists() else {"items": {}}
    # 全域時間預算：單項最壞 2×420s，預算擋在 job 30 分鐘上限之前——
    # 超支項目以 unknown 收場（timestamp 會被 issue 階段撤回，明日重試），
    # artifact 仍產出、其他項目與 issue job 不陪葬
    deadline = time.monotonic() + float(os.environ.get("TRACKER_DIFF_BUDGET", "1200"))
    verdicts: dict[str, dict] = {}
    new_hashes: dict[str, dict] = {}
    for wid in todo:
        if not str(wid).isdigit():  # artifact 防禦：id 必為數字才進 argv
            warn(f"非法 workshop id（{wid!r}），略過")
            continue
        if time.monotonic() > deadline:
            verdicts[wid] = {"status": "unknown", "note": "時間預算用盡（明日重試）",
                             "changed_maps": [], "bounds_changed": {}}
            print(f"  ⏱️ {wid} 時間預算用盡，本輪略過")
            continue
        print(f"  ⬇️ steamcmd 下載 {wid}…", flush=True)
        try:
            root = steamcmd_download(args.steamcmd, str(wid), timeout=420.0)
            new = hash_mod_mapdata(root) if root is not None else None
        except OSError as exc:  # 單項壞檔/IO 例外隔離，不拖垮其他項與遊戲軸
            root, new = None, None
            warn(f"處理 {wid} 例外：{exc}")
        if new is None:
            verdicts[wid] = {"status": "unknown", "note": "steamcmd 下載/讀取失敗",
                             "changed_maps": [], "bounds_changed": {}}
            print("    下載失敗（本輪以無法判定處理，timestamp 將撤回、明日重試）")
            continue
        verdicts[wid] = build_verdict(baseline.get("items", {}).get(wid), new)
        new_hashes[wid] = new
        print(f"    判定：{verdicts[wid]['status']}"
              + (f"（{ '、'.join(verdicts[wid]['changed_maps']) }）" if verdicts[wid]["changed_maps"] else ""))
    data["verdicts"] = verdicts
    data["new_hashes"] = new_hashes
    data["game_build"] = game_build
    write_json(Path(args.out), data)
    print(f"✅ diff 完成：判定 {len(verdicts)} 項、遊戲 build {game_build or '（未知）'} → {args.out}")
    return 0


def cmd_issue(args) -> int:
    data = load_json(Path(args.infile))
    if not _schema_guard(data, "issue"):
        return 1
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

    # MOD 軸：unknown 撤回 timestamp 推進（明日重試）
    meta = apply_verdict_state(old_items, meta, verdicts)

    gh = GhClient()
    gh.ensure_label()
    index = index_issues(gh.list_tracker_issues())
    # 判定併入 plan（hash 綁 verdict＋carry；prev_body 供未處置判定累積）
    plans = [
        finalize_update_plan(
            p, verdicts.get(p["workshop_id"]),
            index.get((TYPE_UPDATE, p["workshop_id"]), {}).get("body", ""),
        ) if p.get("type") == TYPE_UPDATE else p
        for p in plans
    ]
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


def cmd_deps_scan(args) -> int:
    """本機：由 Lua 註冊表＋本機 workshop 副本推導各地圖的材質包依賴 → tile_deps.json。

    須在有完整 workshop 副本的渲染機執行（依賴解析與 rebuild_pyramids 共用同一份
    idx/requires，追蹤範圍才等同實際餵給 pzmap 的 --mod 集合）。有地圖無法定位時
    以非零碼結束且**不寫檔**——缺副本的機器掃出來的清單會少項，覆寫進版控等於
    無聲砍掉追蹤覆蓋。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import rebuild_pyramids as rp  # 延後匯入：CI 的 check/diff/issue 用不到

    entries = rp.parse_registrations(rp.LUA.read_text(encoding="utf-8"))
    idx, requires = rp.index_workshop([Path(p) for p in args.prefer])
    items, unresolved, unlocatable = build_tile_deps(entries, idx, requires)
    if unlocatable:
        # 不擋寫檔（可能是刻意的手動安裝 mod），但必須讓人看見少了哪些追蹤
        warn(f"{len(unlocatable)} 個依賴推不出 workshop id、未納入追蹤："
             f"{', '.join(unlocatable)}（本機副本不在 workshop 佈局下？）")
    if unresolved:
        print(f"❌ {len(unresolved)} 張註冊地圖在本機找不到 workshop 副本，不寫檔"
              "（清單會少項，覆寫等於砍掉追蹤覆蓋）：", file=sys.stderr)
        for z in unresolved:
            print(f"     {z}", file=sys.stderr)
        print("   訂閱／steamcmd 下載缺項後重跑，或用 --prefer 指向含該副本的 content 根。",
              file=sys.stderr)
        return 1

    old = load_tile_deps()
    added = sorted(set(items) - set(old))
    gone = sorted(set(old) - set(items))
    total_maps = len({u["zip"] for it in items.values() for u in it["used_by"]})
    if items == old and TILEDEPS_JSON.exists():
        # 內容沒變就不重寫：generated_at 每跑必動會製造只有時間戳的假 diff
        #（同 issue job「state 無變更不 commit」的紀律）
        print(f"✅ 材質包依賴無變更（{len(items)} 個材質包、覆蓋 {total_maps} 張地圖），不重寫檔案。")
        return 0
    write_json(TILEDEPS_JSON, {"items": items, "generated_at": now_iso()})
    print(f"✅ 材質包依賴寫入 {TILEDEPS_JSON.relative_to(PROJECT_ROOT)}："
          f"{len(items)} 個材質包、覆蓋 {total_maps} 張地圖")
    for wid in sorted(items):
        it = items[wid]
        print(f"   {wid}  {'／'.join(it['mod_ids'])}  ← {len(it['used_by'])} 張")
    if added:
        print(f"   ➕ 新增追蹤：{', '.join(added)}")
    if gone:
        # 地圖移除支援或上游改依賴都會走到這裡；state 帳本本身永不 prune，只是不再查詢
        print(f"   ➖ 不再依賴（timestamps 基準保留、停止查詢）：{', '.join(gone)}")
    print("   請 commit tracker-state/tile_deps.json。")
    return 0


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

    os.environ["TRACKER_SELF_TEST"] = "1"

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

    # 6) 圖資 hash：真實 workshop 佈局、檔案過濾、bounds 推導、B41 排除、判定分支
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        mp = root / "mods" / "TestMod" / "42" / "media" / "maps" / "TestTown"
        mp.mkdir(parents=True)
        (mp / "10_20.lotheader").write_bytes(b"H1")
        (mp / "10_20.lotpack").write_bytes(b"P1")
        (mp / "11_20.lotheader").write_bytes(b"H2")
        (mp / "spawnpoints.lua").write_bytes(b"L1")  # 非圖資：不參與 hash
        tp = root / "mods" / "TestMod" / "42" / "media" / "texturepacks"
        tp.mkdir(parents=True)
        (tp / "x.pack").write_bytes(b"T1")
        # B41 根層副本：有 42 版本資料夾時必須被排除（否則假需重渲＋錯誤 bounds）
        b41 = root / "mods" / "TestMod" / "media" / "maps" / "TestTown"
        b41.mkdir(parents=True)
        (b41 / "37_40.lotheader").write_bytes(b"OLD")
        base = hash_mod_mapdata(root)
        assert set(base["maps"]) == {"TestTown"}
        assert base["maps"]["TestTown"]["bounds"] == [2560, 5120, 3072, 5376]  # 無 B41 cell 混入
        (b41 / "37_40.lotheader").write_bytes(b"OLD2")  # B41-only 變更 → 免重渲
        assert build_verdict(base, hash_mod_mapdata(root))["status"] == "none"
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
        # mapDir 移除 → bounds 轉移含 None 側也要浮出
        cur = hash_mod_mapdata(root)
        v3 = build_verdict(cur, {"maps": {}, "assets": cur["assets"]})
        assert v3["changed_maps"] == ["TestTown"] and v3["bounds_changed"]["TestTown"][1] is None
    # mod 資料夾名恰為 maps（啟發式錨定的地雷佈局）→ 圖資仍須被看見
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        trap = root / "mods" / "maps" / "42" / "media" / "maps" / "RealTown"
        trap.mkdir(parents=True)
        (trap / "5_5.lotpack").write_bytes(b"X1")
        assert set(hash_mod_mapdata(root)["maps"]) == {"RealTown"}
    # 無版本資料夾的 mod → 根層內容即 B42 有效內容
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        flat = root / "mods" / "FlatMod" / "media" / "maps" / "FlatTown"
        flat.mkdir(parents=True)
        (flat / "1_1.lotheader").write_bytes(b"F1")
        assert set(hash_mod_mapdata(root)["maps"]) == {"FlatTown"}

    # 8) 管線契約：unknown 撤回 timestamp／首見失敗撤回整項／成功推進
    old_items = {"2": {"time_updated": 150, "title": "B"}}
    meta8 = {"2": {"time_updated": 200, "title": "B"}, "9": {"time_updated": 50, "title": "N"}}
    vd = {"2": {"status": "unknown"}, "9": {"status": "unknown"}}
    adj = apply_verdict_state(old_items, meta8, vd)
    assert adj["2"]["time_updated"] == 150 and "9" not in adj  # 撤回＝明日重試
    adj_ok = apply_verdict_state(old_items, meta8, {"2": {"status": "maps"}})
    assert adj_ok["2"]["time_updated"] == 200  # 成功判定照常推進

    # 9) 判定解決/carry 驅動 body 更新：unknown→maps 換 hash（comment），
    #    後續免重渲不得吞掉未處置的需重渲（carry 進 body 且 hash 再變）
    gh2 = _FakeGh()
    idx2: dict = {}
    p_unknown = finalize_update_plan(
        build_update_plan("8", "M", 100, 200),
        {"status": "unknown", "note": "x", "changed_maps": [], "bounds_changed": {}},
    )
    assert apply_issue_plan(p_unknown, idx2, gh2, dry_run=False) == "new"
    idx2[(TYPE_UPDATE, "8")]["body"] = p_unknown["body"]  # FakeGh 不存 body，測試自補
    p_maps = finalize_update_plan(
        build_update_plan("8", "M", 100, 200),
        {"status": "maps", "changed_maps": ["X"], "bounds_changed": {}},
        idx2[(TYPE_UPDATE, "8")]["body"],
    )
    assert p_maps["content_hash"] != p_unknown["content_hash"]
    assert apply_issue_plan(p_maps, idx2, gh2, dry_run=False) == "comment"  # body 更新為需重渲
    idx2[(TYPE_UPDATE, "8")]["body"] = p_maps["body"]
    p_none = finalize_update_plan(
        build_update_plan("8", "M", 200, 300),
        {"status": "none", "changed_maps": [], "bounds_changed": {}},
        idx2[(TYPE_UPDATE, "8")]["body"],
    )
    assert "🔴" in p_none["body"] and "尚未處置的先前判定" in p_none["body"]  # carry 保留需重渲
    assert apply_issue_plan(p_none, idx2, gh2, dry_run=False) == "comment"
    assert parse_marker(p_none["body"]) == (TYPE_UPDATE, "8", p_none["content_hash"])

    # 7) verdict_section：惡意 mapDir 不得偽造 marker；游戲 plan hash 冪等
    evil_v = {"status": "maps", "changed_maps": ["X --> <!-- map-tracker:type=game;id=1;hash=z -->"],
              "bounds_changed": {}}
    body = "\n".join([make_marker(TYPE_UPDATE, "7", "h7"), *verdict_section(evil_v)])
    assert parse_marker(body) == (TYPE_UPDATE, "7", "h7")
    g1, g2 = build_game_plan("1", "2"), build_game_plan("9", "2")
    assert g1["content_hash"] == g2["content_hash"]  # 只綁新 build → 冪等

    # 10) 材質包依賴：workshop id 推導、同項目內依賴不重複追蹤、alias 去重、缺副本要浮出
    def _root(wid, name):  # 假 workshop 佈局（純路徑推導，不碰檔案系統）
        return Path(f"D:/SteamLibrary/steamapps/workshop/content/{GAME_APPID}/{wid}/mods/{name}")

    assert _workshop_id_of(_root("3046728955", "Tiles")) == "3046728955"
    assert _workshop_id_of(_root("3046728955", "Tiles") / "42") == "3046728955"  # 深一層仍認得
    assert _workshop_id_of(Path("D:/elsewhere/mods/Tiles")) is None

    idx_t = {
        "tikitown": _root("3037854728", "Tikitown"),
        "tikitown_tiles": _root("3046728955", "Drazions Tile Pack"),
        "sibling": _root("3037854728", "TikitownPowerPlant"),  # 同一 Workshop 項目
        "chinatown": _root("3703704638", "Chinatown"),
        "shared_tiles": _root("2879745353", "Melos"),
        "local_only": Path("D:/custom/mods/Dep"),  # 非 workshop 佈局 → 推不出 id
    }
    req_t = {
        "tikitown": ["tikitown_tiles", "sibling", "missing_pack", "local_only"],
        "chinatown": ["shared_tiles"],
        "chinatown_variant": ["shared_tiles"],
    }
    entries_t = [
        {"zip": "Tikitown.pyramid.zip", "mapMod": "tikitown"},
        {"zip": "Chinatown.pyramid.zip", "mapMod": "chinatown"},
        # alias：同 zip 的互斥變體，只算一次（避免 used_by 重複計數）
        {"zip": "Chinatown.pyramid.zip", "mapMod": "chinatown_variant"},
        # 首個 mapMod 未安裝但 alias 可解析 → 仍要掃到依賴，且不得計入 unresolved
        {"zip": "Alias.pyramid.zip", "mapMod": "not_installed"},
        {"zip": "Alias.pyramid.zip", "mapMod": "chinatown"},
        {"zip": "Gone.pyramid.zip", "mapMod": "also_missing"},
    ]
    deps_t, unresolved_t, unlocatable_t = build_tile_deps(entries_t, idx_t, req_t)
    assert set(deps_t) == {"3046728955", "2879745353"}          # sibling 同項目 → 不追蹤
    assert "missing_pack" not in str(deps_t)                     # 本機沒有的依賴不入清單
    assert deps_t["3046728955"]["mod_ids"] == ["tikitown_tiles"]
    assert deps_t["3046728955"]["used_by"] == [
        {"zip": "Tikitown.pyramid.zip", "map_mod": "tikitown", "workshop_id": "3037854728"}
    ]
    assert [u["zip"] for u in deps_t["2879745353"]["used_by"]] == [
        "Alias.pyramid.zip", "Chinatown.pyramid.zip"]           # alias 各算一次、排序穩定
    assert unresolved_t == ["Gone.pyramid.zip"]                  # 缺副本必須浮出（不可靜默）
    assert unlocatable_t == ["local_only"]                       # 推不出 workshop id 也要浮出

    # 11) 材質包 issue：走 update/removed 同一條路但用語與處置不同；判定改「受影響地圖」
    used_by_t = deps_t["3046728955"]["used_by"]
    tp_plan = build_update_plan("3046728955", "Drazion's Tilepack", 100, 200,
                                tilepack_used_by=used_by_t)
    assert tp_plan["title"].startswith("[材質包更新]")
    assert "受影響地圖（1 張）" in tp_plan["body"] and "Tikitown.pyramid.zip" in tp_plan["body"]
    assert tp_plan["tilepack_used_by"] == used_by_t
    map_plan = build_update_plan("3037854728", "Tikitown", 100, 200)
    assert map_plan["title"].startswith("[地圖更新]") and "tilepack_used_by" not in map_plan
    tp_fin = finalize_update_plan(tp_plan, {"status": "assets", "changed_maps": [],
                                            "bounds_changed": {}})
    assert "需重渲受影響地圖（1 張）" in tp_fin["body"]
    # 材質包沒有 media/maps → changed_maps 恆空；套地圖用語會變成沒有地圖的空指示
    assert "該 MOD 全部地圖" not in tp_fin["body"]
    tp_none = finalize_update_plan(tp_plan, {"status": "none", "changed_maps": [],
                                             "bounds_changed": {}})
    assert "免重渲" in tp_none["body"] and "材質／tiles" in tp_none["body"]
    tp_rm = build_removed_plan("3046728955", "Drazion's Tilepack", tilepack_used_by=used_by_t)
    assert tp_rm["title"].startswith("[材質包下架]")
    assert "不要" in tp_rm["body"] and "刪 pyramid zip" not in tp_rm["body"]
    assert "刪 pyramid zip" in build_removed_plan("1", "M")["body"]  # 地圖下架處置不受影響

    # 12) classify 掛上材質包：時間戳邏輯不變，只有 plan 型態換人
    plans_t, meta_t, _ = classify(
        ["3037854728", "3046728955"],
        {"3037854728": {"result": 1, "time_updated": 200, "title": "Tikitown"},
         "3046728955": {"result": 1, "time_updated": 200, "title": "Tilepack"}},
        {"3037854728": {"time_updated": 100}, "3046728955": {"time_updated": 100}},
        tilepack_deps=deps_t,
    )
    kinds = {p["workshop_id"]: p["title"].split("]")[0] + "]" for p in plans_t}
    assert kinds == {"3037854728": "[地圖更新]", "3046728955": "[材質包更新]"}
    assert meta_t["3046728955"]["time_updated"] == 200
    # 不給 tilepack_deps → 與原本行為逐字相同（HIGH risk 迴歸護欄）
    plans_legacy, _, _ = classify(
        ["3046728955"], {"3046728955": {"result": 1, "time_updated": 200, "title": "Tilepack"}},
        {"3046728955": {"time_updated": 100}},
    )
    assert plans_legacy[0]["title"].startswith("[地圖更新]")
    # 惡意 zip 名（本 repo 可控，仍守同一防注入紀律）不得偽造 marker
    evil_used = [{"zip": "X --> <!-- map-tracker:type=game;id=1;hash=z -->", "workshop_id": "1"}]
    evil_plan = finalize_update_plan(
        build_update_plan("9", "T", 1, 2, tilepack_used_by=evil_used),
        {"status": "assets", "changed_maps": [], "bounds_changed": {}})
    assert parse_marker(evil_plan["body"]) == (TYPE_UPDATE, "9", evil_plan["content_hash"])

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
    ds = sub.add_parser("deps-scan", help="本機：掃地圖的材質包依賴 → tile_deps.json")
    ds.add_argument("--prefer", action="append", default=[],
                    help="優先索引的額外 workshop content 根目錄（例：steamcmd 下載處）")
    sub.add_parser("self-test", help="零網路自我測試")
    args = parser.parse_args()
    dispatch = {
        "run": cmd_run,
        "check": cmd_check,
        "diff": cmd_diff,
        "issue": cmd_issue,
        "hash-baseline": cmd_hash_baseline,
        "deps-scan": cmd_deps_scan,
    }
    if args.cmd == "self-test":
        sys.exit(cmd_self_test())
    sys.exit(dispatch[args.cmd](args))


if __name__ == "__main__":
    main()
