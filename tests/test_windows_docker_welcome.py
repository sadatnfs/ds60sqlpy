"""Exercise the Windows first-run policy without installing or starting software.

The real PowerShell main flow is dot-sourced and its OS/native leaf operations
are replaced inside a fresh process. Set DS60_PWSH to a private pwsh executable
when PowerShell is not on PATH. A native Windows PowerShell 5.1 run remains a
separate platform acceptance check.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, TypedDict, cast

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "start_docker_windows.ps1"
CMD = ROOT / "START_DOCKER_LAB.cmd"


def powershell() -> str | None:
    configured = os.environ.get("DS60_PWSH")
    if configured:
        return shutil.which(configured) or (configured if Path(configured).is_file() else None)
    if os.name == "nt":
        native = (
            Path(os.environ.get("SYSTEMROOT", r"C:\Windows"))
            / "System32/WindowsPowerShell/v1.0/powershell.exe"
        )
        if native.is_file():
            return str(native)
    return shutil.which("pwsh")


PWSH = powershell()
requires_powershell = pytest.mark.skipif(
    PWSH is None,
    reason="PowerShell unavailable; set DS60_PWSH to run the fake-backed policy checks",
)


class Call(TypedDict):
    Name: str
    Arguments: dict[str, Any]


class Outcome(TypedDict):
    Code: int | None
    Error: str | None
    Calls: list[Call]
    Transcript: str


HARNESS = r"""
$ErrorActionPreference = 'Stop'
. $env:DS60_SCRIPT_TO_TEST
Set-StrictMode -Version Latest
$script:Scenario = $env:DS60_WINDOWS_SCENARIO | ConvertFrom-Json
$script:Calls = New-Object 'System.Collections.Generic.List[object]'
$script:Installed = $false
$script:Started = $false
$script:WslPrepared = $false
$script:ConsentIndex = 0

function Record-Ds60TestCall {
    param([string]$Name, [hashtable]$Arguments = @{})
    [void]$script:Calls.Add(@{ Name = $Name; Arguments = $Arguments })
}
function Get-Ds60WindowsHost {
    Record-Ds60TestCall 'Host'
    return $script:Scenario.Host
}
function Get-Ds60WindowsDocker {
    Record-Ds60TestCall 'Docker'
    if ($script:Installed -or $script:Started) {
        return 'C:\Program Files\Local Docker\docker.exe'
    }
    return $script:Scenario.Docker
}
function Get-Ds60ReadyLocalDocker {
    param([string]$Docker)
    Record-Ds60TestCall 'Ready' @{ Docker = $Docker }
    return $script:Scenario.InitialReady
}
function Get-Ds60InstalledDesktops {
    Record-Ds60TestCall 'Desktops'
    if ($script:Installed -and @($script:Scenario.Desktops).Count -eq 0) {
        return [pscustomobject]@{
            Name = $script:Scenario.Engine
            Executable = 'C:\Apps\New Engine.exe'
            Rdctl = 'C:\Apps\rdctl.exe'
        }
    }
    return @($script:Scenario.Desktops)
}
function Get-Ds60WslReadiness {
    Record-Ds60TestCall 'Wsl'
    if ($script:WslPrepared) {
        return [pscustomobject]@{
            Ready = $true; NeedsUpdate = $false; Executable = 'wsl.exe'; Reason = ''
        }
    }
    return $script:Scenario.Wsl
}
function Get-Ds60Winget {
    Record-Ds60TestCall 'Winget'
    return $script:Scenario.Winget
}
function Confirm-Ds60WindowsChange {
    param([string]$Message)
    Record-Ds60TestCall 'Consent' @{ Message = $Message }
    if ($script:ConsentIndex -lt @($script:Scenario.ConsentResponses).Count) {
        $answer = [bool]$script:Scenario.ConsentResponses[$script:ConsentIndex]
        $script:ConsentIndex += 1
        return $answer
    }
    return [bool]$script:Scenario.Consent
}
function Test-Ds60UnusedRancherProfile {
    Record-Ds60TestCall 'UnusedProfileCheck'
    return [bool]$script:Scenario.UnusedRancher
}
function Select-Ds60WindowsEngine {
    param([string[]]$Available, [string]$Recommended)
    Record-Ds60TestCall 'Select' @{ Available = @($Available); Recommended = $Recommended }
    return $script:Scenario.Engine
}
function Invoke-Ds60WslSetup {
    param([switch]$Update)
    Record-Ds60TestCall 'InstallWsl' @{ Update = [bool]$Update }
    if ($script:Scenario.WslExit -eq 0) { $script:WslPrepared = $true }
    return [int]$script:Scenario.WslExit
}
function Install-Ds60WindowsEngine {
    param([string]$Engine, [string]$Winget)
    Record-Ds60TestCall 'InstallEngine' @{ Engine = $Engine; Winget = $Winget }
    if ($script:Scenario.InstallExit -eq 0) { $script:Installed = $true }
    return [int]$script:Scenario.InstallExit
}
function Start-Ds60WindowsEngine {
    param([string]$Engine, [object]$Installation, [switch]$Fresh)
    Record-Ds60TestCall 'StartEngine' @{
        Engine = $Engine; Installation = $Installation; Fresh = [bool]$Fresh
    }
    $script:Started = $true
    return [int]$script:Scenario.StartExit
}
function Wait-Ds60LocalDocker {
    param([string]$Docker, [int]$TimeoutSeconds = 180)
    Record-Ds60TestCall 'Wait' @{ Docker = $Docker; TimeoutSeconds = $TimeoutSeconds }
    return $script:Scenario.FinalReady
}
function Invoke-Ds60DockerLauncher {
    param(
        [string]$Action, [switch]$NoBrowser, [int]$Port, [int]$DatabasePort,
        [string]$DataDir, [string]$Project, [string]$Docker, [object]$Selection
    )
    Record-Ds60TestCall 'Launcher' @{
        Action = $Action; NoBrowser = [bool]$NoBrowser; Port = $Port;
        DatabasePort = $DatabasePort; DataDir = $DataDir; Project = $Project;
        Docker = $Docker; Selection = $Selection
    }
    return [int]$script:Scenario.LauncherExit
}

$Parameters = @{}
foreach ($Property in $script:Scenario.Parameters.PSObject.Properties) {
    $Parameters[$Property.Name] = $Property.Value
}
$Failure = $null
$Code = $null
try { $Code = [int](Invoke-Ds60WindowsDocker @Parameters) }
catch { $Failure = $_.Exception.Message }
$Result = @{ Code = $Code; Error = $Failure; Calls = @($script:Calls.ToArray()) }
Write-Output ('DS60_TEST_RESULT=' + ($Result | ConvertTo-Json -Depth 20 -Compress))
"""


def readiness(ready: bool, *, reason: str = "") -> dict[str, object]:
    return {
        "Ready": ready,
        "Context": "existing-local",
        "Host": "npipe:////./pipe/docker_engine",
        "Reason": reason,
    }


def scenario(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "Host": {"IsWindows": True, "Is64Bit": True, "Build": 22631, "Architecture": "X64"},
        "Docker": r"C:\Program Files\Local Docker\docker.exe",
        "InitialReady": readiness(True),
        "Desktops": [],
        "Wsl": {"Ready": True, "NeedsUpdate": False, "Executable": "wsl.exe", "Reason": ""},
        "Winget": r"C:\Tools\winget.exe",
        "Consent": True,
        "ConsentResponses": [],
        "UnusedRancher": False,
        "Engine": "RancherDesktop",
        "WslExit": 0,
        "InstallExit": 0,
        "StartExit": 0,
        "FinalReady": readiness(True),
        "LauncherExit": 0,
        "Parameters": {"Action": "start", "NoBrowser": True},
    }
    result.update(overrides)
    return result


def run_powershell(tmp_path: Path, source: str, payload: dict[str, object] | None = None) -> str:
    harness = tmp_path / "policy harness with spaces.ps1"
    harness.write_text("$ErrorActionPreference = 'Stop'\n" + source, encoding="utf-8")
    environment = dict(os.environ)
    environment.update(
        {
            "DS60_SCRIPT_TO_TEST": str(SCRIPT),
            "DS60_WINDOWS_SCENARIO": json.dumps(payload or {}),
            "DS60_PWSH_RUNTIME": PWSH or "pwsh",
            "POWERSHELL_TELEMETRY_OPTOUT": "1",
            "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
            "DOTNET_SKIP_FIRST_TIME_EXPERIENCE": "1",
            "DOTNET_CLI_HOME": str(tmp_path / "dotnet"),
            "XDG_CACHE_HOME": str(tmp_path / "cache"),
            "XDG_CONFIG_HOME": str(tmp_path / "config"),
            "XDG_DATA_HOME": str(tmp_path / "data"),
        }
    )
    completed = subprocess.run(
        [PWSH or "pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(harness)],
        capture_output=True,
        text=True,
        env=environment,
        timeout=25,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return completed.stdout


def run_policy(tmp_path: Path, payload: dict[str, object]) -> Outcome:
    output = run_powershell(tmp_path, HARNESS, payload)
    encoded = next(
        line.removeprefix("DS60_TEST_RESULT=")
        for line in output.splitlines()
        if line.startswith("DS60_TEST_RESULT=")
    )
    result = cast(Outcome, json.loads(encoded))
    assert result["Error"] is None, result
    result["Transcript"] = output
    return result


def named(result: Outcome, name: str) -> list[Call]:
    return [call for call in result["Calls"] if call["Name"] == name]


def marked_json(output: str, marker: str = "DS60_LEAF=") -> dict[str, Any]:
    line = next(line for line in output.splitlines() if line.startswith(marker))
    return cast(dict[str, Any], json.loads(line.removeprefix(marker)))


MUTATIONS = {"Consent", "Select", "InstallWsl", "InstallEngine", "StartEngine", "Wait", "Launcher"}


@requires_powershell
def test_script_is_safe_to_dot_source_and_has_51_compatible_grammar(tmp_path: Path) -> None:
    source = r"""
$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $env:DS60_SCRIPT_TO_TEST, [ref]$tokens, [ref]$errors)
$modern = $ast.FindAll({param($node)
    $node.GetType().Name -in @('TernaryExpressionAst', 'PipelineChainAst') -or
    ($node -is [System.Management.Automation.Language.BinaryExpressionAst] -and
        $node.Operator.ToString() -eq 'QuestionQuestion')
}, $true)
if (@($errors).Count -or @($modern).Count) { throw 'Unsupported PowerShell grammar' }
. $env:DS60_SCRIPT_TO_TEST
if (-not (Get-Command Invoke-Ds60WindowsDocker -ErrorAction SilentlyContinue)) {
    throw 'The script did not export its main policy function'
}
Write-Output 'DOT_SOURCE_SAFE'
"""
    assert "DOT_SOURCE_SAFE" in run_powershell(tmp_path, source)


@requires_powershell
def test_existing_ready_local_engine_delegates_without_host_mutation(tmp_path: Path) -> None:
    state = tmp_path / "learning state with spaces"
    state.mkdir()
    evidence = state / "progress.json"
    evidence.write_bytes(b"existing learner evidence")
    result = run_policy(
        tmp_path,
        scenario(
            LauncherExit=7,
            Parameters={
                "Action": "start",
                "NoBrowser": True,
                "Port": 18888,
                "DatabasePort": 15432,
                "DataDir": str(state),
                "Project": "my-course",
            },
        ),
    )
    assert result["Code"] == 7
    assert {call["Name"] for call in result["Calls"]} & MUTATIONS == {"Launcher"}
    launch = named(result, "Launcher")[0]["Arguments"]
    assert launch["DataDir"] == str(state)
    assert launch["Port"] == 18888 and launch["DatabasePort"] == 15432
    assert launch["Project"] == "my-course" and launch["NoBrowser"] is True
    assert launch["Selection"]["Context"] == "existing-local"
    assert evidence.read_bytes() == b"existing learner evidence"


@requires_powershell
@pytest.mark.parametrize("parameters", [{"DiagnosticsOnly": True}, {"Action": "doctor"}])
@pytest.mark.parametrize("ready", [False, True])
def test_diagnostics_and_doctor_modes_are_read_only(
    tmp_path: Path, parameters: dict[str, object], ready: bool
) -> None:
    result = run_policy(tmp_path, scenario(InitialReady=readiness(ready), Parameters=parameters))
    assert result["Code"] == (0 if ready else 2)
    assert not ({call["Name"] for call in result["Calls"]} & MUTATIONS)


@requires_powershell
@pytest.mark.parametrize("ready", [False, True])
@pytest.mark.parametrize("action", ["start", "build", "status", "stop"])
def test_noninteractive_only_delegates_an_explicit_action_to_a_ready_engine(
    tmp_path: Path, ready: bool, action: str
) -> None:
    result = run_policy(
        tmp_path,
        scenario(
            InitialReady=readiness(ready),
            Parameters={"Action": action, "NonInteractive": True, "NoBrowser": False},
        ),
    )
    assert result["Code"] == (0 if ready else 2)
    effects = {call["Name"] for call in result["Calls"]} & MUTATIONS
    assert effects == ({"Launcher"} if ready else set())
    if ready:
        args = named(result, "Launcher")[0]["Arguments"]
        assert args["Action"] == action and args["NoBrowser"] is True


@requires_powershell
def test_install_refusal_has_no_installer_start_or_launcher(tmp_path: Path) -> None:
    result = run_policy(
        tmp_path, scenario(Docker=None, InitialReady=readiness(False), Consent=False)
    )
    assert result["Code"] != 0
    assert named(result, "Consent")
    assert not any(
        named(result, name)
        for name in ("InstallWsl", "InstallEngine", "StartEngine", "Wait", "Launcher")
    )


@requires_powershell
def test_missing_winget_uses_manual_recovery_without_an_install_attempt(tmp_path: Path) -> None:
    result = run_policy(tmp_path, scenario(Docker=None, InitialReady=readiness(False), Winget=None))
    assert result["Code"] != 0
    assert not any(named(result, name) for name in ("InstallEngine", "StartEngine", "Launcher"))
    assert "winget" in result["Transcript"].lower()
    assert "https://" in result["Transcript"]


@requires_powershell
@pytest.mark.parametrize("engine", ["RancherDesktop", "DockerDesktop"])
def test_fresh_install_is_consented_and_only_then_launches_selected_engine(
    tmp_path: Path, engine: str
) -> None:
    result = run_policy(
        tmp_path, scenario(Docker=None, InitialReady=readiness(False), Engine=engine)
    )
    assert result["Code"] == 0
    names = [call["Name"] for call in result["Calls"]]
    assert names.index("Consent") < names.index("InstallEngine") < names.index("StartEngine")
    assert named(result, "InstallEngine")[0]["Arguments"]["Engine"] == engine
    assert named(result, "StartEngine")[0]["Arguments"]["Fresh"] is True
    assert named(result, "Select")[0]["Arguments"]["Recommended"] == "RancherDesktop"
    assert len(named(result, "Launcher")) == 1


@requires_powershell
def test_wsl_reboot_exits_before_engine_install_then_rerun_redetects(tmp_path: Path) -> None:
    first = run_policy(
        tmp_path,
        scenario(
            Docker=None,
            InitialReady=readiness(False),
            WslExit=3010,
            Wsl={
                "Ready": False,
                "NeedsUpdate": False,
                "Executable": "wsl.exe",
                "Reason": "WSL missing",
            },
        ),
    )
    assert first["Code"] == 3010
    assert "START_DOCKER_LAB.cmd" in first["Transcript"]
    assert len(named(first, "InstallWsl")) == 1
    assert not any(named(first, name) for name in ("InstallEngine", "StartEngine", "Launcher"))
    second = run_policy(tmp_path, scenario(Docker=None, InitialReady=readiness(False)))
    assert second["Code"] == 0
    assert not named(second, "InstallWsl")
    assert len(named(second, "InstallEngine")) == len(named(second, "Launcher")) == 1


@requires_powershell
def test_existing_desktop_is_started_without_fresh_configuration_or_reinstall(
    tmp_path: Path,
) -> None:
    result = run_policy(
        tmp_path,
        scenario(
            InitialReady=readiness(False),
            Desktops=[
                {
                    "Name": "RancherDesktop",
                    "Executable": r"C:\Apps\Rancher Desktop.exe",
                    "Rdctl": r"C:\Apps\rdctl.exe",
                }
            ],
        ),
    )
    assert result["Code"] == 0
    assert not named(result, "InstallEngine")
    assert named(result, "StartEngine")[0]["Arguments"]["Fresh"] is False
    assert named(result, "Wait") and len(named(result, "Launcher")) == 1


@requires_powershell
@pytest.mark.parametrize("approve_initialization", [False, True])
def test_installed_unused_rancher_after_reboot_needs_separate_initialization_consent(
    tmp_path: Path, approve_initialization: bool
) -> None:
    result = run_policy(
        tmp_path,
        scenario(
            InitialReady=readiness(False),
            Desktops=[
                {
                    "Name": "RancherDesktop",
                    "Executable": r"C:\Apps\Rancher.exe",
                    "Rdctl": r"C:\Apps\rdctl.exe",
                }
            ],
            UnusedRancher=True,
            ConsentResponses=[approve_initialization],
        ),
    )
    assert not named(result, "InstallEngine")
    assert len(named(result, "Consent")) == 1
    assert "Initialize" in named(result, "Consent")[0]["Arguments"]["Message"]
    if approve_initialization:
        assert result["Code"] == 0
        assert named(result, "StartEngine")[0]["Arguments"]["Fresh"] is True
        assert len(named(result, "Launcher")) == 1
    else:
        assert result["Code"] == 2
        assert not named(result, "StartEngine") and not named(result, "Launcher")


@requires_powershell
def test_skip_install_can_start_existing_desktop_but_cannot_install_a_new_one(
    tmp_path: Path,
) -> None:
    installed = run_policy(
        tmp_path,
        scenario(
            InitialReady=readiness(False),
            Desktops=[{"Name": "DockerDesktop", "Executable": r"C:\Apps\Docker.exe", "Rdctl": ""}],
            Parameters={"SkipInstall": True, "NoBrowser": True},
        ),
    )
    assert installed["Code"] == 0
    assert not named(installed, "InstallEngine") and not named(installed, "InstallWsl")
    assert len(named(installed, "StartEngine")) == 1
    missing = run_policy(
        tmp_path,
        scenario(Docker=None, InitialReady=readiness(False), Parameters={"SkipInstall": True}),
    )
    assert missing["Code"] == 2
    assert not any(
        named(missing, name) for name in ("InstallWsl", "InstallEngine", "StartEngine", "Launcher")
    )


@requires_powershell
@pytest.mark.parametrize("reason", ["remote selected context", "Windows containers selected"])
def test_blocked_existing_endpoint_never_installs_or_starts_an_alternative(
    tmp_path: Path, reason: str
) -> None:
    selection = readiness(False, reason=reason)
    selection["Blocked"] = True
    result = run_policy(tmp_path, scenario(InitialReady=selection))
    assert result["Code"] == 2
    assert not ({call["Name"] for call in result["Calls"]} & MUTATIONS)


@requires_powershell
def test_wsl_update_and_installer_reboot_are_propagated_without_auto_restart(
    tmp_path: Path,
) -> None:
    update = run_policy(
        tmp_path,
        scenario(
            Docker=None,
            InitialReady=readiness(False),
            Wsl={
                "Ready": False,
                "NeedsUpdate": True,
                "Executable": "wsl.exe",
                "Reason": "Old kernel",
            },
        ),
    )
    assert update["Code"] == 0
    assert named(update, "InstallWsl")[0]["Arguments"]["Update"] is True
    reboot = run_policy(
        tmp_path,
        scenario(Docker=None, InitialReady=readiness(False), InstallExit=3010),
    )
    assert reboot["Code"] == 3010
    assert not named(reboot, "StartEngine") and not named(reboot, "Launcher")


@requires_powershell
def test_endpoint_classifier_rejects_remote_hosts_and_misleading_local_names(
    tmp_path: Path,
) -> None:
    endpoints = {
        "npipe:////./pipe/docker_engine": True,
        "npipe://./pipe/rancher-desktop": True,
        "unix:///var/run/docker.sock": True,
        "tcp://127.0.0.1:2375": True,
        "tcp://localhost:2375": True,
        "ssh://127.0.0.1": False,
        "tcp://127.0.0.1.example:2375": False,
        "tcp://localhost.example:2375": False,
        "tcp://user@localhost:2375": False,
        "tcp://localhost:2375/extra": False,
        "npipe:////remote-machine/pipe/docker_engine": False,
        "unix://remote-machine/var/run/docker.sock": False,
        "npipe://": False,
        "": False,
    }
    source = r"""
. $env:DS60_SCRIPT_TO_TEST
$payload = $env:DS60_WINDOWS_SCENARIO | ConvertFrom-Json
$results = @(foreach ($endpoint in $payload.Endpoints) {
    @{ Endpoint = $endpoint; Accepted = [bool](Test-Ds60LocalDockerEndpoint -Endpoint $endpoint) }
})
Write-Output ('DS60_LEAF=' + (@{ Results = $results } | ConvertTo-Json -Depth 5 -Compress))
"""
    result = marked_json(run_powershell(tmp_path, source, {"Endpoints": list(endpoints)}))
    assert {row["Endpoint"]: row["Accepted"] for row in result["Results"]} == endpoints


@requires_powershell
def test_real_native_capture_roundtrips_quoted_empty_and_trailing_slash_arguments(
    tmp_path: Path,
) -> None:
    receiver = tmp_path / "argument receiver with spaces.ps1"
    receiver.write_text(
        "Write-Output ('NATIVE_ARGS=' + (@{ Values = @($args); Host = $env:DOCKER_HOST; "
        "Context = $env:DOCKER_CONTEXT } | ConvertTo-Json -Depth 4 -Compress))\n",
        encoding="utf-8",
    )
    values = [
        "",
        "plain",
        "two words",
        'quote"inside',
        r"C:\Course files\notes" + "\\",
        r"C:\trailing" + "\\",
        'slash\\\\"quote',
        "tab\tinside",
        "line\nbreak",
        "literal;$&text",
    ]
    source = r"""
. $env:DS60_SCRIPT_TO_TEST
$case = $env:DS60_WINDOWS_SCENARIO | ConvertFrom-Json
$env:DOCKER_HOST = 'ssh://parent-only.invalid'
$env:DOCKER_CONTEXT = 'parent-only-context'
$arguments = @('-NoLogo','-NoProfile','-NonInteractive','-File',$case.Receiver) + @($case.Values)
$result = Invoke-Ds60WindowsNative -FilePath $env:DS60_PWSH_RUNTIME `
    -Arguments $arguments -TimeoutSeconds 10
Write-Output ('DS60_LEAF=' + (@{
    Result = $result; ParentHost = $env:DOCKER_HOST; ParentContext = $env:DOCKER_CONTEXT
} | ConvertTo-Json -Depth 6 -Compress))
"""
    result = marked_json(
        run_powershell(tmp_path, source, {"Receiver": str(receiver), "Values": values})
    )
    native = result["Result"]
    assert native["ExitCode"] == 0 and native["TimedOut"] is False, native
    received = marked_json(native["Output"], "NATIVE_ARGS=")
    assert received["Values"] == values
    assert received["Host"] is None and received["Context"] is None
    assert result["ParentHost"] == "ssh://parent-only.invalid"
    assert result["ParentContext"] == "parent-only-context"


@requires_powershell
def test_real_native_capture_retains_stderr_exit_code_and_bounds_a_hanging_child(
    tmp_path: Path,
) -> None:
    receiver = tmp_path / "native protocol receiver.ps1"
    receiver.write_text(
        "if ($args[0] -eq 'wait') { Start-Sleep -Seconds 15; exit 0 }\n"
        "Write-Output 'stdout sentinel'\n[Console]::Error.WriteLine('stderr sentinel')\nexit 7\n",
        encoding="utf-8",
    )
    source = r"""
. $env:DS60_SCRIPT_TO_TEST
$case = $env:DS60_WINDOWS_SCENARIO | ConvertFrom-Json
$base = @('-NoLogo','-NoProfile','-NonInteractive','-File',$case.Receiver)
$failed = Invoke-Ds60WindowsNative -FilePath $env:DS60_PWSH_RUNTIME `
    -Arguments ($base + @('fail')) -TimeoutSeconds 8
$timer = [Diagnostics.Stopwatch]::StartNew()
$timed = Invoke-Ds60WindowsNative -FilePath $env:DS60_PWSH_RUNTIME `
    -Arguments ($base + @('wait')) -TimeoutSeconds 1
$timer.Stop()
$payload = @{ Failed = $failed; Timed = $timed; Seconds = $timer.Elapsed.TotalSeconds }
Write-Output ('DS60_LEAF=' + ($payload | ConvertTo-Json -Depth 6 -Compress))
"""
    result = marked_json(run_powershell(tmp_path, source, {"Receiver": str(receiver)}))
    assert result["Failed"]["ExitCode"] == 7
    assert "stdout sentinel" in result["Failed"]["Output"]
    assert "stderr sentinel" in result["Failed"]["Error"]
    assert result["Timed"]["TimedOut"] is True
    assert result["Timed"]["ExitCode"] != 0
    assert 0.7 <= result["Seconds"] < 4


@requires_powershell
@pytest.mark.parametrize("update", [False, True])
def test_wsl_leaf_elevates_only_fixed_install_or_update_and_does_not_reboot(
    tmp_path: Path, update: bool
) -> None:
    source = r"""
. $env:DS60_SCRIPT_TO_TEST
$case = $env:DS60_WINDOWS_SCENARIO | ConvertFrom-Json
$env:SystemRoot = $case.WindowsRoot
$script:call = $null
function Start-Process {
    [CmdletBinding()]
    param([string]$FilePath, [string]$Verb, [switch]$Wait,
        [switch]$PassThru, [string[]]$ArgumentList)
    $script:call = @{
        FilePath = $FilePath; Verb = $Verb; Wait = [bool]$Wait
        PassThru = [bool]$PassThru; Arguments = $ArgumentList
    }
    return [pscustomobject]@{ ExitCode = 3010 }
}
$code = Invoke-Ds60WslSetup -Update:([bool]$case.Update)
$index = [Array]::IndexOf($script:call.Arguments, '-EncodedCommand')
$bytes = [Convert]::FromBase64String($script:call.Arguments[$index + 1])
$decoded = [Text.Encoding]::Unicode.GetString($bytes)
$payload = @{ Code = $code; Call = $script:call; Decoded = $decoded }
Write-Output ('DS60_LEAF=' + ($payload | ConvertTo-Json -Depth 6 -Compress))
"""
    result = marked_json(
        run_powershell(
            tmp_path, source, {"WindowsRoot": str(tmp_path / "Windows root"), "Update": update}
        )
    )
    assert result["Code"] == 3010
    assert result["Call"]["Verb"] == "RunAs"
    assert result["Call"]["Wait"] and result["Call"]["PassThru"]
    assert result["Call"]["FilePath"].endswith("powershell.exe")
    assert ("--update" if update else "--install --no-distribution") in result["Decoded"]
    assert "Restart-Computer" not in result["Decoded"]
    assert "shutdown" not in result["Decoded"].lower()


@requires_powershell
@pytest.mark.parametrize("fresh", [False, True])
def test_rancher_start_leaf_only_sets_moby_for_an_approved_fresh_profile(
    tmp_path: Path, fresh: bool
) -> None:
    executable, rdctl = tmp_path / "Rancher Desktop.exe", tmp_path / "rdctl.exe"
    executable.touch()
    rdctl.touch()
    source = r"""
. $env:DS60_SCRIPT_TO_TEST
$case = $env:DS60_WINDOWS_SCENARIO | ConvertFrom-Json
$script:call = $null
function Start-Process {
    [CmdletBinding()]
    param([string]$FilePath, [switch]$NoNewWindow, [string[]]$ArgumentList = @())
    $script:call = @{ FilePath = $FilePath; Arguments = @($ArgumentList) }
}
$installation = [pscustomobject]@{
    Name = 'RancherDesktop'; Executable = $case.Executable; Rdctl = $case.Rdctl
}
$code = Start-Ds60WindowsEngine -Engine RancherDesktop `
    -Installation $installation -Fresh:([bool]$case.Fresh)
$payload = @{ Code = $code; Call = $script:call }
Write-Output ('DS60_LEAF=' + ($payload | ConvertTo-Json -Depth 5 -Compress))
"""
    result = marked_json(
        run_powershell(
            tmp_path, source, {"Executable": str(executable), "Rdctl": str(rdctl), "Fresh": fresh}
        )
    )
    assert result["Code"] == 0
    if fresh:
        assert result["Call"]["FilePath"] == str(rdctl)
        assert "--container-engine.name=moby" in result["Call"]["Arguments"]
        assert "--kubernetes.enabled=false" in result["Call"]["Arguments"]
    else:
        assert result["Call"]["FilePath"] == str(executable)
        assert result["Call"]["Arguments"] == []


@requires_powershell
@pytest.mark.parametrize(
    "mode", ["unused-remote", "selected-remote", "environment-remote", "windows-engine"]
)
def test_readiness_leaf_never_probes_remote_endpoints_or_switches_contexts(
    tmp_path: Path, mode: str
) -> None:
    source = r"""
. $env:DS60_SCRIPT_TO_TEST
$case = $env:DS60_WINDOWS_SCENARIO | ConvertFrom-Json
Remove-Item Env:DOCKER_HOST -ErrorAction SilentlyContinue
Remove-Item Env:DOCKER_CONTEXT -ErrorAction SilentlyContinue
if ($case.Mode -eq 'environment-remote') { $env:DOCKER_HOST = 'ssh://do-not-contact.invalid' }
$script:calls = New-Object 'System.Collections.Generic.List[object]'
function Invoke-Ds60WindowsNative {
    param([string]$FilePath, [string[]]$Arguments, [int]$TimeoutSeconds)
    [void]$script:calls.Add(@{
        FilePath = $FilePath; Arguments = @($Arguments); TimeoutSeconds = $TimeoutSeconds
    })
    if ($Arguments[0] -eq 'context') {
        $remote = @{
            Name = 'remote-test'; DockerEndpoint = 'ssh://do-not-contact.invalid'
            Current = ($case.Mode -eq 'selected-remote')
        }
        $local = @{
            Name = 'local-test'; DockerEndpoint = 'npipe:////./pipe/docker_engine'
            Current = ($case.Mode -ne 'selected-remote')
        }
        $output = ($remote | ConvertTo-Json -Compress) + "`n" + ($local | ConvertTo-Json -Compress)
    } elseif ($Arguments -contains 'info') {
        $os = if ($case.Mode -eq 'windows-engine') { 'windows' } else { 'linux' }
        $output = @{ OSType = $os } | ConvertTo-Json -Compress
    } else { $output = 'Docker Compose version v2.fake' }
    return [pscustomobject]@{ ExitCode = 0; Output = $output; Error = ''; TimedOut = $false }
}
$ready = Get-Ds60ReadyLocalDocker -Docker 'fake-docker.exe'
$payload = @{ Ready = $ready; Calls = @($script:calls.ToArray()) }
Write-Output ('DS60_LEAF=' + ($payload | ConvertTo-Json -Depth 7 -Compress))
"""
    result = marked_json(run_powershell(tmp_path, source, {"Mode": mode}))
    calls = result["Calls"]
    probes = [call for call in calls if "info" in call["Arguments"]]
    if mode == "unused-remote":
        assert result["Ready"]["Ready"] is True
        assert probes and all(
            call["Arguments"][:2] == ["--context", "local-test"] for call in probes
        )
    elif mode == "windows-engine":
        assert result["Ready"]["Ready"] is False and result["Ready"]["Blocked"] is True
        assert probes
        assert not any("compose" in call["Arguments"] for call in calls)
    else:
        assert result["Ready"]["Ready"] is False and result["Ready"]["Blocked"] is True
        assert not probes
    assert not any("use" in call["Arguments"] or "rm" in call["Arguments"] for call in calls)
    assert not any("remote-test" in call["Arguments"] for call in calls)


@requires_powershell
def test_readiness_wait_retries_and_returns_after_a_bounded_timeout(tmp_path: Path) -> None:
    source = r"""
. $env:DS60_SCRIPT_TO_TEST
$script:polls = 0
$script:succeed = $true
function Get-Ds60ReadyLocalDocker {
    param([string]$Docker)
    $script:polls += 1
    return [pscustomobject]@{
        Ready = ($script:succeed -and $script:polls -ge 2)
        Context = 'local'; Host = ''; Reason = 'still starting'
    }
}
$ready = Wait-Ds60LocalDocker -Docker 'fake-docker.exe' -TimeoutSeconds 5
$readyPolls = $script:polls
$script:succeed = $false
$script:polls = 0
$timer = [Diagnostics.Stopwatch]::StartNew()
$timed = Wait-Ds60LocalDocker -Docker 'fake-docker.exe' -TimeoutSeconds 1
$timer.Stop()
$payload = @{
    Ready = $ready.Ready; ReadyPolls = $readyPolls; Timed = $timed.Ready
    TimedPolls = $script:polls; Seconds = $timer.Elapsed.TotalSeconds
}
Write-Output ('DS60_LEAF=' + ($payload | ConvertTo-Json -Depth 4 -Compress))
"""
    result = marked_json(run_powershell(tmp_path, source))
    assert result["Ready"] is True and result["ReadyPolls"] == 2
    assert result["Timed"] is False and result["TimedPolls"] >= 1
    assert result["Seconds"] < 4


@requires_powershell
def test_unused_profile_leaf_requires_proven_absence_of_settings_policy_and_distros(
    tmp_path: Path,
) -> None:
    source = r"""
. $env:DS60_SCRIPT_TO_TEST
$case = $env:DS60_WINDOWS_SCENARIO | ConvertFrom-Json
$env:LOCALAPPDATA = $case.Root
$env:SystemRoot = $case.Root
$script:mode = ''
$script:nativeCalls = 0
function Test-Path {
    [CmdletBinding()]
    param([string]$LiteralPath, [string]$PathType = 'Any')
    if ($script:mode -eq 'denied') { throw 'policy access denied' }
    if ($script:mode -eq 'profile' -and $LiteralPath -match 'rancher-desktop$') {
        return $true
    }
    if ($script:mode -eq 'policy' -and $LiteralPath -match '^HK') { return $true }
    return ($LiteralPath -match 'wsl\.exe$')
}
function Invoke-Ds60WindowsNative {
    param([string]$FilePath, [string[]]$Arguments, [int]$TimeoutSeconds)
    $script:nativeCalls += 1
    $status = if ($script:mode -eq 'wsl-failure') { 1 } else { 0 }
    $output = if ($script:mode -eq 'distro') { "Ubuntu`nRANCHER-DESKTOP-DATA" }
        else { 'Ubuntu' }
    return [pscustomobject]@{ ExitCode = $status; Output = $output; Error = ''; TimedOut = $false }
}
$results = @{}
foreach ($mode in @('unused','profile','policy','denied','wsl-failure','distro','missing-env')) {
    $script:mode = $mode
    $env:APPDATA = if ($mode -eq 'missing-env') { '' } else { $case.Root }
    $results[$mode] = [bool](Test-Ds60UnusedRancherProfile)
}
Write-Output ('DS60_LEAF=' + (@{ Results = $results } | ConvertTo-Json -Depth 5 -Compress))
"""
    result = marked_json(run_powershell(tmp_path, source, {"Root": str(tmp_path)}))
    assert result["Results"] == {
        "unused": True,
        "profile": False,
        "policy": False,
        "denied": False,
        "wsl-failure": False,
        "distro": False,
        "missing-env": False,
    }


def test_double_click_entry_uses_system_powershell_and_real_crlf_without_host_python() -> None:
    raw = CMD.read_bytes()
    assert b"\r\n" in raw
    assert b"\n" not in raw.replace(b"\r\n", b"")
    assert b"\\r\\n" not in raw
    source = raw.decode("ascii")
    assert "%SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" in source
    assert '-File "%~dp0scripts\\start_docker_windows.ps1" %*' in source
    assert "DS60_DOCKER_EXIT=%ERRORLEVEL%" in source
    assert '"3010"' in source
    assert "same starter" in source.lower()
    assert not re.search(r"(?im)^\s*(?:python|py|git)(?:\.exe)?\s", source)


@requires_powershell
def test_readiness_timeout_does_not_delegate_to_course_launcher(tmp_path: Path) -> None:
    result = run_policy(
        tmp_path,
        scenario(
            InitialReady=readiness(False),
            Desktops=[
                {
                    "Name": "DockerDesktop",
                    "Executable": r"C:\Apps\Docker Desktop.exe",
                    "Rdctl": None,
                }
            ],
            Engine="DockerDesktop",
            FinalReady=readiness(False, reason="still starting"),
        ),
    )
    assert result["Code"] != 0
    assert named(result, "Wait")
    assert not named(result, "Launcher")
    assert 0 < named(result, "Wait")[0]["Arguments"]["TimeoutSeconds"] <= 180


@requires_powershell
@pytest.mark.parametrize("wsl_exit, install_exit, start_exit", [(5, 0, 0), (0, 5, 0), (0, 0, 5)])
def test_failed_prerequisite_operation_stops_before_launch(
    tmp_path: Path, wsl_exit: int, install_exit: int, start_exit: int
) -> None:
    result = run_policy(
        tmp_path,
        scenario(
            Docker=None,
            InitialReady=readiness(False),
            WslExit=wsl_exit,
            InstallExit=install_exit,
            StartExit=start_exit,
            Wsl={
                "Ready": False,
                "NeedsUpdate": False,
                "Executable": "wsl.exe",
                "Reason": "WSL missing",
            },
        ),
    )
    assert result["Code"] != 0
    assert not named(result, "Launcher")


def test_welcome_script_does_not_require_python_git_or_remove_learner_data() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert source.lower().startswith("#requires -version 5.1")
    assert "Invoke-Ds60WindowsDocker" in source
    assert "docker_lab.ps1" in source
    assert (
        re.search(r"(?i)Get-Command\s+['\"]?(?:python[0-9.]*|git|py)(?:['\"\s]|$)", source) is None
    )
    assert not re.search(r"(?i)docker\s+(?:system\s+prune|volume\s+(?:rm|prune))", source)
    assert "Restart-Computer" not in source
    assert "shutdown.exe" not in source.lower()
