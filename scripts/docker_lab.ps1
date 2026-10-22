#Requires -Version 5.1
[CmdletBinding()]
param(
    [ValidateSet('start', 'build', 'stop', 'status', 'doctor')]
    [string]$Action = 'start',
    [switch]$Build,
    [switch]$NoBrowser,
    [ValidateRange(1, 65535)][int]$Port = 8765,
    [ValidateRange(1, 65535)][int]$DatabasePort = 55432,
    [string]$DataDir,
    [ValidatePattern('^[a-z0-9][a-z0-9_-]{0,48}$')][string]$Project = 'ds60-learning'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
try {
    if ($Port -eq $DatabasePort) { throw 'The browser and database need different host ports.' }
    if (-not $DataDir) {
        if ($env:DS60_LEARNING_DIR) { $DataDir = $env:DS60_LEARNING_DIR }
        else { $DataDir = Join-Path $RepoRoot '.learning' }
    }
    $DataDir = [IO.Path]::GetFullPath($DataDir)
    $DockerCommand = Get-Command docker -ErrorAction SilentlyContinue
    if ($DockerCommand) { $Docker = $DockerCommand.Source }
    elseif (Test-Path (Join-Path $HOME '.rd\bin\docker.exe')) { $Docker = Join-Path $HOME '.rd\bin\docker.exe' }
    else { throw 'Docker CLI not found. Install/start your local Docker engine, then reopen PowerShell.' }
    $Endpoint = $env:DOCKER_HOST
    if ($Endpoint) { Remove-Item Env:DOCKER_CONTEXT -ErrorAction SilentlyContinue }
    if (-not $Endpoint) {
        $Endpoint = & $Docker context inspect --format '{{.Endpoints.docker.Host}}'
        if ($LASTEXITCODE -ne 0) { throw 'Could not read the Docker context.' }
    }
    if ($Endpoint -notmatch '^(unix:///[^\r\n]+|npipe:/{2,4}\./pipe/[A-Za-z0-9_.-]+|tcp://(127\.0\.0\.1|localhost):[0-9]{1,5})$') {
        throw 'Choose a local Docker context so progress stays on this computer.'
    }
    & $Docker compose version
    if ($LASTEXITCODE -ne 0) { throw 'Docker Compose is unavailable. Install the Compose plugin.' }
    $EngineOs = & $Docker info --format '{{.OSType}}'
    if ($LASTEXITCODE -ne 0) { throw 'Docker engine is not ready. Start it and try again.' }
    if ($EngineOs -ne 'linux') { throw 'Switch to Linux containers using the WSL 2 backend.' }
    $Security = & $Docker info --format '{{json .SecurityOptions}}'
    if ($LASTEXITCODE -ne 0) { throw 'Could not inspect Docker engine permissions.' }
    if ($Security -match 'rootless') { $env:DS60_UID = '0'; $env:DS60_GID = '0'; $env:DS60_ROOTLESS = '1' }
    else { $env:DS60_UID = '1000'; $env:DS60_GID = '1000'; $env:DS60_ROOTLESS = '0' }
    $env:DS60_LEARNING_DIR = $DataDir
    $env:DS60_LAB_PORT = [string]$Port
    $env:DS60_POSTGRES_PORT = [string]$DatabasePort
    $Compose = @('compose', '--project-directory', $RepoRoot, '--project-name', $Project,
                 '--file', (Join-Path $RepoRoot 'compose.yaml'), '--profile', 'lab')
    $Url = "http://127.0.0.1:$Port/learn"
    Write-Host "Local lab: $Url"
    Write-Host "Saved progress and pads: $DataDir"
    if ($Action -eq 'doctor') { Write-Host 'Docker and Compose are ready. No data folder was created.'; exit 0 }
    if ($Action -eq 'status') { & $Docker @Compose ps; exit $LASTEXITCODE }
    if ($Action -eq 'stop') { & $Docker @Compose stop; exit $LASTEXITCODE }
    $ExistingImage = & $Docker image ls --quiet 'ds60sqlpy-lab:0.3.0'
    if ($LASTEXITCODE -ne 0) { throw 'Could not inspect local images.' }
    $NeedsBuild = -not $ExistingImage
    if ($Action -eq 'build' -or $Build -or $NeedsBuild) {
        Write-Host 'Building locally. The first build downloads public images/packages. Nothing is pushed.'
        $BuildArgs = @('build')
        if ($env:DS60_BASE_IMAGE) { $BuildArgs += @('--build-arg', "DS60_BASE_IMAGE=$env:DS60_BASE_IMAGE") }
        & $Docker @Compose @BuildArgs lab
        if ($LASTEXITCODE -ne 0) { throw 'Image build failed. Read the first Docker error above.' }
    }
    if ($Action -eq 'build') { exit 0 }
    New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
    & $Docker @Compose up --wait --wait-timeout 120 --no-build
    if ($LASTEXITCODE -ne 0) { throw 'Containers could not start. Check the first error above.' }
    $Ready = $false
    for ($Attempt = 0; $Attempt -lt 120; $Attempt++) {
        try {
            $Request = [System.Net.WebRequest]::Create($Url)
            $Request.Proxy = $null
            $Request.Timeout = 2000
            $Response = $Request.GetResponse()
            try { if ([int]$Response.StatusCode -eq 200) { $Ready = $true } }
            finally { $Response.Close() }
            if ($Ready) { break }
        } catch { Start-Sleep -Seconds 1 }
    }
    if (-not $Ready) {
        & $Docker @Compose logs --tail 40 lab postgres
        throw 'The app did not become ready. Use the status command and review these logs.'
    }
    Write-Host "Ready: $Url"
    Write-Host 'Stop keeps your host-saved progress and database volume.'
    if (-not $NoBrowser) { Start-Process $Url }
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
