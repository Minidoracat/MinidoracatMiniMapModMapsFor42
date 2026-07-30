#!/usr/bin/env bash
# reset_map_mod_chunks.sh — 一鍵重置支援地圖 MOD 區域的存檔 chunk（B42）
#
# 用途：地圖 MOD 加入「已生成過的世界」時，已生成的 chunk 不會重生地圖內容；
#       刪除該區域的存檔檔案可強制引擎依新地圖資料重生。也可用於定期重置。
# 依據：/home/github/MinidoracatBuildingResetFor42 的 area reset 實證——
#       chunk = square//8（map/{x//8}/{y//8}.bin）、cell = square//256，
#       cell 級動 chunkdata_/metacell_/datachunk_/apop_ 四類，zpop 不動。
# 範圍：內嵌 bounds 表（來源：MinidoracatMiniMapModMaps.lua 註冊表，右/下排他）
#       ∩ 伺服器 ini 的 Map= 啟用清單——未啟用的地圖不會被動到。
# 用法：先停伺服器 → ./reset_map_mod_chunks.sh 看 dry-run 統計
#                  → ./reset_map_mod_chunks.sh --execute 實際搬移
#       檔案「搬移」到 /home/pzserver/Zomboid/backups/map_reset_<時間>/（非刪除），
#       還原：cp -a <備份目錄>/. /home/pzserver/Zomboid/Saves/Multiplayer/pzserver/
# 警告：地圖 MOD 範圍與 vanilla 城鎮重疊（Muldraugh/West Point 一帶尤甚），
#       範圍內玩家建築／安全屋物資一併重置——執行前先確認無人設據點。
#       bounds 是矩形外框：非矩形地圖的外框角落也會重置到共用的 vanilla cell 狀態。
# 注意：dry-run 的統計在多張地圖重疊處會重複計數（execute 時每檔只搬一次）。
# ponytail: 表為發版時生成的靜態資料——本包新增地圖後需重新生成（見 AGENTS.md）
set -euo pipefail

SERVER_NAME="${PZ_SERVER_NAME:-pzserver}"
ZOMBOID="${PZ_ZOMBOID:-/home/pzserver/Zomboid}"
INI="${PZ_INI:-$ZOMBOID/Server/${SERVER_NAME}.ini}"   # PZ_INI 覆寫＝指定自製 Map= 清單做「定向重置」
SAVE="$ZOMBOID/Saves/Multiplayer/${SERVER_NAME}"
BACKUP_ROOT="$ZOMBOID/backups"

# --- B42 座標轉換自我檢查（壞了就直接停）---
[ $((10496 / 8)) -eq 1312 ] || { echo "selftest fail: chunk div" >&2; exit 1; }
[ $((10496 / 256)) -eq 41 ] || { echo "selftest fail: cell div" >&2; exit 1; }
[ $(((11008 - 1) / 8)) -eq 1375 ] || { echo "selftest fail: exclusive end" >&2; exit 1; }

MODE="dry-run"
[ "${1:-}" = "--execute" ] && MODE="execute"

if pgrep -f "ProjectZomboid64.*-servername ${SERVER_NAME}" >/dev/null 2>&1; then
    echo "[中止] ${SERVER_NAME} 伺服器仍在執行——請先關閉伺服器再跑本腳本" >&2
    exit 1
fi
[ -f "$INI" ] || { echo "[中止] 找不到 $INI" >&2; exit 1; }
[ -d "$SAVE/map" ] || { echo "[中止] 找不到存檔 $SAVE/map" >&2; exit 1; }

# Map= 啟用資料夾
MAP_LINE=$(grep '^Map=' "$INI" | head -1 | sed 's/^Map=//')
declare -A ENABLED
IFS=';' read -ra _entries <<<"$MAP_LINE"
for e in "${_entries[@]}"; do
    e="${e#"${e%%[![:space:]]*}"}"
    e="${e%"${e##*[![:space:]]}"}"
    [ -n "$e" ] && ENABLED["$e"]=1
done

TS=$(date +%Y%m%d-%H%M%S)
BK="$BACKUP_ROOT/map_reset_$TS"
echo "模式：$MODE（Map= 啟用 ${#ENABLED[@]} 條目）"
total=0
skipped=0

while IFS='|' read -r folder x1 y1 x2 y2; do
    y2="${y2%$'\r'}"   # 縱深防護：表若混入 CRLF，尾欄會帶 CR 使算術炸掉
    [ -n "$folder" ] || continue
    if [ -z "${ENABLED[$folder]:-}" ]; then
        skipped=$((skipped + 1))
        continue
    fi
    cx1=$((x1 / 8)); cx2=$(((x2 - 1) / 8))
    cy1=$((y1 / 8)); cy2=$(((y2 - 1) / 8))
    gx1=$((x1 / 256)); gx2=$(((x2 - 1) / 256))
    gy1=$((y1 / 256)); gy2=$(((y2 - 1) / 256))
    n=0
    # map/<chunkX>/<chunkY>.bin
    for cx in $(seq "$cx1" "$cx2"); do
        d="$SAVE/map/$cx"
        [ -d "$d" ] || continue
        for f in "$d"/*.bin; do
            [ -e "$f" ] || continue
            cy="${f##*/}"; cy="${cy%.bin}"
            [[ "$cy" =~ ^-?[0-9]+$ ]] || continue
            if [ "$cy" -ge "$cy1" ] && [ "$cy" -le "$cy2" ]; then
                if [ "$MODE" = "execute" ]; then
                    mkdir -p "$BK/map/$cx"
                    mv "$f" "$BK/map/$cx/"
                fi
                n=$((n + 1))
            fi
        done
    done
    # cell 級（256）：chunkdata / metagrid / isoregiondata / apop
    for gx in $(seq "$gx1" "$gx2"); do
        for gy in $(seq "$gy1" "$gy2"); do
            for spec in "chunkdata/chunkdata_${gx}_${gy}.bin" \
                        "metagrid/metacell_${gx}_${gy}.bin" \
                        "isoregiondata/datachunk_${gx}_${gy}.bin" \
                        "apop/apop_${gx}_${gy}.bin"; do
                f="$SAVE/$spec"
                [ -e "$f" ] || continue
                if [ "$MODE" = "execute" ]; then
                    mkdir -p "$BK/${spec%/*}"
                    mv "$f" "$BK/$spec"
                fi
                n=$((n + 1))
            done
        done
    done
    if [ "$n" -gt 0 ]; then
        printf '%-50s %7d 檔\n' "$folder" "$n"
    fi
    total=$((total + n))
done <<'BOUNDS'
AnruisiTown|11776|11008|13056|12032
Asakusa lake town|10496|11264|11264|12032
AshenwoodNewB42|11264|11008|11776|11776
Atlanta - Safe Zone-Chinese Survivors’ Community|8448|7680|9216|8448
Atlanta Tower Survival|11008|12544|11520|13056
Atlanta|10496|12288|13056|14592
Begonia_Town|11264|7424|12544|7936
Blackmaze_wp|10752|6144|11264|6656
BlackpineCounty|9728|14080|11776|15360
Bunker 42|11008|9728|11520|10240
Camden County B42|12800|8448|19200|14848
Cathaya Valley2.0 highway|7424|12288|7936|13312
Cathaya Valley2.0|7168|12544|7680|13312
Chinatown Expansion B42 version|10752|8192|11264|9216
Clover Lake|9472|8960|9984|9984
Constown, KY|4864|10752|6400|11520
Coryerdon B42|7168|5632|10752|7424
Daisy County|9728|7168|10752|8192
DawnTown|2816|7936|3328|8448
EchoCreek MilitaryBase回音河 军事基地|2816|9984|3840|11008
EdsAutoSalvageB42|8448|8192|9216|8704
Erikas_Furniture_Store|11264|7936|11776|8448
Estate 39|8192|9728|8704|10240
Floatopia|4352|5376|4864|5888
Fort Benning B42|5888|6656|6400|7424
Fort JadeLake|11008|8448|11520|9216
Fort Waterfront B42|9984|10752|10752|11264
Fort_Boonesborough|13824|1792|14592|2048
Frogtown|2816|6656|4096|7680
Grapeseed|6144|10752|7680|11776
Greenleaf|6144|9984|6912|11008
Greenport, KY|7936|7168|8704|7936
Hartburg, KY|6400|11008|6912|11776
HavenFall|4096|8448|5120|9472
Hazelnut Manor[Poor Version]|12544|5888|13056|6400
Hazelnut Manor|12544|5888|13056|6400
IrisEyot|4096|11008|4864|11520
Kentucky Center Manor_Renovation_B42|7936|9472|8448|9984
KillMingLake|8192|11776|8704|12544
Kingsmouth North B42|0|3840|1280|5120
linzi|8960|11008|9728|11776
LittleTownshipB42|7936|8192|8448|8704
Louisville_Riverboat|13056|1024|13312|1280
Macon|3584|6400|4608|6912
Megurigaoka City, Kanagawa|0|2304|1280|4864
Meiya'sTown|7936|10752|8448|11264
Muldraugh 1993 B42|10496|8960|11264|11008
Muldraugh_FireDept|10496|8960|11008|9472
Muldraugh-SouthernCheckpoint|10496|10752|11008|11520
muldraughmilitarybaseas24|8448|10752|9472|11520
Nettle Township|6400|8960|7424|9728
New Ellroy|4864|9728|5888|10752
ningzi|8960|11520|9728|12800
Path of Zenith, Louisville|12800|768|13312|1280
pzkNewCoalfield|2816|8192|3584|8960
RaccoonCity|9728|9728|10496|10752
Raven Creek B42|4096|14336|6656|17920
RMSafeHouseUnofficial|5376|4864|5888|5632
SafeharborGarrison|11520|10496|12800|11520
SafeWayHamlet|12544|10752|13056|11520
Sector-7 Breach Highway|9472|7936|10496|9216
Sector-7 Breach|8960|6400|9728|7936
Shadyside|5632|9728|6400|10752
SZ_Bunker_3|5888|11520|6400|12032
SZ_Checkpoint1|11776|7936|12544|8448
SZ_Checkpoint5|10752|11008|11264|11520
SZ_Checkpoint6|5632|5632|6144|6144
SZ_Checkpoint8|6400|11008|6912|11520
SZ_DeerheadLake_Base|4352|8192|4864|8704
SZ_Louisville_Military_Complex|13568|1792|15360|3072
SZ_MarchRidge_ResearchFacility|9984|11776|10752|12800
SZ_Muldraugh_Traindepot_Refugee|11264|9472|12032|10752
SZ_MuldraughCrossroads_Checkpoint|10496|11008|11008|11520
SZ_North_Checkpoint|3584|6656|4352|7424
SZ_The_Mall|13568|5632|14336|6144
taibeiroad|7936|9984|9216|11776
Taylorsville|8960|6144|10496|7680
Tikitown|6400|6656|7936|7936
Trapalaketown|8192|11520|9216|12032
vilaz|9472|9472|9984|9984
West Point Expansion_B42|11776|6400|13312|7680
WILDSTEEL|14336|5632|14848|6144
Willowbrook Bastion!|8448|9472|9728|10240
Yanghu Town|8448|8960|9728|9728
BOUNDS

echo "----------------------------------------------------------------"
echo "合計 $total 檔（未啟用跳過 $skipped 張圖）"
if [ "$MODE" = "execute" ]; then
    echo "已搬移至：$BK"
    echo "還原指令：cp -a \"$BK\"/. \"$SAVE\"/"
else
    echo "dry-run 未動任何檔案；確認無誤後加 --execute 執行"
fi
