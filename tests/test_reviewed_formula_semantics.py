"""Complete equations must survive authoring, not merely parse as valid TeX."""

from __future__ import annotations

import json
import math
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree

import pytest

from ds60sqlpy.reader_math import render_math
from scripts.normalize_math_prose import normalize

ROOT = Path(__file__).resolve().parents[1]
RULES = json.loads((ROOT / "curriculum/math-prose.json").read_text())["rules"]
BY_SOURCE = {rule["source"]: rule for rule in RULES}


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("QK^T", r"QK^{\mathsf T}"),
        ("QWD^T", r"QWD^{\mathsf T}"),
        ("XB^T", r"XB^{\mathsf T}"),
        ("dL/dX=G+sGK^T", r"\frac{\partial L}{\partial X}=G+sGK^{\mathsf T}"),
        ("dL/dE=S^T G", r"\frac{\partial L}{\partial E}=S^{\mathsf T}G"),
        ("dL/dK=sX^T G", r"\frac{\partial L}{\partial K}=sX^{\mathsf T}G"),
        ("D=10,000", r"D=10{,}000"),
        ("L=-log p_y", r"L=-\log p_y"),
        ("r=y-X beta", r"r=y-X\beta"),
    ],
)
def test_reviewed_registry_preserves_the_complete_operation(source: str, expected: str) -> None:
    rule = BY_SOURCE[source]
    relative = rule.get("paths", ["guide.md"])[0]
    output, hits = normalize(f"The equation is {source}.", relative, RULES)
    assert output == rf"The equation is \({expected}\)."
    assert hits == {source: 1}


def test_transpose_superscript_belongs_to_the_final_factor() -> None:
    # Valid conversion alone accepted the old whole-product msup base.
    for source, factor in (("QK^T", "K"), ("QWD^T", "D"), ("XB^T", "B")):
        tree = ElementTree.fromstring(render_math(BY_SOURCE[source]["latex"]))
        powers = list(tree.iter("{http://www.w3.org/1998/Math/MathML}msup"))
        assert len(powers) == 1
        base = powers[0][0]
        assert base.tag.endswith("}mi")
        assert base.text == factor


def test_adam_powers_bind_to_beta_with_the_moment_subscript() -> None:
    for index in (1, 2):
        expression = BY_SOURCE[f"1-beta{index}^t"]["latex"]
        assert expression == rf"1-\beta_{index}^t"
        rendered = ElementTree.fromstring(render_math(expression))
        scripts = list(rendered.iter("{http://www.w3.org/1998/Math/MathML}msubsup"))
        assert len(scripts) == 1
        assert scripts[0][0].text == "β"
        assert scripts[0][1].text == str(index)
        assert scripts[0][2].text == "t"
    guide = (ROOT / "courses/llm-applied/guides/llm-applied-015.md").read_text()
    assert r"\(v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2\)" in guide
    assert "1-beta " not in guide


def test_incomplete_replacement_rules_cannot_reintroduce_the_reviewed_defects() -> None:
    fragments = {"D=10", "L=-log", "r=y-X", "1^t", "2^t", "dL/dE=S^T"}
    assert fragments.isdisjoint(BY_SOURCE)
    for rule in RULES:
        latex = rule.get("latex", "")
        assert r"\(" not in latex and r"\)" not in latex


def test_regex_anchors_are_authored_as_complete_code_literals() -> None:
    for relative in (
        "courses/javascript-typescript/authoring/specs.py",
        "courses/javascript-typescript/guides/js-008.md",
        "courses/javascript-typescript/solutions/js-008_solutions.md",
    ):
        source = (ROOT / relative).read_text()
        assert "Compare `/^.$/` and `/^.$/u` on one emoji." in source


def test_mathematical_typography_does_not_rewrite_a_runnable_example() -> None:
    source = """The equation is QWD^T.
```python
scores = queries @ projection @ documents.T
assert scores.shape == (3, 4)
```
`QWD^T` is literal shorthand in this code span.
"""
    relative = "courses/llm-applied/guides/llm-applied-020.md"
    output, _ = normalize(source, relative, RULES)
    assert output[output.index("```python") :] == source[source.index("```python") :]
    assert r"\(QWD^{\mathsf T}\)" in output


def test_bigram_mean_loss_averages_negative_logs_not_probabilities() -> None:
    probability_c_given_a = Fraction(1 + 1, 3 + 3)
    probability_b_given_c = Fraction(0 + 1, 0 + 3)
    mean_loss = -sum(map(math.log, (probability_c_given_a, probability_b_given_c))) / 2
    assert mean_loss == pytest.approx(math.log(3))
    guide = (ROOT / "courses/llm-theory/solutions/llm-014_solutions.md").read_text()
    assert "total negative log likelihood by two active targets" in guide


def test_reviewed_router_derivatives_have_independent_numerical_checks() -> None:
    def softmax(logits: list[float]) -> list[float]:
        weights = [math.exp(x - max(logits)) for x in logits]
        return [x / sum(weights) for x in weights]

    def derivative(
        function: Callable[[list[float]], float], point: list[float], index: int
    ) -> float:
        left, right = point.copy(), point.copy()
        left[index] -= 1e-6
        right[index] += 1e-6
        return (function(right) - function(left)) / 2e-6

    def mixture(z: list[float]) -> float:
        return sum(g * e for g, e in zip(softmax(z), (1, 2), strict=True))

    logits = [math.log(3), 0]
    assert [derivative(mixture, logits, j) for j in range(2)] == pytest.approx(
        [-3 / 16, 3 / 16], abs=1e-9
    )

    # Only one of four tokens is perturbed, with hard assignments held fixed.
    def auxiliary(z: list[float]) -> float:
        return 0.01 * 2 / 4 * sum(f * p for f, p in zip((0.75, 0.25), softmax(z), strict=True))

    logits = [math.log(0.7), math.log(0.3)]
    assert [derivative(auxiliary, logits, j) for j in range(2)] == pytest.approx(
        [0.000525, -0.000525], abs=1e-10
    )


def test_reviewed_gradient_accumulation_and_learning_rate_arithmetic() -> None:
    stored_gradient = -Fraction(56, 3) - Fraction(56, 45)
    assert stored_gradient == -Fraction(896, 45)
    assert Fraction(28, 15) - Fraction(1, 10) * stored_gradient == Fraction(868, 225)
    assert 1 - Fraction(28, 3) * Fraction(1, 10) == Fraction(1, 15)
    assert 1 - Fraction(28, 3) * Fraction(1, 4) == -Fraction(4, 3)


def test_online_attention_prose_keeps_sums_and_products_in_one_expression() -> None:
    guide = (ROOT / "courses/llm-theory/guides/llm-046.md").read_text()
    assert r"\(\ell=\sum_j\exp(s_j-m)\)" in guide
    assert r"\(n=\sum_j\exp(s_j-m)v_j\)" in guide
    assert r"\)*value" not in guide
    assert "denominator ell=sum" not in guide


def test_literal_api_mappings_preserve_complete_calls_and_fenced_source() -> None:
    relative = "courses/deep-learning-pytorch/guides/torch-023.md"
    source = "Call optimizer.zero_grad(set_to_none=True).\n```python\nloss.backward()\n```\n"
    output, _ = normalize(source, relative, RULES)
    assert output.startswith("Call `optimizer.zero_grad(set_to_none=True)`.")
    assert output[output.index("```python") :] == source[source.index("```python") :]
