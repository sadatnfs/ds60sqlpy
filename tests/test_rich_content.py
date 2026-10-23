from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

import pytest

from ds60sqlpy.lesson_reader import (
    LinkResolver,
    _clean_generated_html,
    render_artifact,
    render_inline,
    render_markdown,
)
from ds60sqlpy.reader_content import highlight_source, render_code_block, rich_content_styles
from ds60sqlpy.reader_math import render_math


class TextAndTags(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text: list[str] = []
        self.tags: list[str] = []
        self.attrs: list[tuple[str, str | None]] = []

    def handle_data(self, data: str) -> None:
        self.text.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        self.attrs.extend(attrs)


def parse(document: str) -> TextAndTags:
    result = TextAndTags()
    result.feed(document)
    return result


def resolver(tmp_path: Path) -> LinkResolver:
    return LinkResolver(repo_root=tmp_path, source_path=tmp_path / "lesson.md", targets={})


@pytest.mark.parametrize(
    ("language", "source"),
    [
        ("python", 'import numpy as np\n# sample\nx = "<script>"\nprint(x + 2)\n'),
        ("sql", "SELECT customer_id, COUNT(*) FROM orders WHERE status = 'paid';"),
        ("cpp", '#include <iostream>\nint main() { std::cout << "hello"; }'),
        ("java", "public class Main { public static void main(String[] args) { } }"),
        ("javascript", 'const message = "hello"; console.log(message);'),
        ("typescript", "const count: number = 3;"),
        ("scala", "val count: Int = 3; println(count)"),
        ("yaml", "apiVersion: v1\nkind: Pod\nspec:\n  replicas: 2"),
        ("json", '{"value": 42, "safe": true}'),
        ("bash", 'echo "$HOME" # not executed'),
        ("powershell", 'Write-Output "hello"'),
        ("dockerfile", "FROM python:3.12\nRUN echo hello"),
        ("c", "int main(void) { return 0; }"),
        ("rust", 'fn main() { println!("hello"); }'),
        ("r", "values <- c(1, 2, 3)"),
        ("html", '<script>alert("do not run")</script>'),
        ("css", "body { color: blue; }"),
        ("c#", 'public class Program { static void Main() { Console.WriteLine("Hello"); } }'),
        ("f#", 'let square x = x * x\nprintfn "%d" (square 3)'),
        ("toml", "[settings]\nport = 8765"),
    ],
)
def test_fenced_languages_are_highlighted_copy_faithfully_and_escaped(
    language: str, source: str
) -> None:
    document = render_code_block(source, language)
    decoded = parse(document)
    assert "".join(decoded.text) == source
    assert 'class="syntax-' in document
    assert set(decoded.tags) <= {"pre", "code", "span"}
    assert all(name == "class" for name, _value in decoded.attrs)


@pytest.mark.parametrize("language", ["future-language", "text", '"><script>alert(1)</script>'])
def test_unknown_or_unsafe_language_is_visible_plain_text(language: str) -> None:
    source = '<script>x</script> & "literal"\n$12\n'
    document = render_code_block(source, language)
    assert "".join(parse(document).text) == source
    assert "syntax-" not in document
    assert "<script>" not in document


def test_line_numbered_source_preserves_blank_lines_tabs_and_trailing_newline() -> None:
    source = 'def example():\n\treturn """one\ntwo"""\n\n'
    document = render_code_block(source, "python", line_numbers=True)
    assert "".join(parse(document).text) == source
    assert document.count('class="source-line"') == 5
    assert "syntax-string" in document


def test_large_source_remains_complete_without_lexer_work() -> None:
    source = "x = 1\n" * 40_000
    assert "".join(parse(highlight_source(source, "python")).text) == source


@pytest.mark.parametrize(
    "expression",
    [
        r"\widehat{\Delta}=\bar{x}_A-\bar{x}_B",
        r"\operatorname{SE}(\widehat{\Delta})=\sqrt{\frac{s_A^2}{n_A}+\frac{s_B^2}{n_B}}",
        r"\mathbb{E}[X]=\sum_{i=1}^{n}x_i p_i",
        (
            r"\operatorname{Attention}(Q,K,V)=\operatorname{softmax}"
            r"\left(\frac{QK^{\mathsf T}}{\sqrt{d_k}}\right)V"
        ),
        r"\begin{bmatrix}1&2\\3&4\end{bmatrix}",
        r"\begin{aligned}a&=b+c\\d&=e+f\end{aligned}",
        r"f(x)=\begin{cases}x^2&x>0\\0&x\leq 0\end{cases}",
    ],
)
def test_textbook_notation_has_native_mathml_and_original_accessible_annotation(
    expression: str,
) -> None:
    document = render_math(expression, display=True)
    assert "math-source" not in document
    root = ElementTree.fromstring(document)
    annotation = root.find(".//{http://www.w3.org/1998/Math/MathML}annotation")
    assert annotation is not None and annotation.text == expression
    assert 'display="block"' in document


@pytest.mark.parametrize(
    "expression",
    [
        r"\href{javascript:alert(1)}{x}",
        r"\htmlClass{malicious}{x}",
        r"\text{</mtext><img src=x onerror=alert(1)><mtext>}",
        r"\text{</mtext><script>alert(1)</script><mtext>}",
        r"\color{red; background:url(https://example.com)}x",
    ],
)
def test_math_cannot_introduce_html_attributes_urls_or_active_content(expression: str) -> None:
    document = render_math(expression)
    decoded = parse(document)
    assert not ({"script", "img", "a", "style"} & set(decoded.tags))
    assert not any(
        name.startswith("on") or name in {"href", "src", "style"} for name, _ in decoded.attrs
    )
    assert "math-source" in document


def test_math_text_preserves_angle_brackets_and_ampersand_without_html() -> None:
    document = render_math(r"\text{A & B <script>not HTML</script>}")
    assert "<math" in document
    assert "<script>" not in document
    root = ElementTree.fromstring(document)
    text = root.find(".//{http://www.w3.org/1998/Math/MathML}mtext")
    assert (
        text is not None
        and (text.text or "").replace("\xa0", " ") == "A & B <script>not HTML</script>"
    )


def test_math_delimiters_do_not_change_code_currency_links_or_emphasis(tmp_path: Path) -> None:
    value = resolver(tmp_path)
    source = r"**Mean** \(\bar{x}\); $x_i^2$; cost $5 or $10. `**x** $x$ \(x\)` [help](https://example.com)."
    document = render_inline(source, value)
    assert document.count("<math ") == 2
    assert "<strong>Mean</strong>" in document
    assert "cost $5 or $10." in document
    assert "<code>**x** $x$ \\(x\\)</code>" in document
    assert 'href="https://example.com"' in document
    assert (
        render_inline("**`pip` installs**", value) == "<strong><code>pip</code> installs</strong>"
    )


@pytest.mark.parametrize("opening,closing", [(r"\[", r"\]"), ("$$", "$$")])
def test_display_equations_keep_paragraphs_and_tables_separate(
    tmp_path: Path, opening: str, closing: str
) -> None:
    source = (
        f"Before.\n{opening}\n\\frac{{1}}{{2}}\n{closing}\nAfter.\n\n"
        "| Name | Value |\n| --- | --- |\n| Bars | \\(P(A|B)\\) |\n| Code | `a|b` |"
    )
    document = render_markdown(source, resolver=resolver(tmp_path))
    assert '<p>Before.</p>\n<div class="math-display">' in document
    assert "</div>\n<p>After.</p>" in document
    assert document.count("<td>") == 4
    assert "<mfrac>" in document
    assert "<code>a|b</code>" in document


def test_fences_and_malformed_delimiters_remain_source(tmp_path: Path) -> None:
    source = '```python\nvalue = "\\(x^2\\) $$x$$"\n```\n\nUnclosed \\(x.\n\n\\[\nx+1'
    document = render_markdown(source, resolver=resolver(tmp_path))
    assert "<math" not in document
    assert 'value = "\\(x^2\\) $$x$$"' in "".join(parse(document).text)
    assert "Unclosed \\(x." in document


def test_notebook_language_metadata_and_sql_magic_are_highlighted(tmp_path: Path) -> None:
    notebook = tmp_path / "java.ipynb"
    notebook.write_text(
        json.dumps(
            {
                "metadata": {"language_info": {"name": "java"}},
                "cells": [
                    {"cell_type": "code", "source": "public class Main {}", "outputs": []},
                    {"cell_type": "code", "source": "%%sql\nSELECT 1;", "outputs": []},
                ],
            }
        )
    )
    document = render_artifact(notebook, repo_root=tmp_path, targets={})
    assert "language-java" in document and "language-sql" in document
    assert "syntax-keyword" in document


def test_shared_css_needs_no_external_resource() -> None:
    css = rich_content_styles()
    assert ".math-display" in css and ".syntax-keyword" in css
    assert "@import" not in css and "url(" not in css


@pytest.mark.parametrize("opening,closing", [("```", "````"), ("~~~~", "~~~~~")])
def test_fence_closure_requires_only_matching_markers(
    tmp_path: Path, opening: str, closing: str
) -> None:
    source = (
        opening
        + "text\n"
        + "literal \\(x^2\\) and $x$\n"
        + opening
        + "not-a-closing-fence\n"
        + "<!-- keep this source comment -->\n"
        + closing
        + "\nAfter \\(y^2\\)."
    )
    document = render_markdown(source, resolver=resolver(tmp_path))
    assert document.count("<math ") == 1
    assert opening + "not-a-closing-fence" in "".join(parse(document).text)
    assert "<!-- keep this source comment -->" in "".join(parse(document).text)
    assert "literal \\(x^2\\) and $x$" in "".join(parse(document).text)


def test_unterminated_fence_and_mismatched_markers_protect_the_rest_of_source(
    tmp_path: Path,
) -> None:
    source = "```text\nliteral \\(x^2\\)\n~~~\n<!-- keep comment -->\n$x$"
    document = render_markdown(source, resolver=resolver(tmp_path))
    assert "<math " not in document
    assert "".join(parse(document).text) == source.split("\n", 1)[1]


@pytest.mark.parametrize("language", ["text", "python", "future-language"])
def test_static_html_cleanup_keeps_code_line_ending_whitespace(language: str) -> None:
    source = "value = 1  \t\n\t\n# trailing comment  \nlast = 2  "
    rendered = render_code_block(source, language)
    cleaned = _clean_generated_html(rendered).removesuffix("\n")
    assert "".join(parse(cleaned).text) == source
    assert all(line == line.rstrip() for line in cleaned.splitlines())
