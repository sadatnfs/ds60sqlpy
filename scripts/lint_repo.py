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
QUALITY_ROOTS = ("src/", "scripts/", "tests/", "bridge/", "python/professional/", "packages/")


def run(command: list[str], root: Path) -> bool:
    try:
        result = subprocess.run(command, cwd=root, check=False)
    except FileNotFoundError:
        print(f"Missing lint tool: {command[0]}. Use ./scripts/lint-repo.", file=sys.stderr)
        return False
    return result.returncode == 0


def _cpp_tokens(source: bytes) -> list[tuple[bytes, int, int]]:
    """Locate code tokens without interpreting comments or C++ string contents."""
    if len(source) > 2_000_000:
        raise ValueError("TMB syntax projection exceeds its source-size bound")
    raw_string = re.compile(rb'(?:u8|u|U|L)?R"([^ ()\\\t\r\n]{0,16})\(')
    identifier = re.compile(rb"[A-Za-z_][A-Za-z_0-9]*")
    number = re.compile(rb"[0-9][A-Za-z_0-9'.]*")
    tokens: list[tuple[bytes, int, int]] = []
    cursor = 0
    while cursor < len(source):
        start = cursor
        char = source[cursor : cursor + 1]
        if char.isspace():
            cursor += 1
            continue
        if source.startswith(b"//", cursor):
            while True:
                end = source.find(b"\n", cursor)
                if end < 0:
                    cursor = len(source)
                    break
                continued = source[cursor:end].rstrip(b"\r").endswith(b"\\")
                cursor = end + 1
                if not continued:
                    break
            continue
        if source.startswith(b"/*", cursor):
            end = source.find(b"*/", cursor + 2)
            if end < 0:
                raise ValueError("Unterminated comment in TMB source")
            cursor = end + 2
            continue
        if char == b"#" and not source[source.rfind(b"\n", 0, cursor) + 1 : cursor].strip():
            while True:
                end = source.find(b"\n", cursor)
                if end < 0:
                    cursor = len(source)
                    break
                continued = source[cursor:end].rstrip(b"\r").endswith(b"\\")
                cursor = end + 1
                if not continued:
                    break
            tokens.append((source[start:cursor], start, cursor))
            continue
        raw = raw_string.match(source, cursor)
        if raw:
            closing = b")" + raw.group(1) + b'"'
            end = source.find(closing, raw.end())
            if end < 0:
                raise ValueError("Unterminated raw string in TMB source")
            cursor = end + len(closing)
            tokens.append((b"@literal", start, cursor))
            continue
        if char in {b'"', b"'"}:
            cursor += 1
            while cursor < len(source):
                current = source[cursor : cursor + 1]
                if current == b"\\":
                    cursor += 3 if source.startswith(b"\\\r\n", cursor) else 2
                elif current == char:
                    cursor += 1
                    break
                elif current in {b"\n", b"\r"}:
                    raise ValueError("Unterminated quoted literal in TMB source")
                else:
                    cursor += 1
            else:
                raise ValueError("Unterminated quoted literal in TMB source")
            tokens.append((b"@literal", start, cursor))
            continue
        match = identifier.match(source, cursor) or number.match(source, cursor)
        cursor = match.end() if match else cursor + 1
        tokens.append((source[start:cursor], start, cursor))
        if len(tokens) > 100_000:
            raise ValueError("TMB syntax projection exceeds its token bound")
    return tokens


def tmb_grammar_source(source: bytes) -> bytes:
    """Project two declared TMB macro forms into body-preserving C++ syntax.

    This is not macro expansion, type checking or automatic differentiation.
    SIMULATE's body becomes an ordinary conditional. The four-argument atomic
    macro's forward/reverse statements become separate function bodies. Unknown
    arity or nonliteral metadata fails visibly. Compiler/runtime gates still own
    the actual TMB and derivative semantics. No source file is rewritten.
    """
    if b"TMB.hpp" not in source or not any(
        name in source for name in (b"SIMULATE", b"TMB_ATOMIC_VECTOR_FUNCTION")
    ):
        return source
    tokens = _cpp_tokens(source)
    if not any(
        re.match(rb'#[ \t]*include[ \t]*(?:<TMB\.hpp>|"TMB\.hpp")', text) for text, _, _ in tokens
    ):
        return source
    if any(
        re.match(rb"#[ \t]*(?:define|undef)[ \t]+(?:SIMULATE|TMB_ATOMIC_VECTOR_FUNCTION)\b", text)
        for text, _, _ in tokens
    ):
        raise ValueError("Source-local redefinition of projected TMB macros is unsupported")
    edits: dict[int, tuple[int, bytes]] = {}

    def replace(index: int, value: bytes) -> None:
        _, start, end = tokens[index]
        if start in edits:
            raise ValueError("Overlapping TMB syntax projection")
        edits[start] = (end, value)

    for index, (text, _, _) in enumerate(tokens):
        if text == b"SIMULATE":
            if index + 1 >= len(tokens) or tokens[index + 1][0] != b"{":
                raise ValueError("Only the declared SIMULATE { body } syntax is supported")
            replace(index, b"if(true)")
        elif text == b"TMB_ATOMIC_VECTOR_FUNCTION":
            if index + 1 >= len(tokens) or tokens[index + 1][0] != b"(":
                raise ValueError("TMB atomic syntax requires its four-argument invocation")
            depth = 0
            separators: list[int] = []
            close = None
            for position in range(index + 1, len(tokens)):
                token = tokens[position][0]
                if token == b"(":
                    depth += 1
                    if depth > 256:
                        raise ValueError("TMB atomic parentheses exceed their nesting bound")
                elif token == b")":
                    depth -= 1
                    if depth == 0:
                        close = position
                        break
                elif token == b"," and depth == 1:
                    separators.append(position)
            if close is None or len(separators) != 3:
                raise ValueError("TMB atomic syntax needs exactly four balanced arguments")
            first, second, third = separators
            names = tokens[index + 2 : first]
            dimensions = tokens[first + 1 : second]
            if (
                len(names) != 1
                or re.fullmatch(rb"[A-Za-z_][A-Za-z_0-9]{0,127}", names[0][0]) is None
                or len(dimensions) != 1
                or re.fullmatch(rb"[0-9]{1,6}", dimensions[0][0]) is None
            ):
                raise ValueError("TMB atomic syntax needs a named function and literal dimension")
            replace(index, b"void")
            replace(index + 1, b" ")
            replace(first, b"()")
            replace(first + 1, b" " * (dimensions[0][2] - dimensions[0][1]))
            replace(second, b"{")
            replace(third, b"} void ds60_reverse_" + names[0][0] + b"() {")
            replace(close, b"}")
    projected = bytearray()
    cursor = 0
    for start, (end, value) in sorted(edits.items()):
        if start < cursor:
            raise ValueError("Overlapping TMB syntax projection spans")
        projected.extend(source[cursor:start])
        projected.extend(value)
        cursor = end
    projected.extend(source[cursor:])
    if projected.count(b"\n") != source.count(b"\n"):
        raise ValueError("TMB syntax projection changed diagnostic line positions")
    return bytes(projected)


def grammar_source(path: str, source: bytes, grammar: str) -> tuple[str, bytes]:
    """Project standard linkage guards and declared TMB macro syntax for parsing.

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
    if grammar == "cpp":
        return grammar, tmb_grammar_source(source)
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
        "TMB macro projections retain both bodies but do not model AD semantics. "
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
