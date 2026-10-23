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
PROTECTED = re.compile(
    r"(?P<fence>^[ \t]*(?P<marker>`{3,}|~{3,})[^\n]*\n.*?^[ \t]*(?P=marker)[ \t]*(?:\n|$))"
    r"|(?P<display>\\\[.*?\\\]|\$\$.*?\$\$)"
    r"|(?P<inline>\\\(.*?\\\)|(?<!\$)\$(?!\$)[^\n$]+\$(?!\$))"
    r"|(?P<code>`+[^`\n]*`+)"
    r"|(?P<link>!?\[[^\]\n]*\]\([^\n)]*\))"
    r"|(?P<html><!--.*?-->)",
    re.MULTILINE | re.DOTALL,
)
FENCE = re.compile(
    r"^[ \t]*(?P<marker>`{3,}|~{3,})[^\n]*\n.*?^[ \t]*(?P=marker)[ \t]*(?:\n|$)",
    re.MULTILINE | re.DOTALL,
)
CANDIDATE = re.compile(
    r"\b(?:sqrt|softmax|sigmoid|log|exp|Var|Cov)\s*\(|[A-Za-z0-9)]\^[A-Za-z0-9(]|[∑∂∇]|\bsum_(?!view\b)[A-Za-z]|\bproduct_(?!id\b)[A-Za-z]"
)


def prose_parts(text: str) -> list[tuple[bool, str]]:
    result: list[tuple[bool, str]] = []
    pos = 0
    for match in PROTECTED.finditer(text):
        result.append((False, text[pos : match.start()]))
        result.append((True, match.group()))
        pos = match.end()
    result.append((False, text[pos:]))
    return result


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
    if FENCE.findall(output) != FENCE.findall(text):
        raise ValueError(f"Fence delimiter drift: {relative}")
    if [m.group() for m in FENCE.finditer(output)] != [m.group() for m in FENCE.finditer(text)]:
        raise ValueError(f"Executable or prompt fence changed: {relative}")
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
    rules = json.loads((root / "curriculum/math-prose.json").read_text())["rules"]
    changed: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    protected_before: dict[str, Any] = {}
    protected_after: dict[str, Any] = {}
    inspected = 0
    total = 0
    for path in sources(root):
        inspected += 1
        rel = path.relative_to(root).as_posix()
        original = path.read_text()
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
            protected_before[rel] = digest([m.group() for m in FENCE.finditer(original)])
            updated, file_hits = normalize(original, rel, rules)
            protected_after[rel] = digest([m.group() for m in FENCE.finditer(updated)])
            texts = [updated]
        total += sum(file_hits.values())
        if updated != original:
            changed.append(
                {"path": rel, "replacements": sum(file_hits.values()), "rules": dict(file_hits)}
            )
            if write:
                path.write_text(updated)
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
        args.report.write_text(json.dumps(report, indent=2) + "\n")
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
