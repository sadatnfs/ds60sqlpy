"""Source, reader and independent foundation oracles for the 72-chapter tutorial."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/data-ml-engineering"


def module_at(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def builder() -> ModuleType:
    return module_at("dme_book_builder", BASE / "authoring/build.py")


def reference(number: int) -> ModuleType:
    if number == 4:
        pytest.importorskip("duckdb", reason="Prepared data-engineering runtime required")
    if number == 7:
        pytest.importorskip("pydantic", reason="Prepared data-engineering runtime required")
    return module_at(
        f"dme_reference_{number}", BASE / "authoring/foundations/examples" / f"dme-{number:03}.py"
    )


def test_partial_book_is_not_admitted_as_a_complete_track() -> None:
    publication = builder()
    chapters = publication.load_chapters(complete=False)
    assert len(chapters) >= 8
    if len(chapters) < 72:
        assert not (BASE / "track.json").exists()
        assert not (BASE / "lessons.json").exists()
        with pytest.raises(ValueError):
            publication.load_chapters()
    else:
        expected = publication.render()
        for path, content in expected.items():
            assert path.read_text("utf-8") == content
        track = json.loads((BASE / "track.json").read_text())
        admission = json.loads((BASE / "lessons.json").read_text())
        assert track["learning_mode"] == "tutorial"
        assert [row["id"] for row in track["lessons"]] == [f"dme-{n:03}" for n in range(1, 73)]
        assert all(row["solution_paths"] == [] for row in admission["lessons"])


def test_completed_foundation_text_renders_math_and_exact_highlighted_programs() -> None:
    from ds60sqlpy.lesson_reader import LinkResolver, render_markdown

    publication = builder()
    chapters = [
        row
        for row in publication.load_chapters(complete=False)
        if row["guide_source"].startswith("courses/data-ml-engineering/authoring/foundations/")
    ]
    assert len(chapters) >= 8
    math_count = 0
    for chapter in chapters:
        source = ROOT / chapter["guide_source"]
        program = (ROOT / chapter["source_path"]).read_text()
        guide = source.read_text().replace(publication.MARKER, "```python\n" + program + "```")
        rendered = render_markdown(
            guide, resolver=LinkResolver(repo_root=ROOT, source_path=source, targets={})
        )
        assert 'class="language-python"' in rendered
        assert "math-source" not in rendered
        assert "Worked case 1" in rendered and "Worked case 2" in rendered
        math_count += rendered.count("<math")
        assert "dme-" in rendered
    assert math_count >= 8


def test_local_link_relocation_preserves_code_literals(tmp_path: Path) -> None:
    publication = builder()
    source = tmp_path / "authoring/chapters/chapter.md"
    source.parent.mkdir(parents=True)
    target = tmp_path / "guides/chapter.md"
    target.parent.mkdir()
    reference_path = tmp_path / "project/README.md"
    reference_path.parent.mkdir()
    reference_path.write_text("# Owned project\n")
    source.write_text("# Draft\n")
    text = (
        "[Project](../../project/README.md#run)\n\n```python\n"
        "value = '[Project](../../project/README.md)'\n```\n"
    )
    actual = publication.relocate_links(text, source, target, tmp_path)
    assert "[Project](../project/README.md#run)" in actual
    assert "value = '[Project](../../project/README.md)'" in actual


def test_local_link_relocation_rejects_missing_or_escaped_targets(tmp_path: Path) -> None:
    publication = builder()
    source = tmp_path / "chapter.md"
    source.write_text("# Draft\n")
    with pytest.raises(ValueError, match="Broken or escaped"):
        publication.relocate_links("[Missing](missing.md)", source, tmp_path / "guide.md", tmp_path)
    with pytest.raises(ValueError, match="Broken or escaped"):
        publication.relocate_links(
            "[Escape](../outside.md)", source, tmp_path / "guide.md", tmp_path
        )


@pytest.mark.parametrize("number", range(1, 9))
def test_foundation_programs_execute_two_complete_cases(number: int) -> None:
    program = reference(number)
    assert isinstance(program.example_one(), dict)
    assert isinstance(program.example_two(), dict)


def test_record_reconciliation_does_not_publish_a_partial_valid_subset() -> None:
    program = reference(1)
    result = program.summarize(
        [{"delivery_id": "A", "packages": 4}, {"delivery_id": "B", "packages": "3"}]
    )
    assert result["candidate_packages"] == 4 and result["publishable"] is False
    assert result["input_rows"] == result["accepted_rows"] + len(result["rejected"]) == 2
    for invalid in (True, -1, 0, None):
        assert (
            program.summarize([{"delivery_id": "C", "packages": invalid}])["publishable"] is False
        )


def test_sql_oracle_retains_identities_and_detects_dimension_fanout() -> None:
    program = reference(4)
    assert program.example_one()["packages_by_route"] == [(10, "north", 2 + 3), (20, "south", 1)]
    invalid = program.example_two()
    assert invalid["fanout_total"] == 2 * (2 + 3) + 1
    assert invalid["all_rows_known_values_mean"] == (3, 2, (0 + 10) / 2)


def test_boundary_selection_and_real_negative_test_evidence() -> None:
    functions = reference(5)
    assert functions.delayed_ids(
        [{"id": "at", "delay_minutes": 5}, {"id": "over", "delay_minutes": 6}], 5
    ) == ["over"]
    testing = reference(6).example_two()
    assert testing["changed_expected"] == 9 and testing["wrong_changed_result"] == 6
    assert testing["expected_unittest_failures"] == 1


def test_schema_checks_are_directional_and_reject_blank_identity() -> None:
    program = reference(7)
    assert program.example_one()["old_reader_accepts_new_field"] is False
    for identity in ("", "  "):
        with pytest.raises(ValueError):
            program.DeliveryV1.model_validate({"delivery_id": identity, "packages": 2})
    assert program.example_two()["wrong_unit_rejected"] is True


def test_manifest_rejects_changed_source_independently_of_data(tmp_path: Path) -> None:
    program = reference(8)
    source = tmp_path / "transform.py"
    source.write_text("def compute(values):\n    return sum(values)\n")
    expected = program.manifest(tmp_path, ["transform.py"])
    source.write_text("def compute(values):\n    return 0\n")
    with pytest.raises(ValueError, match="transform.py"):
        program.verify(tmp_path, expected)
    assert program.example_two()["same_values_can_have_different_byte_identities"] is True


def test_link_relocation_preserves_inline_code_and_math(tmp_path: Path) -> None:
    publication = builder()
    source = tmp_path / "source.md"
    source.write_text("# Draft\n")
    text = "`[literal](not-a-file.md)` and \\(f[x](t)\\)\n\n\\[\ng[x](t)\n\\]\n"
    assert publication.relocate_links(text, source, tmp_path / "guide.md", tmp_path) == text


@pytest.mark.parametrize("prerequisites", [["dme-001"], ["dme-073"], ["python-01"]])
def test_source_admission_rejects_nonpreceding_or_external_prerequisite_ids(
    prerequisites: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    publication = builder()
    original_loads = json.loads
    first_fragment = (BASE / "authoring/foundations/chapters.json").read_text()

    def modified(text: str) -> object:
        value = original_loads(text)
        if text == first_fragment:
            value[0]["prerequisites"] = prerequisites
        return value

    monkeypatch.setattr(publication.json, "loads", modified)
    with pytest.raises(ValueError, match="earlier stable"):
        publication.load_chapters(complete=False)
