"""Verify formatting parity without relabeling historical runtime evidence.

The receipt retains compressed original bytes, so future source archives can
independently verify both identities and Python syntax after Git history changes.
This proves AST equality, not a new execution or identical traceback locations.
"""

from __future__ import annotations

import ast
import base64
import hashlib
import json
import re
import zlib
from pathlib import Path
from typing import Any

RECEIPT = "curriculum/source-format-parity.json"


def _tree_value(value: Any) -> Any:
    if isinstance(value, ast.AST):
        return [
            type(value).__name__,
            [
                [name, _tree_value(item)]
                for name, item in ast.iter_fields(value)
                if not (name == "type_params" and item == [])
                and not (isinstance(value, ast.TypeIgnore) and name == "lineno")
            ],
        ]
    if isinstance(value, list):
        return [_tree_value(item) for item in value]
    # repr preserves bytes, complex values and numeric/string type distinctions.
    return [type(value).__name__, repr(value)]


def semantic_sha256(source: bytes) -> str:
    tree = ast.parse(source, type_comments=True)
    payload = json.dumps(_tree_value(tree), ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def create_record(path: str, before: bytes, after: bytes) -> dict[str, str]:
    if Path(path).is_absolute() or ".." in Path(path).parts or not path.endswith(".py"):
        raise ValueError("Formatting parity requires a repository-relative Python source")
    semantic = semantic_sha256(before)
    if semantic != semantic_sha256(after):
        raise ValueError(f"Formatting changed Python syntax: {path}")
    return {
        "path": path,
        "historical_sha256": hashlib.sha256(before).hexdigest(),
        "formatted_sha256": hashlib.sha256(after).hexdigest(),
        "semantic_sha256": semantic,
        "original_zlib_base64": base64.b64encode(zlib.compress(before, level=9)).decode("ascii"),
    }


def verify_record(record: dict[str, str], current: bytes) -> str:
    original = zlib.decompress(base64.b64decode(record["original_zlib_base64"], validate=True))
    original_digest = hashlib.sha256(original).hexdigest()
    if original_digest != record["historical_sha256"]:
        raise ValueError("Formatting receipt does not match its original bytes")
    if hashlib.sha256(current).hexdigest() != record["formatted_sha256"]:
        raise ValueError("Formatting receipt does not match current source")
    if semantic_sha256(original) != record["semantic_sha256"]:
        raise ValueError("Formatting receipt does not match original Python syntax")
    if semantic_sha256(current) != record["semantic_sha256"]:
        raise ValueError("Formatting changed Python syntax")
    return original_digest


def source_digest_before_formatting(root: Path, path: str, current: bytes) -> str:
    receipt = root / RECEIPT
    if not receipt.exists():
        return hashlib.sha256(current).hexdigest()
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    if (
        payload.get("schema_version") != 1
        or payload.get("evidence_kind") != "python_ast_formatting_parity"
    ):
        raise ValueError("Unknown source formatting receipt")
    matches = [record for record in payload["records"] if record["path"] == path]
    if len(matches) > 1:
        raise ValueError("Duplicate source formatting receipt")
    if not matches:
        return hashlib.sha256(current).hexdigest()
    return verify_record(matches[0], current)


# Maximal operators prevent accidental equivalence of e.g. a + +b and a++ + b.
_OPERATORS = re.compile(
    r">>>=|<<=|>>=|<=>|->\*|\.\.\.|>>>|::|->|\.\*|\+\+|--|&&|\|\||==|!=|<=|>=|<<|>>|\+=|-=|\*=|/=|%=|&=|\|=|\^=|##|[^\s]",
    re.S,
)
_WORD = re.compile(r"[A-Za-z_$][\w$]*|(?:\d[\w'.]*)(?:[eEpP][+-]?\d+)?", re.ASCII)
_STRING = re.compile(r"(?:u8|u|U|L)?(?:\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')", re.S)
_RAW = re.compile(r'(?:u8|u|U|L)?R"([^ ()\\\t\r\n]{0,16})\(')


def code_tokens(source: str) -> tuple[str, ...]:
    """Compare C++/Java lexical structure, preserving literal bytes and directives.

    Comments and ordinary whitespace are omitted. This is a source-pairing check;
    compiler and execution tests remain the authority for language correctness.
    """
    source = re.sub(r"\\\r?\n", "", source)
    result: list[str] = []
    position = 0
    directive = False
    while position < len(source):
        if source[position].isspace():
            if source[position] == "\n" and directive:
                result.append("<directive-end>")
                directive = False
            position += 1
            continue
        if source.startswith("//", position):
            end = source.find("\n", position)
            position = len(source) if end == -1 else end
            continue
        if source.startswith("/*", position):
            end = source.find("*/", position + 2)
            if end == -1:
                raise ValueError("Unterminated source comment")
            position = end + 2
            continue
        raw = _RAW.match(source, position)
        if raw:
            ending = ")" + raw.group(1) + '"'
            end = source.find(ending, raw.end())
            if end == -1:
                raise ValueError("Unterminated raw string")
            end += len(ending)
            result.append(source[position:end])
            position = end
            continue
        match = (
            _STRING.match(source, position)
            or _WORD.match(source, position)
            or _OPERATORS.match(source, position)
        )
        if match is None:
            raise ValueError("Unrecognized source token")
        token = match.group()
        result.append(token)
        if token == "#":
            directive = True
        position = match.end()
    if directive:
        result.append("<directive-end>")
    return tuple(result)
