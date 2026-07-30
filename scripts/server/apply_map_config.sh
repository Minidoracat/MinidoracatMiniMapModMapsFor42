#!/usr/bin/env bash
# apply_map_config.sh — 把地圖 MOD 三行設定（Mods=/Map=/WorkshopItems=）套進 pzserver.ini
#
# 為什麼需要：PZ 伺服器「正常關閉」時會把整份 ini 從記憶體回寫，蓋掉伺服器
# 運行中對檔案的手改。安全套用順序＝停服 → 跑本腳本 → 開服。可重複執行（冪等）。
# 三行內容存於同目錄 pzserver_map_lines.conf（單一真相；改地圖清單改它）。
set -euo pipefail

INI="${PZ_INI:-/home/pzserver/Zomboid/Server/pzserver.ini}"
CONF="${PZ_CONF:-$(dirname "$(readlink -f "$0")")/pzserver_map_lines.conf}"

[ -f "$INI" ] || { echo "[中止] 找不到 $INI" >&2; exit 1; }
[ -f "$CONF" ] || { echo "[中止] 找不到 $CONF" >&2; exit 1; }

# 停服 guard：伺服器運行中套用會被之後的整份回寫蓋掉（假成功）。確要線上套用：FORCE=1
SERVER_NAME="$(basename "$INI" .ini)"
if [ "${FORCE:-}" != "1" ] && pgrep -f "ProjectZomboid64.*-servername ${SERVER_NAME}" >/dev/null 2>&1; then
    echo "[中止] ${SERVER_NAME} 伺服器仍在執行——線上套用會被回寫覆蓋。請停服後再跑（或 FORCE=1 強制）" >&2
    exit 1
fi

# tr -d '\r'：conf 若經 Windows 編輯（CRLF），行尾 CR 會污染 ini
MODS_LINE=$(grep '^Mods=' "$CONF" | tr -d '\r')
MAP_LINE=$(grep '^Map=' "$CONF" | tr -d '\r')
WS_LINE=$(grep '^WorkshopItems=' "$CONF" | tr -d '\r')

TS=$(date +%Y%m%d-%H%M%S)
cp -a "$INI" "$INI.bak-$TS"

TMP="$INI.tmp.$$"
# `|| [ -n "$line" ]`：ini 末行可能無換行符，少了它會掉最後一行
while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
        Mods=*)          printf '%s\n' "$MODS_LINE" ;;
        Map=*)           printf '%s\n' "$MAP_LINE" ;;
        WorkshopItems=*) printf '%s\n' "$WS_LINE" ;;
        *)               printf '%s\n' "$line" ;;
    esac
done <"$INI" >"$TMP"

# 三個鍵都必須存在才寫回
for key in Mods Map WorkshopItems; do
    grep -q "^${key}=" "$TMP" || { echo "[中止] 產出缺 ${key}=，未寫回（備份在 $INI.bak-$TS）" >&2; rm -f "$TMP"; exit 1; }
done
# 先對 TMP 套權限再 mv——mode 錯會讓伺服器讀寫不了自己的 ini，必須硬失敗；owner 失敗要大聲說
chmod --reference="$INI" "$TMP" || { echo "[中止] chmod 失敗，未寫回" >&2; rm -f "$TMP"; exit 1; }
chown --reference="$INI" "$TMP" 2>/dev/null || echo "[警告] chown 失敗（非 root 執行？）——請確認 $INI 擁有者仍為 pzserver" >&2
mv "$TMP" "$INI"

echo "[OK] 已套用（原檔備份：$INI.bak-$TS）"
awk -F= '/^(Mods|Map|WorkshopItems)=/ { n = split($2, a, ";"); c = 0; for (i = 1; i <= n; i++) if (a[i] != "") c++; print "  " $1 "= 條目數: " c }' "$INI"
