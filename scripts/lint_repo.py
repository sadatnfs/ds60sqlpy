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

GRAMMARS = {
    "c": "c",
    "cpp": "cpp",
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
PSQL_COMMANDS = {
    "set",
    "unset",
    "getenv",
    "echo",
    "warn",
    "qecho",
    "if",
    "elif",
    "else",
    "endif",
    "ir",
    "i",
    "include",
    "include_relative",
    "connect",
    "c",
    "copy",
    "quit",
    "q",
    "pset",
    "gset",
    "gexec",
    "g",
    "gx",
    "timing",
    "watch",
    "o",
    "out",
    "a",
    "t",
    "x",
    "f",
    "r",
    "encoding",
    "conninfo",
    "d",
    "dt",
    "du",
    "dn",
    "l",
}


def run(command: list[str], root: Path) -> bool:
    try:
        result = subprocess.run(command, cwd=root, check=False)
    except FileNotFoundError:
        print(f"Missing lint tool: {command[0]}. Use ./scripts/lint-repo.", file=sys.stderr)
        return False
    return result.returncode == 0


def _quoted_end(text: str, start: int, quote: str, backslashes: bool = False) -> int:
    index = start + 1
    while index < len(text):
        if backslashes and text[index] == "\\":
            index += 2
        elif text[index] == quote:
            if index + 1 < len(text) and text[index + 1] == quote:
                index += 2
            else:
                return index + 1
        else:
            index += 1
    raise ValueError("Unterminated SQL quoted value")


def sql_for_parser(text: str) -> str:
    """Separate psql controls without interpreting them or rewriting source.

    Quoted SQL, comments, and dollar-quoted function bodies are copied verbatim.
    psql variables become grammar placeholders, so this checks statement syntax,
    not a particular variable expansion, psql branch result, or routine body.
    """
    chunks: list[str] = []
    index = 0
    while index < len(text):
        if text.startswith("--", index):
            end = text.find("\n", index)
            end = len(text) if end < 0 else end
            chunks.append(text[index:end])
            index = end
            continue
        if text.startswith("/*", index):
            end, depth = index + 2, 1
            while end < len(text) and depth:
                if text.startswith("/*", end):
                    depth += 1
                    end += 2
                elif text.startswith("*/", end):
                    depth -= 1
                    end += 2
                else:
                    end += 1
            if depth:
                raise ValueError("Unterminated SQL block comment")
            chunks.append(text[index:end])
            index = end
            continue
        if text[index] in "'\"":
            backslashes = index > 0 and text[index - 1] in "eE"
            end = _quoted_end(text, index, text[index], backslashes)
            chunks.append(text[index:end])
            index = end
            continue
        if text[index] == "$":
            match = re.match(r"\$(?:[A-Za-z_]\w*)?\$", text[index:])
            if match:
                delimiter = match.group()
                end = text.find(delimiter, index + len(delimiter))
                if end < 0:
                    raise ValueError("Unterminated SQL dollar-quoted body")
                end += len(delimiter)
                chunks.append(text[index:end])
                index = end
                continue
        if text[index] == "\\":
            end = text.find("\n", index)
            end = len(text) if end < 0 else end
            command = text[index + 1 : end].split(maxsplit=1)
            name = command[0] if command else ""
            if name not in PSQL_COMMANDS:
                raise ValueError(f"Unsupported psql control \\{name}; add a reviewed parser rule")
            chunks.append(";" if name in {"g", "gx", "gset", "gexec"} else " ")
            index = end
            continue
        if text.startswith("::", index):
            chunks.append("::")
            index += 2
            continue
        if text[index] == ":":
            variable = re.match(
                r":(?:'[^'\n]+'|\"[^\"\n]+\"|[A-Za-z_]\w*|\{\?[A-Za-z_]\w*\})", text[index:]
            )
            if variable:
                token = variable.group()
                chunks.append("'psql_value'" if token.startswith(":'") else '"psql_value"')
                index += len(token)
                continue
        chunks.append(text[index])
        index += 1
    return "".join(chunks)


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
        if language in {"swift", "scala"}:
            continue
        for error in syntax_errors(path, root, language):
            print(error, file=sys.stderr)
            success = False
    if language == "python":
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
        "--list", action="store_true", help="List source coverage without running lint"
    )
    arguments = parser.parse_args(argv)
    groups, excluded, unmanaged = inventory(ROOT)
    selected = [
        language
        for language in LANGUAGES
        if not arguments.language or language in arguments.language
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
