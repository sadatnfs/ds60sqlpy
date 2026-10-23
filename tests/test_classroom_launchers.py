"""Run the shared Bash entrypoint against a deterministic Docker/OS boundary."""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def launcher(tmp_path: Path) -> Any:
    if os.name == "nt":
        pytest.skip("Run the Bash boundary inside Linux/WSL; native CMD has separate static checks")
    root = tmp_path / "course with spaces"
    (root / "scripts").mkdir(parents=True)
    (root / "docker").mkdir()
    for name in ("classroom", "scripts/classroom.sh", "START_DOCKER_CLASSROOM.command"):
        shutil.copyfile(ROOT / name, root / name)
    (root / "compose.classroom.yaml").write_text("services: {}\n")
    (root / "docker/registry-mirrors.env.txt").write_text(
        "DS60_POSTGRES_IMAGE=mirror.gcr.io/library/postgres:17\n"
    )
    binaries = tmp_path / "bin"
    binaries.mkdir()
    settings = tmp_path / "mock.json"
    settings.write_text("{}")
    calls, opened = tmp_path / "calls.jsonl", tmp_path / "opened.jsonl"
    docker = binaries / "docker"
    docker.write_text(
        f"#!{sys.executable}\n"
        + r"""
import json,os,sys,signal,time
from pathlib import Path
a=sys.argv[1:];c=json.loads(Path(os.environ['MOCK']).read_text())
row={'args':a,'port':os.getenv('DS60_CLASSROOM_PORT'),
     'db_port':os.getenv('DS60_POSTGRES_PORT')}
with open(os.environ['CALLS'],'a') as f:f.write(json.dumps(row)+'\n')
if a[:1]==['context']:print(c.get('endpoint','unix:///var/run/docker.sock'))
elif a[:2]==['compose','version']:print(c.get('version','2.28.0'))
elif a[:1]==['info']:
 if c.get('engine_down'):sys.exit(7)
 print(c.get('engine_os','linux'))
elif a[:2]==['image','inspect']:sys.exit(1 if c.get('missing_database') else 0)
elif a[:1]==['inspect']:
 print(c.get('existing_db_port','55432')
       if '5432/tcp' in a[2] else c.get('existing_port','8765'))
elif 'config' in a and '--environment' in a:
 values={'COMPOSE_PROJECT_NAME':'ds60-classroom','UNRELATED_SECRET':'DUMMY_NEVER_LOG_THIS'}
 for i,v in enumerate(a):
  if v=='--env-file':
   for line in Path(a[i+1]).read_text().splitlines():
    if '=' in line and not line.startswith('#'):
     k,v=line.split('=',1);values[k]=v
 for k,v in os.environ.items():
  if k.startswith('DS60_') or k=='COMPOSE_PROJECT_NAME':values[k]=v
 if '--project-name' in a:values['COMPOSE_PROJECT_NAME']=a[a.index('--project-name')+1]
 values.update(c.get('environment',{}))
 for k,v in values.items():print(k+'='+v)
elif 'ps' in a and '--quiet' in a:
 if c.get('existing'):print('owned-postgres')
elif 'port' in a:
 if c.get('fail')=='port':sys.exit(7)
 assert a[-1]==c.get('internal_port','8765'),a
 port=os.getenv('DS60_CLASSROOM_PORT')
 print(c.get('address','127.0.0.1:'+str(port if port!='0' else '49152')))
elif 'build' in a:
 if c.get('signal'):
  os.kill(os.getppid(),signal.SIGTERM);time.sleep(.1)
 if c.get('fail')=='build' or c.get('fail_build')==a[-1]:sys.exit(7)
elif 'pull' in a and c.get('fail')=='pull':sys.exit(7)
elif 'up' in a and (c.get('fail')=='up' or c.get('fail')==a[-1]):sys.exit(7)
elif 'exec' in a and c.get('fail')=='http':sys.exit(7)
"""
    )
    docker.chmod(0o755)
    for name in ("open", "xdg-open", "cmd.exe"):
        p = binaries / name
        p.write_text(
            f"#!{sys.executable}\n"
            "import json,os,sys\nfrom pathlib import Path\n"
            "c=json.loads(Path(os.environ['MOCK']).read_text())\n"
            "with open(os.environ['OPENED'],'a') as f:"
            " f.write(json.dumps(sys.argv)+'\\n')\n"
            "sys.exit(9 if c.get('open_fails') else 0)\n"
        )
        p.chmod(0o755)
    curl = binaries / "curl"
    curl.write_text(
        f"#!{sys.executable}\nimport json,os,sys\nfrom pathlib import Path\n"
        "c=json.loads(Path(os.environ['MOCK']).read_text())\n"
        "sys.exit(7 if c.get('fail')=='external-http' else 0)\n"
    )
    curl.chmod(0o755)
    uname = binaries / "uname"
    uname.write_text(
        f"#!{sys.executable}\nimport json,os\nfrom pathlib import Path\n"
        "print(json.loads(Path(os.environ['MOCK']).read_text()).get('os','Linux'))\n"
    )
    uname.chmod(0o755)
    environment = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("DS60_", "DOCKER_", "COMPOSE_", "WSL_"))
    }
    environment.update(
        PATH=f"{binaries}{os.pathsep}{environment.get('PATH', '')}",
        MOCK=str(settings),
        CALLS=str(calls),
        OPENED=str(opened),
    )
    bash = "/bin/bash" if Path("/bin/bash").exists() else shutil.which("bash")
    if bash is None:
        pytest.skip("Bash is required for this boundary test")

    class Harness:
        directory = root
        env = environment
        config = settings

        def run(self, *args: str, **options: Any) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [str(bash), str(root / "scripts/classroom.sh"), *args],
                cwd=tmp_path,
                env=self.env,
                text=True,
                capture_output=True,
                timeout=20,
                **options,
            )

        def set(self, **values: Any) -> None:
            settings.write_text(json.dumps(values))

        def calls(self) -> list[dict[str, Any]]:
            return [json.loads(x) for x in calls.read_text().splitlines()] if calls.exists() else []

        def opened(self) -> list[Any]:
            return (
                [json.loads(x) for x in opened.read_text().splitlines()] if opened.exists() else []
            )

    return Harness()


def test_default_command_builds_all_profiles_then_starts_health_checks_before_browser(
    launcher: Any,
) -> None:
    launcher.set(missing_database=True)
    result = launcher.run()
    assert result.returncode == 0, result.stderr
    calls = launcher.calls()
    commands = [x["args"] for x in calls]
    builds = [a for a in commands if "build" in a]
    expected = [
        "python-core-worker",
        "cpp-worker",
        "java-worker",
        "javascript-worker",
        "typescript-worker",
        "tensorflow-worker",
        "llm-worker",
        "scala-worker",
        "spark-scala-worker",
        "spark-python-worker",
    ]
    assert [build[build.index("build") + 1 :] for build in builds] == [
        [service] for service in ["lab", *expected]
    ]
    assert commands.index(next(a for a in commands if "pull" in a)) < commands.index(builds[0])
    starts = [a for a in commands if "up" in a]
    assert [a[-1] for a in starts] == ["postgres", "lab", *expected]
    assert commands.index(builds[-1]) < commands.index(starts[0])
    assert all("--wait" in a and "--no-build" in a and "--pull" in a for a in starts)
    assert all("--no-deps" in a for a in starts[2:])
    assert all(c["port"] == "0" and c["db_port"] == "0" for c in calls if "up" in c["args"])
    port_queries = [i for i, command in enumerate(commands) if "port" in command]
    assert commands.index(starts[0]) < port_queries[0] < commands.index(starts[1])
    assert commands.index(next(a for a in commands if "exec" in a)) < port_queries[-1]
    assert launcher.opened()[0][-1] == "http://127.0.0.1:49152/classroom"
    assert "DUMMY_NEVER_LOG_THIS" not in result.stdout + result.stderr
    state = launcher.directory / ".classroom/ds60-classroom"
    assert (state / "ports.env").read_text() == "DS60_CLASSROOM_PORT=0\nDS60_POSTGRES_PORT=0\n"
    assert not (state / "launcher.lock").exists()


@pytest.mark.parametrize(
    "failure", ["pull", "build", "up", "java-worker", "http", "external-http", "port"]
)
def test_failure_never_opens_browser_or_deletes_data(launcher: Any, failure: str) -> None:
    launcher.set(fail=failure, missing_database=True)
    result = launcher.run()
    assert result.returncode != 0
    assert not launcher.opened()
    assert not (launcher.directory / ".classroom/ds60-classroom/launcher.lock").exists()
    assert not any(
        any(x in a["args"] for x in ("down", "prune", "--volumes", "--remove-orphans"))
        for a in launcher.calls()
    )


@pytest.mark.parametrize(
    "address", ["", "0.0.0.0:8765", "127.0.0.1:0", "127.0.0.1:8765\n127.0.0.1:8766"]
)
def test_unconfirmed_address_never_opens_browser(launcher: Any, address: str) -> None:
    launcher.set(address=address)
    result = launcher.run("--starter", "--no-build")
    assert result.returncode != 0 and not launcher.opened()


def test_explicit_env_settings_and_cli_precedence_preserve_local_configuration(
    launcher: Any,
) -> None:
    local = launcher.directory / ".env"
    original = "DS60_LAB_PORT=8766\nDS60_POSTGRES_PORT=55433\nIGNORED=$(touch should-not-exist)\n"
    local.write_text(original)
    launcher.set(internal_port="8766")
    result = launcher.run("--starter", "--port", "8877", "--database-port", "55434", "--no-browser")
    assert result.returncode == 0, result.stderr
    starts = [c for c in launcher.calls() if "up" in c["args"]]
    assert all(c["port"] == "8877" and c["db_port"] == "55434" for c in starts)
    assert local.read_text() == original and not (launcher.directory / "should-not-exist").exists()
    assert "http://127.0.0.1:8877/classroom" in result.stdout
    assert not launcher.opened()


def test_saved_zero_ports_remain_dynamic_on_restart_and_existing_ports_are_adopted(
    launcher: Any,
) -> None:
    launcher.set(existing=True, existing_port="8877", existing_db_port="55434")
    result = launcher.run("--starter", "--no-build", "--no-browser")
    assert result.returncode == 0, result.stderr
    state = launcher.directory / ".classroom/ds60-classroom/ports.env"
    assert state.read_text() == "DS60_CLASSROOM_PORT=8877\nDS60_POSTGRES_PORT=55434\n"
    state.write_text("DS60_CLASSROOM_PORT=0\nDS60_POSTGRES_PORT=0\n")
    result = launcher.run("--starter", "--no-build", "--no-browser")
    assert result.returncode == 0 and "49152/classroom" in result.stdout
    assert not any("build" in c["args"] or "pull" in c["args"] for c in launcher.calls())


def test_profile_selection_deduplicates_and_includes_core(launcher: Any) -> None:
    result = launcher.run("--profile", "java21", "--profile", "java21", "--no-browser")
    assert result.returncode == 0, result.stderr
    builds = [c["args"] for c in launcher.calls() if "build" in c["args"]]
    assert [build[build.index("build") + 1 :] for build in builds] == [
        ["lab"],
        ["python-core-worker"],
        ["java-worker"],
    ]


@pytest.mark.parametrize(
    "config,message",
    [
        ({"endpoint": "ssh://remote.example"}, "local Docker"),
        ({"endpoint": "tcp://other.example:2375"}, "local Docker"),
        ({"version": "2.27.1"}, "2.28.0"),
        ({"engine_os": "windows"}, "Linux containers"),
        ({"engine_down": True}, "not ready"),
        ({"environment": {"DS60_LAB_PORT": "5432"}}, "5432"),
        ({"os": "MINGW64_NT"}, "WSL 2"),
    ],
)
def test_prerequisite_refusals_happen_before_build_or_state_write(
    launcher: Any, config: Any, message: str
) -> None:
    launcher.set(**config)
    result = launcher.run("doctor")
    assert result.returncode != 0 and message in result.stdout + result.stderr
    assert not any("build" in x["args"] or "up" in x["args"] for x in launcher.calls())
    assert not (launcher.directory / ".classroom").exists()


@pytest.mark.parametrize(
    "args",
    [
        ["--port", "65536"],
        ["--port", "-1"],
        ["--port", "2x"],
        ["--profile", "k8s-kind"],
        ["--project", "../other"],
        ["--unknown"],
    ],
)
def test_bad_arguments_do_not_contact_engine(launcher: Any, args: list[str]) -> None:
    assert launcher.run(*args).returncode != 0
    assert not launcher.calls()


def test_doctor_is_read_only_and_help_does_not_need_an_engine(launcher: Any) -> None:
    assert launcher.run("--help").returncode == 0 and not launcher.calls()
    result = launcher.run("doctor", "--starter")
    assert result.returncode == 0 and not (launcher.directory / ".classroom").exists()


def test_stop_only_stops_the_selected_project_without_building_or_removing_volumes(
    launcher: Any,
) -> None:
    result = launcher.run("stop", "--project", "my-classroom")
    assert result.returncode == 0, result.stderr
    stop = next(c["args"] for c in launcher.calls() if "stop" in c["args"])
    assert stop[stop.index("-p") + 1] == "my-classroom" and "--profile" in stop and "*" in stop
    assert not any("build" in c["args"] or "pull" in c["args"] for c in launcher.calls())


def test_live_launcher_lock_is_preserved(launcher: Any) -> None:
    lock = launcher.directory / ".classroom/ds60-classroom/launcher.lock"
    lock.mkdir(parents=True)
    (lock / "pid").write_text(str(os.getpid()))
    result = launcher.run("--starter")
    assert result.returncode != 0 and "Another launcher" in result.stderr
    assert (lock / "pid").read_text() == str(os.getpid())
    assert not any("build" in c["args"] for c in launcher.calls())


def test_signal_releases_owned_lock_and_does_not_start_services(launcher: Any) -> None:
    launcher.set(signal=True)
    result = launcher.run("--starter")
    assert result.returncode == 130 and not launcher.opened()
    assert not (launcher.directory / ".classroom/ds60-classroom/launcher.lock").exists()
    assert not any("up" in c["args"] for c in launcher.calls())


def test_wsl_browser_handoff_and_browser_failure_leave_healthy_classroom_ready(
    launcher: Any,
) -> None:
    launcher.env["WSL_DISTRO_NAME"] = "Ubuntu"
    launcher.set(open_fails=True)
    result = launcher.run("--starter", "--no-build")
    assert result.returncode == 0, result.stderr
    assert launcher.opened()[0][0].endswith("cmd.exe")
    assert "Windows browser" in result.stdout


def test_thin_launchers_share_the_one_command_implementation() -> None:
    source = (ROOT / "classroom.cmd").read_text()
    assert 'wsl.exe --cd "%~dp0." --exec bash ./classroom %*' in source
    assert "docker compose" not in source
    assert "classroom.cmd" in (ROOT / "START_DOCKER_CLASSROOM.cmd").read_text()
    assert "/classroom" in (ROOT / "START_DOCKER_CLASSROOM.command").read_text()
    assert b"\r\n" in (ROOT / "classroom.cmd").read_bytes()
    assert "classroom text eol=lf" in (ROOT / ".gitattributes").read_text()


@pytest.mark.parametrize("mode", ["ok", "bad_status", "timeout", "refused"])
def test_no_curl_host_probe_requires_an_actual_http_200(launcher: Any, mode: str) -> None:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    binaries = Path(launcher.env["PATH"].split(os.pathsep)[0])
    (binaries / "curl").unlink()
    for command in ("awk", "dirname", "cat", "mkdir", "rm", "rmdir", "mktemp", "mv", "grep"):
        executable = shutil.which(command)
        assert executable is not None
        (binaries / command).symlink_to(executable)
    launcher.env["PATH"] = str(binaries)
    release = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if mode == "timeout":
                release.wait(12)
                return
            try:
                self.send_response(200 if mode == "ok" else 400)
                self.end_headers()
            except OSError:
                pass

        def log_message(self, format: str, *args: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    address = f"127.0.0.1:{server.server_port}"
    if mode == "refused":
        server.server_close()
        thread = None
    else:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
    try:
        launcher.set(address=address)
        result = launcher.run("--starter", "--no-build", "--no-browser")
        assert (result.returncode == 0) is (mode == "ok"), result.stdout + result.stderr
        assert not launcher.opened()
        if mode != "ok":
            assert "did not return HTTP 200" in result.stderr
    finally:
        release.set()
        if thread is not None:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


def _stale_lock_fixture(launcher: Any) -> tuple[Path, str]:
    """Use an owned, reaped process instead of guessing an unused PID."""
    with subprocess.Popen([sys.executable, "-c", "pass"]) as completed:
        completed.wait(timeout=5)
        stale_pid = str(completed.pid)
    lock = launcher.directory / ".classroom/ds60-classroom/launcher.lock"
    lock.mkdir(parents=True)
    (lock / "pid").write_text(stale_pid)
    return lock, stale_pid


def _wait_for_lock_marker(marker: Path) -> None:
    deadline = time.monotonic() + 8
    while not marker.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert marker.is_file(), f"The controlled launcher did not reach {marker.name}"


def test_stale_launcher_pid_is_reclaimed_without_removing_project_state(launcher: Any) -> None:
    lock, _ = _stale_lock_fixture(launcher)
    retained = lock.parent / "retained-setting.txt"
    retained.write_text("keep this project state")
    result = launcher.run("--starter", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    assert retained.read_text() == "keep this project state"
    assert (lock.parent / "ports.env").is_file()
    assert not lock.exists()
    assert not (lock.parent / "launcher-recovery.lock").exists()
    assert sum("build" in call["args"] for call in launcher.calls()) == 2


def test_busy_recovery_mutex_preserves_stale_pid_and_does_not_build(launcher: Any) -> None:
    lock, stale_pid = _stale_lock_fixture(launcher)
    recovery = lock.parent / "launcher-recovery.lock"
    recovery.mkdir()
    retained = recovery / "other-reclaimer-marker"
    retained.write_text("owned by another recovery")
    result = launcher.run("--starter", "--no-browser")
    assert result.returncode != 0
    assert "recovering the lock" in result.stderr
    assert (lock / "pid").read_text() == stale_pid
    assert retained.read_text() == "owned by another recovery"
    assert not launcher.opened()
    assert not any("build" in call["args"] or "up" in call["args"] for call in launcher.calls())


def test_concurrent_reclaimers_preserve_the_winning_launchers_new_pid(launcher: Any) -> None:
    if sys.platform == "win32":
        pytest.skip("The concurrent Bash process-group boundary runs inside WSL on Windows.")
    lock, stale_pid = _stale_lock_fixture(launcher)
    recovery = lock.parent / "launcher-recovery.lock"
    binaries = Path(launcher.env["PATH"].split(os.pathsep)[0])
    rm_ready, rm_release = binaries / "rm-ready", binaries / "rm-release"
    build_ready, build_release = binaries / "build-ready", binaries / "build-release"
    real_rm = shutil.which("rm")
    assert real_rm is not None
    original_docker = binaries / "docker-original"
    (binaries / "docker").rename(original_docker)
    launcher.env.update(
        RECLAIM_PID_FILE=str(lock / "pid"),
        RECLAIM_STALE_PID=stale_pid,
        RECLAIM_RM_READY=str(rm_ready),
        RECLAIM_RM_RELEASE=str(rm_release),
        RECLAIM_BUILD_READY=str(build_ready),
        RECLAIM_BUILD_RELEASE=str(build_release),
        RECLAIM_REAL_RM=real_rm,
        RECLAIM_ORIGINAL_DOCKER=str(original_docker),
    )
    wait_code = (
        "def barrier(ready, release):\n"
        "    Path(ready).write_text('reached')\n"
        "    deadline = time.monotonic() + 15\n"
        "    while not Path(release).exists():\n"
        "        if time.monotonic() >= deadline:\n"
        "            raise SystemExit('test barrier timed out')\n"
        "        time.sleep(0.01)\n"
    )
    header = f"#!{sys.executable}\nimport os, sys, time\nfrom pathlib import Path\n"
    (binaries / "rm").write_text(
        header
        + wait_code
        + "target = Path(os.environ['RECLAIM_PID_FILE'])\n"
        + "if (sys.argv[1:] == [str(target)] and target.is_file()\n"
        + "        and target.read_text().strip() == os.environ['RECLAIM_STALE_PID']):\n"
        + "    barrier(os.environ['RECLAIM_RM_READY'], os.environ['RECLAIM_RM_RELEASE'])\n"
        + "command = os.environ['RECLAIM_REAL_RM']\n"
        + "os.execv(command, [command, *sys.argv[1:]])\n"
    )
    (binaries / "docker").write_text(
        header
        + wait_code
        + "if 'build' in sys.argv[1:]:\n"
        + "    barrier(os.environ['RECLAIM_BUILD_READY'], os.environ['RECLAIM_BUILD_RELEASE'])\n"
        + "command = os.environ['RECLAIM_ORIGINAL_DOCKER']\n"
        + "os.execv(command, [command, *sys.argv[1:]])\n"
    )
    (binaries / "rm").chmod(0o755)
    (binaries / "docker").chmod(0o755)
    bash = "/bin/bash" if Path("/bin/bash").exists() else shutil.which("bash")
    assert bash is not None
    winner = subprocess.Popen(
        [bash, str(launcher.directory / "scripts/classroom.sh"), "--starter", "--no-browser"],
        cwd=launcher.directory.parent,
        env=launcher.env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        # Pause the first reclaimer before deleting the old PID. The second
        # process must fail at the recovery mutex, leaving that state intact.
        _wait_for_lock_marker(rm_ready)
        assert recovery.is_dir()
        blocked = launcher.run("--starter", "--no-browser")
        assert blocked.returncode != 0 and "recovering the lock" in blocked.stderr
        assert (lock / "pid").read_text() == stale_pid
        assert recovery.is_dir()
        rm_release.touch()

        # Hold the winner after it installs its new PID. A later contender
        # must reread that PID, refuse the live owner and release only its mutex.
        _wait_for_lock_marker(build_ready)
        winner_pid = str(winner.pid)
        assert (lock / "pid").read_text().strip() == winner_pid
        assert not recovery.exists()
        later = launcher.run("--starter", "--no-browser")
        assert later.returncode != 0 and "Another launcher is active" in later.stderr
        assert (lock / "pid").read_text().strip() == winner_pid
        assert not recovery.exists()
        assert not any("build" in call["args"] for call in launcher.calls())

        build_release.touch()
        stdout, stderr = winner.communicate(timeout=10)
        assert winner.returncode == 0, stdout + stderr
        assert sum("build" in call["args"] for call in launcher.calls()) == 2
        assert not lock.exists() and not recovery.exists()
    finally:
        rm_release.touch()
        build_release.touch()
        if winner.poll() is None:
            os.killpg(winner.pid, signal.SIGTERM)
            try:
                winner.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(winner.pid, signal.SIGKILL)
                winner.communicate(timeout=5)


@pytest.mark.parametrize("failed_service", ["lab", "cpp-worker"])
def test_failed_serial_build_prevents_later_builds_and_startup(
    launcher: Any, failed_service: str
) -> None:
    launcher.set(fail_build=failed_service)
    result = launcher.run("--profile", "cpp20", "--profile", "java21")
    assert result.returncode != 0
    commands = [call["args"] for call in launcher.calls()]
    builds = [command[command.index("build") + 1 :] for command in commands if "build" in command]
    order = ["lab", "python-core-worker", "cpp-worker", "java-worker"]
    assert builds == [[service] for service in order[: order.index(failed_service) + 1]]
    assert not any("up" in command or "exec" in command for command in commands)
    assert not launcher.opened()
    state = launcher.directory / ".classroom/ds60-classroom"
    assert not (state / "launcher.lock").exists()
    assert not (state / "ports.env").exists()
