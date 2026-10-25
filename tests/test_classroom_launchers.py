"""Run the shared Bash entrypoint against a deterministic Docker/OS boundary."""

from __future__ import annotations

import hashlib
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
    for name in (
        "classroom",
        "scripts/classroom.sh",
        "scripts/classroom_images.sh",
        "scripts/publish-images",
        "docker/classroom-images.tsv",
        "pyproject.toml",
        "START_DOCKER_CLASSROOM.command",
    ):
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
import hashlib,json,os,re,sys,signal,time
from pathlib import Path
a=sys.argv[1:];c=json.loads(Path(os.environ['MOCK']).read_text())
row={'args':a,'port':os.getenv('DS60_CLASSROOM_PORT'),
     'db_port':os.getenv('DS60_POSTGRES_PORT'),'public_port':os.getenv('DS60_PUBLIC_PORT'),
     'image_env':{k:v for k,v in os.environ.items()
                  if k.startswith('DS60_') and k.endswith('_IMAGE')},
     'gpu_device':os.getenv('DS60_GPU_DEVICE')}
if '-' in a and '--hash' in a:row['stdin']=sys.stdin.read()
with open(os.environ['CALLS'],'a') as f:f.write(json.dumps(row)+'\n')
images={'lab':'ds60sqlpy-lab:0.4.0','classroom-init':'ds60sqlpy-lab:0.4.0',
 'postgres':'mirror.gcr.io/library/postgres:17',
 'python-core-worker':'ds60sqlpy-worker-python-core:0.4.0'}
for line in (Path.cwd()/'docker/classroom-images.tsv').read_text().splitlines():
 if not line or line.startswith('#'):continue
 profile,service,repository,suffix,variable,kind=line.split()
 images[service]=os.getenv(variable,repository+':0.4.0')
images['classroom-init']=images['lab']
containers=c.setdefault('containers',{})
if c.get('existing'):containers.setdefault('postgres','owned-postgres')
for service,value in containers.items():
 if not re.fullmatch('[a-f0-9]{64}',value):
  containers[service]=hashlib.sha256(value.encode()).hexdigest()
def save():Path(os.environ['MOCK']).write_text(json.dumps(c))
def service_image(service):return images[service]
def built_service():
 if a[:1]==['build']:
  return next(s for s,i in images.items() if i==a[a.index('--tag')+1])
 return a[-1]
if a[:1]==['context']:print(c.get('endpoint','unix:///var/run/docker.sock'))
elif a[:2]==['compose','version']:print(c.get('version','2.28.0'))
elif a[:1]==['info']:
 if c.get('engine_down'):sys.exit(7)
 print(c.get('architecture','amd64') if '{{.Architecture}}' in a else c.get('engine_os','linux'))
elif a[:2]==['image','tag']:
 assert a[-1] not in c.get('built_images',[]),'must not overwrite a prepared tag'
 c.setdefault('built_images',[]).append(a[-1]);save()
elif a[:2]==['image','push']:
 if c.get('fail')=='push':sys.exit(7)
elif a[:2]==['image','inspect']:
 if a[-1].startswith('sha256:'):
  sys.exit(1 if c.get('missing_container_image') else 0)
 missing=c.get('missing_images',c.get('missing_database',False))
 absent=(missing is True or isinstance(missing,list) and a[-1] in missing)
 if '--format' in a:
  if '{{.Os}}' in a[a.index('--format')+1]:
   platform=c.get('image_platforms',{}).get(a[-1],c.get('image_platform','linux amd64'))
   print(platform+' '+c.get('tag_image_id','sha256:'+'d'*64))
  else:print(c.get('tag_image_id','sha256:'+'d'*64))
 sys.exit(1 if absent and a[-1] not in c.get('built_images',[]) else 0)
elif a[:1]==['inspect']:
 fmt=a[2];id=a[-1]
 if fmt=='{{.Config.Image}}':print(c.get('lab_image_name','ds60sqlpy-lab:0.4.0'))
 elif fmt=='{{.Image}}':print(c.get('lab_image_id','sha256:'+'d'*64))
 elif 'config-hash' in fmt:print(c.get('container_hashes',{}).get(id,'a'*64))
 elif '.Config.Env' in fmt:
  print('DS60_PUBLIC_PORT='+str(c.get('lab_port',c.get('existing_port','8765'))))
 elif '.HostConfig.NetworkMode' in fmt:
  print(c.get('lab_network','container:'+containers.get('postgres','f'*64)))
 elif '.State.Status' in fmt:
  service=next((s for s,value in containers.items() if value==id),'unknown')
  states=c.get('health_states',{}).get(service,['running healthy'])
  print(states[0])
  if len(states)>1:states.pop(0);save()
 else:
  print(c.get('existing_db_port','55432')
       if '5432/tcp' in fmt else c.get('existing_port','8765'))
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
elif 'config' in a and '--images' in a:print(images[a[-1]])
elif 'config' in a and '--hash' in a:
 value=c.get('config_hashes',{}).get(a[-1],'a'*64)
 if a[-1]=='lab' and 'stdin' in row:
  assert row['stdin'].startswith('services:\n  lab:\n    network_mode: container:'),row
  value=c.get('resolved_network_hash',value)
 print(a[-1]+' '+value)
elif 'config' in a and '--quiet' not in a:
 service=a[-1];print('services:\n  '+service+':\n    image: '+images[service])
 if service=='lab':print('    network_mode: '+c.get('desired_network','service:postgres'))
elif 'ps' in a and '--quiet' in a:
 if a[-1] in containers:print(containers[a[-1]])
elif 'ps' in a and '--services' in a:
 print('\n'.join(containers))
elif 'port' in a:
 if c.get('fail')=='port':sys.exit(7)
 assert a[-1]==c.get('internal_port','8765'),a
 port=os.getenv('DS60_CLASSROOM_PORT')
 print(c.get('address','127.0.0.1:'+str(port if port!='0' else '49152')))
elif 'build' in a:
 service=built_service()
 if c.get('signal'):
  os.kill(os.getppid(),signal.SIGTERM);time.sleep(.1)
 if c.get('fail')=='build' or c.get('fail_build')==service:sys.exit(7)
 c.setdefault('built_images',[]).append(images[service]);save()
elif 'pull' in a:
 if c.get('fail')=='pull':sys.exit(7)
 c.setdefault('built_images',[]).append(images[a[-1]]);save()
elif 'up' in a or 'start' in a:
 if c.get('fail')=='up' or c.get('fail')==a[-1]:sys.exit(7)
 if 'up' in a:
  service=a[-1]
  if '--force-recreate' in a:containers.pop(service,None)
  containers.setdefault(service,'owned-'+service+'-'+str(len(containers)))
  if service=='lab':c['lab_port']=os.getenv('DS60_PUBLIC_PORT','49152')
  save()
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

        def publish(self, *args: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [str(bash), str(root / "scripts/publish-images"), *args],
                cwd=root,
                env=self.env,
                text=True,
                capture_output=True,
                timeout=20,
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


def built_services(calls: list[dict[str, Any]]) -> list[str]:
    result = []
    for call in calls:
        args = call["args"]
        if "build" not in args:
            continue
        if args[0] == "build":
            assert "--pull=false" in args
            result.append("python-core-worker")
        else:
            result.append(args[-1])
    return result


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
        "c-worker",
        "go-worker",
        "csharp-worker",
        "rust-worker",
        "swift-worker",
        "php-worker",
    ]
    assert built_services(calls) == ["lab", *expected]
    assert commands.index(next(a for a in commands if "pull" in a)) < commands.index(builds[0])
    starts = [a for a in commands if "up" in a]
    assert [a[-1] for a in starts] == ["postgres", "lab", *expected]
    assert commands.index(builds[-1]) < commands.index(starts[0])
    assert all("--wait" in a and "--no-build" in a and "--pull" in a for a in starts)
    assert all("--no-deps" in a for a in starts[2:])
    assert all("--no-recreate" in a for a in starts[:2])
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
    result = launcher.run("--profile", "java21", "--profile", "java21", "--no-browser", "--rebuild")
    assert result.returncode == 0, result.stderr
    assert built_services(launcher.calls()) == ["lab", "python-core-worker", "java-worker"]


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
    launcher.set(signal=True, missing_images=True)
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
    result = launcher.run("--starter", "--no-browser", "--rebuild")
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
        [
            bash,
            str(launcher.directory / "scripts/classroom.sh"),
            "--starter",
            "--no-browser",
            "--rebuild",
        ],
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
    launcher.set(fail_build=failed_service, missing_images=True)
    result = launcher.run("--profile", "cpp20", "--profile", "java21")
    assert result.returncode != 0
    commands = [call["args"] for call in launcher.calls()]
    builds = built_services(launcher.calls())
    order = ["lab", "python-core-worker", "cpp-worker", "java-worker"]
    assert builds == order[: order.index(failed_service) + 1]
    assert not any("up" in command or "exec" in command for command in commands)
    assert not launcher.opened()
    state = launcher.directory / ".classroom/ds60-classroom"
    assert not (state / "launcher.lock").exists()
    assert (state / "ports.env").is_file()


def test_plain_repeat_resumes_exact_containers_without_build_or_pull(launcher: Any) -> None:
    assert launcher.run("--starter", "--no-browser").returncode == 0
    state = json.loads(launcher.config.read_text())
    original = state["containers"].copy()
    offset = len(launcher.calls())
    result = launcher.run("--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    calls = launcher.calls()[offset:]
    assert not any(any(x in c["args"] for x in ("build", "pull", "up")) for c in calls)
    assert [c["args"][-1] for c in calls if "start" in c["args"]] == [
        "postgres",
        "lab",
        "python-core-worker",
    ]
    assert json.loads(launcher.config.read_text())["containers"] == original


def test_partial_build_remembers_selection_and_skips_completed_images(launcher: Any) -> None:
    launcher.set(missing_images=True, fail_build="java-worker")
    failed = launcher.run(
        "--profile", "java21", "--port", "9876", "--database-port", "55435", "--no-browser"
    )
    assert failed.returncode != 0
    selection = launcher.directory / ".classroom/ds60-classroom/selection.env"
    assert "DS60_PROFILES=python-core,java21" in selection.read_text()
    state = json.loads(launcher.config.read_text())
    state.pop("fail_build")
    launcher.config.write_text(json.dumps(state))
    offset = len(launcher.calls())
    result = launcher.run("--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    assert built_services(launcher.calls()[offset:]) == ["java-worker"]
    assert "http://127.0.0.1:9876/classroom" in result.stdout
    assert all(c["db_port"] == "55435" for c in launcher.calls()[offset:] if "up" in c["args"])


def test_existing_containers_do_not_require_image_tags(launcher: Any) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        missing_images=True,
    )
    result = launcher.run("resume", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    assert not any(
        "image" in c["args"] or "build" in c["args"] or "up" in c["args"] for c in launcher.calls()
    )


def test_legacy_profiles_are_inferred_without_expanding_starter(launcher: Any) -> None:
    launcher.set(containers={s: "old-" + s for s in ("postgres", "lab", "java-worker")})
    result = launcher.run("--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    selection = launcher.directory / ".classroom/ds60-classroom/selection.env"
    assert "DS60_PROFILES=python-core,java21" in selection.read_text()
    assert built_services(launcher.calls()) == []


@pytest.mark.parametrize("action", ["resume", "--no-build"])
def test_strict_resume_preflights_missing_images_without_start(launcher: Any, action: str) -> None:
    launcher.set(missing_images=True)
    result = launcher.run(action, "--starter", "--no-browser")
    assert result.returncode != 0 and "never builds or pulls" in result.stderr
    assert not any(
        any(x in c["args"] for x in ("build", "pull", "up", "start")) for c in launcher.calls()
    )


@pytest.mark.parametrize(
    "args", [["resume", "--rebuild"], ["build", "--no-build"], ["--no-build", "--rebuild"]]
)
def test_conflicting_preparation_flags_fail_before_engine(launcher: Any, args: list[str]) -> None:
    assert launcher.run(*args).returncode != 0
    assert not launcher.calls()


@pytest.mark.parametrize(
    "contents",
    [
        "DS60_PROFILES=python-core\nDS60_REGISTRY=$(touch injected)\n",
        "DS60_PROFILES=python-core,unknown\nDS60_REGISTRY=mirrors\n",
        "DS60_PROFILES=python-core\nDS60_PROFILES=java21\nDS60_REGISTRY=mirrors\n",
        "DS60_PROFILES=python-core\n",
        "DS60_PROFILES=python-core\nDS60_REGISTRY=mirrors\nEVIL=yes\n",
    ],
)
def test_invalid_selection_is_preserved_without_preparation(launcher: Any, contents: str) -> None:
    path = launcher.directory / ".classroom/ds60-classroom/selection.env"
    path.parent.mkdir(parents=True)
    path.write_text(contents)
    result = launcher.run("--starter")
    assert result.returncode != 0
    assert path.read_text() == contents
    assert not (launcher.directory / "injected").exists()
    assert not any(
        any(x in c["args"] for x in ("build", "pull", "start", "up")) for c in launcher.calls()
    )


def test_symlinked_selection_is_not_followed(launcher: Any, tmp_path: Path) -> None:
    target = tmp_path / "untouched"
    target.write_text("keep")
    path = launcher.directory / ".classroom/ds60-classroom/selection.env"
    path.parent.mkdir(parents=True)
    path.symlink_to(target)
    assert launcher.run().returncode != 0
    assert target.read_text() == "keep"


def test_changed_configuration_requires_deliberate_rebuild(launcher: Any) -> None:
    launcher.set(containers={"postgres": "old-postgres"}, config_hashes={"postgres": "b" * 64})
    result = launcher.run("--starter", "--port", "9999", "--no-browser")
    assert result.returncode != 0 and "configuration changed" in result.stderr
    assert not any("start" in c["args"] or "up" in c["args"] for c in launcher.calls())
    result = launcher.run("--starter", "--rebuild", "--port", "9999", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr


def test_replaced_database_repairs_only_app_network_namespace(launcher: Any) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        lab_network="container:" + "f" * 64,
    )
    result = launcher.run("resume", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    replacements = [c["args"] for c in launcher.calls() if "--force-recreate" in c["args"]]
    assert len(replacements) == 1 and replacements[0][-1] == "lab"
    assert "--no-build" in replacements[0] and "--no-deps" in replacements[0]
    assert not built_services(launcher.calls())


def test_missing_only_core_build_uses_local_lab_without_compose_rebuilding_it(
    launcher: Any,
) -> None:
    launcher.set(missing_images=["ds60sqlpy-worker-python-core:0.4.0"])
    result = launcher.run("--starter", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    assert built_services(launcher.calls()) == ["python-core-worker"]
    build = next(c["args"] for c in launcher.calls() if "build" in c["args"])
    assert build[0] == "build" and "DS60_CORE_IMAGE=ds60sqlpy-lab:0.4.0" in build


def test_explicit_all_replaces_saved_starter_selection(launcher: Any) -> None:
    assert launcher.run("--starter", "--no-browser").returncode == 0
    result = launcher.run("--all", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    selection = (launcher.directory / ".classroom/ds60-classroom/selection.env").read_text()
    assert "swift-linux" in selection and "rust-stable" in selection


def test_saved_registry_is_reused_but_readonly_commands_do_not_modify_selection(
    launcher: Any,
) -> None:
    assert launcher.run("--starter", "--registry", "upstream", "--no-browser").returncode == 0
    path = launcher.directory / ".classroom/ds60-classroom/selection.env"
    original = path.read_bytes()
    offset = len(launcher.calls())
    assert launcher.run("doctor").returncode == 0
    assert path.read_bytes() == original
    commands = [c["args"] for c in launcher.calls()[offset:]]
    assert not any("build" in c or "up" in c or "start" in c for c in commands)
    # Initial project discovery uses the default registry; restored settings are
    # then used for the final validated configuration and future preparations.
    assert "--env-file" not in next(c for c in reversed(commands) if "config" in c)


def test_strict_resume_missing_only_database_reports_before_start(launcher: Any) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("lab", "python-core-worker")},
        missing_images=["mirror.gcr.io/library/postgres:17"],
    )
    result = launcher.run("resume", "--no-browser")
    assert result.returncode != 0 and "database=1" in result.stderr
    assert not any("start" in c["args"] or "up" in c["args"] for c in launcher.calls())


def test_legacy_database_only_adopts_core_instead_of_every_sdk(launcher: Any) -> None:
    launcher.set(containers={"postgres": "old-postgres"})
    result = launcher.run("--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    selection = (launcher.directory / ".classroom/ds60-classroom/selection.env").read_text()
    assert "DS60_PROFILES=python-core\n" in selection


def test_rebuild_can_repair_old_app_without_public_port_setting(launcher: Any) -> None:
    launcher.set(containers={"postgres": "old-postgres", "lab": "old-lab"}, lab_port="")
    refused = launcher.run("--starter", "--no-browser")
    assert refused.returncode != 0 and "public port setting" in refused.stderr
    repaired = launcher.run("--starter", "--rebuild", "--no-browser")
    assert repaired.returncode == 0, repaired.stdout + repaired.stderr


def test_app_hash_normalizes_runtime_container_network_without_masking_config_changes(
    launcher: Any,
) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        config_hashes={"lab": "b" * 64},
        resolved_network_hash="a" * 64,
    )
    resumed = launcher.run("resume", "--no-browser")
    assert resumed.returncode == 0, resumed.stdout + resumed.stderr
    overrides = [c["stdin"] for c in launcher.calls() if "stdin" in c]
    expected = hashlib.sha256(b"old-postgres").hexdigest()
    assert overrides == [f"services:\n  lab:\n    network_mode: container:{expected}\n"]
    state = json.loads(launcher.config.read_text())
    state["resolved_network_hash"] = "c" * 64
    launcher.config.write_text(json.dumps(state))
    offset = len(launcher.calls())
    refused = launcher.run("resume", "--no-browser")
    assert refused.returncode != 0 and "configuration changed" in refused.stderr
    assert not any("start" in c["args"] or "up" in c["args"] for c in launcher.calls()[offset:])


def test_app_hash_normalization_does_not_hide_an_edited_network_mode(launcher: Any) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        desired_network="host",
    )
    refused = launcher.run("resume", "--no-browser")
    assert refused.returncode != 0 and "network mode changed" in refused.stderr
    assert not any("start" in c["args"] or "up" in c["args"] for c in launcher.calls())


def test_missing_app_tag_and_changed_dynamic_port_recover_existing_image_without_build(
    launcher: Any,
) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        missing_images=True,
        address="127.0.0.1:49153",
    )
    resumed = launcher.run("resume", "--no-browser")
    assert resumed.returncode == 0, resumed.stdout + resumed.stderr
    commands = [c["args"] for c in launcher.calls()]
    tags = [c for c in commands if c[:2] == ["image", "tag"]]
    assert tags == [["image", "tag", "sha256:" + "d" * 64, "ds60sqlpy-lab:0.4.0"]]
    assert not any("build" in c or "pull" in c for c in commands)
    replacements = [c for c in commands if "--force-recreate" in c]
    assert len(replacements) == 1 and replacements[0][-1] == "lab"
    assert "http://127.0.0.1:49153/classroom" in resumed.stdout


@pytest.mark.parametrize(
    "invalid",
    [
        {"lab_image_name": "unrelated-image:latest"},
        {"lab_image_id": "not-an-image-id"},
        {"missing_container_image": True},
    ],
)
def test_app_tag_recovery_refuses_unrelated_or_missing_image(
    launcher: Any, invalid: dict[str, Any]
) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        missing_images=True,
        address="127.0.0.1:49153",
        **invalid,
    )
    result = launcher.run("resume", "--no-browser")
    assert result.returncode != 0 and "could not be recovered" in result.stderr
    assert not any(c["args"][:2] == ["image", "tag"] for c in launcher.calls())
    assert not any("--force-recreate" in c["args"] for c in launcher.calls())


def test_present_app_tag_is_never_overwritten_during_network_repair(launcher: Any) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        address="127.0.0.1:49153",
    )
    result = launcher.run("resume", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    assert not any(c["args"][:2] == ["image", "tag"] for c in launcher.calls())


def test_missing_core_recovers_its_app_base_without_rebuilding_the_app(launcher: Any) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab")},
        missing_images=["ds60sqlpy-lab:0.4.0", "ds60sqlpy-worker-python-core:0.4.0"],
    )
    result = launcher.run("--starter", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    assert built_services(launcher.calls()) == ["python-core-worker"]
    assert len([c for c in launcher.calls() if c["args"][:2] == ["image", "tag"]]) == 1


def test_rebuild_prepares_missing_database_image_even_when_container_exists(launcher: Any) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        missing_images=["mirror.gcr.io/library/postgres:17"],
    )
    result = launcher.run("--starter", "--rebuild", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    pulls = [c["args"] for c in launcher.calls() if "pull" in c["args"]]
    assert len(pulls) == 1 and pulls[0][-1] == "postgres"


def test_changed_app_tag_does_not_silently_upgrade_during_port_repair(launcher: Any) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        address="127.0.0.1:49153",
        tag_image_id="sha256:" + "e" * 64,
    )
    result = launcher.run("resume", "--no-browser")
    assert result.returncode != 0 and "different image" in result.stderr
    assert not any(c["args"][:2] == ["image", "tag"] for c in launcher.calls())
    assert not any("--force-recreate" in c["args"] for c in launcher.calls())


def test_legacy_compose_start_waits_for_exact_container_health(launcher: Any) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        health_states={"postgres": ["running starting", "running healthy"]},
    )
    result = launcher.run("resume", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    commands = [c["args"] for c in launcher.calls()]
    starts = [c for c in commands if "start" in c]
    assert len(starts) == 3 and all("--wait" not in c and "--wait-timeout" not in c for c in starts)
    postgres_id = hashlib.sha256(b"old-postgres").hexdigest()
    probes = [c for c in commands if c[0] == "inspect" and ".State.Status" in c[2]]
    assert len([c for c in probes if c[-1] == postgres_id]) == 2
    assert commands.index(probes[1]) < commands.index(starts[1])


@pytest.mark.parametrize(
    "state", ["running unhealthy", "exited none", "dead none", "paused healthy"]
)
def test_unready_stopped_container_fails_before_starting_next_service(
    launcher: Any,
    state: str,
) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        health_states={"postgres": [state]},
    )
    result = launcher.run("resume", "--no-browser")
    assert result.returncode != 0 and "Saved volumes are retained" in result.stderr
    starts = [c["args"] for c in launcher.calls() if "start" in c["args"]]
    assert len(starts) == 1 and starts[0][-1] == "postgres"
    assert not launcher.opened()


def test_existing_container_readiness_has_a_bounded_deadline(launcher: Any) -> None:
    # Reduce only the disposable test copy's database deadline to one second.
    script = launcher.directory / "scripts/classroom.sh"
    source = script.read_text()
    assert "start_or_create postgres 180" in source
    script.write_text(source.replace("start_or_create postgres 180", "start_or_create postgres 1"))
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        health_states={"postgres": ["running starting"]},
    )
    result = launcher.run("resume", "--no-browser")
    assert result.returncode != 0 and "Timed out after 1s" in result.stderr
    starts = [c["args"] for c in launcher.calls() if "start" in c["args"]]
    assert len(starts) == 1 and starts[0][-1] == "postgres"
    assert not launcher.opened()


def test_running_container_without_healthcheck_is_ready(launcher: Any) -> None:
    launcher.set(
        containers={s: "old-" + s for s in ("postgres", "lab", "python-core-worker")},
        health_states={"python-core-worker": ["running none"]},
    )
    result = launcher.run("resume", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr


def _image_state(launcher: Any, source: str, namespace: str, tag: str) -> Path:
    state = Path(launcher.directory) / ".classroom/ds60-classroom/images.env"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(
        f"DS60_IMAGE_SOURCE={source}\nDS60_IMAGE_NAMESPACE={namespace}\nDS60_IMAGE_TAG={tag}\n"
    )
    return state


@pytest.mark.parametrize(
    "architecture,suffix",
    [("amd64", "amd64"), ("x86_64", "amd64"), ("arm64", "arm64"), ("aarch64", "arm64")],
)
def test_hub_missing_images_pull_matching_architecture_without_any_build(
    launcher: Any, architecture: str, suffix: str
) -> None:
    launcher.set(missing_images=True, architecture=architecture)
    result = launcher.run(
        "--starter", "--from-hub", "exampleuser", "--tag", "0.4.0", "--no-browser"
    )
    assert result.returncode == 0, result.stdout + result.stderr
    calls = launcher.calls()
    assert not built_services(calls)
    pulls = [call for call in calls if "pull" in call["args"] and "up" not in call["args"]]
    assert [call["args"][-1] for call in pulls] == ["postgres", "lab", "python-core-worker"]
    assert pulls[-1]["image_env"]["DS60_LAB_IMAGE"] == f"exampleuser/ds60sqlpy:0.4.0-lab-{suffix}"
    assert (
        pulls[-1]["image_env"]["DS60_WORKER_PYTHON_CORE_IMAGE"]
        == f"exampleuser/ds60sqlpy:0.4.0-worker-python-core-{suffix}"
    )
    assert all("--policy" in call["args"] for call in pulls[1:])
    state = launcher.directory / ".classroom/ds60-classroom/images.env"
    assert (
        state.read_text()
        == "DS60_IMAGE_SOURCE=hub\nDS60_IMAGE_NAMESPACE=exampleuser\nDS60_IMAGE_TAG=0.4.0\n"
    )


def test_saved_hub_resume_preserves_exact_containers_without_pull_or_build(launcher: Any) -> None:
    launcher.set(missing_images=True)
    assert (
        launcher.run(
            "--starter", "--from-hub", "exampleuser", "--tag", "0.4.0", "--no-browser"
        ).returncode
        == 0
    )
    containers = json.loads(launcher.config.read_text())["containers"].copy()
    before = len(launcher.calls())
    result = launcher.run("resume", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    new_calls = launcher.calls()[before:]
    assert not any(
        any(action in call["args"] for action in ("build", "pull", "up")) for call in new_calls
    )
    assert json.loads(launcher.config.read_text())["containers"] == containers
    assert "Images: hub (release 0.4.0)" in result.stdout


def test_hub_strict_resume_with_missing_images_never_downloads(launcher: Any) -> None:
    launcher.set(missing_images=True)
    result = launcher.run("resume", "--starter", "--from-hub", "exampleuser", "--no-browser")
    assert result.returncode != 0 and "Resume never builds or pulls" in result.stderr
    assert not any(
        any(action in call["args"] for action in ("build", "pull", "up"))
        for call in launcher.calls()
    )


def test_hub_pull_action_prepares_images_without_starting_services(launcher: Any) -> None:
    launcher.set(missing_images=True)
    result = launcher.run("pull", "--starter", "--from-hub", "exampleuser")
    assert result.returncode == 0, result.stdout + result.stderr
    assert any("pull" in call["args"] for call in launcher.calls())
    assert not any(
        any(action in call["args"] for action in ("build", "up", "start", "exec"))
        for call in launcher.calls()
    )
    assert not launcher.opened()


def test_failed_hub_pull_preserves_project_preferences_and_never_deletes_volumes(
    launcher: Any,
) -> None:
    state = launcher.directory / ".classroom/ds60-classroom"
    state.mkdir(parents=True)
    retained = state / "learner-note.txt"
    retained.write_text("keep my work")
    launcher.set(missing_images=True, fail="pull")
    result = launcher.run(
        "--starter", "--from-hub", "exampleuser", "--tag", "0.4.0", "--no-browser"
    )
    assert result.returncode != 0
    assert retained.read_text() == "keep my work"
    assert "DS60_IMAGE_SOURCE=hub" in (state / "images.env").read_text()
    assert not (state / "launcher.lock").exists()
    assert not any(
        any(action in call["args"] for action in ("down", "prune", "--volumes", "build", "up"))
        for call in launcher.calls()
    )


@pytest.mark.parametrize(
    "args",
    [
        ("--from-hub", "https://hub.docker.com/example"),
        ("--from-hub", "example/user"),
        ("--from-hub", "example:secret"),
        ("--from-hub", "ExampleUser"),
        ("--tag", "latest"),
        ("--tag", "0.4.0;touch injected"),
        ("--tag", "$(touch injected)"),
    ],
)
def test_invalid_registry_selection_cannot_prepare_or_start_images(
    launcher: Any, args: tuple[str, str]
) -> None:
    result = launcher.run("--starter", *args, "--no-browser")
    assert result.returncode != 0
    assert not (launcher.directory / "injected").exists()
    assert not any(
        any(action in call["args"] for action in ("build", "pull", "up", "start"))
        for call in launcher.calls()
    )


def test_saved_image_settings_are_data_and_reject_unknown_keys(launcher: Any) -> None:
    state = _image_state(launcher, "hub", "exampleuser", "0.4.0")
    state.write_text(state.read_text() + "EVIL=$(touch injected)\n")
    result = launcher.run("--starter", "--no-browser")
    assert result.returncode != 0 and "Unexpected saved image setting" in result.stderr
    assert not (launcher.directory / "injected").exists()
    assert not any("pull" in call["args"] or "build" in call["args"] for call in launcher.calls())


@pytest.mark.parametrize("action", [("--rebuild",), ("build",), ("--local-build", "--rebuild")])
def test_explicit_local_update_uses_checkout_release_not_saved_older_tag(
    launcher: Any, action: tuple[str, ...]
) -> None:
    state = _image_state(launcher, "local", "", "0.3.0")
    result = launcher.run(*action, "--starter", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "DS60_IMAGE_TAG=0.4.0" in state.read_text()
    builds = [call for call in launcher.calls() if "build" in call["args"]]
    assert builds
    assert all(call["image_env"]["DS60_LAB_IMAGE"] == "ds60sqlpy-lab:0.4.0" for call in builds)


def test_hub_rebuild_retains_selected_release_until_tag_explicitly_changes(launcher: Any) -> None:
    state = _image_state(launcher, "hub", "exampleuser", "0.3.0")
    result = launcher.run("--starter", "--rebuild", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "DS60_IMAGE_TAG=0.3.0" in state.read_text()
    assert not built_services(launcher.calls())
    assert any(
        call["image_env"].get("DS60_LAB_IMAGE") == "exampleuser/ds60sqlpy:0.3.0-lab-amd64"
        for call in launcher.calls()
    )


def test_explicit_tag_wins_over_saved_release_for_local_rebuild(launcher: Any) -> None:
    state = _image_state(launcher, "local", "", "0.3.0")
    result = launcher.run("--starter", "--rebuild", "--tag", "0.4.1-test", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "DS60_IMAGE_TAG=0.4.1-test" in state.read_text()


def test_all_ordinary_profiles_include_php_and_never_select_gpu(launcher: Any) -> None:
    result = launcher.run("--all", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    selection = (launcher.directory / ".classroom/ds60-classroom/selection.env").read_text()
    assert "php-cli" in selection
    assert "cuda" not in selection
    commands = [call["args"] for call in launcher.calls()]
    assert any(command[-1] == "php-worker" for command in commands if "up" in command)
    assert not any("cuda" in command[-1] for command in commands if "up" in command)


@pytest.mark.parametrize("profile", ["cuda-cpp", "cuda-python", "pytorch-cuda", "tensorflow-cuda"])
def test_gpu_execution_requires_explicit_device_selection(launcher: Any, profile: str) -> None:
    result = launcher.run("--profile", profile, "--no-browser")
    assert result.returncode != 0 and "explicitly chosen NVIDIA GPU" in result.stderr
    assert not any("build" in call["args"] or "up" in call["args"] for call in launcher.calls())


@pytest.mark.parametrize(
    "device", ["all", "0,1", "-1", "../../gpu", "0;touch injected", "$(touch injected)"]
)
def test_gpu_device_selection_rejects_broad_or_shell_values(launcher: Any, device: str) -> None:
    result = launcher.run("--profile", "cuda-python", "--gpu-device", device, "--no-browser")
    assert result.returncode != 0 and "Choose one NVIDIA device" in result.stderr
    assert not (launcher.directory / "injected").exists()
    assert not any("build" in call["args"] or "up" in call["args"] for call in launcher.calls())


def test_gpu_selection_is_saved_and_restored_for_strict_resume(launcher: Any) -> None:
    result = launcher.run("--profile", "cuda-python", "--gpu-device", "0", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    state = launcher.directory / ".classroom/ds60-classroom/gpu.env"
    assert state.read_text() == "DS60_GPU_DEVICE=0\n"
    before = len(launcher.calls())
    resumed = launcher.run("resume", "--no-browser")
    assert resumed.returncode == 0, resumed.stdout + resumed.stderr
    new_calls = launcher.calls()[before:]
    assert any(
        call["args"][-1] == "cuda-python-worker" for call in new_calls if "start" in call["args"]
    )
    assert all(call["gpu_device"] == "0" for call in new_calls if "start" in call["args"])
    assert not any("pull" in call["args"] or "build" in call["args"] for call in new_calls)


def test_gpu_workers_refuse_unsupported_engine_architecture_without_building(launcher: Any) -> None:
    launcher.set(architecture="arm64")
    result = launcher.run("--profile", "cuda-python", "--gpu-device", "0", "--no-browser")
    assert result.returncode != 0 and "Apple GPUs are not CUDA devices" in result.stderr
    assert not any("build" in call["args"] or "up" in call["args"] for call in launcher.calls())


def test_gpu_image_build_does_not_require_access_to_a_device(launcher: Any) -> None:
    result = launcher.run("build", "--profile", "cuda-python", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "cuda-python-worker" in built_services(launcher.calls())
    assert not any("up" in call["args"] or "start" in call["args"] for call in launcher.calls())


def test_publisher_preview_inspects_all_ordinary_images_without_registry_writes(
    launcher: Any,
) -> None:
    result = launcher.publish("--namespace", "exampleuser")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Preview only. 17 Linux amd64 images exist locally" in result.stdout
    commands = [call["args"] for call in launcher.calls()]
    assert len([command for command in commands if command[:2] == ["image", "inspect"]]) == 17
    assert not any(command[:2] in (["image", "tag"], ["image", "push"]) for command in commands)
    assert not any("cuda" in command[-1] for command in commands)


def test_publisher_checks_complete_set_before_first_tag_or_push(launcher: Any) -> None:
    launcher.set(missing_images=["ds60sqlpy-worker-php-cli:0.4.0"])
    result = launcher.publish("--namespace", "exampleuser", "--push")
    assert result.returncode != 0 and "Nothing has been pushed" in result.stderr
    assert not any(
        call["args"][:2] in (["image", "tag"], ["image", "push"]) for call in launcher.calls()
    )


def test_publisher_push_pins_inspected_image_ids_and_architecture_tags(launcher: Any) -> None:
    launcher.set(image_platform="linux arm64")
    result = launcher.publish("--namespace", "exampleuser", "--push")
    assert result.returncode == 0, result.stdout + result.stderr
    commands = [call["args"] for call in launcher.calls()]
    tags = [command for command in commands if command[:2] == ["image", "tag"]]
    pushes = [command for command in commands if command[:2] == ["image", "push"]]
    assert len(tags) == len(pushes) == 17
    assert all(command[2] == "sha256:" + "d" * 64 for command in tags)
    assert all(
        command[-1].startswith("exampleuser/ds60sqlpy:0.4.0-") and command[-1].endswith("-arm64")
        for command in tags
    )
    last_inspect = max(
        i for i, command in enumerate(commands) if command[:2] == ["image", "inspect"]
    )
    first_tag = min(i for i, command in enumerate(commands) if command[:2] == ["image", "tag"])
    assert last_inspect < first_tag


def test_publisher_refuses_mixed_architectures_before_writing_tags(launcher: Any) -> None:
    launcher.set(image_platforms={"ds60sqlpy-worker-php-cli:0.4.0": "linux arm64"})
    result = launcher.publish("--namespace", "exampleuser", "--push")
    assert result.returncode != 0 and "mixes architectures" in result.stderr
    assert not any(
        call["args"][:2] in (["image", "tag"], ["image", "push"]) for call in launcher.calls()
    )


@pytest.mark.parametrize(
    "args",
    [
        ("--version", "0.3.0"),
        ("--version", "latest"),
        ("--namespace", "https://example.com"),
        ("--profile", "cuda-python"),
        ("--profile", "unknown"),
    ],
)
def test_publisher_invalid_release_or_selection_never_writes_registry(
    launcher: Any, args: tuple[str, str]
) -> None:
    result = launcher.publish("--namespace", "exampleuser", *args, "--push")
    assert result.returncode != 0
    assert not any(
        call["args"][:2] in (["image", "tag"], ["image", "push"]) for call in launcher.calls()
    )


def test_publisher_can_preview_one_declared_image_for_manual_workflow(launcher: Any) -> None:
    result = launcher.publish("--namespace", "exampleuser", "--profile", "php-cli")
    assert result.returncode == 0, result.stdout + result.stderr
    commands = [call["args"] for call in launcher.calls()]
    assert len(commands) == 1 and commands[0][-1] == "ds60sqlpy-worker-php-cli:0.4.0"
    assert "Preview only. 1 Linux amd64 images" in result.stdout


def test_hub_missing_app_tag_and_changed_port_recover_local_image_without_download(
    launcher: Any,
) -> None:
    image = "exampleuser/ds60sqlpy:0.4.0-lab-amd64"
    _image_state(launcher, "hub", "exampleuser", "0.4.0")
    launcher.set(
        containers={
            service: "old-" + service for service in ("postgres", "lab", "python-core-worker")
        },
        missing_images=True,
        lab_image_name=image,
        address="127.0.0.1:49153",
    )
    result = launcher.run("resume", "--no-browser")
    assert result.returncode == 0, result.stdout + result.stderr
    commands = [call["args"] for call in launcher.calls()]
    tags = [command for command in commands if command[:2] == ["image", "tag"]]
    assert tags == [["image", "tag", "sha256:" + "d" * 64, image]]
    assert not any("build" in command or "pull" in command for command in commands)
    replacements = [command for command in commands if "--force-recreate" in command]
    assert len(replacements) == 1 and replacements[0][-1] == "lab"
