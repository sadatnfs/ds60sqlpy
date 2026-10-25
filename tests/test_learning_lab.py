from __future__ import annotations

import json
import sys
import threading
from dataclasses import replace
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.coaching import CoachingService
from ds60sqlpy.container_runtime import prepare_workspace
from ds60sqlpy.execution import MAX_OUTPUT_BYTES, PadRunner
from ds60sqlpy.lab import LabServer
from ds60sqlpy.progress import ProgressStore
from ds60sqlpy.study_plan import build_study_plan


def local_catalog(tmp_path: Path) -> Catalog:
    root = Catalog.load()
    lesson = root.get("python-01")
    for relative in (lesson.guide_path, lesson.lesson_path, *lesson.solution_paths):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(root.resolve(relative).read_bytes())
    return Catalog(tmp_path, (replace(lesson, prerequisites=()),))


def test_python_pad_executes_and_preserves_learner_work(tmp_path: Path) -> None:
    catalog = local_catalog(tmp_path)
    runner = PadRunner(catalog)
    result = runner.run("python-01", "python", "print(sum([3, 7]))")
    assert result["returncode"] == 0
    assert result["output"].strip() == "10"
    assert runner.read("python-01", "python") == "print(sum([3, 7]))"
    assert (tmp_path / "python/ds-60day/notebooks/day01_setup_and_repl.ipynb").stat().st_size != 0
    failed = runner.run("python-01", "python", "raise ValueError('inspect this input')")
    assert failed["returncode"] != 0
    assert "ValueError: inspect this input" in failed["output"]
    assert runner.read("python-01", "python").startswith("raise")


def test_embedded_guide_headings_cannot_shadow_coding_pad_controls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    catalog = local_catalog(tmp_path)
    catalog.resolve(catalog.get("python-01").guide_path).write_text(
        "# Code\n\n## Solution\n", encoding="utf-8"
    )
    monkeypatch.setattr("ds60sqlpy.lab.rendered_targets", lambda catalog: {})
    server = LabServer(catalog, progress_path=tmp_path / "progress.json")
    try:
        result = server.action({"action": "lesson", "lesson_id": "python-01"})
        assert 'id="lab-guide--code"' in result["guide_html"]
        assert 'id="lab-guide--solution"' in result["guide_html"]
        assert 'id="code"' not in result["guide_html"]
    finally:
        server.server_close()


def test_python_pad_stops_hangs_and_bounds_output(tmp_path: Path) -> None:
    runner = PadRunner(local_catalog(tmp_path), timeout=0.4)
    result = runner.run("python-01", "python", "while True: pass")
    assert result["stopped"] == "time limit"
    assert result["elapsed_seconds"] < 4
    result = runner.run("python-01", "python", "print('x' * 1000000)")
    assert len(result["output"].encode()) <= MAX_OUTPUT_BYTES


def test_pad_rejects_unknown_lesson_and_outside_database(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = PadRunner(local_catalog(tmp_path))
    with pytest.raises(KeyError):
        runner.save("../../outside", "python", "print(1)")
    monkeypatch.setenv("DS60_DATABASE_URL", "postgresql://localhost/valuable")
    with pytest.raises(ValueError, match="disposable"):
        runner.run("python-01", "sql", "SELECT 1")


def test_coaching_requires_evidence_and_explicit_solution_reveal(tmp_path: Path) -> None:
    service = CoachingService(local_catalog(tmp_path))
    lesson = service.lesson("python-01")
    assert "guide" in lesson and "solutions" not in lesson
    assert not service.path.exists()
    with pytest.raises(ValueError, match="reveal"):
        service.solution("python-01")
    assert service.solution("python-01", reveal=True)["content"]
    with pytest.raises(ValueError, match="confirm"):
        service.complete("python-01")
    with pytest.raises(ValueError, match="predict"):
        service.complete("python-01", confirmed=True)
    for phase, note in (
        ("predict", "10"),
        ("attempt", "I ran the sum and got 10"),
        ("explain", "Addition combines each value; an empty list sums to zero"),
    ):
        service.save("python-01", phase, note)
    completion = service.complete("python-01", confirmed=True)
    assert "not automatically graded" in completion["evidence_type"]
    assert CoachingService(service.catalog).session("python-01")["attempt"].endswith("10")
    assert service.progress.completions()[0].lesson_id == "python-01"


def test_study_plan_topological_order_shared_prerequisites_and_saved_progress(
    tmp_path: Path,
) -> None:
    base = Catalog.load().get("python-01")
    lessons = (
        replace(base, id="a", day=1),
        replace(base, id="b", day=2, prerequisites=("a",)),
        replace(base, id="c", day=3, prerequisites=("a",)),
        replace(base, id="d", day=4, prerequisites=("b", "c")),
    )
    catalog = Catalog(tmp_path, lessons)
    plan = build_study_plan(catalog, ["d"], completed=["a"], weekly_hours=3)
    assert [lesson.id for lesson in plan.lessons] == ["b", "c", "d"]
    assert plan.ready == ("b", "c")
    assert plan.completed == ("a",)
    assert plan.estimated_weeks >= 1
    cyclic = Catalog(tmp_path, (replace(lessons[0], prerequisites=("b",)), lessons[1]))
    with pytest.raises(ValueError, match="cycle"):
        build_study_plan(cyclic, ["a"])
    for value in (0, -1, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            build_study_plan(catalog, ["d"], weekly_hours=value)


def test_workspace_install_reuses_existing_course_and_preserves_state(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "README.md").write_text("course", encoding="utf-8")
    (source / "curriculum").mkdir()
    (source / "curriculum/catalog.json").write_text("{}", encoding="utf-8")
    destination = tmp_path / "workspace"
    prepare_workspace(source, destination)
    (destination / "README.md").write_text("my notes", encoding="utf-8")
    prepare_workspace(source, destination)
    assert (destination / "README.md").read_text() == "my notes"
    unknown = tmp_path / "occupied"
    unknown.mkdir()
    (unknown / "private.txt").touch()
    with pytest.raises(ValueError, match="empty"):
        prepare_workspace(source, unknown)


def test_lab_requires_exact_origin_and_session_token_before_execution(tmp_path: Path) -> None:
    catalog = Catalog.load()
    server = LabServer(catalog, progress_path=tmp_path / "progress.json", python=sys.executable)
    # Point pad writes to a private temporary catalog, keeping official artifacts untouched.
    server.pads = PadRunner(local_catalog(tmp_path / "pads"))
    server.coaching = CoachingService(catalog, ProgressStore(catalog, tmp_path / "progress.json"))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(server.url + "learn", timeout=3) as response:
            html = response.read().decode()
        assert "/assets/classroom.js" in html and server.token in html
        payload = {
            "action": "run",
            "lesson_id": "python-01",
            "language": "python",
            "code": "print(6 * 7)",
        }
        request = Request(
            server.url + "api/lab",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with pytest.raises(HTTPError) as forbidden:
            urlopen(request, timeout=3)
        assert forbidden.value.code == 403
        request.add_header("X-DS60-Token", server.token)
        request.add_header("Origin", "https://example.invalid")
        with pytest.raises(HTTPError) as cross_origin:
            urlopen(request, timeout=3)
        assert cross_origin.value.code == 403
        request.add_header("Origin", server.url.rstrip("/"))
        with urlopen(request, timeout=3) as response:
            result = json.loads(response.read())
        assert result["output"].strip() == "42"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_workspace_does_not_copy_into_its_own_payload(tmp_path: Path) -> None:
    source = tmp_path / "course"
    (source / "python").mkdir(parents=True)
    destination = source / "python" / "nested-workspace"
    with pytest.raises(ValueError, match="copied content"):
        prepare_workspace(source, destination)
    assert not destination.exists()


def test_source_payload_excludes_local_state_and_build_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import course_payload

    source = tmp_path / "course"
    (source / "src/ds60sqlpy").mkdir(parents=True)
    (source / "src/ds60sqlpy/module.py").write_text("answer = 42\n", encoding="utf-8")
    (source / "src/ds60sqlpy.egg-info").mkdir()
    (source / "src/ds60sqlpy.egg-info/PKG-INFO").write_text("generated", encoding="utf-8")
    (source / ".learning").mkdir()
    (source / ".learning/progress.json").write_text("private learner state", encoding="utf-8")
    (source / ".env").write_text("private local configuration", encoding="utf-8")
    monkeypatch.setattr(course_payload, "ROOT", source)
    payload = tmp_path / "payload"
    course_payload.stage_course(payload)
    assert (payload / "src/ds60sqlpy/module.py").is_file()
    assert not (payload / "src/ds60sqlpy.egg-info").exists()
    assert not (payload / ".learning").exists()
    assert not (payload / ".env").exists()


def test_lab_shutdown_waits_for_active_backend_cleanup(tmp_path: Path) -> None:
    import time

    server = LabServer(Catalog.load(), progress_path=tmp_path / "progress.json")
    server.pads = PadRunner(local_catalog(tmp_path / "course"))
    serving = threading.Thread(target=server.serve_forever)
    serving.start()
    observed: list[dict[str, object]] = []
    errors: list[Exception] = []

    def submit() -> None:
        try:
            request = Request(
                server.url + "api/lab",
                data=json.dumps(
                    {
                        "action": "run",
                        "lesson_id": "python-01",
                        "language": "python",
                        "code": "import time; time.sleep(0.3); print('clean exit')",
                    }
                ).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Origin": server.url.rstrip("/"),
                    "X-DS60-Token": server.token,
                },
            )
            with urlopen(request, timeout=5) as response:
                observed.append(json.loads(response.read()))
        except Exception as exc:
            errors.append(exc)

    client = threading.Thread(target=submit)
    client.start()
    deadline = time.monotonic() + 3
    try:
        while not server.execution_lock.locked():
            assert time.monotonic() < deadline
            time.sleep(0.005)
        server.shutdown()
        server.server_close()
        client.join(timeout=3)
        serving.join(timeout=3)
        assert not errors
        output = observed[0]["output"]
        assert isinstance(output, str) and output.splitlines() == ["clean exit"]
        assert not server.execution_lock.locked()
    finally:
        server.shutdown()
        server.server_close()
        client.join(timeout=3)
        serving.join(timeout=3)


def test_workspace_initialization_preserves_prebound_learning_folder(tmp_path: Path) -> None:
    source = tmp_path / "bundle"
    source.mkdir()
    (source / "README.md").write_text("current course", encoding="utf-8")
    workspace = tmp_path / "workspace"
    learning = workspace / ".learning"
    learning.mkdir(parents=True)
    prior = b'{"schema_version":1,"completed":{}}\n'
    (learning / "progress.json").write_bytes(prior)
    (learning / "practice.py").write_text("my prior code", encoding="utf-8")
    prepare_workspace(source, workspace)
    assert (workspace / "README.md").read_text() == "current course"
    assert (learning / "progress.json").read_bytes() == prior
    assert (learning / "practice.py").read_text() == "my prior code"


def test_authenticated_capabilities_generic_saved_work_and_bounded_run_options(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    catalog = local_catalog(tmp_path / "course")
    base = catalog.get("python-01")
    (catalog.repo_root / "cpp").mkdir()
    (catalog.repo_root / "cpp/practice.cpp").write_text("int main() { return 0; }\n")
    (catalog.repo_root / "cpp/guide.md").write_text("# C++ practice\n")
    catalog = Catalog(
        catalog.repo_root,
        (
            base,
            replace(
                base,
                id="cpp-demo",
                day=2,
                runner="cpp",
                lesson_path="cpp/practice.cpp",
                guide_path="cpp/guide.md",
                solution_paths=(),
            ),
        ),
    )
    monkeypatch.setattr(
        "ds60sqlpy.capabilities.probe_python",
        lambda *args: {"available": True, "missing_modules": [], "python_version": "3.12"},
    )
    monkeypatch.setattr(
        "ds60sqlpy.capabilities.probe_sql", lambda *args: (False, "Local SQL offline")
    )
    monkeypatch.setattr("ds60sqlpy.lab.rendered_targets", lambda catalog: {})
    server = LabServer(catalog, progress_path=tmp_path / "progress.json", python=sys.executable)
    serving = threading.Thread(target=server.serve_forever, daemon=True)
    serving.start()

    def call(payload: dict[str, object]) -> dict[str, object]:
        request = Request(
            server.url + "api/lab",
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Origin": server.url.rstrip("/"),
                "X-DS60-Token": server.token,
            },
        )
        with urlopen(request, timeout=5) as response:
            result: dict[str, object] = json.loads(response.read())
            return result

    try:
        capabilities = call({"action": "capabilities", "lesson_id": "cpp-demo"})
        assert capabilities["default_runner"] == "cpp"
        assert not (catalog.repo_root / ".learning").exists()
        cpp = {"lesson_id": "cpp-demo", "language": "cpp"}
        call({"action": "save-pad", **cpp, "code": "int main() { return 0; }\n"})
        saved = call({"action": "read-pad", **cpp})
        assert saved["saved"] and str(saved["code"]).startswith("int main")
        with pytest.raises(HTTPError) as unsupported:
            call({"action": "run", **cpp, "code": "do not execute this"})
        assert unsupported.value.code == 400
        assert b"not implemented" in unsupported.value.read()
        assert call({"action": "read-pad", **cpp}) == saved
        for timeout in (True, 0, 121, 15.0, "15"):
            with pytest.raises(HTTPError) as invalid:
                call(
                    {
                        "action": "run",
                        "lesson_id": "python-01",
                        "language": "python",
                        "code": "print(42)",
                        "timeout_seconds": timeout,
                    }
                )
            assert invalid.value.code == 400
        result = call(
            {
                "action": "run",
                "lesson_id": "python-01",
                "language": "python",
                "code": "print(42)",
                "timeout_seconds": 120,
            }
        )
        assert result["returncode"] == 0 and str(result["output"]).strip() == "42"
    finally:
        server.shutdown()
        server.server_close()
        serving.join(timeout=3)
