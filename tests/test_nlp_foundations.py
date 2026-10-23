"""NLP foundation examples and counterexamples, independent of model downloads."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]


def entries() -> list[dict[str, Any]]:
    payload = json.loads((ROOT / "courses/nlp/lessons.json").read_text())
    return [entry for entry in payload["lessons"] if int(entry["id"].split("-")[-1]) <= 4]


def reference(key: str) -> Any:
    path = ROOT / "courses/nlp/solutions" / f"{key}_solution.py"
    spec = importlib.util.spec_from_file_location(key.replace("-", "_"), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("entry", entries(), ids=lambda entry: entry["id"])
def test_foundation_contract_and_runnable_examples(
    entry: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    def refuse(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("A default foundation example attempted a network connection.")

    monkeypatch.setattr("socket.socket.connect", refuse)
    guide = (ROOT / entry["guide_path"]).read_text()
    assert len(guide.split()) >= 1400
    assert "\u2014" not in guide
    assert len(re.findall(r"^\d\. \*\*", guide, re.MULTILINE)) == 6
    assert entry["guide_path"] in guide and entry["source_path"] in guide
    assert "## Ask Codex about this lesson" in guide
    namespace: dict[str, Any] = {}
    examples = re.findall(r"```python\n(.*?)\n```", guide, re.DOTALL)
    assert len(examples) >= 2
    for code in examples:
        exec(compile(code, entry["guide_path"], "exec"), namespace)
    result = reference(entry["id"]).verify()
    assert result["status"] == "passed"
    assert result["automated_exercises"] + result.get("written_exercises", 0) == 6
    explanation = next(p for p in entry["solution_paths"] if p.endswith(".md"))
    text = (ROOT / explanation).read_text()
    assert len(text.split()) >= 600
    assert re.findall(r"^## Exercise (\d):", text, re.MULTILINE) == list("123456")
    assert "\u2014" not in text


def test_corpus_does_not_confuse_class_or_text_with_identity() -> None:
    module = reference("nlp-001")
    rows = [
        {"id": "a", "family": "f", "text": "same", "label": "x"},
        {"id": "b", "family": "f", "text": "same", "label": "x"},
    ]
    assert module.validate_corpus(rows) == 2
    rows[1]["id"] = "a"
    with pytest.raises(ValueError, match="Duplicate"):
        module.validate_corpus(rows)


def test_span_check_does_not_silently_clip_invalid_or_boolean_offsets() -> None:
    module = reference("nlp-002")
    for start, end in ((-1, 2), (0, 99), (2, 1), (False, 2)):
        with pytest.raises(ValueError):
            module.checked_span("word", start, end)
    assert module.checked_span("word", 1, 3) == "or"


def test_extraction_keeps_leading_zeroes_and_does_not_authorize_actions() -> None:
    module = reference("nlp-003")
    assert module.extract_invoices("Do not pay INV-0012")[0]["id"] == "INV-0012"
    assert module.extract_invoices("INV-0000 INV-12345 _INV-1234 INV-１２３４") == []
    assert module.exact_metrics(set(), {("doc", 0, 8, "INV-1234")}) == {
        "tp": 0,
        "fp": 0,
        "fn": 1,
        "precision": None,
        "recall": 0.0,
    }


def test_bpe_rejects_invalid_training_and_preserves_supported_round_trips() -> None:
    module = reference("nlp-004")
    for words, steps in (
        ({}, 2),
        ({"low": 0}, 2),
        ({"low": True}, 2),
        ({"LOW": 1}, 2),
        ({"low": 1}, -1),
    ):
        with pytest.raises(ValueError):
            module.train_bpe(words, steps)
    for steps in (0, 1, 2, 10):
        model, _ = module.train_bpe({"low": 3, "lower": 1}, steps)
        for word in ("low", "lower", "row", "were"):
            assert module.decode(module.encode(word, model)) == word
    with pytest.raises(ValueError):
        module.decode(("low",))
