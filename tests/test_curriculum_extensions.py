"""Exercise a new course through the existing catalog, planning, CLI and tutor."""

from __future__ import annotations

import json
import os
import shutil
import threading
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.request import ProxyHandler, build_opener

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.catalog_builder import build_catalog, write_catalog
from ds60sqlpy.classroom_http import CourseHTTPServer
from ds60sqlpy.cli import main
from ds60sqlpy.coaching import CoachingService
from ds60sqlpy.curriculum_framework import RUNNERS, load_extensions
from ds60sqlpy.lab import LabServer
from ds60sqlpy.lesson_reader import build_lesson_html, rendered_targets
from ds60sqlpy.mcp_server import TutorAdapter
from ds60sqlpy.study_plan import build_study_plan
from scripts.course_payload import stage_course

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def skeleton(tmp_path: Path) -> Path:
    root = tmp_path / "course with spaces"
    root.mkdir()
    shutil.copy2(ROOT / "pyproject.toml", root / "pyproject.toml")
    for relative, pattern in (
        ("python/ds-60day/notebooks", "day*.ipynb"),
        ("sql/postgres-60day", "day*.sql"),
        ("bridge/lessons", "day*.py"),
    ):
        (root / relative).mkdir(parents=True)
        for source in (ROOT / relative).glob(pattern):
            (root / relative / source.name).touch()
    (root / "curriculum/extensions").mkdir(parents=True)
    return root


def extension(root: Path, runner: str = "none") -> tuple[Path, dict[str, Any]]:
    folder = root / "courses/reasoning-demo"
    folder.mkdir(parents=True)
    suffix = RUNNERS[runner].file_suffix
    for name, content in {
        "README.md": "# Language-model reasoning\n",
        "guide.md": "# Compare claims\n\nPredict what evidence would change your conclusion.\n",
        f"lesson{suffix}": "# Exercise 1: compare two claims\n",
        "solutions.md": "# Compare the evidence\n\nAn explicit reasoning solution.\n",
    }.items():
        (folder / name).write_text(content, encoding="utf-8")
    payload: dict[str, Any] = {
        "schema_version": 1,
        "tracks": {
            "reasoning-demo": {
                "title": "Language-model reasoning",
                "plan": "courses/reasoning-demo/README.md",
            }
        },
        "lessons": [
            {
                "id": "reasoning-demo-01",
                "track": "reasoning-demo",
                "day": 1,
                "title": "Compare language-model claims",
                "level": "foundation",
                "phase": "Reasoning",
                "estimated_minutes": 40,
                "prerequisites": ["python-01"],
                "lesson_path": f"courses/reasoning-demo/lesson{suffix}",
                "guide_path": "courses/reasoning-demo/guide.md",
                "solution_paths": ["courses/reasoning-demo/solutions.md"],
                "dependency_group": "standard-library",
                "network": "offline",
                "runner": runner,
                "topics": ["language-models", "evidence"],
            }
        ],
        "learning_paths": {
            "language-model-reasoning": {
                "title": "Language-model reasoning",
                "description": "Compare claims with explicit evidence.",
                "targets": ["reasoning-demo-01"],
            }
        },
    }
    manifest = root / "curriculum/extensions/reasoning-demo.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    return manifest, payload


def test_registered_theory_flows_through_catalog_plan_cli_and_tutor(
    skeleton: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    extension(skeleton)
    write_catalog(skeleton)
    catalog = Catalog.load(skeleton)
    lesson = catalog.get("reasoning-demo-01")
    assert len(catalog.lessons()) == 169
    assert lesson.runner == "none" and lesson.topics == ("language-models", "evidence")
    assert [item.id for item in catalog.lessons("reasoning-demo")] == [lesson.id]
    assert [item.id for item in build_study_plan(catalog, [lesson.id]).lessons] == [
        "python-01",
        lesson.id,
    ]
    service = CoachingService(catalog)
    paths = service.paths()
    assert paths["tracks"]["reasoning-demo"]["title"] == "Language-model reasoning"
    assert paths["paths"]["language-model-reasoning"]["targets"] == (lesson.id,)
    assert "Predict what evidence" in service.lesson(lesson.id)["guide"]
    adapter = TutorAdapter(service)
    result = adapter.invoke("course_lessons", {"track": "reasoning-demo", "query": "evidence"})
    assert result["lessons"][0]["id"] == lesson.id
    assert "solution_paths" not in result["lessons"][0]
    assert adapter.invoke("course_plan", {"targets": ["language-model-reasoning"]})["targets"] == (
        lesson.id,
    )
    assert main(["--repo", str(skeleton), "catalog", "--track", "reasoning-demo", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["id"] == lesson.id
    assert (
        main(["--repo", str(skeleton), "plan", "--path", "language-model-reasoning", "--json"]) == 0
    )
    assert json.loads(capsys.readouterr().out)["targets"] == [lesson.id]
    assert not (skeleton / ".learning").exists()


@pytest.mark.parametrize("runner", ["none", "cpp", "scala", "kubernetes"])
def test_future_topics_are_registered_without_claiming_an_executor(
    skeleton: Path, runner: str
) -> None:
    extension(skeleton, runner)
    catalog = build_catalog(skeleton)
    item = next(item for item in catalog["lessons"] if item["id"] == "reasoning-demo-01")
    assert item["runner"] == runner
    assert RUNNERS[runner].executor is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("runner", "shell"),
        ("runner", []),
        ("day", True),
        ("estimated_minutes", 0),
        ("topics", "not-a-list"),
        ("prerequisites", "python-01"),
        ("lesson_path", "../../private.txt"),
        ("guide_path", "/etc/passwd"),
        ("guide_path", "courses\\reasoning-demo\\guide.md"),
        ("solution_paths", []),
    ],
)
def test_bad_manifest_metadata_is_rejected_before_delivery(
    skeleton: Path, field: str, value: object
) -> None:
    manifest, payload = extension(skeleton)
    payload["lessons"][0][field] = value
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        build_catalog(skeleton)


@pytest.mark.parametrize(
    "change",
    [
        "existing-id",
        "existing-track",
        "missing-prerequisite",
        "cycle",
        "day-collision",
        "existing-path",
        "missing-target",
        "lesson-path-collision",
    ],
)
def test_extensions_cannot_replace_inventory_or_break_the_graph(
    skeleton: Path, change: str
) -> None:
    manifest, payload = extension(skeleton)
    lesson = payload["lessons"][0]
    if change == "existing-id":
        lesson["id"] = "python-01"
    elif change == "existing-track":
        payload["tracks"] = {"python": payload["tracks"]["reasoning-demo"]}
    elif change == "missing-prerequisite":
        lesson["prerequisites"] = ["not-registered"]
    elif change == "cycle":
        lesson["prerequisites"] = [lesson["id"]]
    elif change == "day-collision":
        lesson.update(track="python", day=1)
    elif change == "existing-path":
        payload["learning_paths"]["python-foundations"] = payload["learning_paths"].pop(
            "language-model-reasoning"
        )
    elif change == "missing-target":
        payload["learning_paths"]["language-model-reasoning"]["targets"] = ["missing"]
    elif change == "lesson-path-collision":
        payload["learning_paths"]["python-01"] = payload["learning_paths"].pop(
            "language-model-reasoning"
        )
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        build_catalog(skeleton)


def test_windows_utf8_bom_manifest_and_unknown_track_diagnostics(
    skeleton: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest, payload = extension(skeleton)
    manifest.write_text(json.dumps(payload), encoding="utf-8-sig")
    assert len(load_extensions(skeleton).lessons) == 1
    write_catalog(skeleton)
    assert main(["--repo", str(skeleton), "catalog", "--track", "missing"]) == 2
    assert "Unknown registered track" in capsys.readouterr().err


def test_track_registration_is_independent_of_manifest_filename_order(skeleton: Path) -> None:
    manifest, payload = extension(skeleton)
    tracks = payload.pop("tracks")
    early = manifest.with_name("a-lessons.json")
    manifest.unlink()
    early.write_text(json.dumps(payload), encoding="utf-8")
    late = early.with_name("z-track.json")
    late.write_text(json.dumps({"schema_version": 1, "tracks": tracks}), encoding="utf-8")
    assert len(build_catalog(skeleton)["lessons"]) == 169


def test_duplicate_artifact_identity_is_rejected_before_writing_catalog(skeleton: Path) -> None:
    manifest, payload = extension(skeleton)
    payload["lessons"][0]["guide_path"] = payload["lessons"][0]["lesson_path"]
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="appears more than once"):
        write_catalog(skeleton)
    assert not (skeleton / "curriculum/catalog.json").exists()


@pytest.mark.skipif(os.name == "nt", reason="Creating symlinks needs Windows privileges")
def test_internal_symlink_is_rejected_consistently_with_packaging(skeleton: Path) -> None:
    manifest, payload = extension(skeleton)
    (skeleton / "courses/alias").symlink_to(
        skeleton / "courses/reasoning-demo", target_is_directory=True
    )
    payload["lessons"][0]["lesson_path"] = "courses/alias/lesson.md"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="symbolic link"):
        build_catalog(skeleton)


def test_manifest_paths_use_exact_case_on_every_host(skeleton: Path) -> None:
    manifest, payload = extension(skeleton)
    payload["lessons"][0]["guide_path"] = "courses/reasoning-demo/GUIDE.MD"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        write_catalog(skeleton)


@pytest.mark.parametrize("reparse_tag", [0xA0000003, 0xA000000C, 0x9000001A])
def test_windows_redirect_tags_are_rejected_but_cloud_files_remain_portable(
    skeleton: Path, monkeypatch: pytest.MonkeyPatch, reparse_tag: int
) -> None:
    extension(skeleton)
    directory = skeleton / "courses/reasoning-demo"
    original_lstat = Path.lstat

    def windows_lstat(path: Path) -> Any:
        information = original_lstat(path)
        if path == directory:
            return SimpleNamespace(st_mode=information.st_mode, st_reparse_tag=reparse_tag)
        return information

    monkeypatch.setattr(Path, "lstat", windows_lstat)
    if reparse_tag in {0xA0000003, 0xA000000C}:
        with pytest.raises(ValueError, match="symbolic link or junction"):
            build_catalog(skeleton)
    else:
        assert len(build_catalog(skeleton)["lessons"]) == 169


@pytest.mark.parametrize(
    "relative", ["credentials.json", "cache/lesson.md", "example.egg-info/lesson.md"]
)
def test_manifest_cannot_reference_files_omitted_from_distribution(
    skeleton: Path, relative: str
) -> None:
    manifest, payload = extension(skeleton)
    target = skeleton / "courses/reasoning-demo" / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("Public test fixture", encoding="utf-8")
    payload["lessons"][0]["lesson_path"] = target.relative_to(skeleton).as_posix()
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="omitted build metadata"):
        build_catalog(skeleton)


def test_notebook_starter_preserves_magic_cell_boundaries(skeleton: Path) -> None:
    manifest, payload = extension(skeleton, "python")
    payload["lessons"][0]["lesson_path"] = "courses/reasoning-demo/lesson.ipynb"
    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["# Explain the evidence"]},
            {"cell_type": "code", "source": ["value = 21\n"]},
            {"cell_type": "code", "source": ["%timeit -n 1 -r 1 value * 2\n"]},
        ]
    }
    (skeleton / payload["lessons"][0]["lesson_path"]).write_text(
        json.dumps(notebook), encoding="utf-8"
    )
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    write_catalog(skeleton)
    response = CoachingService(Catalog.load(skeleton)).lesson("reasoning-demo-01")
    assert response["learner_code"].count("# %%\n") == 2
    assert "%timeit" in response["learner_code"]
    assert len(response["notebook_cells"]) == 2
    lines = response["learner_code"].splitlines()
    for cell in response["notebook_cells"]:
        assert lines[cell["start_line"] - 1] == cell["code"].splitlines()[0]


def test_new_track_reader_is_served_in_unified_classroom_mode(
    tmp_path: Path,
) -> None:
    root = tmp_path / "complete course"
    stage_course(root)
    beta_inventory = root / "courses/llm-theory/lessons.json"
    beta_before = beta_inventory.read_bytes()
    extension(root)
    assert beta_inventory.read_bytes() == beta_before
    write_catalog(root)
    catalog = Catalog.load(root)
    lesson = catalog.get("reasoning-demo-01")
    targets = rendered_targets(catalog)
    assert catalog.resolve("courses/reasoning-demo/README.md") in targets
    page = root / "lesson-pages/reasoning-demo-01.html"
    page.write_text(build_lesson_html(catalog, lesson, targets=targets), encoding="utf-8")
    assert "const LAB_MODE = false;" in page.read_text()
    opener = build_opener(ProxyHandler({}))
    for server_class, expected in ((LabServer, "true"), (CourseHTTPServer, "true")):
        server = server_class(catalog, progress_path=tmp_path / f"{expected}-progress.json")
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with opener.open(
                server.url + "lesson-pages/reasoning-demo-01.html", timeout=5
            ) as response:
                served = response.read().decode()
            assert f"const LAB_MODE = {expected};" in served
            assert "Compare language-model claims" in served
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
