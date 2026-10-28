"""Protect SQL literals and psql controls while formatting PostgreSQL source."""

from __future__ import annotations

import hashlib
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PSQL_COMMANDS = {
    "a",
    "c",
    "connect",
    "conninfo",
    "copy",
    "d",
    "dn",
    "dt",
    "du",
    "echo",
    "elif",
    "else",
    "encoding",
    "endif",
    "f",
    "g",
    "getenv",
    "gexec",
    "gset",
    "gx",
    "i",
    "if",
    "include",
    "include_relative",
    "ir",
    "l",
    "o",
    "out",
    "pset",
    "q",
    "qecho",
    "quit",
    "r",
    "set",
    "t",
    "timing",
    "unset",
    "warn",
    "watch",
    "x",
}

SQL_COMMAND = [
    "pg_format",
    "--no-rcfile",
    "--redundant-parenthesis",
    "--spaces",
    "2",
    "--keyword-case",
    "0",
    "--function-case",
    "0",
    "--type-case",
    "0",
]
DOLLAR_QUOTE = re.compile(r"\$(?:[^\W\d]\w*)?\$")
VARIABLE = re.compile(r":(?:'[^'\n]+'|\"[^\"\n]+\"|[A-Za-z_]\w*|\{\?[A-Za-z_]\w*\})")
POSITION_KEYS = {"location", "arg_location", "stmt_location", "stmt_len"}


class SQLFormatError(ValueError):
    """Formatting could not prove that SQL and psql behavior stayed unchanged."""


def quoted_end(text: str, start: int, quote: str, backslashes: bool = False) -> int:
    """Return the first position after a complete SQL quoted token."""
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
    raise SQLFormatError("Unterminated SQL quoted token")


def sql_parts(text: str) -> list[tuple[str, str]]:
    """Separate syntax without treating quotes in comments as quoted tokens."""
    parts: list[tuple[str, str]] = []
    plain: list[str] = []
    index = 0

    def emit(kind: str, end: int) -> None:
        if plain:
            parts.append(("plain", "".join(plain)))
            plain.clear()
        parts.append((kind, text[index:end]))

    while index < len(text):
        if text.startswith("--", index):
            end = text.find("\n", index)
            end = len(text) if end < 0 else end
            emit("comment", end)
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
                raise SQLFormatError("Unterminated SQL block comment")
            emit("comment", end)
            index = end
            continue
        if text[index] in "'\"":
            escaped = text[index] == "'" and index > 0 and text[index - 1] in "eE"
            end = quoted_end(text, index, text[index], escaped)
            emit("quoted", end)
            index = end
            continue
        if text[index] == "$":
            dollar = DOLLAR_QUOTE.match(text, index)
            if dollar:
                delimiter = dollar.group()
                end = text.find(delimiter, dollar.end())
                if end < 0:
                    raise SQLFormatError("Unterminated SQL dollar-quoted body")
                end += len(delimiter)
                emit("quoted", end)
                index = end
                continue
        if text[index] == "\\":
            end = text.find("\n", index)
            end = len(text) if end < 0 else end
            command = text[index + 1 : end].split(maxsplit=1)
            name = command[0] if command else ""
            if name not in PSQL_COMMANDS:
                raise SQLFormatError(
                    f"Unsupported psql control \\{name}; add a reviewed lexer rule"
                )
            emit("psql", end)
            index = end
            continue
        if text.startswith("::", index):
            plain.append("::")
            index += 2
            continue
        if text[index] == ":":
            variable = VARIABLE.match(text, index)
            if variable:
                emit("variable", variable.end())
                index = variable.end()
                continue
        plain.append(text[index])
        index += 1
    if plain:
        parts.append(("plain", "".join(plain)))
    return parts


def sql_for_parser(text: str) -> str:
    """Replace psql-only syntax for PostgreSQL parsing, without executing it."""
    result = []
    for kind, value in sql_parts(text):
        if kind == "psql":
            command = value[1:].split(maxsplit=1)[0]
            result.append(";" if command in {"g", "gx", "gset", "gexec"} else " ")
        elif kind == "variable":
            result.append("'psql_value'" if value.startswith(":'") else '"psql_value"')
        else:
            result.append(value)
    return "".join(result)


def protect_sql(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Make literals and controls opaque to the external formatter."""
    prefix = "__DS60_FORMAT_" + hashlib.sha256(text.encode()).hexdigest()[:16] + "_"
    while prefix in text:
        prefix += "X"
    output = []
    replacements: list[tuple[str, str]] = []
    for kind, value in sql_parts(text):
        if kind in {"quoted", "psql", "variable"}:
            label = prefix + str(len(replacements)) + "__"
            if kind == "psql":
                marker = "-- " + label
            elif kind == "quoted" and value.startswith('"'):
                marker = '"' + label + '"'
            else:
                marker = "'" + label + "'"
            replacements.append((marker, value))
            output.append(marker)
        else:
            output.append(value)
    return "".join(output), replacements


def restore_sql(text: str, replacements: list[tuple[str, str]]) -> str:
    """Reject dropped, duplicated or modified placeholders before restoring."""
    for marker, _ in replacements:
        if text.count(marker) != 1:
            raise SQLFormatError("SQL formatter changed a protected literal or psql placeholder")
    for marker, original in replacements:
        text = text.replace(marker, original)
    return text


def _without_positions(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _without_positions(v) for k, v in value.items() if k not in POSITION_KEYS}
    if isinstance(value, list):
        return [_without_positions(v) for v in value]
    return value


def _control_signature(text: str) -> list[Any]:
    # Verify psql ordering and statement terminators as well as the SQL AST.
    # An inserted semicolon before \gset can execute a query twice even though
    # ordinary PostgreSQL parsing ignores the additional empty statement.
    scan = importlib.import_module("pglast.parser").scan

    signature: list[Any] = []
    chunk: list[str] = []

    def flush() -> None:
        source = "".join(chunk)
        tokens = [
            (token.name, source[token.start : token.end + 1])
            for token in scan(source)
            if token.name not in {"C_COMMENT", "SQL_COMMENT"}
        ]
        signature.append(("sql", tokens))
        chunk.clear()

    for kind, value in sql_parts(text):
        if kind == "psql":
            flush()
            signature.append(("psql", value))
        elif kind == "variable":
            flush()
            signature.append(("variable", value))
        else:
            chunk.append(value)
    flush()
    return signature


def _statement_chunks(text: str) -> list[str]:
    """Reset formatter state at complete PostgreSQL statement boundaries.

    PostgreSQL reports UTF-8 byte offsets. Replace psql variables with a valid
    token and padding of the same byte width solely to discover those offsets;
    their original spelling is still protected and checked during formatting.
    Parsing, rather than splitting on semicolons, keeps routine bodies and
    BEGIN ATOMIC blocks intact. Leading/trailing comments remain in the slices.
    """
    parse_sql_json = importlib.import_module("pglast.parser").parse_sql_json

    parser_parts: list[str] = []
    for kind, value in sql_parts(text):
        if kind == "psql":
            raise SQLFormatError("Split psql control lines before statement formatting")
        if kind == "variable":
            if value.startswith(":'"):
                replacement = "'x'"
            elif value.startswith(':"'):
                replacement = '"x"'
            else:
                replacement = "x"
            padding = len(value.encode("utf-8")) - len(replacement)
            parser_parts.append(replacement + " " * padding)
        else:
            parser_parts.append(value)
    statements = json.loads(parse_sql_json("".join(parser_parts))).get("stmts", [])
    source = text.encode("utf-8")
    boundaries = [0]
    for item in statements[1:]:
        offset = item["stmt_location"]
        # Assign separator whitespace to the preceding complete statement. This
        # keeps identity formatters from introducing a second newline while
        # retaining comments with the following statement and preserving bytes.
        while source[offset : offset + 1] in (b" ", b"\t", b"\r", b"\n", b"\f", b"\v"):
            offset += 1
        boundaries.append(offset)
    boundaries.append(len(source))
    if boundaries != sorted(set(boundaries)):
        # Empty/comment-only buffers have coincident start/end offsets.
        if source or statements:
            raise SQLFormatError("Unexpected PostgreSQL statement offsets")
        return []
    return [
        source[start:end].decode("utf-8")
        for start, end in zip(boundaries[:-1], boundaries[1:], strict=True)
    ]


def format_sql_bytes(source: bytes) -> bytes:
    """Return formatted UTF-8 bytes only after semantic preservation checks."""
    parse_sql_json = importlib.import_module("pglast.parser").parse_sql_json

    original = source.decode("utf-8")
    output: list[str] = []
    chunk: list[str] = []

    def flush() -> None:
        text = "".join(chunk)
        chunk.clear()
        if not text.strip():
            return
        # An opaque CREATE FUNCTION body leaves pgFormatter 5.11's routine
        # indentation state active. A fresh invocation for each complete
        # statement prevents that state leaking into unrelated later queries.
        for statement in _statement_chunks(text):
            protected, replacements = protect_sql(statement)
            command = list(SQL_COMMAND)
            if replacements:
                # Keep AS bodies opaque as well as ordinary quoted values.
                pattern = "(?:" + "|".join(re.escape(marker) for marker, _ in replacements) + ")"
                command.extend(["--placeholder", pattern])
            result = subprocess.run(
                command, input=protected.encode(), capture_output=True, check=False
            )
            if result.returncode:
                raise SQLFormatError(result.stderr.decode("utf-8", errors="replace").strip())
            restored = restore_sql(result.stdout.decode("utf-8"), replacements)
            output.append(restored if restored.endswith("\n") else restored + "\n")

    # A psql command owns the rest of its physical line. Format the SQL buffers
    # on either side independently, retaining the control line outside the
    # formatter so it cannot swallow or attach the following SQL statement.
    for kind, value in sql_parts(original):
        if kind == "psql":
            flush()
            output.append(value + "\n")
        else:
            chunk.append(value)
    flush()
    formatted = "".join(output).rstrip("\r\n") + "\n"
    before = _without_positions(json.loads(parse_sql_json(sql_for_parser(original))))
    after = _without_positions(json.loads(parse_sql_json(sql_for_parser(formatted))))
    if before != after:
        raise SQLFormatError("SQL formatter changed the PostgreSQL syntax tree; original retained")
    if _control_signature(original) != _control_signature(formatted):
        raise SQLFormatError(
            "SQL formatter changed literal, variable or psql token ordering; original retained"
        )
    return formatted.encode("utf-8")


def format_sql_paths(paths: list[str], root: Path, check: bool) -> bool:
    """Format checked repository paths, with a genuinely read-only check mode."""
    success = True
    for name in paths:
        path = root / name
        original = path.read_bytes()
        try:
            formatted = format_sql_bytes(original)
        except Exception as error:
            print(f"SQL formatting failed: {name}: {error}", file=sys.stderr)
            success = False
            continue
        if formatted != original:
            if check:
                print(f"Would format: {name}")
                success = False
            else:
                path.write_bytes(formatted)
    return success
