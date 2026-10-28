#!/usr/bin/env python3
"""Read-only static and syntax checks through the prepared offline toolchain.

This does not compile or execute lesson programs, resolve dependencies, contact a
SQL server, or replace the repository's compiler and runtime test suites.
"""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import re
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.format_repo import LANGUAGES, batches, inventory  # noqa: E402
from scripts.sql_formatting import sql_for_parser as sql_for_parser  # noqa: E402

GRAMMARS = {
    "c": "c",
    "cpp": "cpp",
    "cuda": "cuda",
    "php": "php",
    "csharp": "csharp",
    "go": "go",
    "rust": "rust",
    "swift": "swift",
    "java": "java",
    "docker": "dockerfile",
    "cmake": "cmake",
}
WEB_GRAMMARS = {
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".tsx": "tsx",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".jsonc": "json",
}
JAVASCRIPT_SUFFIXES = {".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx"}
QUALITY_ROOTS = ("src/", "scripts/", "tests/", "bridge/", "python/professional/")


def run(command: list[str], root: Path) -> bool:
    try:
        result = subprocess.run(command, cwd=root, check=False)
    except FileNotFoundError:
        print(f"Missing lint tool: {command[0]}. Use ./scripts/lint-repo.", file=sys.stderr)
        return False
    return result.returncode == 0


def grammar_source(path: str, source: bytes, grammar: str) -> tuple[str, bytes]:
    """Project the standard C++ linkage guards of interoperable C headers.

    Tree-sitter does not evaluate preprocessor branches and cannot join an
    opening extern-C brace to its separately guarded closing brace. Checking the
    complete __cplusplus branch avoids that parser limitation. Actual C and C++
    header compilation remains covered by the separate compiler tests.
    """
    if grammar == "c" and Path(path).suffix == ".h" and b'extern "C"' in source:
        pattern = rb"(?m)^[ \t]*#ifdef[ \t]+__cplusplus[ \t]*\n(.*?)^[ \t]*#endif[^\n]*"
        projected, count = re.subn(
            pattern,
            lambda match: b"\n" + match.group(1) + b"\n",
            source,
            flags=re.DOTALL,
        )
        if count:
            return "cpp", projected
    return grammar, source


def grammar_errors(path: str, source: bytes, grammar: str) -> list[str]:
    package = importlib.import_module("tree_sitter_language_pack")
    grammar, source = grammar_source(path, source, grammar)
    tree = package.get_parser(grammar).parse(source)
    errors: list[str] = []
    pending: list[Any] = [tree.root_node]
    while pending:
        node = pending.pop()
        if node.is_error or node.is_missing:
            errors.append(f"{path}:{node.start_point[0] + 1}: {grammar} syntax error ({node.type})")
        else:
            pending.extend(reversed(node.children))
    return errors


def syntax_errors(path: str, root: Path, language: str) -> list[str]:
    source = (root / path).read_bytes()
    suffix = Path(path).suffix.lower()
    try:
        if language == "python" and suffix != ".ipynb":
            ast.parse(source, filename=path)
        elif language == "python":
            notebook = json.loads(source)
            if not isinstance(notebook, dict) or not isinstance(notebook.get("cells"), list):
                raise ValueError("Notebook must contain a cells list")
            for cell in notebook["cells"]:
                if not isinstance(cell, dict) or cell.get("cell_type") not in {
                    "code",
                    "markdown",
                    "raw",
                }:
                    raise ValueError("Invalid notebook cell")
                content = cell.get("source")
                if not isinstance(content, str) and not (
                    isinstance(content, list) and all(isinstance(line, str) for line in content)
                ):
                    raise ValueError("Notebook cell source must be text")
        elif language == "sql":
            parser = importlib.import_module("pglast")
            parser.parse_sql(sql_for_parser(source.decode("utf-8")))
        elif language == "r":
            result = subprocess.run(
                ["Rscript", "--vanilla", str(root / "scripts/r_source_tools.R"), "parse"],
                input=source,
                cwd=root,
                capture_output=True,
                check=False,
            )
            if result.returncode:
                diagnostic = result.stderr.decode("utf-8", errors="replace")
                return [f"{path}: {diagnostic.strip() or 'R parser rejected source'}"]
        elif suffix == ".json":
            json.loads(source)
        elif suffix in {".yaml", ".yml"}:
            yaml = importlib.import_module("yaml")
            list(yaml.compose_all(source, Loader=yaml.SafeLoader))
        elif language == "toml":
            tomllib.loads(source.decode("utf-8"))
        elif language == "xml":
            ET.fromstring(source)
        elif language in GRAMMARS:
            return grammar_errors(path, source, GRAMMARS[language])
        elif language == "web" and suffix in WEB_GRAMMARS:
            return grammar_errors(path, source, WEB_GRAMMARS[suffix])
    except (SyntaxError, ValueError, UnicodeError, ET.ParseError) as exc:
        return [f"{path}: {exc}"]
    except Exception as exc:
        # Optional parsers use their own error classes. Dependency/import errors
        # must fail visibly too; never silently skip an unavailable language.
        return [f"{path}: {type(exc).__name__}: {exc}"]
    return []


def lint_group(language: str, paths: list[str], root: Path) -> bool:
    success = True
    for path in paths:
        # Swift and Scala use their own parsers below because Tree-sitter rejects
        # valid result-builder and inline-lambda syntax in the taught dialects.
        if language in {"swift", "scala", "r", "julia", "stan", "dbt"}:
            continue
        for error in syntax_errors(path, root, language):
            print(error, file=sys.stderr)
            success = False
    if language == "dbt":
        for path in paths:
            result = subprocess.run(
                [sys.executable, str(root / "scripts/dbt_source_tools.py"), "lint"],
                input=(root / path).read_bytes(),
                cwd=root,
                capture_output=True,
                check=False,
            )
            if result.returncode:
                print(
                    path + ": " + result.stderr.decode("utf-8", errors="replace"), file=sys.stderr
                )
                success = False
    elif language in {"julia", "stan"}:
        command = (
            [
                "julia",
                "--startup-file=no",
                "--compiled-modules=existing",
                "--project=/opt/julia-env",
                str(root / "scripts/julia_source_tools.jl"),
                "lint",
            ]
            if language == "julia"
            else [sys.executable, str(root / "scripts/stan_source_tools.py"), "lint"]
        )
        for path in paths:
            try:
                result = subprocess.run(
                    command,
                    input=(root / path).read_bytes(),
                    cwd=root,
                    capture_output=True,
                    check=False,
                )
            except FileNotFoundError:
                print("Missing prepared language tool. Use ./scripts/lint-repo.", file=sys.stderr)
                return False
            if result.returncode:
                print(
                    path + ": " + result.stderr.decode("utf-8", errors="replace"), file=sys.stderr
                )
                success = False
    elif language == "r":
        for path in paths:
            try:
                result = subprocess.run(
                    ["Rscript", "--vanilla", str(root / "scripts/r_source_tools.R"), "lint"],
                    input=(root / path).read_bytes(),
                    cwd=root,
                    capture_output=True,
                    check=False,
                )
            except FileNotFoundError:
                print("Missing Rscript. Use ./scripts/lint-repo.", file=sys.stderr)
                return False
            if result.returncode:
                diagnostic = (result.stdout + result.stderr).decode("utf-8", errors="replace")
                print(f"{path}: {diagnostic.strip()}", file=sys.stderr)
                success = False
    elif language == "python":
        notebooks = [path for path in paths if path.endswith(".ipynb")]
        for batch in batches(notebooks):
            # Ruff understands IPython/JupySQL magics. Unfinished exercises are
            # intentionally not subjected to production-code unused-name rules.
            success = (
                run(["ruff", "check", "--isolated", "--no-cache", "--select", "E9", *batch], root)
                and success
            )
        quality = [
            path
            for path in paths
            if path.startswith(QUALITY_ROOTS) or path == "docker/init_module_runtime.py"
        ]
        for batch in batches(quality):
            success = (
                run(
                    [
                        "ruff",
                        "check",
                        "--no-cache",
                        "--config",
                        str(root / "pyproject.toml"),
                        *batch,
                    ],
                    root,
                )
                and success
            )
    elif language == "web":
        programs = [path for path in paths if Path(path).suffix.lower() in JAVASCRIPT_SUFFIXES]
        for batch in batches(programs):
            success = (
                run(
                    [
                        "eslint",
                        "--no-config-lookup",
                        "--no-ignore",
                        "--max-warnings",
                        "0",
                        "--config",
                        str(root / "docker/formatting/eslint.config.mjs"),
                        *batch,
                    ],
                    root,
                )
                and success
            )
    elif language == "shell":
        for batch in batches(paths):
            success = (
                run(["shellcheck", "--norc", "--severity=warning", "--shell=bash", *batch], root)
                and success
            )
    elif language in {"scala", "swift"}:
        for path in paths:
            if language == "scala":
                command = [
                    "scalafmt",
                    "--config",
                    str(root / "docker/formatting/scalafmt.conf"),
                    "--non-interactive",
                    "--stdin",
                    "--stdout",
                    "--assume-filename",
                    path,
                ]
            else:
                command = [
                    "swift-format",
                    "format",
                    "--configuration",
                    str(root / "docker/formatting/swift-format.json"),
                ]
            try:
                result = subprocess.run(
                    command,
                    input=(root / path).read_bytes(),
                    cwd=root,
                    capture_output=True,
                    check=False,
                )
                if result.returncode:
                    print(
                        f"{path}: {result.stderr.decode('utf-8', errors='replace')}",
                        file=sys.stderr,
                    )
                    success = False
            except FileNotFoundError:
                print(f"Missing {command[0]}. Use ./scripts/lint-repo.", file=sys.stderr)
                return False
    return success


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=LANGUAGES, action="append")
    parser.add_argument(
        "--exclude-language", choices=LANGUAGES, action="append", default=[], help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--list", action="store_true", help="List source coverage without running lint"
    )
    arguments = parser.parse_args(argv)
    groups, excluded, unmanaged = inventory(ROOT)
    # Markdown is formatted separately and checked by the content pipeline.
    # Its deliberately partial snippets are not standalone source programs.
    if "web" in groups:
        groups["web"] = [path for path in groups["web"] if Path(path).suffix.lower() != ".md"]
    selected = [
        language
        for language in LANGUAGES
        if (not arguments.language or language in arguments.language)
        and language not in arguments.exclude_language
    ]
    print(
        "Static/syntax coverage: "
        + ", ".join(f"{language}={len(groups.get(language, []))}" for language in selected),
        flush=True,
    )
    print(
        f"Preserved generated/vendor/evidence files: {len(excluded)}; "
        f"other file types: {len(unmanaged)}",
        flush=True,
    )
    if arguments.list:
        for language in selected:
            for path in groups.get(language, []):
                print(f"LINT [{language}] {path}")
        for path, reason in excluded.items():
            print(f"PRESERVE {path}: {reason}")
        return 0
    success = True
    for language in selected:
        paths = groups.get(language, [])
        if paths:
            print(f"Checking {language}: {len(paths)} files", flush=True)
            success = lint_group(language, paths, ROOT) and success
    print(
        "SQL checks parse statements with placeholder variables. They do not evaluate "
        "psql branches, included files, dynamic SQL or procedural bodies."
    )
    print(
        "Grammar checks do not prove type checking, linking, runtime behavior or "
        "lesson correctness. Markdown fences retain their authoring contracts."
    )
    print("Lint checks passed." if success else "Lint failed; see diagnostics above.")
    return 0 if success else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Lint error: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
