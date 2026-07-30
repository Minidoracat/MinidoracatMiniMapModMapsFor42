# generate_server_artifacts.ps1 — 重生正式伺服器地圖設定產物（新增支援地圖後跑）
#
# 輸入：$ServerLinesFile＝從伺服器抓回的現行三行（Mods=/Map=/WorkshopItems= 原封），例：
#   bash ~/.claude/skills/ssh-remote/scripts/lib/ssh-wrapper.sh pz-server-base-pzserver \
#     bash -s <<<'grep -E "^(Mods|Map|WorkshopItems)=" /home/pzserver/Zomboid/Server/pzserver.ini' > server_current_lines.txt
# 輸出（$OutDir）：
#   pzserver_map_lines.conf — 併入本包全部支援地圖後的三行（上傳到伺服器 /home/pzserver/scripts/）
#   bounds_table.txt        — folder|x1|y1|x2|y2（貼回 reset_map_mod_chunks.sh 的 BOUNDS 區塊）
# 後續：check_map_conflicts.ps1 用新 Map= 驗證 0 危險組合 → 上傳 → 停服套用 apply_map_config.sh
param(
    [Parameter(Mandatory)][string]$ServerLinesFile,
    [string]$OutDir = $PSScriptRoot
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$LuaRegistry = Join-Path $ProjectRoot 'MOD\MinidoracatMiniMapModMapsFor42\Contents\mods\MinidoracatMiniMapModMapsFor42\42\media\lua\client\MinidoracatMiniMapModMaps.lua'
$ServerModIds = @('MinidoracatMiniMapFor42', 'MinidoracatMiniMapModMapsFor42')
$MapPackWorkshopId = '3763914102'

# 與 link_workshop.ps1 的 $MapOrderFirst/$MapFolderExclude 同步維護（NPE 排序見 docs/server-map-order-npe.md）
$MapOrderFirst = @('AnruisiTown', 'Taylorsville', 'Coryerdon B42', 'RaccoonCity', 'Camden County B42', 'Clover Lake')
# Greenport＝GreenportB42 內的 B41 舊版資料夾；Sector-7 兩資料夾＝Workshop 3513107552 已下架（2026-07-21），
# 伺服器下載不到（result=15），資料夾層也排除以免從現行 Map= 被保留回來；
# EchoCreek＝地圖/模組資料夾名含中文，社群實證會讓伺服器 isoregiondata 解析失敗整包載不進（2026-07-21 鴨子回報）
# Meiya'sTown＝Workshop 3478788261 已下架（2026-07-22，玩家無法下載卡進服）；
# taibeiroad＝Taibeiroad4 引用未上架材質包，Missing tile definition 單檔 log 刷 1.1 萬行＋玩家端同樣缺圖
# （2026-07-22 使用者決定移除；含物品腳本、存檔已跑過——WorldDictionary 風險已知情接受，備份保險先行）
# Trapalaketown/KillMingLake＝同樣引用未上架 taibei 材質包（2026-07-22 使用者決定一併移除；
# Trapalaketown 含物品腳本、WorldDictionary 風險知情接受）
$MapFolderExclude = @('Greenport', 'Sector-7 Breach', 'Sector-7 Breach Highway', 'EchoCreek MilitaryBase回音河 军事基地',
    'Muldraugh 1993 B42', "Meiya'sTown", 'taibeiroad', 'Trapalaketown', 'KillMingLake')
# 正式伺服器排除（2026-07-21 決策）：互斥變體取本體；Atlanta/Atlanta Tower 衝突二選一取 Atlanta；
# Sector-7 兩 mod＝Workshop 項目下架；EchoCreek＝非 ASCII 資料夾名（見上）；
# Muldraugh 1993＝使用者決定不上（2026-07-21，覆蓋 vanilla Muldraugh 的重製圖）
$VariantExclude = @('Chinatown Expansion B42 version (Less Traffic Jam)', 'HazelnutManor[Poor Version]', 'Atlanta Tower Survival',
    'Sector-7 Breach', 'Sector-7 Breach Highway', 'EchoCreek MilitaryBase', 'muldraugh1993b42',
    "Meiya'sTown", 'Taibeiroad4', 'TrapalaketownB42', 'KillMingLake')

# --- mod.info 讀取（版本優先序同引擎：42.x > common > root）---
function Read-ModInfo {
    param([string]$ModRoot)
    $cands = @()
    foreach ($d in (Get-ChildItem -LiteralPath $ModRoot -Directory -ErrorAction SilentlyContinue)) {
        if ($d.Name -match '^\d+(\.\d+)?$') {
            $cands += [pscustomobject]@{ v = [double]$d.Name; p = (Join-Path $d.FullName 'mod.info') }
        }
    }
    $ordered = @($cands | Sort-Object v -Descending | ForEach-Object { $_.p })
    $ordered += (Join-Path $ModRoot 'common\mod.info'), (Join-Path $ModRoot 'mod.info')
    foreach ($p in $ordered) {
        if (Test-Path -LiteralPath $p) {
            $txt = Get-Content -LiteralPath $p -Raw -Encoding UTF8
            $id = $null; $req = @()
            if ($txt -match '(?m)^\s*id\s*=\s*(.+?)\s*$') { $id = $Matches[1] }
            if ($txt -match '(?m)^\s*require\s*=\s*(.+?)\s*$') {
                $req = @($Matches[1] -split '\s*,\s*' | ForEach-Object { $_.Trim().TrimStart('\') } | Where-Object { $_ })
            }
            return @{ Id = $id; Requires = $req }
        }
    }
    return $null
}

function Get-ModMapFolders {
    param([string]$ModRoot)
    $found = @()
    $mapsDirs = @()
    foreach ($sub in (Get-ChildItem -LiteralPath $ModRoot -Directory -ErrorAction SilentlyContinue)) {
        $p = Join-Path $sub.FullName 'media\maps'
        if (Test-Path -LiteralPath $p) { $mapsDirs += $p }
    }
    $rootMaps = Join-Path $ModRoot 'media\maps'
    if (Test-Path -LiteralPath $rootMaps) { $mapsDirs += $rootMaps }
    foreach ($md in $mapsDirs) {
        foreach ($mf in (Get-ChildItem -LiteralPath $md -Directory -ErrorAction SilentlyContinue)) {
            if ($found -contains $mf.Name) { continue }
            if (Get-ChildItem -LiteralPath $mf.FullName -Filter *.lotheader -File -ErrorAction SilentlyContinue |
                Select-Object -First 1) { $found += $mf.Name }
        }
    }
    return $found
}

# --- 本機 Workshop 掃描（id -> WorkshopId/Root/Requires）---
$steam = (Get-ItemProperty 'HKCU:\Software\Valve\Steam').SteamPath
$libs = @($steam)
$vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
if (Test-Path -LiteralPath $vdf) {
    $libs += @((Select-String -Path $vdf -Pattern '"path"\s+"([^"]+)"' -AllMatches).Matches |
        ForEach-Object { $_.Groups[1].Value -replace '\\\\', '\' })
}
$wc = $null
foreach ($lib in ($libs | Select-Object -Unique)) {
    $p = Join-Path $lib 'steamapps\workshop\content\108600'
    if (Test-Path -LiteralPath $p) { $wc = $p; break }
}
if (-not $wc) { throw '找不到 Steam Workshop 內容目錄（108600）' }
$installed = @{}
foreach ($item in (Get-ChildItem -LiteralPath $wc -Directory)) {
    $mr = Join-Path $item.FullName 'mods'
    if (-not (Test-Path -LiteralPath $mr)) { continue }
    foreach ($modDir in (Get-ChildItem -LiteralPath $mr -Directory)) {
        $info = Read-ModInfo $modDir.FullName
        if ($info -and $info.Id -and -not $installed.ContainsKey($info.Id)) {
            $installed[$info.Id] = @{ WorkshopId = $item.Name; Root = $modDir.FullName; Requires = $info.Requires }
        }
    }
}

# --- Lua 註冊表 → mod 清單與 bounds ---
$lua = Get-Content -LiteralPath $LuaRegistry -Raw -Encoding UTF8
$rx = [regex]'mapMod\s*=\s*"([^"]+)"(?:,\s*mapDir\s*=\s*"([^"]+)")?,\s*bounds\s*=\s*\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}'
$entries = @($rx.Matches($lua))
$ids = @($entries | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique |
    Where-Object { $ServerModIds -notcontains $_ })

$missing = @($ids | Where-Object { -not $installed.ContainsKey($_) })
if ($missing) { throw "本機 Workshop 未安裝：$($missing -join '、')——先訂閱下載再跑" }

$chosenIds = @($ids | Where-Object { $VariantExclude -notcontains $_ })

# require 依賴閉包
$depIds = @(); $seen = @{}
$queue = New-Object System.Collections.Generic.Queue[string]
foreach ($id in $chosenIds) { $seen[$id] = $true; foreach ($r in $installed[$id].Requires) { $queue.Enqueue($r) } }
while ($queue.Count -gt 0) {
    $rid = $queue.Dequeue()
    if (-not $rid -or $seen.ContainsKey($rid) -or $ServerModIds -contains $rid) { continue }
    $seen[$rid] = $true
    if (-not $installed.ContainsKey($rid)) { throw "依賴未安裝：$rid" }
    $depIds += $rid
    foreach ($r2 in $installed[$rid].Requires) { $queue.Enqueue($r2) }
}

# --- 三行合併 ---
$cur = Get-Content -LiteralPath $ServerLinesFile -Encoding UTF8 | ForEach-Object { $_ -replace "`r$", '' }
$curMods = @(($cur | Where-Object { $_ -match '^Mods=' }) -replace '^Mods=', '' -split ';' |
    ForEach-Object { $_.Trim() } | Where-Object { $_ })
$curWs = @(($cur | Where-Object { $_ -match '^WorkshopItems=' }) -replace '^WorkshopItems=', '' -split ';' |
    ForEach-Object { $_.Trim() } | Where-Object { $_ })
if (-not $curMods -or -not $curWs) { throw "$ServerLinesFile 缺 Mods= 或 WorkshopItems= 行" }

$addMods = @('MinidoracatMiniMapModMapsFor42') + $depIds + $chosenIds
$curModIds = @($curMods | ForEach-Object { $_.TrimStart('\') })
$newMods = @($curMods)
foreach ($id in $addMods) { if ($curModIds -cnotcontains $id) { $newMods += "\$id" } }

$addWs = @($MapPackWorkshopId) + @($chosenIds + $depIds | ForEach-Object { $installed[$_].WorkshopId }) | Select-Object -Unique
$newWs = @($curWs)
foreach ($w in $addWs) { if ($curWs -notcontains $w) { $newWs += $w } }

$folders = @($chosenIds | ForEach-Object { Get-ModMapFolders $installed[$_].Root } | Where-Object { $_ } |
    Where-Object { $MapFolderExclude -notcontains $_ } | Select-Object -Unique | Sort-Object)
# 現行 Map= 中不屬本包 registry 的條目（管理員手動加的外部地圖）必須保留——加法原則，
# 移除地圖會 WorldDictionary 致命（docs/server-map-order-npe.md 附帶坑 2）
$curMap = @(($cur | Where-Object { $_ -match '^Map=' }) -replace '^Map=', '' -split ';' |
    ForEach-Object { $_.Trim() } | Where-Object { $_ })
$preserved = @($curMap | Where-Object {
    $folders -notcontains $_ -and $_ -ne 'Muldraugh, KY' -and $MapFolderExclude -notcontains $_ })
if ($preserved) { Write-Host "保留非本包既有 Map= 條目：$($preserved -join '、')" -ForegroundColor Yellow }
$orderedMap = @($MapOrderFirst | Where-Object { $folders -contains $_ }) +
    @($folders | Where-Object { $MapOrderFirst -notcontains $_ }) + $preserved + @('Muldraugh, KY')

$enc = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $OutDir 'pzserver_map_lines.conf'),
    (('Mods=' + ($newMods -join ';')) + "`n" + ('Map=' + ($orderedMap -join ';')) + "`n" +
     ('WorkshopItems=' + ($newWs -join ';')) + "`n"), $enc)

# --- bounds 表（全部註冊條目含變體；reset 腳本執行期依 Map= 過濾）---
$folderByMod = @{}
foreach ($id in $ids) {
    $fs = @(Get-ModMapFolders $installed[$id].Root | Where-Object { $MapFolderExclude -notcontains $_ })
    if ($fs.Count -eq 1) { $folderByMod[$id] = $fs[0] }
}
$rows = @{}
foreach ($mt in $entries) {
    $mod = $mt.Groups[1].Value
    if ($ServerModIds -contains $mod) { continue }
    $dir = if ($mt.Groups[2].Success) { $mt.Groups[2].Value } else { $folderByMod[$mod] }
    if (-not $dir) { Write-Warning "無資料夾對應（多資料夾 mod 需在 Lua 指定 mapDir）：$mod"; continue }
    $rows["$dir|$($mt.Groups[3].Value)|$($mt.Groups[4].Value)|$($mt.Groups[5].Value)|$($mt.Groups[6].Value)"] = $true
}
[IO.File]::WriteAllText((Join-Path $OutDir 'bounds_table.txt'),
    ((@($rows.Keys | Sort-Object) -join "`n") + "`n"), $enc)

Write-Host "Mods=: $($curMods.Count) -> $($newMods.Count)；WorkshopItems=: $($curWs.Count) -> $($newWs.Count)；Map=: $($orderedMap.Count)（含 vanilla）"
Write-Host "bounds 表: $($rows.Count) 條 -> $OutDir\bounds_table.txt（貼回 reset_map_mod_chunks.sh 的 BOUNDS 區塊）"
Write-Host "下一步：check_map_conflicts.ps1 驗證新 Map= → 上傳 conf → 停服跑 apply_map_config.sh → 開服"
