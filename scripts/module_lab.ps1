[CmdletBinding()]
param(
    [ValidateSet('build', 'start', 'stop', 'status')][string]$Action = 'status',
    [string]$Profiles = 'python-core',
    [switch]$NoBrowser,
    [switch]$Interactive,
    [string]$K8sSession,
    [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
if ($Interactive) {
    Write-Host 'Choose prepared profiles: python-core, cpp20, tensorflow-cpu, scala-jvm, spark-local-scala, spark-local-python'
    $Answer = Read-Host 'Comma-separated profiles [python-core]'
    if ($Answer) { $Profiles = $Answer }
}
$Root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$Names = @{'python-core'='python-core-worker'; 'cpp20'='cpp-worker'; 'tensorflow-cpu'='tensorflow-worker'; 'llm-torch-cpu'='llm-worker'; 'scala-jvm'='scala-worker'; 'spark-local-scala'='spark-scala-worker'; 'spark-local-python'='spark-python-worker'; 'k8s-kind'='kubernetes-worker'}
$Selected = @($Profiles.Split(','))
$K8s = $Selected -contains 'k8s-kind'
$Services = @()
$Endpoints = @{}
foreach ($Profile in $Selected) {
    if (-not $Names.ContainsKey($Profile)) { throw "Unknown profile $Profile. Use a registered profile." }
    $Services += $Names[$Profile]
    $Endpoints[$Profile] = 'http://' + $Names[$Profile] + ':8081'
}
$Project = if ($env:DS60_MODULE_PROJECT) { $env:DS60_MODULE_PROJECT } else { 'ds60-learning' }
if ($Project -notmatch '^[a-z0-9][a-z0-9_-]{0,48}$') { throw 'Invalid Compose project name.' }
$Endpoint = $env:DOCKER_HOST
if ($Endpoint) { Remove-Item Env:DOCKER_CONTEXT -ErrorAction SilentlyContinue }
if (-not $Endpoint) {
    $Endpoint = & docker context inspect --format '{{.Endpoints.docker.Host}}'
    if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect the selected Docker context.' }
}
if ($Endpoint -notmatch '^(unix:///[^\r\n]+|npipe:/{2,4}\./pipe/[A-Za-z0-9_.-]+|tcp://(127\.0\.0\.1|localhost):[0-9]{1,5})$') {
    throw 'Choose a local Docker context before preparing host-saved modules.'
}
$env:DOCKER_HOST = $Endpoint
Remove-Item Env:DOCKER_CONTEXT -ErrorAction SilentlyContinue
& docker compose version | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Docker Compose is unavailable.' }
& docker info | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Start a Docker-compatible Linux-container engine first.' }
$OperatingSystem = & docker info --format '{{.OSType}}'
if ($OperatingSystem.Trim() -ne 'linux') { throw 'Switch the engine to Linux containers.' }
$Security = & docker info --format '{{json .SecurityOptions}}'
if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect local engine identity support.' }
if ($Security -match 'rootless') {
    $env:DS60_UID = '0'; $env:DS60_GID = '0'; $env:DS60_ROOTLESS = '1'
} else {
    if (-not $env:DS60_UID) { $env:DS60_UID = '1000' }
    if (-not $env:DS60_GID) { $env:DS60_GID = '1000' }
    $env:DS60_ROOTLESS = '0'
}
$Hash = [Security.Cryptography.SHA256]::Create()
try { $Scope = ([BitConverter]::ToString($Hash.ComputeHash([Text.Encoding]::UTF8.GetBytes($Root)))).Replace('-', '').Substring(0,16) } finally { $Hash.Dispose() }
$Session = if ($env:DS60_MODULE_RUNTIME_DIR) { $env:DS60_MODULE_RUNTIME_DIR } else { Join-Path ([IO.Path]::GetTempPath()) ('ds60-modules-' + $Scope + '-' + $Project) }
if (-not [IO.Path]::IsPathRooted($Session)) { throw 'Use an absolute private module runtime path.' }
$Session = [IO.Path]::GetFullPath($Session)
$env:DS60_MODULE_RUNTIME_DIR = $Session
$env:DS60_MODULE_ENDPOINTS = ConvertTo-Json -InputObject $Endpoints -Compress
if (-not $env:DS60_LEARNING_DIR) { $env:DS60_LEARNING_DIR = Join-Path $Root '.learning' }
if ($K8s) {
    $env:DS60_K8S_SESSION_DIR = if ($K8sSession) { $K8sSession } else { Join-Path $Session 'not-prepared' }
    if ($Action -eq 'start') {
        if (-not [IO.Path]::IsPathRooted($K8sSession)) { throw 'Use an absolute -K8sSession path from the preparation receipt.' }
        if (-not $K8sSession) { throw 'Kubernetes start requires -K8sSession from explicit host preparation.' }
        & $Python (Join-Path $Root 'scripts/prepare_kubernetes.py') inspect --session $K8sSession --docker-host $Endpoint
        if ($LASTEXITCODE -ne 0) { throw 'Private Kubernetes lease inspection failed; no services started.' }
    }
}
if ($Action -eq 'status' -or $Action -eq 'stop') {
    $Query = @('compose', '--project-name', $Project, '-f', (Join-Path $Root 'compose.yaml'), '-f', (Join-Path $Root 'compose.modules.yaml'), '--profile', 'lab')
    if ($K8s) { $Query += @('-f', (Join-Path $Root 'compose.kubernetes.yaml')) }
    foreach ($Profile in $Selected) { $Query += @('--profile', $Profile) }
    if ($Action -eq 'status') { & docker @Query ps } else { & docker @Query stop lab @Services }
    if ($LASTEXITCODE -ne 0) { throw 'Module query failed.' }
    return
}
$PrivatePath = [IO.Path]::GetFullPath($Session)
while ($PrivatePath) {
    if ([IO.Path]::GetFileName($PrivatePath) -ieq '.learning') { throw 'Private runtime cannot be inside portable .learning.' }
    if ((Test-Path -LiteralPath $PrivatePath) -and ((Get-Item -LiteralPath $PrivatePath).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Private runtime ancestors cannot be links or junctions.' }
    $ParentPath = [IO.Path]::GetDirectoryName($PrivatePath)
    if ($ParentPath -eq $PrivatePath) { break }
    $PrivatePath = $ParentPath
}
if (Test-Path -LiteralPath $Session) {
    if ((Get-Item -LiteralPath $Session).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Runtime session cannot be a link or junction.' }
}
New-Item -ItemType Directory -Path $Session -Force | Out-Null
if ($env:OS -eq 'Windows_NT') {
    $Identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $Acl = New-Object Security.AccessControl.DirectorySecurity
    $Acl.SetAccessRuleProtection($true, $false)
    $Rule = New-Object Security.AccessControl.FileSystemAccessRule($Identity, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow')
    $Acl.AddAccessRule($Rule)
    Set-Acl -LiteralPath $Session -AclObject $Acl
} else { & chmod 700 $Session; if ($LASTEXITCODE -ne 0) { throw 'Cannot protect private runtime directory.' } }
$TokenPath = Join-Path $Session 'worker-token'
if ((Test-Path -LiteralPath $TokenPath) -and ((Get-Item -LiteralPath $TokenPath).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Worker token cannot be a symbolic link.' }
if (-not (Test-Path -LiteralPath $TokenPath)) {
    $Bytes = New-Object byte[] 32
    $Generator = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $Generator.GetBytes($Bytes) } finally { $Generator.Dispose() }
    $Token = ([BitConverter]::ToString($Bytes)).Replace('-', '').ToLowerInvariant()
    [IO.File]::WriteAllText($TokenPath, $Token, (New-Object Text.UTF8Encoding($false)))
}
if ($env:OS -ne 'Windows_NT') { & chmod 600 $TokenPath; if ($LASTEXITCODE -ne 0) { throw 'Cannot protect worker token.' } }
$env:DS60_MODULE_RUNTIME_DIR = $Session
$env:DS60_MODULE_ENDPOINTS = ConvertTo-Json -InputObject $Endpoints -Compress
if (-not $env:DS60_LEARNING_DIR) { $env:DS60_LEARNING_DIR = Join-Path $Root '.learning' }
New-Item -ItemType Directory -Path $env:DS60_LEARNING_DIR -Force | Out-Null
$Compose = @('compose', '--project-name', $Project, '-f', (Join-Path $Root 'compose.yaml'), '-f', (Join-Path $Root 'compose.modules.yaml'), '--profile', 'lab')
if ($K8s) { $Compose += @('-f', (Join-Path $Root 'compose.kubernetes.yaml')) }
foreach ($Profile in $Selected) { $Compose += @('--profile', $Profile) }
if ($Interactive -and $Action -eq 'start' -and -not $K8s) {
    $Prepare = Read-Host 'Build selected local images now? First preparation needs internet [y/N]'
    if ($Prepare -match '^(y|yes)$') {
        & $PSCommandPath build -Profiles $Profiles -NoBrowser
    }
}
switch ($Action) {
    'build' {
        $BuildServices = @('lab') + $Services
        if ($K8s) { $BuildServices = @('k8s-fixture') + $BuildServices }
        foreach ($Service in $BuildServices) {
            try {
                $HostDrive = New-Object IO.DriveInfo([IO.Path]::GetPathRoot($Root))
                if (-not $HostDrive.IsReady -or $HostDrive.AvailableFreeSpace -lt 8589934592) { throw 'Insufficient host disk.' }
            } catch { throw 'Need at least 8 GiB verified free host disk before building. No cleanup was performed.' }
            # The engine filesystem is measured inside an already prepared base image.
            $Space = & docker run --rm --pull never --network none --entrypoint sh postgres:17 -c 'df -Pk /'
            if ($LASTEXITCODE -ne 0) { throw 'Cannot measure engine disk. Prepare the base course first.' }
            $Parts = ($Space[-1].Trim() -split '\s+')
            if (($Parts.Count -lt 4) -or ([double]$Parts[3] -lt 8388608)) { throw 'Need at least 8 GiB free engine disk. No cleanup was performed.' }
            Write-Host "Building $Service with foreground logs."
            $env:COMPOSE_PROGRESS = 'plain'; $env:BUILDKIT_PROGRESS = 'plain'
            if ($Service -eq 'k8s-fixture') {
                $Base = if ($env:DS60_PYTHON_IMAGE) { $env:DS60_PYTHON_IMAGE } else { 'python:3.12.12-slim-bookworm' }
                & docker build --progress plain -f (Join-Path $Root 'docker/kubernetes/Dockerfile.fixture') --build-arg "DS60_PYTHON_IMAGE=$Base" -t ds60sqlpy-k8s-fixture:0.1.0 $Root
            } else { & docker @Compose build $Service }
            if ($LASTEXITCODE -ne 0) { throw "Build failed for $Service. Saved progress was preserved." }
        }
    }
    'start' {
        & docker @Compose up -d --no-build --pull never --wait --wait-timeout 180 lab @Services
        if ($LASTEXITCODE -ne 0) { throw 'A module service did not become ready. Inspect the worker logs before retrying.' }
        $Port = if ($env:DS60_LAB_PORT) { $env:DS60_LAB_PORT } else { '8765' }
        $Url = 'http://127.0.0.1:' + $Port + '/journeys'
        Write-Host "Module labs: $Url"
        if (-not $NoBrowser) { Start-Process $Url }
    }
    'stop' { & docker @Compose stop lab @Services; if ($LASTEXITCODE -ne 0) { throw 'Module stop failed.' } }
    'status' { & docker @Compose ps; if ($LASTEXITCODE -ne 0) { throw 'Module status failed.' } }
}
