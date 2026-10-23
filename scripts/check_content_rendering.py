#!/usr/bin/env python3
"""Reject unreadable authored math using the classroom's actual offline renderer.

Scope is the catalog's Markdown/notebook artifacts plus the recursive rendered
reference closure, including authored module guides and tutorial chapters. Code
is never executed. Only an explicitly supplied --report destination is written.
"""

from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from ds60sqlpy.catalog import Catalog  # noqa: E402
from ds60sqlpy.lesson_reader import (  # noqa: E402
    artifact_targets,
    reference_source_paths,
    render_artifact,
)


class _RenderedContent(HTMLParser):
    """Inspect generated nodes rather than guessing math syntax in source code."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.math_expressions = 0
        self.code_blocks = 0
        self.fallbacks: list[str] = []
        self._fallback: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "math":
            self.math_expressions += 1
        elif tag == "pre":
            self.code_blocks += 1
        elif tag == "code" and "math-source" in (dict(attrs).get("class") or "").split():
            self._fallback = []

    def handle_data(self, data: str) -> None:
        if self._fallback is not None:
            self._fallback.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "code" and self._fallback is not None:
            self.fallbacks.append("".join(self._fallback))
            self._fallback = None


def inspect_catalog(catalog: Catalog) -> dict[str, Any]:
    """Inspect exactly the text sources published by the reader generators."""
    targets = artifact_targets(catalog)
    paths = sorted(
        path
        for path in set(targets).union(reference_source_paths(catalog))
        if path.suffix.lower() in {".md", ".ipynb"}
    )
    failures: list[dict[str, Any]] = []
    math_count = 0
    code_blocks = 0
    for path in paths:
        relative = path.relative_to(catalog.repo_root).as_posix()
        try:
            document = render_artifact(path, repo_root=catalog.repo_root, targets=targets)
            content = _RenderedContent()
            content.feed(document)
            content.close()
        except (OSError, TypeError, ValueError, RecursionError) as exc:
            failures.append({"path": relative, "kind": "render_error", "detail": str(exc)})
            continue
        math_count += content.math_expressions
        code_blocks += content.code_blocks
        for index, source in enumerate(content.fallbacks, 1):
            failures.append(
                {
                    "path": relative,
                    "kind": "math_fallback",
                    "expression_index": index,
                    "source": source,
                }
            )
    return {
        "schema_version": 1,
        "scope": "Published catalog Markdown/notebooks and recursive rendered-reference sources",
        "files_checked": len(paths),
        "math_expressions": math_count,
        "code_blocks": code_blocks,
        "failure_count": len(failures),
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository source directory")
    parser.add_argument("--report", type=Path, help="optional JSON report destination")
    args = parser.parse_args(argv)
    try:
        report = inspect_catalog(Catalog.load(args.root.resolve()))
    except (KeyError, OSError, TypeError, ValueError, RecursionError) as exc:
        report = {
            "schema_version": 1,
            "files_checked": 0,
            "math_expressions": 0,
            "code_blocks": 0,
            "failure_count": 1,
            "failures": [
                {"path": "[source discovery]", "kind": "discovery_error", "detail": str(exc)}
            ],
        }
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print(
        f"Content rendering: {report['files_checked']} sources; "
        f"{report['math_expressions']} MathML expressions; "
        f"{report['code_blocks']} code/output blocks; {report['failure_count']} failures."
    )
    for failure in report["failures"]:
        detail = failure.get("source", failure.get("detail", ""))
        summary = " ".join(str(detail).split())[:200]
        print(f"- {failure['path']}: {failure['kind']}: {summary}")
    if report["failure_count"]:
        print(
            "Correct the authored LaTeX or render error before publishing. "
            "Code examples stay literal."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
