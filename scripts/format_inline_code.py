#!/usr/bin/env python3
"""Format supported fenced programs without rewriting prose or running examples.

The pinned source adapters own style. Independent parsing and protected-literal
checks own admission. Generated Markdown is inspected but repaired through its
normal owner/generator, never by this module. Every preserved block has a reason.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib
import io
import json
import re
import subprocess
import sys
import time
import tokenize
import tomllib
import xml.etree.ElementTree as ET
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import format_repo  # noqa: E402
from scripts.source_format_parity import _tree_value, semantic_sha256  # noqa: E402

MAX_DOCUMENT = 5_000_000
MAX_SNIPPET = 256_000
MAX_FENCES = 1024
MAX_TREE_NODES = 100_000
MAX_TREE_DEPTH = 256
MAX_CACHE_BYTES = 64 * 1024 * 1024

# Family names match the existing public --language adapters. Suffixes select
# the precise pinned parser for families containing several source languages.
ALIASES: dict[str, tuple[str, str]] = {
    "python": ("python", ".py"),
    "py": ("python", ".py"),
    "r": ("r", ".R"),
    "julia": ("julia", ".jl"),
    "jl": ("julia", ".jl"),
    "stan": ("stan", ".stan"),
    "dbt": ("dbt", ".sql"),
    "sql+jinja": ("dbt", ".sql"),
    "javascript": ("web", ".js"),
    "js": ("web", ".js"),
    "typescript": ("web", ".ts"),
    "ts": ("web", ".ts"),
    "jsx": ("web", ".jsx"),
    "tsx": ("web", ".tsx"),
    "json": ("web", ".json"),
    "jsonc": ("web", ".jsonc"),
    "yaml": ("web", ".yaml"),
    "yml": ("web", ".yaml"),
    "html": ("web", ".html"),
    "css": ("web", ".css"),
    "scss": ("web", ".scss"),
    "java": ("java", ".java"),
    "c": ("c", ".c"),
    "cpp": ("cpp", ".cpp"),
    "c++": ("cpp", ".cpp"),
    "cuda": ("cuda", ".cu"),
    "cu": ("cuda", ".cu"),
    "php": ("php", ".php"),
    "csharp": ("csharp", ".cs"),
    "cs": ("csharp", ".cs"),
    "go": ("go", ".go"),
    "golang": ("go", ".go"),
    "rust": ("rust", ".rs"),
    "rs": ("rust", ".rs"),
    "swift": ("swift", ".swift"),
    "scala": ("scala", ".scala"),
    "sql": ("sql", ".sql"),
    "postgresql": ("sql", ".sql"),
    "sh": ("shell", ".sh"),
    "bash": ("shell", ".sh"),
    "shell": ("shell", ".sh"),
    "toml": ("toml", ".toml"),
    "xml": ("xml", ".xml"),
    "cmake": ("cmake", ".cmake"),
    "dockerfile": ("docker", ".Dockerfile"),
    "docker": ("docker", ".Dockerfile"),
}
TRANSCRIPTS = {"", "text", "plaintext", "console", "output", "shell-session", "terminal"}
OPENING = re.compile(r"^( {0,3})(`{3,}|~{3,})([^\r\n]*)(?:\r?\n)?$")
UNSUPPORTED_CONTAINER = re.compile(r"^(?: {4,}|[ \t]*>[ \t]*)(?:`{3,}|~{3,})")
TREE_GRAMMARS = {
    "c": "c",
    "cpp": "cpp",
    "cuda": "cuda",
    "csharp": "csharp",
    "java": "java",
    "go": "go",
    "rust": "rust",
    "swift": "swift",
    "scala": "scala",
    "shell": "bash",
    "php": "php",
    "cmake": "cmake",
    "docker": "dockerfile",
}
WEB_GRAMMARS = {
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".jsonc": "json",
}
PROTECTED_NODES = {
    "char_literal",
    "character_literal",
    "integer_literal",
    "float_literal",
    "number_literal",
    "number",
    "integer",
    "float",
    "heredoc_body",
    "heredoc_content",
    "preproc_arg",
    "system_lib_string",
    "shell_command",
    "text",
    "raw_text",
    "attribute_value",
}


class UnsupportedSnippet(ValueError):
    """This excerpt needs context or is an intentional non-program surface."""


class BudgetExhausted(Exception):
    """A bounded read-only inventory reached its declared time limit."""


class FormatFailure(ValueError):
    """A supported formatting operation failed its preservation contract."""


@dataclass(frozen=True)
class Fence:
    line: int
    start: int
    end: int
    body_start: int
    body_end: int
    indent: str
    info: str
    closed: bool
    body: str

    @property
    def tag(self) -> str:
        fields = self.info.strip().split()
        return fields[0].lower() if fields else ""


def fences(text: str) -> tuple[list[Fence], list[dict[str, Any]]]:
    """Read top-level CommonMark fences, retaining every outer source byte."""
    if "```" not in text and "~~~" not in text:
        return [], []
    if len(text.encode()) > MAX_DOCUMENT or "\x00" in text:
        raise FormatFailure("Document exceeds its UTF-8/NUL bounds")
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    result: list[Fence] = []
    unsupported: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        match = OPENING.fullmatch(lines[index])
        if match is None or (match[2][0] == "`" and "`" in match[3]):
            if UNSUPPORTED_CONTAINER.match(lines[index]):
                unsupported.append(
                    {"line": index + 1, "status": "preserved", "reason": "nested-or-indented-fence"}
                )
            index += 1
            continue
        first = index
        indent, marker, info = match.groups()
        close = re.compile(
            r"^ {0,3}" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}[ \t]*(?:\r?\n)?$"
        )
        index += 1
        while index < len(lines) and close.fullmatch(lines[index]) is None:
            index += 1
        closed = index < len(lines)
        body_end = offsets[index]
        body = text[offsets[first + 1] : body_end]
        result.append(
            Fence(
                first + 1,
                offsets[first],
                offsets[index + 1] if closed else len(text),
                offsets[first + 1],
                body_end,
                indent,
                info,
                closed,
                body,
            )
        )
        if len(result) > MAX_FENCES:
            raise FormatFailure("Document exceeds the fenced-block bound")
        index += 1
    return result, unsupported


def code_body(fence: Fence) -> tuple[bytes, str]:
    body = fence.body
    if "\r" in body.replace("\r\n", ""):
        raise UnsupportedSnippet("mixed-or-bare-CR-newlines")
    newline = "\r\n" if "\r\n" in body else "\n"
    if newline == "\r\n" and "\n" in body.replace("\r\n", ""):
        raise UnsupportedSnippet("mixed-newline-styles")
    body = body.replace("\r\n", "\n")
    if fence.indent:
        width = len(fence.indent)
        body = "".join(
            line[min(len(line) - len(line.lstrip(" ")), width) :]
            for line in body.splitlines(keepends=True)
        )
    raw = body.encode("utf-8")
    if len(raw) > MAX_SNIPPET:
        raise UnsupportedSnippet("snippet-size-bound")
    return raw, newline


def typed_value(value: Any) -> Any:
    if isinstance(value, dict):
        return ("dict", tuple((key, typed_value(item)) for key, item in value.items()))
    if isinstance(value, (list, tuple)):
        return (type(value).__name__, tuple(typed_value(item) for item in value))
    return (type(value).__name__, repr(value))


def yaml_value(raw: bytes) -> Any:
    yaml = importlib.import_module("yaml")
    roots = list(yaml.compose_all(raw, Loader=yaml.SafeLoader))
    visited: dict[int, int] = {}
    nodes = 0

    def convert(node: Any, depth: int = 0) -> Any:
        nonlocal nodes
        if depth > MAX_TREE_DEPTH:
            raise UnsupportedSnippet("YAML nesting exceeds its bound")
        if node is None:
            return None
        identity = id(node)
        if identity in visited:
            return ("alias", visited[identity])
        nodes += 1
        if nodes > MAX_TREE_NODES:
            raise UnsupportedSnippet("YAML node count exceeds its bound")
        visited[identity] = len(visited)
        if isinstance(node, yaml.ScalarNode):
            return ("scalar", node.tag, node.value)
        if isinstance(node, yaml.SequenceNode):
            return ("sequence", node.tag, tuple(convert(item, depth + 1) for item in node.value))
        return (
            "mapping",
            node.tag,
            tuple(
                (convert(key, depth + 1), convert(value, depth + 1)) for key, value in node.value
            ),
        )

    return tuple(convert(node) for node in roots)


def xml_value(raw: bytes) -> Any:
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True))
    root = ET.fromstring(raw, parser=parser)

    def convert(node: Any, inherited_preserve: bool = False, ignore_tail: bool = False) -> Any:
        mode = node.attrib.get("{http://www.w3.org/XML/1998/namespace}space")
        preserve = mode == "preserve" or (mode != "default" and inherited_preserve)
        # Indentation between element-only children is a layout surface. Mixed
        # content, leaf values and xml:space=preserve remain byte-value exact.
        element_only = bool(len(node)) and not preserve and not (node.text or "").strip()
        element_only = element_only and all(not (child.tail or "").strip() for child in node)
        text = None if element_only else node.text
        tail = None if ignore_tail else node.tail
        return (
            str(node.tag),
            tuple(node.attrib.items()),
            text,
            tail,
            tuple(convert(child, preserve, element_only) for child in node),
        )

    namespaces = tuple(value for _, value in ET.iterparse(io.BytesIO(raw), events=("start-ns",)))
    return namespaces, convert(root)


def tree_signature(
    raw: bytes, grammar: str, *, opaque: bool = False
) -> tuple[Any, list[tuple[int, int]]]:
    parser = importlib.import_module("tree_sitter_language_pack").get_parser(grammar)
    tree = parser.parse(raw)
    if tree.root_node.has_error:
        raise UnsupportedSnippet("fragment-or-unaccepted-" + grammar + "-syntax")
    protected: list[tuple[int, int]] = []
    count = 0

    def convert(node: Any, depth: int = 0) -> Any:
        nonlocal count
        count += 1
        if count > MAX_TREE_NODES or depth > MAX_TREE_DEPTH:
            raise UnsupportedSnippet("syntax-tree-bound")
        kind = node.type
        value = raw[node.start_byte : node.end_byte]
        if "string" in kind or "comment" in kind or kind in PROTECTED_NODES:
            protected.append((node.start_byte, node.end_byte))
            category = "string" if opaque and "string" in kind else kind
            return ("protected", category, b"" if opaque else value)
        if not node.is_named and kind == ";":
            return None
        if kind == "parenthesized_expression" and len(node.named_children) == 1:
            return convert(node.named_children[0], depth + 1)
        children = [convert(child, depth + 1) for child in node.children]
        children = [child for child in children if child is not None]
        if children:
            return (kind, tuple(children))
        if grammar == "dockerfile" and kind.isupper():
            value = value.upper()
        return (kind, value)

    return convert(tree.root_node), protected


def lexical_signature(raw: bytes, alias: str) -> Any:
    lexers = importlib.import_module("pygments.lexers")
    tokens = importlib.import_module("pygments.token")
    lexer = lexers.get_lexer_by_name(alias, stripnl=False, ensurenl=False)
    result = []
    for kind, value in lexer.get_tokens(raw.decode()):
        if kind in tokens.Error:
            raise UnsupportedSnippet("unaccepted-" + alias + "-token")
        if kind in tokens.Text and not value.strip():
            continue
        result.append((str(kind), value))
    return tuple(result)


def signature(raw: bytes, language: str, suffix: str) -> Any:
    try:
        if language == "python":
            comments = tuple(
                token.string
                for token in tokenize.tokenize(io.BytesIO(raw).readline)
                if token.type == tokenize.COMMENT
            )
            return semantic_sha256(raw), comments
        if language == "web" and suffix == ".json":
            return typed_value(json.loads(raw, object_pairs_hook=lambda pairs: tuple(pairs)))
        if language == "web" and suffix == ".yaml":
            return yaml_value(raw)
        if language == "toml":
            return typed_value(tomllib.loads(raw.decode()))
        if language == "xml":
            return xml_value(raw)
        if language in {"stan", "dbt"}:
            return lexical_signature(raw, "stan" if language == "stan" else "sql+jinja")
        if language == "sql":
            from scripts.sql_formatting import (
                _control_signature,
                _without_positions,
                sql_for_parser,
            )

            parser = importlib.import_module("pglast.parser")
            return (
                _without_positions(json.loads(parser.parse_sql_json(sql_for_parser(raw.decode())))),
                _control_signature(raw.decode()),
            )
        grammar = WEB_GRAMMARS[suffix] if language == "web" else TREE_GRAMMARS[language]
        return tree_signature(raw, grammar)[0]
    except (SyntaxError, ValueError, UnicodeError, ET.ParseError, RecursionError) as error:
        if isinstance(error, UnsupportedSnippet):
            raise
        raise UnsupportedSnippet(
            "fragment-or-invalid-syntax: " + str(error).splitlines()[0][:180]
        ) from None
    except Exception as error:
        if type(error).__module__.startswith(("yaml.", "pglast.")):
            raise UnsupportedSnippet(
                "fragment-or-invalid-syntax: " + str(error).splitlines()[0][:180]
            ) from None
        raise


def invoke(command: list[str], source: bytes, root: Path) -> bytes:
    try:
        result = subprocess.run(
            command, input=source, cwd=root, capture_output=True, check=False, timeout=60
        )
    except FileNotFoundError:
        raise FormatFailure("Missing prepared adapter: " + command[0]) from None
    except subprocess.TimeoutExpired:
        raise FormatFailure("Pinned source adapter exceeded its time bound") from None
    if result.returncode:
        message = result.stderr.decode("utf-8", "replace").strip()[:2000]
        raise FormatFailure("Pinned adapter rejected source: " + (message or command[0]))
    if len(result.stdout) > MAX_SNIPPET * 4:
        raise FormatFailure("Pinned adapter output exceeds its bound")
    return result.stdout


def adapter_bytes(source: bytes, language: str, suffix: str, root: Path) -> bytes:
    """Reuse pinned commands and configuration, always through bounded stdin."""
    config = root / "docker/formatting"
    if language == "python":
        command = [
            "ruff",
            "format",
            "--no-cache",
            "--config",
            str(root / "pyproject.toml"),
            "--stdin-filename",
            "snippet.py",
            "-",
        ]
    elif language in {"web", "java", "php", "xml", "toml"}:
        command = [
            "prettier",
            "--config",
            str(config / "prettier.json"),
            "--ignore-path",
            "/dev/null",
            "--stdin-filepath",
            "snippet" + suffix,
        ]
        if language == "xml":
            command.extend(["--parser", "xml"])
    elif language in {"c", "cpp", "cuda", "csharp"}:
        command = [
            "clang-format",
            "--style=file:" + str(config / "clang-format.yaml"),
            "--assume-filename=snippet" + suffix,
        ]
    elif language == "go":
        command = ["gofmt"]
    elif language == "rust":
        command = ["rustfmt", "--config-path", str(config / "rustfmt.toml"), "--emit", "stdout"]
    elif language == "swift":
        command = ["swift-format", "format", "--configuration", str(config / "swift-format.json")]
    elif language == "scala":
        command = [
            "scalafmt",
            "--config",
            str(config / "scalafmt.conf"),
            "--non-interactive",
            "--stdin",
            "--stdout",
            "--assume-filename",
            "snippet.scala",
        ]
    elif language == "shell":
        command = ["shfmt", "-ln", "bash", "-i", "2", "-ci"]
    elif language == "docker":
        command = ["dockerfmt"]
    elif language == "cmake":
        command = ["cmake-format", "--config-files", str(config / "cmake-format.yaml"), "--", "-"]
    elif language == "sql":
        from scripts.sql_formatting import format_sql_bytes

        return format_sql_bytes(source)
    elif language == "r":
        command = ["Rscript", "--vanilla", str(root / "scripts/r_source_tools.R"), "format"]
    elif language == "julia":
        command = [
            "julia",
            "--startup-file=no",
            "--compiled-modules=existing",
            "--project=/opt/julia-env",
            str(root / "scripts/julia_source_tools.jl"),
            "format",
        ]
    elif language in {"stan", "dbt"}:
        command = [sys.executable, str(root / f"scripts/{language}_source_tools.py"), "format"]
    else:
        raise FormatFailure("No pinned adapter for " + language)
    result = invoke(command, source, root)
    if language == "docker":
        result = result.rstrip(b"\r\n") + b"\n"
    return result


def native_admission(source: bytes, language: str, root: Path) -> None:
    if language == "r":
        command = ["Rscript", "--vanilla", str(root / "scripts/r_source_tools.R"), "parse"]
    elif language == "julia":
        command = [
            "julia",
            "--startup-file=no",
            "--compiled-modules=existing",
            "--project=/opt/julia-env",
            str(root / "scripts/julia_source_tools.jl"),
            "parse",
        ]
    elif language in {"stan", "dbt"}:
        command = [sys.executable, str(root / f"scripts/{language}_source_tools.py"), "parse"]
    else:
        return
    try:
        invoke(command, source, root)
    except FormatFailure as error:
        message = str(error)
        if message.startswith("Pinned adapter rejected source:") and any(
            word in message.lower()
            for word in (
                "syntax",
                "parseerror",
                "unexpected",
                "incomplete",
                "semantic error",
                "parser",
                "invalid julia source",
            )
        ):
            raise UnsupportedSnippet("fragment-or-invalid-" + language + "-syntax") from None
        raise


class Formatter:
    def __init__(
        self,
        root: Path,
        adapter: Callable[[bytes, str, str, Path], bytes] = adapter_bytes,
        *,
        max_seconds: float | None = None,
    ) -> None:
        self.root = root
        self.adapter = adapter
        self.cache: dict[tuple[str, str, bytes], bytes] = {}
        self.cache_bytes = 0
        self.deadline = None if max_seconds is None else time.monotonic() + max_seconds
        self.expired = False

    def check_time(self) -> None:
        if self.deadline is not None and time.monotonic() >= self.deadline:
            self.expired = True
            raise BudgetExhausted("read-only-time-budget-exhausted")

    def once(self, source: bytes, language: str, suffix: str) -> bytes:
        if language in {"r", "julia"}:
            # These maintained adapters independently compare native parsed
            # expressions, including literal values, before emitting output.
            return self.adapter(source, language, suffix, self.root)
        before = signature(source, language, suffix)
        formatted = self.adapter(source, language, suffix, self.root)
        grammar = WEB_GRAMMARS.get(suffix) if language == "web" else TREE_GRAMMARS.get(language)
        if grammar:
            shape, originals = tree_signature(source, grammar, opaque=True)
            try:
                candidate, replacements = tree_signature(formatted, grammar, opaque=True)
            except UnsupportedSnippet as error:
                raise FormatFailure("Formatter emitted invalid syntax: " + str(error)) from None
            if shape != candidate or len(originals) != len(replacements):
                raise FormatFailure("Formatter changed the program structure")
            for (start, end), (old_start, old_end) in reversed(
                list(zip(replacements, originals, strict=True))
            ):
                formatted = formatted[:start] + source[old_start:old_end] + formatted[end:]
        try:
            after = signature(formatted, language, suffix)
        except UnsupportedSnippet as error:
            raise FormatFailure("Formatter emitted invalid syntax: " + str(error)) from None
        if before != after:
            raise FormatFailure("Formatter changed syntax or literal values")
        return formatted

    def format(self, source: bytes, language: str, suffix: str) -> bytes:
        self.check_time()
        key = (language, suffix, source)
        if key in self.cache:
            return self.cache[key]
        native_admission(source, language, self.root)
        self.check_time()
        # All native and generic syntax checks happen without executing source.
        formatted = self.once(source, language, suffix)
        self.check_time()
        if self.once(formatted, language, suffix) != formatted:
            raise FormatFailure("Pinned formatting did not reach an idempotent result")
        size = len(source) + len(formatted)
        if self.cache_bytes + size > MAX_CACHE_BYTES:
            self.cache.clear()
            self.cache_bytes = 0
        self.cache[key] = formatted
        self.cache_bytes += size
        return formatted


def format_document(
    text: str,
    formatter: Formatter,
    selected: set[str],
    *,
    path: str,
    generated: bool = False,
    protected: str | None = None,
    list_only: bool = False,
) -> tuple[str, list[dict[str, Any]]]:
    blocks, records = fences(text)
    edits: list[tuple[int, int, str]] = []
    for block in blocks:
        record: dict[str, Any] = {
            "path": path,
            "line": block.line,
            "tag": block.tag,
            "status": "preserved",
            "source_sha256": hashlib.sha256(block.body.encode()).hexdigest(),
        }
        records.append(record)
        if protected:
            record["reason"] = "protected-source: " + protected
            continue
        if not block.closed:
            record["reason"] = "unclosed-fence"
            continue
        if block.tag in TRANSCRIPTS:
            record["reason"] = "untyped-or-output-transcript"
            continue
        if block.tag not in ALIASES:
            record["reason"] = "unsupported-language"
            continue
        language, suffix = ALIASES[block.tag]
        if language == "sql" and path.startswith("courses/dbt/"):
            language = "dbt"
        record["language"] = language
        if language not in selected:
            record.update(status="not-selected", reason="other-language-or-toolchain")
            continue
        if list_only:
            record.update(status="candidate", reason="generator-owned" if generated else "authored")
            continue
        try:
            original, newline = code_body(block)
            if not original.strip():
                raise UnsupportedSnippet("empty-fence")
            if re.search(rb"(?m)^(?:>>> |\.\.\. |\$ |PS> |In \[[0-9]+\]:)", original):
                raise UnsupportedSnippet("interactive-prompt-transcript")
            formatted = formatter.format(original, language, suffix)
            formatted_text = formatted.decode("utf-8")
            if not formatted_text.endswith("\n"):
                formatted_text += "\n"
            restored = "".join(
                block.indent + line if line.strip() else line
                for line in formatted_text.splitlines(keepends=True)
            ).replace("\n", newline)
            record["formatted_sha256"] = hashlib.sha256(restored.encode()).hexdigest()
            if restored == block.body:
                record.update(status="clean", reason="syntax-and-literals-preserved")
            elif generated:
                record.update(
                    status="needs-regeneration",
                    reason="edit-durable-source-and-run-owner-generator",
                )
            else:
                record.update(status="formatted", reason="syntax-and-literals-preserved")
                edits.append((block.body_start, block.body_end, restored))
        except BudgetExhausted as error:
            record.update(status="not-checked", reason=str(error))
        except UnsupportedSnippet as error:
            record["reason"] = str(error)
        except (FormatFailure, ImportError, LookupError, OSError, ValueError) as error:
            record.update(status="error", reason=str(error)[:2200])
    for record in records:
        record.setdefault("path", path)
    if any(record["status"] == "error" for record in records):
        return text, records
    for start, end, value in reversed(edits):
        text = text[:start] + value + text[end:]
    return text, records


def literal_source(value: str, original: str) -> str:
    """Keep ordinary triple-quoted authoring prose readable where safe."""
    match = re.match(r"(?is)^([ru]*)(\"\"\"|''')", original)
    if match:
        prefix, quote = match.groups()
        if "r" in prefix.lower():
            if quote not in value and not value.endswith("\\"):
                return prefix + quote + value + quote
        else:
            encoded = value.replace("\\", "\\\\").replace(quote, "\\" + quote)
            return prefix + quote + encoded + quote
    return repr(value)


def format_authoring_python(
    source: str, formatter: Formatter, selected: set[str], *, path: str, list_only: bool = False
) -> tuple[str, list[dict[str, Any]]]:
    tree = ast.parse(source, type_comments=True)
    nodes = list(ast.walk(tree))
    replacements: list[tuple[int, str]] = []
    parents = {id(child): node for node in nodes for child in ast.iter_child_nodes(node)}
    lines = source.encode().splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    records: list[dict[str, Any]] = []
    edits = []
    for position, node in enumerate(nodes):
        if isinstance(node, ast.JoinedStr):
            value = "".join(
                item.value
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
                else "<dynamic>"
                for item in node.values
            )
            blocks, _ = fences(value)
            for block in blocks:
                records.append(
                    {
                        "path": path,
                        "line": node.lineno,
                        "virtual_line": block.line,
                        "tag": block.tag,
                        "status": "preserved",
                        "reason": "dynamic-authoring-template",
                    }
                )
            continue
        if (
            not isinstance(node, ast.Constant)
            or not isinstance(node.value, str)
            or isinstance(parents.get(id(node)), ast.JoinedStr)
        ):
            continue
        if not fences(node.value)[0]:
            continue
        if node.end_lineno is None or node.end_col_offset is None:
            raise FormatFailure("Authoring string has no bounded source span")
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        original = source.encode()[start:end].decode()
        # Adjacent concatenated literals share one AST Constant but cannot be
        # replaced as an arbitrary token sequence without changing authorship.
        members = [
            token
            for token in tokens
            if token.type == tokenize.STRING
            and node.lineno <= token.start[0] <= node.end_lineno
            and original.find(token.string) >= 0
        ]
        if len(members) != 1:
            records.append(
                {
                    "path": path,
                    "line": node.lineno,
                    "status": "preserved",
                    "reason": "concatenated-authoring-literals",
                }
            )
            continue
        formatted, items = format_document(
            node.value, formatter, selected, path=path, list_only=list_only
        )
        for item in items:
            item["virtual_line"] = item["line"]
            item["line"] = node.lineno
            item["container"] = "python-authoring-string"
        records.extend(items)
        if formatted != node.value:
            replacements.append((position, formatted))
            edits.append((start, end, literal_source(formatted, original).encode()))
    if any(item["status"] == "error" for item in records) or not edits:
        return source, records
    expected = copy.deepcopy(tree)
    expected_nodes = list(ast.walk(expected))
    for position, formatted in replacements:
        expected_node = expected_nodes[position]
        if not isinstance(expected_node, ast.Constant):
            raise FormatFailure("Authoring AST position changed unexpectedly")
        expected_node.value = formatted
    encoded = source.encode()
    for start, end, replacement in sorted(edits, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    rewritten = encoded.decode()
    if _tree_value(ast.parse(rewritten, type_comments=True)) != _tree_value(expected):
        raise FormatFailure("Authoring rewrite changed Python outside approved prose constants")
    return rewritten, records


def container_json(source: str) -> Any:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise FormatFailure("Duplicate JSON key in an authoring container")
            value[key] = item
        return value

    return json.loads(source, object_pairs_hook=unique)


def format_authoring_json(
    source: str, formatter: Formatter, selected: set[str], *, path: str, list_only: bool = False
) -> tuple[str, list[dict[str, Any]]]:
    original = container_json(source)
    decoder = json.JSONDecoder()
    edits = []
    records = []
    values: dict[str, str] = {}
    index = 0
    while index < len(source):
        if source[index] != '"':
            index += 1
            continue
        value, end = decoder.raw_decode(source, index)
        following = end
        while following < len(source) and source[following].isspace():
            following += 1
        if source[following : following + 1] != ":" and fences(value)[0]:
            formatted, items = format_document(
                value, formatter, selected, path=path, list_only=list_only
            )
            for item in items:
                item["virtual_line"] = item["line"]
                item["line"] = source[:index].count("\n") + 1
                item["container"] = "json-authoring-string"
            records.extend(items)
            if formatted != value:
                values[value] = formatted
                edits.append((index, end, json.dumps(formatted, ensure_ascii=False)))
        index = end
    if any(item["status"] == "error" for item in records) or not edits:
        return source, records
    rewritten = source
    for start, end, value in reversed(edits):
        rewritten = rewritten[:start] + value + rewritten[end:]

    def expected(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: expected(item) for key, item in value.items()}
        if isinstance(value, list):
            return [expected(item) for item in value]
        return values.get(value, value) if isinstance(value, str) else value

    if typed_value(json.loads(rewritten)) != typed_value(expected(original)):
        raise FormatFailure("Authoring JSON changed outside approved prose strings")
    return rewritten, records


def format_notebook(
    source: str,
    formatter: Formatter,
    selected: set[str],
    *,
    path: str,
    protected: str | None = None,
    list_only: bool = False,
) -> tuple[str, list[dict[str, Any]]]:
    notebook = container_json(source)
    if not isinstance(notebook, dict) or not isinstance(notebook.get("cells"), list):
        raise FormatFailure("Notebook must contain a cell list")
    revised = copy.deepcopy(notebook)
    records: list[dict[str, Any]] = []
    changed = False
    for index, cell in enumerate(notebook["cells"]):
        if not isinstance(cell, dict) or cell.get("cell_type") != "markdown":
            continue
        value = cell.get("source")
        if isinstance(value, str):
            text = value
        elif isinstance(value, list) and all(isinstance(line, str) for line in value):
            text = "".join(value)
        else:
            raise FormatFailure("Notebook Markdown source must be text or text lines")
        formatted, items = format_document(
            text, formatter, selected, path=path, protected=protected, list_only=list_only
        )
        for item in items:
            item["cell"] = index
            item["container"] = "notebook-markdown"
        records.extend(items)
        if formatted != text:
            revised["cells"][index]["source"] = (
                formatted.splitlines(keepends=True) if isinstance(value, list) else formatted
            )
            changed = True
    if not changed or any(item["status"] == "error" for item in records):
        return source, records
    # Only Markdown source fields change. Code, outputs and metadata values are
    # retained; the ordinary notebook formatter then owns container indentation.
    result = json.dumps(revised, indent=1, ensure_ascii=False) + "\n"
    if typed_value(json.loads(result)) != typed_value(revised):
        raise FormatFailure("Notebook serialization changed values")
    return result, records


def ownership(path: str, policy: dict[str, Any]) -> tuple[bool, str | None]:
    import fnmatch

    reasons = [row["reason"] for row in policy["preserve"] if row["path"] == path]
    reasons.extend(
        row["reason"]
        for row in policy["exclude"]
        if row["pattern"] != "*.md" and fnmatch.fnmatchcase(path, row["pattern"])
    )
    if not reasons:
        return False, None
    if any(
        any(
            word in reason.lower()
            for word in (
                "historical",
                "vendor",
                "third-party",
                "credential",
                "signature",
                "immutable",
            )
        )
        for reason in reasons
    ):
        return False, reasons[0]
    if path.endswith(".md") and any(
        any(
            word in reason.lower()
            for word in ("generated", "generator", "published output", "authoring pipeline")
        )
        for reason in reasons
    ):
        return True, None
    return False, reasons[0]


def eligible_source(path: str) -> bool:
    suffix = Path(path).suffix.lower()
    return suffix in {".md", ".ipynb", ".rmd", ".qmd"} or (
        suffix in {".py", ".json"} and "/authoring/" in path
    )


def inspect_sources(
    root: Path,
    selected: set[str],
    *,
    check: bool = True,
    list_only: bool = False,
    formatter: Formatter | None = None,
    max_seconds: float | None = None,
) -> dict[str, Any]:
    if max_seconds is not None and (not check or not 0 < max_seconds <= 1200):
        raise ValueError("A time-bounded inventory must be read-only and at most 1200 seconds")
    formatter = Formatter(root, max_seconds=max_seconds) if formatter is None else formatter
    policy = format_repo.load_policy(root)
    records: list[dict[str, Any]] = []
    changed = []
    owner_candidates: dict[str, list[dict[str, Any]]] = {}
    inspected_files: list[dict[str, str]] = []
    discovery_complete = True
    try:
        files = format_repo.source_files(root, include=eligible_source, deadline=formatter.deadline)
    except (OSError, subprocess.SubprocessError) as error:
        discovery_complete = False
        records.append(
            {
                "path": ".",
                "line": 1,
                "status": "error",
                "reason": "source-inventory-unavailable: use the public wrapper host list or "
                "a validated local snapshot; " + type(error).__name__,
            }
        )
        files = []
    for name in files:
        try:
            formatter.check_time()
        except BudgetExhausted:
            records.append(
                {
                    "path": name,
                    "line": 1,
                    "status": "not-checked",
                    "reason": "read-only-time-budget-exhausted",
                }
            )
            break
        path = root / name
        authoring = "/authoring/" in name
        if path.suffix.lower() not in {".md", ".py", ".json", ".ipynb", ".rmd", ".qmd"}:
            continue
        if path.suffix in {".py", ".json"} and not authoring:
            continue
        if path.suffix.lower() in {".rmd", ".qmd"}:
            records.append(
                {
                    "path": name,
                    "line": 1,
                    "status": "preserved",
                    "reason": "R-Markdown-or-Quarto-container-unsupported",
                }
            )
            continue
        generated, protected = ownership(name, policy)
        original = path.read_bytes().decode("utf-8")
        inspected_files.append(
            {"path": name, "sha256": hashlib.sha256(original.encode()).hexdigest()}
        )
        if len(original.encode()) > MAX_DOCUMENT:
            records.append(
                {"path": name, "line": 1, "status": "error", "reason": "document-size-bound"}
            )
            continue
        try:
            if path.suffix == ".md":
                rewritten, items = format_document(
                    original,
                    formatter,
                    selected,
                    path=name,
                    generated=generated,
                    protected=protected,
                    list_only=list_only,
                )
                if not generated and not protected:
                    for block in fences(original)[0]:
                        digest = hashlib.sha256(block.body.encode()).hexdigest()
                        owner_candidates.setdefault(digest, []).append(
                            {"path": name, "line": block.line}
                        )
            elif path.suffix == ".ipynb":
                rewritten, items = format_notebook(
                    original,
                    formatter,
                    selected,
                    path=name,
                    protected=protected,
                    list_only=list_only,
                )
            elif protected:
                continue
            elif path.suffix == ".py":
                rewritten, items = format_authoring_python(
                    original, formatter, selected, path=name, list_only=list_only
                )
            else:
                rewritten, items = format_authoring_json(
                    original, formatter, selected, path=name, list_only=list_only
                )
            records.extend(items)
            if rewritten != original:
                changed.append(name)
                if not check and not list_only:
                    path.write_bytes(rewritten.encode())
        except (OSError, ValueError, SyntaxError, UnicodeError, tokenize.TokenError) as error:
            records.append(
                {"path": name, "line": 1, "status": "error", "reason": str(error)[:2200]}
            )
    for item in records:
        if item["status"] == "needs-regeneration":
            item["owner_candidates"] = owner_candidates.get(item.get("source_sha256", ""), [])[:16]
    counts = Counter(item["status"] for item in records)
    reasons = Counter(
        (item.get("tag", ""), item.get("reason", ""))
        for item in records
        if item["status"] == "preserved"
    )
    failures = (
        counts["error"]
        + counts["needs-regeneration"]
        + counts["not-checked"]
        + (len(changed) if check else 0)
    )
    return {
        "schema_version": 1,
        "kind": "fenced-source-formatting",
        "selected_languages": sorted(selected),
        "check": check,
        "complete": discovery_complete and not formatter.expired,
        "source_inventory": inspected_files,
        "list_only": list_only,
        "changed_files": changed,
        "status_counts": dict(counts),
        "preservation_counts": [
            {"tag": tag, "reason": reason, "count": count}
            for (tag, reason), count in sorted(reasons.items())
        ],
        "records": records,
        "passed": failures == 0,
        "limitations": [
            "Technical identifier code spans are untyped prose and remain exact.",
            "Nested Markdown containers, dynamic authoring templates and unadmitted "
            "fragments are inventoried, not reformatted.",
            "Generated Markdown drift requires durable source repair and its normal generator.",
            "Parsing and formatting never execute lesson programs or create runtime qualification.",
        ],
    }


def print_report(report: dict[str, Any], *, detail: bool = False) -> None:
    print(
        "Fenced source coverage: "
        + ", ".join(f"{name}={count}" for name, count in sorted(report["status_counts"].items())),
        flush=True,
    )
    for item in report["preservation_counts"]:
        print(f"PRESERVE-FENCE [{item['tag'] or 'untyped'}] {item['count']}: {item['reason']}")
    for item in report["records"]:
        if detail or item["status"] in {"error", "needs-regeneration", "formatted"}:
            print(
                f"{item['status'].upper()} {item['path']}:{item['line']} "
                f"[{item.get('tag', '')}]: {item['reason']}"
            )
            if item.get("owner_candidates"):
                print(
                    "  Source candidates: "
                    + ", ".join(f"{row['path']}:{row['line']}" for row in item["owner_candidates"])
                )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--language", choices=format_repo.LANGUAGES, action="append")
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--max-seconds", type=float, help="bounded read-only check, up to 1200 seconds"
    )
    args = parser.parse_args(argv)
    report = inspect_sources(
        args.root,
        set(args.language or format_repo.LANGUAGES),
        check=args.check,
        list_only=args.list,
        max_seconds=args.max_seconds,
    )
    print_report(report, detail=args.list)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
