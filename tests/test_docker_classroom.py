"""Private Docker volume initialization and classroom topology contracts."""

from __future__ import annotations

import importlib.util
import json
import os
import stat
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest

ROOT = Path(__file__).resolve().parents[1]
INITIALIZER = ROOT / "docker/init_module_runtime.py"
POSIX_ONLY = pytest.mark.skipif(os.name == "nt", reason="Docker initializer uses Linux ownership.")


@pytest.fixture
def initializer() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ds60_classroom_initializer_test", INITIALIZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def identity() -> tuple[int, int]:
    # Root-based Linux test containers can exercise the real non-root owner too.
    return (1000, 1000) if os.geteuid() == 0 else (os.geteuid(), os.getegid())


def state(path: Path) -> tuple[bytes, int, int, int, int]:
    info = path.stat()
    return path.read_bytes(), info.st_ino, stat.S_IMODE(info.st_mode), info.st_uid, info.st_gid


def invoke(module: ModuleType, runtime: Path, learning: Path, identity: tuple[int, int]) -> bool:
    initialize = cast(Callable[[Path, Path, int, int], bool], module.initialize)
    return initialize(runtime, learning, *identity)


@POSIX_ONLY
def test_new_volumes_have_one_private_non_root_token(
    tmp_path: Path, initializer: ModuleType, identity: tuple[int, int]
) -> None:
    runtime, learning = tmp_path / "private", tmp_path / "learning"
    assert invoke(initializer, runtime, learning, identity) is True
    token = runtime / "token"
    value, _, mode, uid, gid = state(token)
    assert len(value) == 64 and all(byte in b"0123456789abcdef" for byte in value)
    assert (mode, uid, gid) == (0o400, *identity)
    for directory in (runtime, learning):
        info = directory.stat()
        assert stat.S_IMODE(info.st_mode) == 0o700
        assert (info.st_uid, info.st_gid) == identity
    assert ".learning" not in runtime.parts


@POSIX_ONLY
def test_resume_preserves_token_inode_and_every_existing_learner_child(
    tmp_path: Path, initializer: ModuleType, identity: tuple[int, int]
) -> None:
    runtime, learning = tmp_path / "private", tmp_path / "learning"
    invoke(initializer, runtime, learning, identity)
    notes = learning / "modules" / "notes.txt"
    notes.parent.mkdir()
    notes.write_bytes(b"My prediction and a deliberately empty source follow.\n")
    notes.chmod(0o640)
    empty = notes.with_name("source.cpp")
    empty.touch()
    external = tmp_path / "external-notes"
    external.write_text("Retain this exact owner, mode, inode and content.")
    (learning / "link-to-external").symlink_to(external)
    before = {path: state(path) for path in (runtime / "token", notes, empty, external)}
    assert invoke(initializer, runtime, learning, identity) is False
    assert {path: state(path) for path in before} == before
    assert (learning / "link-to-external").is_symlink()


@POSIX_ONLY
@pytest.mark.parametrize(
    "corruption", ["token-mode", "runtime-mode", "malformed", "token-hardlink", "extra"]
)
def test_existing_invalid_private_state_is_refused_without_rotation(
    tmp_path: Path, initializer: ModuleType, identity: tuple[int, int], corruption: str
) -> None:
    runtime, learning = tmp_path / "private", tmp_path / "learning"
    invoke(initializer, runtime, learning, identity)
    token = runtime / "token"
    if corruption == "token-mode":
        token.chmod(0o644)
    elif corruption == "runtime-mode":
        runtime.chmod(0o755)
    elif corruption == "malformed":
        token.chmod(0o600)
        token.write_bytes(b"a" * 63 + b"\n")
        token.chmod(0o400)
    elif corruption == "token-hardlink":
        os.link(token, tmp_path / "linked-token")
    else:
        (runtime / "unexpected").write_text("Preserve for operator review.")
    before = state(token)
    with pytest.raises(ValueError):
        invoke(initializer, runtime, learning, identity)
    assert state(token) == before
    if corruption == "extra":
        assert (runtime / "unexpected").read_text() == "Preserve for operator review."


@POSIX_ONLY
@pytest.mark.parametrize("corruption", ["mode", "symlink", "hardlink"])
def test_private_lock_tampering_does_not_change_the_stable_token(
    tmp_path: Path, initializer: ModuleType, identity: tuple[int, int], corruption: str
) -> None:
    runtime, learning = tmp_path / "private", tmp_path / "learning"
    invoke(initializer, runtime, learning, identity)
    token = state(runtime / "token")
    lock = runtime / ".init.lock"
    external = tmp_path / "external-lock"
    external.write_bytes(b"Preserve this external file.")
    if corruption == "mode":
        lock.chmod(0o644)
    elif corruption == "symlink":
        lock.unlink()
        lock.symlink_to(external)
    else:
        os.link(lock, external.with_name("linked-lock"))
    before = state(external)
    with pytest.raises((OSError, ValueError)):
        invoke(initializer, runtime, learning, identity)
    assert state(runtime / "token") == token
    assert state(external) == before


@POSIX_ONLY
def test_wrong_runtime_identity_is_refused_without_chown_or_rotation(
    tmp_path: Path, initializer: ModuleType, identity: tuple[int, int]
) -> None:
    runtime, learning = tmp_path / "private", tmp_path / "learning"
    invoke(initializer, runtime, learning, identity)
    before = state(runtime / "token")
    with pytest.raises(ValueError):
        invoke(initializer, runtime, learning, (identity[0] + 1, identity[1]))
    assert state(runtime / "token") == before
    assert (runtime.stat().st_uid, runtime.stat().st_gid) == identity


@POSIX_ONLY
@pytest.mark.parametrize("location", ["runtime", "token", "parent"])
def test_links_cannot_redirect_credential_initialization(
    tmp_path: Path, initializer: ModuleType, identity: tuple[int, int], location: str
) -> None:
    runtime, learning = tmp_path / "private", tmp_path / "learning"
    invoke(initializer, runtime, learning, identity)
    token = runtime / "token"
    original = state(token)
    if location == "runtime":
        alias = tmp_path / "alias"
        alias.symlink_to(runtime, target_is_directory=True)
        runtime = alias
    elif location == "parent":
        alias = tmp_path / "alias"
        alias.symlink_to(tmp_path, target_is_directory=True)
        runtime = alias / "private"
    else:
        replacement = tmp_path / "preserved-token"
        token.rename(replacement)
        token.symlink_to(replacement)
    with pytest.raises(ValueError):
        invoke(initializer, runtime, learning, identity)
    assert state(token) == original


@POSIX_ONLY
@pytest.mark.parametrize(
    "relation", ["same", "private-in-learning", "learning-in-private", "portable"]
)
def test_credentials_and_portable_learning_storage_must_be_separate(
    tmp_path: Path, initializer: ModuleType, identity: tuple[int, int], relation: str
) -> None:
    runtime, learning = tmp_path / "private", tmp_path / "learning"
    if relation == "same":
        learning = runtime
    elif relation == "private-in-learning":
        runtime = learning / "private"
    elif relation == "learning-in-private":
        learning = runtime / "learning"
    else:
        runtime = tmp_path / ".learning" / "private"
    with pytest.raises(ValueError):
        invoke(initializer, runtime, learning, identity)
    assert not (runtime / "token").exists()


@POSIX_ONLY
def test_populated_wrong_owner_learning_is_never_recursively_repaired(
    tmp_path: Path,
    initializer: ModuleType,
    identity: tuple[int, int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime, learning = tmp_path / "private", tmp_path / "learning"
    invoke(initializer, runtime, learning, identity)
    notes = learning / "notes.txt"
    notes.write_bytes(b"Existing learner evidence.")
    before = state(notes)
    actual_stat = Path.stat
    actual_chown = os.chown
    chowns: list[Path] = []

    def wrong_learning_owner(path: Path, *args: Any, **kwargs: Any) -> os.stat_result:
        info = actual_stat(path, *args, **kwargs)
        if path == learning:
            values = list(info)
            values[4] = identity[0] + 1
            return os.stat_result(values)
        return info

    def record_chown(path: Any, uid: int, gid: int, **kwargs: Any) -> None:
        chowns.append(Path(path))
        actual_chown(path, uid, gid, **kwargs)

    monkeypatch.setattr(Path, "stat", wrong_learning_owner)
    monkeypatch.setattr(os, "chown", record_chown)
    with pytest.raises(ValueError, match="Populated learner"):
        invoke(initializer, runtime, learning, identity)
    assert notes not in chowns and learning not in chowns
    assert state(notes) == before


@pytest.mark.parametrize(
    "value", ["0", "-1", "65533", "65534", "2147483648", "1.0", "True", "1;id"]
)
def test_dangerous_or_command_like_identities_are_rejected(
    initializer: ModuleType, value: str
) -> None:
    with pytest.raises(ValueError):
        initializer.identifier(value)


@pytest.mark.parametrize("uid,gid", [("1000", 1000), (1000.0, 1000), (True, 1000), (1000, "1000")])
def test_api_rejects_coercible_non_integer_identities_before_creating_storage(
    tmp_path: Path, initializer: ModuleType, uid: Any, gid: Any
) -> None:
    runtime, learning = tmp_path / "private", tmp_path / "learning"
    with pytest.raises(ValueError):
        initializer.initialize(runtime, learning, uid, gid)
    assert not runtime.exists() and not learning.exists()


@POSIX_ONLY
def test_concurrent_initializers_publish_exactly_once_and_resume_same_token(
    tmp_path: Path, identity: tuple[int, int]
) -> None:
    runtime, learning = tmp_path / "private", tmp_path / "learning"
    go = tmp_path / "go"
    code = """import json, runpy, sys, time
from pathlib import Path
initialize = runpy.run_path(sys.argv[1])['initialize']
Path(sys.argv[6]).touch()
limit = time.monotonic() + 10
while not Path(sys.argv[7]).exists():
    if time.monotonic() > limit: raise RuntimeError('No synchronized start signal')
    time.sleep(0.005)
created = initialize(Path(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
print(json.dumps({'created':created}))
"""
    processes: list[subprocess.Popen[str]] = []
    ready = [tmp_path / "ready-0", tmp_path / "ready-1"]
    try:
        for marker in ready:
            processes.append(
                subprocess.Popen(
                    [
                        sys.executable,
                        "-B",
                        "-c",
                        code,
                        str(INITIALIZER),
                        str(runtime),
                        str(learning),
                        str(identity[0]),
                        str(identity[1]),
                        str(marker),
                        str(go),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            )
        deadline = time.monotonic() + 10
        while not all(path.exists() for path in ready):
            assert time.monotonic() < deadline, (
                "Initializer children did not reach the start barrier"
            )
            time.sleep(0.01)
        go.touch()
        values = []
        for process in processes:
            output, errors = process.communicate(timeout=15)
            assert process.returncode == 0, errors
            values.append(json.loads(output)["created"])
        assert sorted(values) == [False, True]
        token = state(runtime / "token")
        module = runpy_initializer()
        assert invoke(module, runtime, learning, identity) is False
        assert state(runtime / "token") == token
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)


def runpy_initializer() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ds60_classroom_resume_test", INITIALIZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_direct_main_refuses_host_initialization_without_writing(
    initializer: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("Host invocation reached volume initialization")

    monkeypatch.delenv("DS60_CONTAINER", raising=False)
    monkeypatch.setattr(initializer, "initialize", forbidden)
    assert initializer.main() == 2
    assert "Docker classroom init service" in capsys.readouterr().err


def test_classroom_compose_has_named_only_state_and_private_workers() -> None:
    yaml = pytest.importorskip("yaml", reason="Compose structural checks use optional PyYAML.")

    ComposeLoader: Any = type("ComposeLoader", (yaml.SafeLoader,), {})

    ComposeLoader.add_constructor("!reset", lambda loader, node: loader.construct_sequence(node))
    config = yaml.load((ROOT / "compose.classroom.yaml").read_text(), Loader=ComposeLoader)
    services = config["services"]
    init = services["classroom-init"]
    lab = services["lab"]
    assert init["network_mode"] == "none" and init["read_only"] is True
    assert init["user"] == "0:0" and init["cap_drop"] == ["ALL"]
    assert set(init["cap_add"]) == {"CHOWN", "DAC_OVERRIDE", "FOWNER"}
    assert init["entrypoint"] == ["python", "/opt/course/docker/init_module_runtime.py"]
    assert "command" in init and init["command"] == []
    assert lab["extends"] == {"file": "compose.yaml", "service": "lab"}
    assert lab["profiles"] == []
    assert lab["depends_on"]["classroom-init"]["condition"] == "service_completed_successfully"
    assert lab["depends_on"]["postgres"]["condition"] == "service_healthy"
    assert lab["environment"]["DS60_ROOTLESS"] == "0"
    assert lab["environment"]["DS60_MODULE_TOKEN_FILE"] == "/run/ds60/worker-token/token"
    endpoints = json.loads(lab["environment"]["DS60_MODULE_ENDPOINTS"])
    expected = {
        "python-core": "python-core-worker",
        "cpp20": "cpp-worker",
        "tensorflow-cpu": "tensorflow-worker",
        "scala-jvm": "scala-worker",
        "spark-local-scala": "spark-scala-worker",
        "spark-local-python": "spark-python-worker",
    }
    assert endpoints == {profile: f"http://{service}:8081" for profile, service in expected.items()}
    assert config["networks"]["module-private"]["internal"] is True
    assert services["postgres"]["networks"] == ["default", "module-private"]
    for name in ["classroom-init", "lab", *expected.values()]:
        service = services[name]
        for volume in service["volumes"]:
            assert volume["type"] == "volume"
            assert volume["source"] in {"classroom-learning", "classroom-runtime"}
            assert volume["volume"]["nocopy"] is True
        if name in expected.values():
            assert service["extends"] == {"file": "compose.modules.yaml", "service": name}
            assert (
                service["depends_on"]["classroom-init"]["condition"]
                == "service_completed_successfully"
            )
            assert service["volumes"][0]["read_only"] is True
            assert (
                service["environment"]["DS60_WORKER_TOKEN_FILE"] == "/run/ds60/worker-token/token"
            )
            assert "ports" not in service and "networks" not in service
    base = yaml.safe_load((ROOT / "compose.yaml").read_text())
    assert all(port.startswith("127.0.0.1:") for port in base["services"]["postgres"]["ports"])
    worker = yaml.safe_load((ROOT / "compose.modules.yaml").read_text())["x-worker"]
    assert worker["networks"] == ["module-private"] and "ports" not in worker
    assert worker["read_only"] is True and "KILL" in worker["cap_add"]
    all_text = (ROOT / "compose.classroom.yaml").read_text()
    assert "docker.sock" not in all_text and "DS60_MODULE_RUNTIME_DIR" not in all_text
