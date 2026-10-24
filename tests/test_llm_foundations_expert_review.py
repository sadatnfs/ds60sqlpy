"""Regression guards and sequential worked programs for reviewed LLM experts."""

from __future__ import annotations

import re
import runpy
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/llm-theory"


@pytest.mark.parametrize("lesson", [43, 46])
@pytest.mark.parametrize("variant", ["reference", "worked"])
@pytest.mark.parametrize("case", ["overflow", "zero_width"])
def test_attention_refuses_undefined_scores(lesson: int, variant: str, case: str) -> None:
    key = f"llm-{lesson:03d}"
    namespace: dict[str, Any]
    if variant == "reference":
        namespace = runpy.run_path(str(BASE / "solutions" / (key + "_solution.py")))
    else:
        blocks = re.findall(
            r"```python\n(.*?)```", (BASE / "guides" / (key + ".md")).read_text(), re.S
        )
        namespace = {}
        exec(compile("\n\n".join(blocks), key + "-worked", "exec"), namespace)
    width = 0 if case == "zero_width" else 1
    q = np.full((1, width), 1e308)
    k = q.copy()
    v = np.ones((1, 1))
    allowed = np.ones((1, 1), dtype=bool)
    functions = (
        [namespace["attention"]]
        if lesson == 43
        else [namespace["dense"], lambda *args: namespace["online_attention"](*args, 1)]
    )
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        for function in functions:
            with pytest.raises(ValueError), np.errstate(all="raise"):
                function(q, k, v, allowed)
    assert not recorded


@pytest.mark.parametrize("lesson", [43, 46])
def test_repaired_helper_keeps_nonuniform_finite_oracle(lesson: int) -> None:
    namespace = runpy.run_path(str(BASE / "solutions" / f"llm-{lesson:03d}_solution.py"))
    q = np.array([[1.0, 0.0]])
    k = np.array([[1.0, 0.0], [0.0, 1.0]])
    v = np.array([[2.0, 0.0], [0.0, 2.0]])
    allowed = np.ones((1, 2), dtype=bool)
    weight = 1 / (1 + np.exp(-1 / np.sqrt(2)))
    expected = np.array([[2 * weight, 2 * (1 - weight)]])
    if lesson == 43:
        result, _ = namespace["attention"](q, k, v, allowed)
    else:
        result, _ = namespace["online_attention"](q, k, v, allowed, 1)
        np.testing.assert_allclose(
            namespace["dense"](q, k, v, allowed), expected, rtol=0, atol=1e-12
        )
    np.testing.assert_allclose(result, expected, rtol=0, atol=1e-12)


def _final_numeric_namespace(lesson: int, variant: str) -> dict[str, Any]:
    identity = f"llm-{lesson:03d}"
    if variant == "reference":
        return runpy.run_path(str(BASE / "solutions" / f"{identity}_solution.py"))
    blocks = re.findall(
        r"```python\n(.*?)```", (BASE / "guides" / f"{identity}.md").read_text(), re.S
    )
    namespace: dict[str, Any] = {}
    exec(compile("\n\n".join(blocks), identity + "-worked", "exec"), namespace)
    return namespace


@pytest.mark.parametrize("variant", ["reference", "worked"])
@pytest.mark.parametrize("operation", ["online_row", "online_attention"])
def test_online_attention_rejects_nonfinite_value_accumulation(
    variant: str, operation: str
) -> None:
    namespace = _final_numeric_namespace(46, variant)
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        with (
            pytest.raises(ValueError, match="finite online attention accumulators"),
            np.errstate(all="raise"),
        ):
            if operation == "online_row":
                namespace[operation]([0.0, 0.0, 1000.0], [[1e308], [1e308], [1.0]], 2)
            else:
                namespace[operation](
                    np.zeros((1, 1)),
                    np.zeros((2, 1)),
                    np.full((2, 1), 1e308),
                    np.ones((1, 2), dtype=bool),
                    2,
                )
    assert not recorded
    # The refusal is about the online representation's intermediate range,
    # not a claim that this average has no representable mathematical answer.
    dense = namespace["dense"](
        np.zeros((1, 1)),
        np.zeros((2, 1)),
        np.full((2, 1), 1e308),
        np.ones((1, 2), dtype=bool),
    )
    np.testing.assert_array_equal(dense, [[1e308]])
    single, _ = namespace["online_row"]([0.0], [[1e308]], 1)
    np.testing.assert_array_equal(single, [1e308])


@pytest.mark.parametrize("variant", ["reference", "worked"])
@pytest.mark.parametrize(
    ("probability", "uniform", "expected"),
    [
        (np.r_[np.full(10, 0.1), 0.0], float(np.nextafter(1.0, 0.0)), 9),
        (np.r_[0.0, np.full(10, 0.1)], float(np.nextafter(1.0, 0.0)), 10),
        (np.array([0.0, 0.5, 0.0, 0.5, 0.0]), 0.0, 1),
        (np.array([0.0, 0.5, 0.0, 0.5, 0.0]), float(np.nextafter(0.5, 0.0)), 1),
        (np.array([0.0, 0.5, 0.0, 0.5, 0.0]), 0.5, 3),
        (np.array([0.0, 0.0, 1.0, 0.0]), float(np.nextafter(1.0, 0.0)), 2),
    ],
)
def test_speculative_draw_never_assigns_mass_to_zero_support(
    variant: str, probability: Any, uniform: float, expected: int
) -> None:
    draw = _final_numeric_namespace(48, variant)["draw"]
    actual = draw(probability, uniform)
    assert actual == expected and probability[actual] > 0


@pytest.mark.parametrize("variant", ["reference", "worked"])
def test_zero_support_padding_preserves_token_identity_and_speculative_round(variant: str) -> None:
    namespace = _final_numeric_namespace(48, variant)
    probability = np.array([0.2, 0.3, 0.5])
    expanded = np.array([0.0, 0.2, 0.0, 0.3, 0.5, 0.0])
    identity = [1, 3, 4]
    for uniform in [0.0, 0.1, 0.2, 0.49, 0.5, 0.9, float(np.nextafter(1.0, 0.0))]:
        assert (
            namespace["draw"](expanded, uniform)
            == identity[namespace["draw"](probability, uniform)]
        )
    distribution = np.r_[np.full(10, 0.1), 0.0]
    result = namespace["speculative_round"](
        [],
        lambda _: distribution,
        lambda _: distribution,
        [float(np.nextafter(1.0, 0.0))],
        [0.5],
        0.1,
        budget=1,
    )
    assert result["tokens"] == [9] and result["accepted_count"] == 1
