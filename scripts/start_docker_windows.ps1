#Requires -Version 5.1
<#
.SYNOPSIS
Launch the extracted Windows starter without Python or Git.
.DESCRIPTION
Existing local Linux engines are reused. Optional prerequisites require consent.
Only a fixed WSL subprocess is elevated; apps and the browser retain the user.
#>
[CmdletBinding()]
param(
    [ValidateSet('start','build','stop','status','doctor')][string]$Action = 'start',
    [switch]$NoBrowser, [int]$Port = 8765, [int]$DatabasePort = 55432,
    [string]$DataDir = '', [string]$Project = 'ds60-learning',
    [switch]$NonInteractive, [switch]$DiagnosticsOnly, [switch]$SkipInstall
)
$script:Ds60WindowsStarterRoot = $PSScriptRoot

function ConvertTo-Ds60WindowsArgument {
    param([AllowEmptyString()][string]$Value)
    if ($Value -ne '' -and $Value -notmatch '[\s"]') { return $Value }
    $quoted = [regex]::Replace($Value, '(\\*)"', '$1$1\"')
    $quoted = [regex]::Replace($quoted, '(\\+)$', '$1$1')
    return '"' + $quoted + '"'
}

function Invoke-Ds60WindowsNative {
    param([string]$FilePath, [string[]]$Arguments = @(), [int]$TimeoutSeconds = 20)
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo.FileName = $FilePath
    $process.StartInfo.Arguments = (($Arguments | ForEach-Object { ConvertTo-Ds60WindowsArgument $_ }) -join ' ')
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.CreateNoWindow = $true
    $process.StartInfo.RedirectStandardOutput = $true
    $process.StartInfo.RedirectStandardError = $true
    $process.StartInfo.RedirectStandardInput = $true
    $process.StartInfo.StandardOutputEncoding = [Text.Encoding]::UTF8
    $process.StartInfo.StandardErrorEncoding = [Text.Encoding]::UTF8
    # Explicit CLI endpoint flags below must never inherit a remote override.
    $process.StartInfo.EnvironmentVariables.Remove('DOCKER_CONTEXT')
    $process.StartInfo.EnvironmentVariables.Remove('DOCKER_HOST')
    try {
        [void]$process.Start()
        $process.StandardInput.Close()
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            try { $process.Kill() } catch { }
            [void]$process.WaitForExit(2000)
            return [pscustomobject]@{ ExitCode = 2; Output = ''; Error = 'Timed out.'; TimedOut = $true }
        }
        $out = if ($stdout.Wait(1000)) { $stdout.Result.Replace("`0", '') } else { '' }
        $err = if ($stderr.Wait(1000)) { $stderr.Result.Replace("`0", '') } else { '' }
        return [pscustomobject]@{ ExitCode = $process.ExitCode; Output = $out; Error = $err; TimedOut = $false }
    } catch {
        return [pscustomobject]@{ ExitCode = 2; Output = ''; Error = 'Command could not start.'; TimedOut = $false }
    } finally { $process.Dispose() }
}

function Get-Ds60WindowsHost {
    $architecture = if ($env:PROCESSOR_ARCHITEW6432) { $env:PROCESSOR_ARCHITEW6432 } else { $env:PROCESSOR_ARCHITECTURE }
    return [pscustomobject]@{ IsWindows = ($env:OS -eq 'Windows_NT'); Is64Bit = [Environment]::Is64BitOperatingSystem; Build = [Environment]::OSVersion.Version.Build; Architecture = [string]$architecture }
}

function Get-Ds60WindowsDesktop {
    param([ValidateSet('RancherDesktop','DockerDesktop')][string]$Engine)
    $roots = if ($Engine -eq 'RancherDesktop') {
        @((Join-Path $env:ProgramFiles 'Rancher Desktop'), (Join-Path $env:LOCALAPPDATA 'Programs\Rancher Desktop'))
    } else {
        @((Join-Path $env:ProgramFiles 'Docker\Docker'), (Join-Path $env:LOCALAPPDATA 'Programs\DockerDesktop'))
    }
    $name = if ($Engine -eq 'RancherDesktop') { 'Rancher Desktop.exe' } else { 'Docker Desktop.exe' }
    foreach ($root in $roots) {
        $exe = Join-Path $root $name
        if (Test-Path -LiteralPath $exe -PathType Leaf) {
            $rdctl = if ($Engine -eq 'RancherDesktop') { Join-Path $root 'resources\resources\win32\bin\rdctl.exe' } else { '' }
            return [pscustomobject]@{ Name = $Engine; Executable = $exe; Rdctl = $rdctl }
        }
    }
    return $null
}

function Get-Ds60InstalledDesktops {
    foreach ($name in @('RancherDesktop','DockerDesktop')) {
        $installed = Get-Ds60WindowsDesktop -Engine $name
        if ($null -ne $installed) { $installed }
    }
}

function Get-Ds60WindowsDocker {
    $found = Get-Command docker.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { return $found.Source }
    $candidates = @()
    if ($env:USERPROFILE) { $candidates += Join-Path $env:USERPROFILE '.rd\bin\docker.exe' }
    foreach ($desktop in @(Get-Ds60InstalledDesktops)) {
        $relative = if ($desktop.Name -eq 'RancherDesktop') { 'resources\resources\win32\bin\docker.exe' } else { 'resources\bin\docker.exe' }
        $candidates += Join-Path (Split-Path -Parent $desktop.Executable) $relative
    }
    foreach ($candidate in $candidates) { if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate } }
    return $null
}

function Test-Ds60LocalDockerEndpoint {
    param([string]$Endpoint)
    return ($Endpoint -match '^npipe:/{2,4}\./pipe/[A-Za-z0-9_.-]+$' -or $Endpoint -match '^unix:///[^\s]+$' -or $Endpoint -match '^tcp://(?:127\.0\.0\.1|localhost):[0-9]+$')
}

function Get-Ds60ReadyLocalDocker {
    param([string]$Docker)
    $missing = [pscustomobject]@{ Ready = $false; Context = ''; Host = ''; Reason = 'No ready local Linux Docker engine was found.'; Blocked = $false }
    $choices = @()
    if ($env:DOCKER_HOST -and -not $env:DOCKER_CONTEXT -and -not (Test-Ds60LocalDockerEndpoint $env:DOCKER_HOST)) {
        $missing.Blocked = $true
        $missing.Reason = 'DOCKER_HOST selects a remote engine. Choose your local desktop context for this session, then rerun. No remote daemon was contacted and no prerequisites were changed.'
        return $missing
    }
    if (-not $Docker) {
        if ($env:DOCKER_CONTEXT) {
            $missing.Blocked = $true
            $missing.Reason = 'DOCKER_CONTEXT is set but Docker CLI cannot verify it as local. Check the existing Docker installation and local context before running setup.'
        }
        return $missing
    }
    if ($env:DOCKER_HOST -and -not $env:DOCKER_CONTEXT -and (Test-Ds60LocalDockerEndpoint $env:DOCKER_HOST)) {
        $choices += [pscustomobject]@{ Context = ''; Host = $env:DOCKER_HOST }
    }
    $listed = Invoke-Ds60WindowsNative -FilePath $Docker -Arguments @('context','ls','--format','{{json .}}') -TimeoutSeconds 10
    $selectedFound = $false
    if ($listed.ExitCode -eq 0) {
        foreach ($line in ($listed.Output -split "`r?`n")) {
            if (-not $line.Trim()) { continue }
            try {
                $item = $line | ConvertFrom-Json -ErrorAction Stop
                $selected = if ($env:DOCKER_CONTEXT) { $item.Name -eq $env:DOCKER_CONTEXT } else { -not $env:DOCKER_HOST -and $item.Current -eq $true }
                if ($selected) {
                    $selectedFound = $true
                    if (-not (Test-Ds60LocalDockerEndpoint $item.DockerEndpoint)) {
                        $missing.Blocked = $true
                        $missing.Reason = 'The selected Docker context is remote. Choose a local desktop context, then rerun. No remote daemon was contacted and no system setup was attempted.'
                        return $missing
                    }
                }
                if (Test-Ds60LocalDockerEndpoint $item.DockerEndpoint) { $choices += [pscustomobject]@{ Context = $item.Name; Host = $item.DockerEndpoint } }
            } catch { }
        }
    }
    if ($env:DOCKER_CONTEXT -and -not $selectedFound) {
        $missing.Blocked = $true
        $missing.Reason = 'DOCKER_CONTEXT could not be resolved to a local context. Check your local Docker context selection before running setup.'
        return $missing
    }
    if ($env:DOCKER_CONTEXT) { $choices = @($choices | Where-Object { $_.Context -eq $env:DOCKER_CONTEXT }) }
    elseif ($env:DOCKER_HOST) { $choices = @($choices | Where-Object { -not $_.Context -and $_.Host -eq $env:DOCKER_HOST }) }
    # Context enumeration reads local metadata; probes never contact remote endpoints.
    foreach ($choice in $choices) {
        $prefix = if ($choice.Context) { @('--context',$choice.Context) } else { @('--host',$choice.Host) }
        $info = Invoke-Ds60WindowsNative -FilePath $Docker -Arguments ($prefix + @('info','--format','{{json .}}')) -TimeoutSeconds 5
        if ($info.ExitCode -ne 0) { continue }
        try { $details = $info.Output | ConvertFrom-Json -ErrorAction Stop } catch { continue }
        if ($details.OSType -ne 'linux') { $missing.Blocked = $true; $missing.Reason = 'A local engine uses Windows containers. Select Linux containers in its desktop app, then rerun this starter.'; return $missing }
        $compose = Invoke-Ds60WindowsNative -FilePath $Docker -Arguments ($prefix + @('compose','version')) -TimeoutSeconds 5
        if ($compose.ExitCode -eq 0) { return [pscustomobject]@{ Ready = $true; Context = $choice.Context; Host = $choice.Host; Reason = 'Local Linux engine and Compose are ready.' } }
        $missing.Reason = 'The local engine needs Docker Compose. Update that desktop app, then rerun this starter.'
    }
    return $missing
}

function Get-Ds60WslReadiness {
    $wsl = Join-Path $env:SystemRoot 'System32\wsl.exe'
    if (-not (Test-Path -LiteralPath $wsl -PathType Leaf)) { return [pscustomobject]@{ Ready = $false; NeedsUpdate = $false; Executable = $wsl; Reason = 'WSL 2 is not installed.' } }
    $status = Invoke-Ds60WindowsNative -FilePath $wsl -Arguments @('--status') -TimeoutSeconds 15
    $version = Invoke-Ds60WindowsNative -FilePath $wsl -Arguments @('--version') -TimeoutSeconds 15
    $modern = $false
    if ($version.ExitCode -eq 0 -and $version.Output -match '(\d+\.\d+\.\d+)') { $modern = ([version]$Matches[1] -ge [version]'2.1.5') }
    return [pscustomobject]@{ Ready = ($status.ExitCode -eq 0 -and $modern); NeedsUpdate = ($status.ExitCode -eq 0 -and -not $modern); Executable = $wsl; Reason = 'Current WSL 2 and enabled hardware virtualization are needed.' }
}

function Get-Ds60Winget {
    $command = Get-Command winget.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) { return $command.Source }; return $null
}

function Test-Ds60UnusedRancherProfile {
    # Absence must be proven, not inferred from a failed command or missing CLI.
    if (-not $env:LOCALAPPDATA -or -not $env:APPDATA -or -not $env:SystemRoot) { return $false }
    try {
        foreach ($path in @((Join-Path $env:APPDATA 'rancher-desktop'), (Join-Path $env:LOCALAPPDATA 'rancher-desktop'), 'HKCU:\Software\Policies\Rancher Desktop', 'HKLM:\Software\Policies\Rancher Desktop')) {
            if (Test-Path -LiteralPath $path -ErrorAction Stop) { return $false }
        }
        $wsl = Join-Path $env:SystemRoot 'System32\wsl.exe'
        if (-not (Test-Path -LiteralPath $wsl -PathType Leaf)) { return $false }
        $list = Invoke-Ds60WindowsNative -FilePath $wsl -Arguments @('--list','--quiet') -TimeoutSeconds 15
        if ($list.ExitCode -ne 0) { return $false }
        foreach ($line in ($list.Output -split "`r?`n")) {
            if ($line.Trim() -match '^(?i:rancher-desktop(?:-data)?)$') { return $false }
        }
        return $true
    } catch { return $false }
}

function Confirm-Ds60WindowsChange {
    param([string]$Message)
    Write-Host $Message
    return ((Read-Host 'Continue? Type Y to approve, or press Enter to stop') -match '^(?i:y|yes)$')
}

function Select-Ds60WindowsEngine {
    param([string[]]$Available, [string]$Recommended = 'RancherDesktop')
    Write-Host 'Choose a desktop engine. Existing installations and workloads will be preserved.'
    if ($Available -contains 'RancherDesktop') { Write-Host 'R: Rancher Desktop (recommended for a new Windows 11 x64 setup)' }
    if ($Available -contains 'DockerDesktop') { Write-Host 'D: Docker Desktop (review its subscription terms before installing)' }
    $choice = Read-Host 'Type R or D, or press Enter to cancel'
    if ($choice -match '^(?i:r)$' -and $Available -contains 'RancherDesktop') { return 'RancherDesktop' }
    if ($choice -match '^(?i:d)$' -and $Available -contains 'DockerDesktop') { return 'DockerDesktop' }
    return $null
}

function Show-Ds60ManualWindowsSetup {
    Write-Host 'Use official installers if WinGet or organization policy prevents guided installation:'
    Write-Host 'App Installer / WinGet: https://apps.microsoft.com/detail/9nblggh4nns1'
    Write-Host 'WSL: https://learn.microsoft.com/windows/wsl/install'
    Write-Host 'Rancher Desktop: https://docs.rancherdesktop.io/getting-started/installation/'
    Write-Host 'Docker Desktop: https://docs.docker.com/desktop/setup/install/windows-install/'
    Write-Host 'After installation or a requested restart, double-click START_DOCKER_LAB.cmd again.'
}

function Invoke-Ds60WslSetup {
    param([switch]$Update)
    # A fixed prerequisite subprocess alone is elevated, not the wizard or apps.
    $operation = if ($Update) { '--update' } else { '--install --no-distribution' }
    $code = '& "$env:SystemRoot\System32\wsl.exe" ' + $operation + '; exit $LASTEXITCODE'
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($code))
    $powershell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
    try {
        $child = Start-Process -FilePath $powershell -Verb RunAs -Wait -PassThru -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-EncodedCommand',$encoded) -ErrorAction Stop
        return [int]$child.ExitCode
    } catch { Write-Host 'WSL setup was cancelled or could not obtain administrator approval.'; return 2 }
}

function Install-Ds60WindowsEngine {
    param([string]$Engine, [string]$Winget)
    $id = if ($Engine -eq 'RancherDesktop') { 'SUSE.RancherDesktop' } else { 'Docker.DockerDesktop' }
    $arguments = @('install','--exact','--id',$id,'--source','winget','--accept-source-agreements','--accept-package-agreements','--no-upgrade')
    Write-Host ('Installing ' + $id + '. Its installer may request permission. No automatic reboot is allowed.')
    try {
        $child = Start-Process -FilePath $Winget -ArgumentList (($arguments | ForEach-Object { ConvertTo-Ds60WindowsArgument $_ }) -join ' ') -NoNewWindow -Wait -PassThru -ErrorAction Stop
        return [int]$child.ExitCode
    } catch { Write-Host 'The installer could not start.'; return 2 }
}

function Start-Ds60WindowsEngine {
    param([string]$Engine, [object]$Installation, [switch]$Fresh)
    try {
        if ($Fresh -and $Engine -eq 'RancherDesktop') {
            if (-not (Test-Path -LiteralPath $Installation.Rdctl -PathType Leaf)) { Write-Host 'New Rancher CLI not found. Open Rancher Desktop, select dockerd (Moby), disable Kubernetes, then rerun.'; return 2 }
            Start-Process -FilePath $Installation.Rdctl -NoNewWindow -ArgumentList @('start','--application.start-in-background','--container-engine.name=moby','--kubernetes.enabled=false') -ErrorAction Stop | Out-Null
        } else { Start-Process -FilePath $Installation.Executable -ErrorAction Stop | Out-Null }
        return 0
    } catch { Write-Host 'The desktop app could not start. Open it from the Start menu to inspect its message.'; return 2 }
}

function Wait-Ds60LocalDocker {
    param([string]$Docker, [int]$TimeoutSeconds = 180)
    $timer = [Diagnostics.Stopwatch]::StartNew()
    $result = [pscustomobject]@{ Ready = $false; Context = ''; Host = ''; Reason = 'The desktop engine did not become ready in time.' }
    while ($timer.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
        if (-not $Docker) { $Docker = Get-Ds60WindowsDocker }
        $result = Get-Ds60ReadyLocalDocker -Docker $Docker
        if ($result.Ready) { return $result }
        Start-Sleep -Seconds 2
    }
    return $result
}

function Invoke-Ds60DockerLauncher {
    param([string]$Action, [switch]$NoBrowser, [int]$Port, [int]$DatabasePort, [string]$DataDir, [string]$Project, [string]$Docker, [object]$Selection)
    $savedPath = $env:PATH; $savedHost = $env:DOCKER_HOST; $savedContext = $env:DOCKER_CONTEXT
    try {
        $env:PATH = (Split-Path -Parent $Docker) + [IO.Path]::PathSeparator + $savedPath
        if ($Selection.Context) { $env:DOCKER_CONTEXT = $Selection.Context; Remove-Item Env:DOCKER_HOST -ErrorAction SilentlyContinue }
        else { $env:DOCKER_HOST = $Selection.Host; Remove-Item Env:DOCKER_CONTEXT -ErrorAction SilentlyContinue }
        $powershell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
        $runtime = Join-Path $script:Ds60WindowsStarterRoot 'docker_lab.ps1'
        $arguments = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$runtime,$Action,'-Port',$Port,'-DatabasePort',$DatabasePort,'-Project',$Project)
        if ($DataDir) { $arguments += @('-DataDir',$DataDir) }; if ($NoBrowser) { $arguments += '-NoBrowser' }
        $child = Start-Process -FilePath $powershell -ArgumentList (($arguments | ForEach-Object { ConvertTo-Ds60WindowsArgument ([string]$_) }) -join ' ') -NoNewWindow -Wait -PassThru -ErrorAction Stop
        return [int]$child.ExitCode
    } finally {
        $env:PATH = $savedPath
        if ($null -eq $savedHost) { Remove-Item Env:DOCKER_HOST -ErrorAction SilentlyContinue } else { $env:DOCKER_HOST = $savedHost }
        if ($null -eq $savedContext) { Remove-Item Env:DOCKER_CONTEXT -ErrorAction SilentlyContinue } else { $env:DOCKER_CONTEXT = $savedContext }
    }
}

function Invoke-Ds60WindowsDocker {
    [CmdletBinding()]
    param([ValidateSet('start','build','stop','status','doctor')][string]$Action = 'start',
        [switch]$NoBrowser, [int]$Port = 8765, [int]$DatabasePort = 55432,
        [string]$DataDir = '', [string]$Project = 'ds60-learning',
        [switch]$NonInteractive, [switch]$DiagnosticsOnly, [switch]$SkipInstall)
    if ($Port -lt 1 -or $Port -gt 65535 -or $DatabasePort -lt 1 -or $DatabasePort -gt 65535 -or $Port -eq $DatabasePort -or $Project -notmatch '^[a-z0-9][a-z0-9_-]{0,48}$') { Write-Host 'Use different ports between 1 and 65535 and a lowercase project name.'; return 2 }
    $hostInfo = Get-Ds60WindowsHost
    if (-not $hostInfo.IsWindows -or -not $hostInfo.Is64Bit) { Write-Host 'Use 64-bit Windows for this starter. Other platforms use scripts/docker_lab.sh.'; return 2 }
    $docker = Get-Ds60WindowsDocker
    $ready = Get-Ds60ReadyLocalDocker -Docker $docker
    if ($DiagnosticsOnly -or $Action -eq 'doctor') {
        Write-Host $ready.Reason
        Write-Host ("Windows build: " + $hostInfo.Build + "; processor: " + $hostInfo.Architecture)
        $desktops = @(Get-Ds60InstalledDesktops)
        Write-Host ('Installed desktop apps found: ' + $desktops.Count)
        $wslInfo = Get-Ds60WslReadiness
        Write-Host ('Current WSL available: ' + $wslInfo.Ready)
        Write-Host ('WinGet available: ' + [bool](Get-Ds60Winget))
        Write-Host 'A ready existing engine can be used regardless of which optional installer is available.'
        Write-Host 'Diagnostics made no installation, engine, browser or learner-state changes.'
        if ($ready.Ready) { return 0 }; return 2
    }
    if ($ready.Ready) { return Invoke-Ds60DockerLauncher -Action $Action -NoBrowser:($NoBrowser -or $NonInteractive) -Port $Port -DatabasePort $DatabasePort -DataDir $DataDir -Project $Project -Docker $docker -Selection $ready }
    Write-Host $ready.Reason
    if ($ready.PSObject.Properties['Blocked'] -and $ready.Blocked) { return 2 }
    if ($NonInteractive) { Write-Host 'NonInteractive cannot install prerequisites or start a desktop engine. Run the starter interactively first.'; return 2 }
    if ($Action -in @('stop','status')) { Write-Host 'Start your local Linux engine before managing this course project.'; return 2 }
    $installed = @(Get-Ds60InstalledDesktops)
    $fresh = ($installed.Count -eq 0)
    if ($fresh -and $SkipInstall) { Write-Host 'SkipInstall leaves missing prerequisites unchanged.'; Show-Ds60ManualWindowsSetup; return 2 }
    if ($fresh) {
        if ($hostInfo.Build -lt 22000 -or $hostInfo.Architecture -notin @('AMD64','x64')) { Write-Host 'Guided new-engine installation supports Windows 11 x64. Ready existing local Linux engines can still be reused. For other systems, use vendor supported-system instructions.'; Show-Ds60ManualWindowsSetup; return 2 }
        $engine = Select-Ds60WindowsEngine -Available @('RancherDesktop','DockerDesktop') -Recommended 'RancherDesktop'
    } elseif ($installed.Count -eq 1) { $engine = $installed[0].Name }
    else { $engine = Select-Ds60WindowsEngine -Available @($installed | ForEach-Object { $_.Name }) -Recommended 'RancherDesktop' }
    if (-not $engine) { Write-Host 'Setup cancelled. No installation or engine settings were changed.'; return 2 }
    if ($fresh -and $engine -eq 'DockerDesktop' -and $hostInfo.Build -lt 22631) {
        Write-Host 'Current Docker Desktop requires Windows 11 version 23H2 (build 22631) or newer on this guided route. Update Windows or choose a supported engine. Nothing was installed.'
        Show-Ds60ManualWindowsSetup
        return 2
    }
    $winget = $null
    $configureFresh = $fresh
    if ($fresh) {
        $winget = Get-Ds60Winget
        if (-not $winget) { Write-Host 'WinGet is not available. Nothing was installed.'; Show-Ds60ManualWindowsSetup; return 2 }
        $terms = if ($engine -eq 'RancherDesktop') { 'https://github.com/rancher-sandbox/rancher-desktop/blob/main/LICENSE' } else { 'https://www.docker.com/legal/docker-subscription-service-agreement/' }
        if (-not (Confirm-Ds60WindowsChange -Message "Install $engine with WinGet and accept package/source terms ($terms)? Its installer may request administrator approval. Docker Desktop may require a paid subscription for some organizations. Only new Rancher gets Moby with Kubernetes disabled. No automatic reboot occurs.")) { return 2 }
    } elseif ($engine -eq 'RancherDesktop' -and (Test-Ds60UnusedRancherProfile)) {
        if (-not (Confirm-Ds60WindowsChange -Message 'This Rancher installation has no user profile, policy or Rancher WSL distributions yet. Initialize it with dockerd (Moby) and Kubernetes disabled? Existing other engines and distributions will be preserved.')) { return 2 }
        $configureFresh = $true
    } elseif (-not (Confirm-Ds60WindowsChange -Message "Start your installed $engine with its existing settings? No engine settings, other containers or volumes will change.")) { return 2 }
    $wsl = Get-Ds60WslReadiness
    if (-not $wsl.Ready) {
        if ($SkipInstall) { Write-Host 'SkipInstall leaves WSL prerequisites unchanged.'; Show-Ds60ManualWindowsSetup; return 2 }
        if (-not (Confirm-Ds60WindowsChange -Message 'Install/update Microsoft WSL 2 without an Ubuntu distribution? Windows will request administrator approval for that prerequisite only. Restart manually if requested, then double-click the same starter again.')) { return 2 }
        $code = Invoke-Ds60WslSetup -Update:$wsl.NeedsUpdate
        if ($code -in @(3010,1641)) { Write-Host 'Restart when convenient, then double-click START_DOCKER_LAB.cmd again. This starter will not reboot your PC.'; return 3010 }
        if ($code -ne 0) { Write-Host 'WSL setup failed. Check hardware virtualization, Windows updates and administrator policy.'; Show-Ds60ManualWindowsSetup; return 2 }
        $wsl = Get-Ds60WslReadiness
        if (-not $wsl.Ready) { Write-Host 'A manual restart or WSL repair is needed. Run the same starter after restarting.'; return 3010 }
    }
    if ($fresh) {
        $code = Install-Ds60WindowsEngine -Engine $engine -Winget $winget
        if ($code -in @(3010,1641)) { Write-Host 'The installer requests a restart. Restart when convenient, then rerun this starter. No reboot was initiated by this script.'; return 3010 }
        if ($code -ne 0) { Write-Host ('Engine installation did not complete (exit ' + $code + ').'); Show-Ds60ManualWindowsSetup; return 2 }
        $installed = @(Get-Ds60InstalledDesktops)
    }
    $installation = $installed | Where-Object { $_.Name -eq $engine } | Select-Object -First 1
    if (-not $installation) { Write-Host 'Desktop path not found. Finish its installer and rerun this starter.'; Show-Ds60ManualWindowsSetup; return 2 }
    if ((Start-Ds60WindowsEngine -Engine $engine -Installation $installation -Fresh:$configureFresh) -ne 0) { return 2 }
    Write-Host 'Waiting up to 180 seconds for the local Linux engine. First startup can download more components.'
    $docker = Get-Ds60WindowsDocker
    $ready = Wait-Ds60LocalDocker -Docker $docker -TimeoutSeconds 180
    if (-not $ready.Ready) { Write-Host $ready.Reason; Write-Host 'Open the desktop app to finish welcome/license prompts or inspect errors. Existing Rancher users choose dockerd (Moby) manually if using containerd; this starter preserves that setting.'; return 2 }
    $docker = Get-Ds60WindowsDocker
    return Invoke-Ds60DockerLauncher -Action $Action -NoBrowser:$NoBrowser -Port $Port -DatabasePort $DatabasePort -DataDir $DataDir -Project $Project -Docker $docker -Selection $ready
}

# Dot sourcing exposes helpers for tests, without native actions or state writes.
if ($MyInvocation.InvocationName -ne '.') { exit (Invoke-Ds60WindowsDocker @PSBoundParameters) }
