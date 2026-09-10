#!/usr/bin/env python3
"""地圖街名翻譯資料生成器：names.json → 街名索引 Lua 表 ＋ 四語 UI.json。

單一真相是 `street-names/<dataset-id>/names.json`。生成物（都進 git）：

  MOD/.../42/media/lua/shared/MinidoracatMiniMapModMapsStreetNames.lua
      全域表 `MinidoracatMiniMapModMapsStreetNames = { [dataset] = { [上游英文原街名] = UI 鍵 } }`
      註冊清單（MinidoracatMiniMapModMaps.lua）的 `streetNames` 欄位直接引用其中一格。
  MOD/.../42/media/lua/shared/Translate/{EN,CH,CN,JP}/UI.json
      UI 鍵 → 譯名（EN 槽＝英文原名）。非街名鍵原樣保留、不重排。

**為何是「純名稱」而不是替換語系 XML**：舊做法把上游 `streets.xml` 整份替換掉
（幾何＋名稱一起烘進 `media/minimapstreets/`），代價是一整套幾何契約——逐字節
幾何比對、矩形→中心線正規化、官方路網剔除清單（keep-scan）——而且上游任何幾何
變動都要重生一次。改成只提供「原名 → 翻譯鍵」的查表後：幾何永遠是上游原件（本包
不再碰），本包只負責文字，執行期由主 MOD 拿 `getText` 取譯名。沒有翻譯鍵的街名
（上游新增、我方尚未補譯）執行期原樣顯示，照樣可搜尋、可導航。

用法：
  python scripts/gen_streets_i18n.py gen [--prefer DIR] [--update-hash]
  python scripts/gen_streets_i18n.py verify
  python scripts/gen_streets_i18n.py --selftest

閘門：
  gen     fail-closed 於 names.json 結構錯誤（缺 `names`、空白鍵、未知語言欄位、
          正規化後撞鍵）。缺譯只是 warning——該語言退回英文原名，玩家看到的仍是
          可用的街名。
  verify  重跑同一支生成器、與磁碟上的生成物**逐字節**比對，再核對註冊清單引用的
          dataset 集合＝`street-names/` 實際內容 ⇒ 手改一定被抓到。

names.json 的鍵必須是上游 `streets.xml` 的**原字串**（逐字節，含連續空白）：執行期
是 `names[原名]` 精確查表（主 MOD `translateStreetName`），鍵差一個空白就查不到＝
該街顯示英文。

`--prefer` 與 map_tracker deps-scan 同語意：優先的 workshop content 根
（`<root>/<workshop_id>/mods/…`）。gen 只拿它做**非阻擋**的上游對照（照上述精確語意
列出未收錄街名、sha256 是否已變），生成物本身不依賴上游副本 ⇒ CI 無需 workshop。
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OWNER_MOD_ID = "MinidoracatMiniMapModMapsFor42"
# 與 rebuild_pyramids.WORKSHOP／map_tracker --prefer 預設同一 workshop content 根
DEFAULT_WORKSHOP = Path(r"D:\SteamLibrary\steamapps\workshop\content\108600")

_MOD_REL = Path("MOD") / OWNER_MOD_ID / "Contents" / "mods" / OWNER_MOD_ID
# 街名索引表：shared/ 先於 client/ 載入 ⇒ 註冊清單引用時全域表必已就緒。
# 檔名／全域名沿用既有的 MinidoracatMiniMapModMaps 前綴（**沒有** For42 尾綴，
# 與 mod id 不同名）——這兩個字串是與註冊清單、主 MOD 的接線契約，勿由 mod id 推導。
STREET_TABLE_GLOBAL = "MinidoracatMiniMapModMapsStreetNames"
STREET_TABLE_REL = (
    _MOD_REL / "42" / "media" / "lua" / "shared" / f"{STREET_TABLE_GLOBAL}.lua"
)
TRANSLATE_REL = _MOD_REL / "42" / "media" / "lua" / "shared" / "Translate"
REGISTRY_REL = (
    _MOD_REL / "42" / "media" / "lua" / "client" / "MinidoracatMiniMapModMaps.lua"
)

# UI 鍵前綴：本生成器獨佔這個命名空間，UI.json 內其餘鍵一概不碰
UI_KEY_PREFIX = "UI_MinidoracatMiniMapModMaps_Street_"
UI_LANGS = ("EN", "CH", "CN", "JP")
TR_LANGS = ("CH", "CN", "JP")
LANG_KEYS = {"CH": "ch", "CN": "cn", "JP": "jp"}
# 鍵指紋長度：40 bit，遠大於單一 dataset 的街名規模（實際最大 175 條）
_KEY_HASH_LEN = 10

_VERSION_DIR_RE = re.compile(r"^42(\.\d+)*$")
_STREET_NAME_RE = re.compile(r'<street\b[^>]*?\bname="([^"]*)"')
# 註冊清單引用形如 `streetNames = StreetNames["daisy-county"]`（別名由該檔自己宣告）
_REGISTRY_STREETNAMES_RE = re.compile(r'streetNames\s*=\s*[\w.]+\s*\[\s*"([^"]+)"\s*\]')
_REGISTRY_LEGACY_RE = re.compile(r"\bstreetI18n\b")


class Result(NamedTuple):
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


class Row(NamedTuple):
    """一條街名的生成資料。"""

    table_keys: tuple[str, ...]  # Lua 表鍵：原名，正規化後不同時再掛一個別名
    ui_key: str
    values: dict[str, str]  # lang -> UI.json 值（未做 % escape）


def warn(msg: str) -> None:
    on_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    print(f"::warning::{msg}" if on_ci else f"  ⚠️ {msg}")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_name(s: str) -> str:
    """多重空白折疊為單一空格＋trim（撞鍵偵測與別名鍵用；查表鍵一律原字串）。"""
    return " ".join(s.split())


# ============================================================
# 上游來源檔定位
# map_tracker streets-scan 匯入 iter_workshop_roots／find_streets_xml
# （另有 discover_names_files／read_names_json／file_sha256）⇒ 勿改這些簽名。
# gen_street_repairs 也共用來源定位、_lua_str、write_bytes_atomic、Result 與路徑常數。
# ============================================================
def iter_workshop_roots(prefer: list[str] | None) -> list[Path]:
    roots: list[Path] = []
    for raw in prefer or []:
        p = Path(raw)
        if p.is_dir():
            roots.append(p)
    if DEFAULT_WORKSHOP.is_dir():
        roots.append(DEFAULT_WORKSHOP)
    return roots


def find_streets_xml(
    roots: list[Path], workshop_id: str, map_dir: str
) -> Path | None:
    """`<root>/<workshop_id>/mods/*/{common,42*}/media/maps/<map_dir>/streets.xml`。

    版本目錄優先於 common（B42 專屬圖資勝出），首見為準。
    """
    if not workshop_id or not map_dir:
        return None
    for root in roots:
        base = root / workshop_id / "mods"
        if not base.is_dir():
            continue
        for mod_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            buckets = sorted(
                (p for p in mod_dir.iterdir() if p.is_dir()),
                key=lambda p: (0 if _VERSION_DIR_RE.match(p.name) else 1, p.name),
            )
            for bucket in buckets:
                cand = bucket / "media" / "maps" / map_dir / "streets.xml"
                if cand.is_file():
                    return cand
    return None


def upstream_names(xml_text: str) -> list[str]:
    """streets.xml → 依出現順序去重的 `<street name>` 原字串。

    只 unescape、**不正規化**：執行期是精確查表，把上游的髒名（連續空白）折疊後
    比對會讓它看起來「已收錄」，實際上執行期查不到。
    """
    names = map(html.unescape, _STREET_NAME_RE.findall(xml_text))
    return list(dict.fromkeys(name for name in names if name.strip()))


# ============================================================
# names.json
# ============================================================
def read_names_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_names_json(path: Path, data: dict) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def discover_names_files(
    street_names_dir: Path, dataset: str | None
) -> list[Path]:
    if dataset:
        p = street_names_dir / dataset / "names.json"
        return [p]
    if not street_names_dir.is_dir():
        return []
    return sorted(p for p in street_names_dir.glob("*/names.json") if p.is_file())


def _load_names_map(data: dict) -> tuple[dict[str, dict], list[str]]:
    """names.json → {上游原名: {ch,cn,jp}}。

    鍵保留**原樣**（不折疊空白）：Lua 表要用引擎索引裡的那個字串當鍵才查得到。
    正規化只用來偵測撞鍵——`Forest  St` 與 `Forest St` 同時存在＝資料有歧義，
    無法決定哪一條該拿哪個譯名，直接視為錯誤。
    """
    errors: list[str] = []
    raw = data.get("names")
    if not isinstance(raw, dict):
        return {}, ["names.json 缺少 names 物件"]
    out: dict[str, dict] = {}
    seen_norm: dict[str, str] = {}
    for key, val in raw.items():
        name = str(key)
        nk = normalize_name(name)
        if not nk:
            errors.append("names.json 有空白鍵")
            continue
        if nk in seen_norm:
            errors.append(
                f"names.json 空白折疊後撞鍵：{seen_norm[nk]!r} 與 {name!r}"
            )
            continue
        if not isinstance(val, dict):
            errors.append(f"names.json[{name!r}] 不是物件")
            continue
        unknown = sorted(set(val) - set(LANG_KEYS.values()))
        if unknown:
            # 手寫 JSON 的欄位錯字（zh／jap…）只會靜默少一語，故直接拒收
            errors.append(f"names.json[{name!r}] 有未知欄位：{unknown}")
            continue
        seen_norm[nk] = name
        out[name] = val
    return out, errors


def _field(entry: dict, lang: str) -> str | None:
    val = entry.get(LANG_KEYS[lang])
    if not isinstance(val, str):
        return None
    text = val.strip()
    return text or None


# ============================================================
# 生成
# ============================================================
def street_ui_key(dataset_id: str, name: str) -> str:
    """UI 翻譯鍵：`UI_..._Street_<dataset>_<原名 sha1 前 10 hex>`。

    指紋取**原名逐字節**而非正規化名：空白折疊會讓 `Forest  St` 與 `Forest St`
    折成同一個鍵，兩條不同的街就會共用譯名。dataset 進鍵名 ⇒ 跨圖同名街各自可譯。
    """
    h = hashlib.sha1(name.encode("utf-8")).hexdigest()[:_KEY_HASH_LEN]
    return f"{UI_KEY_PREFIX}{dataset_id}_{h}"


def build_rows(dataset_id: str, names: dict[str, dict]) -> tuple[list[Row], list[str]]:
    """→ (依原名排序的 Row，warnings)。三語全缺者不出鍵（執行期原樣顯示）。"""
    rows: list[Row] = []
    warnings: list[str] = []
    for raw in sorted(names):
        entry = names[raw]
        tr = {lang: _field(entry, lang) for lang in TR_LANGS}
        if not any(tr.values()):
            warnings.append(f"{raw!r} 三語全缺，不出翻譯鍵（執行期顯示英文原名）")
            continue
        missing = [lang for lang in TR_LANGS if not tr[lang]]
        if missing:
            warnings.append(f"{raw!r} 缺 {'/'.join(missing)}，該語言退回英文原名")
        keys = [raw]
        norm = normalize_name(raw)
        if norm != raw:
            keys.append(norm)
        values = {"EN": raw}
        values.update({lang: tr[lang] or raw for lang in TR_LANGS})
        rows.append(Row(tuple(keys), street_ui_key(dataset_id, raw), values))
    return rows, warnings


def load_all(files: list[Path]) -> tuple[dict[str, list[Row]], list[str], list[str]]:
    """→ ({dataset: rows}, errors, warnings)。有 names.json 就有一格（可能是空表），
    註冊清單引用時才不會拿到 nil。"""
    rows_by_ds: dict[str, list[Row]] = {}
    errors: list[str] = []
    warnings: list[str] = []
    for path in files:
        ds = path.parent.name
        if not path.is_file():
            errors.append(f"找不到 {path}")
            continue
        try:
            data = read_names_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{ds}：讀 names.json 失敗（{exc}）")
            continue
        declared = data.get("dataset")
        if declared is not None and str(declared) != ds:
            errors.append(f"{ds}：dataset 欄位 {declared!r} 與目錄名不符")
        names, load_err = _load_names_map(data)
        errors.extend(f"{ds}：{e}" for e in load_err)
        if load_err:
            continue
        rows, warn_list = build_rows(ds, names)
        warnings.extend(f"{ds} {w}" for w in warn_list)
        rows_by_ds[ds] = rows
    return rows_by_ds, errors, warnings


def _lua_str(s: str) -> str:
    """Lua 字串常值：非 ASCII 一律 `\\ddd`（UTF-8 位元組十進位、固定三位）。

    固定三位是必要的——Lua 的 `\\ddd` 最多吃三位數字，補滿才不會被後面的字面數字
    黏走。純 ASCII 輸出讓生成檔與編碼設定、編輯器、git 的 autocrlf/BOM 全部脫鉤。
    """
    out = ['"']
    for b in s.encode("utf-8"):
        if b == 0x22:
            out.append('\\"')
        elif b == 0x5C:
            out.append("\\\\")
        elif 0x20 <= b < 0x7F:
            out.append(chr(b))
        else:
            out.append(f"\\{b:03d}")
    out.append('"')
    return "".join(out)


def render_street_table(rows_by_ds: dict[str, list[Row]]) -> bytes:
    total = sum(len(r) for r in rows_by_ds.values())
    lines = [
        f"-- {STREET_TABLE_REL.name}（生成檔，勿手編）",
        "-- 由 scripts/gen_streets_i18n.py 依 street-names/<dataset>/names.json 生成。",
        "--",
        "-- 內容＝每個 dataset 的「上游英文原街名 → UI 翻譯鍵」。譯名本體在",
        "-- media/lua/shared/Translate/<LANG>/UI.json，執行期由主 MOD 取用；本包不碰",
        "-- 上游 streets.xml 的幾何。查不到鍵的街名（上游新增、尚未補譯）原樣顯示。",
        "--",
        "-- 空白折疊後與原名不同者會多掛一個別名鍵，讓引擎索引裡的髒名（連續空白）",
        "-- 也查得到；兩者指向同一個 UI 鍵。",
        f"-- 共 {len(rows_by_ds)} 個 dataset／{total} 條街名。",
        f"{STREET_TABLE_GLOBAL} = {{",
    ]
    for ds in sorted(rows_by_ds):
        lines.append(f"    [{_lua_str(ds)}] = {{")
        for row in rows_by_ds[ds]:
            for key in row.table_keys:
                lines.append(f"        [{_lua_str(key)}] = {_lua_str(row.ui_key)},")
        lines.append("    },")
    lines.append("}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def _escape_pct(s: str) -> str:
    """PZ 的 Translator 對值做 printf 式替換，裸 `%` 必須寫成 `%%`
    （verify_mod.py 的「翻譯值無裸 %」閘門也照這條規則驗）。"""
    return s.replace("%", "%%")


def ui_json_path(project_root: Path, lang: str) -> Path:
    return project_root / TRANSLATE_REL / lang / "UI.json"


def load_ui_json(path: Path) -> tuple[dict[str, str] | None, str | None]:
    """→ (資料, 錯誤)。dict 保插入序＝保留原檔鍵序。"""
    if not path.is_file():
        return None, f"缺 {path}"
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return None, f"{path} 含 UTF-8 BOM（禁止）"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return None, f"{path} 非 UTF-8：{exc}"
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"{path} JSON 解析失敗：{exc}"
    if not isinstance(data, dict):
        return None, f"{path} 頂層不是物件"
    return data, None


def render_ui_json(
    existing: dict[str, str], rows_by_ds: dict[str, list[Row]], lang: str
) -> bytes:
    """既有鍵原序保留，本生成器命名空間的鍵整批重出（移除的 dataset 自然被清掉）。

    無尾換行＝本包四語 UI.json 的既有慣例（輸出固定，與輸入檔尾狀態無關 ⇒ 手改
    加尾換行也會被 verify 的逐字節比對抓到）。
    """
    out = {k: v for k, v in existing.items() if not str(k).startswith(UI_KEY_PREFIX)}
    for ds in sorted(rows_by_ds):
        for row in rows_by_ds[ds]:
            out[row.ui_key] = _escape_pct(row.values[lang])
    return json.dumps(out, ensure_ascii=False, indent=4).encode("utf-8")


def render_all(
    project_root: Path, rows_by_ds: dict[str, list[Row]]
) -> tuple[dict[Path, bytes], list[str]]:
    """→ ({路徑: 期望位元組}, errors)。gen 與 verify 共用同一支 ⇒ verify 就是重跑。"""
    errors: list[str] = []
    out: dict[Path, bytes] = {
        project_root / STREET_TABLE_REL: render_street_table(rows_by_ds)
    }
    for lang in UI_LANGS:
        path = ui_json_path(project_root, lang)
        existing, err = load_ui_json(path)
        if existing is None:
            errors.append(err or f"{path} 無法讀取")
            continue
        out[path] = render_ui_json(existing, rows_by_ds, lang)
    return out, errors


def write_bytes_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


# ============================================================
# 註冊清單交叉比對
# ============================================================
def read_registry_datasets(project_root: Path) -> tuple[list[str], list[str]]:
    """→ (`streetNames` 引用的 dataset 清單, errors)。"""
    path = project_root / REGISTRY_REL
    if not path.is_file():
        return [], [f"找不到註冊清單 {path}"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if _REGISTRY_LEGACY_RE.search(text):
        errors.append(
            "註冊清單仍有 streetI18n（語系 XML 替換已移除，改用 "
            f"streetNames = <別名>[\"<dataset>\"] 引用 {STREET_TABLE_GLOBAL}）"
        )
    return _REGISTRY_STREETNAMES_RE.findall(text), errors


# ============================================================
# 上游對照（非阻擋：只給補譯提示，不影響生成物）
# ============================================================
def survey_upstream(
    project_root: Path, *, prefer: list[str], update_hash: bool
) -> list[str]:
    """比對本機上游副本：列出待補譯（或鍵與原字串不符）的街名、sha256 是否已變。"""
    roots = iter_workshop_roots(prefer)
    if not roots:
        return ["無本機 workshop 副本，略過上游對照（不影響生成物）"]
    notes: list[str] = []
    for path in discover_names_files(project_root / "street-names", None):
        ds = path.parent.name
        try:
            data = read_names_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        src = data.get("source") if isinstance(data.get("source"), dict) else {}
        wid = str(src.get("workshop_id") or "")
        recorded = str(src.get("streets_xml_sha256") or "")
        xml = find_streets_xml(roots, wid, str(src.get("map_dir") or ""))
        if xml is None:
            continue
        try:
            text = xml.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            notes.append(f"{ds}：上游 streets.xml 讀取失敗（{exc}）")
            continue
        known = set(data.get("names") or ())
        new = [n for n in upstream_names(text) if n not in known]
        if new:
            # repr：把「連續空白」這種看不見的差異印出來（鍵必須是上游原字串）
            notes.append(
                f"{ds}：上游有 {len(new)} 個未收錄街名（執行期顯示英文原名）："
                + "、".join(repr(n) for n in new[:8])
                + ("…" if len(new) > 8 else "")
            )
        current = file_sha256(xml)
        if recorded and recorded != current:
            if update_hash:
                data.setdefault("source", {})
                data["source"]["streets_xml_sha256"] = current
                data["source"]["captured"] = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%d"
                )
                write_names_json(path, data)
                notes.append(f"{ds}：已更新 source.streets_xml_sha256 → {current}")
            else:
                notes.append(
                    f"{ds}：上游 sha256 已變（記錄 {recorded[:12]}／現行 "
                    f"{current[:12]}），補譯後以 gen --update-hash 接受"
                )
    return notes


# ============================================================
# CLI
# ============================================================
def _print_result(label: str, result: Result) -> None:
    for w in result.warnings:
        warn(f"{label} {w}")
    if result.ok:
        print(f"✅ {label}")
        return
    print(f"❌ {label}", file=sys.stderr)
    for e in result.errors:
        print(f"     {e}", file=sys.stderr)


def gen(project_root: Path) -> tuple[Result, dict[str, list[Row]]]:
    files = discover_names_files(project_root / "street-names", None)
    rows_by_ds, errors, warnings = load_all(files)
    if errors:
        return Result(errors, warnings), rows_by_ds
    expected, render_err = render_all(project_root, rows_by_ds)
    if render_err:
        return Result(render_err, warnings), rows_by_ds
    for path, data in expected.items():
        write_bytes_atomic(path, data)
    return Result([], warnings), rows_by_ds


def verify(project_root: Path) -> Result:
    files = discover_names_files(project_root / "street-names", None)
    rows_by_ds, errors, warnings = load_all(files)
    if errors:
        # names.json 自己就壞掉時不比對生成物：那些「與重跑結果不符」全是雜訊
        return Result(errors, warnings)
    expected, errors = render_all(project_root, rows_by_ds)
    for path, data in expected.items():
        rel = path.relative_to(project_root) if path.is_relative_to(project_root) else path
        if not path.is_file():
            errors.append(f"缺生成檔 {rel}（跑 gen）")
        elif path.read_bytes() != data:
            errors.append(f"{rel} 與重跑生成器的結果不符（手改？跑 gen 重生）")

    referenced, reg_err = read_registry_datasets(project_root)
    errors.extend(reg_err)
    for ds in referenced:
        if ds not in rows_by_ds:
            errors.append(f"註冊清單引用不存在的 dataset：{ds}")
    for ds in sorted(rows_by_ds):
        if ds not in referenced:
            warnings.append(f"{ds} 有 names.json 但註冊清單未引用（死資料？）")
    return Result(errors, warnings)


def cmd_gen(args: argparse.Namespace, *, project_root: Path | None = None) -> int:
    root = project_root or PROJECT_ROOT
    result, rows_by_ds = gen(root)
    _print_result("gen 街名索引表＋四語 UI.json", result)
    if not result.ok:
        return 1
    total = sum(len(r) for r in rows_by_ds.values())
    print(f"   → {STREET_TABLE_REL.name}：{len(rows_by_ds)} dataset／{total} 條")
    print(f"   → Translate/{{{','.join(UI_LANGS)}}}/UI.json")
    for note in survey_upstream(root, prefer=args.prefer, update_hash=args.update_hash):
        warn(f"上游對照 {note}")
    return 0


def cmd_verify(args: argparse.Namespace, *, project_root: Path | None = None) -> int:
    root = project_root or PROJECT_ROOT
    result = verify(root)
    _print_result("verify 街名資料", result)
    return 0 if result.ok else 1


# ============================================================
# selftest（自造迷你 fixture，不依賴真 names.json／真 workshop）
# ============================================================
_SEED_UI = {"UI_MinidoracatMiniMapModMaps_Demo": "示範", "UI_Keep_Pct": "100%% done"}


def _fixture(
    root: Path,
    datasets: dict[str, dict],
    *,
    registry_ids: list[str] | None = None,
    stale_ui_key: bool = False,
) -> None:
    for ds, names in datasets.items():
        d = root / "street-names" / ds
        d.mkdir(parents=True, exist_ok=True)
        write_names_json(
            d / "names.json",
            {"dataset": ds, "source": {"workshop_id": "1", "map_dir": ds}, "names": names},
        )
    for lang in UI_LANGS:
        path = ui_json_path(root, lang)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = dict(_SEED_UI)
        if stale_ui_key:
            data[f"{UI_KEY_PREFIX}gone-dataset_0123456789"] = "殘留"
        path.write_bytes(
            (json.dumps(data, ensure_ascii=False, indent=4) + "\n").encode("utf-8")
        )
    reg = root / REGISTRY_REL
    reg.parent.mkdir(parents=True, exist_ok=True)
    ids = registry_ids if registry_ids is not None else sorted(datasets)
    body = "\n".join(
        f'        {{ zip = "{i}.pyramid.zip", mapMod = "M{n}", mapDir = "D{n}",\n'
        f'            streetNames = StreetNames["{i}"],\n'
        f'            bounds = {{ 1, 2, 3, 4 }}, nameKey = "UI_x" }},'
        for n, i in enumerate(ids)
    )
    reg.write_text(
        f"local StreetNames = {STREET_TABLE_GLOBAL} or {{}}\n"
        'MinidoracatMiniMapAPI.registerMaps("X", {\n' + body + "\n})\n",
        encoding="utf-8",
    )


def cmd_selftest() -> int:
    n_ok = 0
    n_all = 0

    def check(label: str, cond: bool, detail: str = "") -> None:
        nonlocal n_ok, n_all
        n_all += 1
        if cond:
            n_ok += 1
            print(f"  ✅ {label}")
        else:
            print(f"  ❌ {label}{('：' + detail) if detail else ''}", file=sys.stderr)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "case1"
        _fixture(
            root,
            {
                "alpha": {
                    "Main St": {"ch": "主街", "cn": "主街", "jp": "メイン通り"},
                    "Forest  St": {"ch": "森林街", "cn": "森林街", "jp": "森林通り"},
                    "Pct Way": {"ch": "百分之 100% 道", "cn": "百分之 100% 道",
                                "jp": "100% パーセント道"},
                    "Untranslated Rd": {},
                    "成華 Road": {"ch": "成華路", "cn": "成华路", "jp": None},
                },
                "beta": {"Main St": {"ch": "大街", "cn": "大街", "jp": "大通り"}},
            },
            stale_ui_key=True,
        )
        res, rows = gen(root)
        check("gen 成功", res.ok, "; ".join(res.errors))
        lua = (root / STREET_TABLE_REL).read_bytes()
        ch, _ = load_ui_json(ui_json_path(root, "CH"))
        en, _ = load_ui_json(ui_json_path(root, "EN"))
        jp, _ = load_ui_json(ui_json_path(root, "JP"))

        check(
            "非 ASCII 原名用十進位位元組跳脫",
            b"\\230\\136\\144\\232\\143\\175 Road" in lua,
            "找不到 成華 Road 的跳脫鍵",
        )

        alpha_keys = {r.table_keys[0]: r.ui_key for r in rows["alpha"]}
        check(
            "三語全缺者不出鍵",
            "Untranslated Rd" not in alpha_keys
            and b"Untranslated Rd" not in lua,
            "未翻譯街名仍被寫進表",
        )
        check(
            "空白折疊別名指向同一 UI 鍵",
            b'["Forest  St"] = "' in lua and b'["Forest St"] = "' in lua
            and lua.count(alpha_keys["Forest  St"].encode()) == 2,
            "缺別名或指向不同鍵",
        )
        check(
            "跨 dataset 同名街各自成鍵",
            alpha_keys["Main St"] != {r.table_keys[0]: r.ui_key for r in rows["beta"]}["Main St"],
            "兩個 dataset 的 Main St 撞鍵",
        )
        check(
            "UI 鍵格式＝前綴＋dataset＋10 hex",
            re.fullmatch(
                re.escape(UI_KEY_PREFIX) + r"alpha_[0-9a-f]{10}", alpha_keys["Main St"]
            )
            is not None,
            alpha_keys["Main St"],
        )
        check(
            "EN 槽＝英文原名、CH 槽＝譯名",
            en[alpha_keys["Main St"]] == "Main St" and ch[alpha_keys["Main St"]] == "主街",
            f"{en.get(alpha_keys['Main St'])!r}/{ch.get(alpha_keys['Main St'])!r}",
        )
        check(
            "缺該語言時退回英文原名",
            jp[alpha_keys["成華 Road"]] == "成華 Road",
            repr(jp.get(alpha_keys["成華 Road"])),
        )
        check(
            "裸 % escape 成 %%",
            ch[alpha_keys["Pct Way"]] == "百分之 100%% 道"
            and ch["UI_Keep_Pct"] == "100%% done",
            "既有 % 值被改動",
        )
        check(
            "既有非街名鍵保留、殘留街名鍵被清掉",
            ch["UI_MinidoracatMiniMapModMaps_Demo"] == "示範"
            and not any(
                k.startswith(f"{UI_KEY_PREFIX}gone-dataset") for k in ch
            ),
            "非街名鍵遺失或殘留鍵未清",
        )
        check(
            "四語鍵集一致（verify_mod 閘門）",
            len({frozenset(load_ui_json(ui_json_path(root, l))[0]) for l in UI_LANGS}) == 1,
            "四語鍵集不一致",
        )
        before = {p: p.read_bytes() for p in [root / STREET_TABLE_REL] + [ui_json_path(root, l) for l in UI_LANGS]}
        gen(root)
        check(
            "重跑生成確定性（逐字節相同）",
            all(p.read_bytes() == b for p, b in before.items()),
            "同輸入產生不同輸出",
        )
        after = verify(root)
        check("verify 在 gen 後通過", after.ok, "; ".join(after.errors))

        # 手改偵測
        p = ui_json_path(root, "CH")
        data, _ = load_ui_json(p)
        data[alpha_keys["Main St"]] = "被手改"
        p.write_bytes((json.dumps(data, ensure_ascii=False, indent=4) + "\n").encode())
        check("手改 UI.json 街名值 → verify fail", not verify(root).ok)
        gen(root)
        lua_path = root / STREET_TABLE_REL
        lua_path.write_bytes(lua_path.read_bytes() + "-- 手改\n".encode("utf-8"))
        check("手改 Lua 表 → verify fail", not verify(root).ok)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "case2"
        _fixture(root, {"alpha": {"A St": {"ch": "甲街", "cn": "甲街", "jp": "甲通り"}}},
                 registry_ids=["alpha", "ghost"])
        gen(root)
        res = verify(root)
        check(
            "註冊清單引用不存在的 dataset → verify fail",
            not res.ok and any("ghost" in e for e in res.errors),
            "; ".join(res.errors),
        )

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "case3"
        _fixture(root, {"alpha": {"A St": {"ch": "甲街", "cn": "甲街", "jp": "甲通り"}}})
        gen(root)
        reg = root / REGISTRY_REL
        reg.write_text(
            reg.read_text(encoding="utf-8").replace("streetNames =", "streetI18n ="),
            encoding="utf-8",
        )
        res = verify(root)
        check(
            "殘留 streetI18n → verify fail",
            not res.ok and any("streetI18n" in e for e in res.errors),
            "; ".join(res.errors),
        )

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "case4"
        _fixture(
            root,
            {"alpha": {
                "Forest  St": {"ch": "森林街", "cn": "森林街", "jp": "森林通り"},
                "Forest St": {"ch": "林街", "cn": "林街", "jp": "林通り"},
                "Typo Ave": {"zh": "錯欄位"},
            }},
        )
        res, _ = gen(root)
        check(
            "空白折疊後撞鍵 → gen fail",
            not res.ok and any("撞鍵" in e for e in res.errors),
            "; ".join(res.errors),
        )
        check(
            "未知語言欄位 → gen fail",
            any("未知欄位" in e for e in res.errors),
            "; ".join(res.errors),
        )
        check("gen 失敗時不寫檔", not (root / STREET_TABLE_REL).exists())

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "case5"
        _fixture(root, {"alpha": {"A St": {"ch": "甲街", "cn": "甲街", "jp": "甲通り"}}})
        ui_json_path(root, "JP").unlink()
        res, _ = gen(root)
        check(
            "缺任一語 UI.json → gen fail（不半套寫入）",
            not res.ok and not (root / STREET_TABLE_REL).exists(),
            "; ".join(res.errors),
        )

    print(f"selftest {n_ok}/{n_all}")
    return 0 if n_ok == n_all else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="自我測試（零外部依賴）")
    sub = parser.add_subparsers(dest="cmd")
    g = sub.add_parser("gen", help="生成街名索引表與四語 UI.json")
    g.add_argument("--prefer", action="append", default=[],
                   help="優先索引的額外 workshop content 根（僅供上游對照提示）")
    g.add_argument("--update-hash", action="store_true",
                   help="接受上游新 sha256（寫回 names.json 的 source）")
    sub.add_parser("verify", help="重跑生成器與磁碟逐字節比對＋註冊清單交叉核對")
    args = parser.parse_args(argv)
    if args.selftest:
        return cmd_selftest()
    if args.cmd == "gen":
        return cmd_gen(args)
    if args.cmd == "verify":
        return cmd_verify(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
