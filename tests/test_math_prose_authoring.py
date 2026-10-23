"""Safety contracts for converting authored prose without altering runnable material."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "normalize_math_prose", ROOT / "scripts/normalize_math_prose.py"
)
assert SPEC and SPEC.loader
MIGRATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIGRATION)


def test_exact_math_preserves_programs_prompts_links_and_existing_tex() -> None:
    source = r"""The estimate is sqrt(a/b), and an existing formula is \(sqrt(a/b)\).
`value = sqrt(a/b)` stays literal.
[formula source](https://example.test/sqrt(a/b))
```python
value = sqrt(a/b)
print("sqrt(a/b)")
```
```text
Explain sqrt(a/b) in your own words.
```
"""
    output, hits = MIGRATION.normalize(
        source,
        "courses/example/guides/example-001.md",
        [{"source": "sqrt(a/b)", "latex": r"\sqrt{\frac{a}{b}}"}],
    )
    assert hits == {"sqrt(a/b)": 1}
    assert r"The estimate is \(\sqrt{\frac{a}{b}}\)" in output
    assert output[output.index("`value") :] == source[source.index("`value") :]
    assert r"\(sqrt(a/b)\)" in output


def test_longest_equation_wins_and_repeated_migration_is_stable() -> None:
    rules = [
        {"source": "sqrt(n)", "latex": r"\sqrt{n}"},
        {"source": "sigma/sqrt(n)", "latex": r"\frac{\sigma}{\sqrt{n}}"},
    ]
    source = "The SE is sigma/sqrt(n)."
    output, hits = MIGRATION.normalize(source, "guide.md", rules)
    assert hits == {"sigma/sqrt(n)": 1}
    assert output == r"The SE is \(\frac{\sigma}{\sqrt{n}}\)."
    assert MIGRATION.normalize(output, "guide.md", rules) == (output, {})


def test_scoped_rule_does_not_reinterpret_identifiers_or_other_subjects() -> None:
    rule = {"source": "log(2)", "latex": r"\log2", "paths": ["math.md"]}
    source = "log(2), catalog(2), api/log(2) and `log(2)`."
    unchanged, hits = MIGRATION.normalize(source, "code.md", [rule])
    assert unchanged == source and not hits
    output, hits = MIGRATION.normalize(source, "math.md", [rule])
    assert hits == {"log(2)": 1}
    assert "catalog(2), api/log(2)" in output


def test_notebook_code_outputs_and_metadata_are_preserved(tmp_path: Path) -> None:
    (tmp_path / "curriculum").mkdir()
    (tmp_path / "python").mkdir()
    (tmp_path / "curriculum/math-prose.json").write_text(
        json.dumps(
            {
                "rules": [{"source": "sqrt(n)", "latex": r"\sqrt{n}"}],
            }
        )
    )
    code: dict[str, Any] = {
        "cell_type": "code",
        "source": ["print('sqrt(n)')\n"],
        "execution_count": 3,
        "metadata": {"tags": ["keep"]},
        "outputs": [{"output_type": "stream", "name": "stdout", "text": ["sqrt(n)\n"]}],
    }
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {"language": "python"},
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": ["Scale by sqrt(n)."]},
            code,
        ],
    }
    path = tmp_path / "python/example.ipynb"
    path.write_text(json.dumps(notebook))
    report = MIGRATION.run(tmp_path, True)
    saved = json.loads(path.read_text())
    assert report["code_fences_and_notebook_code_unchanged"]
    assert saved["cells"][1] == code
    assert saved["metadata"] == notebook["metadata"]
    assert saved["cells"][0]["source"] == [r"Scale by \(\sqrt{n}\)."]
    assert MIGRATION.run(tmp_path, False)["files_changed"] == 0


def test_registry_has_unique_explicit_rules_and_valid_local_scopes() -> None:
    rules = json.loads((ROOT / "curriculum/math-prose.json").read_text())["rules"]
    sources = [r["source"] for r in rules]
    assert len(sources) == len(set(sources))
    assert all(source and "```" not in source for source in sources)
    for rule in rules:
        assert ("latex" in rule) != ("text" in rule)
        for relative in rule.get("paths", []):
            assert (ROOT / relative).is_file()
            assert (ROOT / relative).resolve().is_relative_to(ROOT)


def test_display_math_and_nested_fence_content_remain_exact() -> None:
    source = r"""\[
sqrt(n)
\]
````markdown
```python
sqrt(n)
```
````
Then sqrt(n).
"""
    output, hits = MIGRATION.normalize(
        source, "guide.md", [{"source": "sqrt(n)", "latex": r"\sqrt{n}"}]
    )
    assert hits == {"sqrt(n)": 1}
    assert output.startswith(source[: source.index("Then")])


def test_longer_closing_fence_and_unterminated_fence_protect_programs() -> None:
    rule = [{"source": "sqrt(n)", "latex": r"\sqrt{n}"}]
    for source in (
        "```python\nvalue = sqrt(n)\n````\n",
        "~~~python\nvalue = sqrt(n)\n~~~~~\n",
        "```python\nvalue = sqrt(n)\n",
    ):
        assert MIGRATION.normalize(source, "guide.md", rule) == (source, {})


def test_indented_programs_and_multiline_code_spans_remain_exact() -> None:
    rule = [{"source": "sqrt(n)", "latex": r"\sqrt{n}"}]
    for source in (
        "    value = sqrt(n)\n\n    print(value)\n",
        "\tvalue = sqrt(n)\n",
        "``call\nsqrt(n)\nwith `literal` ticks``",
    ):
        assert MIGRATION.normalize(source, "guide.md", rule) == (source, {})


def test_every_reviewed_latex_rule_is_supported_by_the_offline_renderer() -> None:
    from ds60sqlpy.reader_math import render_math

    rules = json.loads((ROOT / "curriculum/math-prose.json").read_text())["rules"]
    unsupported = [
        rule["source"]
        for rule in rules
        if "latex" in rule and 'class="math-source"' in render_math(rule["latex"])
    ]
    assert not unsupported
