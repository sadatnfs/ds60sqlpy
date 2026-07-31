#Requires -Version 5.1
<#
.SYNOPSIS
Checks or prepares the DS60 Windows environment and opens the private portal.

.DESCRIPTION
This is the learner-facing Windows orchestrator used by START_DS60.cmd. It
resolves the repository from this script's location, supports either Windows
.venv layout, invokes bootstrap_windows.ps1 only when setup or repair is
needed, runs environment readiness checks, runs the course doctor, and starts
the loopback-only learning portal.

The first setup downloads declared packages and therefore needs an internet
connection. This launcher never requests, stores, or prints a database
credential and never creates, drops, or resets database data. Course doctor
may perform its documented no-prompt, read-only reachability check against only
the disposable course database.

.EXAMPLE
& .\scripts\start_ds60.ps1

.EXAMPLE
& .\scripts\start_ds60.ps1 -DiagnosticsOnly -NonInteractive

.EXAMPLE
& .\scripts\start_ds60.ps1 -WhatIf
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "Low")]
param(
    [ValidateSet("Core", "Advanced")]
    [string]$Profile = "Core",

    [ValidateSet("Auto", "Locked", "Project")]
    [string]$DependencyMode = "Auto",

    [switch]$Setup,

    [switch]$DiagnosticsOnly,

    [switch]$AcceptConnectedSetup,

    [switch]$NonInteractive,

    [switch]$PersistUserPath,

    [switch]$InstallMissingWithWinget,

    [switch]$SkipPostgreSql,

    [switch]$NoBrowser,

    [switch]$NoLaunches,

    [switch]$PauseOnError
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$DryRun = [bool]$WhatIfPreference

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BootstrapScript = Join-Path $PSScriptRoot "bootstrap_windows.ps1"
$PortalScript = Join-Path $PSScriptRoot "learning_portal.py"
$StandardVenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$CondaPrefixPython = Join-Path $RepoRoot ".venv\python.exe"

function Write-Step {
    param([Parameter(Mandatory = $true)][string]$Message)

    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$ArgumentList = @(),
        [switch]$AllowFailure
    )

    # Windows PowerShell 5.1 turns native stderr into PowerShell error records.
    # Let the native exit code, rather than a harmless warning, decide success.
    $PreviousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        & $FilePath @ArgumentList | Out-Host
        $ExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $PreviousErrorActionPreference
    }
    if ($ExitCode -ne 0 -and -not $AllowFailure) {
        $RenderedArguments = $ArgumentList -join " "
        throw "Command failed with exit code ${ExitCode}: $FilePath $RenderedArguments"
    }
    return $ExitCode
}

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$ArgumentList = @()
    )

    # Keep stderr out of structured stdout and prevent Windows PowerShell 5.1
    # from escalating benign native warnings under the script's strict mode.
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
        [switch]$AllowFailure
    )

    # Windows PowerShell 5.1's legacy native-argument serializer removes
    # embedded quote characters from `python -c` source. A short UTF-8 file
    # preserves the probe exactly and is deleted before this function returns.
    $ProbePath = Join-Path `
        ([IO.Path]::GetTempPath()) `
        ("ds60-python-probe-{0}.py" -f [Guid]::NewGuid().ToString("N"))
    try {
        [IO.File]::WriteAllText(
            $ProbePath,
            $Source,
            [Text.UTF8Encoding]::new($false)
        )
        return Invoke-Native `
            -FilePath $PythonPath `
            -ArgumentList @($ProbePath) `
            -AllowFailure:$AllowFailure
    } finally {
        Remove-Item `
            -LiteralPath $ProbePath `
            -Force `
            -ErrorAction SilentlyContinue `
            -WhatIf:$false
    }
}

function Get-CoursePython {
    foreach ($Candidate in @($StandardVenvPython, $CondaPrefixPython)) {
        if (Test-Path -LiteralPath $Candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $Candidate).Path
        }
    }
    return $null
}

function Get-CoursePsql {
    $Candidates = [System.Collections.Generic.List[string]]::new()
    $Seen = @{}

    foreach (
        $Command in @(
            Get-Command "psql" -CommandType Application -ErrorAction SilentlyContinue
        )
    ) {
        if ($Command.Source) {
            $Candidates.Add($Command.Source) | Out-Null
        }
    }

    foreach ($AppPath in @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths\psql.exe",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths\psql.exe",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\psql.exe"
    )) {
        try {
            $RegisteredPath = (Get-Item -Path $AppPath -ErrorAction Stop).GetValue("")
            if (-not [string]::IsNullOrWhiteSpace($RegisteredPath)) {
                $Candidates.Add($RegisteredPath) | Out-Null
            }
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
                $Candidates.Add(
                    (Join-Path $BaseDirectoryProperty.Value "bin\psql.exe")
                ) | Out-Null
            }
        }
    }

    foreach ($ProgramFilesRoot in @($env:ProgramFiles, ${env:ProgramFiles(x86)})) {
        if ([string]::IsNullOrWhiteSpace($ProgramFilesRoot)) {
            continue
        }
        $PostgreSqlRoot = Join-Path $ProgramFilesRoot "PostgreSQL"
        $VersionDirectories = @(
            Get-ChildItem `
                -Path $PostgreSqlRoot `
                -Directory `
                -ErrorAction SilentlyContinue |
                Sort-Object -Property Name -Descending
        )
        foreach ($VersionDirectory in $VersionDirectories) {
            $Candidates.Add(
                (Join-Path $VersionDirectory.FullName "bin\psql.exe")
            ) | Out-Null
        }
    }

    foreach ($Candidate in $Candidates) {
        if (-not (Test-Path -LiteralPath $Candidate -PathType Leaf)) {
            continue
        }
        $Resolved = (Resolve-Path -LiteralPath $Candidate).Path
        $Key = $Resolved.ToLowerInvariant()
        if ($Seen.ContainsKey($Key)) {
            continue
        }
        $Seen[$Key] = $true

        try {
            $VersionOutput = Invoke-NativeCapture `
                -FilePath $Resolved `
                -ArgumentList @("--version")
            if (
                $VersionOutput -match "psql \(PostgreSQL\) (?<major>\d+)" -and
                [int]$Matches.major -ge 16
            ) {
                return $Resolved
            }
        } catch {
            Write-Verbose "Ignoring unusable psql candidate $Resolved."
        }
    }
    return $null
}

function Get-CourseVsCode {
    foreach ($Command in @(Get-Command "code" -ErrorAction SilentlyContinue)) {
        if ($Command.Source) {
            return (Resolve-Path -LiteralPath $Command.Source).Path
        }
    }

    $Candidates = [System.Collections.Generic.List[string]]::new()
    foreach ($Root in @($env:LOCALAPPDATA, $env:ProgramFiles, ${env:ProgramFiles(x86)})) {
        if ([string]::IsNullOrWhiteSpace($Root)) {
            continue
        }
        foreach ($RelativePath in @(
            "Programs\Microsoft VS Code\Code.exe",
            "Microsoft VS Code\Code.exe",
            "Microsoft VS Code\bin\code.cmd"
        )) {
            $Candidates.Add((Join-Path $Root $RelativePath)) | Out-Null
        }
    }
    foreach ($Candidate in $Candidates) {
        if (Test-Path -LiteralPath $Candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $Candidate).Path
        }
    }
    return $null
}

function Add-ProcessToolDirectory {
    param([Parameter(Mandatory = $true)][string]$ExecutablePath)

    $Directory = Split-Path -Parent $ExecutablePath
    $Present = @(
        $env:Path -split ";" |
            Where-Object {
                -not [string]::IsNullOrWhiteSpace($_) -and
                $_.TrimEnd("\") -ieq $Directory.TrimEnd("\")
            }
    ).Count -gt 0
    if (-not $Present) {
        $env:Path = "$Directory;$env:Path"
    }
}

function Test-CourseStack {
    param([Parameter(Mandatory = $true)][string]$PythonPath)

    $Probe = @'
from importlib.metadata import version
import os
import sys

if not ((3, 11) <= sys.version_info[:2] < (3, 13)):
    raise SystemExit(
        f"Unsupported environment Python {sys.version_info.major}.{sys.version_info.minor}; "
        "DS60 supports Python 3.11-3.12."
    )

for distribution in (
    "IPython",
    "ipykernel",
    "jupyterlab",
    "notebook",
    "jupysql",
    "psycopg",
    "sqlalchemy",
    "numpy",
    "pandas",
    "scikit-learn",
    "matplotlib",
    "seaborn",
):
    version(distribution)

import IPython
import ipykernel
import jupyterlab
from jupyter_client.kernelspec import KernelSpecManager
import matplotlib
import notebook
import numpy
import pandas
import psycopg
import seaborn
import sklearn
import sql
import sqlalchemy

kernel = KernelSpecManager().get_kernel_spec("ds60sqlpy")
kernel_python = os.path.normcase(os.path.abspath(kernel.argv[0]))
course_python = os.path.normcase(os.path.abspath(sys.executable))
if kernel_python != course_python:
    raise SystemExit(
        "The Python (ds60sqlpy) kernel points outside this repository environment."
    )

print(f"Course Python: {sys.executable}")
print(f"Python version: {sys.version.split()[0]}")
print("Notebook packages and Python (ds60sqlpy) kernel: ready")
'@

    $ProbeExit = Invoke-PythonSource `
        -PythonPath $PythonPath `
        -Source $Probe `
        -AllowFailure
    return ($ProbeExit -eq 0)
}

function Invoke-Bootstrap {
    $Parameters = @{
        Profile = $Profile
        DependencyMode = $DependencyMode
    }
    if ($PersistUserPath) {
        $Parameters["PersistUserPath"] = $true
    }
    if ($InstallMissingWithWinget) {
        $Parameters["InstallMissingWithWinget"] = $true
    }
    if ($SkipPostgreSql) {
        $Parameters["SkipPostgreSql"] = $true
    }
    if ($DryRun) {
        $Parameters["WhatIf"] = $true
    }

    & $BootstrapScript @Parameters | Out-Host
    if (-not $?) {
        throw "The Windows bootstrap did not complete successfully."
    }
}

function Confirm-ConnectedSetup {
    Write-Host ""
    Write-Host "CONNECTED FIRST SETUP" -ForegroundColor Yellow
    Write-Host "DS60 needs to create or repair this repository's .venv and download"
    Write-Host "the declared course packages. Stay connected until setup finishes."
    Write-Host "Setup requests no database credential and creates, drops, or resets no"
    Write-Host "database data. Course doctor may later make its bounded, read-only,"
    Write-Host "no-prompt reachability check against only the disposable course database."
    Write-Host ""

    if ($AcceptConnectedSetup) {
        return
    }
    if ($NonInteractive) {
        throw @"
Connected setup is required, but this run is noninteractive.
Review the plan with -WhatIf, then rerun with -AcceptConnectedSetup.
"@
    }

    $Response = Read-Host "Type SETUP to continue, or close this window to stop"
    if ($Response.Trim().ToUpperInvariant() -ne "SETUP") {
        throw "Setup was cancelled. Nothing was installed by this launcher."
    }
}

function Invoke-Diagnostics {
    param(
        [AllowNull()]
        [string]$PythonPath,
        [AllowNull()]
        [string]$PsqlPath
    )

    Write-Step "DS60 Windows readiness"
    Write-Host "Repository: $RepoRoot"
    Write-Host "Mode: read-only diagnostics"

    if ([string]::IsNullOrWhiteSpace($PythonPath)) {
        Write-Warning (
            "Repository environment not found. Expected either " +
            "$StandardVenvPython or $CondaPrefixPython."
        )
        return $false
    }

    Write-Host "Environment interpreter: $PythonPath"
    if (-not (Test-CourseStack -PythonPath $PythonPath)) {
        Write-Warning "The repository environment is incomplete or unsupported."
        return $false
    }
    if (-not $SkipPostgreSql -and [string]::IsNullOrWhiteSpace($PsqlPath)) {
        Write-Warning (
            "PostgreSQL 16+ client tools are required for full-course readiness. " +
            "Use -SkipPostgreSql only for an intentional Python-only diagnostic."
        )
        return $false
    }

    Write-Step "Course doctor"
    $DoctorExit = Invoke-Native `
        -FilePath $PythonPath `
        -ArgumentList @("scripts\course.py", "doctor") `
        -AllowFailure
    if ($DoctorExit -ne 0) {
        Write-Warning (
            "Course doctor reported a required-tool failure. Review the FAIL line above."
        )
        return $false
    }

    Write-Host ""
    Write-Host "Readiness diagnostics passed." -ForegroundColor Green
    return $true
}

function Invoke-CourseStart {
    if ($env:OS -ne "Windows_NT") {
        throw "start_ds60.ps1 is intended for Windows 10 or Windows 11."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot "pyproject.toml") -PathType Leaf)) {
        throw "Could not find pyproject.toml beside this launcher."
    }
    if (-not (Test-Path -LiteralPath $BootstrapScript -PathType Leaf)) {
        throw "Missing Windows bootstrap script: $BootstrapScript"
    }
    if (-not (Test-Path -LiteralPath $PortalScript -PathType Leaf)) {
        throw "Missing private portal launcher: $PortalScript"
    }
    if ($DiagnosticsOnly -and $Setup) {
        throw "-DiagnosticsOnly cannot be combined with -Setup."
    }

    Set-Location -LiteralPath $RepoRoot
    Write-Host ""
    Write-Host "DS60 Python + SQL Learning Course" -ForegroundColor Green
    Write-Host "Repository: $RepoRoot"

    Write-Step "Checking Visual Studio Code"
    $VsCodePath = Get-CourseVsCode
    if ($VsCodePath) {
        if ($DryRun) {
            Write-Host (
                "What if: $VsCodePath would be added to this launcher process PATH."
            )
        } else {
            Add-ProcessToolDirectory -ExecutablePath $VsCodePath
        }
        Write-Host "Visual Studio Code: $VsCodePath"
    } else {
        Write-Warning (
            "Visual Studio Code was not found. Install it before using Open in VS Code; " +
            "the browser and Jupyter actions can still work."
        )
    }

    $PsqlPath = $null
    if (-not $SkipPostgreSql) {
        Write-Step "Checking PostgreSQL command-line tools"
        $PsqlPath = Get-CoursePsql
        if ($PsqlPath) {
            if ($DryRun) {
                Write-Host (
                    "What if: $PsqlPath would be added to this launcher process PATH."
                )
            } else {
                Add-ProcessToolDirectory -ExecutablePath $PsqlPath
            }
            Write-Host "PostgreSQL 16+ client: $PsqlPath"
        } else {
            Write-Warning (
                "PostgreSQL 16+ client tools were not found. Connected setup will " +
                "run discovery; use -InstallMissingWithWinget to authorize a system " +
                "install, or -SkipPostgreSql for an intentional Python-only start."
            )
        }
    } else {
        Write-Host "PostgreSQL readiness was explicitly skipped for this Python-only run."
    }

    $CoursePython = Get-CoursePython
    $StackReady = $false
    if ($CoursePython) {
        Write-Step "Checking the existing course environment"
        $StackReady = Test-CourseStack -PythonPath $CoursePython
    }

    if ($DiagnosticsOnly) {
        if (Invoke-Diagnostics -PythonPath $CoursePython -PsqlPath $PsqlPath) {
            return 0
        }
        return 1
    }

    $BootstrapRequested = (
        $Setup -or
        $Profile -eq "Advanced" -or
        $DependencyMode -ne "Auto" -or
        $PersistUserPath -or
        $InstallMissingWithWinget -or
        (-not $SkipPostgreSql -and -not $PsqlPath)
    )
    $NeedsBootstrap = $BootstrapRequested -or -not $StackReady
    if ($DryRun) {
        if ($NeedsBootstrap) {
            Write-Step "Previewing connected setup"
            Invoke-Bootstrap
        } else {
            Write-Host "What if: the ready environment at $CoursePython would be reused."
        }
        Write-Host "What if: course doctor would run."
        Write-Host "What if: the private 127.0.0.1 learning portal would start."
        Write-Host "Dry run complete; the portal was not started."
        return 0
    }

    if ($NeedsBootstrap) {
        Confirm-ConnectedSetup
        Write-Step "Preparing the Windows learning environment"
        Invoke-Bootstrap
        $CoursePython = Get-CoursePython
        if (-not $CoursePython) {
            throw "Bootstrap completed without a recognizable repository interpreter."
        }
        if (-not (Test-CourseStack -PythonPath $CoursePython)) {
            throw "Bootstrap completed, but the course package readiness check failed."
        }
    } else {
        Write-Host "Existing course environment is ready: $CoursePython"
    }

    Write-Step "Running course doctor"
    $DoctorExit = Invoke-Native `
        -FilePath $CoursePython `
        -ArgumentList @("scripts\course.py", "doctor") `
        -AllowFailure
    if ($DoctorExit -ne 0) {
        Write-Warning (
            "Course doctor reported a missing required tool. The portal can still open; " +
            "review the FAIL line above and use its setup guidance before that tool's lessons."
        )
    }

    $PortalArguments = @($PortalScript)
    if ($NoBrowser) {
        $PortalArguments += "--no-browser"
    }
    if ($NoLaunches) {
        $PortalArguments += "--no-launches"
    }

    Write-Step "Starting the private learning portal"
    Write-Host "Your browser will open automatically unless -NoBrowser was supplied."
    Write-Host "Keep this window open while studying; press Ctrl+C here to stop."
    $PortalExit = Invoke-Native `
        -FilePath $CoursePython `
        -ArgumentList $PortalArguments `
        -AllowFailure
    if ($PortalExit -ne 0) {
        throw "The private learning portal exited with code $PortalExit."
    }
    return 0
}

try {
    $Result = Invoke-CourseStart
    exit $Result
} catch {
    Write-Host ""
    Write-Host "DS60 could not start." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Nothing in a database was created, dropped, or reset by this launcher."
    Write-Host "Run diagnostics with:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File `"$PSCommandPath`" -DiagnosticsOnly"
    if ($PauseOnError -and -not $NonInteractive) {
        Read-Host "Press Enter to close this window"
    }
    exit 1
}
