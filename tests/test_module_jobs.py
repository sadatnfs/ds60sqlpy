from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from ds60sqlpy.module_jobs import ModuleJobs, WorkerClient
from ds60sqlpy.modules import ModuleCatalog, ModuleState


@pytest.fixture
def authored(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ModuleCatalog:
    plan = {
        "id": "cpp",
        "title": "C++",
        "summary": "Ownership",
        "stages": [],
        "pilot": {"lesson_id": "cpp-009"},
        "lessons": [
            {
                "id": "cpp-009",
                "title": "Ownership",
                "level": "beginner",
                "minutes": 90,
                "prerequisites": [],
                "runtime": "cpp20",
                "outcome": "Explain copies",
                "lab": "Compare vectors",
                "verification": "Check independence",
                "concepts": ["ownership"],
            }
        ],
    }
    monkeypatch.setattr("ds60sqlpy.modules.load_designs", lambda root: [plan])
    monkeypatch.setattr(
        "ds60sqlpy.modules.Catalog.load", lambda root: SimpleNamespace(lessons=lambda: [])
    )
    base = tmp_path / "courses/cpp"
    base.mkdir(parents=True)
    for name, text in {
        "guide.md": "# Ownership\n",
        "lesson.cpp": "int main(){return 0;}\n",
        "solution.cpp": "int main(){return 0;}\n",
        "solutions.md": "# Reasoning\n",
    }.items():
        (base / name).write_text(text)
    manifest = {
        "schema_version": 1,
        "track_id": "cpp",
        "lessons": [
            {
                "id": "cpp-009",
                "status": "authored",
                "language": "cpp",
                "runtime_profile": "cpp20",
                "guide_path": "courses/cpp/guide.md",
                "source_path": "courses/cpp/lesson.cpp",
                "solution_paths": ["courses/cpp/solution.cpp", "courses/cpp/solutions.md"],
                "verification_id": None,
            }
        ],
    }
    (base / "lessons.json").write_text(json.dumps(manifest))
    return ModuleCatalog(tmp_path)


class FakeClient(WorkerClient):
    def __init__(self, *, hold: bool = False, ready: bool = True) -> None:
        self.hold = hold
        self.ready = ready
        self.submitted = 0
        self.cancelled = False
        self.unreachable = False
        self.jobs: dict[str, dict[str, Any]] = {}
        self.changed = threading.Event()

    def readiness(self, profile: str) -> dict[str, Any]:
        return {"profile": profile, "ready": self.ready, "detail": "fixture probe"}

    def call(
        self, profile: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if self.unreachable:
            raise ValueError("fixture connection lost")
        if path == "/jobs":
            assert payload is not None
            self.submitted += 1
            self.jobs[payload["job_id"]] = {
                "job_id": payload["job_id"],
                "profile": profile,
                "status": "running",
                "output": "",
                "returncode": None,
                "checks": [],
                "truncated": False,
                "elapsed_seconds": 0,
                "detail": "fixture",
            }
            return dict(self.jobs[payload["job_id"]])
        key = path.split("/")[2]
        job = self.jobs[key]
        if path.endswith("/cancel"):
            self.cancelled = True
            job.update(status="cancelled", returncode=-15, detail="Descendants reaped in fixture")
        elif not self.hold and job["status"] == "running":
            job.update(status="succeeded", returncode=0, output="42\n", elapsed_seconds=0.1)
        self.changed.set()
        return dict(job)


def wait_status(jobs: ModuleJobs, key: str, expected: str) -> dict[str, Any]:
    until = time.monotonic() + 5
    while time.monotonic() < until:
        value = jobs.get(key)
        if value["status"] == expected:
            return value
        time.sleep(0.02)
    raise AssertionError(jobs.get(key))


def test_manifest_reading_is_nonmutating_and_planned_content_is_separate(
    authored: ModuleCatalog,
) -> None:
    before = set(authored.root.rglob("*"))
    assert authored.index()["authored_count"] == 1
    assert authored.index()["tracks"][0]["lessons"][0]["status"] == "authored"
    with pytest.raises(ValueError, match="authored"):
        authored.get("cpp-042")
    assert set(authored.root.rglob("*")) == before


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_path", "../../outside.cpp"),
        ("runtime_profile", "arbitrary-shell"),
        ("verification_id", "shell-command"),
        ("language", "sql"),
        ("status", "published"),
    ],
)
def test_manifest_cannot_invent_paths_commands_or_published_status(
    authored: ModuleCatalog, field: str, value: str
) -> None:
    path = authored.root / "courses/cpp/lessons.json"
    manifest = json.loads(path.read_text())
    manifest["lessons"][0][field] = value
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        ModuleCatalog(authored.root)


def test_session_sidecar_preserves_empty_source_and_does_not_rewrite_legacy(
    authored: ModuleCatalog,
) -> None:
    legacy = authored.root / ".learning/progress.json"
    legacy.parent.mkdir()
    legacy.write_text('{"private":"keep"}')
    store = ModuleState(authored)
    assert store.read("cpp-009") == {}
    assert not store.path.exists()
    store.save("cpp-009", {"source": "", "prediction": "An independent copy"})
    assert store.read("cpp-009")["source"] == ""
    assert legacy.read_text() == '{"private":"keep"}'
    with pytest.raises(ValueError):
        store.save("cpp-009", {"complete": True})
    with pytest.raises(ValueError):
        store.save("cpp-009", {"explanation": "x" * 12001})


def test_job_persists_source_hash_result_and_idempotency_without_replaying(
    authored: ModuleCatalog,
) -> None:
    client = FakeClient()
    state = ModuleState(authored)
    jobs = ModuleJobs(authored, state, client)
    key = "a" * 32
    try:
        jobs.start("cpp-009", "int main() {}", 15, key)
        result = wait_status(jobs, key, "succeeded")
        assert result["output"] == "42\n" and result["returncode"] == 0
        assert len(result["source_sha256"]) == 64
        assert state.read("cpp-009")["source"] == "int main() {}"
        jobs.start("cpp-009", "int main() {}", 15, key)
        assert client.submitted == 1
        with pytest.raises(ValueError, match="different"):
            jobs.start("cpp-009", "int main(){return 1;}", 15, key)
    finally:
        jobs.close()
    recovered = ModuleJobs(authored, state, client)
    try:
        assert recovered.get(key)["status"] == "succeeded" and client.submitted == 1
    finally:
        recovered.close()


def test_busy_and_cancel_use_owned_job_identity(authored: ModuleCatalog) -> None:
    client = FakeClient(hold=True)
    jobs = ModuleJobs(authored, ModuleState(authored), client)
    try:
        jobs.start("cpp-009", "int main() {}", 15, "b" * 32)
        with pytest.raises(ValueError, match="active or unresolved"):
            jobs.start("cpp-009", "int main() {}", 15, "c" * 32)
        assert jobs.cancel("b" * 32)["status"] == "cancelled"
        assert client.cancelled
        with pytest.raises(ValueError):
            jobs.get("../../private")
    finally:
        jobs.close()


def test_unavailable_runtime_still_preserves_the_submitted_source(authored: ModuleCatalog) -> None:
    store = ModuleState(authored)
    jobs = ModuleJobs(authored, store, FakeClient(ready=False))
    try:
        with pytest.raises(ValueError, match="fixture probe"):
            jobs.start("cpp-009", "int main(){return 3;}", 15, "d" * 32)
        assert store.read("cpp-009")["source"] == "int main(){return 3;}"
        assert not jobs.directory.exists()
    finally:
        jobs.close()


def test_controller_rejects_false_success_or_mismatched_receipts(authored: ModuleCatalog) -> None:
    client = FakeClient(hold=True)
    jobs = ModuleJobs(authored, ModuleState(authored), client)
    key = "e" * 32
    try:
        jobs.start("cpp-009", "int main(){}", 15, key)
        value = dict(client.jobs[key], status="succeeded", returncode=1)
        with pytest.raises(ValueError, match="success"):
            jobs._snapshot(value, key)
        with pytest.raises(ValueError, match="identity"):
            jobs._snapshot(dict(value, job_id="f" * 32), key)
    finally:
        jobs.close()


@pytest.mark.parametrize(
    "url",
    [
        "https://cpp-worker:8081",
        "http://remote.example:8081",
        "http://" + "user:secret" + "@127.0.0.1:8081",
        "http://127.0.0.1:8081/arbitrary",
        "http://127.0.0.1:8081/?token=x",
    ],
)
def test_worker_configuration_rejects_remote_redirect_and_credential_targets(url: str) -> None:
    with pytest.raises(ValueError):
        WorkerClient({"DS60_MODULE_ENDPOINTS": json.dumps({"cpp20": url})})


def test_missing_worker_configuration_never_claims_ready() -> None:
    client = WorkerClient({})
    assert not client.readiness("cpp20")["ready"]
    assert client.readiness("reading")["ready"]


def test_curated_variants_have_separate_drafts_without_inflating_lesson_count(
    authored: ModuleCatalog,
) -> None:
    base = authored.root / "courses/cpp"
    (base / "alternate.py").write_text("print(42)\n")
    (base / "alternate_solution.py").write_text("print(42)\n")
    path = base / "lessons.json"
    payload = json.loads(path.read_text())
    payload["lessons"][0]["variants"] = [
        {
            "id": "python",
            "title": "Python comparison",
            "language": "python",
            "runtime_profile": "python-core",
            "source_path": "courses/cpp/alternate.py",
            "solution_paths": ["courses/cpp/alternate_solution.py", "courses/cpp/solutions.md"],
            "verification_id": None,
        }
    ]
    path.write_text(json.dumps(payload))
    catalog = ModuleCatalog(authored.root)
    assert catalog.index()["authored_count"] == 1
    assert catalog.index()["planned_count"] == 1
    assert catalog.get("cpp-009@python").runtime_profile == "python-core"
    state = ModuleState(catalog)
    state.save("cpp-009", {"source": "C++ attempt"})
    state.save("cpp-009@python", {"source": "Python attempt"})
    assert state.read("cpp-009")["source"] == "C++ attempt"
    assert state.read("cpp-009@python")["source"] == "Python attempt"


def test_state_rejects_nested_links_instead_of_overwriting_external_files(
    authored: ModuleCatalog, tmp_path: Path
) -> None:
    external = tmp_path / "external"
    external.mkdir()
    (authored.root / ".learning").mkdir()
    (authored.root / ".learning/modules").symlink_to(external, target_is_directory=True)
    state = ModuleState(authored)
    with pytest.raises(ValueError, match="symbolic link"):
        state.save("cpp-009", {"source": "keep inside"})
    assert list(external.iterdir()) == []


def test_every_source_read_revalidates_a_mutated_content_path(
    authored: ModuleCatalog, tmp_path: Path
) -> None:
    lesson = authored.get("cpp-009")
    outside = tmp_path / "outside-secret.cpp"
    outside.write_text("must not be returned")
    source = authored.root / lesson.source_path
    source.unlink()
    source.symlink_to(outside)
    with pytest.raises(ValueError, match="symbolic link"):
        authored.source(lesson)


def test_whitespace_worker_configuration_means_no_prepared_profiles() -> None:
    assert not WorkerClient({"DS60_MODULE_ENDPOINTS": "   "}).readiness("cpp20")["ready"]


def test_reconnecting_old_job_cannot_release_a_different_active_job(
    authored: ModuleCatalog,
) -> None:
    from ds60sqlpy.state_files import atomic_json_write, locked_update

    client = FakeClient(hold=True)
    jobs = ModuleJobs(authored, ModuleState(authored), client)
    first, older, third = "1" * 32, "2" * 32, "3" * 32
    try:
        jobs.start("cpp-009", "int main(){}", 60, first)
        old = {**jobs.get(first), "job_id": older, "status": "interrupted"}
        path = jobs._path(older)
        with locked_update(path):
            atomic_json_write(path, old)
        client.jobs[older] = {**client.jobs[first], "job_id": older}
        jobs.get(older)
        assert jobs.active == first
        assert jobs.pending == {first, older}
        client.jobs[older].update(status="succeeded", returncode=0)
        wait_status(jobs, older, "succeeded")
        assert jobs.active == first and jobs.pending == {first}
        with pytest.raises(ValueError, match="active or unresolved"):
            jobs.start("cpp-009", "int main(){}", 60, third)
    finally:
        jobs.close()


def test_confirmed_worker_replacement_resolves_unknown_result_without_replay(
    authored: ModuleCatalog,
) -> None:
    from ds60sqlpy.module_jobs import WorkerError

    class Restarted(FakeClient):
        def __init__(self) -> None:
            super().__init__(hold=True)
            self.instance = "a" * 32
            self.poll_entered = threading.Event()
            self.release_poll = threading.Event()

        def readiness(self, profile: str) -> dict[str, Any]:
            return {
                "profile": profile,
                "ready": True,
                "detail": "fixture",
                "instance_id": self.instance,
            }

        def call(
            self, profile: str, path: str, payload: dict[str, Any] | None = None
        ) -> dict[str, Any]:
            if path != "/jobs" and path.split("/")[2] not in self.jobs:
                raise WorkerError("job not present", 404)
            if path != "/jobs" and not path.endswith("/cancel"):
                self.poll_entered.set()
                assert self.release_poll.wait(5), "The controlled poll was never released."
            return super().call(profile, path, payload)

    client = Restarted()
    jobs = ModuleJobs(authored, ModuleState(authored), client)
    key = "4" * 32
    try:
        jobs.start("cpp-009", "int main(){}", 60, key)
        assert client.poll_entered.wait(5), "The monitor did not reach the controlled poll."
        assert jobs.get(key)["worker_instance_id"] == "a" * 32
        with jobs.lock:
            monitor = jobs.threads[key]
        # Establish a real unknown outcome before replacing the fake worker.
        # A healthy in-flight poll is otherwise allowed to recover interrupted
        # back to running and would race the replacement assertion below.
        client.unreachable = True
        client.release_poll.set()
        monitor.join(timeout=5)
        assert not monitor.is_alive()
        assert jobs._read(key)["status"] == "interrupted"
        assert jobs.pending == {key} and jobs.active == key
        assert client.submitted == 1
        client.jobs.clear()
        client.instance = "b" * 32
        client.unreachable = False
        result = jobs.get(key)
        assert (
            result["status"] == "failed"
            and result["recovery"]["type"] == "confirmed-new-worker-instance"
        )
        assert not jobs.pending and client.submitted == 1
        assert jobs.state.read("cpp-009")["source"] == "int main(){}"
        assert result["returncode"] is None and not result["checks"]
        stale = jobs._update(key, {"status": "running", "output": "late old-worker snapshot"})
        assert stale == result and not jobs.pending
        assert client.submitted == 1
    finally:
        client.release_poll.set()
        client.unreachable = False
        jobs.close()


def test_operator_recovery_is_explicit_and_does_not_create_verification(
    authored: ModuleCatalog,
) -> None:
    client = FakeClient(hold=True)
    jobs = ModuleJobs(authored, ModuleState(authored), client)
    key = "5" * 32
    try:
        jobs.start("cpp-009", "int main(){}", 60, key)
        client.unreachable = True
        # Let any earlier successful poll finish before asserting the unknown
        # outcome policy. The monitor must first observe this connection loss.
        with jobs.lock:
            monitor = jobs.threads.get(key)
        if monitor is not None:
            monitor.join(timeout=5)
            assert not monitor.is_alive()
        jobs._update(key, {"status": "interrupted"})
        with pytest.raises(ValueError, match="WORKER RESTARTED"):
            jobs.recover(key, "yes")
        result = jobs.recover(key, "WORKER RESTARTED")
        assert result["status"] == "failed" and not result["checks"]
        assert result["recovery"]["type"] == "operator-confirmed"
        assert not jobs.pending and client.submitted == 1
    finally:
        client.unreachable = False
        jobs.close()


def test_late_worker_snapshot_cannot_revive_a_resolved_attempt(authored: ModuleCatalog) -> None:
    client = FakeClient(hold=True)
    jobs = ModuleJobs(authored, ModuleState(authored), client)
    key = "6" * 32
    try:
        jobs.start("cpp-009", "int main(){}", 60, key)
        jobs.cancel(key)
        assert jobs.get(key)["status"] == "cancelled"
        result = jobs._update(key, {"status": "running", "output": "stale response"})
        assert result["status"] == "cancelled"
        assert result["output"] != "stale response"
        assert not jobs.pending
    finally:
        jobs.close()


def test_monitor_start_failure_preserves_accepted_job_and_reconnects(
    authored: ModuleCatalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = FakeClient(hold=True)
    state = ModuleState(authored)
    jobs = ModuleJobs(authored, state, client)
    key = "1" * 32

    def refuse_start(thread: threading.Thread) -> None:
        raise RuntimeError("injected local thread admission failure")

    try:
        with monkeypatch.context() as unavailable:
            unavailable.setattr(threading.Thread, "start", refuse_start)
            result = jobs.start("cpp-009", "int main(){return 7;}", 60, key)
            assert result["status"] == "interrupted"
            assert "monitoring could not start" in result["detail"]
            assert key in jobs.pending and key not in jobs.threads
            assert state.read("cpp-009")["source"] == "int main(){return 7;}"
            assert jobs.get(key)["status"] == "interrupted"
            with pytest.raises(ValueError, match="active or unresolved"):
                jobs.start("cpp-009", "int main(){return 8;}", 60, "2" * 32)
            assert client.submitted == 1
        assert jobs.get(key)["status"] == "running"
        assert jobs.threads[key].is_alive()
        client.hold = False
        completed = wait_status(jobs, key, "succeeded")
        assert completed["output"] == "42\n"
        assert not jobs.pending and client.submitted == 1
    finally:
        jobs.close()


def test_constructor_monitor_admission_failure_stays_recoverable_and_closes(
    authored: ModuleCatalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = FakeClient(hold=True)
    state = ModuleState(authored)
    first = ModuleJobs(authored, state, client)
    key = "3" * 32
    monkeypatch.setattr(first, "_monitor", lambda identity: None)
    first.start("cpp-009", "int main(){return 3;}", 60, key)
    first.closed.set()

    def refuse_start(thread: threading.Thread) -> None:
        raise RuntimeError("injected constructor recovery admission failure")

    with monkeypatch.context() as unavailable:
        unavailable.setattr(threading.Thread, "start", refuse_start)
        recovered = ModuleJobs(authored, state, client)
        assert recovered._read(key)["status"] == "interrupted"
        assert recovered.pending == {key} and not recovered.threads
        assert client.submitted == 1
        recovered.close()
    assert client.cancelled
    assert recovered._read(key)["status"] == "cancelled"
    assert state.read("cpp-009")["source"] == "int main(){return 3;}"


def test_monitor_creation_failure_does_not_replay_or_hide_worker_result(
    authored: ModuleCatalog, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = FakeClient(hold=True)
    jobs = ModuleJobs(authored, ModuleState(authored), client)
    key = "4" * 32

    def refuse_constructor(*args: Any, **kwargs: Any) -> threading.Thread:
        raise RuntimeError("injected thread constructor failure")

    try:
        with monkeypatch.context() as unavailable:
            unavailable.setattr(threading, "Thread", refuse_constructor)
            receipt = jobs.start("cpp-009", "int main(){return 4;}", 60, key)
            assert receipt["status"] == "interrupted"
            assert jobs.pending == {key} and not jobs.threads
            assert client.submitted == 1
        client.hold = False
        actual = jobs.get(key)
        assert actual["status"] == "succeeded" and actual["returncode"] == 0
        assert actual["output"] == "42\n"
        assert not jobs.pending and client.submitted == 1
    finally:
        jobs.close()


def test_close_does_not_join_an_unstarted_monitor(authored: ModuleCatalog) -> None:
    client = FakeClient()
    jobs = ModuleJobs(authored, ModuleState(authored), client)
    jobs.threads["5" * 32] = threading.Thread(target=lambda: None)
    jobs.close()
    assert jobs.closed.is_set() and client.submitted == 0


@pytest.mark.parametrize(
    "terminal", ["succeeded", "failed", "cancelled", "timed_out", "blocked", "interrupted"]
)
def test_get_reconciles_a_published_terminal_snapshot_before_returning(
    authored: ModuleCatalog, monkeypatch: pytest.MonkeyPatch, terminal: str
) -> None:
    from ds60sqlpy.state_files import atomic_json_write, locked_update

    client = FakeClient(hold=True)
    jobs = ModuleJobs(authored, ModuleState(authored), client)
    first, older = "1" * 32, "2" * 32
    # Control publication explicitly instead of relying on monitor scheduling.
    monkeypatch.setattr(jobs, "_monitor", lambda key: None)
    publish = threading.Event()
    published = threading.Event()
    errors: list[Exception] = []
    thread: threading.Thread | None = None
    try:
        jobs.start("cpp-009", "int main(){}", 60, first)
        old = {**jobs._read(first), "job_id": older}
        with locked_update(jobs._path(older)):
            atomic_json_write(jobs._path(older), old)
        client.jobs[older] = {**client.jobs[first], "job_id": older}
        jobs._reserve(older)
        original = jobs._read
        first_snapshot = True

        def read_before_publication(key: str) -> dict[str, Any]:
            nonlocal first_snapshot
            value = original(key)
            if key == older and first_snapshot:
                first_snapshot = False
                publish.set()
                assert published.wait(5), "The controlled publisher did not complete."
                assert not errors
            return value

        def publisher() -> None:
            try:
                assert publish.wait(5), "No initial stale snapshot was observed."
                jobs._update(
                    older, {"status": terminal, "returncode": 0 if terminal == "succeeded" else 1}
                )
            except Exception as error:
                errors.append(error)
            finally:
                published.set()

        monkeypatch.setattr(jobs, "_read", read_before_publication)
        thread = threading.Thread(target=publisher)
        thread.start()
        receipt = jobs.get(older)
        assert receipt["status"] == terminal
        expected = {first, older} if terminal == "interrupted" else {first}
        assert jobs.pending == expected and jobs.active == first
        assert client.submitted == 1
    finally:
        publish.set()
        if thread is not None:
            thread.join(timeout=5)
            assert not thread.is_alive()
        jobs.close()
