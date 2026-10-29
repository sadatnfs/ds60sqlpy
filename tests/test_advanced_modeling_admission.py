"""Actual new-track admission, learner isolation and offline source delivery."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.classroom import ClassroomService
from ds60sqlpy.coaching import CoachingService
from ds60sqlpy.mcp_server import TutorAdapter
from ds60sqlpy.module_jobs import ModuleJobs, WorkerClient
from ds60sqlpy.module_service import ModuleService
from ds60sqlpy.modules import ModuleCatalog, ModuleState
from ds60sqlpy.progress import ProgressStore
from scripts.course_payload import ignore_private_files, stage_course

ROOT = Path(__file__).resolve().parents[1]
TRACKS = {
    "advanced-spark-modeling": ("asm", 38),
    "custom-likelihood-pytorch": ("clp", 20),
    "tmb-modeling": ("tmb", 48),
    "python-web": ("pyweb", 72),
}


@pytest.fixture(scope="module")
def modules() -> ModuleCatalog:
    return ModuleCatalog(ROOT)


@pytest.fixture(scope="module")
def legacy() -> Catalog:
    return Catalog.load(ROOT)


@pytest.mark.parametrize("subject", TRACKS)
def test_complete_tutorial_admission_and_cross_subject_prerequisites(
    modules: ModuleCatalog, legacy: Catalog, subject: str
) -> None:
    prefix, count = TRACKS[subject]
    expected = {f"{prefix}-{number:03}" for number in range(1, count + 1)}
    observed = {key for key in modules.canonical_ids if modules.planned[key]["track_id"] == subject}
    assert observed == expected
    available = modules.lessons.keys() | {lesson.id for lesson in legacy}
    for key in observed:
        lesson = modules.get(key)
        assert lesson.learning_mode == "tutorial"
        assert lesson.verification_id is None
        assert all(parent in available for parent in modules.planned[key]["prerequisites"])
        assert modules.content_path(lesson.guide_path).is_file()
        assert modules.content_path(lesson.source_path).is_file()
        assert modules.source(lesson).strip()
    plan = next(plan for plan in modules.plans if plan["id"] == subject)
    assert {row["level"] for row in plan["lessons"]} == {"beginner", "intermediate", "advanced"}


def test_unified_directory_retains_original_and_new_learning_paths(
    modules: ModuleCatalog, legacy: Catalog, tmp_path: Path
) -> None:
    def dispatch(payload: dict[str, Any]) -> dict[str, Any]:
        if payload["action"] == "module-index":
            return {**modules.index(), "active_job": None}
        if payload["action"] == "paths":
            return {"completed": ["python-01"], "paths": {}}
        raise AssertionError("Directory discovery requested an unrelated operation")

    service = ClassroomService(legacy, dispatch, {}, runs_directory=tmp_path / "runs")
    directory = service.index()
    subjects = {row["id"]: row for row in directory["tracks"]}
    assert subjects.keys() >= TRACKS.keys() | {"python", "sql", "scala-spark", "r"}
    assert subjects["python"]["lessons"][0]["completed"] is True
    for key, (_, count) in TRACKS.items():
        assert subjects[key]["theme_key"] == key
        assert subjects[key]["authored_count"] == subjects[key]["lesson_count"] == count
        assert all(row["learning_mode"] == "tutorial" for row in subjects[key]["lessons"])
    assert not (tmp_path / "runs").exists()


def test_project_chapters_cannot_start_an_ordinary_worker_job(
    modules: ModuleCatalog, tmp_path: Path
) -> None:
    state = ModuleState(modules, tmp_path / "modules")
    jobs = ModuleJobs(modules, state, client=WorkerClient(environment={}))
    project_ids = ["asm-018", "asm-021", "asm-022", "asm-023", "asm-026", "asm-031", "asm-038"]
    project_ids += ["pyweb-068", "pyweb-070", "pyweb-072"]
    for key in project_ids:
        assert modules.get(key).runtime_profile == "reading"
        with pytest.raises(ValueError, match="reading lesson"):
            jobs.start(key, "This is a project reference, not a worker program", 60, "probe")
    assert jobs.active is None and not jobs.pending
    assert not jobs.directory.exists()
    assert modules.get("asm-001").runtime_profile == "spark-local-python"
    assert modules.get("asm-013").runtime_profile == "spark-local-scala"
    assert modules.get("clp-001").runtime_profile == "llm-torch-cpu"
    assert modules.get("pyweb-001").runtime_profile == "python-web"
    assert all(modules.get(f"tmb-{i:03}").runtime_profile == "r-statistics" for i in range(1, 49))


def test_new_subject_drafts_and_notes_survive_reopen_without_overwriting_existing_work(
    modules: ModuleCatalog, tmp_path: Path
) -> None:
    directory = tmp_path / "modules"
    state = ModuleState(modules, directory)
    old = {"source": "int main() { return 0; }", "explanation": "Existing C++ notes"}
    state.save("cpp-009", old)
    attempts = {
        "asm-001": {"source": "print('Spark draft')", "prediction": "Twelve rows"},
        "asm-021": {"source": "My Catalyst project notes", "review": "Check exact Spark ABI"},
        "clp-001": {"source": "print('likelihood draft')", "explanation": "One observation"},
        "tmb-048": {"source": "print('R companion draft')", "review": "Native C++ is separate"},
        "pyweb-013": {"source": "print('Flask draft')", "explanation": "Flask context"},
        "pyweb-027": {"source": "print('FastAPI draft')", "explanation": "Typed response"},
        "pyweb-045": {"source": "print('Django draft')", "explanation": "Django routing"},
    }
    for key, record in attempts.items():
        state.save(key, record)
    reopened = ModuleState(modules, directory)
    assert reopened.read("cpp-009") == old
    for key, record in attempts.items():
        assert reopened.read(key) == record
    reopened.save("asm-001", {"source": "print('revised Spark draft')"})
    assert reopened.read("clp-001") == attempts["clp-001"]
    assert reopened.read("asm-021") == attempts["asm-021"]
    assert reopened.read("tmb-048") == attempts["tmb-048"]


def test_reading_and_r_companion_services_describe_the_actual_execution_surface(
    legacy: Catalog, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("ds60sqlpy.module_service.rendered_targets", lambda _catalog: {})
    service = ModuleService(legacy, tmp_path / "modules")
    service.jobs.client = WorkerClient(environment={})
    reading = service.action({"action": "module-lesson", "lesson_id": "asm-021"})
    assert reading["source_filename"] == "notes.md"
    assert reading["setup_commands"] == []
    assert "no code execution" in reading["runtime_guidance"]
    assert reading["capability"]["profile"] == "reading"
    assert "Spark 4.0.1" in reading["guide_html"]
    companion = service.action({"action": "module-lesson", "lesson_id": "tmb-005"})
    assert companion["language"] == "r" and companion["runtime_profile"] == "r-statistics"
    assert companion["source_filename"] == "main.R"
    assert not companion["capability"]["ready"]
    assert "TMB" in companion["guide_html"]
    assert companion["setup_commands"] == ["./classroom --profile r-statistics"]
    assert not service.jobs.directory.exists()


@pytest.mark.parametrize("subject", TRACKS)
def test_mcp_tutor_discovers_full_tracks_without_claiming_runtime_or_mastery(
    modules: ModuleCatalog, legacy: Catalog, tmp_path: Path, subject: str
) -> None:
    progress = ProgressStore(legacy, tmp_path / "progress.json")
    tutor = TutorAdapter(CoachingService(legacy, progress))
    tutor._module_catalog = modules
    prefix, count = TRACKS[subject]
    subjects = tutor.invoke("module_subjects", {})
    discovered = next(row for row in subjects["subjects"] if row["id"] == subject)
    assert discovered["authored_count"] == count and discovered["unwritten_count"] == 0
    keys: list[str] = []
    cursor = None
    while True:
        arguments: dict[str, Any] = {"subject": subject, "limit": 10}
        if cursor is not None:
            arguments["cursor"] = cursor
        page = tutor.invoke("module_lessons", arguments)
        assert page["total"] == count
        assert all(row["runtime_status"] == "not_probed" for row in page["lessons"])
        keys.extend(row["id"] for row in page["lessons"])
        cursor = page["next_cursor"]
        if cursor is None:
            break
    assert keys == [f"{prefix}-{i:03}" for i in range(1, count + 1)]
    lesson = tutor.invoke("module_lesson", {"lesson_id": keys[-1]})
    assert lesson["learning_mode"] == "tutorial"
    assert "Do not add exams" in lesson["coaching"]
    assert "no saved pad, runtime, job or mastery operation" in lesson["boundary"]
    assert lesson["guide"]["text"] and lesson["learner"]["text"]
    assert not progress.path.exists()


def test_source_distribution_contains_new_curricula_and_projects_without_local_artifacts(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    for subject in TRACKS:
        shutil.copytree(
            ROOT / "courses" / subject,
            source / "courses" / subject,
            ignore=ignore_private_files,
        )
    shutil.copytree(
        ROOT / "src/ds60sqlpy/spark_likelihood",
        source / "src/ds60sqlpy/spark_likelihood",
        ignore=ignore_private_files,
    )
    shutil.copytree(
        ROOT / "packages/spark-likelihood",
        source / "packages/spark-likelihood",
        ignore=ignore_private_files,
    )
    for relative in (
        "packages/spark-likelihood/dist/unpublished.whl",
        "packages/spark-likelihood/artifacts/private-model.json",
        ".workshop/spark-tmb/run.log",
        "courses/advanced-spark-modeling/projects/catalyst/build/compiled.jar",
        "courses/tmb-modeling/projects/tmb-local/__pycache__/bridge.pyc",
    ):
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Synthetic local state, exclude from distribution")
    destination = tmp_path / "payload"
    stage_course(destination, source_root=source)
    for subject in TRACKS:
        assert (destination / "courses" / subject / "track.json").is_file()
        assert (destination / "courses" / subject / "lessons.json").is_file()
    for relative in (
        "courses/advanced-spark-modeling/projects/catalyst/src/main/scala/ds60/spark/TeachingExtensions.scala",
        "courses/advanced-spark-modeling/projects/spark-tmb/registry.json",
        "courses/advanced-spark-modeling/projects/spark-torch/requirements.lock",
        "courses/tmb-modeling/projects/tmb-local/README.md",
        "courses/custom-likelihood-pytorch/authoring/build.py",
        "courses/python-web/projects/web-lab/README.md",
        "courses/python-web/runtime_probe.py",
        "src/ds60sqlpy/spark_likelihood/contracts.py",
        "src/ds60sqlpy/spark_likelihood/spark_backend.py",
        "packages/spark-likelihood/pyproject.toml",
        "packages/spark-likelihood/src/ds60_spark_likelihood/contracts.py",
    ):
        assert (destination / relative).read_bytes() == (ROOT / relative).read_bytes()
    assert not (destination / ".workshop").exists()
    assert not (destination / "packages/spark-likelihood/dist").exists()
    assert not (destination / "packages/spark-likelihood/artifacts").exists()
    assert not (destination / "courses/advanced-spark-modeling/projects/catalyst/build").exists()
    assert not (destination / "courses/tmb-modeling/projects/tmb-local/__pycache__").exists()


def luminance(color: str) -> float:
    values = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    channels = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in values
    ]
    return sum(
        weight * value for weight, value in zip((0.2126, 0.7152, 0.0722), channels, strict=True)
    )


def test_new_subject_themes_are_distinct_and_readable_in_both_modes() -> None:
    script = (ROOT / "src/ds60sqlpy/assets/classroom.js").read_text()
    accents = set()
    badges = set()
    for subject in TRACKS:
        match = re.search(r'"' + re.escape(subject) + r'": (\[[^\n]+\])', script)
        assert match is not None, f"{subject} falls back to the generic theme"
        light, light_tint, dark, dark_tint, badge = json.loads(match.group(1))
        accents.add(light)
        badges.add(badge)
        for text, background in ((light, light_tint), (dark, dark_tint)):
            values = sorted((luminance(text), luminance(background)))
            assert (values[1] + 0.05) / (values[0] + 0.05) >= 4.5
    assert len(accents) == len(badges) == len(TRACKS)
