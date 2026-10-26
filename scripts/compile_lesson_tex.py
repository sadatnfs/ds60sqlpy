#!/usr/bin/env python3
"""Compile explicit lesson TeX at build time using the pinned offline compiler."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ds60sqlpy import lesson_reader  # noqa: E402
from ds60sqlpy._tex_cache_digest import TEX_CACHE_SHA256  # noqa: E402
from ds60sqlpy.catalog import Catalog  # noqa: E402
from ds60sqlpy.reader_math import _validate_source  # noqa: E402
from ds60sqlpy.reader_tex import expression_key, font_stylesheet  # noqa: E402


def collect(root: Path) -> list[dict[str, Any]]:
    """Use the actual Markdown/notebook parser, so code remains literal."""
    expressions: dict[str, dict[str, Any]] = {}

    def remember(expression: str, *, display: bool = False) -> str:
        _validate_source(expression)
        expressions[expression_key(expression, display)] = {
            "source": expression,
            "display": display,
        }
        return ""

    original = lesson_reader.render_math
    lesson_reader.render_math = remember
    try:
        catalog = Catalog.load(root)
        targets = lesson_reader.artifact_targets(catalog)
        paths = set(targets).union(lesson_reader.reference_source_paths(catalog))
        for path in sorted(paths):
            if path.suffix.lower() in {".md", ".ipynb"}:
                lesson_reader.render_artifact(path, repo_root=root, targets=targets)
    finally:
        lesson_reader.render_math = original
    return [expressions[key] for key in sorted(expressions)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="recompile and check all generated TeX bytes"
    )
    parser.add_argument(
        "--check-inputs", action="store_true", help="verify source coverage without invoking Node"
    )
    args = parser.parse_args()
    fonts = font_stylesheet()
    fonts_path = ROOT / "src/ds60sqlpy/assets/vendor/textbook/fonts.css"
    if (args.check or args.check_inputs) and (
        not fonts_path.is_file() or fonts_path.read_text("utf-8") != fonts
    ):
        print("Bundled font sheet is stale. Rebuild lesson TeX.")
        return 1
    inputs = collect(ROOT)
    serialized = json.dumps(inputs, ensure_ascii=False, separators=(",", ":")) + "\n"
    input_path = ROOT / "curriculum/tex-inputs.json"
    output_path = ROOT / "src/ds60sqlpy/assets/vendor/textbook/compiled-tex.json"
    if (args.check or args.check_inputs) and (
        not input_path.is_file() or input_path.read_text("utf-8") != serialized
    ):
        print("TeX inputs are stale. Run python scripts/compile_lesson_tex.py.")
        return 1
    if args.check_inputs:
        if (
            not output_path.is_file()
            or hashlib.sha256(output_path.read_bytes()).hexdigest() != TEX_CACHE_SHA256
        ):
            print("Compiled TeX integrity is stale. Run python scripts/compile_lesson_tex.py.")
            return 1
        print(f"TeX source coverage is current: {len(inputs)} distinct expression/mode pairs.")
        return 0
    result = subprocess.run(
        ["node", str(ROOT / "scripts/compile_lesson_tex.mjs")],
        input=serialized,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=120,
        check=True,
    )
    digest = hashlib.sha256(result.stdout.encode("utf-8")).hexdigest()
    digest_path = ROOT / "src/ds60sqlpy/_tex_cache_digest.py"
    digest_text = (
        '"""Generated TeX cache integrity binding; regenerate with compile_lesson_tex.py."""\n\n'
        + 'TEX_CACHE_SHA256 = "'
        + digest
        + '"\n'
    )
    if args.check:
        if not digest_path.is_file() or digest_path.read_text("utf-8") != digest_text:
            print("Compiled TeX integrity binding is stale. Rebuild lesson TeX.")
            return 1
        if not output_path.is_file() or output_path.read_text("utf-8") != result.stdout:
            print("Compiled TeX is stale. Run python scripts/compile_lesson_tex.py.")
            return 1
    else:
        input_path.write_text(serialized, "utf-8")
        output_path.write_text(result.stdout, "utf-8")
        digest_path.write_text(digest_text, "utf-8")
        fonts_path.write_text(fonts, "utf-8")
    print(f"Compiled TeX verified: {len(inputs)} expressions; offline HTML and accessible MathML.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
