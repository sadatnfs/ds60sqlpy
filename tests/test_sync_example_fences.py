"""Book synchronization preserves code meaning and unrelated teaching material."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import sync_example_fences as sync


def book(root: Path, rows: list[tuple[str, str]]) -> list[Path]:
    chapters = []
    result = []
    for index, (guide, source) in enumerate(rows, 1):
        chapter = root / sync.BOOK / "chapters" / f"{index}.md"
        example = root / sync.BOOK / "examples" / f"{index}.py"
        chapter.parent.mkdir(parents=True, exist_ok=True)
        example.parent.mkdir(parents=True, exist_ok=True)
        chapter.write_text(guide)
        example.write_text(source)
        result.append(chapter)
        chapters.append(
            {
                "chapter_path": str(chapter.relative_to(root)),
                "example_paths": [str(example.relative_to(root))],
            }
        )
    (root / sync.BOOK / "manifest.json").write_text(json.dumps({"chapters": chapters}))
    return result


def test_check_is_read_only_and_sync_is_exact_and_idempotent(tmp_path: Path) -> None:
    untouched = "Opening prose.\n```python\nif broken(\n```\n\n"
    guide = untouched + '```python\nvalue=1\nprint("a b",value)\n```\nClosing prose.\n'
    program = 'value = 1\nprint("a b", value)\n'
    chapter = book(tmp_path, [(guide, program)])[0]
    frozen = tmp_path / "courses/llm-applied/guides/frozen.md"
    frozen.parent.mkdir(parents=True)
    frozen.write_text(guide)
    assert sync.synchronize(tmp_path, check=True) == [str(chapter.relative_to(tmp_path))]
    assert chapter.read_text() == guide
    assert sync.synchronize(tmp_path, check=False)
    assert chapter.read_text() == untouched + "```python\n" + program + "```\nClosing prose.\n"
    assert frozen.read_text() == guide
    assert sync.synchronize(tmp_path, check=True) == []
    assert sync.synchronize(tmp_path, check=False) == []


def test_changed_string_or_operator_fails_before_any_chapter_write(tmp_path: Path) -> None:
    for original, changed in [('print("a b")', 'print("ab")'), ("answer=1+2", "answer = 1 - 2")]:
        guides = ["```python\nvalue=1\n```\n", f"```python\n{original}\n```\n"]
        paths = book(tmp_path, [(guides[0], "value = 1\n"), (guides[1], changed + "\n")])
        with pytest.raises(ValueError, match="found 0"):
            sync.synchronize(tmp_path, check=False)
        assert [path.read_text() for path in paths] == guides


def test_ambiguous_duplicate_complete_program_requires_review(tmp_path: Path) -> None:
    guide = "```python\nvalue=1\n```\n```py\nvalue = 1\n```\n"
    chapter = book(tmp_path, [(guide, "value = 1\n")])[0]
    with pytest.raises(ValueError, match="found 2"):
        sync.synchronize(tmp_path, check=False)
    assert chapter.read_text() == guide


def test_nested_fence_examples_do_not_become_owned_programs(tmp_path: Path) -> None:
    nested = "````markdown\n```python\nvalue=1\n```\n````\n"
    guide = nested + "~~~python\nvalue=1\n~~~\n"
    chapter = book(tmp_path, [(guide, "value = 1\n")])[0]
    sync.synchronize(tmp_path, check=False)
    assert chapter.read_text() == nested + "~~~python\nvalue = 1\n~~~\n"


def test_path_escape_or_symlink_cannot_write_learner_data(tmp_path: Path) -> None:
    chapter = book(tmp_path, [("```python\nx=1\n```\n", "x = 1\n")])[0]
    private = tmp_path / ".learning/notes.md"
    private.parent.mkdir()
    private.write_text("Keep my notes.\n")
    with pytest.raises(ValueError, match="outside"):
        sync.owned_path(tmp_path, "../notes.md", "chapters", ".md")
    chapter.unlink()
    try:
        chapter.symlink_to(private)
    except OSError:
        pytest.skip("Symlinks unavailable")
    with pytest.raises(ValueError, match="symlinks"):
        sync.synchronize(tmp_path, check=False)
    assert private.read_text() == "Keep my notes.\n"


def test_cli_reports_drift_then_accepts_synchronized_book(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    book(tmp_path, [("```python\nx=1\n```\n", "x = 1\n")])
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    assert sync.main(["--check"]) == 1
    assert sync.main([]) == 0
    assert sync.main(["--check"]) == 0
