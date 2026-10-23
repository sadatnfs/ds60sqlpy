"""Reviewable prose repairs must not change programs, IDs or runtime contracts."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/normalize_lesson_prose.py"
SPEC = importlib.util.spec_from_file_location("normalize_lesson_prose", SCRIPT)
assert SPEC and SPEC.loader
PIPELINE = importlib.util.module_from_spec(SPEC)
sys.path.insert(0, str(SCRIPT.parent))
try:
    SPEC.loader.exec_module(PIPELINE)
finally:
    sys.path.pop(0)


def test_repairs_preserve_code_math_and_identifiers() -> None:
    source = r"""A finite guide andcorrection.
`andcorrection` is an identifier, and \(andcorrection\) is explicit math.
[reference](some/andcorrection.md)
```python
andcorrection = "andcorrection"
````
    andcorrection = 3
"""
    output, hits = PIPELINE.normalize(source, {"andcorrection": "and correction"})
    assert hits == {"andcorrection": 1}
    assert output == source.replace("guide andcorrection.", "guide and correction.")


def test_authoring_prose_slots_preserve_embedded_programs_and_helper_strings() -> None:
    source = """add("stable-id", "An afinitething.", "andcorrection.", [("Name", "afinitething")], [
    ex("andcorrection", "afinitething", "andcorrection",
       "andcorrection = 'afinitething'", "andcorrection")
], helper="andcorrection = 'afinitething'", imports="from afinitething import andcorrection")
"""
    output, hits = PIPELINE.repair_authoring(
        source, {"afinitething": "a finite thing", "andcorrection": "and correction"}
    )
    assert hits
    assert "helper=\"andcorrection = 'afinitething'\"" in output
    assert 'imports="from afinitething import andcorrection"' in output
    assert "\"andcorrection = 'afinitething'\"" in output
    assert "stable-id" in output
    assert "and correction" in output


def test_display_metadata_changes_do_not_mutate_identity_or_execution(tmp_path: Path) -> None:
    (tmp_path / "curriculum").mkdir()
    (tmp_path / "courses/example").mkdir(parents=True)
    (tmp_path / "curriculum/prose-repairs.json").write_text(
        json.dumps({"repairs": {"andcorrection": "and correction"}})
    )
    path = tmp_path / "courses/example/track.json"
    original = {
        "id": "andcorrection",
        "summary": "Learn andcorrection.",
        "lessons": [
            {
                "id": "andcorrection",
                "source_path": "andcorrection.py",
                "runtime": "python-core",
                "prerequisites": ["andcorrection"],
                "title": "Trace andcorrection",
                "lab": "Explain andcorrection.",
            }
        ],
    }
    path.write_text(json.dumps(original))
    report = PIPELINE.run(tmp_path, True)
    updated = json.loads(path.read_text())
    assert updated["id"] == original["id"]
    for key in ("id", "source_path", "runtime", "prerequisites"):
        assert updated["lessons"][0][key] == original["lessons"][0][key]
    assert updated["summary"] == "Learn and correction."
    assert report["protected_code_unchanged"]
    assert PIPELINE.run(tmp_path, False)["files_changed"] == 0


def test_reviewed_exceptions_are_not_repaired() -> None:
    registry = json.loads((ROOT / "curriculum/prose-repairs.json").read_text())
    for word in ("async", "overfitting", "isfinite", "isinstance", "noexcept", "toarray"):
        assert word in registry["reviewed_exceptions"]
        assert word not in registry["repairs"]


def test_sentence_punctuation_is_not_an_identifier_boundary() -> None:
    repairs = {"andcorrection": "and correction"}
    output, hits = PIPELINE.normalize(
        "Status:andcorrection. object.andcorrection andcorrection.method", repairs
    )
    assert output == "Status:and correction. object.andcorrection andcorrection.method"
    assert hits == {"andcorrection": 1}
