#!/usr/bin/env python3
"""Apply reviewed mathematics typography without changing executable lesson text.

The explicit registry is an authoring input. No new formulas are inferred here.
Run after subject generators and before the HTML readers. Existing TeX, links,
inline code, fenced code, notebook code cells and supplied outlines are preserved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "curriculum/math-prose.json"
INLINE_PROTECTED = re.compile(
    r"\\\[.*?\\\]|\$\$.*?\$\$|\\\(.*?\\\)"
    r"|(?<!\$)\$(?!\$)[^\n$]+\$(?!\$)"
    r"|!?\[[^\]\n]*\]\([^\n)]*\)|<!--.*?-->",
    re.DOTALL,
)
CANDIDATE = re.compile(
    r"\b(?:sqrt|softmax|sigmoid|log|exp|Var|Cov)\s*\("
    r"|[A-Za-z0-9)]\^[A-Za-z0-9(]|[∑∂∇]"
    r"|\bsum_(?!view\b)[A-Za-z]|\bproduct_(?!id\b)[A-Za-z]"
)


def block_ranges(text: str) -> list[tuple[int, int]]:
    """Conservatively protect fenced and indented Markdown code through EOF."""
    lines = text.splitlines(keepends=True)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line))
    result: list[tuple[int, int]] = []
    index = 0
    while index < len(lines):
        opening = re.match(r"^[ \t]*(`{3,}|~{3,})(.*)$", lines[index].rstrip("\r\n"))
        if opening:
            marker = opening.group(1)
            end = index + 1
            while end < len(lines):
                closing = re.fullmatch(
                    r"[ \t]*" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}[ \t]*",
                    lines[end].rstrip("\r\n"),
                )
                if closing:
                    end += 1
                    break
                end += 1
            result.append((starts[index], starts[end]))
            index = end
        elif lines[index].startswith(("    ", "\t")):
            end = index + 1
            while end < len(lines) and (
                not lines[end].strip() or lines[end].startswith(("    ", "\t"))
            ):
                end += 1
            result.append((starts[index], starts[end]))
            index = end
        else:
            index += 1
    return result


def inline_parts(text: str) -> list[tuple[bool, str]]:
    ranges: list[tuple[int, int]] = []
    position = 0
    # CommonMark code spans may contain newlines and shorter backtick runs.
    # Only a run of exactly the opening length closes the span.
    while position < len(text):
        opening = re.search(r"(?<![\\`])`+", text[position:])
        if not opening:
            break
        start = position + opening.start()
        marker = opening.group()
        content_start = position + opening.end()
        closing = re.search(r"(?<!`)" + re.escape(marker) + r"(?!`)", text[content_start:])
        end = content_start + closing.end() if closing else len(text)
        ranges.append((start, end))
        position = end
    for match in INLINE_PROTECTED.finditer(text):
        if not any(start < match.end() and end > match.start() for start, end in ranges):
            ranges.append((match.start(), match.end()))
    result: list[tuple[bool, str]] = []
    position = 0
    for start, end in sorted(ranges):
        if start < position:
            continue
        result.extend(((False, text[position:start]), (True, text[start:end])))
        position = end
    result.append((False, text[position:]))
    return result


def prose_parts(text: str) -> list[tuple[bool, str]]:
    result: list[tuple[bool, str]] = []
    position = 0
    for start, end in block_ranges(text):
        result.extend(inline_parts(text[position:start]))
        result.append((True, text[start:end]))
        position = end
    result.extend(inline_parts(text[position:]))
    return result


def protected_code(text: str) -> list[str]:
    """Exact block-code bytes used by preservation receipts and assertions."""
    return [text[start:end] for start, end in block_ranges(text)]


def normalize(text: str, relative: str, rules: list[dict[str, Any]]) -> tuple[str, Counter[str]]:
    applicable = [r for r in rules if not r.get("paths") or relative in r["paths"]]
    replacements: dict[str, str] = {
        str(r["source"]): (r"\(" + str(r["latex"]) + r"\)" if "latex" in r else str(r["text"]))
        for r in applicable
    }
    if not replacements:
        return text, Counter()
    # A whole-token boundary prevents replacing a partial identifier or URL.
    pattern = re.compile(
        r"(?<![/\\])(?:"
        + "|".join(re.escape(s) for s in sorted(replacements, key=len, reverse=True))
        + r")(?![\w/])"
    )
    hits: Counter[str] = Counter()

    def replace(match: re.Match[str]) -> str:
        source = match.group()
        prior = match.string[match.start() - 1 : match.start()]
        if source[0].isalnum() and prior and (prior.isalnum() or prior == "_"):
            return source
        hits[source] += 1
        prefix = " " if prior and prior.isalnum() else ""
        return prefix + replacements[source]

    output = "".join(
        value if protected else pattern.sub(replace, value)
        for protected, value in prose_parts(text)
    )
    if protected_code(output) != protected_code(text):
        raise ValueError(f"Executable or prompt block changed: {relative}")
    return output, hits


def sources(root: Path) -> list[Path]:
    result: list[Path] = []
    for directory in ("courses", "python", "sql", "bridge", "docs/learning"):
        for path in (root / directory).rglob("*"):
            if path.suffix not in (".md", ".ipynb") or path.is_symlink():
                continue
            if path.name in ("source-outline.md", "AGENTS.md") or "fixtures" in path.parts:
                continue
            result.append(path)
    return sorted(result)


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def run(root: Path, write: bool) -> dict[str, Any]:
    rules = json.loads((root / "curriculum/math-prose.json").read_text(encoding="utf-8"))["rules"]
    changed: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    protected_before: dict[str, Any] = {}
    protected_after: dict[str, Any] = {}
    inspected = 0
    total = 0
    for path in sources(root):
        inspected += 1
        rel = path.relative_to(root).as_posix()
        original = path.read_text(encoding="utf-8")
        if path.suffix == ".ipynb":
            notebook = json.loads(original)
            before = {k: v for k, v in notebook.items() if k != "cells"}
            before["cells"] = [
                cell for cell in notebook["cells"] if cell.get("cell_type") != "markdown"
            ]
            protected_before[rel] = digest(before)
            file_hits: Counter[str] = Counter()
            for cell in notebook["cells"]:
                if cell.get("cell_type") == "markdown":
                    text = "".join(cell["source"])
                    updated, hits = normalize(text, rel, rules)
                    file_hits.update(hits)
                    if hits:
                        cell["source"] = updated.splitlines(keepends=True)
            after = {k: v for k, v in notebook.items() if k != "cells"}
            after["cells"] = [
                cell for cell in notebook["cells"] if cell.get("cell_type") != "markdown"
            ]
            protected_after[rel] = digest(after)
            updated = (
                json.dumps(notebook, ensure_ascii=False, indent=1) + "\n" if file_hits else original
            )
            texts = [
                "".join(c["source"]) for c in notebook["cells"] if c.get("cell_type") == "markdown"
            ]
        else:
            protected_before[rel] = digest(protected_code(original))
            updated, file_hits = normalize(original, rel, rules)
            protected_after[rel] = digest(protected_code(updated))
            texts = [updated]
        total += sum(file_hits.values())
        if updated != original:
            changed.append(
                {"path": rel, "replacements": sum(file_hits.values()), "rules": dict(file_hits)}
            )
            if write:
                path.write_text(updated, encoding="utf-8", newline="\n")
        for text in texts:
            for protected, part in prose_parts(text):
                if protected:
                    continue
                for line in part.splitlines():
                    if CANDIDATE.search(line):
                        remaining.append({"path": rel, "text": line.strip()})
    if protected_before != protected_after:
        raise ValueError("Protected code or notebook data changed")
    return {
        "schema": 1,
        "rules": len(rules),
        "sources_inspected": inspected,
        "files_changed": len(changed),
        "replacements": total,
        "code_fences_and_notebook_code_unchanged": True,
        "protected_sha256": digest(protected_before),
        "changes": changed,
        "remaining_candidates": remaining,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = run(args.root.resolve(), args.write)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(
        f"Math prose: {report['sources_inspected']} sources; "
        f"{report['files_changed']} files needing normalization; "
        f"{report['replacements']} replacements; "
        f"{len(report['remaining_candidates'])} candidate passages for editorial review. "
        "Protected code unchanged."
    )
    if not args.write and report["files_changed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
