"""Generate safe, portable HTML readers for every cataloged lesson.

The readers deliberately use only the Python standard library.  They render
checked-in Markdown, notebooks, Python, and SQL into escaped HTML so a learner
can read the complete lesson over ``file://`` without a Markdown extension,
notebook server, or network connection.  Running code still belongs in VS Code,
Jupyter, or PostgreSQL; the optional loopback portal can launch those fixed
targets.
"""

from __future__ import annotations

import html
import json
import posixpath
import re
from collections.abc import Iterable, Mapping
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from textwrap import dedent
from typing import Any
from urllib.parse import quote, unquote, urlsplit

from ds60sqlpy.catalog import Catalog, Lesson

LESSON_PAGES_DIR = "lesson-pages"
REFERENCE_PAGES_DIR = "reference-pages"
COURSE_GUIDE_REFERENCE_PATHS = (
    "README.md",
    "AGENTS.md",
    "docs/content-authoring.md",
    "docs/curriculum-design-references.md",
    "docs/curriculum-map.md",
    "docs/guided-sql-notebooks.md",
    "docs/lesson-readers.md",
    "docs/learning-portal.md",
    "docs/learning-with-codex.md",
    "docs/professional-paths.md",
    "docs/setup/jupyter-postgresql.md",
    "docs/setup/linux.md",
    "docs/setup/macos.md",
    "docs/setup/windows.md",
    "docs/validation.md",
)
_REFERENCE_SUFFIXES = {".md", ".sql"}
_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*([^`]*)$")
_FENCE_LINE_RE = re.compile(r"^[ \t]*(?:`{3,}|~{3,})", re.MULTILINE)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_LIST_RE = re.compile(r"^\s*(?P<marker>[-+*]|\d+[.)])\s+(?P<body>.*)$")
_TABLE_SEPARATOR_RE = re.compile(r"^:?-{3,}:?$")
_LINK_OR_CODE_RE = re.compile(
    r"(?P<code>`+)(?P<code_text>.+?)(?P=code)"
    r"|(?P<image>!)?\[(?P<label>[^\]]*)\]\((?P<target>[^)]+)\)"
)
_SAFE_ID_RE = re.compile(r"[^a-z0-9]+")


def _clean_generated_html(document: str) -> str:
    """Return deterministic HTML with one newline and no trailing whitespace."""

    return "\n".join(line.rstrip() for line in document.splitlines()) + "\n"


@dataclass(frozen=True, slots=True)
class ReaderTarget:
    """Where one repository source appears in the generated HTML set."""

    generated_path: str
    anchor: str


class HeadingIds:
    """Create deterministic, unique fragment identifiers for one document."""

    def __init__(self) -> None:
        self._counts: dict[str, int] = {}

    def next(self, text: str) -> str:
        """Return a GitHub-like lowercase heading ID."""

        plain = re.sub(r"[`*_~]", "", text).lower()
        base = _SAFE_ID_RE.sub("-", plain).strip("-") or "section"
        count = self._counts.get(base, 0)
        self._counts[base] = count + 1
        return base if count == 0 else f"{base}-{count + 1}"


def reader_relative_path(lesson_id: str) -> str:
    """Return the stable generated path for a lesson ID."""

    if not re.fullmatch(r"[a-z0-9-]+", lesson_id):
        raise ValueError(f"Unsafe lesson ID for reader path: {lesson_id}")
    return f"{LESSON_PAGES_DIR}/{lesson_id}.html"


def reference_relative_path(relative_path: str | Path) -> str:
    """Return the stable rendered path for a repository Markdown or SQL file."""

    pure_path = PurePosixPath(Path(relative_path).as_posix())
    if (
        pure_path.is_absolute()
        or not pure_path.parts
        or any(part in {"", ".", ".."} or part.startswith(".") for part in pure_path.parts)
        or pure_path.suffix.lower() not in _REFERENCE_SUFFIXES
    ):
        raise ValueError(f"Unsafe source path for rendered reference: {relative_path}")
    return f"{REFERENCE_PAGES_DIR}/{pure_path.as_posix()}.html"


def artifact_targets(catalog: Catalog) -> dict[Path, ReaderTarget]:
    """Map every catalog artifact to its reader page and section."""

    targets: dict[Path, ReaderTarget] = {}
    for lesson in catalog:
        entries = [
            (lesson.guide_path, "guide"),
            (lesson.lesson_path, "learner"),
            *(
                (solution, f"solution-{index}")
                for index, solution in enumerate(lesson.solution_paths, start=1)
            ),
        ]
        for relative_path, anchor in entries:
            path = catalog.resolve(relative_path)
            if path in targets:
                raise ValueError(f"Catalog artifact appears more than once: {relative_path}")
            targets[path] = ReaderTarget(reader_relative_path(lesson.id), anchor)
    return targets


def _markdown_link_sources(path: Path) -> Iterable[str]:
    """Yield Markdown-bearing source blocks from a rendered artifact."""

    suffix = path.suffix.lower()
    if suffix == ".md":
        yield path.read_text(encoding="utf-8")
        return
    if suffix != ".ipynb":
        return
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    cells = payload.get("cells", [])
    if not isinstance(cells, list):
        return
    for cell in cells:
        if not isinstance(cell, Mapping) or cell.get("cell_type") != "markdown":
            continue
        raw_source = cell.get("source", "")
        yield "".join(map(str, raw_source)) if isinstance(raw_source, list) else str(raw_source)


def _linked_reference_sources(
    source_path: Path,
    source: str,
    *,
    repo_root: Path,
) -> Iterable[Path]:
    """Yield safe local Markdown/SQL link targets rendered by this module."""

    for match in _LINK_OR_CODE_RE.finditer(source):
        if match.group("code") is not None or match.group("image"):
            continue
        raw_target = match.group("target") or ""
        target = _split_markdown_target(raw_target)
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path or "\\" in parts.path:
            continue
        candidate = (source_path.parent / unquote(parts.path)).resolve()
        if (
            candidate.is_relative_to(repo_root)
            and candidate.is_file()
            and candidate.suffix.lower() in _REFERENCE_SUFFIXES
            and not any(part.startswith(".") for part in candidate.relative_to(repo_root).parts)
        ):
            yield candidate


def reference_source_paths(catalog: Catalog) -> tuple[Path, ...]:
    """Return the deterministic closure of non-lesson Markdown/SQL references."""

    repo_root = catalog.repo_root.resolve()
    lesson_targets = artifact_targets(catalog)
    pending: list[Path] = []
    references: set[Path] = set()

    def add_reference(path: Path) -> None:
        resolved = path.resolve()
        if resolved in lesson_targets or resolved in references:
            return
        if (
            not resolved.is_relative_to(repo_root)
            or not resolved.is_file()
            or resolved.suffix.lower() not in _REFERENCE_SUFFIXES
            or any(part.startswith(".") for part in resolved.relative_to(repo_root).parts)
        ):
            raise ValueError(f"Unsafe or missing rendered reference source: {path}")
        references.add(resolved)
        pending.append(resolved)

    for relative_path in COURSE_GUIDE_REFERENCE_PATHS:
        add_reference(repo_root / relative_path)

    for artifact_path in sorted(lesson_targets):
        for source in _markdown_link_sources(artifact_path):
            for linked_path in _linked_reference_sources(
                artifact_path,
                source,
                repo_root=repo_root,
            ):
                add_reference(linked_path)

    while pending:
        source_path = pending.pop()
        for source in _markdown_link_sources(source_path):
            for linked_path in _linked_reference_sources(
                source_path,
                source,
                repo_root=repo_root,
            ):
                add_reference(linked_path)

    return tuple(sorted(references, key=lambda path: path.relative_to(repo_root).as_posix()))


def rendered_targets(catalog: Catalog) -> dict[Path, ReaderTarget]:
    """Map catalog artifacts and linked references to generated HTML pages."""

    targets = artifact_targets(catalog)
    for source_path in reference_source_paths(catalog):
        relative_path = source_path.relative_to(catalog.repo_root)
        targets[source_path] = ReaderTarget(reference_relative_path(relative_path), "")
    return targets


def _split_markdown_target(raw: str) -> str:
    """Discard an optional Markdown link title while preserving angle URLs."""

    value = raw.strip()
    if value.startswith("<") and ">" in value:
        return value[1 : value.index(">")]
    match = re.match(r"""(?P<url>\S+?)(?:\s+["'(].*)?$""", value)
    return match.group("url") if match else value


class LinkResolver:
    """Resolve Markdown links from source artifacts into portable reader links."""

    def __init__(
        self,
        *,
        repo_root: Path,
        source_path: Path,
        targets: Mapping[Path, ReaderTarget],
        fragment_prefix: str = "",
        output_path: str = f"{LESSON_PAGES_DIR}/_reader.html",
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.source_path = source_path.resolve()
        self.targets = targets
        self.fragment_prefix = fragment_prefix
        pure_output = PurePosixPath(output_path)
        if pure_output.is_absolute() or any(part in {"", ".", ".."} for part in pure_output.parts):
            raise ValueError(f"Unsafe generated output path: {output_path}")
        self.output_path = pure_output

    def _relative_url(self, generated_path: str) -> str:
        relative = posixpath.relpath(
            generated_path,
            start=self.output_path.parent.as_posix(),
        )
        return quote(relative, safe="/")

    def href(self, raw_target: str) -> str | None:
        """Return a safe URL relative to a page inside ``lesson-pages``."""

        target = _split_markdown_target(raw_target)
        parts = urlsplit(target)
        if parts.scheme:
            if parts.scheme.lower() in {"http", "https", "mailto"}:
                return target
            return None
        if parts.netloc:
            return None
        if not parts.path:
            if not parts.fragment:
                return "#"
            fragment = _SAFE_ID_RE.sub("-", unquote(parts.fragment).lower()).strip("-")
            return f"#{quote(self.fragment_prefix + fragment)}"

        decoded_path = unquote(parts.path)
        if "\\" in decoded_path:
            return None
        candidate = (self.source_path.parent / decoded_path).resolve()
        if not candidate.is_relative_to(self.repo_root):
            return None

        reader_target = self.targets.get(candidate)
        if reader_target is not None:
            result = self._relative_url(reader_target.generated_path)
            fragment = reader_target.anchor
            if parts.fragment:
                nested = _SAFE_ID_RE.sub("-", unquote(parts.fragment).lower()).strip("-")
                fragment = f"{fragment}--{nested}" if fragment else nested
            if parts.query:
                result += f"?{parts.query}"
            if fragment:
                result += f"#{quote(fragment)}"
            return result

        relative = candidate.relative_to(self.repo_root).as_posix()
        result = self._relative_url(relative)
        if parts.query:
            result += f"?{parts.query}"
        if parts.fragment:
            result += f"#{quote(unquote(parts.fragment))}"
        return result


def _format_plain_inline(text: str) -> str:
    """Escape plain inline text and support a small safe emphasis subset."""

    escaped = html.escape(text, quote=True)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"__(.+?)__", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", escaped)
    escaped = re.sub(r"~~(.+?)~~", r"<del>\1</del>", escaped)
    return escaped


def render_inline(text: str, resolver: LinkResolver) -> str:
    """Render safe inline Markdown."""

    output: list[str] = []
    position = 0
    for match in _LINK_OR_CODE_RE.finditer(text):
        output.append(_format_plain_inline(text[position : match.start()]))
        if match.group("code") is not None:
            output.append(f"<code>{html.escape(match.group('code_text'), quote=True)}</code>")
        else:
            label = render_inline(match.group("label") or "", resolver)
            if match.group("image"):
                output.append(
                    '<span class="image-note" role="note">'
                    f"Image reference: {label or 'unnamed image'}"
                    "</span>"
                )
            else:
                href = resolver.href(match.group("target") or "")
                if href is None:
                    output.append(label)
                else:
                    output.append(f'<a href="{html.escape(href, quote=True)}">{label}</a>')
        position = match.end()
    output.append(_format_plain_inline(text[position:]))
    rendered = "".join(output)
    # Emphasis can intentionally span inline-code or link tokens, for example
    # ``**`pip` installs here:**``. Finish those safe, already-escaped spans
    # after token rendering so Markdown markers do not leak into the reader.
    rendered = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"__(.+?)__", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"~~(.+?)~~", r"<del>\1</del>", rendered)
    return rendered


def _split_table_row(line: str) -> list[str]:
    """Split a simple Markdown table row, respecting escaped pipes."""

    source = line.strip().strip("|")
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for character in source:
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip())
    return cells


def _is_table(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines) or "|" not in lines[index] or "|" not in lines[index + 1]:
        return False
    separators = _split_table_row(lines[index + 1])
    return bool(separators) and all(_TABLE_SEPARATOR_RE.fullmatch(cell) for cell in separators)


def _starts_block(lines: list[str], index: int) -> bool:
    line = lines[index]
    return bool(
        not line.strip()
        or _FENCE_RE.match(line)
        or _HEADING_RE.match(line)
        or _LIST_RE.match(line)
        or line.lstrip().startswith(">")
        or line.strip() in {"---", "***", "___"}
        or _is_table(lines, index)
    )


def _strip_html_comments_outside_fences(source: str) -> str:
    """Remove authoring-only HTML comments without changing fenced examples.

    Markdown comments are useful as stable boundaries for curriculum-maintenance
    scripts, but they are not learner content. The reader intentionally escapes
    raw HTML, so leaving comments in the input would display ``<!-- ... -->`` as
    prose. Strip them before block parsing while preserving comments inside
    fenced code, where they are part of an example the learner should see.
    """

    normalized = source.replace("\r\n", "\n").replace("\r", "\n")
    output: list[str] = []
    fence_marker: str | None = None
    position = 0

    while position < len(normalized):
        at_line_start = position == 0 or normalized[position - 1] == "\n"
        if at_line_start:
            line_end = normalized.find("\n", position)
            if line_end == -1:
                line_end = len(normalized)
            line = normalized[position:line_end]

            if fence_marker is not None:
                output.append(line)
                if line_end < len(normalized):
                    output.append("\n")
                if line.lstrip().startswith(fence_marker[0] * len(fence_marker)):
                    fence_marker = None
                position = line_end + (line_end < len(normalized))
                continue

            fence = _FENCE_RE.match(line)
            if fence:
                fence_marker = fence.group(1)
                output.append(line)
                if line_end < len(normalized):
                    output.append("\n")
                position = line_end + (line_end < len(normalized))
                continue

        if normalized[position] == "`":
            marker_end = position
            while marker_end < len(normalized) and normalized[marker_end] == "`":
                marker_end += 1
            marker = normalized[position:marker_end]
            line_end = normalized.find("\n", marker_end)
            search_end = len(normalized) if line_end == -1 else line_end
            closing = normalized.find(marker, marker_end, search_end)
            if closing != -1:
                closing += len(marker)
                output.append(normalized[position:closing])
                position = closing
                continue

        if normalized.startswith("<!--", position):
            closing = normalized.find("-->", position + 4)
            nested_opening = normalized.find("<!--", position + 4)
            crosses_fence = (
                closing != -1
                and _FENCE_LINE_RE.search(normalized, position + 4, closing) is not None
            )
            if (
                closing != -1
                and (nested_opening == -1 or nested_opening > closing)
                and not crosses_fence
            ):
                position = closing + 3
                continue

        output.append(normalized[position])
        position += 1

    return "".join(output)


def render_markdown(
    source: str,
    *,
    resolver: LinkResolver,
    heading_offset: int = 2,
    id_prefix: str = "",
) -> str:
    """Render a conservative Markdown subset as safe, readable HTML."""

    lines = _strip_html_comments_outside_fences(source).split("\n")
    output: list[str] = []
    heading_ids = HeadingIds()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue

        fence = _FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            language = fence.group(2).strip().split(maxsplit=1)[0] if fence.group(2).strip() else ""
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].lstrip().startswith(
                marker[0] * len(marker)
            ):
                code_lines.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            language_class = (
                f' class="language-{html.escape(language, quote=True)}"' if language else ""
            )
            output.append(
                f"<pre><code{language_class}>"
                f"{html.escape(chr(10).join(code_lines), quote=True)}"
                "</code></pre>"
            )
            continue

        heading = _HEADING_RE.match(line)
        if heading:
            level = min(6, len(heading.group(1)) + heading_offset)
            heading_text = heading.group(2)
            heading_id = id_prefix + heading_ids.next(heading_text)
            output.append(
                f'<h{level} id="{heading_id}">'
                f"{render_inline(heading_text, resolver)}"
                f'<a class="heading-anchor" href="#{heading_id}" aria-label="Link to this section">#</a>'
                f"</h{level}>"
            )
            index += 1
            continue

        if line.strip() in {"---", "***", "___"}:
            output.append("<hr>")
            index += 1
            continue

        if _is_table(lines, index):
            headers = _split_table_row(line)
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip() and "|" in lines[index]:
                rows.append(_split_table_row(lines[index]))
                index += 1
            output.append('<div class="table-wrap"><table><thead><tr>')
            output.extend(f"<th>{render_inline(cell, resolver)}</th>" for cell in headers)
            output.append("</tr></thead><tbody>")
            for row in rows:
                output.append("<tr>")
                padded = row + [""] * max(0, len(headers) - len(row))
                output.extend(
                    f"<td>{render_inline(cell, resolver)}</td>" for cell in padded[: len(headers)]
                )
                output.append("</tr>")
            output.append("</tbody></table></div>")
            continue

        if line.lstrip().startswith(">"):
            quote_lines: list[str] = []
            while index < len(lines) and lines[index].lstrip().startswith(">"):
                quote_lines.append(lines[index].lstrip()[1:].lstrip())
                index += 1
            output.append(
                f"<blockquote>{render_markdown(chr(10).join(quote_lines), resolver=resolver)}</blockquote>"
            )
            continue

        list_match = _LIST_RE.match(line)
        if list_match:
            ordered = list_match.group("marker")[0].isdigit()
            tag = "ol" if ordered else "ul"
            items: list[str] = []
            while index < len(lines):
                current = _LIST_RE.match(lines[index])
                if current is None or current.group("marker")[0].isdigit() != ordered:
                    break
                item_lines = [current.group("body")]
                index += 1
                while (
                    index < len(lines)
                    and lines[index].strip()
                    and not _LIST_RE.match(lines[index])
                    and not _starts_block(lines, index)
                ):
                    item_lines.append(lines[index].strip())
                    index += 1
                items.append(" ".join(item_lines))
            output.append(f"<{tag}>")
            output.extend(f"<li>{render_inline(item, resolver)}</li>" for item in items)
            output.append(f"</{tag}>")
            continue

        paragraph = [line.strip()]
        index += 1
        while index < len(lines) and not _starts_block(lines, index):
            paragraph.append(lines[index].strip())
            index += 1
        output.append(f"<p>{render_inline(' '.join(paragraph), resolver)}</p>")

    return "\n".join(output)


def _render_source_code(source: str, *, language: str) -> str:
    """Render source with copy-friendly CSS line numbers."""

    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    rendered_lines = "\n".join(
        f"<span>{html.escape(line, quote=True) if line else ' '}</span>" for line in lines
    )
    return (
        f'<pre class="source-code language-{html.escape(language, quote=True)}">'
        f"<code>{rendered_lines}</code></pre>"
    )


def _notebook_output_text(output: Mapping[str, Any]) -> tuple[str, str] | None:
    """Return a safe label/text pair for a supported notebook output."""

    output_type = str(output.get("output_type", ""))
    if output_type == "stream":
        raw = output.get("text", "")
        text = "".join(map(str, raw)) if isinstance(raw, list) else str(raw)
        return "Stream output", text
    if output_type == "error":
        traceback = output.get("traceback", [])
        text = "\n".join(map(str, traceback)) if isinstance(traceback, list) else str(traceback)
        return "Error output", text
    if output_type in {"execute_result", "display_data"}:
        data = output.get("data", {})
        if isinstance(data, Mapping) and "text/plain" in data:
            raw = data["text/plain"]
            text = "".join(map(str, raw)) if isinstance(raw, list) else str(raw)
            return "Displayed output", text
    return None


def render_notebook(
    path: Path,
    *,
    repo_root: Path,
    targets: Mapping[Path, ReaderTarget],
    id_prefix: str = "",
    output_path: str = f"{LESSON_PAGES_DIR}/_reader.html",
) -> str:
    """Render notebook cells without executing code or trusting rich output."""

    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    raw_cells = payload.get("cells")
    if not isinstance(raw_cells, list):
        raise ValueError(f"Notebook has no cells list: {path}")
    resolver = LinkResolver(
        repo_root=repo_root,
        source_path=path,
        targets=targets,
        fragment_prefix=id_prefix,
        output_path=output_path,
    )
    output = [
        '<div class="preview-note" role="note"><strong>Readable preview.</strong> '
        "Code cells are not running in this browser page. Use the run controls above "
        "to open the real notebook with the course kernel.</div>"
    ]
    code_count = 0
    markdown_count = 0
    for position, raw_cell in enumerate(raw_cells, start=1):
        if not isinstance(raw_cell, Mapping):
            continue
        cell_type = str(raw_cell.get("cell_type", ""))
        raw_source = raw_cell.get("source", "")
        source = "".join(map(str, raw_source)) if isinstance(raw_source, list) else str(raw_source)
        if cell_type == "markdown":
            markdown_count += 1
            output.append(
                '<article class="notebook-cell markdown-cell">'
                f'<div class="cell-label">Explanation {markdown_count}</div>'
                f"{render_markdown(source, resolver=resolver, heading_offset=2, id_prefix=f'{id_prefix}cell-{position}--')}"
                "</article>"
            )
        elif cell_type == "code":
            code_count += 1
            output.append(
                '<article class="notebook-cell code-cell">'
                f'<div class="cell-label">Code cell {code_count}</div>'
                f"{_render_source_code(source, language='python')}"
            )
            raw_outputs = raw_cell.get("outputs", [])
            if isinstance(raw_outputs, list):
                for raw_output in raw_outputs:
                    if not isinstance(raw_output, Mapping):
                        continue
                    safe_output = _notebook_output_text(raw_output)
                    if safe_output is not None:
                        label, text = safe_output
                        output.append(
                            '<div class="cell-output">'
                            f"<strong>{html.escape(label)}:</strong>"
                            f"<pre><code>{html.escape(text, quote=True)}</code></pre>"
                            "</div>"
                        )
            output.append("</article>")
        elif source.strip():
            output.append(
                '<article class="notebook-cell raw-cell">'
                f'<div class="cell-label">Cell {position}</div>'
                f"{_render_source_code(source, language='text')}"
                "</article>"
            )
    return "\n".join(output)


def render_artifact(
    path: Path,
    *,
    repo_root: Path,
    targets: Mapping[Path, ReaderTarget],
    id_prefix: str = "",
    output_path: str = f"{LESSON_PAGES_DIR}/_reader.html",
) -> str:
    """Render a supported catalog artifact."""

    suffix = path.suffix.lower()
    if suffix == ".md":
        resolver = LinkResolver(
            repo_root=repo_root,
            source_path=path,
            targets=targets,
            fragment_prefix=id_prefix,
            output_path=output_path,
        )
        return render_markdown(
            path.read_text(encoding="utf-8"),
            resolver=resolver,
            id_prefix=id_prefix,
        )
    if suffix == ".ipynb":
        return render_notebook(
            path,
            repo_root=repo_root,
            targets=targets,
            id_prefix=id_prefix,
            output_path=output_path,
        )
    if suffix in {".py", ".sql"}:
        language = "python" if suffix == ".py" else "sql"
        return (
            '<div class="preview-note" role="note"><strong>Readable preview.</strong> '
            "This page does not execute source code. Use the run controls above in the "
            "real course environment.</div>"
            + _render_source_code(path.read_text(encoding="utf-8"), language=language)
        )
    raise ValueError(f"Unsupported catalog artifact type: {path}")


def _path_kind(path: str) -> str:
    suffix = Path(path).suffix.lower()
    return {
        ".ipynb": "Jupyter notebook",
        ".py": "Python source file",
        ".sql": "PostgreSQL script",
        ".md": "lesson notes",
    }.get(suffix, "lesson artifact")


def _run_copy(lesson: Lesson) -> tuple[str, str]:
    """Return tailored runner heading and guidance."""

    suffix = Path(lesson.lesson_path).suffix.lower()
    escaped_path = html.escape(lesson.lesson_path)
    if suffix == ".ipynb":
        return (
            "Run this notebook with the course kernel",
            (
                "Open the real notebook in VS Code or JupyterLab, select "
                "<strong>Python (ds60sqlpy)</strong>, and run cells in order. "
                "The preview below is intentionally read-only."
            ),
        )
    if suffix == ".sql":
        return (
            "Open your guided SQL workspace",
            (
                "In private launcher mode, choose <strong>Create/open guided SQL "
                "notebook</strong>. It opens an editable copy, a safe database-preparation "
                "step, and the real <code>psql -X -v ON_ERROR_STOP=1 -f</code> transcript "
                "in one JupyterLab notebook. The target must be the disposable "
                "<code>advanced_sql_training</code> database—never a shared or valuable one."
            ),
        )
    return (
        "Run this Python file from the repository environment",
        (
            "Open the source in VS Code, read the exercise contract, and run it from "
            "the repository root with the interpreter reported by the setup checker. "
            f"The cataloged path is <code>{escaped_path}</code>."
        ),
    )


def _static_run_help(lesson: Lesson) -> str:
    """Explain the safest runnable handoff when no loopback launcher exists."""

    if lesson.track == "sql":
        return (
            "<strong>If the green SQL-notebook button is not visible, this is reading "
            "mode.</strong><br><strong>Windows:</strong> return to the repository folder "
            "and double-click <code>START_DS60.cmd</code>. Keep its terminal open; the "
            "launcher opens a new private browser page. Find this lesson there and choose "
            "<strong>Create/open guided SQL notebook</strong>.<br>"
            "<strong>macOS/Linux:</strong> from the repository root run "
            "<code>.venv/bin/python scripts/learning_portal.py</code>, then use the new "
            "private browser page. The manual fallback is to open the real "
            "<code>.sql</code> file in VS Code and use the guide's fixed "
            "<code>psql -f</code> command."
        )
    return (
        "Static/USB mode can ask VS Code to open the real file. If your browser does "
        "not recognize that link, open this repository in VS Code and use the printed "
        "catalog path. On Windows, <code>START_DS60.cmd</code> is the guided setup and "
        "launcher route."
    )


def _default_codex_coaching_prompt(lesson: Lesson) -> str:
    """Build a context-rich fallback prompt when a guide has no prompt block."""

    prerequisites = ", ".join(lesson.prerequisites) if lesson.prerequisites else "none"
    execution_boundary = (
        "For runnable work, use only the disposable advanced_sql_training database. "
        "Prefer the lesson reader's Create/open guided SQL notebook action, explain "
        "the expected row grain before execution, and inspect my actual psql transcript."
        if lesson.track == "sql"
        else (
            "For runnable work, use the repository environment and the Python "
            "(ds60sqlpy) kernel. Have me run cells or the cataloged source in order, "
            "then inspect my actual output, assertions, or error."
        )
    )
    return dedent(
        f"""\
        Use $guide-ds60sqlpy-learning to coach me through `{lesson.id}` —
        {lesson.title}.

        Goal:
        Help me understand and demonstrate this lesson's objective. Assume I am a
        complete beginner except for the declared prerequisites: {prerequisites}.

        Repository context:
        - Stable lesson ID: `{lesson.id}`
        - Catalog: `curriculum/catalog.json`
        - Companion guide: `{lesson.guide_path}`
        - Learner artifact: `{lesson.lesson_path}`
        - Applicable instructions: root `AGENTS.md` and the closest track `AGENTS.md`

        Boundaries:
        - Read the catalog entry, guide, and learner artifact first.
        - Do not open, quote, or reproduce anything under `solutions/` until I ask
          for it or show you an honest attempt.
        - Explain every new term in plain language and use a small analogous example
          before asking me to edit the official exercise.
        - {execution_boundary}
        - Give one progressive hint at a time. Do not silently complete the exercise.

        Learning loop:
        1. State the lesson's purpose and mental model in plain language.
        2. Walk through the syntax or query anatomy and ask me to predict an example.
        3. Ask me to attempt one bounded exercise and paste or run my evidence.
        4. Diagnose the first mismatch from that evidence, then give only the next hint.
        5. After I succeed, ask three retrieval questions and one transfer question.

        Done when:
        I can produce a working result, explain why it works in my own words, identify
        one common failure mode, and verify the result without relying on the official
        solution.
        """
    )


def codex_coaching_prompt(catalog: Catalog, lesson: Lesson) -> str:
    """Return the guide's checked-in tutoring prompt, with a safe fallback.

    The companion guide is the authoring source of truth for lesson-specific
    concepts, evidence, and coaching boundaries. Generated HTML must not drift
    into a second, generic prompt merely because the reader is rebuilt.
    """

    guide_path = catalog.resolve(lesson.guide_path)
    with suppress(OSError):
        source = guide_path.read_text(encoding="utf-8")
        heading = re.search(
            r"(?im)^##[ \t]+Ask Codex about this lesson[ \t]*$",
            source,
        )
        if heading:
            remainder = source[heading.end() :]
            next_heading = re.search(r"(?m)^##[ \t]+", remainder)
            section = remainder[: next_heading.start()] if next_heading else remainder
            prompt = re.search(
                r"(?ms)^[ \t]*```text[ \t]*\n(?P<body>.*?)(?:\n)?^[ \t]*```[ \t]*$",
                section,
            )
            if prompt and prompt.group("body").strip():
                return prompt.group("body").strip()

    return _default_codex_coaching_prompt(lesson)


def _sql_run_walkthrough(lesson: Lesson) -> str:
    """Render a concrete first-run path for a SQL lesson reader."""

    if lesson.track != "sql":
        return ""
    workspace = f".learning/sql/{lesson.id}/lesson/"
    return f"""
      <section class="sql-run-guide" aria-labelledby="sql-run-guide-heading">
        <p class="eyebrow">SQL beginner path</p>
        <h2 id="sql-run-guide-heading">From this page to a real query result</h2>
        <p>
          The browser explains the lesson; PostgreSQL executes it. The private
          course portal connects the two safely by creating your own ignored
          workspace at <code>{html.escape(workspace)}</code>.
        </p>
        <ol class="run-steps">
          <li>
            <strong>Start guided mode.</strong>
            <span>On Windows, double-click <code>START_DS60.cmd</code> and keep its
            terminal open. On macOS/Linux, run
            <code>.venv/bin/python scripts/learning_portal.py</code> from the repository root.</span>
          </li>
          <li>
            <strong>Check the database boundary.</strong>
            <span>The readiness check must identify local PostgreSQL and only the
            disposable <code>advanced_sql_training</code> database. Never substitute a
            workplace, shared, or valuable database.</span>
          </li>
          <li>
            <strong>Create the lesson workspace.</strong>
            <span>Return to this lesson over <code>127.0.0.1</code> and click
            <strong>Create/open guided SQL notebook</strong>. JupyterLab opens
            <code>guided.ipynb</code> beside an editable copy of the lesson SQL.</span>
          </li>
          <li>
            <strong>Read, predict, edit, then run.</strong>
            <span>Run the readiness cells first. Open the linked editable
            <code>.sql</code> file, complete one exercise, save it, explicitly confirm
            the course-schema reset, then run the fixed <code>psql -f</code> cell.</span>
          </li>
          <li>
            <strong>Inspect evidence.</strong>
            <span>Results and errors appear in the notebook transcript. Success means
            the command exits cleanly, the course verification cell passes, and you
            can explain the result's columns, row grain, and ordering.</span>
          </li>
        </ol>
        <details>
          <summary><strong>If something fails, start with the first message</strong></summary>
          <dl class="error-map">
            <dt><code>psql was not found</code></dt>
            <dd>Close Jupyter, rerun the course launcher/bootstrap so PostgreSQL is
            discovered, then reopen the notebook from that same portal session.</dd>
            <dt><code>connection refused</code></dt>
            <dd>Start the local PostgreSQL service and rerun the readiness check.</dd>
            <dt><code>database "advanced_sql_training" does not exist</code></dt>
            <dd>Return to setup and create only the disposable course database.</dd>
            <dt><code>relation "training.…" does not exist</code></dt>
            <dd>Read the reset warning, set the notebook's confirmation value to
            <code>True</code>, and rerun the preparation cell before the lesson.</dd>
            <dt><code>ERROR … at line …</code></dt>
            <dd>Fix the first reported error in the editable SQL copy, save the file,
            and run the lesson cell again. Later errors can be consequences of the first.</dd>
          </dl>
        </details>
      </section>
    """


def _artifact_panel(
    *,
    catalog: Catalog,
    targets: Mapping[Path, ReaderTarget],
    lesson: Lesson,
    path_text: str,
    panel_id: str,
    label: str,
    artifact_name: str,
    artifact_kind: str,
    selected: bool,
    output_path: str,
    solution_index: int | None = None,
) -> str:
    path = catalog.resolve(path_text)
    rendered = render_artifact(
        path,
        repo_root=catalog.repo_root,
        targets=targets,
        id_prefix=f"{panel_id}--",
        output_path=output_path,
    )
    data_solution = f' data-solution-index="{solution_index}"' if solution_index is not None else ""
    solution_notice = (
        '<div class="solution-notice" role="note"><strong>Reference solution.</strong> '
        "Attempt the learner work and record your reasoning before comparing answers.</div>"
        if solution_index is not None
        else ""
    )
    return f"""
      <section
        class="artifact-panel"
        id="{panel_id}"
        role="tabpanel"
        aria-labelledby="tab-{panel_id}"
        data-panel="{panel_id}"
        {"data-selected" if selected else ""}
      >
        <header class="artifact-head">
          <div>
            <p class="eyebrow">{html.escape(label)}</p>
            <h2>{html.escape(artifact_name)}</h2>
            <p class="artifact-path"><code>{html.escape(path_text)}</code></p>
          </div>
          <div class="artifact-actions">
            <a class="button secondary" href="#" data-vscode-path="{html.escape(path_text, quote=True)}">
              Open this file in VS Code
            </a>
            <button
              class="button launcher-only"
              type="button"
              data-launch-artifact="{html.escape(artifact_name, quote=True)}"
              data-artifact-kind="{html.escape(artifact_kind, quote=True)}"
              {data_solution}
              hidden
            >Open with guided launcher</button>
          </div>
        </header>
        {solution_notice}
        <div class="artifact-content">{rendered}</div>
      </section>
    """


def _safe_script_json(value: str) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def build_lesson_html(
    catalog: Catalog,
    lesson: Lesson,
    *,
    targets: Mapping[Path, ReaderTarget] | None = None,
) -> str:
    """Build one complete self-contained lesson reader."""

    artifact_map = dict(targets or rendered_targets(catalog))
    output_path = reader_relative_path(lesson.id)
    lessons = list(catalog)
    position = lessons.index(lesson)
    previous_lesson = lessons[position - 1] if position > 0 else None
    next_lesson = lessons[position + 1] if position + 1 < len(lessons) else None
    previous_link = (
        f'<a class="nav-card" href="{previous_lesson.id}.html">'
        f"<small>Previous lesson</small><strong>{html.escape(previous_lesson.id)}</strong>"
        f"<span>{html.escape(previous_lesson.title)}</span></a>"
        if previous_lesson
        else '<span class="nav-card disabled"><small>Previous lesson</small><strong>Course start</strong></span>'
    )
    next_link = (
        f'<a class="nav-card next" href="{next_lesson.id}.html">'
        f"<small>Next lesson</small><strong>{html.escape(next_lesson.id)}</strong>"
        f"<span>{html.escape(next_lesson.title)}</span></a>"
        if next_lesson
        else '<span class="nav-card next disabled"><small>Next lesson</small><strong>Course complete</strong></span>'
    )
    prerequisites = (
        " ".join(
            f'<a class="tag" href="{prerequisite}.html">{html.escape(prerequisite)}</a>'
            for prerequisite in lesson.prerequisites
        )
        if lesson.prerequisites
        else '<span class="tag">None</span>'
    )
    run_heading, run_guidance = _run_copy(lesson)
    solution_tabs = "\n".join(
        f'<a id="tab-solution-{index}" role="tab" aria-selected="false" '
        f'aria-controls="solution-{index}" href="#solution-{index}" data-tab="solution-{index}">'
        f"Solution {index}</a>"
        for index, _ in enumerate(lesson.solution_paths, start=1)
    )
    solution_panels = "\n".join(
        _artifact_panel(
            catalog=catalog,
            targets=artifact_map,
            lesson=lesson,
            path_text=solution_path,
            panel_id=f"solution-{index}",
            label=f"Reference solution {index}",
            artifact_name=_path_kind(solution_path),
            artifact_kind="solution",
            selected=False,
            output_path=output_path,
            solution_index=index - 1,
        )
        for index, solution_path in enumerate(lesson.solution_paths, start=1)
    )
    guide_panel = _artifact_panel(
        catalog=catalog,
        targets=artifact_map,
        lesson=lesson,
        path_text=lesson.guide_path,
        panel_id="guide",
        label="Understand the concept",
        artifact_name="Companion guide",
        artifact_kind="guide",
        selected=True,
        output_path=output_path,
    )
    learner_panel = _artifact_panel(
        catalog=catalog,
        targets=artifact_map,
        lesson=lesson,
        path_text=lesson.lesson_path,
        panel_id="learner",
        label="Practice actively",
        artifact_name=_path_kind(lesson.lesson_path),
        artifact_kind="lesson",
        selected=False,
        output_path=output_path,
    )
    lesson_id_json = _safe_script_json(lesson.id)
    lesson_path_json = _safe_script_json(lesson.lesson_path)
    static_run_help = _static_run_help(lesson)
    codex_prompt = html.escape(codex_coaching_prompt(catalog, lesson))
    sql_run_walkthrough = _sql_run_walkthrough(lesson)
    notebook_action = (
        '<button class="button launcher-only" type="button" id="launch-jupyter" hidden>'
        "Open this notebook in JupyterLab</button>"
        if Path(lesson.lesson_path).suffix.lower() == ".ipynb"
        else ""
    )
    sql_notebook_action = (
        '<button class="button launcher-only" type="button" id="launch-sql-notebook" hidden>'
        "Create/open guided SQL notebook</button>"
        if lesson.track == "sql"
        else ""
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <meta
    http-equiv="Content-Security-Policy"
    content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src data:; form-action 'none'"
  >
  <title>{html.escape(lesson.id)} · {html.escape(lesson.title)} · DS60</title>
  <style>
    :root {{
      --paper: #f6f2e8;
      --surface: #fffdf8;
      --ink: #17221e;
      --muted: #59655f;
      --line: #d7d7ca;
      --navy: #173f5f;
      --navy-soft: #e8f0f5;
      --green: #0f6b4f;
      --green-soft: #e4f3ec;
      --gold: #9d6515;
      --gold-soft: #f7ead2;
      --red: #9c3f35;
      --shadow: 0 18px 46px rgb(28 45 37 / 10%);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    [hidden] {{ display: none !important; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at 0 0, rgb(15 107 79 / 10%), transparent 25rem),
        radial-gradient(circle at 100% 3rem, rgb(23 63 95 / 11%), transparent 29rem),
        var(--paper);
      line-height: 1.6;
    }}
    a {{ color: var(--navy); text-underline-offset: .18em; }}
    a:hover {{ color: var(--green); }}
    button, input {{ font: inherit; }}
    code, pre {{ font-family: "Cascadia Code", "SFMono-Regular", Consolas, monospace; }}
    code {{ border-radius: .35rem; padding: .08rem .3rem; background: rgb(23 63 95 / 8%); }}
    .shell {{ width: min(1120px, calc(100% - 2rem)); margin-inline: auto; }}
    .skip-link {{
      position: fixed; z-index: 100; top: .5rem; left: .5rem; transform: translateY(-160%);
      border-radius: .5rem; padding: .65rem 1rem; color: #fff; background: var(--navy);
    }}
    .skip-link:focus {{ transform: translateY(0); }}
    :focus-visible {{ outline: 3px solid #efb74c; outline-offset: 3px; }}
    .topbar {{
      position: sticky; z-index: 20; top: 0; border-bottom: 1px solid rgb(215 215 202 / 80%);
      background: rgb(246 242 232 / 92%); backdrop-filter: blur(14px);
    }}
    .topbar .shell {{
      display: flex; min-height: 4rem; align-items: center; justify-content: space-between; gap: 1rem;
    }}
    .brand {{ color: var(--ink); font-weight: 850; text-decoration: none; }}
    .brand span {{
      display: inline-grid; width: 2.25rem; height: 2.25rem; place-items: center; margin-right: .55rem;
      border-radius: .65rem; color: #fff; background: linear-gradient(145deg, var(--navy), var(--green));
      font-size: .73rem; letter-spacing: .04em;
    }}
    .top-actions {{ display: flex; align-items: center; gap: .7rem; }}
    .completion {{ display: flex; align-items: center; gap: .4rem; color: var(--muted); font-size: .86rem; font-weight: 750; }}
    .completion input {{ width: 1.05rem; height: 1.05rem; accent-color: var(--green); }}
    .hero {{ padding: clamp(2.5rem, 7vw, 5.5rem) 0 2.5rem; }}
    .eyebrow {{ margin: 0 0 .5rem; color: var(--green); font-size: .78rem; font-weight: 850; letter-spacing: .12em; text-transform: uppercase; }}
    h1, h2, h3, h4, h5, h6 {{ line-height: 1.18; text-wrap: balance; }}
    h1 {{ max-width: 19ch; margin: .55rem 0 1rem; font-size: clamp(2.4rem, 6vw, 5rem); letter-spacing: -.055em; }}
    h2 {{ margin-top: 0; font-size: clamp(1.7rem, 3vw, 2.55rem); letter-spacing: -.035em; }}
    h3 {{ margin-top: 2.2rem; font-size: 1.45rem; letter-spacing: -.02em; }}
    h4 {{ margin-top: 1.7rem; font-size: 1.2rem; }}
    .hero-copy {{ max-width: 68ch; color: var(--muted); font-size: 1.08rem; }}
    .meta, .prerequisite-list {{ display: flex; flex-wrap: wrap; gap: .4rem; margin: 1rem 0; }}
    .tag {{
      display: inline-flex; border: 1px solid var(--line); border-radius: 999px; padding: .2rem .55rem;
      color: var(--muted); background: var(--surface); font-size: .76rem; text-decoration: none;
    }}
    .run-card {{
      display: grid; grid-template-columns: 1fr auto; align-items: center; gap: 1.5rem;
      border: 1px solid #79aa94; border-radius: 20px; padding: clamp(1.2rem, 3vw, 2rem);
      background: linear-gradient(135deg, var(--surface), var(--green-soft)); box-shadow: var(--shadow);
    }}
    .run-card h2 {{ margin-bottom: .55rem; font-size: 1.65rem; }}
    .run-card p {{ max-width: 70ch; margin: 0; color: var(--muted); }}
    .run-actions, .artifact-actions {{ display: flex; flex-wrap: wrap; justify-content: flex-end; gap: .55rem; }}
    .button {{
      display: inline-flex; min-height: 2.65rem; align-items: center; justify-content: center;
      border: 1px solid var(--navy); border-radius: 999px; padding: .55rem 1rem;
      color: #fff; background: var(--navy); cursor: pointer; font-weight: 760; text-decoration: none;
    }}
    .button:hover {{ color: #fff; background: var(--green); border-color: var(--green); }}
    .button.secondary {{ color: var(--navy); background: transparent; }}
    .button.secondary:hover {{ color: #fff; background: var(--navy); }}
    .launcher-status {{ margin: .75rem 0 0; color: var(--muted); font-size: .85rem; }}
    .static-help {{ margin: .8rem 0 0; color: var(--muted); font-size: .82rem; }}
    .sql-run-guide {{
      margin: 1rem 0 2rem; border: 1px solid #8eac9e; border-radius: 20px;
      padding: clamp(1.2rem, 3vw, 2rem); background: var(--surface); box-shadow: var(--shadow);
    }}
    .sql-run-guide > p:not(.eyebrow) {{ max-width: 80ch; color: var(--muted); }}
    .run-steps {{ display: grid; gap: .75rem; padding: 0; list-style: none; counter-reset: sql-step; }}
    .run-steps li {{
      display: grid; grid-template-columns: 2rem minmax(9rem, .36fr) 1fr; gap: .8rem;
      align-items: start; border: 1px solid var(--line); border-radius: 13px;
      padding: .85rem; background: #fff; counter-increment: sql-step;
    }}
    .run-steps li::before {{
      display: grid; width: 2rem; height: 2rem; place-items: center; border-radius: 50%;
      color: #fff; background: var(--green); font-weight: 850; content: counter(sql-step);
    }}
    .run-steps span {{ color: var(--muted); }}
    .sql-run-guide details {{ margin-top: 1rem; border-top: 1px solid var(--line); padding-top: 1rem; }}
    .sql-run-guide summary {{ cursor: pointer; color: var(--navy); }}
    .error-map {{ display: grid; grid-template-columns: minmax(12rem, .35fr) 1fr; gap: .65rem 1rem; }}
    .error-map dt {{ font-weight: 780; }}
    .error-map dd {{ margin: 0; color: var(--muted); }}
    .sequence {{
      display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; margin: 1.25rem 0 2.5rem;
    }}
    .sequence article {{ border: 1px solid var(--line); border-radius: 14px; padding: 1rem; background: var(--surface); }}
    .sequence strong {{ display: block; margin-bottom: .25rem; }}
    .sequence span {{ color: var(--muted); font-size: .88rem; }}
    .coach-card {{
      margin: 0 0 2.5rem; border: 1px solid #89a7be; border-radius: 20px;
      padding: clamp(1.2rem, 3vw, 2rem); background: linear-gradient(135deg, var(--surface), var(--navy-soft));
      box-shadow: var(--shadow);
    }}
    .coach-grid {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 1rem; align-items: end; }}
    .coach-card h2 {{ margin-bottom: .55rem; font-size: 1.65rem; }}
    .coach-card p {{ max-width: 78ch; color: var(--muted); }}
    .codex-prompt {{
      width: 100%; min-height: 20rem; resize: vertical; border: 1px solid var(--line);
      border-radius: 12px; padding: 1rem; color: var(--ink); background: #fff;
      font-family: "Cascadia Code", "SFMono-Regular", Consolas, monospace;
      font-size: .82rem; line-height: 1.5;
    }}
    .copy-status {{ min-height: 1.3rem; margin: .55rem 0 0; color: var(--muted); font-size: .82rem; }}
    .tabs {{
      position: sticky; z-index: 10; top: 4rem; display: flex; overflow-x: auto; gap: .4rem;
      border: 1px solid var(--line); border-radius: 14px; padding: .5rem; background: rgb(255 253 248 / 94%);
      box-shadow: 0 8px 25px rgb(28 45 37 / 8%); backdrop-filter: blur(12px);
    }}
    .tabs a {{
      flex: 0 0 auto; border-radius: 9px; padding: .55rem .8rem; color: var(--muted);
      font-size: .86rem; font-weight: 780; text-decoration: none;
    }}
    .tabs a[aria-selected="true"] {{ color: #fff; background: var(--navy); }}
    .artifact-panel {{
      scroll-margin-top: 9rem; margin: 1rem 0 2rem; border: 1px solid var(--line);
      border-radius: 20px; padding: clamp(1rem, 3vw, 2rem); background: var(--surface); box-shadow: var(--shadow);
    }}
    .tabs-ready .artifact-panel:not([data-selected]) {{ display: none; }}
    .artifact-head {{ display: flex; align-items: start; justify-content: space-between; gap: 1.2rem; border-bottom: 1px solid var(--line); padding-bottom: 1rem; }}
    .artifact-head h2 {{ margin-bottom: .35rem; }}
    .artifact-path {{ margin: 0; color: var(--muted); font-size: .82rem; overflow-wrap: anywhere; }}
    .artifact-content {{ max-width: 88ch; margin: 1.7rem auto 0; }}
    .artifact-content p, .artifact-content li {{ color: #26332d; }}
    .artifact-content img {{ max-width: 100%; }}
    .heading-anchor {{ margin-left: .4rem; color: var(--line); font-size: .75em; text-decoration: none; }}
    .artifact-content h3:hover .heading-anchor,
    .artifact-content h4:hover .heading-anchor {{ color: var(--green); }}
    pre {{
      overflow: auto; border: 1px solid #294958; border-radius: 12px; padding: 1rem;
      color: #eaf4ef; background: #152d35; line-height: 1.55; white-space: pre;
    }}
    pre code {{ padding: 0; color: inherit; background: transparent; }}
    .source-code {{ padding: 1rem 0; }}
    .source-code code {{ display: block; counter-reset: source-line; }}
    .source-code code > span {{ display: block; min-height: 1.55em; padding: 0 1rem 0 4.2rem; }}
    .source-code code > span::before {{
      float: left; width: 2.8rem; margin-left: -3.5rem; color: #81a0a8; text-align: right;
      counter-increment: source-line; content: counter(source-line); user-select: none;
    }}
    .source-code code > span:target, .source-code code > span:hover {{ background: rgb(255 255 255 / 6%); }}
    .notebook-cell {{ margin: 1rem 0; border: 1px solid var(--line); border-radius: 13px; padding: 1rem; background: #fff; }}
    .markdown-cell {{ border-left: 4px solid var(--green); }}
    .code-cell {{ border-left: 4px solid var(--navy); }}
    .cell-label {{ margin-bottom: .5rem; color: var(--muted); font-family: "Cascadia Code", Consolas, monospace; font-size: .72rem; font-weight: 780; text-transform: uppercase; }}
    .cell-output {{ margin-top: .7rem; }}
    .preview-note, .solution-notice {{
      border-left: 4px solid var(--gold); border-radius: 0 10px 10px 0; padding: .8rem 1rem;
      color: #594217; background: var(--gold-soft);
    }}
    .solution-notice {{ margin-top: 1rem; }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid var(--line); padding: .65rem; text-align: left; vertical-align: top; }}
    th {{ background: var(--navy-soft); }}
    blockquote {{ margin-left: 0; border-left: 4px solid var(--navy); padding: .2rem 1rem; color: var(--muted); background: var(--navy-soft); }}
    .image-note {{ display: inline-block; border: 1px dashed var(--line); border-radius: .4rem; padding: .15rem .4rem; color: var(--muted); }}
    .lesson-nav {{ display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; margin: 2rem 0 4rem; }}
    .nav-card {{ display: grid; border: 1px solid var(--line); border-radius: 14px; padding: 1rem; background: var(--surface); text-decoration: none; }}
    .nav-card small {{ color: var(--muted); }}
    .nav-card span {{ color: var(--muted); font-size: .88rem; }}
    .nav-card.next {{ text-align: right; }}
    .nav-card.disabled {{ opacity: .65; }}
    footer {{ border-top: 1px solid var(--line); padding: 2rem 0; color: var(--muted); font-size: .85rem; }}
    @media (max-width: 760px) {{
      .top-actions .completion {{ display: none; }}
      .run-card, .sequence, .coach-grid, .run-steps li, .error-map, .lesson-nav {{ grid-template-columns: 1fr; }}
      .run-steps li::before {{ margin-bottom: .15rem; }}
      .run-actions, .artifact-actions {{ justify-content: flex-start; }}
      .artifact-head {{ display: block; }}
      .artifact-actions {{ margin-top: 1rem; }}
      .nav-card.next {{ text-align: left; }}
    }}
    @media print {{
      .topbar, .run-card, .coach-card, .tabs, .artifact-actions, .lesson-nav, footer {{ display: none !important; }}
      body {{ background: #fff; }}
      .artifact-panel {{ display: block !important; border: 0; box-shadow: none; break-before: page; }}
      .solution-notice {{ break-after: avoid; }}
    }}
  </style>
</head>
<body>
  <a class="skip-link" href="#lesson-content">Skip to lesson</a>
  <header class="topbar">
    <div class="shell">
      <a class="brand" href="../START_HERE.html#catalog"><span>DS60</span>Learning guide</a>
      <div class="top-actions">
        <label class="completion launcher-only" hidden>
          <input id="lesson-complete" type="checkbox">
          Mark complete
        </label>
        <a class="static-only" href="../START_HERE.html#catalog">
          Track completion on the course dashboard
        </a>
        <a href="../START_HERE.html#catalog">All lessons</a>
      </div>
    </div>
  </header>

  <main id="lesson-content">
    <div class="shell">
      <section class="hero">
        <p class="eyebrow">{html.escape(lesson.track)} · lesson {html.escape(lesson.id)}</p>
        <h1>{html.escape(lesson.title)}</h1>
        <p class="hero-copy">{html.escape(lesson.phase)}</p>
        <div class="meta">
          <span class="tag">{html.escape(lesson.level)}</span>
          <span class="tag">{lesson.estimated_minutes} minutes</span>
          <span class="tag">{html.escape(lesson.dependency_group)} setup</span>
          <span class="tag">{html.escape(lesson.network)}</span>
        </div>
        <p><strong>Prerequisites:</strong></p>
        <div class="prerequisite-list">{prerequisites}</div>
      </section>

      <section class="run-card" aria-labelledby="run-heading">
        <div>
          <p class="eyebrow">Your working copy</p>
          <h2 id="run-heading">{html.escape(run_heading)}</h2>
          <p>{run_guidance}</p>
          <div class="static-help">
            {static_run_help}
          </div>
          <p class="launcher-status" id="launcher-status" aria-live="polite"></p>
        </div>
        <div class="run-actions">
          <a class="button" href="#" data-vscode-path="{html.escape(lesson.lesson_path, quote=True)}">
            Open learner artifact in VS Code
          </a>
          <button class="button launcher-only" type="button" id="launch-learner" hidden>
            Open with guided launcher
          </button>
          {notebook_action}
          {sql_notebook_action}
        </div>
      </section>

      {sql_run_walkthrough}

      <div class="sequence" aria-label="Recommended learning sequence">
        <article><strong>1 · Understand</strong><span>Read the guide and predict the worked examples.</span></article>
        <article><strong>2 · Practice</strong><span>Open the learner artifact and run or query it in the course environment.</span></article>
        <article><strong>3 · Reflect</strong><span>Compare solutions only after an honest attempt, then explain the difference.</span></article>
      </div>

      <nav class="tabs" role="tablist" aria-label="Lesson materials">
        <a id="tab-guide" role="tab" aria-selected="true" aria-controls="guide" href="#guide" data-tab="guide">Guide</a>
        <a id="tab-learner" role="tab" aria-selected="false" aria-controls="learner" href="#learner" data-tab="learner">Learner artifact</a>
        {solution_tabs}
      </nav>

      {guide_panel}
      {learner_panel}
      {solution_panels}

      <section class="coach-card" aria-labelledby="coach-heading">
        <p class="eyebrow">Optional learning coach · after reading the guide</p>
        <h2 id="coach-heading">Ask Codex about this lesson</h2>
        <p>
          The lesson is complete without Codex. If this repository is open in Codex,
          copy the prompt below to get a context-aware explanation, progressive hints,
          and evidence-based review without opening the official solution too early.
        </p>
        <div class="coach-grid">
          <label>
            <span class="cell-label">Copy-ready lesson prompt</span>
            <textarea class="codex-prompt" id="codex-prompt" readonly>{codex_prompt}</textarea>
          </label>
          <button class="button" type="button" id="copy-codex-prompt">Copy Codex prompt</button>
        </div>
        <p class="copy-status" id="copy-status" aria-live="polite"></p>
      </section>

      <nav class="lesson-nav" aria-label="Previous and next lessons">
        {previous_link}
        {next_link}
      </nav>
    </div>
  </main>

  <footer>
    <div class="shell">
      Generated from checked-in course artifacts · readable offline · run code only in the course environment
    </div>
  </footer>

  <script>
    "use strict";
    const LESSON_ID = {lesson_id_json};
    const LEARNER_PATH = {lesson_path_json};
    const STORAGE_KEY = "ds60sqlpy.portable-guide.v1";
    const SERVER_TOKEN = "";
    const launcherMode = Boolean(
      SERVER_TOKEN &&
      location.protocol === "http:" &&
      location.hostname === "127.0.0.1"
    );

    document.documentElement.classList.add("tabs-ready");
    const panels = [...document.querySelectorAll("[data-panel]")];
    const tabs = [...document.querySelectorAll("[data-tab]")];

    function activatePanel(panelId, focusTab = false) {{
      const selected = panels.some((panel) => panel.id === panelId) ? panelId : "guide";
      panels.forEach((panel) => {{
        panel.toggleAttribute("data-selected", panel.id === selected);
      }});
      tabs.forEach((tab) => {{
        const active = tab.dataset.tab === selected;
        tab.setAttribute("aria-selected", String(active));
        tab.tabIndex = active ? 0 : -1;
        if (active && focusTab) tab.focus();
      }});
    }}

    function panelFromHash() {{
      return decodeURIComponent(location.hash.slice(1)).split("--")[0] || "guide";
    }}

    function activateFromHash() {{
      activatePanel(panelFromHash());
      const exactTarget = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (exactTarget && !exactTarget.matches("[data-panel]")) {{
        requestAnimationFrame(() => exactTarget.scrollIntoView({{ block: "start" }}));
      }}
    }}

    tabs.forEach((tab, index) => {{
      tab.addEventListener("click", () => activatePanel(tab.dataset.tab));
      tab.addEventListener("keydown", (event) => {{
        if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        let nextIndex = index;
        if (event.key === "ArrowLeft") nextIndex = (index - 1 + tabs.length) % tabs.length;
        if (event.key === "ArrowRight") nextIndex = (index + 1) % tabs.length;
        if (event.key === "Home") nextIndex = 0;
        if (event.key === "End") nextIndex = tabs.length - 1;
        const nextTab = tabs[nextIndex];
        location.hash = nextTab.dataset.tab;
        activatePanel(nextTab.dataset.tab, true);
      }});
    }});
    window.addEventListener("hashchange", activateFromHash);
    activateFromHash();

    function fileUrlFor(relativePath) {{
      return new URL("../" + relativePath.split("/").map(encodeURIComponent).join("/"), location.href);
    }}

    function vscodeUrlFor(relativePath) {{
      const fileUrl = fileUrlFor(relativePath);
      const host = fileUrl.host ? "//" + fileUrl.host : "";
      return "vscode://file" + host + fileUrl.pathname;
    }}

    document.querySelectorAll("[data-vscode-path]").forEach((link) => {{
      if (location.protocol !== "file:") {{
        link.hidden = true;
      }} else try {{
        link.href = vscodeUrlFor(link.dataset.vscodePath);
      }} catch {{
        link.removeAttribute("href");
        link.setAttribute("aria-disabled", "true");
      }}
    }});

    const codexPrompt = document.querySelector("#codex-prompt");
    const copyStatus = document.querySelector("#copy-status");
    document.querySelector("#copy-codex-prompt").addEventListener("click", async () => {{
      codexPrompt.focus();
      codexPrompt.select();
      try {{
        if (navigator.clipboard && window.isSecureContext) {{
          await navigator.clipboard.writeText(codexPrompt.value);
        }} else if (!document.execCommand("copy")) {{
          throw new Error("copy command was unavailable");
        }}
        copyStatus.textContent = "Prompt copied. Paste it into a Codex task opened at the repository root.";
      }} catch {{
        copyStatus.textContent = "Automatic copy was blocked. The prompt is selected; use Ctrl+C or Cmd+C.";
      }}
    }});

    function readProgress() {{
      try {{
        const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
        return value && Array.isArray(value.completed) ? value : {{ completed: [], setup: {{}}, os: "windows" }};
      }} catch {{
        return {{ completed: [], setup: {{}}, os: "windows" }};
      }}
    }}

    function writeProgress(complete) {{
      const state = readProgress();
      const completed = new Set(state.completed);
      complete ? completed.add(LESSON_ID) : completed.delete(LESSON_ID);
      state.completed = [...completed].sort();
      try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }} catch {{}}
    }}

    const completion = document.querySelector("#lesson-complete");
    if (launcherMode) {{
      completion.checked = readProgress().completed.includes(LESSON_ID);
      completion.addEventListener("change", async () => {{
        writeProgress(completion.checked);
        try {{
          await apiRequest("/api/progress", {{
            method: "POST",
            body: JSON.stringify({{ lesson_id: LESSON_ID, complete: completion.checked }})
          }});
          setStatus(completion.checked ? "Progress saved as complete." : "Progress saved as incomplete.");
        }} catch (error) {{
          setStatus("Browser progress changed, but the progress file was not updated: " + error.message, true);
        }}
      }});
    }}

    function setStatus(message, failed = false) {{
      const status = document.querySelector("#launcher-status");
      status.textContent = message;
      status.style.color = failed ? "var(--red)" : "var(--muted)";
    }}

    async function apiRequest(path, options = {{}}) {{
      const response = await fetch(path, {{
        ...options,
        headers: {{
          "Content-Type": "application/json",
          "X-DS60-Token": SERVER_TOKEN,
          ...(options.headers || {{}})
        }}
      }});
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "Guided launcher request failed.");
      return payload;
    }}

    async function launch(detail) {{
      setStatus("Opening the allowlisted course artifact…");
      try {{
        const payload = await apiRequest("/api/launch", {{
          method: "POST",
          body: JSON.stringify(detail)
        }});
        setStatus(payload.action + " started.");
      }} catch (error) {{
        setStatus("Could not launch this artifact: " + error.message, true);
      }}
    }}

    if (launcherMode) {{
      document.querySelectorAll(".launcher-only").forEach((button) => {{ button.hidden = false; }});
      document.querySelectorAll(".static-only").forEach((element) => {{ element.hidden = true; }});
      setStatus("Guided launcher mode is ready.");
      document.querySelector("#launch-learner").addEventListener("click", () => {{
        void launch({{ action: "open-artifact", lesson_id: LESSON_ID, artifact: "lesson" }});
      }});
      const jupyterButton = document.querySelector("#launch-jupyter");
      if (jupyterButton) {{
        jupyterButton.addEventListener("click", () => {{
          void launch({{ action: "jupyter-lesson", lesson_id: LESSON_ID }});
        }});
      }}
      const sqlNotebookButton = document.querySelector("#launch-sql-notebook");
      if (sqlNotebookButton) {{
        sqlNotebookButton.addEventListener("click", () => {{
          void launch({{
            action: "jupyter-sql",
            lesson_id: LESSON_ID,
            artifact: "lesson",
            solution_index: 1
          }});
        }});
      }}
      document.querySelectorAll("[data-launch-artifact]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const detail = {{
            action: "open-artifact",
            lesson_id: LESSON_ID,
            artifact: button.dataset.artifactKind
          }};
          if (button.dataset.solutionIndex !== undefined) {{
            detail.solution_index = Number(button.dataset.solutionIndex);
          }}
          void launch(detail);
        }});
      }});
    }}
  </script>
</body>
</html>
"""


def _reference_title(path: Path) -> str:
    """Return a concise title from the first Markdown heading or filename."""

    if path.suffix.lower() == ".md":
        for line in path.read_text(encoding="utf-8").splitlines():
            match = _HEADING_RE.match(line)
            if match is not None:
                title = re.sub(r"[`*_~]", "", match.group(2)).strip()
                if title:
                    return title
    return path.stem.replace("_", " ").replace("-", " ").title()


def build_reference_html(
    catalog: Catalog,
    source_path: Path,
    *,
    targets: Mapping[Path, ReaderTarget] | None = None,
) -> str:
    """Build one safe, standalone rendered Markdown or SQL reference page."""

    resolved_source = source_path.resolve()
    if not resolved_source.is_relative_to(catalog.repo_root) or not resolved_source.is_file():
        raise ValueError(f"Reference source is outside the repository or missing: {source_path}")
    source_relative = resolved_source.relative_to(catalog.repo_root)
    output_path = reference_relative_path(source_relative)
    target_map = dict(targets or rendered_targets(catalog))
    title = _reference_title(resolved_source)
    if resolved_source.suffix.lower() == ".md":
        resolver = LinkResolver(
            repo_root=catalog.repo_root,
            source_path=resolved_source,
            targets=target_map,
            output_path=output_path,
        )
        rendered = render_markdown(
            resolved_source.read_text(encoding="utf-8"),
            resolver=resolver,
            heading_offset=1,
        )
        kind = "Rendered course document"
    elif resolved_source.suffix.lower() == ".sql":
        rendered = (
            '<div class="preview-note" role="note"><strong>Readable SQL reference.</strong> '
            "This page does not connect to PostgreSQL or execute statements. Use the "
            "course's guided SQL controls for runnable work.</div>"
            + _render_source_code(
                resolved_source.read_text(encoding="utf-8"),
                language="sql",
            )
        )
        kind = "Rendered SQL reference"
    else:
        raise ValueError(f"Unsupported reference source: {source_relative}")

    home_href = quote(
        posixpath.relpath(
            "START_HERE.html",
            start=PurePosixPath(output_path).parent.as_posix(),
        ),
        safe="/",
    )
    source_text = html.escape(source_relative.as_posix())
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <meta
    http-equiv="Content-Security-Policy"
    content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; form-action 'none'"
  >
  <title>{html.escape(title)} · DS60 reference</title>
  <style>
    :root {{
      --paper: #f6f2e8; --surface: #fffdf8; --ink: #17221e; --muted: #59655f;
      --line: #d7d7ca; --navy: #173f5f; --green: #0f6b4f; --gold: #9d6515;
      --navy-soft: #e8f0f5; --gold-soft: #f7ead2;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0; color: var(--ink); line-height: 1.65;
      background:
        radial-gradient(circle at 0 0, rgb(15 107 79 / 10%), transparent 24rem),
        radial-gradient(circle at 100% 0, rgb(23 63 95 / 10%), transparent 27rem),
        var(--paper);
    }}
    a {{ color: var(--navy); text-underline-offset: .18em; }}
    a:hover {{ color: var(--green); }}
    :focus-visible {{ outline: 3px solid #efb74c; outline-offset: 3px; }}
    code, pre {{ font-family: "Cascadia Code", "SFMono-Regular", Consolas, monospace; }}
    code {{ border-radius: .35rem; padding: .08rem .3rem; background: rgb(23 63 95 / 8%); }}
    .shell {{ width: min(980px, calc(100% - 2rem)); margin-inline: auto; }}
    .topbar {{
      position: sticky; top: 0; z-index: 10; border-bottom: 1px solid var(--line);
      background: rgb(246 242 232 / 94%); backdrop-filter: blur(12px);
    }}
    .topbar .shell {{
      display: flex; min-height: 4rem; align-items: center; justify-content: space-between; gap: 1rem;
    }}
    .brand {{ color: var(--ink); font-weight: 850; text-decoration: none; }}
    .brand span {{
      display: inline-grid; width: 2.25rem; height: 2.25rem; place-items: center;
      margin-right: .55rem; border-radius: .65rem; color: #fff;
      background: linear-gradient(145deg, var(--navy), var(--green)); font-size: .73rem;
    }}
    .hero {{ padding: clamp(2.6rem, 7vw, 5rem) 0 1.5rem; }}
    .eyebrow {{
      margin: 0 0 .45rem; color: var(--green); font-size: .78rem; font-weight: 850;
      letter-spacing: .12em; text-transform: uppercase;
    }}
    h1, h2, h3, h4, h5, h6 {{ line-height: 1.2; text-wrap: balance; }}
    h1 {{ max-width: 22ch; margin: .4rem 0 .8rem; font-size: clamp(2.2rem, 6vw, 4rem); letter-spacing: -.045em; }}
    h2 {{ margin-top: 2.5rem; font-size: 1.75rem; }}
    h3 {{ margin-top: 2rem; font-size: 1.4rem; }}
    .source-path {{ color: var(--muted); overflow-wrap: anywhere; }}
    .document {{
      margin: 0 0 4rem; border: 1px solid var(--line); border-radius: 20px;
      padding: clamp(1rem, 4vw, 2.4rem); background: var(--surface);
      box-shadow: 0 18px 46px rgb(28 45 37 / 10%);
    }}
    .heading-anchor {{ margin-left: .4rem; color: var(--line); font-size: .75em; text-decoration: none; }}
    h2:hover .heading-anchor, h3:hover .heading-anchor {{ color: var(--green); }}
    pre {{
      overflow: auto; border: 1px solid #294958; border-radius: 12px; padding: 1rem;
      color: #eaf4ef; background: #152d35; line-height: 1.55; white-space: pre;
    }}
    pre code {{ padding: 0; color: inherit; background: transparent; }}
    .source-code {{ padding: 1rem 0; }}
    .source-code code {{ display: block; counter-reset: source-line; }}
    .source-code code > span {{ display: block; min-height: 1.55em; padding: 0 1rem 0 4.2rem; }}
    .source-code code > span::before {{
      float: left; width: 2.8rem; margin-left: -3.5rem; color: #81a0a8;
      text-align: right; counter-increment: source-line; content: counter(source-line);
      user-select: none;
    }}
    .source-code code > span:target, .source-code code > span:hover {{ background: rgb(255 255 255 / 6%); }}
    .preview-note {{
      border-left: 4px solid var(--gold); border-radius: 0 10px 10px 0;
      padding: .8rem 1rem; color: #594217; background: var(--gold-soft);
    }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid var(--line); padding: .65rem; text-align: left; vertical-align: top; }}
    th {{ background: var(--navy-soft); }}
    blockquote {{
      margin-left: 0; border-left: 4px solid var(--navy); padding: .2rem 1rem;
      color: var(--muted); background: var(--navy-soft);
    }}
    .image-note {{
      display: inline-block; border: 1px dashed var(--line); border-radius: .4rem;
      padding: .15rem .4rem; color: var(--muted);
    }}
    @media (max-width: 620px) {{
      .topbar .shell {{ align-items: flex-start; flex-direction: column; padding-block: .7rem; }}
    }}
    @media print {{
      .topbar {{ display: none; }}
      body {{ background: #fff; }}
      .document {{ border: 0; box-shadow: none; }}
    }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="shell">
      <a class="brand" href="{home_href}#catalog"><span>DS60</span>Learning guide</a>
      <a href="{home_href}#catalog">Back to lessons</a>
    </div>
  </header>
  <main class="shell">
    <header class="hero">
      <p class="eyebrow">{kind}</p>
      <h1>{html.escape(title)}</h1>
      <p class="source-path">Generated from <code>{source_text}</code></p>
    </header>
    <article class="document">{rendered}</article>
  </main>
</body>
</html>
"""


def build_reader_files(catalog: Catalog) -> dict[str, str]:
    """Return every expected reader path and its deterministic contents."""

    targets = rendered_targets(catalog)
    return {
        reader_relative_path(lesson.id): _clean_generated_html(
            build_lesson_html(catalog, lesson, targets=targets)
        )
        for lesson in catalog
    }


def build_reference_files(catalog: Catalog) -> dict[str, str]:
    """Return every deterministic rendered reference path and document."""

    sources = reference_source_paths(catalog)
    targets = rendered_targets(catalog)
    return {
        reference_relative_path(source.relative_to(catalog.repo_root)): _clean_generated_html(
            build_reference_html(
                catalog,
                source,
                targets=targets,
            )
        )
        for source in sources
    }


def reader_drift(
    expected: Mapping[str, str],
    *,
    repo_root: Path,
    output_dir: Path | None = None,
) -> list[str]:
    """Return missing, changed, and unexpected generated HTML paths."""

    root = output_dir or (repo_root / LESSON_PAGES_DIR)
    expected_names = {Path(path).name for path in expected}
    failures: list[str] = []
    for relative_path, rendered in expected.items():
        path = root / Path(relative_path).name
        if not path.is_file():
            failures.append(f"missing: {path}")
        elif path.read_text(encoding="utf-8") != rendered:
            failures.append(f"changed: {path}")
    if root.is_dir():
        for path in sorted(root.glob("*.html")):
            if path.name not in expected_names:
                failures.append(f"unexpected: {path}")
    return failures


def reference_drift(
    expected: Mapping[str, str],
    *,
    repo_root: Path,
    output_dir: Path | None = None,
) -> list[str]:
    """Return missing, changed, and unexpected rendered-reference paths."""

    root = output_dir or (repo_root / REFERENCE_PAGES_DIR)
    expected_paths = {
        Path(*PurePosixPath(path).parts[1:]): rendered for path, rendered in expected.items()
    }
    failures: list[str] = []
    for relative_path, rendered in expected_paths.items():
        path = root / relative_path
        if not path.is_file():
            failures.append(f"missing: {path}")
        elif path.read_text(encoding="utf-8") != rendered:
            failures.append(f"changed: {path}")
    if root.is_dir():
        for path in sorted(root.rglob("*.html")):
            if path.relative_to(root) not in expected_paths:
                failures.append(f"unexpected: {path}")
    return failures


def write_reader_files(
    expected: Mapping[str, str],
    *,
    repo_root: Path,
    output_dir: Path | None = None,
) -> None:
    """Write every generated reader and remove only obsolete generated HTML."""

    root = output_dir or (repo_root / LESSON_PAGES_DIR)
    root.mkdir(parents=True, exist_ok=True)
    expected_names = {Path(path).name for path in expected}
    for relative_path, rendered in expected.items():
        (root / Path(relative_path).name).write_text(rendered, encoding="utf-8", newline="\n")
    for path in root.glob("*.html"):
        if path.name not in expected_names:
            path.unlink()


def write_reference_files(
    expected: Mapping[str, str],
    *,
    repo_root: Path,
    output_dir: Path | None = None,
) -> None:
    """Write rendered references and remove only obsolete generated HTML."""

    root = output_dir or (repo_root / REFERENCE_PAGES_DIR)
    root.mkdir(parents=True, exist_ok=True)
    expected_paths = {
        Path(*PurePosixPath(path).parts[1:]): rendered for path, rendered in expected.items()
    }
    for relative_path, rendered in expected_paths.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8", newline="\n")
    for path in sorted(root.rglob("*.html")):
        if path.relative_to(root) not in expected_paths:
            path.unlink()
    for directory in sorted(
        (path for path in root.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        with suppress(OSError):
            directory.rmdir()


def iter_reader_paths(catalog: Catalog) -> Iterable[str]:
    """Yield generated lesson reader paths in catalog order."""

    return (reader_relative_path(lesson.id) for lesson in catalog)
