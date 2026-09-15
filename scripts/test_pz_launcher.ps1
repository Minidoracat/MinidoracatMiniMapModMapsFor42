param([string]$LauncherPath = (Join-Path $PSScriptRoot 'PZ_Test.ps1'))

# 真同步引擎＋TEMP 來源；只攔截遊戲程序，不以 GUI 控制項名稱或內部呼叫次數當驗收。
$ErrorActionPreference = 'Stop'
$root = Join-Path $env:TEMP ('pz-launcher-' + [guid]::NewGuid().ToString('N'))
$oldProfile, $oldProject, $oldGame = $env:USERPROFILE, $env:PROJECT_ROOT, $env:PZ_PATH
$repo = Join-Path $root 'repos\MinidoracatLauncherFixtureFor42'
$id = 'MinidoracatLauncherFixtureFor42'
$src = Join-Path $repo "MOD\$id\Contents\mods\$id\42"
$probe = Join-Path $src 'media\probe.lua'
$copy = Join-Path $root "Zomboid\mods\$id\42\media\probe.lua"
$workshopCopy = Join-Path $root "Zomboid\Workshop\$id\Contents\mods\$id\42\media\probe.lua"
$script:Starts = [Collections.Generic.List[object]]::new()
$script:Messages = [Collections.Generic.List[string]]::new()
$script:FakeProcesses = @()
$script:AfterStart = $null
$script:Stopped = @()

function Assert([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "$Message`n$($script:Messages -join "`n")" }
}
function Write-Host { param($Object, $ForegroundColor, [switch]$NoNewline) $script:Messages.Add([string]$Object) }
function Start-Sleep { param($Seconds, $Milliseconds) }
function Get-CimInstance {
    param($ClassName, $Filter, $ErrorAction)
    $names = @([regex]::Matches([string]$Filter, "Name\s*=\s*'([^']+)'") | ForEach-Object { $_.Groups[1].Value })
    if ($names.Count) { return @($script:FakeProcesses | Where-Object { $names -contains $_.Name }) }
    return $script:FakeProcesses
}
function Read-Text([string]$Path) { if ([IO.File]::Exists($Path)) { return [IO.File]::ReadAllText($Path) }; return '' }
function Start-Process {
    param($FilePath, $ArgumentList, $WorkingDirectory, $ErrorAction)
    $script:Starts.Add([pscustomobject]@{
        File = $FilePath; Args = @($ArgumentList); ArgsGiven = $PSBoundParameters.ContainsKey('ArgumentList')
        Content = (Read-Text $copy); WorkshopContent = (Read-Text $workshopCopy)
        Added = [IO.File]::Exists((Join-Path (Split-Path $copy) 'added.lua'))
        Stale = [IO.File]::Exists((Join-Path (Split-Path $copy) 'stale.lua'))
    })
    if ($script:AfterStart) { & $script:AfterStart $script:Starts.Count }
}
function Stop-Process { param($Id, [switch]$Force, $ErrorAction) $script:Stopped += $Id }
function Run-Action([hashtable]$Options, [object[]]$Processes = @(), [scriptblock]$AfterStart) {
    $script:Starts.Clear(); $script:Messages.Clear()
    $script:FakeProcesses = $Processes
    $script:AfterStart = $AfterStart
    try { return (Invoke-PZLauncherAction @Options) }
    finally { $script:AfterStart = $null }
}
function Arg-Value($Start, [string]$Name) {
    $n = [array]::IndexOf($Start.Args, $Name)
    if ($n -ge 0 -and $n + 1 -lt $Start.Args.Count) { return ([string]$Start.Args[$n + 1]).Trim('"') }
    return $null
}
function Server-Process([string]$Mode) {
    [pscustomobject]@{ Name='java.exe'; ProcessId=4242; CommandLine="java -Dzomboid.steam=$Mode zombie.network.GameServer -servername servertest" }
}

try {
    $env:USERPROFILE = $root; $env:PROJECT_ROOT = $repo; $env:PZ_PATH = Join-Path $root 'game'
    [void][IO.Directory]::CreateDirectory((Join-Path $src 'media'))
    [void][IO.Directory]::CreateDirectory((Join-Path $repo 'scripts'))
    [void][IO.Directory]::CreateDirectory((Join-Path $root 'Zomboid\Server'))
    [void][IO.Directory]::CreateDirectory($env:PZ_PATH)
    [IO.File]::WriteAllText((Join-Path $env:PZ_PATH 'ProjectZomboid64.exe'), '')
    [IO.File]::WriteAllText((Join-Path $src 'mod.info'), "id=$id`r`nname=Launcher Fixture`r`n")
    [IO.File]::WriteAllText($probe, 'marker=v1')
    [IO.File]::WriteAllText((Join-Path $src 'media\stale.lua'), 'remove me')
    [IO.File]::WriteAllText((Join-Path $root 'Zomboid\Server\servertest.ini'), "Mods=\$id`r`nDefaultPort=16261")
    [IO.File]::WriteAllText((Join-Path $root 'Zomboid\Server\map test.ini'), "Mods=\$id`r`nDefaultPort=16271")
    $cnIni = Join-Path $root 'Zomboid\Server\cntrans.ini'
    [IO.File]::WriteAllText($cnIni, "Mods=\$id`r`nDefaultPort=16299")
    $cnOriginal = [IO.File]::ReadAllText($cnIni)
    $engine = Join-Path $repo 'scripts\sync_mod.ps1'
    Copy-Item -LiteralPath (Join-Path (Split-Path $LauncherPath) 'sync_mod.ps1') -Destination $engine
    . $LauncherPath -LoadOnly
    $supportsCN = [bool](Get-Command Ensure-CNTransConfig -ErrorAction SilentlyContinue)

    $cases = @(
        @{Action='client'; NoSteam=$true; Clients=1; DebugClient=$false},
        @{Action='client'; NoSteam=$true; Clients=1; DebugClient=$true},
        @{Action='server'; NoSteam=$true; Clients=1; DebugClient=$false},
        @{Action='combo'; NoSteam=$true; Clients=1; DebugClient=$false},
        @{Action='combo'; NoSteam=$true; Clients=1; DebugClient=$true},
        @{Action='combo'; NoSteam=$true; Clients=2; DebugClient=$false},
        @{Action='combo'; NoSteam=$true; Clients=2; DebugClient=$true},
        @{Action='client'; NoSteam=$true; Clients=2; DebugClient=$true},
        @{Action='client'; NoSteam=$false; Clients=1; DebugClient=$false},
        @{Action='client'; NoSteam=$false; Clients=1; DebugClient=$true},
        @{Action='server'; NoSteam=$false; Clients=1; DebugClient=$false},
        @{Action='combo'; NoSteam=$false; Clients=1; DebugClient=$false},
        @{Action='combo'; NoSteam=$false; Clients=1; DebugClient=$true}
    )
    if ($supportsCN) {
        $cases += @{Action='cntrans'; NoSteam=$true; Clients=1; DebugClient=$true}
        $cases += @{Action='cntrans'; NoSteam=$false; Clients=1; DebugClient=$true}
    }
    foreach ($case in $cases) {
        Assert (Run-Action $case) "啟動失敗：$($case.Action) / noSteam=$($case.NoSteam)"
        $servers = @($script:Starts | Where-Object { $_.Args -contains 'zombie.network.GameServer' })
        $clientStarts = @($script:Starts | Where-Object { $_.File -like '*ProjectZomboid64.exe' })
        $wantServer = $case.Action -in @('server','combo','cntrans')
        $wantClients = if ($case.Action -eq 'server') {0} else {$case.Clients}
        Assert ($servers.Count -eq [int]$wantServer -and $clientStarts.Count -eq $wantClients) '程序數量不符'
        if ($wantServer) {
            $flag = if ($case.NoSteam) {'-Dzomboid.steam=0'} else {'-Dzomboid.steam=1'}
            Assert ($servers[0].Args -contains $flag) 'server 連線模式錯誤'
            $name = if ($case.Action -eq 'cntrans') {'cntrans'} else {'servertest'}
            Assert ((Arg-Value $servers[0] '-servername') -eq $name) 'server 設定檔錯誤'
        }
        foreach ($client in $clientStarts) {
            Assert (($client.Args -contains '-nosteam') -eq $case.NoSteam) 'client 連線模式錯誤'
            Assert (($client.Args -contains '-debug') -eq $case.DebugClient) 'client Debug 模式錯誤'
            if (-not $case.NoSteam -and -not $case.DebugClient) { Assert (-not $client.ArgsGiven) '空 ArgumentList 不應傳給 Start-Process' }
        }
        foreach ($start in $script:Starts) { Assert ($start.Content -eq 'marker=v1' -and $start.WorkshopContent -eq 'marker=v1') '啟動前副本內容錯誤' }
    }
    Assert ([IO.File]::ReadAllText($cnIni) -eq $cnOriginal) '既有漢化對照設定不應被覆寫'

    Assert (-not (Run-Action @{Action='client';Clients=2})) 'Steam 多開必須拒絕'
    Assert ($script:Starts.Count -eq 0) '拒絕 Steam 多開後不應啟動'
    Assert (-not (Run-Action @{Action='server';ServerName='../escape'})) '非法server名必須拒絕'
    Assert ($script:Starts.Count -eq 0) '非法server名不應啟動'
    Assert (-not (Run-Action @{Action='combo';NoSteam=$true} @((Server-Process '1')))) '異模式server不得重用'
    Assert ($script:Starts.Count -eq 0) '異模式時不得續開client'
    Assert (Run-Action @{Action='combo';NoSteam=$true} @((Server-Process '0'))) '同模式且一致應能重用'
    Assert ($script:Starts.Count -eq 1) '重用server不應再啟動一個server'
    Assert (-not (Run-Action @{Action='server'} @([pscustomobject]@{Name='java.exe';ProcessId=9;CommandLine=$null}))) '未知Java命令列不得猜成没有server'
    Assert ($script:Starts.Count -eq 0) '未知server狀態不應啟動'

    [IO.File]::WriteAllText($probe, 'marker=v2')
    [IO.File]::WriteAllText((Join-Path $src 'media\added.lua'), 'new')
    Remove-Item -LiteralPath (Join-Path $src 'media\stale.lua')
    Assert (-not (Run-Action @{Action='combo';NoSteam=$true} @((Server-Process '0')))) '正在跑且副本需更新必須拒絕'
    Assert ((Read-Text $copy) -eq 'marker=v1' -and $script:Starts.Count -eq 0) '執行中改了副本或啟動程序'
    Assert (Run-Action @{Action='combo';NoSteam=$true}) '關服後應同步並啟動'
    foreach ($start in $script:Starts) { Assert ($start.Content -eq 'marker=v2' -and $start.WorkshopContent -eq 'marker=v2' -and $start.Added -and -not $start.Stale) '增改刪未在啟動前反映' }

    $stamp = [IO.File]::GetLastWriteTimeUtc($probe)
    [IO.File]::WriteAllText($probe, 'marker=v3')
    [IO.File]::SetLastWriteTimeUtc($probe, $stamp)
    Assert (Run-Action @{Action='sync';ForceVerify=$true}) '完整驗證應偵測同size/mtime內容變動'
    Assert ((Read-Text $copy) -eq 'marker=v3' -and $script:Starts.Count -eq 0) '完整驗證未套用新內容或誤啟動遊戲'

    [void](Run-Action @{Action='combo';NoSteam=$true;Clients=2} @() {param($n) if($n -eq 2){[IO.File]::Delete($copy)}})
    Assert ($script:Starts.Count -eq 2 -and -not [IO.File]::Exists($copy)) '多開中途副本變更後不得寫回或續開'
    $info = Join-Path $src 'mod.info'
    Move-Item $info ($info+'.hold')
    Assert (-not (Run-Action @{Action='client';NoSteam=$true})) '缺來源必須拒絕'
    Assert ($script:Starts.Count -eq 0) '缺來源仍啟動'
    Move-Item ($info+'.hold') $info
    Move-Item $engine ($engine+'.hold')
    Assert (-not (Run-Action @{Action='client';NoSteam=$true})) '缺引擎必須拒絕'
    Assert ($script:Starts.Count -eq 0) '缺引擎仍啟動'
    Move-Item ($engine+'.hold') $engine
    Assert (Run-Action @{Action='combo';NoSteam=$true;ServerName='map test'}) '下拉選擇含空格的server應可啟動'
    $selected = @($script:Starts | Where-Object { $_.Args -contains 'zombie.network.GameServer' })[0]
    Assert ((Arg-Value $selected '-servername') -eq 'map test') '所選server未傳至真正啟動參數'
    Assert (-not [IO.Directory]::Exists((Join-Path $root 'Zomboid\Saves'))) '測試不應產生存檔'
    Write-Output "test_pz_launcher: PASS $($cases.Count) 個啟動組合、同步新鮮度、ForceVerify、缺失與忙碌拒絕、多開保護、含空格設定名"
} finally {
    $env:USERPROFILE, $env:PROJECT_ROOT, $env:PZ_PATH = $oldProfile, $oldProject, $oldGame
    if ([IO.Directory]::Exists($root)) { Remove-Item -LiteralPath $root -Recurse -Force }
}
