"""JavaScript/TypeScript teaching contracts and prepared-runtime execution checks."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/javascript-typescript"
ALL_ENTRIES = json.loads((BASE / "lessons.json").read_text())["lessons"]
# Preserve the original language/Node/browser-fixture contracts independently of D3.
ENTRIES = [row for row in ALL_ENTRIES if int(row["id"].split("-")[-1]) <= 42]
PLAN = {row["id"]: row for row in json.loads((BASE / "track.json").read_text())["lessons"]}


class FixtureMarkup(HTMLParser):
    """Read meaningful HTML attributes independently of quote and line style."""

    def __init__(self, source: str) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.feed(source)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))


def test_registered_bundles_have_real_host_contracts_and_separate_solutions() -> None:
    assert len(PLAN) == len(ALL_ENTRIES) == 66
    assert len(ENTRIES) == 42
    assert {entry["id"] for entry in ALL_ENTRIES} == {f"js-{i:03d}" for i in range(1, 67)}
    assert {entry["id"] for entry in ENTRIES} == {f"js-{i:03d}" for i in range(1, 43)}
    assert len({entry["id"] for entry in ENTRIES}) == len(ENTRIES)
    for entry in ENTRIES:
        assert entry["id"] in PLAN
        assert entry["runtime_profile"] == PLAN[entry["id"]]["runtime"]
        reading = entry["runtime_profile"] == "reading"
        typed = entry["runtime_profile"] == "typescript-node"
        assert entry["language"] == (
            "markdown" if reading else "typescript" if typed else "javascript"
        )
        assert len(entry["solution_paths"]) == (1 if reading else 2)
        guide = (ROOT / entry["guide_path"]).read_text()
        assert all(f"### Example {label}:" in guide for label in "AB")
        assert len(re.findall(r"^\s*[1-6]\. \*\*", guide, re.MULTILINE)) == 6
        assert len(re.findall(r"\b[\w'-]+\b", guide)) >= 1050
        assert "## Ask an AI tutor about this lesson" in guide
        assert entry["guide_path"] in guide and entry["source_path"] in guide
        for prerequisite in PLAN[entry["id"]]["prerequisites"]:
            assert f"`{prerequisite}`" in guide
        for relative in [entry["guide_path"], entry["source_path"], *entry["solution_paths"]]:
            path = ROOT / relative
            assert path.is_file() and path.resolve().is_relative_to(BASE)
            text = path.read_text()
            assert "\u2014" not in text and "\u200b" not in text
            if path.suffix in {".mjs", ".mts"}:
                assert re.findall(r"// Exercise ([1-6]):", text) == list("123456")
            if "/solutions/" in relative and path.suffix == ".md":
                assert re.findall(r"^## Exercise ([1-6]):", text, re.MULTILINE) == list("123456")
                assert len(re.findall(r"\b[\w'-]+\b", text)) >= 700


@pytest.mark.skipif(shutil.which("node") is None, reason="Node is not installed for syntax checks")
def test_javascript_references_and_worked_examples_parse(tmp_path: Path) -> None:
    """Catch authoring escape corruption even when the supported runtime is elsewhere."""
    for entry in ENTRIES:
        if entry["language"] != "javascript":
            continue
        reference = next(ROOT / path for path in entry["solution_paths"] if path.endswith(".mjs"))
        guide = (ROOT / entry["guide_path"]).read_text()
        examples = re.findall(r"```javascript\n(.*?)\n```", guide, re.DOTALL)
        assert len(examples) >= 2
        sources = [reference.read_text(), *examples]
        for index, source in enumerate(sources):
            path = tmp_path / f"{entry['id']}-{index}.mjs"
            path.write_text(source)
            result = subprocess.run(
                ["node", "--check", str(path)],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            assert result.returncode == 0, f"{entry['id']} example {index}: {result.stderr}"


@pytest.mark.skipif(
    os.environ.get("DS60_TEST_NODE") != "1",
    reason="Requires explicitly prepared Node24 execution",
)
@pytest.mark.parametrize(
    "entry",
    [row for row in ENTRIES if row["language"] == "javascript"],
    ids=[row["id"] for row in ENTRIES if row["language"] == "javascript"],
)
def test_javascript_reference_on_prepared_node(entry: dict[str, Any]) -> None:
    version = subprocess.run(
        ["node", "-p", "process.versions.node.split('.')[0]"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert version.returncode == 0 and version.stdout.strip() == "24"
    source = next(ROOT / path for path in entry["solution_paths"] if path.endswith(".mjs"))
    result = subprocess.run(
        ["node", str(source)], capture_output=True, text=True, timeout=60, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout.strip().splitlines()[-1]) == {"checks": 6, "status": "passed"}


def test_bounded_host_examples_keep_failure_channels_and_cleanup_visible() -> None:
    cli = (BASE / "solutions/js-018_solution.mjs").read_text()
    assert "bytes > 4096" in cli and "process.exitCode = 2" in cli
    assert (
        "process.stdout.write(JSON.stringify" in cli and "process.stderr.write(error.message" in cli
    )
    assert "maxBuffer:" in cli and "timeout:" in cli
    assert "shell: true" not in cli
    module = (BASE / "solutions/js-010_solution.mjs").read_text()
    assert "ERR_MODULE_NOT_FOUND" in module and "pathToFileURL" in module
    cancellation = (BASE / "solutions/js-013_solution.mjs").read_text()
    assert re.search(
        r"signal\s*\.\s*removeEventListener\s*\(\s*(['\"])abort\1\s*,\s*onAbort\s*,?\s*\)",
        cancellation,
    )
    assert "clearTimeout(timer)" in cancellation and "if (signal.aborted)" in cancellation
    http = (BASE / "solutions/js-017_solution.mjs").read_text()
    assert re.search(r"server\s*\.\s*listen\s*\(\s*0\s*,\s*(['\"])127\.0\.0\.1\1\s*,", http)
    assert "server.closeAllConnections()" in http
    assert "integerParameter" in http and "unsafe_total" in http


@pytest.mark.skipif(
    os.environ.get("DS60_TEST_TYPESCRIPT") != "1",
    reason="Requires explicitly prepared TypeScript5.9.3 and Node24 execution",
)
@pytest.mark.parametrize(
    "entry",
    [row for row in ENTRIES if row["language"] == "typescript"],
    ids=[row["id"] for row in ENTRIES if row["language"] == "typescript"],
)
def test_typescript_reference_compiles_and_runs(entry: dict[str, Any], tmp_path: Path) -> None:
    compiler = Path(
        os.environ.get("DS60_TSC_JS", "/opt/typescript/node_modules/typescript/bin/tsc")
    )
    assert compiler.is_file(), "Prepare the pinned compiler before requesting this test"
    version = subprocess.run(
        ["node", "-p", "process.versions.node.split('.')[0]"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert version.returncode == 0 and version.stdout.strip() == "24"
    source = next(ROOT / path for path in entry["solution_paths"] if path.endswith(".mts"))
    (tmp_path / "main.mts").write_text(source.read_text())
    args = [
        "node",
        str(compiler),
        "--target",
        "ES2022",
        "--module",
        "NodeNext",
        "--moduleResolution",
        "NodeNext",
        "--strict",
        "--noEmitOnError",
        "--skipLibCheck",
        "--types",
        "node",
        "--typeRoots",
        str(compiler.parents[2] / "@types"),
        "--outDir",
        str(tmp_path / "compiled"),
        str(tmp_path / "main.mts"),
    ]
    compiled = subprocess.run(args, capture_output=True, text=True, timeout=60, check=False)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    environment = dict(os.environ, DS60_TSC_JS=str(compiler))
    executed = subprocess.run(
        ["node", str(tmp_path / "compiled/main.mjs")],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env=environment,
    )
    assert executed.returncode == 0, executed.stdout + executed.stderr
    assert json.loads(executed.stdout.strip().splitlines()[-1]) == {"checks": 6, "status": "passed"}


def test_typescript_checks_keep_static_and_runtime_boundaries_distinct() -> None:
    for entry in ENTRIES:
        if entry["language"] != "typescript":
            continue
        reference = next(ROOT / path for path in entry["solution_paths"] if path.endswith(".mts"))
        text = reference.read_text()
        assert "@ts-ignore" not in text and "@ts-nocheck" not in text
    compiled_project = (BASE / "solutions/js-025_solution.mts").read_text()
    assert "--noEmitOnError" in compiled_project and "TS2322" in compiled_project
    assert "TS2835" in compiled_project and "ERR_MODULE_NOT_FOUND" in compiled_project
    schema = (BASE / "solutions/js-024_solution.mts").read_text()
    assert "function validateOrder(value: unknown)" in schema
    assert "value.items.length > 20" in schema and "Number.isSafeInteger" in schema
    assert "items.push({ sku: item.sku, quantity: item.quantity })" in schema


def test_browser_lessons_have_separate_real_fixtures_and_explicit_reading_profiles() -> None:
    registered = {row["id"]: row for row in ENTRIES}
    for number in [29, 30, 31]:
        identity = f"js-{number:03d}"
        assert registered[identity]["runtime_profile"] == "reading"
        for folder in ["fixtures", "solutions/browser"]:
            base = BASE / folder / identity
            for name in ["index.html", "app.js", "style.css", "README.md"]:
                assert (base / name).is_file()
            markup = (base / "index.html").read_text()
            tags = FixtureMarkup(markup).tags
            assert any(tag == "html" and attrs.get("lang") == "en" for tag, attrs in tags)
            assert any(tag == "script" and attrs.get("src") == "app.js" for tag, attrs in tags)
            instructions = (base / "README.md").read_text()
            assert "--bind 127.0.0.1" in instructions
            assert "No screen-reader compatibility claim" in instructions
        starter = (BASE / "fixtures" / identity / "app.js").read_text()
        assert re.findall(r"// Exercise ([1-6]):", starter) == list("123456")
    storage = (BASE / "solutions/browser/js-030/app.js").read_text()
    assert "localStorage.clear" not in storage
    assert "localStorage.removeItem(KEY)" in storage
    assert re.search(r"window\s*\.\s*addEventListener\s*\(\s*(['\"])storage\1\s*,", storage)
    rendering = (BASE / "solutions/browser/js-031/app.js").read_text()
    assert "innerHTML" not in rendering and "output.textContent = input.value" in rendering
    assert "url.origin !== location.origin" in rendering
    policy = (BASE / "solutions/browser/js-031/index.html").read_text()
    assert "default-src 'none'" in policy and "script-src 'self'" in policy
    assert "unsafe-inline" not in policy and "unsafe-eval" not in policy
