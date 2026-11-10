#!/usr/bin/env bash
# test_reset_script.sh — reset_map_mod_chunks.sh 回歸測試（假存檔樹，不碰真實存檔）
# 覆蓋：範圍內搬移／四側範圍外保留／zpop 不動／未啟用地圖跳過／dry-run 不動檔案且檔數與 execute 相同／
#       isoregiondata 照 chunk 座標（和 cell 同號的 chunk、前綴相同的 chunk、RegionHeader.bin 都不動；
#       沒有 map/<cx> 目錄的 chunk 照搬）／execute 中途失敗時印還原指令
# 用 DawnTown bounds 2816,7936,3328,8448 → chunk 352-415/992-1055、cell 11-12/31-32
set -euo pipefail
SC="$(dirname "$(readlink -f "$0")")/reset_map_mod_chunks.sh"
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
Z="$T/Zomboid"
S="$Z/Saves/Multiplayer/rtest"
mkdir -p "$Z/Server" "$S"/{map/351,map/352,map/415,map/416,map/512,chunkdata,metagrid,isoregiondata,apop,zpop}
printf 'Map=DawnTown;Muldraugh, KY\n' > "$Z/Server/rtest.ini"
IN="map/352/992.bin map/415/1055.bin
    isoregiondata/datachunk_352_992.bin isoregiondata/datachunk_415_1055.bin isoregiondata/datachunk_400_1000.bin
    chunkdata/chunkdata_11_31.bin metagrid/metacell_12_32.bin apop/apop_12_31.bin"
# 四側範圍外、未啟用的 IrisEyot 區、範圍外 cell、zpop；isoregion 另加 chunk (11,32)（舊版當成 cell 座標誤搬）、
# 前綴相同的 chunk 3520、不是 datachunk 的 RegionHeader.bin；檔名不是標準格式的（多一段、借用別類的前綴）都不動
OUT="map/351/992.bin map/352/991.bin map/416/992.bin map/415/1056.bin map/512/1376.bin
     map/352/backup_992.bin map/352/datachunk_352_992.bin
     isoregiondata/datachunk_351_992.bin isoregiondata/datachunk_352_991.bin
     isoregiondata/datachunk_416_992.bin isoregiondata/datachunk_415_1056.bin
     isoregiondata/datachunk_11_32.bin isoregiondata/datachunk_3520_992.bin isoregiondata/RegionHeader.bin
     isoregiondata/datachunk_352_991_1000.bin
     chunkdata/chunkdata_10_31.bin zpop/zpop_11_31.bin"
for f in $IN $OUT; do touch "$S/$f"; done
want=$(set -- $IN; echo $#)   # 不用 wc -w：有些 wc 會在數字前補空白

run() { PZ_SERVER_NAME=rtest PZ_ZOMBOID="$Z" bash "$SC" "$@"; }

dry=$(run)                                                           # dry-run
for f in $IN; do [ -e "$S/$f" ] || { echo "FAIL: dry-run 不應動檔案（$f）"; exit 1; }; done
# 不用 `| grep -q`：grep 提早結束時腳本吃 SIGPIPE，pipefail 下會誤判失敗
[[ "$dry" == *"合計 $want 檔"* ]] || { echo "FAIL: dry-run 應列 $want 檔：$dry"; exit 1; }
exe=$(run --execute)
[[ "$exe" == *"合計 $want 檔"* ]] || { echo "FAIL: execute 應搬 $want 檔：$exe"; exit 1; }
for f in $IN; do
    [ ! -e "$S/$f" ] || { echo "FAIL: 範圍內 $f 未搬移"; exit 1; }
    [ -e "$Z/backups"/map_reset_*/"$f" ] || { echo "FAIL: 備份缺 $f"; exit 1; }
done
for f in $OUT; do [ -e "$S/$f" ] || { echo "FAIL: $f 不應被搬移"; exit 1; }; done

# execute 中途失敗：第二次 mv 失敗時以非 0 結束，而且印出還原指令
mkdir "$T/bin"
printf '#!/usr/bin/env bash\nn=$(cat "$CNT" 2>/dev/null || echo 0); echo $((n + 1)) > "$CNT"\n[ "$n" -ge 1 ] && exit 1\nexec %s "$@"\n' "$(command -v mv)" > "$T/bin/mv"
chmod +x "$T/bin/mv"
touch "$S/map/352/992.bin" "$S/map/415/1055.bin"
err=$(CNT="$T/cnt" PATH="$T/bin:$PATH" run --execute 2>&1 >/dev/null) && { echo "FAIL: mv 失敗時應以非 0 結束"; exit 1; }
[[ "$err" == *"還原指令"* ]] || { echo "FAIL: 中途失敗沒印還原指令：$err"; exit 1; }
echo "PASS: reset_map_mod_chunks.sh 回歸測試全過"
