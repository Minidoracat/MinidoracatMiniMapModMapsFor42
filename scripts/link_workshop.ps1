# MinidoracatMiniMapModMapsFor42 開發同步管理（本 repo 專屬版：含地圖 MOD 全量掛載）
# 用途：本包（與主 MOD）以「實體副本」同步到 Zomboid\Workshop 與 Zomboid\mods，方便本地測試和 Workshop 上傳
# 為什麼本包不再建符號連結：PZ 會把 Workshop/mods 路徑反解成真實路徑再映射 MOD 來源，
#   link 會讓 A MOD 的來源被串成別的 repo 的內容（已用真 jar 驗證）——家族自身 MOD 一律走 sync_mod.ps1。
#   選單 4-7 的「第三方地圖 MOD」仍走 Steam Workshop 目錄的 junction：來源是 Steam 唯讀安裝目錄、
#   數十 GB 圖資，複製既無意義又塞爆硬碟，且不是家族 repo（不受同步引擎管轄）。

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

# Zomboid 快取根（同步目的地、地圖 MOD 連結與伺服器設定都由此推導）
$ZomboidDir = Join-Path $env:UserProfile "Zomboid"

# Workshop 副本（用於上傳；目錄名 = 資料夾名）
$WorkshopDest = Join-Path (Join-Path $ZomboidDir "Workshop") "MinidoracatMiniMapModMapsFor42"

# mods 副本（no-Steam 測試也可讀取；目錄名 = mod id）
$ModsDir = Join-Path $ZomboidDir "mods"
$ModsDest = Join-Path $ModsDir "MinidoracatMiniMapModMapsFor42"

# 非 Steam 伺服器設定檔（-nosteam 伺服器不掃 Workshop，需把 mod id 寫進 ini 的 Mods=）
$ServerIniDir = Join-Path $ZomboidDir "Server"
# 伺服器契約（AGENTS.md）：Mods= 需同時含主 MOD 與本包；移除時只動本包，不動共用的主 MOD
$ServerModIds = @("MinidoracatMiniMapFor42", "MinidoracatMiniMapModMapsFor42")
$ServerModIdsOwn = @("MinidoracatMiniMapModMapsFor42")

# 地圖測試專用伺服器：全部地圖 MOD 只寫進這份，servertest.ini 保持乾淨（測其他 MOD 用）。
# 存檔目錄與埠都與 servertest 分離（Saves\Multiplayer\maptest、16271/16272）——
# 兩份可各自留存檔，也不會在忘記關掉另一個時撞埠。
$MapTestServerName = "maptest"
$MapTestIniPath = Join-Path $ServerIniDir "$MapTestServerName.ini"
$BaseServerName = "servertest"   # 缺 maptest 時的複製來源

# 地圖 MOD 清單的單一真相：Lua 註冊表（mapMod= 的 mod id）
$LuaRegistry = Join-Path $ModContent "42\media\lua\client\MinidoracatMiniMapModMaps.lua"

# 伺服器 Map= 順序約束（scripts/check_map_conflicts.ps1 推導）：引擎
# getZombieIntensityForChunk 混用 300/256 兩種 cell 網格，這幾張圖的 bg300 覆蓋圖會
# 「聲稱」蓋到鄰圖的 cell 卻拿不出 lotheader → NPE 崩服。排在最前面＝優先序最高，
# 掃描（只往低優先方向走）就永遠不會經過它們。新增地圖後重跑 check_map_conflicts.ps1 驗證。
# Coryerdon 需在 Taylorsville 後（作者聲明）、Greenport 前（bg300 潛在雷）——列表順序即滿足
$MapOrderFirst = @('AnruisiTown', 'Taylorsville', 'Coryerdon B42', 'RaccoonCity', 'Camden County B42', 'Clover Lake')  # Clover Lake：作者要求優先（歷史：曾因 Sector-7 公路 basement 衝突；Sector-7 已下架移除）

# 翻譯 MOD 必須排在 Mods= 最後：PZ 的 Mods= 順序＝載入序，**後載入者覆蓋先載入者**
# （log 的 mod "X" overrides ... 就是這個機制）。翻譯包排前面會被後面的 MOD 蓋掉。
# 順序＝模組漢化在前、本體漢化最後（本體翻譯是絕對權威）。
# 只重排既有條目、不新增：沒裝該漢化就不該被硬塞進 Mods=（EnsureLast 會硬塞，故不能用它）。
$TranslationModsLast = @('CatModLangFor42', 'CatLangFor42')

# 伺服器排除清單（mod id）：選單 4/5 不建連結、不寫入 Mods=/Map=，且選單 4 會把既有
# 條目順手拔掉（自癒）；選單 6/7 的移除照常涵蓋。想排除哪張圖就把它的 mod id 加進來。
# 注意：已在存檔啟用過的圖拔掉會觸發 WorldDictionary 錯誤——排除請配合開新存檔。
$MapModExclude = @(
    'IrisEyot',   # 鳶尾島
    # tikitown：2026-09-09 no-steam 多人重測仍在 GoKartIdle.xml 動畫校驗失敗，依使用者要求恢復排除。
    # 資源檔實際存在，但 AdvancedAnimator.buildChecksum 無法由資源索引解析路徑；不視為道路座標問題。
    # 需另查引擎路徑解析與本機連結環境，不能只歸因為檔名大小寫。
    # 產出小寫絕對路徑 → getAbsolutePath 查表 miss → buildChecksum 拋
    # IllegalStateException → GameServer.doMinimumInit 中斷 → lua 環境沒建起
    # （SpawnRegionMgr undefined）→ 地圖資料夾清單全空 → worldgen 為 nil →
    # WorldGenOverride.lua 索引 biomes 失敗 → NPE → Server Terminated。
    # 2026-08-26 實測 log 全檔只有這一個 couldn't find，其他有 AnimSets 的 MOD 不觸發。
    # AdvancedAnimator.load(:845) 的 checksum 只在 GameServer.server || GameClient.client
    # 執行；單機不走這條多人校驗。這次只恢復排除，不改上游動畫或停用校驗。
    'tikitown',
    # Taibeiroad4：MOD 自身的 B41 殘留 lua 讓「多人連線」後畫面全黑。
    # common/media/lua/shared/TCGMusicDefenitionsTCBoomboxtb1.lua 第 1 行
    # require "TCMusicDefenitions"（該檔不存在於此 MOD），第 3 行就對未定義的
    # GlobalMusic 做索引 → attempted index of non-table。炸點在
    # Core.ResetLua（Core.java:4194）← ConnectToServerState.receiveServerOptions(:135)
    # ＝連線流程的 lua 重置，客戶端 lua 環境沒建完 → 進遊戲全黑（伺服器端不報錯）。
    # GlobalMusic/TCMusicDefenitions 都不是 vanilla（整個 media/lua grep 零命中），
    # 值 tsarcraft_music_01_62 指向 B41 的 Tsar's 音樂框架；Workshop 3401261192
    # 標題就叫「B42 test」、描述自承「一些前置物品刷新会报错」、且未列任何 Required
    # Items，2025-11-15 有玩家留言貼出同一 stack ⇒ 該 MOD 既有缺陷，非我方環境。
    # 作者說「不影響遊戲體驗」是單機情境；MP 才會全黑。
    'Taibeiroad4',
    # muldraugh1993b42 已於 2026-08-26 移出本清單：疊字根因（streets.xml 是官方 Muldraugh
    # 街道的英文複本、917 條同座標）已由 street-names/muldraugh-1993 的 keep_geometry 解決
    # ——只保留本圖獨有的 175 條並翻譯，重疊的整條剔除、交回本體漢化那份顯示。
    # kardinal_ravencreek_B42：與 RavenCreekB42 同 mapDir='Raven Creek B42' 但圖資不同
    # （21 vs 44 unique 街名、互不相交），registry 註解已寫「二選一，勿同時啟用」。
    # 兩個都進 Mods= 會讓 streetI18n 無法唯一判定（log: conflict for mapDir=...
    # using English streets.xml）＝該圖街名退回英文，地圖資料本身也未定義行為。
    # 取本體（同正式伺服器「互斥變體取本體」的既有決策）。
    'kardinal_ravencreek_B42'
)

# 資料夾層排除：個別 mod 內不該上 B42 伺服器的地圖資料夾（加入時過濾＋自癒拔除）
$MapFolderExclude = @('Greenport')  # GreenportB42 內的 B41 舊版資料夾（300 格座標）

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

# 註：AI 工具狀態目錄（.omc 等）不再就地刪除——同步引擎複製時直接排除，來源保持原狀。

# ============================================
# 同步引擎（sync_mod.ps1）：bat 以 ScriptBlock 執行時沒有 $PSScriptRoot，
# 所以先找專案 scripts/，再退回腳本自身同目錄。缺引擎＝fail-closed，絕不「沒同步照樣繼續」。
# ============================================
$enginePaths = @(Join-Path $ProjectRoot "scripts\sync_mod.ps1")
if ($PSScriptRoot) { $enginePaths += (Join-Path $PSScriptRoot "sync_mod.ps1") }
$SyncEngine = @($enginePaths | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1)[0]
if (-not $SyncEngine) {
    Write-Host ""
    Write-Host "[錯誤] 找不到同步引擎 sync_mod.ps1，已中止（不會建立任何副本或連結）" -ForegroundColor Red
    foreach ($p in $enginePaths) { Write-Host "  找過：$p" -ForegroundColor DarkGray }
    Write-Host "  請從 D:/github/pz-family-docs/scripts 同步腳本到本 repo 的 scripts/。" -ForegroundColor Yellow
    Read-Host "按 Enter 結束"
    exit 1
}
. $SyncEngine
foreach ($fn in @('Invoke-PZModSync', 'Remove-PZModSync')) {
    if (-not (Get-Command $fn -CommandType Function -ErrorAction SilentlyContinue)) {
        Write-Host ""
        Write-Host "[錯誤] $SyncEngine 未提供 $fn，引擎版本不符，已中止" -ForegroundColor Red
        Read-Host "按 Enter 結束"
        exit 1
    }
}

# ============================================
# 功能函式
# ============================================

# 只接受引擎契約的單一布林成功值，避免雜訊輸出被 PowerShell 當作成功。
function Test-SyncResult {
    param($Result)
    return ($Result -is [bool] -and $Result)
}

# 唯讀：狀態顯示用（本包已不建連結；地圖 MOD 的連結偵測走 Test-IsSymlinkL）
function Test-IsSymlink {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $false }
    $item = Get-Item $Path -Force -ErrorAction SilentlyContinue
    return ($null -ne $item.LinkType)
}

function Show-DestState {
    param([string]$Label, [string]$Path)
    Write-Host "  [$Label] " -NoNewline
    if (-not (Test-Path $Path)) {
        Write-Host "未同步" -ForegroundColor DarkGray
    } elseif (Test-IsSymlink $Path) {
        $target = (Get-Item $Path -Force).Target
        Write-Host "舊符號連結 -> $target（下次同步會先歸檔再改成實體副本）" -ForegroundColor Yellow
    } else {
        Write-Host "實體副本" -ForegroundColor Green
    }
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
    # 排除清單分流：Excluded 不入 MapMods（加入路徑跳過），但保留供移除路徑清理
    $excluded = @()
    foreach ($xid in @($ids | Where-Object { $MapModExclude -contains $_ })) {
        if ($installed.ContainsKey($xid)) {
            $entry = $installed[$xid]
            $excluded += [pscustomobject]@{
                Id = $xid; Root = $entry.Root
                LinkName = Split-Path -Leaf $entry.Root
                MapFolders = @(Get-ModMapFolders $entry.Root)
            }
        }
    }
    $ids = @($ids | Where-Object { $MapModExclude -notcontains $_ })

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
    $script:MapModInventory = @{ MapMods = $mapMods; Deps = $deps; Missing = @($missing | Select-Object -Unique); Excluded = $excluded }
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
    Write-Host "=== 同步狀態（本包＋家族依賴）===" -ForegroundColor Cyan
    Show-DestState -Label "Workshop" -Path $WorkshopDest
    Show-DestState -Label "mods    " -Path $ModsDest

    # 內容一致性（含主 MOD 等家族依賴）交給引擎唯讀檢查：CheckOnly 不寫入任何東西
    if (Test-SyncResult (Invoke-PZModSync -ProjectRoot $ProjectRoot -ZomboidDir $ZomboidDir -CheckOnly)) {
        Write-Host "  [一致性] 已同步，副本與來源一致" -ForegroundColor Green
    } else {
        Write-Host "  [一致性] 需同步——請執行選單 [1]" -ForegroundColor Yellow
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
            # PZ_Test.ps1 的預設 $SERVER_NAME；地圖 MOD 不寫這份（保持乾淨測其他 MOD）
            Write-Host "   <- PZ_Test.bat 一般測試伺服器（不含地圖 MOD）" -ForegroundColor Green -NoNewline
        } elseif ($inis[$i].Name -eq "$MapTestServerName.ini") {
            Write-Host "   <- 地圖 MOD 專用（選單 4/6/7 固定寫這份）" -ForegroundColor Cyan -NoNewline
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

# 地圖測試伺服器設定：缺檔時從 servertest 複製「四件套」——ini ＋ SandboxVars ＋
# spawnpoints ＋ spawnregions。只複製 ini 會讓沙盒設定退回引擎預設，測試環境與
# servertest 不一致（殭屍量、出生點都不同），問題難查，所以四件一起帶。
# 只改埠：DefaultPort/UDPPort 各 +10，兩份伺服器可各自留存檔、忘記關也不撞埠。
function Initialize-MapTestIni {
    if (Test-Path -LiteralPath $MapTestIniPath) { return $MapTestIniPath }
    $baseIni = Join-Path $ServerIniDir "$BaseServerName.ini"
    if (-not (Test-Path -LiteralPath $baseIni)) {
        Write-Host "  [伺服器] 找不到來源 $BaseServerName.ini，無法建立 $MapTestServerName.ini" -ForegroundColor Red
        return $null
    }
    try {
        # 走 bytes→UTF8 字串→bytes：不動換行風格與 BOM（Set-Content 會改寫 CRLF）
        $text = [System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($baseIni))
        $text = $text -replace 'DefaultPort=16261', 'DefaultPort=16271'
        $text = $text -replace 'UDPPort=16262', 'UDPPort=16272'
        [System.IO.File]::WriteAllBytes($MapTestIniPath, [System.Text.Encoding]::UTF8.GetBytes($text))
        foreach ($suffix in @('_SandboxVars.lua', '_spawnpoints.lua', '_spawnregions.lua')) {
            $s = Join-Path $ServerIniDir "$BaseServerName$suffix"
            $d = Join-Path $ServerIniDir "$MapTestServerName$suffix"
            if ((Test-Path -LiteralPath $s) -and -not (Test-Path -LiteralPath $d)) {
                Copy-Item -LiteralPath $s -Destination $d
            }
        }
    } catch {
        Write-Host "  [伺服器] 建立 $MapTestServerName.ini 失敗: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
    Write-Host "  [伺服器] 已從 $BaseServerName 建立地圖測試設定 $MapTestServerName.ini（埠 16271/16272）" -ForegroundColor Green
    return $MapTestIniPath
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
        # MoveLast：該條目**若存在**就移到最後（不新增）。翻譯 MOD 專用——Mods= 後載入
        # 者覆蓋先載入者，翻譯包必須最後才有覆蓋權；但沒裝的漢化不該被硬塞（EnsureLast
        # 會無條件新增，故另立此語意）。陣列依序處理 ⇒ 最後一個落在最尾。
        # 注意 Mods= 的條目帶 '\' 前綴（BackslashStyle），比對必須去前綴——直接
        # -contains 無前綴 id 永遠不命中（實測踩過）。大小寫敏感同 Add（PZ mod id 是）。
        if ($op.ContainsKey('MoveLast') -and @($op.MoveLast).Count -gt 0) {
            foreach ($ml in @($op.MoveLast)) {
                $hit = @($updated | Where-Object { $_.TrimStart('\') -ceq $ml })
                if ($hit.Count -gt 0) {
                    $updated = @($updated | Where-Object { $_.TrimStart('\') -cne $ml }) + $hit
                }
            }
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
        Update-IniLists -IniPath $IniPath -Ops @(@{ Key = 'Mods'; Add = $ServerModIds; BackslashStyle = $true; MoveLast = $TranslationModsLast })
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
    # 只移除地圖 MOD 的連結（含排除清單的殘留）；tile 依賴包可能被其他 MOD 共用，保留
    $removed = 0
    foreach ($m in (@($Inventory.MapMods) + @($Inventory.Excluded))) {
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
    # 固定寫地圖測試專用設定，不再每次選：地圖 MOD 一旦寫進 servertest.ini，之後測
    # 其他 MOD 都得載入這幾十張圖（也是使用者要求分開的原因）。缺檔就地建立。
    $ini = Initialize-MapTestIni
    if (-not $ini) { Write-Host "  [伺服器] 無法取得 $MapTestServerName.ini，設定檔未變更" -ForegroundColor DarkGray; return }
    Write-Host "  [伺服器] 目標：$MapTestServerName.ini（地圖 MOD 專用；servertest.ini 不動）" -ForegroundColor Cyan
    $mapIds  = @($Inventory.MapMods | ForEach-Object { $_.Id })
    $folders = @($Inventory.MapMods | ForEach-Object { $_.MapFolders } | Where-Object { $_ } |
        Where-Object { $MapFolderExclude -notcontains $_ } | Select-Object -Unique | Sort-Object)
    $exIds     = @($Inventory.Excluded | ForEach-Object { $_.Id })
    $exFolders = @(@($Inventory.Excluded | ForEach-Object { $_.MapFolders } | Where-Object { $_ }) + $MapFolderExclude | Select-Object -Unique)
    if ($Remove) {
        Update-IniLists -IniPath $ini -Ops @(
            @{ Key = 'Mods'; Remove = ($mapIds + $exIds); BackslashStyle = $true },
            @{ Key = 'Map';  Remove = ($folders + $exFolders); EnsureLast = 'Muldraugh, KY' }
        )
        Write-Host "  [提示] tile 依賴包的 Mods= 條目保留（可能被其他 MOD 共用；純材質包無副作用）" -ForegroundColor DarkGray
    } else {
        $depIds = @($Inventory.Deps | ForEach-Object { $_.Id })
        # Add 同時帶 Remove＝排除清單：既有殘留條目一併拔掉（自癒）
        Update-IniLists -IniPath $ini -Ops @(
            @{ Key = 'Mods'; Add = @($ServerModIds) + $depIds + $mapIds; Remove = $exIds; BackslashStyle = $true; MoveLast = $TranslationModsLast },
            @{ Key = 'Map';  Add = $folders; Remove = $exFolders; OrderFirst = $MapOrderFirst; EnsureLast = 'Muldraugh, KY' }
        )
        Write-Host "  [提示] Map= 順序＝優先序（先者為大、vanilla 墊底）；已自動把已知會" -ForegroundColor DarkGray
        Write-Host "         崩服的 bg300 肇事圖排到最前（詳見 check_map_conflicts.ps1）" -ForegroundColor DarkGray
        if ($exIds.Count) {
            Write-Host "  [排除] 未加入（`$MapModExclude）：$($exIds -join '、')——已在存檔啟用過的圖" -ForegroundColor Yellow
            Write-Host "         拔掉會觸發 WorldDictionary 錯誤，請配合開新存檔" -ForegroundColor Yellow
        }
    }
}

function Show-MapModSummary {
    param($Inventory)
    $folderCount = @($Inventory.MapMods | ForEach-Object { $_.MapFolders } | Where-Object { $_ }).Count
    Write-Host ""
    Write-Host "  地圖 MOD：$(@($Inventory.MapMods).Count) 個（地圖資料夾 $folderCount 個）＋ tile 依賴 $(@($Inventory.Deps).Count) 個" -ForegroundColor Cyan
    if (@($Inventory.Excluded).Count -gt 0) {
        Write-Host "  [排除] $(@($Inventory.Excluded | ForEach-Object { $_.Id }) -join '、')（`$MapModExclude；不加入伺服器）" -ForegroundColor Yellow
    }
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

# ============================================
# 本包同步 / 卸載（實作全在 sync_mod.ps1；地圖 MOD 走下方選單 4-7 的第三方連結流程）
# ============================================

function Sync-Workshop {
    Write-Host ""
    Write-Host "正在同步實體副本（Workshop + mods，含主 MOD 等家族依賴）..." -ForegroundColor Cyan
    Write-Host ""

    $ok = Test-SyncResult (Invoke-PZModSync -ProjectRoot $ProjectRoot -ZomboidDir $ZomboidDir)

    Write-Host ""
    if (-not $ok) {
        # 失敗不得假成功：不寫 ini、不提示可以開遊戲
        Write-Host "[未完成] 同步失敗，請依上方訊息處理（遊戲或伺服器執行中請先關閉後重試）。" -ForegroundColor Red
        Write-Host "[提示] 同步未成功，略過伺服器 ini 寫入詢問" -ForegroundColor Yellow
        Write-Host ""
        return
    }

    Write-Host "[全部完成] 現在可以在 PZ 遊戲中測試此 MOD。" -ForegroundColor Green
    Write-Host "[提示] 地圖 MOD 圖資（第三方 Steam 訂閱）不在同步範圍——用選單 4/5 建立連結。" -ForegroundColor DarkGray
    Write-Host ""
    Invoke-ServerIniPrompt
    Write-Host ""
}

function Unsync-Workshop {
    Write-Host ""
    Write-Host "正在歸檔受管副本（只動本 repo 的 Workshop/mods 副本，主 MOD 與地圖連結保留）..." -ForegroundColor Cyan
    Write-Host ""

    $ok = Test-SyncResult (Remove-PZModSync -ProjectRoot $ProjectRoot -ZomboidDir $ZomboidDir)

    Write-Host ""
    if (-not $ok) {
        Write-Host "[未完成] 卸載未完成，請檢查上方歸檔結果；略過伺服器 ini 移除詢問。" -ForegroundColor Red
        Write-Host ""
        return
    }
    Write-Host "[完成] 受管副本已歸檔。" -ForegroundColor Green
    Write-Host ""
    Invoke-ServerIniPrompt -Remove
    Write-Host ""
}

# ============================================
# 主選單
# ============================================
$Host.UI.RawUI.WindowTitle = "MinidoracatMiniMapModMapsFor42 開發同步管理"

while ($true) {
    Clear-Host
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  MinidoracatMiniMapModMapsFor42 開發同步管理" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Workshop: $WorkshopDest"
    Write-Host "  mods:     $ModsDest"
    Write-Host ""
    Write-Host "  [1] 同步本包 - 複製到 Workshop + mods（實體副本，含主 MOD）"
    Write-Host "  [2] 卸載本包 - 歸檔本 repo 的受管副本（主 MOD 與地圖連結保留）"
    Write-Host "  [3] 查看目前狀態（唯讀檢查）"
    Write-Host ""
    Write-Host "  --- 支援的地圖 MOD（第三方 Steam 訂閱，依 Lua 註冊清單；仍用 junction 連結）---" -ForegroundColor DarkCyan
    Write-Host "  [4] 地圖 MOD：連結＋寫入伺服器（mods 連結 + Mods= + Map= → $MapTestServerName.ini）"
    Write-Host "  [5] 地圖 MOD：只建 mods 連結（不動伺服器設定）"
    Write-Host "  [6] 地圖 MOD：只從伺服器移除（$MapTestServerName.ini 的 Mods= + Map=；連結保留）"
    Write-Host "  [7] 地圖 MOD：全部移除（$MapTestServerName.ini 設定＋連結）"
    Write-Host "      地圖只寫 $MapTestServerName.ini（埠 16271）——servertest.ini 保持乾淨，測其他 MOD 免載入幾十張圖" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  [Q] 離開"
    Write-Host ""
    $choice = Read-Host "請選擇"

    switch ($choice.ToUpper()) {
        "1" { Sync-Workshop; Read-Host "按 Enter 繼續" }
        "2" { Unsync-Workshop; Read-Host "按 Enter 繼續" }
        "3" { Show-Status; Read-Host "按 Enter 繼續" }
        "4" { Invoke-MapMods -Mode 'link-server'; Read-Host "按 Enter 繼續" }
        "5" { Invoke-MapMods -Mode 'link-only'; Read-Host "按 Enter 繼續" }
        "6" { Invoke-MapMods -Mode 'server-remove'; Read-Host "按 Enter 繼續" }
        "7" { Invoke-MapMods -Mode 'remove-all'; Read-Host "按 Enter 繼續" }
        "Q" { Write-Host ""; Write-Host "再見！"; exit 0 }
    }
}
