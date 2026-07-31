#Requires -Version 5.1
<#
.SYNOPSIS
Bootstraps the DS60 course on Windows when Python or PostgreSQL may not be on PATH.

.DESCRIPTION
Discovers a supported Python installation (including Anaconda/Miniconda) and
PostgreSQL's psql through PATH, the Windows registry, and common installation
locations. The script creates or updates the repository .venv, installs a
selected dependency profile, registers the ds60sqlpy Jupyter kernel, and runs
read-only environment checks.

PATH changes affect only this PowerShell process unless -PersistUserPath is
explicitly supplied. The script never creates, drops, resets, or connects to a
database and never asks for or prints database credentials.

.EXAMPLE
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\scripts\bootstrap_windows.ps1

.EXAMPLE
& .\scripts\bootstrap_windows.ps1 -Profile Advanced -PersistUserPath

.EXAMPLE
& .\scripts\bootstrap_windows.ps1 -DependencyMode Locked
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "Medium")]
param(
    [ValidateSet("Core", "Advanced")]
    [string]$Profile = "Core",

    [ValidateSet("Auto", "Locked", "Project")]
    [string]$DependencyMode = "Auto",

    [switch]$PersistUserPath,

    [switch]$InstallMissingWithWinget,

    [switch]$SkipPostgreSql
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$DryRun = [bool]$WhatIfPreference
$script:LastPythonProbeError = ""
$script:PythonDiscoveryReport = ""

if ($env:OS -ne "Windows_NT") {
    throw "bootstrap_windows.ps1 is intended for Windows 10 or Windows 11."
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvDirectory = Join-Path $RepoRoot ".venv"
$StandardVenvPython = Join-Path $VenvDirectory "Scripts\python.exe"
$CondaPrefixPython = Join-Path $VenvDirectory "python.exe"
$VenvPython = $StandardVenvPython

if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot "pyproject.toml") -PathType Leaf)) {
    throw "Could not find pyproject.toml. Run this script from its checked-out repository."
}

function Write-Step {
    param([Parameter(Mandatory = $true)][string]$Message)

    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$ArgumentList = @()
    )

    # Windows PowerShell 5.1 turns native stderr into PowerShell error records.
    # Temporarily use Continue so a successful tool that prints a warning does
    # not terminate this strict script before we can inspect its exit code.
    $PreviousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        & $FilePath @ArgumentList
        $ExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }
    if ($ExitCode -ne 0) {
        $RenderedArguments = $ArgumentList -join " "
        throw "Command failed with exit code ${ExitCode}: $FilePath $RenderedArguments"
    }
}

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$ArgumentList = @()
    )

    # Keep stderr out of structured stdout such as JSON and version probes.
    # This also avoids the Windows PowerShell 5.1 behavior where redirected
    # native stderr obeys $ErrorActionPreference.
    $OutputPath = [IO.Path]::GetTempFileName()
    $ErrorPath = [IO.Path]::GetTempFileName()
    try {
        $PreviousErrorActionPreference = $ErrorActionPreference
        try {
            $ErrorActionPreference = "Continue"
            & $FilePath @ArgumentList 1> $OutputPath 2> $ErrorPath
            $ExitCode = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $PreviousErrorActionPreference
        }

        $Output = [string](Get-Content -LiteralPath $OutputPath -Raw)
        $Output = $Output.Trim()
        $ErrorText = [string](Get-Content -LiteralPath $ErrorPath -Raw)
        $ErrorText = $ErrorText.Trim()
        if ($ExitCode -ne 0) {
            $RenderedArguments = $ArgumentList -join " "
            $Message = "Command failed with exit code ${ExitCode}: $FilePath $RenderedArguments"
            if (-not [string]::IsNullOrWhiteSpace($ErrorText)) {
                $Message += "`n$ErrorText"
            }
            throw $Message
        }
        if (-not [string]::IsNullOrWhiteSpace($ErrorText)) {
            Write-Verbose $ErrorText
        }
        return $Output
    } finally {
        # Cleanup must override the caller's -WhatIf preference because these
        # two files are implementation details that this function created.
        Remove-Item `
            -LiteralPath $OutputPath, $ErrorPath `
            -Force `
            -ErrorAction SilentlyContinue `
            -WhatIf:$false
    }
}

function Invoke-PythonSource {
    param(
        [Parameter(Mandatory = $true)][string]$PythonPath,
        [Parameter(Mandatory = $true)][string]$Source,
        [string[]]$ArgumentList = @(),
        [switch]$Capture
    )

    # Windows PowerShell 5.1's legacy native-argument serializer removes
    # embedded quote characters from `python -c` source. A short UTF-8 file
    # preserves the Python exactly and is always deleted before returning.
    $ProbePath = Join-Path `
        ([IO.Path]::GetTempPath()) `
        ("ds60-python-probe-{0}.py" -f [Guid]::NewGuid().ToString("N"))
    try {
        [IO.File]::WriteAllText(
            $ProbePath,
            $Source,
            [Text.UTF8Encoding]::new($false)
        )
        if ($Capture) {
            $PythonArguments = @($ProbePath)
            $PythonArguments += $ArgumentList
            return Invoke-NativeCapture `
                -FilePath $PythonPath `
                -ArgumentList $PythonArguments
        }
        $PythonArguments = @($ProbePath)
        $PythonArguments += $ArgumentList
        Invoke-Native -FilePath $PythonPath -ArgumentList $PythonArguments
    } finally {
        Remove-Item `
            -LiteralPath $ProbePath `
            -Force `
            -ErrorAction SilentlyContinue `
            -WhatIf:$false
    }
}

function Add-ExistingFile {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [System.Collections.Generic.List[string]]$Candidates,
        [Parameter(Mandatory = $true)]
        [hashtable]$Seen,
        [AllowNull()]
        [AllowEmptyString()]
        [string]$Path
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return
    }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return
    }

    $Resolved = (Resolve-Path -LiteralPath $Path).Path
    $Key = $Resolved.TrimEnd("\").ToLowerInvariant()
    if (-not $Seen.ContainsKey($Key)) {
        $Seen[$Key] = $true
        $Candidates.Add($Resolved) | Out-Null
    }
}

function Add-ExistingDirectory {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [System.Collections.Generic.List[string]]$Directories,
        [Parameter(Mandatory = $true)]
        [hashtable]$Seen,
        [AllowNull()]
        [AllowEmptyString()]
        [string]$Path
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return
    }
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return
    }

    $Resolved = (Resolve-Path -LiteralPath $Path).Path
    $Key = $Resolved.TrimEnd("\").ToLowerInvariant()
    if (-not $Seen.ContainsKey($Key)) {
        $Seen[$Key] = $true
        $Directories.Add($Resolved) | Out-Null
    }
}

function Get-LastNonEmptyLine {
    param([Parameter(Mandatory = $true)][string]$Text)

    return (
        $Text -split "\r?\n" |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
            Select-Object -Last 1
    ).Trim()
}

function Get-CondaCommands {
    $Candidates = [System.Collections.Generic.List[string]]::new()
    $Seen = @{}

    foreach ($Command in @(Get-Command "conda" -ErrorAction SilentlyContinue)) {
        if ($Command.Source) {
            Add-ExistingFile -Candidates $Candidates -Seen $Seen -Path $Command.Source
        }
    }

    $CondaRoots = [System.Collections.Generic.List[string]]::new()
    $RootSeen = @{}
    foreach ($Root in @(
        (Join-Path $env:USERPROFILE "anaconda3"),
        (Join-Path $env:USERPROFILE "miniconda3"),
        (Join-Path $env:LOCALAPPDATA "anaconda3"),
        (Join-Path $env:LOCALAPPDATA "miniconda3"),
        (Join-Path $env:LOCALAPPDATA "Continuum\anaconda3"),
        (Join-Path $env:ProgramData "Anaconda3"),
        (Join-Path $env:ProgramData "Miniconda3"),
        (Join-Path $env:SystemDrive "Anaconda3"),
        (Join-Path $env:SystemDrive "Miniconda3")
    )) {
        Add-ExistingDirectory -Directories $CondaRoots -Seen $RootSeen -Path $Root
    }

    foreach ($RegistryRoot in @(
        "HKCU:\Software\Python\ContinuumAnalytics",
        "HKLM:\Software\Python\ContinuumAnalytics",
        "HKLM:\Software\WOW6432Node\Python\ContinuumAnalytics"
    )) {
        foreach ($DistributionKey in Get-ChildItem -Path $RegistryRoot -ErrorAction SilentlyContinue) {
            $InstallKey = Join-Path $DistributionKey.PSPath "InstallPath"
            try {
                $InstallDirectory = (Get-Item -Path $InstallKey -ErrorAction Stop).GetValue("")
                Add-ExistingDirectory `
                    -Directories $CondaRoots `
                    -Seen $RootSeen `
                    -Path $InstallDirectory
            } catch {
                Write-Verbose "Could not inspect conda registry key $InstallKey."
            }
        }
    }

    foreach ($UninstallRoot in @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )) {
        foreach ($Product in Get-ItemProperty -Path $UninstallRoot -ErrorAction SilentlyContinue) {
            $DisplayNameProperty = $Product.PSObject.Properties["DisplayName"]
            $InstallLocationProperty = $Product.PSObject.Properties["InstallLocation"]
            if (
                $DisplayNameProperty -and
                $InstallLocationProperty -and
                $DisplayNameProperty.Value -match "^(Anaconda|Miniconda)" -and
                -not [string]::IsNullOrWhiteSpace($InstallLocationProperty.Value)
            ) {
                Add-ExistingDirectory `
                    -Directories $CondaRoots `
                    -Seen $RootSeen `
                    -Path $InstallLocationProperty.Value
            }
        }
    }

    foreach ($Root in $CondaRoots) {
        Add-ExistingFile `
            -Candidates $Candidates `
            -Seen $Seen `
            -Path (Join-Path $Root "Scripts\conda.exe")
        Add-ExistingFile `
            -Candidates $Candidates `
            -Seen $Seen `
            -Path (Join-Path $Root "condabin\conda.bat")
    }

    return $Candidates
}

function Find-UsableConda {
    foreach ($Candidate in Get-CondaCommands) {
        try {
            $null = Invoke-Native `
                -FilePath $Candidate `
                -ArgumentList @("--version")
            return $Candidate
        } catch {
            Write-Verbose "Ignoring unusable conda candidate $Candidate."
        }
    }
    return $null
}

function Get-PythonCandidates {
    $Candidates = [System.Collections.Generic.List[string]]::new()
    $Seen = @{}

    # The Python launcher knows about Python.org installations even when their
    # directories were not added to PATH.
    foreach (
        $Launcher in @(
            Get-Command "py" -CommandType Application -ErrorAction SilentlyContinue
        )
    ) {
        foreach ($Version in @("-3.12", "-3.11")) {
            try {
                $Output = Invoke-NativeCapture `
                    -FilePath $Launcher.Source `
                    -ArgumentList @($Version, "-c", "import sys; print(sys.executable)")
                Add-ExistingFile `
                    -Candidates $Candidates `
                    -Seen $Seen `
                    -Path (Get-LastNonEmptyLine -Text $Output)
            } catch {
                Write-Verbose "The Python launcher did not resolve $Version."
            }
        }
    }

    foreach ($Name in @("python", "python3")) {
        foreach (
            $Command in @(
                Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue
            )
        ) {
            if ($Command.Source -notmatch "\\Microsoft\\WindowsApps\\python(?:3)?\.exe$") {
                Add-ExistingFile -Candidates $Candidates -Seen $Seen -Path $Command.Source
            }
        }
    }

    # Each maintained conda executable lives below either Scripts or condabin,
    # so its parent directory identifies the distribution root without parsing
    # native stdout under Windows PowerShell 5.1.
    foreach ($Conda in Get-CondaCommands) {
        $CondaDirectory = Split-Path -Parent $Conda
        $BaseDirectory = Split-Path -Parent $CondaDirectory
        Add-ExistingFile `
            -Candidates $Candidates `
            -Seen $Seen `
            -Path (Join-Path $BaseDirectory "python.exe")
    }

    # actions/setup-python and some managed Windows installers publish their
    # selected interpreter root through this process-scoped variable.
    if (-not [string]::IsNullOrWhiteSpace($env:pythonLocation)) {
        Add-ExistingFile `
            -Candidates $Candidates `
            -Seen $Seen `
            -Path (Join-Path $env:pythonLocation "python.exe")
    }

    # Python.org and compatible distributions register PythonCore install paths.
    foreach ($RegistryRoot in @(
        "HKCU:\Software\Python\PythonCore",
        "HKLM:\Software\Python\PythonCore",
        "HKLM:\Software\WOW6432Node\Python\PythonCore"
    )) {
        foreach ($VersionKey in Get-ChildItem -Path $RegistryRoot -ErrorAction SilentlyContinue) {
            $InstallKey = Join-Path $VersionKey.PSPath "InstallPath"
            try {
                $InstallItem = Get-Item -Path $InstallKey -ErrorAction Stop
                $ExecutablePath = $InstallItem.GetValue("ExecutablePath")
                if ($ExecutablePath) {
                    Add-ExistingFile `
                        -Candidates $Candidates `
                        -Seen $Seen `
                        -Path $ExecutablePath
                }
                $InstallDirectory = $InstallItem.GetValue("")
                if ($InstallDirectory) {
                    Add-ExistingFile `
                        -Candidates $Candidates `
                        -Seen $Seen `
                        -Path (Join-Path $InstallDirectory "python.exe")
                }
            } catch {
                Write-Verbose "Could not inspect Python registry key $InstallKey."
            }
        }
    }

    # Continuum/Anaconda installers have historically used a provider-specific
    # Python registry branch instead of PythonCore.
    foreach ($RegistryRoot in @(
        "HKCU:\Software\Python\ContinuumAnalytics",
        "HKLM:\Software\Python\ContinuumAnalytics",
        "HKLM:\Software\WOW6432Node\Python\ContinuumAnalytics"
    )) {
        foreach ($DistributionKey in Get-ChildItem -Path $RegistryRoot -ErrorAction SilentlyContinue) {
            $InstallKey = Join-Path $DistributionKey.PSPath "InstallPath"
            try {
                $InstallDirectory = (Get-Item -Path $InstallKey -ErrorAction Stop).GetValue("")
                if ($InstallDirectory) {
                    Add-ExistingFile `
                        -Candidates $Candidates `
                        -Seen $Seen `
                        -Path (Join-Path $InstallDirectory "python.exe")
                }
            } catch {
                Write-Verbose "Could not inspect Anaconda registry key $InstallKey."
            }
        }
    }

    # Anaconda's installer normally records an uninstall location.
    foreach ($UninstallRoot in @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )) {
        foreach ($Product in Get-ItemProperty -Path $UninstallRoot -ErrorAction SilentlyContinue) {
            $DisplayNameProperty = $Product.PSObject.Properties["DisplayName"]
            $InstallLocationProperty = $Product.PSObject.Properties["InstallLocation"]
            if (
                $DisplayNameProperty -and
                $InstallLocationProperty -and
                $DisplayNameProperty.Value -match "^(Anaconda|Miniconda)" -and
                -not [string]::IsNullOrWhiteSpace($InstallLocationProperty.Value)
            ) {
                Add-ExistingFile `
                    -Candidates $Candidates `
                    -Seen $Seen `
                    -Path (Join-Path $InstallLocationProperty.Value "python.exe")
            }
        }
    }

    foreach ($Path in @(
        (Join-Path $env:USERPROFILE "anaconda3\python.exe"),
        (Join-Path $env:USERPROFILE "miniconda3\python.exe"),
        (Join-Path $env:LOCALAPPDATA "anaconda3\python.exe"),
        (Join-Path $env:LOCALAPPDATA "miniconda3\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Continuum\anaconda3\python.exe"),
        (Join-Path $env:ProgramData "Anaconda3\python.exe"),
        (Join-Path $env:ProgramData "Miniconda3\python.exe"),
        (Join-Path $env:SystemDrive "Anaconda3\python.exe"),
        (Join-Path $env:SystemDrive "Miniconda3\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"),
        (Join-Path $env:ProgramFiles "Python312\python.exe"),
        (Join-Path $env:ProgramFiles "Python311\python.exe")
    )) {
        Add-ExistingFile -Candidates $Candidates -Seen $Seen -Path $Path
    }

    return $Candidates
}

function Get-PythonInfo {
    param([Parameter(Mandatory = $true)][string]$Path)

    $InfoPath = [IO.Path]::GetTempFileName()
    $Probe = @'
import json
from pathlib import Path
import sys

Path(sys.argv[1]).write_text(json.dumps({
    "executable": sys.executable,
    "major": sys.version_info.major,
    "minor": sys.version_info.minor,
    "micro": sys.version_info.micro,
}), encoding="utf-8")
'@

    try {
        $null = Invoke-PythonSource `
            -PythonPath $Path `
            -Source $Probe `
            -ArgumentList @($InfoPath)
        $Data = Get-Content -LiteralPath $InfoPath -Raw | ConvertFrom-Json
        return [PSCustomObject]@{
            Path = (Resolve-Path -LiteralPath $Data.executable).Path
            Major = [int]$Data.major
            Minor = [int]$Data.minor
            Micro = [int]$Data.micro
            Version = "$($Data.major).$($Data.minor).$($Data.micro)"
        }
    } catch {
        $script:LastPythonProbeError = $_.Exception.Message
        Write-Verbose "Ignoring unusable Python candidate $Path`: $script:LastPythonProbeError"
        return $null
    } finally {
        Remove-Item `
            -LiteralPath $InfoPath `
            -Force `
            -ErrorAction SilentlyContinue `
            -WhatIf:$false
    }
}

function Find-SupportedPython {
    $Found = @()
    $Failures = [System.Collections.Generic.List[string]]::new()
    $CandidatePaths = @(Get-PythonCandidates)
    foreach ($Candidate in $CandidatePaths) {
        $script:LastPythonProbeError = ""
        $Info = Get-PythonInfo -Path $Candidate
        if ($Info) {
            $Found += $Info
        } else {
            $Failure = $script:LastPythonProbeError -replace "\s+", " "
            $Failures.Add("$Candidate -> $Failure") | Out-Null
        }
    }

    $Supported = @(
        $Found |
            Where-Object {
                $_.Major -eq 3 -and $_.Minor -ge 11 -and $_.Minor -le 12
            } |
            Sort-Object `
                -Property `
                    @{ Expression = { $_.Minor }; Descending = $true },
                    @{ Expression = { $_.Micro }; Descending = $true },
                    @{ Expression = { $_.Path }; Descending = $false }
    )
    if ($Supported.Count -gt 0) {
        $script:PythonDiscoveryReport = (
            "Validated $($Supported.Count) supported interpreter(s) from " +
            "$($CandidatePaths.Count) discovered candidate(s)."
        )
        return $Supported[0]
    }

    if ($Found.Count -gt 0) {
        $Versions = ($Found | ForEach-Object { "$($_.Version) at $($_.Path)" }) -join "; "
        $script:PythonDiscoveryReport = "Unsupported candidates: $Versions"
        Write-Warning "Python was found, but no supported 3.11-3.12 interpreter was found: $Versions"
    } elseif ($CandidatePaths.Count -eq 0) {
        $script:PythonDiscoveryReport = (
            "No executable candidate was found through PATH, the Python launcher, " +
            "pythonLocation, conda, the registry, or maintained install locations."
        )
    } else {
        $FailureSummary = @($Failures | Select-Object -First 3) -join "; "
        $script:PythonDiscoveryReport = (
            "Discovered $($CandidatePaths.Count) candidate(s), but validation failed: " +
            $FailureSummary
        )
    }
    return $null
}

function Get-PsqlCandidates {
    $Candidates = [System.Collections.Generic.List[string]]::new()
    $Seen = @{}

    foreach (
        $Command in @(
            Get-Command "psql" -CommandType Application -ErrorAction SilentlyContinue
        )
    ) {
        Add-ExistingFile -Candidates $Candidates -Seen $Seen -Path $Command.Source
    }

    foreach ($AppPath in @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths\psql.exe",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths\psql.exe",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\psql.exe"
    )) {
        try {
            $RegisteredPath = (Get-Item -Path $AppPath -ErrorAction Stop).GetValue("")
            Add-ExistingFile -Candidates $Candidates -Seen $Seen -Path $RegisteredPath
        } catch {
            Write-Verbose "Could not inspect PostgreSQL App Paths key $AppPath."
        }
    }

    foreach ($RegistryRoot in @(
        "HKLM:\SOFTWARE\PostgreSQL\Installations\*",
        "HKLM:\SOFTWARE\WOW6432Node\PostgreSQL\Installations\*"
    )) {
        foreach ($Installation in Get-ItemProperty -Path $RegistryRoot -ErrorAction SilentlyContinue) {
            $BaseDirectoryProperty = $Installation.PSObject.Properties["Base Directory"]
            if ($BaseDirectoryProperty -and $BaseDirectoryProperty.Value) {
                Add-ExistingFile `
                    -Candidates $Candidates `
                    -Seen $Seen `
                    -Path (Join-Path $BaseDirectoryProperty.Value "bin\psql.exe")
            }
        }
    }

    foreach ($ProgramFilesRoot in @($env:ProgramFiles, ${env:ProgramFiles(x86)})) {
        if ([string]::IsNullOrWhiteSpace($ProgramFilesRoot)) {
            continue
        }
        $PostgreSqlRoot = Join-Path $ProgramFilesRoot "PostgreSQL"
        foreach (
            $VersionDirectory in Get-ChildItem `
                -Path $PostgreSqlRoot `
                -Directory `
                -ErrorAction SilentlyContinue
        ) {
            Add-ExistingFile `
                -Candidates $Candidates `
                -Seen $Seen `
                -Path (Join-Path $VersionDirectory.FullName "bin\psql.exe")
        }
    }

    return $Candidates
}

function Get-PsqlInfo {
    param([Parameter(Mandatory = $true)][string]$Path)

    try {
        $VersionOutput = Invoke-NativeCapture -FilePath $Path -ArgumentList @("--version")
        if ($VersionOutput -notmatch "psql \(PostgreSQL\) (?<major>\d+)(?:\.(?<minor>\d+))?") {
            return $null
        }
        $Minor = 0
        if ($Matches.minor) {
            $Minor = [int]$Matches.minor
        }
        return [PSCustomObject]@{
            Path = (Resolve-Path -LiteralPath $Path).Path
            Major = [int]$Matches.major
            Minor = $Minor
            VersionText = Get-LastNonEmptyLine -Text $VersionOutput
        }
    } catch {
        Write-Verbose "Ignoring unusable psql candidate $Path."
        return $null
    }
}

function Find-SupportedPsql {
    $Found = @()
    foreach ($Candidate in Get-PsqlCandidates) {
        $Info = Get-PsqlInfo -Path $Candidate
        if ($Info) {
            $Found += $Info
        }
    }

    $Supported = @(
        $Found |
            Where-Object { $_.Major -ge 16 } |
            Sort-Object `
                -Property `
                    @{ Expression = { $_.Major }; Descending = $true },
                    @{ Expression = { $_.Minor }; Descending = $true },
                    @{ Expression = { $_.Path }; Descending = $false }
    )
    if ($Supported.Count -gt 0) {
        return $Supported[0]
    }

    if ($Found.Count -gt 0) {
        $Versions = ($Found | ForEach-Object { "$($_.VersionText) at $($_.Path)" }) -join "; "
        Write-Warning "psql was found, but PostgreSQL 16 or newer is required: $Versions"
    }
    return $null
}

function Find-Winget {
    foreach (
        $Command in @(
            Get-Command "winget" -CommandType Application -ErrorAction SilentlyContinue
        )
    ) {
        if ($Command.Source) {
            return $Command.Source
        }
    }
    return $null
}

function Install-WingetPackage {
    param(
        [Parameter(Mandatory = $true)][string]$WingetPath,
        [Parameter(Mandatory = $true)][string]$PackageId
    )

    Write-Warning "Installing $PackageId because -InstallMissingWithWinget was supplied."
    Invoke-Native -FilePath $WingetPath -ArgumentList @(
        "install",
        "--id", $PackageId,
        "--exact",
        "--source", "winget",
        "--accept-package-agreements",
        "--accept-source-agreements"
    )
}

function Add-PathEntries {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [string[]]$Entries,
        [Parameter(Mandatory = $true)]
        [System.EnvironmentVariableTarget]$Target
    )

    # Put explicitly selected tools before older PATH copies while retaining
    # every unrelated entry. This makes `psql` and the repository environment
    # resolve consistently in the current process and future user sessions.
    $RequestedParts = [System.Collections.Generic.List[string]]::new()
    $RequestedSeen = @{}
    foreach ($Entry in $Entries) {
        if (-not (Test-Path -LiteralPath $Entry -PathType Container)) {
            continue
        }
        $Resolved = (Resolve-Path -LiteralPath $Entry).Path
        $Key = $Resolved.TrimEnd("\").ToLowerInvariant()
        if (-not $RequestedSeen.ContainsKey($Key)) {
            $RequestedSeen[$Key] = $true
            $RequestedParts.Add($Resolved) | Out-Null
        }
    }

    $Current = [Environment]::GetEnvironmentVariable("Path", $Target)
    $CurrentParts = [System.Collections.Generic.List[string]]::new()
    $CurrentSeen = @{}
    foreach ($Part in @($Current -split ";")) {
        if ([string]::IsNullOrWhiteSpace($Part)) {
            continue
        }
        $Trimmed = $Part.Trim()
        $Root = [IO.Path]::GetPathRoot($Trimmed)
        if (
            -not $Root -or
            $Trimmed.TrimEnd("\") -ine $Root.TrimEnd("\")
        ) {
            $Trimmed = $Trimmed.TrimEnd("\")
        }
        $Key = $Trimmed.ToLowerInvariant()
        if (-not $CurrentSeen.ContainsKey($Key)) {
            $CurrentSeen[$Key] = $true
            $CurrentParts.Add($Trimmed) | Out-Null
        }
    }

    $Parts = [System.Collections.Generic.List[string]]::new()
    foreach ($Part in $RequestedParts) {
        $Parts.Add($Part) | Out-Null
        $Key = $Part.ToLowerInvariant()
        if ($CurrentSeen.ContainsKey($Key)) {
            Write-Host "Prioritized on $Target PATH: $Part"
        } else {
            Write-Host "Added to $Target PATH: $Part"
        }
    }
    foreach ($Part in $CurrentParts) {
        if (-not $RequestedSeen.ContainsKey($Part.ToLowerInvariant())) {
            $Parts.Add($Part) | Out-Null
        }
    }

    $NewPath = $Parts -join ";"
    [Environment]::SetEnvironmentVariable("Path", $NewPath, $Target)
    if ($Target -eq [System.EnvironmentVariableTarget]::Process) {
        $env:Path = $NewPath
    }
}

function Find-Uv {
    $Candidates = [System.Collections.Generic.List[string]]::new()
    $Seen = @{}
    foreach (
        $Command in @(
            Get-Command "uv" -CommandType Application -ErrorAction SilentlyContinue
        )
    ) {
        # Do not select uv from the environment it is about to synchronize.
        # Windows cannot reliably replace a running executable in that venv.
        $CommandPath = [IO.Path]::GetFullPath($Command.Source)
        $VenvPrefix = [IO.Path]::GetFullPath($VenvDirectory).TrimEnd("\") + "\"
        if (-not $CommandPath.StartsWith($VenvPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            Add-ExistingFile -Candidates $Candidates -Seen $Seen -Path $CommandPath
        }
    }
    Add-ExistingFile `
        -Candidates $Candidates `
        -Seen $Seen `
        -Path (Join-Path $env:USERPROFILE ".local\bin\uv.exe")
    Add-ExistingFile `
        -Candidates $Candidates `
        -Seen $Seen `
        -Path (Join-Path $env:APPDATA "Python\Scripts\uv.exe")

    if ($Candidates.Count -gt 0) {
        return $Candidates[0]
    }
    return $null
}

Write-Step "Discovering Python 3.11-3.12"
$ExistingVenvInfo = $null
if (Test-Path -LiteralPath $StandardVenvPython -PathType Leaf) {
    $VenvPython = $StandardVenvPython
} elseif (Test-Path -LiteralPath $CondaPrefixPython -PathType Leaf) {
    # A Windows conda prefix stores python.exe at the prefix root, whereas a
    # standard-library venv stores it beneath Scripts.
    $VenvPython = $CondaPrefixPython
}

if (Test-Path -LiteralPath $VenvPython -PathType Leaf) {
    $ExistingVenvInfo = Get-PythonInfo -Path $VenvPython
    if (
        -not $ExistingVenvInfo -or
        $ExistingVenvInfo.Major -ne 3 -or
        $ExistingVenvInfo.Minor -lt 11 -or
        $ExistingVenvInfo.Minor -gt 12
    ) {
        throw @"
The existing .venv is not a usable Python 3.11-3.12 environment.
Rename or remove only this repository's .venv after preserving any work you
need, then rerun the bootstrapper. It was not deleted automatically.
"@
    }
} elseif (Test-Path -LiteralPath $VenvDirectory) {
    throw @"
.venv exists but contains neither Scripts\python.exe nor python.exe.
Rename or remove only this repository's incomplete .venv, then rerun.
It was not deleted automatically.
"@
}

$PythonInfo = $null
if (-not $ExistingVenvInfo) {
    $PythonInfo = Find-SupportedPython
}
$CondaForEnvironment = $null
if (-not $PythonInfo -and -not $ExistingVenvInfo) {
    $CondaForEnvironment = Find-UsableConda
    if ($CondaForEnvironment) {
        Write-Warning (
            "Anaconda/Miniconda is installed, but its base Python is outside " +
            "3.11-3.12. Conda will create the supported repository .venv."
        )
    }
}
if (
    -not $PythonInfo -and
    -not $ExistingVenvInfo -and
    -not $CondaForEnvironment -and
    $InstallMissingWithWinget
) {
    $Winget = Find-Winget
    if (-not $Winget) {
        throw "winget is unavailable. Install Python 3.12 manually, then rerun."
    }
    if ($DryRun) {
        Write-Host "What if: winget would install Python.Python.3.12."
    } elseif ($PSCmdlet.ShouldProcess("Python.Python.3.12", "Install with winget")) {
        Install-WingetPackage -WingetPath $Winget -PackageId "Python.Python.3.12"
        $PythonInfo = Find-SupportedPython
    }
}
if (-not $PythonInfo -and -not $ExistingVenvInfo -and -not $CondaForEnvironment) {
    if ($DryRun -and $InstallMissingWithWinget) {
        Write-Host "What if: discovery would run again after the Python installation."
        return
    }
    throw @"
No supported Python interpreter was found.

$script:PythonDiscoveryReport

Install Python 3.12 or Anaconda/Miniconda, then rerun.
To allow an explicit winget installation instead, rerun with:
  -InstallMissingWithWinget
"@
}
if ($PythonInfo) {
    Write-Host "Using Python $($PythonInfo.Version): $($PythonInfo.Path)"
} elseif ($ExistingVenvInfo) {
    Write-Host "Reusing .venv with Python $($ExistingVenvInfo.Version)."
} else {
    Write-Host "Using conda at $CondaForEnvironment to create Python 3.12 at $VenvDirectory."
}

$PsqlInfo = $null
if (-not $SkipPostgreSql) {
    Write-Step "Discovering PostgreSQL 16+"
    $PsqlInfo = Find-SupportedPsql
    if (-not $PsqlInfo -and $InstallMissingWithWinget) {
        $Winget = Find-Winget
        if (-not $Winget) {
            throw "winget is unavailable. Install PostgreSQL 16 or newer manually, then rerun."
        }
        if ($DryRun) {
            Write-Host "What if: winget would install PostgreSQL.PostgreSQL.17."
        } elseif ($PSCmdlet.ShouldProcess("PostgreSQL.PostgreSQL.17", "Install with winget")) {
            Install-WingetPackage -WingetPath $Winget -PackageId "PostgreSQL.PostgreSQL.17"
            $PsqlInfo = Find-SupportedPsql
        }
    }
    if (-not $PsqlInfo) {
        if ($DryRun -and $InstallMissingWithWinget) {
            Write-Host "What if: discovery would run again after the PostgreSQL installation."
            return
        }
        throw @"
No supported psql executable was found.

Install PostgreSQL 16 or newer, or rerun with -InstallMissingWithWinget.
If you intentionally want only the Python lessons, use -SkipPostgreSql.
This bootstrapper never requests a PostgreSQL password or changes a database.
"@
    }
    Write-Host "Using $($PsqlInfo.VersionText): $($PsqlInfo.Path)"
}

$UvBeforeSetup = Find-Uv
if ($DryRun) {
    Write-Step "Dry-run plan"
    Write-Host "What if: selected tool directories would be added to this process PATH."
    if ($PersistUserPath) {
        Write-Host "What if: narrowly scoped executable directories would be added to user PATH."
    }
    if (Test-Path -LiteralPath $VenvPython -PathType Leaf) {
        Write-Host "What if: the existing repository .venv would be validated and reused."
    } elseif ($CondaForEnvironment) {
        Write-Host "What if: conda would create a Python 3.12 environment at $VenvDirectory."
    } else {
        Write-Host "What if: $($PythonInfo.Path) would create the repository .venv."
    }
    if ($DependencyMode -eq "Locked" -or ($DependencyMode -eq "Auto" -and $UvBeforeSetup)) {
        Write-Host "What if: the $Profile profile would be synchronized from uv.lock."
    } else {
        Write-Host "What if: the $Profile profile would be installed from pyproject.toml."
    }
    Write-Host "What if: the Python (ds60sqlpy) kernel would be registered and verified."
    Write-Host "What if: psql, Jupyter, the notebook stack, and course doctor would be checked."
    Write-Host "Dry run complete; no PATH, environment, package, kernel, or system setting changed."
    return
}

Write-Step "Preparing this PowerShell process PATH"
$PathEntries = [System.Collections.Generic.List[string]]::new()
$PathEntrySeen = @{}
$PythonDirectory = $null
if ($PythonInfo) {
    $PythonDirectory = Split-Path -Parent $PythonInfo.Path
    foreach ($Directory in @(
        $PythonDirectory,
        (Join-Path $PythonDirectory "Scripts"),
        (Join-Path $PythonDirectory "Library\bin"),
        (Join-Path $PythonDirectory "condabin")
    )) {
        Add-ExistingDirectory `
            -Directories $PathEntries `
            -Seen $PathEntrySeen `
            -Path $Directory
    }
}
if ($PsqlInfo) {
    Add-ExistingDirectory `
        -Directories $PathEntries `
        -Seen $PathEntrySeen `
        -Path (Split-Path -Parent $PsqlInfo.Path)
}
Add-PathEntries `
    -Entries $PathEntries `
    -Target ([System.EnvironmentVariableTarget]::Process)

if ($PersistUserPath) {
    Write-Step "Persisting selected tool directories to the current user's PATH"
    $PersistentPathEntries = [System.Collections.Generic.List[string]]::new()
    $PersistentEntrySeen = @{}

    # Anaconda recommends using its dedicated prompt/activation instead of
    # permanently placing the entire distribution on PATH. The course itself
    # uses the validated repository interpreter, so only native PostgreSQL
    # needs persistence when no supported base Python was selected.
    if ($PsqlInfo) {
        Add-ExistingDirectory `
            -Directories $PersistentPathEntries `
            -Seen $PersistentEntrySeen `
            -Path (Split-Path -Parent $PsqlInfo.Path)
    }

    # Python.org installs can safely expose their narrow interpreter and
    # Scripts directories. Conda roots contain conda-meta and are excluded.
    if (
        $PythonDirectory -and
        -not (Test-Path -LiteralPath (Join-Path $PythonDirectory "conda-meta"))
    ) {
        Add-ExistingDirectory `
            -Directories $PersistentPathEntries `
            -Seen $PersistentEntrySeen `
            -Path $PythonDirectory
        Add-ExistingDirectory `
            -Directories $PersistentPathEntries `
            -Seen $PersistentEntrySeen `
            -Path (Join-Path $PythonDirectory "Scripts")
    }

    Add-PathEntries `
        -Entries $PersistentPathEntries `
        -Target ([System.EnvironmentVariableTarget]::User)
    Write-Host "User PATH updated with narrow executable directories."
    Write-Host "Anaconda roots are never persisted; new terminals can use conda activation."
} else {
    Write-Host "No persistent PATH setting was changed. Use -PersistUserPath to opt in."
}

Write-Step "Creating or reusing the repository virtual environment"
if ($ExistingVenvInfo) {
    Write-Host "Reusing .venv with Python $($ExistingVenvInfo.Version)."
} elseif ($CondaForEnvironment) {
    Invoke-Native `
        -FilePath $CondaForEnvironment `
        -ArgumentList @(
            "create", "--yes", "--no-default-packages",
            "--prefix", $VenvDirectory, "python=3.12", "pip"
        )
    $VenvPython = $CondaPrefixPython
    Write-Host "Created conda environment $VenvDirectory"
} else {
    Invoke-Native `
        -FilePath $PythonInfo.Path `
        -ArgumentList @("-m", "venv", $VenvDirectory)
    Write-Host "Created $VenvDirectory"
}

$EnvironmentPathEntries = [System.Collections.Generic.List[string]]::new()
$EnvironmentPathSeen = @{}
foreach ($Directory in @(
    $VenvDirectory,
    (Join-Path $VenvDirectory "Library\mingw-w64\bin"),
    (Join-Path $VenvDirectory "Library\usr\bin"),
    (Join-Path $VenvDirectory "Library\bin"),
    (Join-Path $VenvDirectory "Scripts"),
    (Join-Path $VenvDirectory "bin")
)) {
    Add-ExistingDirectory `
        -Directories $EnvironmentPathEntries `
        -Seen $EnvironmentPathSeen `
        -Path $Directory
}
Add-PathEntries `
    -Entries $EnvironmentPathEntries `
    -Target ([System.EnvironmentVariableTarget]::Process)

$ReadyVenvInfo = Get-PythonInfo -Path $VenvPython
if (
    -not $ReadyVenvInfo -or
    $ReadyVenvInfo.Major -ne 3 -or
    $ReadyVenvInfo.Minor -lt 11 -or
    $ReadyVenvInfo.Minor -gt 12
) {
    throw @"
The repository environment did not produce a usable Python 3.11-3.12
interpreter at $VenvPython. It was not deleted automatically.
"@
}
$VenvPython = $ReadyVenvInfo.Path
Write-Host "Environment interpreter verified: $VenvPython"

Write-Step "Installing the $Profile dependency profile"
$CoreExtras = @(
    "notebooks",
    "data",
    "quality",
    "bridge",
    "professional",
    "sql-notebooks"
)
$AdvancedExtras = @(
    "ml",
    "production",
    "deep-learning",
    "nlp",
    "geo"
)
$SelectedExtras = @($CoreExtras)
if ($Profile -eq "Advanced") {
    $SelectedExtras += $AdvancedExtras
}

$Uv = Find-Uv
$ResolvedDependencyMode = $DependencyMode
if ($ResolvedDependencyMode -eq "Auto") {
    if ($Uv) {
        $ResolvedDependencyMode = "Locked"
    } else {
        $ResolvedDependencyMode = "Project"
    }
}

Set-Location $RepoRoot
if ($ResolvedDependencyMode -eq "Locked") {
    if (-not $Uv -and $InstallMissingWithWinget) {
        $Winget = Find-Winget
        if (
            $Winget -and
            $PSCmdlet.ShouldProcess("astral-sh.uv", "Install with winget")
        ) {
            Install-WingetPackage -WingetPath $Winget -PackageId "astral-sh.uv"
            $Uv = Find-Uv
        }
    }
    if (-not $Uv) {
        throw @"
Locked mode requires uv, but uv was not found.
Install uv, use -InstallMissingWithWinget, or choose -DependencyMode Project
to install the same declared extras directly from pyproject.toml.
"@
    }

    $UvArguments = @("sync", "--locked", "--python", $VenvPython)
    foreach ($Extra in $SelectedExtras) {
        $UvArguments += @("--extra", $Extra)
    }
    $PreviousUvProjectEnvironment = [Environment]::GetEnvironmentVariable(
        "UV_PROJECT_ENVIRONMENT",
        [System.EnvironmentVariableTarget]::Process
    )
    try {
        # Explicitly target the repository prefix. This supports both a
        # standard venv and the conda-prefix fallback without asking uv to
        # discover or replace a different environment.
        [Environment]::SetEnvironmentVariable(
            "UV_PROJECT_ENVIRONMENT",
            $VenvDirectory,
            [System.EnvironmentVariableTarget]::Process
        )
        Invoke-Native -FilePath $Uv -ArgumentList $UvArguments
    } finally {
        [Environment]::SetEnvironmentVariable(
            "UV_PROJECT_ENVIRONMENT",
            $PreviousUvProjectEnvironment,
            [System.EnvironmentVariableTarget]::Process
        )
    }
    Write-Host "Installed from the checked and unchanged uv.lock."
} else {
    Invoke-Native -FilePath $VenvPython -ArgumentList @("-m", "ensurepip", "--upgrade")
    $ExtraSpec = ".[$($SelectedExtras -join ',')]"
    Invoke-Native -FilePath $VenvPython -ArgumentList @(
        "-m", "pip", "--disable-pip-version-check",
        "install", "-e", $ExtraSpec
    )
    Write-Host "Installed declared extras from pyproject.toml."
}

Write-Step "Registering the course Jupyter kernel"
Invoke-Native -FilePath $VenvPython -ArgumentList @(
    "-m", "ipykernel", "install",
    "--user",
    "--name", "ds60sqlpy",
    "--display-name", "Python (ds60sqlpy)"
)

Write-Step "Verifying IPython, JupyterLab, Notebook, ipykernel, JupySQL, Psycopg, and SQLAlchemy"
$ImportProbe = @'
from importlib.metadata import version

checks = (
    ("IPython", "IPython"),
    ("JupyterLab", "jupyterlab"),
    ("Notebook", "notebook"),
    ("ipykernel", "ipykernel"),
    ("JupySQL", "jupysql"),
    ("SQLAlchemy", "sqlalchemy"),
    ("Psycopg", "psycopg"),
)
for label, distribution in checks:
    print(f"{label}: {version(distribution)}")

import IPython
import ipykernel
import jupyterlab
import notebook
import psycopg
import sql
import sqlalchemy
'@
Invoke-PythonSource -PythonPath $VenvPython -Source $ImportProbe
Invoke-Native -FilePath $VenvPython -ArgumentList @("-m", "jupyter", "--version")

$KernelProbe = @'
import os
import sys

from jupyter_client.kernelspec import KernelSpecManager

kernel = KernelSpecManager().get_kernel_spec("ds60sqlpy")
kernel_python = os.path.normcase(os.path.abspath(kernel.argv[0]))
course_python = os.path.normcase(os.path.abspath(sys.executable))
if kernel_python != course_python:
    raise SystemExit(
        "The Python (ds60sqlpy) kernel does not point to this repository environment."
    )
print(f"Kernel verified: Python (ds60sqlpy) -> {kernel.argv[0]}")
'@
Invoke-PythonSource -PythonPath $VenvPython -Source $KernelProbe

if ($PsqlInfo) {
    Invoke-Native -FilePath $PsqlInfo.Path -ArgumentList @("--version")
}

Write-Step "Running the course environment doctor"
Invoke-Native `
    -FilePath $VenvPython `
    -ArgumentList @("scripts\course.py", "doctor", "--no-database")

Write-Host ""
Write-Host "Bootstrap complete." -ForegroundColor Green
Write-Host "Python: $VenvPython"
if ($PsqlInfo) {
    Write-Host "psql:   $($PsqlInfo.Path)"
}
Write-Host "Kernel: Python (ds60sqlpy)"
Write-Host ""
Write-Host "Start JupyterLab from the repository root:"
Write-Host "  & `"$VenvPython`" -m jupyter lab"
Write-Host ""
Write-Host "No database was contacted or modified, and no credential was requested."
