"""Detailed NLP content and offline mechanism checks, independent of pretrained assets."""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import socket
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.checks import _markdown_link_text

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/nlp"
RECORDS = [
    record
    for record in json.loads((BASE / "lessons.json").read_text())["lessons"]
    if 5 <= int(record["id"].split("-")[-1]) <= 24
]
IDS = [f"nlp-{number:03d}" for number in range(5, 25)]


def reference(key: str) -> Any:
    path = BASE / "solutions" / f"{key}_solution.py"
    spec = importlib.util.spec_from_file_location(key.replace("-", "_"), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def refuse_network(*args: Any, **kwargs: Any) -> None:
    raise AssertionError("An offline NLP example attempted a network connection")


def test_advanced_inventory_retains_all_assigned_stable_ids() -> None:
    assert [record["id"] for record in RECORDS] == IDS
    plan = json.loads((BASE / "track.json").read_text())["lessons"]
    planned = {entry["id"]: entry for entry in plan}
    for record in RECORDS:
        assert record["runtime_profile"] == "python-core"
        assert record["verification_id"] is None
        guide = (ROOT / record["guide_path"]).read_text()
        for prerequisite in planned[record["id"]]["prerequisites"]:
            assert f"`{prerequisite}`" in guide


@pytest.mark.parametrize("record", RECORDS, ids=lambda record: record["id"])
def test_guides_scaffolds_and_explanations_are_complete(record: dict[str, Any]) -> None:
    guide = (ROOT / record["guide_path"]).read_text()
    assert len(guide.split()) >= 1400
    assert re.findall(r"^### Exercise ([1-6]):", guide, re.M) == list("123456")
    assert len(re.findall(r"^### Worked example", guide, re.M)) >= 2
    assert len(re.findall(r"```python\n", guide)) >= 2
    assert guide.count("**Interview:") >= 3
    assert "$guide-ds60sqlpy-learning" in guide
    assert record["source_path"] in guide and record["guide_path"] in guide
    assert guide.rfind("## Ask Codex about this lesson") > guide.rfind("## Exercises")
    learner = (ROOT / record["source_path"]).read_text()
    assert "NotImplementedError" in learner
    assert re.findall(r"# Exercise ([1-6]):", learner) == list("123456")
    executable = (ROOT / record["solution_paths"][0]).read_text()
    explanation = (ROOT / record["solution_paths"][1]).read_text()
    assert executable != learner
    assert len(explanation.split()) >= 600
    assert re.findall(r"^## Exercise ([1-6]):", explanation, re.M) == list("123456")
    for text in (guide, learner, executable, explanation):
        assert "\u2014" not in text
    tree = ast.parse(executable)
    assert sum(isinstance(node, ast.Assert) for node in ast.walk(tree)) >= 5
    assert 'if __name__ == "__main__":' in executable
    fixture = json.loads((BASE / "fixtures" / f"{record['id']}-cases.json").read_text())
    assert [case["exercise"] for case in fixture["cases"]] == list(range(1, 7))
    assert len({case["task"] for case in fixture["cases"]}) == 6
    for path in [ROOT / record["guide_path"], ROOT / record["solution_paths"][1]]:
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", _markdown_link_text(path.read_text())):
            if target.startswith(("https://", "http://", "#")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            assert resolved.is_relative_to(ROOT) and resolved.exists(), (path, target)


@pytest.mark.parametrize("record", RECORDS, ids=lambda record: record["id"])
def test_all_guide_blocks_and_references_execute_without_network(
    record: dict[str, Any], monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(socket.socket, "connect", refuse_network)
    monkeypatch.setattr(socket, "create_connection", refuse_network)
    monkeypatch.setenv("LOKY_MAX_CPU_COUNT", "2")
    namespace: dict[str, Any] = {}
    guide = (ROOT / record["guide_path"]).read_text()
    for block in re.findall(r"```python\n(.*?)\n```", guide, re.S):
        exec(compile(block, record["guide_path"], "exec"), namespace)
    reference(record["id"]).main()
    assert capsys.readouterr().out.strip()


@pytest.mark.parametrize(
    "key,original,broken",
    [
        ("nlp-006", "events=len(tokens)+1", "events=len(tokens)"),
        ("nlp-010", "candidates=dp[:,None]+lt", "candidates=np.zeros_like(lt)+lt"),
        (
            "nlp-011",
            "gold=set(gold);predicted=set(predicted)",
            "gold={(x[0],x[1],x[2]) for x in gold};predicted={(x[0],x[1],x[2]) for x in predicted}",
        ),
        ("nlp-015", "scores=np.where(mask[None,:],scores,-np.inf)", "scores=scores"),
        (
            "nlp-017",
            "sum(min(count,r[gram]) for gram,count in c.items())",
            "sum(count for gram,count in c.items() if gram in r)",
        ),
        ("nlp-020", "np.where(negative>positive,0,-1)", "np.where(negative>positive,0,0)"),
        ("nlp-023", "role in doc['roles'] and ", ""),
        ("nlp-024", "(?![0-9])", ""),
    ],
)
def test_reference_checks_reject_plausible_shortcuts(
    key: str, original: str, broken: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(socket.socket, "connect", refuse_network)
    source = (BASE / "solutions" / f"{key}_solution.py").read_text()
    assert original in source
    namespace: dict[str, Any] = {"__name__": "regression_probe"}
    exec(compile(source.replace(original, broken, 1), key, "exec"), namespace)
    with pytest.raises(AssertionError):
        namespace["main"]()


def test_probability_and_label_boundaries_reject_invalid_inputs() -> None:
    classifier = reference("nlp-009")
    with pytest.raises(ValueError):
        classifier.brier([1.2], [1])
    weak = reference("nlp-020")
    with pytest.raises(ValueError):
        weak.weak_summary([[1.5]])
    tagger = reference("nlp-015")
    with pytest.raises(ValueError):
        tagger.tag_loss([[1.0, 0.0]], [-100])
    with pytest.raises(ValueError):
        tagger.encode([[1.0, 0.0]], [False])
