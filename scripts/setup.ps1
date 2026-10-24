[CmdletBinding()]
param(
    [switch]$Advanced
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [string[]]$ArgumentList = @()
    )

    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        $RenderedArguments = $ArgumentList -join " "
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $RenderedArguments"
    }
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$Created = $false
if (Get-Command py -ErrorAction SilentlyContinue) {
    foreach ($Version in @("-3.12", "-3.11")) {
        try {
            Invoke-Native -FilePath "py" -ArgumentList @($Version, "-m", "venv", ".venv")
            $Created = $true
            break
        } catch {
            Write-Verbose "Could not create .venv with py $Version; trying the next supported interpreter."
        }
    }
}

if (-not $Created) {
    $PythonPath = $null
    $PythonCommands = @(
        Get-Command python -CommandType Application -ErrorAction SilentlyContinue
    )
    if ($PythonCommands.Count -eq 0) {
        throw "Python was not found. Install Python 3.12, then rerun this script."
    }
    foreach ($Python in $PythonCommands) {
        if (-not $Python.Source) {
            continue
        }
        try {
            Invoke-Native -FilePath $Python.Source -ArgumentList @(
                "-c",
                "import sys; raise SystemExit(not ((3, 11) <= sys.version_info[:2] < (3, 13)))"
            )
            $PythonPath = [string]$Python.Source
            break
        } catch {
            Write-Verbose "Ignoring an unsupported Python command at $($Python.Source)."
        }
    }
    if (-not $PythonPath) {
        throw "This course supports Python 3.11-3.12. Install Python 3.12, then rerun."
    }
    Invoke-Native -FilePath $PythonPath -ArgumentList @("-m", "venv", ".venv")
}

$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
Invoke-Native -FilePath $VenvPython -ArgumentList @("-m", "pip", "install", "--upgrade", "pip")
Invoke-Native -FilePath $VenvPython -ArgumentList @(
    "-m", "pip", "install", "-e", ".[notebooks,data,quality]"
)

if ($Advanced) {
    Invoke-Native -FilePath $VenvPython -ArgumentList @(
        "-m", "pip", "install", "-e",
        ".[ml,production,bridge,professional,sql-notebooks,deep-learning,nlp,geo]"
    )
}

Invoke-Native -FilePath $VenvPython -ArgumentList @(
    "-m", "ipykernel", "install",
    "--user",
    "--name", "ds60sqlpy",
    "--display-name", "Python (ds60sqlpy)"
)
Invoke-Native -FilePath $VenvPython -ArgumentList @("scripts\course.py", "doctor")

Write-Host ""
Write-Host "Setup complete. Start Jupyter with:"
Write-Host "  .\.venv\Scripts\python.exe -m jupyter lab"
