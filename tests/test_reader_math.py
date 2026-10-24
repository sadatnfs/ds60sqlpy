from __future__ import annotations

from xml.etree import ElementTree

import pytest

from ds60sqlpy.reader_math import render_math


@pytest.mark.parametrize(
    ("expression", "tag", "text"),
    [
        (r"P(A\mid B)", "mo", "∣"),
        (r"P(\text{disease}\mid\text{positive})", "mtext", "disease"),
        ("R^2", "msup", ""),
        ("x_{12}", "msub", ""),
        ("x_1^2", "msubsup", ""),
        (r"\frac{1}{2}", "mfrac", ""),
        (r"\sqrt{4}", "msqrt", ""),
        (r"\mu=3", "mi", "μ"),
    ],
)
def test_supported_math_preserves_structure(expression: str, tag: str, text: str) -> None:
    rendered = render_math(expression)
    document = ElementTree.fromstring(rendered)
    nodes = list(document.iter("{http://www.w3.org/1998/Math/MathML}" + tag))

    assert nodes
    assert not text or any(node.text == text for node in nodes)
    annotation = document.find(".//{http://www.w3.org/1998/Math/MathML}annotation")
    assert annotation is not None and annotation.text == expression


@pytest.mark.parametrize("expression", [r"\unknown{a}", "a^^2", "{a", "}", "x" * 8193])
def test_unsupported_math_preserves_original_notation(expression: str) -> None:
    rendered = render_math(expression)

    assert rendered.startswith('<code class="math-source">')
    assert r"\(" in rendered and r"\)" in rendered
    assert "<math" not in rendered


def test_math_text_and_fallback_escape_html() -> None:
    supported = render_math(r"\text{<script>alert(1)</script>}")
    fallback = render_math(r"\unknown{<img src=x onerror=alert(1)>}")

    assert "<script>" not in supported and "&lt;script&gt;" in supported
    assert "<img" not in fallback and "&lt;img" in fallback
