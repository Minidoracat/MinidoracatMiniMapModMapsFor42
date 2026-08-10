#!/usr/bin/env python3
"""支援地圖更新追蹤器（每日排程；邏輯沿用 MinidoracatModLangFor42 scripts/tracker.py 精簡而來）。

watchlist＝Steam「支援地圖收藏」3766382352（發現來源，發版流程本來就會維護），
排除自家項目（creator=OWN_CREATOR 者）；state 是附加式帳本（merge、永不 prune），
收藏瞬時異常不會毀基準。比對 time_updated：
  變動 → 冪等開/更「[地圖更新]」issue（提醒重渲染 pyramid）
  下架（API result=9）→ 開「[地圖下架]」issue 一次；自下輪起不再查詢（tombstone 保留），
    重新上架要恢復追蹤＝手動把 state 該項 removed 改回 false
  首次見到（含 --bootstrap 首建）→ 靜默記基準，零 issue
state（tracker-state/timestamps.json）進版控；gh 任一步失敗即中止、state 不推進，
下一輪由 issue body marker 冪等自癒（不會重複開）。

用法：
  python scripts/map_tracker.py run [--dry-run] [--bootstrap]
  python scripts/map_tracker.py self-test
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

COLLECTION_ID = "3766382352"  # 支援地圖收藏（含全部地圖 MOD＋自家系列 MOD）
# Minidoracat 的 steamID64：排除收藏內自家項目用。寫死而非查本包 detail 推導——
# 否則本包被隱藏/暫下架時追蹤器天天死（自傷 kill switch）。日後多帳號改 set 即可。
OWN_CREATOR = "76561198033176898"

COLLECTION_API = "https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/"
DETAILS_API = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
RESULT_OK = 1
RESULT_NOT_FOUND = 9  # 已下架 / 隱藏 / 無效 ID

# issue 冪等：單一共通 label + body 首個 HTML marker（只認第一個，防上游字串偽造）
ISSUE_LABEL = "tracker"
TYPE_UPDATE = "update"
TYPE_REMOVED = "removed"
_MARKER_RE = re.compile(
    r"<!--\s*map-tracker:type=(?P<type>[^;]+);id=(?P<id>[^;]+);hash=(?P<hash>[^;\s]+)\s*-->"
)


def make_marker(issue_type: str, workshop_id: str, content_hash: str) -> str:
    return f"<!-- map-tracker:type={issue_type};id={workshop_id};hash={content_hash} -->"


def parse_marker(body: str) -> tuple[str, str, str] | None:
    m = _MARKER_RE.search(body)
    return (m["type"], m["id"], m["hash"]) if m else None


def neutralize(text: str) -> str:
    """中和上游字串（地圖標題等）：HTML comment 邊界（防偽 marker）＋換行摺疊
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
        "**處置**（地圖內容有變才需要；純說明頁／小修可直接關閉）：",
        "",
        "- [ ] pzmap Studio 重新渲染該地圖（「遊戲內小地圖」模式）→ pyramid.zip 放入 `media/minimap/`",
        "- [ ] 渲染輸出 `pyramid.txt` 的 bounds 若變動，同步 `MinidoracatMiniMapModMaps.lua`",
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
        "**處置確認**：",
        "",
        "- 圖像與註冊**預設保留**（既有訂閱者仍可用；未啟用該地圖 MOD 的玩家不受影響）。",
        "- 自下輪起本項目**停止每日查詢**（記錄保留於 tracker-state）；確認處置後關閉本 issue，",
        "  並將該地圖補進 README「已下架地圖」表。",
        "- 若日後重新上架：把 `tracker-state/timestamps.json` 該項 `removed` 改回 `false` 即恢復追蹤。",
        "- 若確認永久移除且要清理：自 `media/minimap/` 移除 pyramid、刪 Lua 註冊與翻譯鍵，",
        f"  並自[支援地圖收藏](https://steamcommunity.com/sharedfiles/filedetails/?id={COLLECTION_ID})移除該項目。",
    ])
    return {
        "type": TYPE_REMOVED,
        "workshop_id": wid,
        "content_hash": content_hash,
        "title": f"[地圖下架] {label} 已無法存取（{wid}）",
        "body": body,
        "comment": "追蹤器再次確認此項目仍不可存取。",
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
                "--description", "地圖更新追蹤器自動 issue（地圖更新/下架）",
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
# git state commit（fetch → rebase → push；只對 non-fast-forward 重試）
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
def cmd_run(args) -> int:
    if (
        os.environ.get("TRACKER_CI") == "1"
        and not args.bootstrap
        and not STATE_JSON.exists()
    ):
        print(
            "❌ CI baseline 缺失（tracker-state/timestamps.json）。"
            "須先於本機 `python scripts/map_tracker.py run --bootstrap` 建立並 commit。",
            file=sys.stderr,
        )
        return 1

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
        return 1
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

    # state＝附加式帳本：merge、永不 prune——收藏瞬時異常（誤刪/API 抖動）不毀基準
    new_items = {**old_items, **meta}

    if args.dry_run:
        print("✅ dry-run 完成（零 issue、state 未寫入）。")
        return 0

    if args.bootstrap:
        dead = sorted(wid for wid, e in new_items.items() if e.get("removed"))
        if dead:
            print(f"  ⚠️ 基準內含已下架項目（收藏仍列但 Workshop 已無法存取）：{', '.join(dead)}")
        write_json(STATE_JSON, {"items": new_items, "generated_at": now_iso()})
        print(f"✅ bootstrap 完成：基準 {len(new_items)} 項寫入 {STATE_JSON.relative_to(PROJECT_ROOT)}"
              "（零 issue；請 commit 該檔）。")
        return 0

    gh = GhClient()
    gh.ensure_label()
    index = index_issues(gh.list_tracker_issues())
    for plan in plans:
        action = apply_issue_plan(plan, index, gh, dry_run=False)
        print(f"    {action}: {plan['title']}")

    if new_items == old_items:
        print("✅ 完成（state 無變更、不 commit——排程停用風險見 workflow 註解）。")
        return 0
    write_json(STATE_JSON, {"items": new_items, "generated_at": now_iso()})
    if os.environ.get("TRACKER_CI") == "1":
        status = commit_state_with_retry(
            [str(STATE_JSON.relative_to(PROJECT_ROOT)).replace("\\", "/")],
            f"chore(tracker): 地圖追蹤 state 更新（{datetime.now(timezone.utc):%Y-%m-%d}）",
        )
        print(f"  state commit: {status}")
        if status == COMMIT_FAILED:
            return 1
    else:
        print("  ℹ️ 本機模式：state 已寫入，請自行 commit。")
    print("✅ 完成。")
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

    print("✅ self-test 全數通過")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="查收藏＋比對 time_updated＋開/更 issue")
    run.add_argument("--dry-run", action="store_true", help="只印計畫，零 issue、不寫 state")
    run.add_argument("--bootstrap", action="store_true", help="首建基準：寫 state、零 issue")
    sub.add_parser("self-test", help="零網路自我測試")
    args = parser.parse_args()
    if args.cmd == "run":
        sys.exit(cmd_run(args))
    sys.exit(cmd_self_test())


if __name__ == "__main__":
    main()
