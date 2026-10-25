"""Guidance validation catches real maintenance drift without executing examples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.modules import ModuleCatalog
from scripts import check_repository_guidance as gate

ROOT = Path(__file__).resolve().parents[1]


def write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def guidance(tmp_path: Path) -> Path:
    for name in ("README.md", "CONTRIBUTING.md", "AGENTS.md"):
        write(tmp_path, name, "# Guidance\n[Details](docs/details.md)\n")
    write(tmp_path, "docs/details.md", "# Details\n")
    for name in ("README.md", "AGENTS.md"):
        write(tmp_path, "courses/example/" + name, "# Subject\n[Details](../../docs/details.md)\n")
    for name in gate.REQUIRED_SKILLS:
        write(
            tmp_path,
            f".agents/skills/{name}/SKILL.md",
            f"---\nname: {name}\ndescription: Use for the declared purpose.\n---\n"
            "# Skill\n[Contract](references/contract.md)\n",
        )
        write(tmp_path, f".agents/skills/{name}/references/contract.md", "# Contract\n")
    return tmp_path


def inspect(root: Path) -> dict[str, Any]:
    return gate.inspect_guidance(root, subject_ids=["example"])


def kinds(report: dict[str, Any]) -> set[str]:
    return {str(failure["kind"]) for failure in report["failures"]}


def test_guidance_links_and_catalog_subject_requirements(guidance: Path) -> None:
    report = inspect(guidance)
    assert report["failure_count"] == 0
    assert report["module_subjects_checked"] == 1
    assert report["skills_checked"] == 2
    assert report["local_links_checked"] == 7


def test_missing_source_link_and_skill_reference_are_reported(guidance: Path) -> None:
    (guidance / "docs/details.md").unlink()
    (guidance / ".agents/skills/add-learning-path/references/contract.md").unlink()
    report = inspect(guidance)
    assert report["failure_count"] == 6
    assert kinds(report) == {"missing_local_target"}
    assert any(failure["path"].endswith("SKILL.md") for failure in report["failures"])


@pytest.mark.parametrize(
    "relative",
    [
        "courses/example/README.md",
        "courses/example/AGENTS.md",
        ".agents/skills/add-learning-path/SKILL.md",
        "AGENTS.md",
    ],
)
def test_deleted_required_guidance_cannot_disappear_from_inventory(
    guidance: Path,
    relative: str,
) -> None:
    (guidance / relative).unlink()
    report = inspect(guidance)
    assert {"path": relative, "line": 0, "kind": "missing_guidance_source", "target": ""} in report[
        "failures"
    ]


def test_only_actual_links_are_checked_not_fenced_or_inline_examples(guidance: Path) -> None:
    write(
        guidance,
        "docs/examples.md",
        """# Examples
```markdown
[Illustration](courses/<subject>/guides/example.md)
```
~~~~text
[Another example](missing.md)
~~~
[Still inside the longer fence](missing-too.md)
~~~~
A literal `[sample](not-a-file.md)` is not a link.
An inline ``code ` [example](also-missing.md)`` is not a link.
[Actual](details.md#heading-not-validated-here)
""",
    )
    report = inspect(guidance)
    assert report["failure_count"] == 0
    assert report["fragments_deferred"] == 1
    assert any("Fragments" in limit for limit in report["limitations"])


def test_local_url_decoding_titles_and_external_urls(guidance: Path) -> None:
    write(guidance, "docs/space name.md", "# A spaced name\n")
    write(
        guidance,
        "docs/urls.md",
        """[Encoded](space%20name.md?view=read#section)
[Title](details.md "Some title")
[Angle](<space name.md> "Title")
[Web](https://example.invalid/does-not-exist)
[Email](mailto:learner@example.test)
[Other origin](//example.invalid/path)
""",
    )
    report = inspect(guidance)
    assert report["failure_count"] == 0
    assert report["external_urls_skipped"] == 3


@pytest.mark.parametrize(
    "target",
    [
        "../../../private.md",
        "/tmp/private.md",
        "file:///tmp/private.md",
        "C:/private.md",
        "C:\\private.md",
        "~/private.md",
        "%2fetc/passwd",
        "..%2f..%2f..%2fprivate.md",
    ],
)
def test_filesystem_targets_outside_checkout_are_rejected(guidance: Path, target: str) -> None:
    write(guidance, "docs/escape.md", f"[Private]({target})\n")
    assert "external_filesystem_target" in kinds(inspect(guidance))


def test_symlinked_guidance_and_link_targets_are_not_read(
    guidance: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    outside = tmp_path_factory.mktemp("outside-guidance") / "secret.md"
    outside.write_bytes(b"\xff")
    (guidance / "docs/linked.md").symlink_to(outside)
    write(guidance, "docs/link.md", "[Linked](linked.md)\n")
    report = inspect(guidance)
    assert "linked_guidance_source" in kinds(report)
    assert "external_filesystem_target" in kinds(report)
    assert "unreadable_guidance_source" not in kinds(report)


def test_exact_retired_commands_fail_but_external_projects_and_fixture_text_do_not(
    guidance: Path,
) -> None:
    write(guidance, "docs/run.md", "```sh\npython scripts/learning_portal.py\n```\n")
    write(guidance, "tests/fixtures/negative.md", "scripts/build_app.py\n")
    write(guidance, "courses/example/lessons/example.md", "scripts/module_lab.sh\n")
    write(guidance, "work/AGENTS.md", "scripts/build_app.py\n")
    write(
        guidance,
        "courses/example/authoring/README.md",
        "Use CMake for a separate native C++ project.\n",
    )
    report = inspect(guidance)
    assert report["failures"] == [
        {
            "path": "docs/run.md",
            "line": 2,
            "kind": "retired_command_path",
            "target": "scripts/learning_portal.py",
        }
    ]


@pytest.mark.parametrize(
    "name", ["Wrong Name", "another-skill", "[add-learning-path]", "'add-learning-path"]
)
def test_invalid_skill_identity(guidance: Path, name: str) -> None:
    write(
        guidance,
        ".agents/skills/add-learning-path/SKILL.md",
        f"---\nname: {name}\ndescription: A purpose.\n---\n# Guide\n",
    )
    assert "invalid_skill_identity" in kinds(inspect(guidance))


def test_duplicate_skill_identity_and_duplicate_identity_field(guidance: Path) -> None:
    write(
        guidance,
        ".agents/skills/copy/SKILL.md",
        "---\nname: add-learning-path\ndescription: A purpose.\n---\n",
    )
    assert "duplicate_skill_identity" in kinds(inspect(guidance))
    write(
        guidance,
        ".agents/skills/copy/SKILL.md",
        "---\nname: copy\nname: other\ndescription: A purpose.\n---\n",
    )
    assert "invalid_skill_identity" in kinds(inspect(guidance))


@pytest.mark.parametrize(
    "header,expected",
    [
        ("# No header\n", "missing_skill_frontmatter"),
        ("---\nname: add-learning-path\ndescription: ''\n---\n", "missing_skill_description"),
    ],
)
def test_skill_metadata_must_remain_usable(guidance: Path, header: str, expected: str) -> None:
    write(guidance, ".agents/skills/add-learning-path/SKILL.md", header)
    assert expected in kinds(inspect(guidance))


def test_invalid_module_catalog_is_not_silently_treated_as_no_subjects(guidance: Path) -> None:
    assert "invalid_module_catalog" in kinds(gate.inspect_guidance(guidance))


def test_cli_root_json_and_explicit_report_are_read_only_by_default(
    guidance: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    original = gate.inspect_guidance

    def fixture_inspection(root: Path) -> dict[str, Any]:
        assert root == guidance
        return original(root, subject_ids=["example"])

    monkeypatch.setattr(gate, "inspect_guidance", fixture_inspection)
    before = {
        path.relative_to(guidance): path.read_bytes()
        for path in guidance.rglob("*")
        if path.is_file()
    }
    assert gate.main(["--root", str(guidance), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["failure_count"] == 0
    assert {
        path.relative_to(guidance): path.read_bytes()
        for path in guidance.rglob("*")
        if path.is_file()
    } == before
    report = tmp_path / "reports" / "guidance.json"
    assert gate.main(["--root", str(guidance), "--report", str(report)]) == 0
    assert json.loads(report.read_text())["skills_checked"] == 2
    (guidance / "AGENTS.md").unlink()
    assert gate.main(["--root", str(guidance)]) == 1


def test_real_catalog_subjects_and_maintained_guidance() -> None:
    report = gate.inspect_guidance(ROOT)
    assert report["module_subjects_checked"] == len(ModuleCatalog(ROOT).plans)
    assert report["failure_count"] == 0, report["failures"]
