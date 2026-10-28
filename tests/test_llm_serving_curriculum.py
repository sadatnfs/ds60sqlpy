"""Chapter contracts and independent numerical mechanisms; real workers are separate."""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from ds60sqlpy.lesson_reader import LinkResolver, render_markdown

ROOT = Path(__file__).resolve().parents[1]
FRAGMENT = ROOT / "courses/data-ml-engineering/authoring/serving"


def program(number: int) -> dict[str, Any]:
    return runpy.run_path(str(FRAGMENT / "examples" / f"dme-{number:03}.py"))


def test_sixteen_complete_chapters_render_math_and_exact_code() -> None:
    records = json.loads((FRAGMENT / "chapters.json").read_text())
    assert [row["id"] for row in records] == [f"dme-{number:03}" for number in range(57, 73)]
    math_count = 0
    for row in records:
        path = ROOT / row["guide_source"]
        source = path.read_text()
        code = (ROOT / row["source_path"]).read_text()
        assert source.startswith(f"# {row['id']}: {row['title']}\n")
        assert source.count("<!-- worked-program -->") == 1
        assert source.count("## Worked case 1:") == source.count("## Worked case 2:") == 1
        assert len(source.split()) >= 1000
        assert chr(0x2014) not in source
        assembled = source.replace("<!-- worked-program -->", "```python\n" + code + "```")
        rendered = render_markdown(
            assembled, resolver=LinkResolver(repo_root=ROOT, source_path=path, targets={})
        )
        assert "math-source" not in rendered
        assert "language-python" in rendered
        math_count += rendered.count("<math ")
        for related in row["related_paths"]:
            assert (ROOT / related["path"]).is_file()
    assert math_count >= 100


@pytest.mark.parametrize("number", [number for number in range(57, 73) if number not in {61, 63}])
def test_complete_core_worked_cases(number: int) -> None:
    program(number)["main"]()


def test_attention_online_softmax_against_direct_reference() -> None:
    calculate = program(66)["online_attention"]
    generator = np.random.default_rng(2026)
    for count in (1, 3, 7, 11):
        scores = generator.normal(size=count) * 20 + 1000
        vectors = generator.normal(size=(count, 4))
        weights = np.exp(scores - scores.max())
        reference = (weights / weights.sum()) @ vectors
        for tile in range(1, count + 1):
            np.testing.assert_allclose(
                calculate(scores, vectors, tile), reference, rtol=1e-12, atol=1e-12
            )


def test_sampling_shift_invariance_and_support() -> None:
    distribution = program(64)["distribution"]
    a = distribution([1.0, 3.0, -2.0, 5.0], 0.7, 3)
    b = distribution([1001.0, 1003.0, 998.0, 1005.0], 0.7, 3)
    np.testing.assert_allclose(a, b, atol=1e-12)
    assert a[2] == 0 and abs(a.sum() - 1) < 1e-12
    np.testing.assert_array_equal(distribution([1.0, 2.0, 3.0], 1.0, 1), [0.0, 0.0, 1.0])


def test_sse_all_bytes_preserve_literal_markup() -> None:
    scope = program(69)
    value = '<img src="x" onerror="alert(1)">é🙂'
    raw = scope["encode"](1, value)
    assert scope["parse"]([bytes([byte]) for byte in raw]) == [(1, value)]


def test_fifo_round_robin_distinct_latency_objectives() -> None:
    scope = program(65)
    lengths = {"a": 1, "b": 4, "c": 2}
    first, finish = scope["round_robin"](lengths)
    assert first == {"a": 1, "b": 2, "c": 3}
    assert finish == {"a": 1, "c": 5, "b": 7}
    assert scope["sequential"](lengths)[1] == {"a": 1, "b": 5, "c": 7}
