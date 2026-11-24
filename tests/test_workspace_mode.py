"""Check the workspace mode descriptor using the actual offline JavaScript helper."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

ASSET = Path(__file__).parents[1] / "src/ds60sqlpy/assets/classroom.js"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node is an optional developer UI check")


def evaluate_mode(lesson: dict[str, Any], cap: dict[str, Any] | None) -> dict[str, Any]:
    document = ASSET.read_text(encoding="utf-8")
    source = document.split("// BEGIN WORKSPACE MODE PURE HELPERS", 1)[1].split(
        "// END WORKSPACE MODE PURE HELPERS", 1
    )[0]
    program = (
        "const vm = require('node:vm');\n"
        'let input = "";\n'
        "process.stdin.setEncoding('utf8');\n"
        "process.stdin.on('data', chunk => input += chunk);\n"
        "process.stdin.on('end', () => {\n"
        "const value = JSON.parse(input);\n"
        "const sandbox = {lesson: value.lesson, cap: value.cap}; vm.createContext(sandbox);\n"
        "vm.runInContext(value.source, sandbox);\n"
        "console.log(JSON.stringify(vm.runInContext('workspaceMode(lesson, cap)', sandbox)));\n"
        "});\n"
    )
    result = subprocess.run(
        [str(NODE), "-e", program],
        input=json.dumps({"source": source, "lesson": lesson, "cap": cap}),
        text=True,
        capture_output=True,
        timeout=5,
        check=True,
    )
    value = json.loads(result.stdout)
    assert isinstance(value, dict)
    return value


def test_module_reading_lesson_hides_results_and_never_prompts_a_run() -> None:
    mode = evaluate_mode(
        {"engine": "module", "runtime_profile": "reading"},
        {"profile": "reading", "ready": True, "detail": "x"},
    )
    assert mode["kind"] == "reading"
    assert mode["label"] == "Reading lesson"
    assert mode["runLabel"] == "Reading and reasoning"
    assert mode["runsIn"] == "No code runs in this lesson."
    assert mode["resultsIn"] == "No run results. Your worksheet is saved with this lesson."
    assert mode["showResults"] is False
    assert mode["emptyStatus"] == ""
    assert mode["emptyOutput"] == ""


def test_legacy_reading_wins_over_save_only() -> None:
    mode = evaluate_mode(
        {
            "engine": "legacy",
            "runtime_profile": "reading",
            "runner": {
                "id": "none",
                "title": "Reading",
                "executor": "none",
                "implemented": False,
            },
        },
        {"ready": False},
    )
    assert mode["kind"] == "reading"
    assert mode["resultsIn"] == "No run results. Your reading notes are saved with this lesson."
    assert mode["showResults"] is False


def legacy(runner_id: str, title: str, executor: str, *, implemented: bool = True) -> dict:
    return {
        "engine": "legacy",
        "runtime_profile": runner_id,
        "runner": {
            "id": runner_id,
            "title": title,
            "executor": executor,
            "implemented": implemented,
        },
    }


def module(profile: str, **extra: str) -> dict:
    return {"engine": "module", "runtime_profile": profile, **extra}


RUN_RESULTS = "The Result panel under your code"
READY = "Ready to run in your local classroom."
SAVE_ONLY_DETAIL = "Source can be saved here; this execution adapter is not implemented."
CASES: list[tuple[str, dict, dict, dict]] = [
    (
        "legacy-python-ready",
        legacy("python", "Python", "python"),
        {"profile": "python", "ready": True, "detail": "Python is ready."},
        {
            "kind": "python",
            "runLabel": "Run code",
            "runsIn": "The Python runner in your local classroom",
            "resultsIn": RUN_RESULTS,
            "showResults": True,
            "ready": True,
            "readyText": READY + " Python is ready.",
        },
    ),
    (
        "legacy-python-not-ready",
        legacy("python", "Python", "python"),
        {"profile": "python", "ready": False, "detail": "Python is unavailable."},
        {
            "kind": "python",
            "runLabel": "Run code",
            "runsIn": "The Python runner in your local classroom",
            "resultsIn": RUN_RESULTS,
            "showResults": True,
            "ready": False,
            "readyText": READY + " Python is unavailable.",
        },
    ),
    (
        "legacy-sql-ready",
        legacy("sql", "SQL", "sql"),
        {"profile": "sql", "ready": True, "detail": ""},
        {
            "kind": "sql",
            "runLabel": "Run code",
            "runsIn": "PostgreSQL in your local classroom",
            "resultsIn": RUN_RESULTS,
            "showResults": True,
            "ready": True,
            "readyText": READY,
        },
    ),
    (
        "legacy-reading",
        {**legacy("reading", "Reading", "none", implemented=False), "runtime_profile": "reading"},
        {"profile": "reading", "ready": False, "detail": ""},
        {
            "kind": "reading",
            "runLabel": "Reading and reasoning",
            "runsIn": "No code runs in this lesson.",
            "resultsIn": "No run results. Your reading notes are saved with this lesson.",
            "showResults": False,
            "ready": True,
            "readyText": "Read the guide and record your reasoning. "
            "This lesson needs no code runtime.",
        },
    ),
    (
        "legacy-save-only",
        legacy("cpp", "C++", "cpp", implemented=False),
        {"profile": "cpp", "ready": False, "detail": SAVE_ONLY_DETAIL},
        {
            "kind": "save-only",
            "runLabel": "Save only",
            "runsIn": "Nothing runs here. This classroom saves C++ code but cannot run it.",
            "resultsIn": "No run results. Your code is saved with this lesson.",
            "showResults": False,
            "ready": False,
            "readyText": "Save only. Your C++ code is saved in your local learning workspace, "
            "but this classroom has no runner for it. " + SAVE_ONLY_DETAIL,
        },
    ),
    (
        "module-python-core-ready",
        module("python-core"),
        {"profile": "python-core", "ready": True, "detail": "Worker ready."},
        {
            "kind": "worker",
            "runLabel": "Run code",
            "runsIn": "The python-core worker container on this computer",
            "resultsIn": RUN_RESULTS,
            "showResults": True,
            "ready": True,
            "readyText": READY + " Worker ready.",
        },
    ),
    (
        "module-go-not-ready",
        module("go"),
        {"profile": "go", "ready": False, "detail": "Prepare go first."},
        {
            "kind": "worker",
            "runLabel": "Run code",
            "runsIn": "The go worker container on this computer",
            "resultsIn": RUN_RESULTS,
            "showResults": True,
            "ready": False,
            "readyText": READY + " Prepare go first.",
        },
    ),
    (
        "module-pytorch-cuda-ready",
        module("pytorch-cuda"),
        {"profile": "pytorch-cuda", "ready": True, "detail": ""},
        {
            "kind": "worker",
            "runLabel": "Run code",
            "runsIn": "The pytorch-cuda worker container on this computer (uses your NVIDIA GPU)",
            "resultsIn": RUN_RESULTS,
            "showResults": True,
            "ready": True,
            "readyText": READY,
        },
    ),
    (
        "module-reading",
        module("reading"),
        {"profile": "reading", "ready": True},
        {
            "kind": "reading",
            "runLabel": "Reading and reasoning",
            "runsIn": "No code runs in this lesson.",
            "resultsIn": "No run results. Your worksheet is saved with this lesson.",
            "showResults": False,
            "ready": True,
            "readyText": "Read the guide and record your reasoning. "
            "This lesson needs no code runtime.",
        },
    ),
    (
        "module-dax-offline-draft",
        module("dax-offline", execution_mode="draft"),
        {"profile": "dax-offline", "ready": True, "detail": "Offline reference desk"},
        {
            "kind": "draft",
            "runLabel": None,
            "runsIn": "Nothing runs. You save, compare and export this draft.",
            "resultsIn": "The worked comparison below the editor",
            "showResults": False,
            "ready": True,
            "readyText": "Offline reference desk",
        },
    ),
    (
        "module-html-browser",
        module("html-browser"),
        {"profile": "html-browser", "ready": True, "detail": "Preview isolated."},
        {
            "kind": "browser",
            "runLabel": "Run browser preview",
            "runsIn": "The isolated preview in this browser tab",
            "resultsIn": "The preview frame in the code panel, "
            "with saved observations under Saved runs",
            "showResults": True,
            "ready": True,
            "readyText": "Ready to preview in this browser tab. Preview isolated.",
        },
    ),
    (
        "module-javascript-browser",
        module("javascript-browser"),
        {"profile": "javascript-browser", "ready": True, "detail": ""},
        {
            "kind": "browser",
            "runLabel": "Run browser preview",
            "runsIn": "The isolated preview in this browser tab",
            "resultsIn": "The preview frame in the code panel, "
            "with saved observations under Saved runs",
            "showResults": True,
            "ready": True,
            "readyText": "Ready to preview in this browser tab.",
        },
    ),
]


@pytest.mark.parametrize(
    ("lesson", "cap", "expected"), [c[1:] for c in CASES], ids=[c[0] for c in CASES]
)
def test_every_mode_has_exact_copy(lesson: dict, cap: dict, expected: dict) -> None:
    mode = evaluate_mode(lesson, cap)
    assert {key: mode[key] for key in expected} == expected


def test_non_running_modes_hide_results_and_never_prompt_a_run() -> None:
    for _, lesson, cap, _expected in CASES:
        mode = evaluate_mode(lesson, cap)
        if mode["kind"] not in {"reading", "draft", "save-only"}:
            continue
        assert mode["showResults"] is False
        for value in mode.values():
            assert "Press Run" not in str(value)


def test_no_mode_copy_contains_en_or_em_dashes() -> None:
    for _, lesson, cap, _expected in CASES:
        for value in evaluate_mode(lesson, cap).values():
            assert "\u2013" not in str(value)
            assert "\u2014" not in str(value)
