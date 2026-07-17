# check_map_conflicts.ps1 — 離線偵測 B42 伺服器多地圖 NPE 崩服條件
#
# 引擎 bug（42.19 反編譯查證）：LotHeader.getZombieIntensityForChunk（LotHeader.java:63-83）
# 用 B41 的 300 格網格（MapFiles.bgHasCell300，MapFiles.java:120-135）檢查「哪個地圖目錄
# 涵蓋此處」，命中後卻用 B42 的 256 格座標拿 lotheader——兩網格對不齊時拿到 null 直接 NPE：
#   java.lang.NullPointerException: ... "lotHeader2" is null at LotHeader.getZombieIntensityForChunk
# 觸發時機：IsoMetaGrid.CreateStep2 建房間（含跨 cell 建築的 addRoomsToAdjacentCells），
# vanilla 建築跨進 MOD 擁有的 cell 也會觸發。
#
# 修法：查詢從 cell 擁有者的 priority 只往「低優先」掃——把肇事圖排在 Map= 最前面
# （優先序最高），掃描就永遠不會經過它們（見 link_workshop.ps1 的 $MapOrderFirst）。
#
# 用法：新增支援地圖後執行本腳本；「危險組合」非 0 就把 culprit 圖加進 $MapOrderFirst
# 再重跑驗證（culprit 需排在 owner 之前；提前可能改變 cell 擁有權，迭代至歸零）。
param(
    [string]$ServerIni = "$env:USERPROFILE\Zomboid\Server\servertest.ini",
    [string]$GamePath = 'D:\SteamLibrary\steamapps\common\ProjectZomboid',
    [string]$PoiExe = 'D:\github\MinidoracatMapRendering\target\release\pzmap.exe',
    [string]$ModsDir = "$env:USERPROFILE\Zomboid\mods"
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if (-not (Test-Path -LiteralPath $PoiExe)) { throw "找不到 pzmap.exe（$PoiExe）——MapRendering repo cargo build --release" }
$tmpDir = Join-Path $env:TEMP 'pz_map_conflict_poi'
New-Item -ItemType Directory -Force $tmpDir | Out-Null

# 1) Map= 順序（= MapFiles priority：先者為大）
$mapLine = (Get-Content -LiteralPath $ServerIni | Where-Object { $_ -match '^\s*Map\s*=' }) -replace '^\s*Map\s*=', ''
$entries = @($mapLine -split ';' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
"Map= 條目數: $($entries.Count)"

# 2) 條目 → 地圖資料夾（vanilla 從遊戲目錄；其餘掃 Zomboid\mods 下各 mod 的版本資料夾）
$folderPath = @{ 'Muldraugh, KY' = (Join-Path $GamePath 'media\maps\Muldraugh, KY') }
foreach ($modDir in (Get-ChildItem -LiteralPath $ModsDir -Directory -Force -ErrorAction SilentlyContinue)) {
    $mediaDirs = @()
    foreach ($sub in (Get-ChildItem -LiteralPath $modDir.FullName -Directory -ErrorAction SilentlyContinue)) {
        $p = Join-Path $sub.FullName 'media\maps'
        if (Test-Path -LiteralPath $p) { $mediaDirs += $p }
    }
    $rootMaps = Join-Path $modDir.FullName 'media\maps'
    if (Test-Path -LiteralPath $rootMaps) { $mediaDirs += $rootMaps }
    foreach ($md in $mediaDirs) {
        foreach ($mf in (Get-ChildItem -LiteralPath $md -Directory -ErrorAction SilentlyContinue)) {
            if (-not $folderPath.ContainsKey($mf.Name)) { $folderPath[$mf.Name] = $mf.FullName }
        }
    }
}
$missing = @($entries | Where-Object { -not $folderPath.ContainsKey($_) })
if ($missing) { "[警告] 找不到資料夾（mods 連結未建？）: $($missing -join '、')" }

# 3) 每目錄：cellSet / bg300（MapFiles.java:120-131，float 除法）
$dirs = @()
foreach ($e in $entries) {
    if (-not $folderPath.ContainsKey($e)) { continue }
    $cells = New-Object 'System.Collections.Generic.HashSet[string]'
    $minX = [int]::MaxValue; $minY = [int]::MaxValue; $maxX = [int]::MinValue; $maxY = [int]::MinValue
    foreach ($lh in (Get-ChildItem -LiteralPath $folderPath[$e] -Filter *.lotheader -File)) {
        if ($lh.BaseName -match '^(\d+)_(\d+)$') {
            $cx = [int]$Matches[1]; $cy = [int]$Matches[2]
            [void]$cells.Add("$cx,$cy")
            if ($cx -lt $minX) { $minX = $cx }; if ($cy -lt $minY) { $minY = $cy }
            if ($cx -gt $maxX) { $maxX = $cx }; if ($cy -gt $maxY) { $maxY = $cy }
        }
    }
    if ($cells.Count -eq 0) { continue }
    $min300X = [int][Math]::Floor($minX * 256.0 / 300.0); $min300Y = [int][Math]::Floor($minY * 256.0 / 300.0)
    $max300X = [int][Math]::Floor(($maxX + 1) * 256.0 / 300.0); $max300Y = [int][Math]::Floor(($maxY + 1) * 256.0 / 300.0)
    $bg = New-Object 'System.Collections.Generic.HashSet[string]'
    for ($c3y = $min300Y; $c3y -le $max300Y; $c3y++) {
        for ($c3x = $min300X; $c3x -le $max300X; $c3x++) {
            $c256x = [int][Math]::Floor($c3x * 300.0 / 256.0); $c256y = [int][Math]::Floor($c3y * 300.0 / 256.0)
            if ($cells.Contains("$c256x,$c256y") -and $cells.Contains("$($c256x+1),$($c256y+1)")) {
                [void]$bg.Add("$c3x,$c3y")
            }
        }
    }
    $dirs += [pscustomobject]@{ Name = $e; Cells = $cells; Bg = $bg
        Min300X = $min300X; Min300Y = $min300Y; Max300X = $max300X; Max300Y = $max300Y }
}
"載入目錄: $($dirs.Count)（含 vanilla）"

# 4) cell 擁有者（Map= 首見者）＋危險 (cell, c300) 判定
$ownerIdx = @{}
for ($i = 0; $i -lt $dirs.Count; $i++) {
    foreach ($c in $dirs[$i].Cells) { if (-not $ownerIdx.ContainsKey($c)) { $ownerIdx[$c] = $i } }
}
$dangerous = New-Object 'System.Collections.Generic.HashSet[string]'
$dangerInfo = @{}
foreach ($cellKey in $ownerIdx.Keys) {
    $parts = $cellKey -split ','
    $cx = [int]$parts[0]; $cy = [int]$parts[1]
    $oi = $ownerIdx[$cellKey]
    # 一個 256-cell 的 chunk 最多落在 2x2 個 c300
    $c3xs = @([int][Math]::Floor($cx * 256.0 / 300.0), [int][Math]::Floor((($cx + 1) * 256.0 - 8) / 300.0)) | Select-Object -Unique
    $c3ys = @([int][Math]::Floor($cy * 256.0 / 300.0), [int][Math]::Floor((($cy + 1) * 256.0 - 8) / 300.0)) | Select-Object -Unique
    foreach ($c3y in $c3ys) { foreach ($c3x in $c3xs) {
        for ($j = $oi; $j -lt $dirs.Count; $j++) {
            $d = $dirs[$j]
            if ($c3x -lt $d.Min300X -or $c3x -gt $d.Max300X -or $c3y -lt $d.Min300Y -or $c3y -gt $d.Max300Y) { continue }
            if (-not $d.Bg.Contains("$c3x,$c3y")) { continue }
            if (-not $d.Cells.Contains($cellKey)) {
                $k = "$cellKey|$c3x,$c3y"
                [void]$dangerous.Add($k)
                $dangerInfo[$k] = "owner=$($dirs[$oi].Name) culprit=$($d.Name)"
            }
            break   # 第一個 bg 命中者決定結果
        }
    } }
}
"危險 (cell,c300) 組合: $($dangerous.Count)"
foreach ($k in $dangerous) { "  $k  $($dangerInfo[$k])" }

# 5) poi 建築掃描（vanilla 也掃：原版建築跨進 MOD cell 一樣觸發）
$hits = @{}
$n = 0
foreach ($e in $entries) {
    if (-not $folderPath.ContainsKey($e)) { continue }
    $n++
    $poiOut = Join-Path $tmpDir "poi_$n.json"
    & $PoiExe poi --maps-dir $folderPath[$e] --out $poiOut 2>$null | Out-Null
    if (-not (Test-Path -LiteralPath $poiOut)) { continue }
    $blds = Get-Content -LiteralPath $poiOut -Raw | ConvertFrom-Json
    foreach ($b in $blds) {
        $chX0 = [int][Math]::Floor($b.x / 8); $chX1 = [int][Math]::Floor(($b.x + $b.width - 1) / 8)
        $chY0 = [int][Math]::Floor($b.y / 8); $chY1 = [int][Math]::Floor(($b.y + $b.height - 1) / 8)
        for ($chy = $chY0; $chy -le $chY1; $chy++) {
            for ($chx = $chX0; $chx -le $chX1; $chx++) {
                $cx = [int][Math]::Floor($chx / 32.0); $cy = [int][Math]::Floor($chy / 32.0)
                $c3x = [int][Math]::Floor(($chx * 8) / 300.0); $c3y = [int][Math]::Floor(($chy * 8) / 300.0)
                $k = "$cx,$cy|$c3x,$c3y"
                if ($dangerous.Contains($k)) {
                    $tag = "$e :: $($b.building_id) @cell($cx,$cy) [$($dangerInfo[$k])]"
                    if (-not $hits.ContainsKey($tag)) { $hits[$tag] = $true }
                }
            }
        }
    }
}
""
if ($dangerous.Count -eq 0) {
    "[OK] 無危險組合——此 Map= 順序可安全開服"
} else {
    "=== 會實際觸發 NPE 的建築 ==="
    if ($hits.Count -eq 0) { "  （目前無建築踩到——屬潛在雷，仍建議把 culprit 提前排除）" }
    $hits.Keys | Sort-Object | ForEach-Object { "  $_" }
    ""
    "[修法] 把上列 culprit 圖加入 link_workshop.ps1 的 `$MapOrderFirst（culprit 必須排在 owner 之前），重寫 Map= 後重跑本腳本驗證歸零"
}
