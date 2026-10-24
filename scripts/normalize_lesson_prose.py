#!/usr/bin/env python3
"""Normalize reviewed teaching prose, then math, without changing programs.

This is the single authoring pipeline after subject generation and before HTML
readers. Exact repair inputs live in curriculum/prose-repairs.json and
curriculum/math-prose.json. Unknown language is reported for editorial review,
never split using an automatic dictionary guess.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.normalize_math_prose import digest, prose_parts, protected_code  # noqa: E402
from scripts.normalize_math_prose import run as normalize_math  # noqa: E402

TEXT_FIELDS = frozenset(
    {
        "title",
        "summary",
        "outcome",
        "lab",
        "verification",
        "concepts",
        "learning_outcomes",
        "description",
        "expected",
        "hints",
        "mental",
        "anatomy",
        "decisions",
        "comparison",
        "interview",
        "diagnosis",
        "terms",
    }
)
# These forms are candidate indicators, not a rewriting grammar.
JOINED_COUNT = re.compile(
    r"\b(?:full|detailed|complete|This|all|each|a|A)\d+(?:-?lessons?|chapters?|tokens?|rows?|seconds?)\b"
    r"|\b\d+(?:lessons?|chapters?|examples?|observations?)\b"
)


def replacements(root: Path) -> dict[str, str]:
    payload = json.loads((root / "curriculum/prose-repairs.json").read_text(encoding="utf-8"))
    return {str(k): str(v) for k, v in payload["repairs"].items()}


def normalize(text: str, repairs: dict[str, str]) -> tuple[str, Counter[str]]:
    """Repair known complete words or phrases only in prose, never code/math."""
    pattern = re.compile(
        r"(?<![\w/.-])(?:"
        + "|".join(re.escape(x) for x in sorted(repairs, key=len, reverse=True))
        + r")(?![\w/-]|\.[A-Za-z_])"
    )
    hits: Counter[str] = Counter()

    def fix(value: str) -> str:
        for _ in range(3):

            def replace(match: re.Match[str]) -> str:
                source = match.group()
                hits[source] += 1
                return repairs[source]

            new = pattern.sub(replace, value)
            if new == value:
                break
            value = new
        return value

    result = "".join(part if protected else fix(part) for protected, part in prose_parts(text))
    before = protected_code(text)
    after = protected_code(result)
    if before != after:
        raise ValueError("Prose cleanup changed a fenced block")
    return result, hits


def content_paths(root: Path) -> list[Path]:
    files: set[Path] = set()
    for directory in ("courses", "python", "sql", "bridge", "docs"):
        for path in (root / directory).rglob("*"):
            if path.suffix not in {".md", ".ipynb"} or path.is_symlink():
                continue
            relative = path.relative_to(root).parts
            if path.name == "source-outline.md" or "fixtures" in relative:
                continue
            if len(relative) > 1 and relative[:2] == ("docs", "implementation"):
                continue
            files.add(path)
    for filename in ("README.md", "CONTRIBUTING.md"):
        if (root / filename).exists():
            files.add(root / filename)
    return sorted(files)


def prose_constants(tree: ast.AST) -> list[ast.Constant]:
    """Select explicit authoring prose fields, excluding code/import/helper slots."""
    selected: dict[tuple[int, int], ast.Constant] = {}

    def collect(node: ast.AST) -> None:
        for child in ast.walk(node):
            if isinstance(child, ast.Constant) and isinstance(child.value, str):
                selected[(child.lineno, child.col_offset)] = child

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else ""
            if name == "ex":
                for index in (0, 1, 2, 4):
                    if index < len(node.args):
                        collect(node.args[index])
            elif name == "add":
                for index in (1, 2, 3):
                    if index < len(node.args):
                        collect(node.args[index])
            elif name == "review":
                for argument in node.args[1:]:
                    collect(argument)
            for keyword in node.keywords:
                if keyword.arg in TEXT_FIELDS:
                    collect(keyword.value)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Subscript)
                    and isinstance(target.slice, ast.Constant)
                    and target.slice.value in TEXT_FIELDS
                ):
                    collect(node.value)
    return list(selected.values())


def repair_authoring(source: str, repairs: dict[str, str]) -> tuple[str, Counter[str]]:
    tree = ast.parse(source)
    lines = source.encode().splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    edits: list[tuple[int, int, bytes]] = []
    hits: Counter[str] = Counter()
    for node in prose_constants(tree):
        value = str(node.value)
        cleaned, changed = normalize(value, repairs)
        if not changed:
            continue
        assert node.end_lineno is not None and node.end_col_offset is not None
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        edits.append((start, end, repr(cleaned).encode()))
        hits.update(changed)
    raw = source.encode()
    for start, end, replacement in sorted(edits, reverse=True):
        raw = raw[:start] + replacement + raw[end:]
    result = raw.decode()

    # Compare every non-prose string value plus executable AST structure. This
    # catches accidental repairs to embedded example source or fixture data.
    def skeleton(text: str) -> str:
        parsed = ast.parse(text)
        for node in prose_constants(parsed):
            node.value = "<authored prose>"
        return ast.dump(parsed, include_attributes=False)

    if skeleton(source) != skeleton(result):
        raise ValueError("Authoring edit changed executable structure or a protected string")
    return result, hits


def run(root: Path, write: bool) -> dict[str, Any]:
    repairs = replacements(root)
    changes: list[dict[str, Any]] = []
    candidates: list[dict[str, str]] = []
    protected: dict[str, str] = {}
    scanned = 0
    for path in content_paths(root):
        scanned += 1
        rel = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8")
        hits: Counter[str] = Counter()
        if path.suffix == ".ipynb":
            notebook = json.loads(source)
            before = [c for c in notebook["cells"] if c.get("cell_type") != "markdown"]
            for cell in notebook["cells"]:
                if cell.get("cell_type") == "markdown":
                    text, count = normalize("".join(cell["source"]), repairs)
                    if count:
                        cell["source"] = text.splitlines(keepends=True)
                    hits.update(count)
            after = [c for c in notebook["cells"] if c.get("cell_type") != "markdown"]
            if before != after:
                raise ValueError(f"Notebook code changed: {rel}")
            protected[rel] = digest(before)
            updated = json.dumps(notebook, ensure_ascii=False, indent=1) + "\n" if hits else source
            prose = "\n".join(
                "".join(c["source"]) for c in notebook["cells"] if c.get("cell_type") == "markdown"
            )
        else:
            updated, hits = normalize(source, repairs)
            protected[rel] = digest(protected_code(source))
            prose = updated
        if updated != source:
            changes.append({"path": rel, "replacements": sum(hits.values()), "rules": dict(hits)})
            if write:
                path.write_text(updated, encoding="utf-8", newline="\n")
        for is_protected, part in prose_parts(prose):
            if not is_protected:
                for match in JOINED_COUNT.finditer(part):
                    candidates.append({"path": rel, "text": match.group()})
    metadata = sorted((root / "courses").glob("*/track.json")) + sorted(
        (root / "docs/expansion/plans").glob("*.json")
    )
    for path in metadata:
        rel = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8")
        document = json.loads(source)
        original = json.loads(source)
        hits = Counter()

        def visit(
            value: Any, key: str = "", counts: Counter[str] = hits, source_path: str = rel
        ) -> Any:
            if isinstance(value, dict):
                return {k: visit(v, k) for k, v in value.items()}
            if isinstance(value, list):
                return [visit(v, key) for v in value]
            if isinstance(value, str) and key in TEXT_FIELDS:
                cleaned, count = normalize(value, repairs)
                counts.update(count)
                for is_protected, part in prose_parts(cleaned):
                    if not is_protected:
                        for match in JOINED_COUNT.finditer(part):
                            candidates.append({"path": source_path, "text": match.group()})
                return cleaned
            return value

        document = visit(document)
        # The exact whitelist above is the mutation boundary for IDs, paths,
        # ordering, prerequisites, runtimes, exercise budgets and data fields.
        if document != original:
            changes.append(
                {
                    "path": rel,
                    "replacements": sum(hits.values()),
                    "rules": dict(hits),
                    "kind": "display_metadata",
                }
            )
            if write:
                path.write_text(
                    json.dumps(document, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
    authoring = sorted((root / "courses").glob("*/authoring/**/*.py"))
    for path in authoring:
        source = path.read_text(encoding="utf-8")
        cleaned, hits = repair_authoring(source, repairs)
        if hits:
            changes.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "replacements": sum(hits.values()),
                    "rules": dict(hits),
                    "kind": "authoring_prose",
                }
            )
            if write:
                path.write_text(cleaned, encoding="utf-8", newline="\n")
    return {
        "schema": 1,
        "prose_files_scanned": scanned,
        "metadata_files_scanned": len(metadata),
        "authoring_files_scanned": len(authoring),
        "files_changed": len(changes),
        "replacements": sum(x["replacements"] for x in changes),
        "protected_code_unchanged": True,
        "protected_code_sha256": digest(protected),
        "changes": changes,
        "remaining_count_candidates": candidates,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    report = {"prose": run(root, args.write), "math": normalize_math(root, args.write)}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    for name, section in report.items():
        print(f"{name}: {section['files_changed']} files; {section['replacements']} changes")
    if report["prose"]["remaining_count_candidates"]:
        print("Unreviewed joined count/word forms require editorial review.")
        raise SystemExit(1)
    if not args.write and any(section["files_changed"] for section in report.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
