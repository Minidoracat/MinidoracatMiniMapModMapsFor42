# MinidoracatMiniMapModMapsFor42 Workshop 符號連結管理
# 用途：將開發目錄連結到 Zomboid Workshop 和 mods 目錄，方便本地測試和 Workshop 上傳

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# ============================================
# 路徑偵測（支援 bat 啟動器和直接執行兩種模式）
# ============================================
if ($env:PROJECT_ROOT) {
    # 從 bat 啟動器呼叫，使用傳入的專案根目錄
    $ProjectRoot = $env:PROJECT_ROOT.TrimEnd('\\')
} elseif ($PSScriptRoot) {
    # 直接執行 ps1，使用腳本所在目錄推算
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
} else {
    # Fallback：使用目前工作目錄
    $ProjectRoot = (Get-Location).Path
}
$ModSource = Join-Path $ProjectRoot "MOD\MinidoracatMiniMapModMapsFor42"
$ModContent = Join-Path $ModSource "Contents\mods\MinidoracatMiniMapModMapsFor42"

# Workshop 符號連結（用於上傳）
$WorkshopDir = Join-Path $env:UserProfile "Zomboid\Workshop"
$WorkshopLink = Join-Path $WorkshopDir "MinidoracatMiniMapModMapsFor42"

# Mods 符號連結（用於遊戲載入，PZ 優先從此處讀取；連結名 = mod id）
$ModsDir = Join-Path $env:UserProfile "Zomboid\mods"
$ModsLink = Join-Path $ModsDir "MinidoracatMiniMapModMapsFor42"

# 非 Steam 伺服器設定檔（-nosteam 伺服器不掃 Workshop，需把 mod id 寫進 ini 的 Mods=）
$ServerIniDir = Join-Path $env:UserProfile "Zomboid\Server"
# 伺服器契約（AGENTS.md）：Mods= 需同時含主 MOD 與本包；移除時只動本包，不動共用的主 MOD
$ServerModIds = @("MinidoracatMiniMapFor42", "MinidoracatMiniMapModMapsFor42")
$ServerModIdsOwn = @("MinidoracatMiniMapModMapsFor42")

# 地圖 MOD 清單的單一真相：Lua 註冊表（mapMod= 的 mod id）
$LuaRegistry = Join-Path $ModContent "42\media\lua\client\MinidoracatMiniMapModMaps.lua"

# 伺服器 Map= 順序約束（scripts/check_map_conflicts.ps1 推導）：引擎
# getZombieIntensityForChunk 混用 300/256 兩種 cell 網格，這幾張圖的 bg300 覆蓋圖會
# 「聲稱」蓋到鄰圖的 cell 卻拿不出 lotheader → NPE 崩服。排在最前面＝優先序最高，
# 掃描（只往低優先方向走）就永遠不會經過它們。新增地圖後重跑 check_map_conflicts.ps1 驗證。
$MapOrderFirst = @('AnruisiTown', 'Taylorsville', 'RaccoonCity', 'Camden County B42')

# 驗證 MOD 來源目錄（以 mod.info 為準；workshop.txt 由 Workshop 上傳流程才會產生）
if (-not (Test-Path (Join-Path $ModContent "42\mod.info"))) {
    Write-Host ""
    Write-Host "[錯誤] 找不到 MOD 來源目錄:" -ForegroundColor Red
    Write-Host "  $ModContent\42\mod.info" -ForegroundColor Red
    Write-Host ""
    Write-Host "請確認此腳本位於專案的 scripts/ 目錄下。"
    Read-Host "按 Enter 結束"
    exit 1
}

# 清理誤入 MOD 內容樹的 .omc 開發狀態目錄（AI 工具 hook 會就地寫入；
# git 已忽略，但 Workshop 上傳是整包目錄，出貨包內必須不存在）
Get-ChildItem -Path $ModSource -Recurse -Force -Directory -Filter ".omc" -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -Confirm:$false

# ============================================
# 功能函式
# ============================================

function Test-IsSymlink {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $false }
    $item = Get-Item $Path -Force -ErrorAction SilentlyContinue
    return ($null -ne $item.LinkType)
}

# 地圖 MOD 目錄名常含 [] 等萬用字元，一律走 -LiteralPath 版本
function Test-IsSymlinkL {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    return ($null -ne $item.LinkType)
}

# ============================================
# 地圖 MOD 盤點（Lua 註冊表 → Workshop 安裝掃描 → require 依賴閉包）
# ============================================

function Get-WorkshopContentDir {
    if ($script:WorkshopContentDir) { return $script:WorkshopContentDir }
    $steam = $null
    try { $steam = (Get-ItemProperty 'HKCU:\Software\Valve\Steam' -ErrorAction Stop).SteamPath } catch {}
    if (-not $steam) { return $null }
    $libs = @($steam)
    $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
    if (Test-Path -LiteralPath $vdf) {
        $libs += @((Select-String -Path $vdf -Pattern '"path"\s+"([^"]+)"' -AllMatches).Matches |
            ForEach-Object { $_.Groups[1].Value -replace '\\\\', '\' })
    }
    foreach ($lib in ($libs | Select-Object -Unique)) {
        $wc = Join-Path $lib 'steamapps\workshop\content\108600'
        if (Test-Path -LiteralPath $wc) { $script:WorkshopContentDir = $wc; return $wc }
    }
    return $null
}

# mod.info 版本優先序（同引擎）：最高 42.x > common > root；回傳 @{ Id=..; Requires=@(..) }
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
                # 引擎會去掉 require 條目的 \ 前綴（B42 風格）
                $req = @($Matches[1] -split '\s*,\s*' | ForEach-Object { $_.Trim().TrimStart('\') } | Where-Object { $_ })
            }
            return @{ Id = $id; Requires = $req }
        }
    }
    return $null
}

# 有 lotheader 的地圖資料夾（伺服器 Map= 需要；純出生點資料夾不算）
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
            $lot = Get-ChildItem -LiteralPath $mf.FullName -Filter *.lotheader -File -ErrorAction SilentlyContinue |
                Select-Object -First 1
            if ($lot) { $found += $mf.Name }
        }
    }
    return $found
}

# 盤點結果（快取）：MapMods=地圖 MOD、Deps=require 閉包的依賴（tile 包等）、Missing=未安裝 id
function Get-MapModInventory {
    if ($script:MapModInventory) { return $script:MapModInventory }
    if (-not (Test-Path -LiteralPath $LuaRegistry)) {
        Write-Host "  [地圖MOD] 找不到註冊清單：$LuaRegistry" -ForegroundColor Red
        return $null
    }
    $lua = Get-Content -LiteralPath $LuaRegistry -Raw -Encoding UTF8
    $ids = @([regex]::Matches($lua, 'mapMod\s*=\s*"([^"]+)"') |
        ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique |
        Where-Object { $ServerModIds -notcontains $_ })
    $wc = Get-WorkshopContentDir
    if (-not $wc) {
        Write-Host "  [地圖MOD] 找不到 Steam Workshop 內容目錄（108600）" -ForegroundColor Red
        return $null
    }
    Write-Host "  掃描已安裝 Workshop MOD（$wc）..." -ForegroundColor DarkGray
    $installed = @{}   # id -> @{ Root=..; Requires=@(..) }
    foreach ($item in (Get-ChildItem -LiteralPath $wc -Directory)) {
        $mr = Join-Path $item.FullName 'mods'
        if (-not (Test-Path -LiteralPath $mr)) { continue }
        foreach ($modDir in (Get-ChildItem -LiteralPath $mr -Directory)) {
            $info = Read-ModInfo $modDir.FullName
            if ($info -and $info.Id -and -not $installed.ContainsKey($info.Id)) {
                $installed[$info.Id] = @{ Root = $modDir.FullName; Requires = $info.Requires }
            }
        }
    }
    $mapMods = @(); $missing = @(); $depIds = @(); $seen = @{}
    $queue = New-Object System.Collections.Generic.Queue[string]
    foreach ($id in $ids) {
        if (-not $installed.ContainsKey($id)) { $missing += $id; continue }
        $entry = $installed[$id]
        $mapMods += [pscustomobject]@{
            Id = $id; Root = $entry.Root
            LinkName = Split-Path -Leaf $entry.Root
            MapFolders = @(Get-ModMapFolders $entry.Root)
        }
        $seen[$id] = $true
        foreach ($r in $entry.Requires) { $queue.Enqueue($r) }
    }
    while ($queue.Count -gt 0) {
        $rid = $queue.Dequeue()
        if (-not $rid -or $seen.ContainsKey($rid)) { continue }
        $seen[$rid] = $true
        if ($ServerModIds -contains $rid) { continue }
        if ($installed.ContainsKey($rid)) {
            $depIds += $rid
            foreach ($r2 in $installed[$rid].Requires) { $queue.Enqueue($r2) }
        } else {
            $missing += $rid
        }
    }
    $deps = @($depIds | ForEach-Object {
        [pscustomobject]@{ Id = $_; Root = $installed[$_].Root; LinkName = Split-Path -Leaf $installed[$_].Root }
    })
    $script:MapModInventory = @{ MapMods = $mapMods; Deps = $deps; Missing = @($missing | Select-Object -Unique) }
    return $script:MapModInventory
}

function Show-Status {
    Write-Host ""
    Write-Host "=== MOD 來源 ===" -ForegroundColor Cyan
    Write-Host "路徑: $ModSource"

    $checks = @(
        @{ File = "workshop.txt"; Desc = "workshop.txt（Workshop 上傳後才有）" }
        @{ File = "preview.png";  Desc = "preview.png" }
        @{ File = "Contents";     Desc = "Contents/" }
    )
    foreach ($c in $checks) {
        $p = Join-Path $ModSource $c.File
        if (Test-Path $p) {
            Write-Host "  [OK] $($c.Desc)" -ForegroundColor Green
        } else {
            Write-Host "  [缺少] $($c.Desc)" -ForegroundColor Yellow
        }
    }

    # 地圖包 pyramid zip 狀態（以 Lua 註冊表為準；渲染產物不進版控，缺少時用 pzmap 重渲）
    if (Test-Path -LiteralPath $LuaRegistry) {
        $luaTxt = Get-Content -LiteralPath $LuaRegistry -Raw -Encoding UTF8
        $zipNames = @([regex]::Matches($luaTxt, 'zip\s*=\s*"([^"]+)"') |
            ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique)
        $missingZips = @($zipNames | Where-Object {
            -not (Test-Path -LiteralPath (Join-Path $ModContent "42\media\minimap\$_")) })
        if ($missingZips.Count -eq 0) {
            Write-Host "  [OK] pyramid zip $($zipNames.Count)/$($zipNames.Count) 齊全" -ForegroundColor Green
        } else {
            $preview = @($missingZips | Select-Object -First 5) -join '、'
            if ($missingZips.Count -gt 5) { $preview += '…' }
            Write-Host "  [缺少] pyramid zip 缺 $($missingZips.Count)/$($zipNames.Count)：$preview（pzmap 重渲）" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [缺少] Lua 註冊清單 $LuaRegistry" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "=== 連結狀態 ===" -ForegroundColor Cyan

    # Workshop 連結
    Write-Host "  [Workshop] " -NoNewline
    if (-not (Test-Path $WorkshopLink)) {
        Write-Host "未掛載" -ForegroundColor DarkGray
    } elseif (Test-IsSymlink $WorkshopLink) {
        $target = (Get-Item $WorkshopLink -Force).Target
        Write-Host "已掛載 -> $target" -ForegroundColor Green
    } else {
        Write-Host "實體資料夾（非符號連結）" -ForegroundColor Yellow
    }

    # Mods 連結
    Write-Host "  [Mods]     " -NoNewline
    if (-not (Test-Path $ModsLink)) {
        Write-Host "未掛載" -ForegroundColor DarkGray
    } elseif (Test-IsSymlink $ModsLink) {
        $target = (Get-Item $ModsLink -Force).Target
        Write-Host "已掛載 -> $target" -ForegroundColor Green
    } else {
        Write-Host "實體資料夾（Steam 快取？）" -ForegroundColor Yellow
    }

    # 地圖 MOD 連結統計（不掃 Workshop——只數 mods 目錄裡指向 108600 的符號連結）
    $mapLinks = @(Get-ChildItem -LiteralPath $ModsDir -Directory -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.LinkType -and (('' + $_.Target) -match 'workshop[\\/]content[\\/]108600') })
    Write-Host "  [地圖MOD]  " -NoNewline
    if ($mapLinks.Count -gt 0) {
        Write-Host "mods 目錄內 Workshop 連結 $($mapLinks.Count) 個" -ForegroundColor Green
    } else {
        Write-Host "未掛載（選單 4/5 建立）" -ForegroundColor DarkGray
    }
    Write-Host ""
}

function New-SymlinkSafe {
    param([string]$LinkPath, [string]$Target, [string]$Label)

    if (Test-Path $LinkPath) {
        if (Test-IsSymlink $LinkPath) {
            $existing = (Get-Item $LinkPath -Force).Target
            Write-Host "  [$Label] 已掛載 -> $existing" -ForegroundColor Green
            return
        }
        # 實體資料夾（可能是 Steam 快取）—— 自動重新命名
        $bakPath = "$LinkPath.bak"
        if (Test-Path $bakPath) {
            Remove-Item $bakPath -Recurse -Force -ErrorAction SilentlyContinue
        }
        Rename-Item $LinkPath $bakPath -Force
        Write-Host "  [$Label] 已將舊資料夾重新命名為 .bak" -ForegroundColor Yellow
    }

    # 確保父目錄存在
    $parentDir = Split-Path -Parent $LinkPath
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    # 嘗試建立符號連結
    try {
        New-Item -ItemType SymbolicLink -Path $LinkPath -Target $Target -ErrorAction Stop | Out-Null
        Write-Host "  [$Label] 建立成功" -ForegroundColor Green
        Write-Host "           $LinkPath" -ForegroundColor DarkGray
        Write-Host "           -> $Target" -ForegroundColor DarkGray
        return $true
    } catch {
        return $false
    }
}

function New-SymlinkElevated {
    param([string]$LinkPath, [string]$Target, [string]$Label)
    try {
        Start-Process powershell.exe -Verb RunAs -Wait -ArgumentList @(
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-Command",
            "New-Item -ItemType SymbolicLink -Path '$LinkPath' -Target '$Target' -ErrorAction Stop | Out-Null"
        )
        if (Test-IsSymlink $LinkPath) {
            Write-Host "  [$Label] 建立成功（UAC）" -ForegroundColor Green
            return $true
        }
    } catch {}
    Write-Host "  [$Label] 建立失敗" -ForegroundColor Red
    return $false
}

# ============================================
# 非 Steam 伺服器設定檔（Mods=）
# ============================================

function Select-ServerIni {
    $inis = @(Get-ChildItem $ServerIniDir -Filter "*.ini" -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -eq ".ini" })
    if ($inis.Count -eq 0) {
        Write-Host "  [伺服器] 找不到伺服器設定檔（$ServerIniDir\*.ini），跳過" -ForegroundColor Yellow
        return $null
    }
    if ($inis.Count -eq 1) { return $inis[0].FullName }
    Write-Host ""
    for ($i = 0; $i -lt $inis.Count; $i++) {
        Write-Host "  [$($i + 1)] $($inis[$i].Name)" -NoNewline
        if ($inis[$i].Name -eq "servertest.ini") {
            # PZ_Test.ps1 的 $SERVER_NAME 固定 servertest，本機測試都走這份
            Write-Host "   <- PZ_Test.bat 主要測試伺服器" -ForegroundColor Green -NoNewline
        }
        Write-Host ""
    }
    $sel = Read-Host "請選擇伺服器設定檔（Enter 取消）"
    $n = 0
    if ([int]::TryParse($sel, [ref]$n) -and $n -ge 1 -and $n -le $inis.Count) {
        return $inis[$n - 1].FullName
    }
    return $null
}

# 通用 ini 清單更新：一次讀檔、套用多個鍵的加/移除、一次備份寫回。
# $Ops = @(@{ Key='Mods'; Add=@(id..); Remove=@(id..); BackslashStyle=$true; EnsureLast='' }, ...)
#   - BackslashStyle：B42 的 Mods= 條目帶 \ 前綴；比對去前綴，寫入沿用檔內既有風格
#   - EnsureLast：Map= 用——確保該條目存在且墊底（vanilla 'Muldraugh, KY'）
function Update-IniLists {
    param([string]$IniPath, [array]$Ops)

    # 讀取失敗（檔案被伺服器程序鎖住等）必須中止：$null 流下去會變成破壞性改寫
    try {
        # 編碼偵測：有 BOM → UTF-8 BOM；可嚴格 UTF-8 解碼 → UTF-8 無 BOM；否則系統 ANSI
        $bytes = [IO.File]::ReadAllBytes($IniPath)
        if ($bytes.Length -ge 2 -and (($bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) -or ($bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF))) {
            Write-Host "  [伺服器] 設定檔是 UTF-16/32 編碼，不支援，未變更" -ForegroundColor Red
            return
        }
        if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            $enc = New-Object System.Text.UTF8Encoding($true)
        } else {
            try {
                [void](New-Object System.Text.UTF8Encoding($false, $true)).GetString($bytes)
                $enc = New-Object System.Text.UTF8Encoding($false)
            } catch {
                # 不用 [Text.Encoding]::Default：pwsh 7 下它是 UTF-8，會把 ANSI 中文毀成 U+FFFD
                $enc = [System.Text.Encoding]::GetEncoding(
                    [System.Globalization.CultureInfo]::CurrentCulture.TextInfo.ANSICodePage)
            }
        }
        $lines = [IO.File]::ReadAllLines($IniPath, $enc)
    } catch {
        Write-Host "  [伺服器] 讀取設定檔失敗，未變更: $($_.Exception.Message)" -ForegroundColor Red
        return
    }

    $changed = $false
    $report = @()
    foreach ($op in $Ops) {
        $key = $op.Key
        $idx = -1
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match "^\s*$key\s*=") { $idx = $i; break }
        }
        $current = @()
        if ($idx -ge 0) {
            $current = @(($lines[$idx] -replace "^\s*$key\s*=", '') -split ';' |
                ForEach-Object { $_.Trim() } | Where-Object { $_ })
        }
        $updated = @($current)

        # 注意：hashtable 缺鍵時 $op.Add / $op.Remove 會解析成 .NET 方法（truthy），必須用 ContainsKey
        if ($op.ContainsKey('Remove') -and @($op.Remove).Count -gt 0) {
            $removeList = @($op.Remove)
            # 大小寫寬鬆以順便清掉手打錯大小寫的殘留
            $updated = @($updated | Where-Object { $removeList -notcontains $_.TrimStart('\') })
        }
        if ($op.ContainsKey('Add') -and @($op.Add).Count -gt 0) {
            $prefix = ''
            if ($op.BackslashStyle) {
                $prefix = '\'
                if ($updated.Count -gt 0 -and @($updated | Where-Object { $_.StartsWith('\') }).Count -eq 0) {
                    $prefix = ''
                }
            }
            $existingIds = @($updated | ForEach-Object { $_.TrimStart('\') })
            # PZ 的 mod id 比對是 case-sensitive：大小寫不同視為不存在，補上正確大小寫的條目
            foreach ($id in $op.Add) {
                if ($existingIds -cnotcontains $id) { $updated += "$prefix$id" }
            }
        }
        # OrderFirst：把指定條目拉到最前（順序照清單），其餘保持原相對順序——
        # 純 Add 只會 append，既有錯序也要能矯正
        if ($op.ContainsKey('OrderFirst') -and @($op.OrderFirst).Count -gt 0) {
            $of = @($op.OrderFirst)
            $updated = @($of | Where-Object { $updated -contains $_ }) +
                @($updated | Where-Object { $of -notcontains $_ })
        }
        if ($op.EnsureLast -and $updated.Count -gt 0) {
            $updated = @($updated | Where-Object { $_ -ne $op.EnsureLast }) + @($op.EnsureLast)
        }

        if (($updated -join ';') -ne ($current -join ';')) {
            $changed = $true
            $newLine = "$key=" + ($updated -join ';')
            if ($idx -ge 0) { $lines[$idx] = $newLine } else { $lines += $newLine }
            $report += $newLine
        }
    }

    if (-not $changed) {
        Write-Host "  [伺服器] $(Split-Path -Leaf $IniPath) 無需變更" -ForegroundColor DarkGray
        return
    }

    # 伺服器啟動/關閉時會整檔回寫 ini（AGENTS.md），執行中寫入必被覆蓋——同名伺服器在跑就拒絕（偵測失敗放行）
    $serverName = [IO.Path]::GetFileNameWithoutExtension($IniPath)
    try {
        $namePattern = '-servername\s+' + [regex]::Escape($serverName) + '(\s|$)'
        $running = @(Get-CimInstance Win32_Process -Filter "Name='java.exe'" -ErrorAction Stop |
            Where-Object { $_.CommandLine -match 'zombie\.network\.GameServer' -and
                ($_.CommandLine -match $namePattern -or
                 ($serverName -eq 'servertest' -and $_.CommandLine -notmatch '-servername\s')) })
    } catch { $running = @() }
    if ($running.Count -gt 0) {
        Write-Host "  [伺服器] $serverName 伺服器正在執行，關閉時會整檔回寫覆蓋——請先停止伺服器再寫入" -ForegroundColor Red
        return
    }

    # 備份失敗就不寫；寫入失敗要明講——不能讓紅字例外後面跟著綠色成功訊息
    try {
        Copy-Item $IniPath "$IniPath.bak" -Force -ErrorAction Stop
    } catch {
        Write-Host "  [伺服器] 備份失敗，取消寫入: $($_.Exception.Message)" -ForegroundColor Red
        return
    }
    try {
        [IO.File]::WriteAllLines($IniPath, $lines, $enc)
    } catch {
        Write-Host "  [伺服器] 寫入失敗: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "           原檔已備份為 .ini.bak，可還原" -ForegroundColor Yellow
        return
    }
    Write-Host "  [伺服器] 已更新 $(Split-Path -Leaf $IniPath)（原檔備份為 .ini.bak）" -ForegroundColor Green
    foreach ($r in $report) {
        $shown = if ($r.Length -gt 200) { $r.Substring(0, 200) + '...' } else { $r }
        Write-Host "           $shown" -ForegroundColor DarkGray
    }
}

function Update-ServerIniMods {
    param([string]$IniPath, [switch]$Remove)
    if ($Remove) {
        # 只移除本 repo 擁有的 id，不動共用/主 MOD
        Update-IniLists -IniPath $IniPath -Ops @(@{ Key = 'Mods'; Remove = $ServerModIdsOwn; BackslashStyle = $true })
    } else {
        Update-IniLists -IniPath $IniPath -Ops @(@{ Key = 'Mods'; Add = $ServerModIds; BackslashStyle = $true })
    }
}

function Invoke-ServerIniPrompt {
    param([switch]$Remove)
    $question = if ($Remove) {
        "是否同時從非 Steam 伺服器設定檔的 Mods= 移除？(y/N)"
    } else {
        "是否同時把 mod id 寫入非 Steam 伺服器設定檔的 Mods=？(y/N)"
    }
    $ans = Read-Host $question
    if ($ans -notmatch '^[Yy]') { return }
    $ini = Select-ServerIni
    if ($ini) {
        Update-ServerIniMods -IniPath $ini -Remove:$Remove
    } else {
        Write-Host "  [伺服器] 已取消，設定檔未變更" -ForegroundColor DarkGray
    }
}

# ============================================
# 地圖 MOD 掛載／卸載（mods 連結 ＋ 伺服器 Mods=/Map=）
# ============================================

# MOD 目錄名常帶 []（New-Item 的 -Path 會當萬用字元）與彎引號 ’（單引號字串終結符）——
# 一律走 cmd mklink：對這些字元完全無感，名稱不需要進任何 PowerShell 字串程式碼。
# 用 junction（/j）不用 symlink（/d）：免管理員權限／開發人員模式，遊戲讀取無差別
function New-DirSymlink {
    param([string]$LinkPath, [string]$TargetPath)
    & cmd.exe /d /c mklink /j "$LinkPath" "$TargetPath" 2>$null | Out-Null
    return (Test-IsSymlinkL $LinkPath)
}

function Mount-MapModLinks {
    param($Inventory)
    # 地圖 MOD 與 tile 依賴包都要連（-nosteam 伺服器/客戶端只掃 Zomboid\mods）
    $all = @($Inventory.MapMods) + @($Inventory.Deps)
    $ok = 0; $skip = 0; $failed = @()
    foreach ($m in $all) {
        $link = Join-Path $ModsDir $m.LinkName
        if (Test-Path -LiteralPath $link) {
            if (Test-IsSymlinkL $link) { $skip++ } else {
                Write-Host "  [連結] $($m.LinkName)：已有實體資料夾，跳過（手動安裝？）" -ForegroundColor Yellow
            }
            continue
        }
        if (New-DirSymlink -LinkPath $link -TargetPath $m.Root) { $ok++ } else { $failed += $m }
    }
    if ($failed.Count -gt 0) {
        # 逐個 UAC 會按到手軟——寫「資料檔＋讀檔迴圈」一次提權批次建立
        # （名稱只存在資料檔裡，不嵌入腳本程式碼 → 免除引號/萬用字元地雷）
        Write-Host "  [連結] $($failed.Count) 個需要管理員權限，批次提權建立..." -ForegroundColor Yellow
        $dataFile = Join-Path $env:TEMP "link_mapmods_$PID.txt"
        # '|' 是 Windows 檔名非法字元，安全作分隔
        $failed | ForEach-Object { (Join-Path $ModsDir $_.LinkName) + '|' + $_.Root } |
            Set-Content -Path $dataFile -Encoding UTF8
        $tmp = Join-Path $env:TEMP "link_mapmods_$PID.ps1"
        @(
            "`$lines = Get-Content -LiteralPath '$dataFile' -Encoding UTF8",
            'foreach ($ln in $lines) {',
            '    $p = $ln -split ''\|'', 2',
            '    & cmd.exe /d /c mklink /d "$($p[0])" "$($p[1])" | Out-Null',
            '}'
        ) | Set-Content -Path $tmp -Encoding UTF8
        try {
            Start-Process powershell.exe -Verb RunAs -Wait -ArgumentList @(
                "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $tmp)
        } catch {}
        Remove-Item $tmp, $dataFile -Force -ErrorAction SilentlyContinue
        $stillFailed = @($failed | Where-Object { -not (Test-IsSymlinkL (Join-Path $ModsDir $_.LinkName)) })
        $ok += ($failed.Count - $stillFailed.Count)
        foreach ($m in $stillFailed) { Write-Host "  [連結] $($m.LinkName) 建立失敗" -ForegroundColor Red }
    }
    Write-Host "  [連結] 新建 $ok、已存在 $skip（共 $($all.Count) 個 MOD）" -ForegroundColor Green
}

function Dismount-MapModLinks {
    param($Inventory)
    # 只移除地圖 MOD 的連結；tile 依賴包可能被其他 MOD 共用，保留
    $removed = 0
    foreach ($m in @($Inventory.MapMods)) {
        $link = Join-Path $ModsDir $m.LinkName
        if (-not (Test-Path -LiteralPath $link)) { continue }
        if (-not (Test-IsSymlinkL $link)) {
            Write-Host "  [連結] $($m.LinkName)：實體資料夾，跳過（請手動處理）" -ForegroundColor Yellow
            continue
        }
        # 保險絲：只刪指向 Workshop 內容目錄的連結
        $target = (Get-Item -LiteralPath $link -Force).Target
        if ($target -notmatch 'workshop[\\/]content[\\/]108600') {
            Write-Host "  [連結] $($m.LinkName)：指向非 Workshop 目錄，跳過" -ForegroundColor Yellow
            continue
        }
        try { (Get-Item -LiteralPath $link -Force).Delete(); $removed++ } catch {
            Write-Host "  [連結] $($m.LinkName) 移除失敗: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Write-Host "  [連結] 已移除 $removed 個地圖 MOD 連結（tile 依賴包連結保留）" -ForegroundColor Green
}

function Invoke-MapModsServerWrite {
    param($Inventory, [switch]$Remove)
    $ini = Select-ServerIni
    if (-not $ini) { Write-Host "  [伺服器] 已取消，設定檔未變更" -ForegroundColor DarkGray; return }
    $mapIds  = @($Inventory.MapMods | ForEach-Object { $_.Id })
    $folders = @($Inventory.MapMods | ForEach-Object { $_.MapFolders } | Where-Object { $_ } |
        Select-Object -Unique | Sort-Object)
    if ($Remove) {
        Update-IniLists -IniPath $ini -Ops @(
            @{ Key = 'Mods'; Remove = $mapIds; BackslashStyle = $true },
            @{ Key = 'Map';  Remove = $folders; EnsureLast = 'Muldraugh, KY' }
        )
        Write-Host "  [提示] tile 依賴包的 Mods= 條目保留（可能被其他 MOD 共用；純材質包無副作用）" -ForegroundColor DarkGray
    } else {
        $depIds = @($Inventory.Deps | ForEach-Object { $_.Id })
        Update-IniLists -IniPath $ini -Ops @(
            @{ Key = 'Mods'; Add = @($ServerModIds) + $depIds + $mapIds; BackslashStyle = $true },
            @{ Key = 'Map';  Add = $folders; OrderFirst = $MapOrderFirst; EnsureLast = 'Muldraugh, KY' }
        )
        Write-Host "  [提示] Map= 順序＝優先序（先者為大、vanilla 墊底）；已自動把已知會" -ForegroundColor DarkGray
        Write-Host "         崩服的 bg300 肇事圖排到最前（詳見 check_map_conflicts.ps1）" -ForegroundColor DarkGray
    }
}

function Show-MapModSummary {
    param($Inventory)
    $folderCount = @($Inventory.MapMods | ForEach-Object { $_.MapFolders } | Where-Object { $_ }).Count
    Write-Host ""
    Write-Host "  地圖 MOD：$(@($Inventory.MapMods).Count) 個（地圖資料夾 $folderCount 個）＋ tile 依賴 $(@($Inventory.Deps).Count) 個" -ForegroundColor Cyan
    if (@($Inventory.Missing).Count -gt 0) {
        Write-Host "  [警告] 未安裝（Workshop 未訂閱/未下載）：$($Inventory.Missing -join '、')" -ForegroundColor Yellow
    }
}

function Invoke-MapMods {
    param([string]$Mode)
    Write-Host ""
    $inv = Get-MapModInventory
    if (-not $inv) { return }
    Show-MapModSummary $inv
    Write-Host ""
    switch ($Mode) {
        'link-only'     { Mount-MapModLinks $inv }
        'link-server'   { Mount-MapModLinks $inv; Invoke-MapModsServerWrite $inv }
        'server-remove' { Invoke-MapModsServerWrite $inv -Remove }
        'remove-all'    { Invoke-MapModsServerWrite $inv -Remove; Dismount-MapModLinks $inv }
    }
}

function Mount-Workshop {
    Write-Host ""
    Write-Host "正在建立符號連結..." -ForegroundColor Cyan
    Write-Host ""

    # 嘗試不需提權建立兩個連結
    $ws = New-SymlinkSafe -LinkPath $WorkshopLink -Target $ModSource -Label "Workshop"
    $md = New-SymlinkSafe -LinkPath $ModsLink -Target $ModContent -Label "Mods"

    # 如果任一個失敗，嘗試 UAC 提權
    $needElevate = @()
    if ($ws -eq $false) { $needElevate += @{ Link=$WorkshopLink; Target=$ModSource; Label="Workshop" } }
    if ($md -eq $false) { $needElevate += @{ Link=$ModsLink; Target=$ModContent; Label="Mods" } }

    if ($needElevate.Count -gt 0) {
        Write-Host ""
        Write-Host "[提示] 需要管理員權限，正在請求提升..." -ForegroundColor Yellow
        foreach ($item in $needElevate) {
            New-SymlinkElevated -LinkPath $item.Link -Target $item.Target -Label $item.Label
        }
    }

    Write-Host ""
    if ((Test-IsSymlink $WorkshopLink) -and (Test-IsSymlink $ModsLink)) {
        Write-Host "[全部完成] 現在可以在 PZ 遊戲中測試此 MOD。" -ForegroundColor Green
    } else {
        Write-Host "[部分完成] 請檢查上方狀態。" -ForegroundColor Yellow
        Write-Host "替代方案：啟用 Windows 開發人員模式後即可免管理員建立連結：" -ForegroundColor Yellow
        Write-Host "  設定 -> 系統 -> 開發人員專用 -> 開發人員模式" -ForegroundColor Yellow
    }

    Write-Host ""
    if ((Test-IsSymlink $ModsLink) -and (Test-Path (Join-Path $ModsDir "MinidoracatMiniMapFor42"))) {
        Invoke-ServerIniPrompt
    } else {
        Write-Host "[提示] Mods 連結未建立或主 MOD 不在 mods 目錄，略過伺服器設定檔寫入詢問" -ForegroundColor Yellow
    }
    Write-Host ""
}

function Remove-SymlinkSafe {
    param([string]$LinkPath, [string]$Label)

    if (-not (Test-Path $LinkPath)) {
        Write-Host "  [$Label] 不存在，跳過" -ForegroundColor DarkGray
        return
    }

    if (-not (Test-IsSymlink $LinkPath)) {
        Write-Host "  [$Label] 是實體資料夾，跳過（請手動處理）" -ForegroundColor Yellow
        return
    }

    try {
        (Get-Item $LinkPath -Force).Delete()
        Write-Host "  [$Label] 已移除" -ForegroundColor Green
    } catch {
        Write-Host "  [$Label] 需要提權移除..." -ForegroundColor Yellow
        try {
            Start-Process powershell.exe -Verb RunAs -Wait -ArgumentList @(
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                "(Get-Item '$LinkPath' -Force).Delete()"
            )
            if (-not (Test-Path $LinkPath)) {
                Write-Host "  [$Label] 已移除（UAC）" -ForegroundColor Green
            } else {
                Write-Host "  [$Label] 移除失敗" -ForegroundColor Red
            }
        } catch {
            Write-Host "  [$Label] 移除失敗: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

function Dismount-Workshop {
    Write-Host ""
    Write-Host "正在移除符號連結..." -ForegroundColor Cyan
    Write-Host ""
    Remove-SymlinkSafe -LinkPath $WorkshopLink -Label "Workshop"
    Remove-SymlinkSafe -LinkPath $ModsLink -Label "Mods"

    Write-Host ""
    Invoke-ServerIniPrompt -Remove
    Write-Host ""
}

# ============================================
# 主選單
# ============================================
$Host.UI.RawUI.WindowTitle = "MinidoracatMiniMapModMapsFor42 Workshop 連結管理"

while ($true) {
    Clear-Host
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  MinidoracatMiniMapModMapsFor42 符號連結管理" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Workshop: $WorkshopLink"
    Write-Host "  Mods:     $ModsLink"
    Write-Host ""
    Write-Host "  [1] 掛載本包 - 建立符號連結（Workshop + Mods）"
    Write-Host "  [2] 卸載本包 - 移除符號連結（Workshop + Mods）"
    Write-Host "  [3] 查看目前狀態"
    Write-Host ""
    Write-Host "  --- 支援的地圖 MOD（依 Lua 註冊清單）---" -ForegroundColor DarkCyan
    Write-Host "  [4] 地圖 MOD：連結＋寫入伺服器（mods 連結 + Mods= + Map=）"
    Write-Host "  [5] 地圖 MOD：只建 mods 連結（不動伺服器設定）"
    Write-Host "  [6] 地圖 MOD：只從伺服器移除（Mods= + Map=；連結保留）"
    Write-Host "  [7] 地圖 MOD：全部移除（伺服器設定＋連結）"
    Write-Host ""
    Write-Host "  [Q] 離開"
    Write-Host ""
    $choice = Read-Host "請選擇"

    switch ($choice.ToUpper()) {
        "1" { Mount-Workshop; Read-Host "按 Enter 繼續" }
        "2" { Dismount-Workshop; Read-Host "按 Enter 繼續" }
        "3" { Show-Status; Read-Host "按 Enter 繼續" }
        "4" { Invoke-MapMods -Mode 'link-server'; Read-Host "按 Enter 繼續" }
        "5" { Invoke-MapMods -Mode 'link-only'; Read-Host "按 Enter 繼續" }
        "6" { Invoke-MapMods -Mode 'server-remove'; Read-Host "按 Enter 繼續" }
        "7" { Invoke-MapMods -Mode 'remove-all'; Read-Host "按 Enter 繼續" }
        "Q" { Write-Host ""; Write-Host "再見！"; exit 0 }
    }
}
