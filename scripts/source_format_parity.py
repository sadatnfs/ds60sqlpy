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


# Additive evidence for formatting Python fences in Markdown. These records do
# not modify or replace historical execution or presentation receipts.
INLINE_RECEIPT = "curriculum/inline-format-parity.json"
INLINE_KIND = "python_fenced_formatting_parity"
MAX_INLINE_GUIDE = 5_000_000
MAX_INLINE_RECEIPT = 32_000_000
MAX_INLINE_RECORDS = 10_000
INLINE_RECORD_KEYS = {
    "path",
    "historical_sha256",
    "formatted_sha256",
    "original_bytes",
    "original_zlib_base64",
    "changed_python_blocks",
}
INLINE_BLOCK_KEYS = {
    "ordinal",
    "historical_body_sha256",
    "formatted_body_sha256",
    "semantic_sha256",
    "ordered_comment_sha256",
}


def _inline_path(value: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 4096
        or Path(value).is_absolute()
        or Path(value).as_posix() != value
        or ".." in Path(value).parts
        or "\\" in value
        or not value.endswith(".md")
        or any(ord(character) < 32 for character in value)
    ):
        raise ValueError("Inline parity requires a safe relative Markdown path")
    return value


def _inline_sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def _inline_record_shape(record: Any) -> None:
    if not isinstance(record, dict) or set(record) != INLINE_RECORD_KEYS:
        raise ValueError("Malformed inline formatting binding")
    _inline_path(record["path"])
    if not all(_inline_sha(record[key]) for key in ("historical_sha256", "formatted_sha256")):
        raise ValueError("Invalid inline formatting SHA256")
    if (
        type(record["original_bytes"]) is not int
        or not 0 < record["original_bytes"] <= MAX_INLINE_GUIDE
    ):
        raise ValueError("Inline original byte count exceeds its bound")
    encoded = record["original_zlib_base64"]
    if not isinstance(encoded, str) or not encoded or len(encoded) > MAX_INLINE_GUIDE * 2:
        raise ValueError("Inline compressed source exceeds its bound")
    blocks = record["changed_python_blocks"]
    if not isinstance(blocks, list) or not blocks or len(blocks) > 1024:
        raise ValueError("Inline binding needs bounded changed Python blocks")
    ordinals = []
    for block in blocks:
        if not isinstance(block, dict) or set(block) != INLINE_BLOCK_KEYS:
            raise ValueError("Malformed inline block binding")
        if type(block["ordinal"]) is not int or not 0 <= block["ordinal"] < 1024:
            raise ValueError("Invalid inline block ordinal")
        if not all(_inline_sha(block[key]) for key in INLINE_BLOCK_KEYS - {"ordinal"}):
            raise ValueError("Invalid inline block SHA256")
        ordinals.append(block["ordinal"])
    if ordinals != sorted(set(ordinals)):
        raise ValueError("Duplicate or unordered inline block binding")


def _python_comments(source: bytes) -> str:
    import io
    import tokenize

    comments = [
        token.string
        for token in tokenize.tokenize(io.BytesIO(source).readline)
        if token.type == tokenize.COMMENT
    ]
    encoded = json.dumps(comments, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _inline_semantic_sha256(source: bytes) -> str:
    """Normalize positions while retaining each type-ignore's logical attachment."""
    tree = ast.parse(source, type_comments=True)
    statements: list[tuple[tuple[str | int, ...], ast.stmt, int | None]] = []

    def visit(node: ast.AST, path: tuple[str | int, ...] = ()) -> None:
        if isinstance(node, ast.stmt):
            descendants = [
                child.lineno
                for child in ast.walk(node)
                if isinstance(child, ast.stmt) and child is not node
            ]
            statements.append((path, node, min(descendants) if descendants else None))
        for name, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                visit(value, (*path, name))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    if isinstance(child, ast.AST):
                        visit(child, (*path, name, index))

    visit(tree)
    anchors = []
    for ignore in tree.type_ignores:
        enclosing = [
            path
            for path, node, first_child in statements
            if node.lineno <= ignore.lineno <= (node.end_lineno or node.lineno)
            and (first_child is None or ignore.lineno < first_child)
        ]
        if enclosing:
            depth = max(map(len, enclosing))
            deepest = [path for path in enclosing if len(path) == depth]
            if len(deepest) != 1:
                raise ValueError("Ambiguous Python type-ignore statement attachment")
            anchor: Any = ("statement", deepest[0])
        else:
            preceding = [
                (node.end_lineno or node.lineno, len(path), path)
                for path, node, _ in statements
                if (node.end_lineno or node.lineno) < ignore.lineno
            ]
            following = [
                (node.lineno, -len(path), path)
                for path, node, _ in statements
                if node.lineno > ignore.lineno
            ]
            # Distinguish module-leading directives and each later statement gap.
            anchor = (
                "gap",
                max(preceding)[2] if preceding else None,
                min(following)[2] if following else None,
            )
        anchors.append((ignore.tag, anchor))
    payload = json.dumps([_tree_value(tree), anchors], ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def _inline_blocks(before: bytes, after: bytes) -> list[dict[str, Any]]:
    import tokenize

    from scripts.format_inline_code import code_body, fences

    if not 0 < len(before) <= MAX_INLINE_GUIDE or not 0 < len(after) <= MAX_INLINE_GUIDE:
        raise ValueError("Inline Markdown exceeds its byte bound")
    old_text, new_text = before.decode("utf-8"), after.decode("utf-8")
    old, _ = fences(old_text)
    new, _ = fences(new_text)
    if len(old) != len(new):
        raise ValueError("Inline formatting changed fence identities")
    old_cursor, new_cursor = 0, 0
    blocks = []
    for index, (left, right) in enumerate(zip(old, new, strict=True)):
        if (
            old_text[old_cursor : left.body_start] != new_text[new_cursor : right.body_start]
            or left.info != right.info
            or left.indent != right.indent
            or left.closed != right.closed
        ):
            raise ValueError("Inline formatting changed non-code spans or fence identities")
        old_cursor, new_cursor = left.body_end, right.body_end
        if left.body == right.body:
            continue
        if not left.closed or left.tag not in {"python", "py"}:
            raise ValueError("Non-Python and unclosed protected blocks must remain byte-identical")
        original, _ = code_body(left)
        current, _ = code_body(right)
        try:
            semantic = _inline_semantic_sha256(original)
            current_semantic = _inline_semantic_sha256(current)
            comments = _python_comments(original)
            current_comments = _python_comments(current)
        except (SyntaxError, tokenize.TokenError) as error:
            raise ValueError("Inline binding contains invalid Python source") from error
        if semantic != current_semantic:
            raise ValueError("Inline formatting changed Python syntax or literal values")
        if comments != current_comments:
            raise ValueError("Inline formatting changed ordered Python comment content")
        blocks.append(
            {
                "ordinal": index,
                "historical_body_sha256": hashlib.sha256(left.body.encode()).hexdigest(),
                "formatted_body_sha256": hashlib.sha256(right.body.encode()).hexdigest(),
                "semantic_sha256": semantic,
                "ordered_comment_sha256": comments,
            }
        )
    if old_text[old_cursor:] != new_text[new_cursor:]:
        raise ValueError("Inline formatting changed non-code spans or fence identities")
    if not blocks:
        raise ValueError("Inline binding has no changed Python block")
    return blocks


def create_inline_record(path: str, before: bytes, after: bytes) -> dict[str, Any]:
    """Retain complete historical guide bytes with independently checked Python parity."""
    _inline_path(path)
    blocks = _inline_blocks(before, after)
    return {
        "path": path,
        "historical_sha256": hashlib.sha256(before).hexdigest(),
        "formatted_sha256": hashlib.sha256(after).hexdigest(),
        "original_bytes": len(before),
        "original_zlib_base64": base64.b64encode(zlib.compress(before, level=9)).decode("ascii"),
        "changed_python_blocks": blocks,
    }


def verify_inline_record(record: dict[str, Any], current: bytes) -> bytes:
    """Return historical bytes only after verifying the complete formatting-only chain."""
    _inline_record_shape(record)
    if not 0 < len(current) <= MAX_INLINE_GUIDE:
        raise ValueError("Current inline Markdown exceeds its byte bound")
    if hashlib.sha256(current).hexdigest() != record["formatted_sha256"]:
        raise ValueError("Inline binding does not match current guide bytes")
    try:
        compressed = base64.b64decode(record["original_zlib_base64"], validate=True)
        decoder = zlib.decompressobj()
        original = decoder.decompress(compressed, MAX_INLINE_GUIDE + 1)
    except (ValueError, zlib.error) as error:
        raise ValueError("Malformed compressed inline source") from error
    if (
        len(original) > MAX_INLINE_GUIDE
        or not decoder.eof
        or decoder.unused_data
        or decoder.unconsumed_tail
        or len(original) != record["original_bytes"]
    ):
        raise ValueError("Compressed inline source violates its byte/stream bound")
    if hashlib.sha256(original).hexdigest() != record["historical_sha256"]:
        raise ValueError("Inline binding does not match original guide bytes")
    if _inline_blocks(original, current) != record["changed_python_blocks"]:
        raise ValueError("Inline block proof differs from independently computed parity")
    return original


def load_inline_records(root: Path) -> dict[str, dict[str, Any]]:
    target = root / INLINE_RECEIPT
    for path in (target, target.parent):
        if path.is_symlink():
            raise ValueError("Inline parity receipt must not be a symlink")
    if not target.exists():
        return {}
    if not target.is_file() or target.stat().st_size > MAX_INLINE_RECEIPT:
        raise ValueError("Inline parity receipt exceeds its byte bound")

    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate inline receipt JSON key")
            result[key] = value
        return result

    def invalid_constant(_: str) -> None:
        raise ValueError("Nonfinite inline receipt JSON value")

    with target.open("rb") as stream:
        raw = stream.read(MAX_INLINE_RECEIPT + 1)
    if len(raw) > MAX_INLINE_RECEIPT:
        raise ValueError("Inline parity receipt exceeds its byte bound")
    payload = json.loads(
        raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=invalid_constant
    )
    if (
        not isinstance(payload, dict)
        or set(payload) != {"schema_version", "evidence_kind", "records"}
        or type(payload["schema_version"]) is not int
        or payload["schema_version"] != 1
        or payload["evidence_kind"] != INLINE_KIND
        or not isinstance(payload["records"], list)
        or len(payload["records"]) > MAX_INLINE_RECORDS
    ):
        raise ValueError("Unknown or malformed inline formatting receipt")
    records = {}
    for record in payload["records"]:
        _inline_record_shape(record)
        if record["path"] in records:
            raise ValueError("Duplicate inline formatting receipt")
        records[record["path"]] = record
    return records


def markdown_before_formatting(
    root: Path, path: str, current: bytes, *, expected_sha256: str | None = None
) -> bytes:
    """Evidence readback only. Execution tests must continue to use current source."""
    _inline_path(path)
    if not 0 < len(current) <= MAX_INLINE_GUIDE:
        raise ValueError("Current inline Markdown exceeds its byte bound")
    record = load_inline_records(root).get(path)
    historical = verify_inline_record(record, current) if record is not None else current
    if expected_sha256 is not None:
        if not _inline_sha(expected_sha256):
            raise ValueError("Invalid expected historical Markdown SHA256")
        if hashlib.sha256(historical).hexdigest() != expected_sha256:
            raise ValueError("Missing or mismatched inline formatting binding for historical guide")
    return historical
