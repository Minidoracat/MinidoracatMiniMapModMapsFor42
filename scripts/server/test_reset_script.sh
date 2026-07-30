#!/usr/bin/env bash
# test_reset_script.sh — reset_map_mod_chunks.sh 回歸測試（假存檔樹，不碰真實存檔）
# 覆蓋：範圍內搬移／四側範圍外保留／zpop 不動／未啟用地圖跳過／dry-run 不動檔案
# 用 DawnTown bounds 2816,7936,3328,8448 → chunk 352-415/992-1055、cell 11-12/31-32
set -euo pipefail
SC="$(dirname "$(readlink -f "$0")")/reset_map_mod_chunks.sh"
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
Z="$T/Zomboid"
S="$Z/Saves/Multiplayer/rtest"
mkdir -p "$Z/Server" "$S"/{map/351,map/352,map/415,map/416,map/512,chunkdata,metagrid,isoregiondata,apop,zpop}
printf 'Map=DawnTown;Muldraugh, KY\n' > "$Z/Server/rtest.ini"
touch "$S/map/352/992.bin" "$S/map/415/1055.bin"                    # 範圍內（兩角）
touch "$S/map/351/992.bin" "$S/map/352/991.bin" "$S/map/416/992.bin" "$S/map/415/1056.bin"  # 四側範圍外
touch "$S/map/512/1376.bin"                                          # IrisEyot 區（未啟用）
touch "$S/chunkdata/chunkdata_11_31.bin" "$S/chunkdata/chunkdata_10_31.bin"
touch "$S/metagrid/metacell_12_32.bin" "$S/isoregiondata/datachunk_11_32.bin"
touch "$S/apop/apop_12_31.bin" "$S/zpop/zpop_11_31.bin"

run() { PZ_SERVER_NAME=rtest PZ_ZOMBOID="$Z" bash "$SC" "$@"; }

run > /dev/null                                                      # dry-run
[ -e "$S/map/352/992.bin" ] || { echo "FAIL: dry-run 不應動檔案"; exit 1; }
run --execute > /dev/null
[ ! -e "$S/map/352/992.bin" ] && [ ! -e "$S/map/415/1055.bin" ] || { echo "FAIL: 範圍內未搬移"; exit 1; }
for f in map/351/992.bin map/352/991.bin map/416/992.bin map/415/1056.bin map/512/1376.bin \
         chunkdata/chunkdata_10_31.bin zpop/zpop_11_31.bin; do
    [ -e "$S/$f" ] || { echo "FAIL: $f 不應被搬移"; exit 1; }
done
for f in chunkdata/chunkdata_11_31.bin metagrid/metacell_12_32.bin isoregiondata/datachunk_11_32.bin apop/apop_12_31.bin; do
    [ ! -e "$S/$f" ] || { echo "FAIL: cell 級 $f 未搬移"; exit 1; }
done
[ -e "$Z/backups"/map_reset_*/map/352/992.bin ] || { echo "FAIL: 備份缺檔"; exit 1; }
echo "PASS: reset_map_mod_chunks.sh 回歸測試全過"
