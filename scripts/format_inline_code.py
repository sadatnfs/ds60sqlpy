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
import textwrap
import time
import tokenize
import tomllib
import xml.etree.ElementTree as ET
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import format_repo  # noqa: E402
from scripts.source_format_parity import _inline_semantic_sha256, _tree_value  # noqa: E402

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
    "quoted_attribute_value",
    "mount_param",
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


# Only these grammar nodes admit a style-only terminal separator. Tuple commas
# in Rust and array holes in JavaScript remain meaningful and are retained.
TRAILING_COMMA_NODES = {
    "javascript": {
        "arguments",
        "array",
        "object",
        "formal_parameters",
        "named_imports",
        "export_clause",
        "array_pattern",
        "object_pattern",
    },
    "typescript": {
        "arguments",
        "array",
        "object",
        "formal_parameters",
        "named_imports",
        "export_clause",
        "array_pattern",
        "object_pattern",
        "type_arguments",
        "type_parameters",
        "tuple_type",
        "object_type",
    },
    "tsx": {
        "arguments",
        "array",
        "object",
        "formal_parameters",
        "named_imports",
        "export_clause",
        "array_pattern",
        "object_pattern",
        "type_arguments",
        "type_parameters",
        "tuple_type",
        "object_type",
    },
    "rust": {
        "arguments",
        "parameters",
        "field_declaration_list",
        "field_initializer_list",
        "enum_variant_list",
        "type_arguments",
        "type_parameters",
        "match_arm",
    },
}


def style_comma(node: Any, grammar: str) -> bool:
    parent = node.parent
    if (
        node.type != ","
        or parent is None
        or parent.type not in TRAILING_COMMA_NODES.get(grammar, set())
    ):
        return False
    children = [child for child in parent.children if "comment" not in child.type]
    position = next(index for index, child in enumerate(children) if child.id == node.id)
    # No preceding value means an array hole; a following value means a real separator.
    if position == 0 or not children[position - 1].is_named:
        return False
    tail = children[position + 1 :]
    return not tail or (len(tail) == 1 and tail[0].type in {")", "]", "}", ">"})


HTML_VOID_TAGS = {
    b"area",
    b"base",
    b"br",
    b"col",
    b"embed",
    b"hr",
    b"img",
    b"input",
    b"link",
    b"meta",
    b"param",
    b"source",
    b"track",
    b"wbr",
}


def html_void_tag(node: Any) -> bool:
    if node.type not in {"start_tag", "self_closing_tag"}:
        return False
    tags = [child for child in node.children if child.type == "tag_name"]
    if len(tags) != 1 or tags[0].text.lower() not in HTML_VOID_TAGS:
        return False
    ancestor = node.parent
    while ancestor is not None:
        if ancestor.type == "element":
            for child in ancestor.children:
                if child.type in {"start_tag", "self_closing_tag"}:
                    names = [
                        part.text.lower() for part in child.children if part.type == "tag_name"
                    ]
                    if names in ([b"svg"], [b"math"]):
                        return False
                    break
        ancestor = ancestor.parent
    return True


def rust_macro_regions(source: bytes) -> int:
    parser = importlib.import_module("tree_sitter_language_pack").get_parser("rust")
    pending = [parser.parse(source).root_node]
    count = 0
    while pending:
        node = pending.pop()
        if node.type == "token_tree":
            count += 1
        else:
            pending.extend(node.children)
    return count


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
        if (
            "string" in kind
            or "comment" in kind
            or kind in PROTECTED_NODES
            or (grammar == "rust" and kind == "token_tree")
        ):
            protected.append((node.start_byte, node.end_byte))
            category = "string" if opaque and "string" in kind else kind
            if (
                opaque
                and grammar == "html"
                and kind in {"attribute_value", "quoted_attribute_value"}
            ):
                category = "html-attribute-value"
            return ("protected", category, b"" if opaque else value)
        if (not node.is_named and kind == ";") or style_comma(node, grammar):
            return None
        if grammar == "dockerfile" and kind == "line_continuation":
            return None
        if (
            grammar in {"javascript", "typescript", "tsx"}
            and kind == "formal_parameters"
            and node.parent.type == "arrow_function"
            and len(node.named_children) == 1
        ):
            parameter = node.named_children[0]
            if parameter.type == "identifier":
                return convert(parameter, depth + 1)
            if (
                parameter.type == "required_parameter"
                and len(parameter.named_children) == 1
                and parameter.named_children[0].type == "identifier"
            ):
                return convert(parameter.named_children[0], depth + 1)
        if grammar == "scala" and kind == "indented_block" and len(node.named_children) == 1:
            expression = node.named_children[0]
            if expression.type.endswith(("_expression", "_literal")) or expression.type in {
                "string",
                "identifier",
            }:
                return convert(expression, depth + 1)
        if kind == "parenthesized_expression" and len(node.named_children) == 1:
            return convert(node.named_children[0], depth + 1)
        children = [convert(child, depth + 1) for child in node.children]
        children = [child for child in children if child is not None]
        if grammar in {"typescript", "tsx"} and kind == "union_type":
            members: list[Any] = []
            for child in children:
                if child == ("|", b"|"):
                    continue
                members.extend(child[1] if child[0] == "union_type" else [child])
            return members[0] if len(members) == 1 else ("union_type", tuple(members))
        if grammar == "html":
            expanded: list[Any] = []
            for child in children:
                expanded.extend(child[1] if child[0] == "html_void_with_tail" else [child])
            children = expanded
            if html_void_tag(node):
                kind = "html_void_tag"
                if children and children[-1] in {(">", b">"), ("/>", b"/>")}:
                    children[-1] = (">", b">")
            if kind == "element" and children and children[0][0] == "html_void_tag":
                # The grammar may attach following text to a non-self-closed
                # HTML void element. In HTML that text is its sibling.
                return ("html_void_with_tail", (("element", (children[0],)), *children[1:]))
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
            return _inline_semantic_sha256(raw), comments
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


def python_comments(raw: bytes) -> list[tuple[int, int]]:
    source = raw.decode()
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    return [
        (offsets[token.start[0] - 1] + token.start[1], offsets[token.end[0] - 1] + token.end[1])
        for token in tokenize.generate_tokens(io.StringIO(source).readline)
        if token.type == tokenize.COMMENT
    ]


def restore_python_comments(source: bytes, candidate: bytes) -> bytes:
    before, after = source.decode(), candidate.decode()
    originals, replacements = python_comments(source), python_comments(candidate)
    if len(originals) != len(replacements):
        raise FormatFailure("Formatter changed Python comment count")
    for (start, end), (old_start, old_end) in reversed(
        list(zip(replacements, originals, strict=True))
    ):
        after = after[:start] + before[old_start:old_end] + after[end:]
    return after.encode()


def java_context(source: bytes) -> tuple[bytes, str]:
    parser = importlib.import_module("tree_sitter_language_pack").get_parser("java")
    tree = parser.parse(source)
    if tree.root_node.has_error:
        raise UnsupportedSnippet("fragment-or-unaccepted-java-syntax")
    top_level = {
        "package_declaration",
        "import_declaration",
        "class_declaration",
        "interface_declaration",
        "enum_declaration",
        "record_declaration",
        "annotation_type_declaration",
        "line_comment",
        "block_comment",
    }
    if all(node.type in top_level for node in tree.root_node.named_children):
        return source, "unit"
    # The permissive tree grammar admits some statement nodes in class bodies.
    # Prefer the actual statement context; explicit members use the class context.
    member_types = {
        "method_declaration",
        "constructor_declaration",
        "field_declaration",
        "static_initializer",
    }
    class_modifiers = {"public", "protected", "private", "static", "transient", "volatile"}
    members = any(
        node.type in member_types
        or any(
            child.type == "modifiers"
            and any(item.type in class_modifiers for item in child.children)
            for child in node.children
        )
        for node in tree.root_node.named_children
    )
    if members and any(
        node.type not in top_level | member_types | {"local_variable_declaration", "block"}
        for node in tree.root_node.named_children
    ):
        raise UnsupportedSnippet("java-mixed-member-and-statement-context")
    wrappers = (
        [(b"class DS60InlineSnippet {\n", b"\n}\n", "members")]
        if members
        else [(b"class DS60InlineSnippet { void ds60Example() {\n", b"\n} }\n", "statements")]
    )
    for prefix, suffix, mode in wrappers:
        wrapped = prefix + source + suffix
        if not parser.parse(wrapped).root_node.has_error:
            return wrapped, mode
    raise UnsupportedSnippet("java-excerpt-needs-unsupported-class-or-method-context")


def java_unwrap(candidate: bytes, mode: str) -> bytes:
    if mode == "unit":
        return candidate
    parser = importlib.import_module("tree_sitter_language_pack").get_parser("java")
    tree = parser.parse(candidate)
    if tree.root_node.has_error or len(tree.root_node.named_children) != 1:
        raise FormatFailure("Formatter changed Java wrapper structure")
    declaration = tree.root_node.named_children[0]
    name = declaration.child_by_field_name("name")
    if declaration.type != "class_declaration" or name is None or name.text != b"DS60InlineSnippet":
        raise FormatFailure("Formatter changed Java wrapper identity")
    body = declaration.child_by_field_name("body")
    if body is None:
        raise FormatFailure("Formatter removed Java wrapper body")
    if mode == "statements":
        if len(body.named_children) != 1 or body.named_children[0].type != "method_declaration":
            raise FormatFailure("Formatter changed Java method wrapper")
        method = body.named_children[0]
        name = method.child_by_field_name("name")
        body = method.child_by_field_name("body")
        if name is None or name.text != b"ds60Example" or body is None:
            raise FormatFailure("Formatter changed Java method identity")
    content = candidate[body.start_byte + 1 : body.end_byte - 1].decode()
    return (textwrap.dedent(content).strip("\r\n") + "\n").encode()


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
    java_mode = "unit"
    if language == "java":
        source, java_mode = java_context(source)
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
        style = importlib.import_module("yaml").safe_load(
            (config / "clang-format.yaml").read_text()
        )
        # Namespace comments are authored evidence, not a formatter-generated sentence.
        style["FixNamespaceComments"] = False
        command = [
            "clang-format",
            "--style=" + json.dumps(style),
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
    if language == "java":
        result = java_unwrap(result, java_mode)
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
        if language == "python":
            formatted = restore_python_comments(source, formatted)
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
        # The pinned source adapter is deterministic: unchanged guarded bytes
        # are already a fixed point. Custom adapters may be stateful, so retain
        # their second invocation even when the first output is unchanged.
        if self.adapter is adapter_bytes and formatted == source:
            self.check_time()
        else:
            # Restored authored literals can affect a formatter's next line-wrap
            # decision. Allow bounded convergence, checking meaning on every pass.
            for _ in range(3):
                self.check_time()
                repeated = self.once(formatted, language, suffix)
                if repeated == formatted:
                    break
                formatted = repeated
            else:
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
            if language == "rust":
                count = rust_macro_regions(original)
                if count:
                    record["preserved_regions"] = {"opaque-rust-macro-token-trees": count}
            if language == "shell":
                placeholders = list(re.finditer(rb"<your[-_][A-Za-z0-9_-]+>", original))
                if placeholders:
                    _, protected_spans = tree_signature(original, "bash")
                    if any(
                        not any(start <= match.start() < end for start, end in protected_spans)
                        for match in placeholders
                    ):
                        raise UnsupportedSnippet("unsubstituted-shell-template-placeholder")
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
            if record.get("preserved_regions"):
                record["reason"] += "; opaque-rust-macro-token-trees-preserved"
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


PROSE_ROLES = {
    "guide",
    "chapter",
    "introduction",
    "overview",
    "sections",
    "examples",
    "body",
    "text",
    "content",
    "markdown",
    "explanation",
    "narrative",
    "mechanism",
    "anatomy",
    "worked_examples",
    "solution_explanation",
}
NON_PROSE_ROLES = {
    "expected",
    "output",
    "outputs",
    "reference",
    "solution",
    "starter",
    "source",
    "code",
    "program",
    "pattern",
    "needle",
    "replacement",
    "regex",
    "transcript",
}


def python_prose_role(node: ast.AST, parents: dict[int, ast.AST], path: str) -> bool:
    """Admit known authoring data roles, never a replace needle or code literal."""
    cursor = node
    prose = False
    while (parent := parents.get(id(cursor))) is not None:
        if isinstance(parent, ast.List | ast.Tuple):
            cursor = parent
            continue
        if isinstance(parent, ast.Dict):
            for key, value in zip(parent.keys, parent.values, strict=True):
                if value is cursor and isinstance(key, ast.Constant) and isinstance(key.value, str):
                    if key.value in NON_PROSE_ROLES:
                        return False
                    prose = prose or key.value in PROSE_ROLES
                    cursor = parent
                    break
            else:
                return False
            continue
        if isinstance(parent, ast.Assign):
            return bool(parent.targets) and all(
                isinstance(target, ast.Name)
                and target.id not in NON_PROSE_ROLES
                and (prose or target.id in PROSE_ROLES)
                for target in parent.targets
            )
        if isinstance(parent, ast.AnnAssign | ast.AugAssign):
            return (
                isinstance(parent.target, ast.Name)
                and parent.target.id not in NON_PROSE_ROLES
                and (prose or parent.target.id in PROSE_ROLES)
            )
        if isinstance(parent, ast.keyword):
            return parent.arg in PROSE_ROLES
        if isinstance(parent, ast.Call):
            # This reviewed author() contract takes examples as positional arg3.
            # The remaining executable fields and arbitrary calls are excluded.
            return (
                path.startswith("courses/nlp/authoring/advanced/")
                and isinstance(parent.func, ast.Name)
                and parent.func.id == "author"
                and len(parent.args) > 3
                and parent.args[3] is cursor
            )
        return False
    return False


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
        def token_offset(position: tuple[int, int]) -> int:
            line, column = position
            return offsets[line - 1] + len(lines[line - 1].decode()[:column].encode())

        members = [
            token
            for token in tokens
            if token.type == tokenize.STRING
            and start <= token_offset(token.start)
            and token_offset(token.end) <= end
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
            node.value,
            formatter,
            selected,
            path=path,
            list_only=list_only,
            protected=None
            if python_prose_role(node, parents, path)
            else "non-prose-or-unknown-authoring-role",
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


def web_example_slots(value: Any, path: str) -> dict[tuple[str | int, ...], str]:
    """Only the maintained five-field web example schema admits raw program text."""
    if path != "courses/web-development/authoring/chapters.json":
        return {}
    if (
        not isinstance(value, dict)
        or type(value.get("schema_version")) is not int
        or value["schema_version"] != 1
        or not isinstance(value.get("chapters"), list)
    ):
        raise FormatFailure("Unknown web authoring chapter schema")
    slots: dict[tuple[str | int, ...], str] = {}
    for chapter_index, chapter in enumerate(value["chapters"]):
        if not isinstance(chapter, dict) or not isinstance(chapter.get("examples"), list):
            raise FormatFailure("Web chapters require explicit example arrays")
        for example_index, example in enumerate(chapter["examples"]):
            if (
                not isinstance(example, list)
                or len(example) != 5
                or not all(isinstance(item, str) for item in example)
                or re.fullmatch(r"[A-Za-z0-9_+-]+", example[2]) is None
            ):
                raise FormatFailure(
                    "Web examples require heading, intro, language, code and expected text"
                )
            slots[("chapters", chapter_index, "examples", example_index, 3)] = example[2]
    return slots


def format_authoring_program(
    value: str,
    tag: str,
    formatter: Formatter,
    selected: set[str],
    *,
    path: str,
    list_only: bool,
) -> tuple[str, list[dict[str, Any]]]:
    if len(value.encode()) > MAX_SNIPPET:
        raise FormatFailure("Authoring program exceeds its byte bound")
    marker = "~" * max(3, max((len(m.group()) + 1 for m in re.finditer(r"~+", value)), default=3))
    # The web renderer appends exactly one separator newline to this raw field.
    virtual = marker + tag + "\n" + value + "\n" + marker + "\n"
    output, records = format_document(virtual, formatter, selected, path=path, list_only=list_only)
    if records and records[0]["status"] in {"clean", "formatted"}:
        blocks, _ = fences(output)
        if len(blocks) != 1 or not blocks[0].closed or not blocks[0].body.endswith("\n"):
            raise FormatFailure("Authoring program wrapper identity changed")
        result = blocks[0].body[:-1]
    else:
        result = value
    return result, records


def format_authoring_json(
    source: str, formatter: Formatter, selected: set[str], *, path: str, list_only: bool = False
) -> tuple[str, list[dict[str, Any]]]:
    original = container_json(source)
    revised = copy.deepcopy(original)
    code_slots = web_example_slots(original, path)
    example_rows = {trail[:-1] for trail in code_slots}
    # JSON keeps insertion order. Align every raw string token with its parsed
    # key/value role so identical text in prose and expected output stays distinct.
    tokens: list[tuple[str, tuple[str | int, ...], bool, bool]] = []

    def walk(value: Any, trail: tuple[str | int, ...] = (), prose: bool = False) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                tokens.append((key, trail, False, True))
                role = key in PROSE_ROLES or (prose and key not in NON_PROSE_ROLES)
                walk(item, (*trail, key), role)
        elif isinstance(value, list):
            for position, item in enumerate(value):
                walk(item, (*trail, position), prose)
        elif isinstance(value, str):
            tokens.append((value, trail, prose, False))

    walk(original)
    decoder = json.JSONDecoder()
    edits = []
    records = []
    index, position = 0, 0
    while index < len(source):
        if source[index] != '"':
            index += 1
            continue
        value, end = decoder.raw_decode(source, index)
        if position >= len(tokens) or tokens[position][0] != value:
            raise FormatFailure("JSON source tokens differ from parsed authoring roles")
        _, trail, prose, is_key = tokens[position]
        position += 1
        formatted = value
        items: list[dict[str, Any]] = []
        raw_program = not is_key and trail in code_slots
        if raw_program:
            formatted, items = format_authoring_program(
                value, code_slots[trail], formatter, selected, path=path, list_only=list_only
            )
        elif not is_key and fences(value)[0]:
            protected = None if prose else "non-prose-or-unknown-authoring-role"
            if trail[:-1] in example_rows:
                protected = "web-example-heading-intro-language-or-expected"
            formatted, items = format_document(
                value, formatter, selected, path=path, list_only=list_only, protected=protected
            )
        for item in items:
            item["virtual_line"] = item["line"]
            item["line"] = source[:index].count("\n") + 1
            item["container"] = "json-authoring-code" if raw_program else "json-authoring-string"
            item["json_path"] = list(trail)
            if raw_program:
                item["raw_value_sha256"] = hashlib.sha256(value.encode()).hexdigest()
        records.extend(items)
        if formatted != value:
            target = revised
            for key in trail[:-1]:
                target = target[key]
            target[trail[-1]] = formatted
            edits.append((index, end, json.dumps(formatted, ensure_ascii=False)))
        index = end
    if position != len(tokens):
        raise FormatFailure("JSON source has incomplete role coverage")
    if any(item["status"] == "error" for item in records) or not edits:
        return source, records
    rewritten = source
    for start, end, value in reversed(edits):
        rewritten = rewritten[:start] + value + rewritten[end:]
    if typed_value(container_json(rewritten)) != typed_value(revised):
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


@lru_cache(maxsize=2)
def generation_formatter(root: Path) -> Formatter:
    # One generator can emit hundreds of repeated examples. Keep the same
    # bounded adapter cache without creating an unbounded cache per document.
    return Formatter(root)


def canonical_markdown(
    text: str, *, root: Path, path: str, formatter: Formatter | None = None
) -> str:
    """Canonicalize an owner's in-memory Markdown before its normal file write.

    This is a generation hook, not permission for a formatter to rewrite derived
    files. It requires the pinned tools for every supported fence present, never
    installs a tool, and never executes a snippet. Call it before write_text().
    """
    relative = Path(path)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or str(relative) != path
        or "\\" in path
        or relative.suffix != ".md"
    ):
        raise ValueError("Canonical generation requires a relative Markdown output path")
    for part in [root / relative, *(root / relative).parents]:
        if part.is_symlink():
            raise ValueError("Canonical generation refuses symlink output components")
        if part == root:
            break
    generated, protected = ownership(path, format_repo.load_policy(root))
    if not generated or protected:
        raise ValueError(
            "Canonical generation requires an explicitly generator-owned output: " + path
        )
    tool = formatter if formatter is not None else generation_formatter(root)
    revised, records = format_document(text, tool, set(format_repo.LANGUAGES), path=path)
    errors = [row for row in records if row["status"] not in {"clean", "formatted", "preserved"}]
    if errors:
        first = errors[0]
        raise FormatFailure(
            f"Canonical generation failed for {path}:{first.get('line', 0)}: {first['reason']}. "
            "Run the documented generator in the prepared formatter environment; "
            "no fallback or dependency installation was attempted."
        )
    preserved = Counter(
        (row.get("tag", "untyped"), row["reason"])
        for row in records
        if row["status"] == "preserved" or row.get("preserved_regions")
    )
    for (tag, reason), count in sorted(preserved.items()):
        print(f"GENERATION-PRESERVE {path} [{tag}] {count}: {reason}", file=sys.stderr)
    return revised


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
