"""Structured exercises, progressive hints and separately revealed solutions.

Guides author exercises in several Markdown layouts: numbered lists with bold
field labels, ``Exercise N`` or ``N. Title`` headings, and separate progressive
hint sections. This module turns those layouts into numbered exercises without
executing anything. Each fragment is rendered by the classroom's existing safe
Markdown renderer. Exercise payloads report only whether a solution exists;
solution text and reference programs are returned only after an explicit reveal.
"""

from __future__ import annotations

import builtins
import json
import re
import symtable
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from ds60sqlpy.lesson_reader import (
    _FENCE_RE,
    _HEADING_RE,
    LinkResolver,
    ReaderTarget,
    _is_fence_closer,
    _strip_html_comments_outside_fences,
    render_markdown,
)
from ds60sqlpy.reader_content import normalize_language

MAX_DOCUMENT_BYTES = 2_000_000
MAX_EXERCISE_NUMBER = 999
MAX_TITLE_CHARACTERS = 120
REVEAL_MESSAGE = "Explicitly reveal a solution after your own attempt."

_EXERCISE_HEADING = re.compile(
    r"^(?:exercise|task|investigation|problem|challenge)\s+(?P<number>\d{1,3})\b"
    r"(?!\s*[-\u2013]\s*\d)\s*[:.)]?\s*(?P<title>.*)$",
    re.IGNORECASE,
)
_NUMBERED_HEADING = re.compile(r"^(?P<number>\d{1,3})[.)]\s+(?P<title>\S.*)$")
_HINT_FOR_HEADING = re.compile(
    r"^hints?\s+(?:for\s+)?(?:investigation|exercise|task|problem)\s+(?P<number>\d{1,3})\b",
    re.IGNORECASE,
)
_HINT_SECTION = re.compile(r"^(?:progressive\s+)?hints?\b", re.IGNORECASE)
_CONTAINER = re.compile(
    r"^(?:[A-Za-z-]+\s+){0,3}?(?:exercises|practice|investigations)\b", re.IGNORECASE
)
_NOT_CONTAINER = re.compile(
    r"\b(?:map|ramp|assumptions?|review method|reasoning lens)\b|^worked\b", re.IGNORECASE
)
_NUMBERED_ITEM = re.compile(r"^(?P<indent>[ \t]*)(?P<number>\d{1,3})[.)][ \t]+(?P<body>\S.*)$")
_LIST_LINE = re.compile(r"^[ \t]*(?:[-+*]|\d{1,9}[.)])[ \t]+\S")
_BULLET_PREFIX = re.compile(r"^[-+*][ \t]+")
_LEADING_LABEL = re.compile(
    r"^\*\*(?P<label>[^*\n]{1,100}?)(?P<mark>:\*\*|\*\*:|\.\*\*|\*\*\.|\?\*\*)[ \t]*(?P<rest>.*)$",
    re.DOTALL,
)
_INLINE_LABEL = re.compile(
    r"(?<!\S)\*\*(?P<label>[A-Za-z][A-Za-z0-9 /,()'-]{0,48}?)(?::\*\*|\*\*:)"
)
_PLAIN_LABEL = re.compile(
    r"(?:(?<=[.!?)])[ \t]+|^)(?P<label>Hint ladder,[ \t]*rung[ \t]+\d{1,2}|Expected evidence|"
    r"Expected result|Expected output|Expected|Progressive hints?|Hints?|Verify|Check):[ \t]+"
)
_CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)+?\1|\\\(.+?\\\)")
_RUNG_SPLIT = re.compile(
    r"(?<=[.!?])[ \t\n]+(?=(?:Then|Next|Finally|Second|Third|Lastly|After that)\b)"
)
_NUMBERED_RUNG = re.compile(r"(?:^|(?<=[;.])[ \t]+)\(\d{1,2}\)[ \t]+")
_RANGE_REFERENCE = re.compile(
    r"\bexercises?\s+(?P<first>\d{1,3})(?:\s*(?:-|\u2013|to|through)\s*(?P<last>\d{1,3}))?"
    r"(?P<more>(?:\s*(?:,|and|&)\s*\d{1,3})*)",
    re.IGNORECASE,
)
_SQL_MARKER = re.compile(r"^--\s*Exercise\s+(?P<number>\d{1,3})\b", re.IGNORECASE)
_SQL_SEPARATOR = re.compile(r"^--\s*-{3,}\s*$")
_SQL_TERMINATOR = re.compile(r"^(?:ROLLBACK|COMMIT|END)\s*;\s*$", re.IGNORECASE)
_FUTURE_IMPORT = re.compile(r"^from[ \t]+__future__[ \t]+import\b")
_CODE_ALIASES = {
    "postgres": "sql",
    "postgresql": "sql",
    "psql": "sql",
    "cs": "csharp",
    "c#": "csharp",
    "golang": "go",
    "rs": "rust",
    "jl": "julia",
    "cuda": "cpp",
    "cu": "cpp",
    "mjs": "javascript",
    "node": "javascript",
    "mts": "typescript",
    "py3": "python",
}
_PROGRAM_LANGUAGES = {
    ".py": "python",
    ".ipynb": "python",
    ".sql": "sql",
    ".hql": "sql",
    ".go": "go",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".cu": "cpp",
    ".java": "java",
    ".cs": "csharp",
    ".rs": "rust",
    ".swift": "swift",
    ".scala": "scala",
    ".js": "javascript",
    ".mjs": "javascript",
    ".ts": "typescript",
    ".mts": "typescript",
    ".r": "r",
    ".jl": "julia",
    ".stan": "stan",
    ".dax": "dax",
    ".php": "php",
}
_DOCUMENT_LANGUAGES = {".html": "html", ".yaml": "yaml", ".yml": "yaml", ".json": "json"}
_MODULE_DUNDERS = frozenset(
    {"__name__", "__file__", "__doc__", "__builtins__", "__spec__", "__loader__", "__package__"}
)


@dataclass(frozen=True, slots=True)
class ExerciseDetail:
    """One authored labeled field, such as an expected result or a check."""

    label: str
    markdown: str


@dataclass(frozen=True, slots=True)
class ParsedExercise:
    """An exercise's own prompt, labeled fields and progressive hints."""

    number: int
    title: str
    prompt: str
    details: tuple[ExerciseDetail, ...]
    hints: tuple[str, ...]
    hints_shared: bool = False


@dataclass(frozen=True, slots=True)
class ParsedGuide:
    """Exercises from one guide plus section guidance that is not one exercise."""

    exercises: tuple[ParsedExercise, ...]
    intro: str
    has_exercise_section: bool


@dataclass(frozen=True, slots=True)
class CodeBlock:
    """Raw source of one fenced code block, ready to copy, run or load."""

    language: str
    text: str


@dataclass(frozen=True, slots=True)
class ReferenceProgram:
    """A complete reference program file from a lesson's solution paths."""

    path: Path
    language: str
    text: str
    standalone: bool


@dataclass(slots=True)
class _Block:
    kind: str
    text: str


@dataclass(slots=True)
class _Field:
    kind: str
    label: str
    parts: list[str] = field(default_factory=list)
    open: bool = False
    rung: int | None = None


@dataclass(slots=True)
class _RawExercise:
    number: int
    heading_title: str | None
    lines: list[str]
    last: bool = False


@dataclass(slots=True)
class _HintRegion:
    specific: dict[int, list[str]] = field(default_factory=dict)
    general: list[str] = field(default_factory=list)
    numbered: list[str] = field(default_factory=list)


# Text structure helpers -----------------------------------------------------


def _lines(text: str) -> list[str]:
    return _strip_html_comments_outside_fences(text).split("\n")


def _headings(lines: Sequence[str]) -> list[tuple[int, int, str]]:
    """Return (line index, level, text) for headings outside fenced code."""

    found: list[tuple[int, int, str]] = []
    marker: str | None = None
    for index, line in enumerate(lines):
        if marker is not None:
            if _is_fence_closer(line, marker):
                marker = None
            continue
        fence = _FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            continue
        heading = _HEADING_RE.match(line)
        if heading:
            found.append((index, len(heading.group(1)), heading.group(2).strip()))
    return found


def _span_end(heads: Sequence[tuple[int, int, str]], position: int, limit: int) -> int:
    """Return the line index ending the heading at ``position`` within ``limit``."""

    _, level, _ = heads[position]
    for index, other_level, _ in heads[position + 1 :]:
        if index >= limit:
            break
        if other_level <= level:
            return index
    return limit


def _mask_code(text: str) -> str:
    """Hide code and inline math so labels inside them are never parsed."""

    return _CODE_SPAN.sub(lambda match: "\x00" * len(match.group()), text)


def _blocks(lines: Sequence[str]) -> list[_Block]:
    """Split dedented Markdown into paragraphs, list runs, fences and field starts."""

    blocks: list[_Block] = []
    current: _Block | None = None
    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        fence = _FENCE_RE.match(raw)
        if fence:
            indent = len(raw) - len(raw.lstrip())
            marker = fence.group(1)
            code = [stripped]
            index += 1
            while index < len(lines):
                line = lines[index]
                content = line[indent:] if line[:indent].strip() == "" else line.lstrip()
                code.append(content)
                index += 1
                if _is_fence_closer(line, marker):
                    break
            blocks.append(_Block("code", "\n".join(code)))
            current = None
            continue
        index += 1
        if not stripped:
            current = None
            continue
        if _field_start(stripped):
            current = _Block("field", _BULLET_PREFIX.sub("", stripped))
            blocks.append(current)
            continue
        if _LIST_LINE.match(raw):
            if current is None or current.kind != "list":
                current = _Block("list", stripped)
                blocks.append(current)
            else:
                current.text += "\n" + stripped
            continue
        if current is None:
            current = _Block("para", stripped)
            blocks.append(current)
        else:
            current.text += ("\n" if current.kind == "list" else " ") + stripped
    return blocks


_DETAIL_LABELS = {
    "input": "Input",
    "inputs": "Input",
    "input/evidence": "Input",
    "inputs/evidence": "Input",
    "inputs and evidence": "Input",
    "expected": "Expected result",
    "expected result": "Expected result",
    "expected results": "Expected result",
    "expected result/shape": "Expected result",
    "expected shape": "Expected result",
    "expected output": "Expected result",
    "expected evidence": "Expected result",
    "expected observation": "Expected result",
    "expected behavior": "Expected result",
    "constraint": "Constraints",
    "constraints": "Constraints",
    "check": "Check",
    "checks": "Check",
    "verify": "Verify",
}
_HINT_LABEL = re.compile(
    r"(?:progressive\s+)?hints?(?:\s+\d{1,2})?|hint\s+ladder(?:,?\s*rung\s+\d{1,2})?"
)


def _field_kind(label: str) -> tuple[str, str] | None:
    """Classify an authored bold label as a hint, a known detail, or neither."""

    text = " ".join(label.strip().rstrip(":.").split()).lower()
    if _HINT_LABEL.fullmatch(text):
        return ("hint", "Hint")
    detail = _DETAIL_LABELS.get(text)
    return None if detail is None else ("detail", detail)


def _short_label(label: str) -> bool:
    words = label.strip().split()
    return 0 < len(words) <= 6 and len(label) <= 48 and not label.rstrip().endswith("?")


def _field_start(line: str) -> bool:
    """Whether a stripped line starts a labeled field rather than continuing prose.

    Known labels may also appear as bullets. Other short colon labels start a
    field only at the left margin, so bold emphasis in prose stays in place.
    """

    candidate = _BULLET_PREFIX.sub("", line)
    leading = _LEADING_LABEL.match(candidate)
    if leading is None or ":" not in leading.group("mark"):
        return False
    if _field_kind(leading.group("label")) is not None:
        return True
    return candidate == line and _short_label(leading.group("label"))


def _plain(text: str) -> str:
    """Return a compact plain-text title from inline Markdown."""

    value = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    pieces = re.split(r"(`+)(.+?)\1", value)
    value = "".join(
        piece
        if position % 3 == 2
        else ""
        if position % 3 == 1
        else re.sub(r"(?<!\w)__(.+?)__(?!\w)", r"\1", piece.replace("**", ""))
        for position, piece in enumerate(pieces)
    )
    value = " ".join(value.split()).strip()
    if value.endswith(".") and not value.endswith(".."):
        value = value[:-1].rstrip()
    if len(value) > MAX_TITLE_CHARACTERS:
        cut = value[: MAX_TITLE_CHARACTERS - 1]
        if " " in cut[40:]:
            cut = cut[: cut.rfind(" ")]
        value = cut.rstrip(" ,;:") + "\u2026"
    return value


def _split_inline(text: str) -> list[tuple[str | None, str]]:
    """Split one paragraph at known bold or plain field labels.

    The first element has no label; it is the text before the first label.
    """

    masked = _mask_code(text)
    cuts: list[tuple[int, int, str]] = []
    for match in _INLINE_LABEL.finditer(masked):
        if _field_kind(match.group("label")) is not None:
            cuts.append((match.start(), match.end(), match.group("label")))
    for match in _PLAIN_LABEL.finditer(masked):
        start = match.start("label")
        if any(left <= start < right for left, right, _ in cuts):
            continue
        cuts.append((start, match.end(), match.group("label")))
    cuts.sort()
    pieces: list[tuple[str | None, str]] = []
    position = 0
    label: str | None = None
    for start, end, name in cuts:
        if start < position:
            continue
        pieces.append((label, text[position:start].strip()))
        label, position = name, end
    pieces.append((label, text[position:].strip()))
    return pieces


def _split_rungs(text: str) -> list[str]:
    """Split a "First ... Then ... Finally ..." paragraph into separate hints."""

    value = text.strip()
    if not re.match(r"First\b", value):
        return [value] if value else []
    masked = _mask_code(value)
    positions = [match.start() for match in _RUNG_SPLIT.finditer(masked)]
    if not positions:
        return [value]
    rungs: list[str] = []
    previous = 0
    for position in positions:
        rungs.append(value[previous:position].strip())
        previous = position
    rungs.append(value[previous:].strip())
    return [rung for rung in rungs if rung]


def _list_items(text: str) -> list[str]:
    """Return top-level items of a Markdown list run, without their markers."""

    items: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        marker = re.match(r"^(?:[-+*]|\d{1,9}[.)])[ \t]+(.*)$", stripped)
        if marker:
            items.append(marker.group(1).strip())
        elif items and stripped:
            items[-1] += " " + stripped
    return [item for item in items if item]


# Exercise bodies --------------------------------------------------------------


def _dedent(lines: Sequence[str]) -> list[str]:
    """Remove list indentation outside fences while keeping fenced code exact."""

    output: list[str] = []
    marker: str | None = None
    indent = 0
    for line in lines:
        if marker is not None:
            output.append(line[indent:] if line[:indent].strip() == "" else line.lstrip())
            if _is_fence_closer(line, marker):
                marker = None
            continue
        fence = _FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            indent = len(line) - len(line.lstrip())
        output.append(line.strip())
    return output


def _parse_body(
    lines: Sequence[str], *, heading_title: str | None, last: bool
) -> tuple[str, list[_Field], list[str], list[str]]:
    """Return (kind label, fields, prompt parts, trailing prose parts)."""

    kind_label = ""
    fields: list[_Field] = []
    prompt: list[str] = []
    trailing: list[str] = []
    current: _Field | None = None
    first = True
    for block in _blocks(_dedent(lines)):
        if block.kind == "code" or block.kind == "list":
            if current is not None:
                current.parts.append(block.text)
            elif fields:
                trailing.append(block.text)
            else:
                prompt.append(block.text)
            first = False
            continue
        text = block.text
        if first and heading_title is None:
            leading = _LEADING_LABEL.match(text)
            if leading and _field_kind(leading.group("label")) is None:
                kind_label = leading.group("label").strip()
                text = leading.group("rest").strip()
        first = False
        pieces = _split_inline(text)
        head_label, head_text = pieces[0]
        if block.kind == "field" and head_label is None and head_text:
            leading = _LEADING_LABEL.match(head_text)
            if leading:
                label = leading.group("label").strip()
                kind = _field_kind(label)
                rest = leading.group("rest").strip()
                current = _Field(kind[0] if kind else "detail", kind[1] if kind else _plain(label))
                current.open = not rest
                if rest:
                    current.parts.append(rest)
                fields.append(current)
                head_text = ""
        if head_text:
            if fields and current is not None and current.open:
                current.parts.append(head_text)
                current.open = False
            elif fields:
                trailing.append(head_text)
                current = None
            else:
                prompt.append(head_text)
        for label, value in pieces[1:]:
            kind = _field_kind(label or "")
            current = _Field(
                kind[0] if kind else "detail", kind[1] if kind else _plain(label or "")
            )
            if label and label.lower().startswith("hint ladder"):
                rung = re.search(r"\d+", label)
                current.rung = int(rung.group()) if rung else 1
            current.open = not value
            if value:
                current.parts.append(value)
            fields.append(current)
    if trailing and not last:
        prompt.extend(trailing)
        trailing = []
    return kind_label, fields, prompt, trailing


def _hints_from_fields(fields: Iterable[_Field]) -> list[str]:
    hints: list[str] = []
    ladder: list[tuple[int, str]] = []
    for item in fields:
        if item.kind != "hint":
            continue
        if item.rung is not None:
            ladder.append((item.rung, " ".join(item.parts)))
            continue
        for part in item.parts:
            if _LIST_LINE.match(part):
                hints.extend(_list_items(part))
            elif _NUMBERED_RUNG.match(part):
                hints.extend(
                    rung.strip(" ;") for rung in _NUMBERED_RUNG.split(part) if rung.strip(" ;")
                )
            else:
                hints.extend(_split_rungs(part))
    hints.extend(text for _, text in sorted(ladder, key=lambda pair: pair[0]))
    return [hint for hint in hints if hint]


def _exercise(raw: _RawExercise) -> tuple[ParsedExercise, str]:
    kind_label, fields, prompt, trailing = _parse_body(
        raw.lines, heading_title=raw.heading_title, last=raw.last
    )
    title = raw.heading_title or kind_label
    prompt_text = "\n\n".join(part for part in prompt if part)
    if not prompt_text:
        prompt_text = raw.heading_title or kind_label
    details = tuple(
        ExerciseDetail(item.label, "\n\n".join(item.parts))
        for item in fields
        if item.kind == "detail" and any(part.strip() for part in item.parts)
    )
    exercise = ParsedExercise(
        number=raw.number,
        title=_plain(title) if title.strip() else f"Exercise {raw.number}",
        prompt=prompt_text,
        details=details,
        hints=tuple(_hints_from_fields(fields)),
    )
    return exercise, "\n\n".join(trailing)


# Guide sections -----------------------------------------------------------------


def _first_list(lines: Sequence[str]) -> tuple[list[str], bool]:
    """Return the items of the first top-level list and whether it is numbered."""

    items: list[str] = []
    numbered = True
    base: int | None = None
    blank = False
    marker: str | None = None
    for line in lines:
        if marker is not None:
            if _is_fence_closer(line, marker):
                marker = None
            continue
        fence = _FENCE_RE.match(line)
        if fence:
            if items:
                break
            marker = fence.group(1)
            continue
        stripped = line.strip()
        item = re.match(
            r"^(?P<indent>[ \t]{0,3})(?P<marker>[-+*]|\d{1,3}[.)])[ \t]+(?P<body>.*)$", line
        )
        if item and (base is None or len(item.group("indent")) <= base):
            base = len(item.group("indent"))
            items.append(item.group("body").strip())
            numbered = numbered and item.group("marker")[0].isdigit()
            blank = False
            continue
        if not items:
            continue
        if not stripped:
            blank = True
            continue
        if blank and not line[:1].isspace():
            break
        items[-1] += " " + stripped
        blank = False
    return [item for item in items if item], numbered and bool(items)


def _unlabeled(item: str) -> str:
    leading = _LEADING_LABEL.match(item)
    if leading and re.fullmatch(r"hint(?:\s+\d{1,2})?", leading.group("label").strip(), re.I):
        return leading.group("rest").strip()
    return item


def _first_paragraph(lines: Sequence[str]) -> str:
    for block in _blocks(_dedent(lines)):
        if block.kind == "para" and not _LEADING_LABEL.match(block.text):
            return block.text
    return ""


def _parse_hint_region(lines: Sequence[str]) -> _HintRegion:
    """Read a separate progressive-hint section into specific and general hints."""

    region = _HintRegion()
    heads = _headings(lines)
    direct_end = heads[0][0] if heads else len(lines)
    for position, (index, _level, text) in enumerate(heads):
        match = _HINT_FOR_HEADING.match(text) or _EXERCISE_HEADING.match(text)
        if match is None:
            continue
        body = lines[index + 1 : _span_end(heads, position, len(lines))]
        items, _numbered = _first_list(body)
        rungs = [_unlabeled(item) for item in items]
        if not rungs:
            rungs = [
                rung
                for block in _blocks(_dedent(body))
                if block.kind in {"para", "field"}
                for rung in _split_rungs(_unlabeled(block.text))
            ]
        region.specific.setdefault(int(match.group("number")), []).extend(rungs)
    items, numbered = _first_list(lines[:direct_end])
    if not items:
        region.general.extend(_split_rungs(_first_paragraph(lines[:direct_end])))
        return region
    for item in items:
        leading = _LEADING_LABEL.match(item)
        label = leading.group("label").strip() if leading else ""
        target = re.fullmatch(
            r"(?:for\s+)?(?:exercise|task|investigation|problem)\s+(\d{1,3})", label, re.I
        )
        if leading and target:
            rest = leading.group("rest").strip()
            region.specific.setdefault(int(target.group(1)), []).extend(_split_rungs(rest))
        elif leading and re.fullmatch(r"hint(?:\s+\d{1,2})?", label, re.I):
            region.general.extend(_split_rungs(leading.group("rest")))
        elif numbered:
            region.numbered.append(item)
        else:
            region.general.append(item)
    return region


def _container_heading(text: str) -> bool:
    return bool(
        _CONTAINER.search(text)
        and not _NOT_CONTAINER.search(text)
        and not _EXERCISE_HEADING.match(text)
        and not _HINT_FOR_HEADING.match(text)
        and not _HINT_SECTION.match(text)
    )


def _hint_heading(text: str) -> bool:
    return _HINT_SECTION.match(text) is not None


def _scan_items(
    lines: Sequence[str], start: int, end: int
) -> tuple[list[tuple[int, int, int, str]], list[tuple[int, int]]]:
    """Find top-level numbered exercise items in an area of a container.

    Returns (start, end, number, first body line) items and the unconsumed ranges.
    """

    items: list[tuple[int, int, int, str]] = []
    base_indent: int | None = None
    marker: str | None = None
    index = start
    current: list[Any] | None = None
    blank = False
    free: list[tuple[int, int]] = []
    free_start = start
    while index < end:
        line = lines[index]
        if marker is not None:
            if _is_fence_closer(line, marker):
                marker = None
            index += 1
            continue
        fence = _FENCE_RE.match(line)
        item = _NUMBERED_ITEM.match(line)
        indent = len(line) - len(line.lstrip())
        if item and (base_indent is None or indent <= base_indent) and indent <= 3:
            if base_indent is None:
                base_indent = indent
            if current is not None:
                current[1] = index
                items.append((current[0], current[1], current[2], current[3]))
            else:
                free.append((free_start, index))
            current = [index, end, int(item.group("number")), item.group("body")]
            blank = False
            index += 1
            continue
        if current is not None:
            stripped = line.strip()
            if not stripped:
                blank = True
            elif blank and indent < 2:
                if not _field_start(stripped):
                    current[1] = index
                    items.append((current[0], current[1], current[2], current[3]))
                    current = None
                    free_start = index
                blank = False
            else:
                blank = False
        if fence:
            marker = fence.group(1)
        index += 1
    if current is not None:
        items.append((current[0], end, current[2], current[3]))
    else:
        free.append((free_start, end))
    return items, free


def _parse_guide_text(text: str) -> ParsedGuide:
    lines = _lines(text)
    heads = _headings(lines)
    containers: list[tuple[int, int]] = []
    covered_until = -1
    for position, (index, level, heading) in enumerate(heads):
        if index < covered_until or level < 2 or not _container_heading(heading):
            continue
        end = _span_end(heads, position, len(lines))
        containers.append((position, end))
        covered_until = end
    has_section = bool(containers)
    raw: list[_RawExercise] = []
    intro_parts: list[str] = []
    hint_regions: list[_HintRegion] = []
    hint_ranges: list[tuple[int, int]] = []
    for position, (index, level, heading) in enumerate(heads):
        inside = any(heads[c][0] < index < end for c, end in containers)
        if level > 1 and _hint_heading(heading) and not _HINT_FOR_HEADING.match(heading):
            if inside:
                continue
            end = _span_end(heads, position, len(lines))
            hint_regions.append(_parse_hint_region(lines[index + 1 : end]))
            hint_ranges.append((index, end))
    if not containers:
        stray = [
            position
            for position, (index, _level, heading) in enumerate(heads)
            if _EXERCISE_HEADING.match(heading)
            and not any(left <= index < right for left, right in hint_ranges)
        ]
        if stray:
            containers = [(-1, len(lines))]
    for container, end in containers:
        start = 0 if container < 0 else heads[container][0] + 1
        before = len(raw)
        notes: list[str] = []
        _scan_container(lines, heads, start, end, raw, notes, hint_regions, top_level=container < 0)
        if len(raw) > before:
            raw[-1].last = True
            intro_parts.extend(notes)
    exercises: list[ParsedExercise] = []
    seen: set[int] = set()
    for item in raw:
        if item.number in seen or not 1 <= item.number <= MAX_EXERCISE_NUMBER:
            continue
        seen.add(item.number)
        exercise, trailing = _exercise(item)
        exercises.append(exercise)
        if trailing:
            intro_parts.append(trailing)
    exercises = _assign_hints(exercises, hint_regions)
    return ParsedGuide(
        exercises=tuple(exercises),
        intro="\n\n".join(part for part in intro_parts if part.strip()),
        has_exercise_section=has_section,
    )


def _scan_container(
    lines: Sequence[str],
    heads: Sequence[tuple[int, int, str]],
    start: int,
    end: int,
    raw: list[_RawExercise],
    intro: list[str],
    hint_regions: list[_HintRegion],
    *,
    top_level: bool,
) -> None:
    """Collect exercises, hint sections and leftover guidance inside a container."""

    inner = [
        (position, index, level, text)
        for position, (index, level, text) in enumerate(heads)
        if start <= index < end
    ]
    cursor = start
    area_heading: str | None = None
    skip_until = -1
    for position, index, level, text in inner:
        if index < skip_until:
            continue
        if cursor < index and not top_level:
            _scan_area(lines, cursor, index, raw, intro, area_heading)
        area_heading = None
        section_end = _span_end(heads, position, end)
        match = _EXERCISE_HEADING.match(text) or (
            None if top_level else _NUMBERED_HEADING.match(text)
        )
        if match is not None:
            title = match.group("title").strip()
            raw.append(
                _RawExercise(
                    int(match.group("number")),
                    title or None,
                    list(lines[index + 1 : section_end]),
                )
            )
            cursor = skip_until = section_end
        elif _hint_heading(text):
            if not top_level:
                nested = _HINT_FOR_HEADING.match(text) is not None
                hint_regions.append(
                    _parse_hint_region(lines[index if nested else index + 1 : section_end])
                )
            cursor = skip_until = section_end
        elif _NOT_CONTAINER.search(text) and _CONTAINER.search(text):
            cursor = skip_until = section_end
        else:
            area_heading = "#" * min(level, 6) + " " + text
            cursor = index + 1
    if cursor < end and not top_level:
        _scan_area(lines, cursor, end, raw, intro, area_heading)


def _scan_area(
    lines: Sequence[str],
    start: int,
    end: int,
    raw: list[_RawExercise],
    intro: list[str],
    heading: str | None,
) -> None:
    items, free = _scan_items(lines, start, end)
    for item_start, item_end, number, body in items:
        raw.append(_RawExercise(number, None, [body, *lines[item_start + 1 : item_end]]))
    text = "\n".join("\n".join(lines[left:right]) for left, right in free).strip()
    if heading and (text or items):
        intro.append(heading)
    if text:
        intro.append(text)


def _assign_hints(
    exercises: list[ParsedExercise], regions: Sequence[_HintRegion]
) -> list[ParsedExercise]:
    if not exercises:
        return exercises
    specific: dict[int, list[str]] = {}
    general: list[str] = []
    numbered: list[str] = []
    for region in regions:
        for number, hints in region.specific.items():
            specific.setdefault(number, []).extend(hints)
        general.extend(region.general)
        numbered.extend(region.numbered)
    output: list[ParsedExercise] = []
    lacking = [item.number for item in exercises if not item.hints and item.number not in specific]
    positional: dict[int, str] = {}
    if numbered and len(numbered) == len(lacking) and not general:
        positional = dict(zip(lacking, numbered, strict=True))
    else:
        general = [*general, *numbered]
    for item in exercises:
        hints = list(item.hints) or specific.get(item.number, [])
        shared = False
        if not hints and item.number in positional:
            hints = [positional[item.number]]
        if not hints and general:
            hints, shared = list(general), True
        output.append(
            ParsedExercise(
                number=item.number,
                title=item.title,
                prompt=item.prompt,
                details=item.details,
                hints=tuple(hints),
                hints_shared=shared,
            )
        )
    return output


# Solutions ------------------------------------------------------------------------


def _referenced_numbers(text: str) -> list[int]:
    numbers: list[int] = []
    for match in _RANGE_REFERENCE.finditer(text):
        first = int(match.group("first"))
        last = int(match.group("last")) if match.group("last") else first
        if last < first or last - first > 50:
            continue
        numbers.extend(range(first, last + 1))
        numbers.extend(int(value) for value in re.findall(r"\d{1,3}", match.group("more") or ""))
    return sorted(set(numbers))


def _parse_solution_text(text: str) -> dict[int, str]:
    """Map exercise numbers to their own solution section plus shared sections."""

    lines = _lines(text)
    heads = _headings(lines)
    direct: dict[int, list[str]] = {}
    shared: dict[int, list[str]] = {}
    for position, (index, _level, heading) in enumerate(heads):
        end = _span_end(heads, position, len(lines))
        match = _EXERCISE_HEADING.match(heading) or _NUMBERED_HEADING.match(heading)
        if match:
            body = "\n".join(lines[index + 1 : end]).strip()
            if body:
                direct.setdefault(int(match.group("number")), []).append(body)
            continue
        numbers = _referenced_numbers(heading)
        if not numbers:
            continue
        nested = any(
            _EXERCISE_HEADING.match(other) or _NUMBERED_HEADING.match(other)
            for other_index, _other_level, other in heads[position + 1 :]
            if other_index < end
        )
        if nested:
            continue
        body = "\n".join(lines[index:end]).strip()
        for number in numbers:
            shared.setdefault(number, []).append(body)
    sections: dict[int, str] = {}
    for number in sorted({*direct, *shared}):
        if not 1 <= number <= MAX_EXERCISE_NUMBER:
            continue
        parts: list[str] = []
        for part in [*direct.get(number, []), *shared.get(number, [])]:
            if part not in parts:
                parts.append(part)
        sections[number] = "\n\n".join(parts)
    return sections


def _parse_sql_blocks(text: str) -> dict[int, str]:
    """Map ``-- Exercise N`` blocks of an executable SQL companion to statements."""

    lines = text.replace("\r\n", "\n").split("\n")
    blocks: dict[int, str] = {}
    index = 0
    while index < len(lines):
        marker = _SQL_MARKER.match(lines[index])
        if marker is None:
            index += 1
            continue
        number = int(marker.group("number"))
        body: list[str] = []
        index += 1
        while index < len(lines):
            line = lines[index]
            if (
                _SQL_MARKER.match(line)
                or _SQL_SEPARATOR.match(line)
                or _SQL_TERMINATOR.match(line.strip())
            ):
                break
            body.append(line)
            index += 1
        while body and (not body[0].strip() or body[0].lstrip().startswith("--")):
            body.pop(0)
        while body and (not body[-1].strip() or body[-1].lstrip().startswith("--")):
            body.pop()
        if body and number not in blocks:
            blocks[number] = "\n".join(body)
    return blocks


def _code_blocks(markdown: str) -> list[CodeBlock]:
    lines = markdown.split("\n")
    blocks: list[CodeBlock] = []
    index = 0
    while index < len(lines):
        fence = _FENCE_RE.match(lines[index])
        if fence is None:
            index += 1
            continue
        marker = fence.group(1)
        info = fence.group(2).strip()
        tag = info.split(maxsplit=1)[0] if info else ""
        code: list[str] = []
        index += 1
        while index < len(lines) and not _is_fence_closer(lines[index], marker):
            code.append(lines[index])
            index += 1
        index += 1
        if tag.lower() != "math":
            blocks.append(CodeBlock(code_language(tag), "\n".join(code)))
    return blocks


def code_language(tag: str) -> str:
    """Normalize a fence or file language tag to a classroom pad language name."""

    value = normalize_language(tag)
    return _CODE_ALIASES.get(value, value)


# Standalone checks ------------------------------------------------------------


def _hoist_future(source: str) -> str:
    lines = source.split("\n")
    future = [line for line in lines if _FUTURE_IMPORT.match(line)]
    if not future:
        return source
    return "\n".join([*future, *(line for line in lines if not _FUTURE_IMPORT.match(line))])


def python_free_names(source: str) -> frozenset[str] | None:
    """Return module-level names a snippet reads but never binds, or None if invalid."""

    hoisted = _hoist_future(source)
    try:
        compile(hoisted, "main.py", "exec", dont_inherit=True)
        table = symtable.symtable(hoisted, "main.py", "exec")
    except (SyntaxError, ValueError, OverflowError, MemoryError, RecursionError):
        return None
    bound: set[str] = set()
    referenced: set[str] = set()
    star = re.search(r"^\s*from\s+\S+\s+import\s+\*", hoisted, re.MULTILINE) is not None

    def visit(scope: symtable.SymbolTable, module: bool) -> None:
        for symbol in scope.get_symbols():
            name = symbol.get_name()
            if module:
                if symbol.is_assigned() or symbol.is_imported() or symbol.is_namespace():
                    bound.add(name)
                if symbol.is_referenced():
                    referenced.add(name)
            elif symbol.is_global():
                if symbol.is_declared_global() and symbol.is_assigned():
                    bound.add(name)
                if symbol.is_referenced():
                    referenced.add(name)
        for child in scope.get_children():
            visit(child, False)

    visit(table, True)
    if star:
        return frozenset()
    return frozenset(referenced - bound - set(dir(builtins)) - _MODULE_DUNDERS)


def is_standalone(language: str, text: str) -> bool:
    """Decide whether source can run on its own in the classroom pad."""

    language = code_language(language)
    if language == "sql":
        return not any(line.lstrip().startswith("\\") for line in text.split("\n"))
    if language == "python":
        free = python_free_names(text)
        return free is not None and not free
    if language == "go":
        return "package main" in text and "func main(" in text
    if language in {"c", "cpp"}:
        return "int main(" in text
    if language == "java":
        return "static void main(" in text
    if language == "csharp":
        return "static void Main(" in text or "static async Task Main(" in text
    if language == "rust":
        return "fn main(" in text
    if language == "scala":
        return "def main(" in text or "@main" in text
    if language == "php":
        return text.lstrip().startswith("<?php")
    return False


# Cached file access -------------------------------------------------------------


def _read(path: Path) -> str:
    size = path.stat().st_size
    if size > MAX_DOCUMENT_BYTES:
        raise ValueError("An authored exercise document exceeds its size limit.")
    return path.read_text(encoding="utf-8")


def _cache_key(path: Path) -> tuple[str, int, int]:
    status = path.stat()
    return str(path), status.st_mtime_ns, status.st_size


@lru_cache(maxsize=512)
def _parsed_guide(path: str, _mtime_ns: int, _size: int) -> ParsedGuide:
    return _parse_guide_text(_read(Path(path)))


@lru_cache(maxsize=512)
def _parsed_solution(path: str, _mtime_ns: int, _size: int) -> dict[int, str]:
    file = Path(path)
    if file.suffix.lower() == ".sql":
        return {}
    return _parse_solution_text(_read(file))


@lru_cache(maxsize=512)
def _parsed_sql(path: str, _mtime_ns: int, _size: int) -> dict[int, str]:
    return _parse_sql_blocks(_read(Path(path)))


@lru_cache(maxsize=256)
def _notebook_source(path: str, _mtime_ns: int, _size: int) -> str:
    payload = json.loads(_read(Path(path)))
    cells = payload.get("cells") if isinstance(payload, dict) else None
    if not isinstance(cells, list):
        return ""
    sources: list[str] = []
    for cell in cells:
        if not isinstance(cell, dict) or cell.get("cell_type") != "code":
            continue
        raw = cell.get("source", "")
        source = "".join(map(str, raw)) if isinstance(raw, list) else str(raw)
        if source.strip():
            sources.append(source.rstrip("\n"))
    return "\n\n".join(sources)


def parse_guide(path: Path) -> ParsedGuide:
    """Parse a guide's exercises, cached by path, modification time and size."""

    return _parsed_guide(*_cache_key(path))


def solution_sections(solutions: Sequence[Path]) -> dict[int, str]:
    """Return Markdown solution sections by exercise number across solution files."""

    sections: dict[int, str] = {}
    for path in solutions:
        if path.suffix.lower() != ".md":
            continue
        for number, markdown in _parsed_solution(*_cache_key(path)).items():
            sections[number] = (
                sections[number] + "\n\n" + markdown if number in sections else markdown
            )
    return sections


def sql_solution_blocks(solutions: Sequence[Path]) -> dict[int, str]:
    """Return executable SQL companion blocks by exercise number."""

    blocks: dict[int, str] = {}
    for path in solutions:
        if path.suffix.lower() == ".sql":
            for number, text in _parsed_sql(*_cache_key(path)).items():
                blocks.setdefault(number, text)
    return blocks


def reference_programs(solutions: Sequence[Path], language: str) -> list[ReferenceProgram]:
    """Return complete reference program files from a lesson's solution paths."""

    programs: list[ReferenceProgram] = []
    documents: list[ReferenceProgram] = []
    for path in solutions:
        kind = _program_kind(path, language)
        if kind == "notebook":
            source = _notebook_source(*_cache_key(path))
            programs.append(
                ReferenceProgram(path, "python", source, is_standalone("python", source))
            )
        elif kind == "program":
            program_language = _PROGRAM_LANGUAGES[path.suffix.lower()]
            text = _read(path)
            standalone = is_standalone("sql", text) if program_language == "sql" else True
            programs.append(ReferenceProgram(path, program_language, text, standalone))
        elif kind == "document":
            documents.append(ReferenceProgram(path, code_language(language), _read(path), False))
    return programs or documents


def has_reference_program(solutions: Sequence[Path], language: str) -> bool:
    """Whether ``reference_programs`` would return a program, without reading programs."""

    return any(_program_kind(path, language) is not None for path in solutions)


def _program_kind(path: Path, language: str) -> str | None:
    suffix = path.suffix.lower()
    if suffix == ".ipynb":
        return "notebook" if _notebook_source(*_cache_key(path)).strip() else None
    if suffix in _PROGRAM_LANGUAGES:
        return "program"
    if suffix in _DOCUMENT_LANGUAGES and _DOCUMENT_LANGUAGES[suffix] == code_language(language):
        return "document"
    return None


# Rendering and payloads -----------------------------------------------------------


def _slug(lesson_id: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", lesson_id.lower()).strip("-") or "lesson"


def _render(
    markdown: str,
    *,
    source: Path,
    repo_root: Path,
    targets: Mapping[Path, ReaderTarget],
    id_prefix: str,
    link_prefix: str | None = None,
) -> str:
    resolver = LinkResolver(
        repo_root=repo_root,
        source_path=source,
        targets=targets,
        fragment_prefix=id_prefix if link_prefix is None else link_prefix,
        output_path="classroom",
    )
    return render_markdown(markdown, resolver=resolver, id_prefix=id_prefix)


def lesson_exercises(
    *,
    lesson_id: str,
    language: str,
    guide: Path,
    solutions: Sequence[Path],
    repo_root: Path,
    targets: Mapping[Path, ReaderTarget],
    guide_link_prefix: str,
) -> dict[str, Any]:
    """Return rendered exercises and hints for one lesson, never solution text."""

    parsed = parse_guide(guide)
    solved = set(solution_sections(solutions)) | set(sql_solution_blocks(solutions))
    slug = _slug(lesson_id)

    def render(markdown: str, prefix: str) -> str:
        return _render(
            markdown,
            source=guide,
            repo_root=repo_root,
            targets=targets,
            id_prefix=prefix,
            link_prefix=guide_link_prefix,
        )

    exercises = []
    for item in parsed.exercises:
        prefix = f"exercise-{slug}-{item.number}--"
        exercises.append(
            {
                "number": item.number,
                "title": item.title,
                "prompt_html": render(item.prompt, prefix + "prompt--"),
                "details": [
                    {
                        "label": detail.label,
                        "html": render(detail.markdown, f"{prefix}detail-{i}--"),
                    }
                    for i, detail in enumerate(item.details, 1)
                ],
                "hints": [
                    render(hint, f"{prefix}hint-{i}--") for i, hint in enumerate(item.hints, 1)
                ],
                "hints_shared": item.hints_shared,
                "has_solution": item.number in solved,
            }
        )
    return {
        "lesson_id": lesson_id,
        "language": language,
        "intro_html": render(parsed.intro, f"exercise-{slug}--intro--") if parsed.intro else "",
        "exercises": exercises,
        "reference_program": has_reference_program(solutions, language),
    }


def exercise_number(value: object) -> int:
    """Validate a requested exercise number."""

    if type(value) is not int or not 1 <= value <= MAX_EXERCISE_NUMBER:
        raise ValueError("Choose an exercise number from this lesson.")
    return value


def exercise_solution(
    *,
    lesson_id: str,
    number: object,
    language: str,
    solutions: Sequence[Path],
    repo_root: Path,
    targets: Mapping[Path, ReaderTarget],
) -> dict[str, Any]:
    """Render one exercise's separate solution and list its raw code blocks."""

    chosen = exercise_number(number)
    sections = solution_sections(solutions)
    markdown = sections.get(chosen, "")
    code = _code_blocks(markdown)
    fallback = sql_solution_blocks(solutions).get(chosen)
    if not code and fallback is not None:
        code = [CodeBlock("sql", fallback)]
        if not markdown:
            markdown = f"```sql\n{fallback}\n```"
    if not markdown:
        raise ValueError(f"Exercise {chosen} has no separate written solution in this lesson.")
    source = next((path for path in solutions if path.suffix.lower() == ".md"), solutions[0])
    pad = code_language(language)
    entries = [
        {
            "language": block.language,
            "text": block.text,
            "standalone": is_standalone(block.language, block.text),
        }
        for block in code
    ]
    same = [entry for entry in entries if entry["language"] == pad]
    joined = "\n\n".join(str(entry["text"]) for entry in same)
    return {
        "number": chosen,
        "html": _render(
            markdown,
            source=source,
            repo_root=repo_root,
            targets=targets,
            id_prefix=f"exercise-{_slug(lesson_id)}-{chosen}--solution--",
        ),
        "code": entries,
        "joined_standalone": bool(same)
        and (all(entry["standalone"] for entry in same) or is_standalone(pad, joined)),
    }


def reference_program_payload(
    *, solutions: Sequence[Path], language: str, repo_root: Path
) -> dict[str, Any]:
    """Return complete reference programs with repository-relative paths."""

    return {
        "programs": [
            {
                "path": program.path.resolve().relative_to(repo_root.resolve()).as_posix(),
                "language": program.language,
                "text": program.text,
                "standalone": program.standalone,
            }
            for program in reference_programs(solutions, language)
        ]
    }
