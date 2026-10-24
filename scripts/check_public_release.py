#!/usr/bin/env python3
"""Check source and portable distributions for private or branded project residue.

This complements the credential scanner. Diagnostics identify a file, line and
category without reproducing potentially private text. It works in a Git clone
and in an extracted source distribution.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ds60sqlpy.curriculum_framework import is_content_link  # noqa: E402
from ds60sqlpy.secret_scan import sensitive_filename  # noqa: E402

CREDENTIAL_DIRECTORY = ".codex"
FIXTURE_MARKER = "public-release: synthetic-fixture"
IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".venv",
        ".learning",
        ".classroom",
        ".serena",
        ".cache",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".hypothesis",
        "__pycache__",
        "node_modules",
        "work",
        "build",
        "dist",
        "artifacts",
        "mlruns",
    }
)
RULES = (
    # These names are policy definitions, never product attribution.
    ("assistant branding", re.compile(r"\b(?:Codex|OpenAI|ChatGPT)\b", re.IGNORECASE)),
    ("personal home path", re.compile(r"(?<![\w])/(?:Users|home)/[^/\s\"'<>]+/")),
    (
        "personal Windows path",
        re.compile(r"[A-Za-z]:\\(?:Users|Documents and Settings)\\[^\\\s\"'<>]+\\"),
    ),
    (
        "internal host URL",
        re.compile(r"https?://[A-Za-z0-9_.-]+\.(?:corp|internal)(?=[:/\s\"'<>]|$)", re.IGNORECASE),
    ),
    (
        "assistant transcript marker",
        re.compile(
            r"(?:<send_user_message_question_reply>|<environment_context>|clipboard-[0-9a-f]{8}-)"
        ),
    ),
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    category: str


def source_paths(root: Path, *, payload: bool = False) -> list[Path]:
    """Honor Git ignores in a clone; inspect public source in extracted copies."""
    if not payload and (root / ".git").exists():
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            capture_output=True,
            check=True,
        )
        return sorted({root / os.fsdecode(item) for item in result.stdout.split(b"\0") if item})
    paths = []
    for directory, names, files in os.walk(root, followlinks=False):
        descend = []
        for name in names:
            path = Path(directory) / name
            if name.casefold() in IGNORED_DIRECTORIES:
                if payload:
                    paths.append(path)
            elif is_content_link(path):
                paths.append(path)
            else:
                descend.append(name)
        names[:] = descend
        paths.extend(Path(directory) / name for name in files)
    return sorted(paths)


def _policy_spans(text: str) -> dict[int, list[tuple[int, int]]]:
    """Permit only this gate's literal rule definitions, not arbitrary prose."""
    try:
        statements = ast.parse(text).body
    except SyntaxError:
        return {}
    lines = text.splitlines()
    allowed: dict[int, list[tuple[int, int]]] = {}
    for statement in statements:
        if not isinstance(statement, ast.Assign):
            continue
        names = {target.id for target in statement.targets if isinstance(target, ast.Name)}
        literals: list[ast.Constant] = []
        if (
            "CREDENTIAL_DIRECTORY" in names
            and isinstance(statement.value, ast.Constant)
            and statement.value.value == CREDENTIAL_DIRECTORY
        ):
            literals.append(statement.value)
        if "RULES" in names:
            literals.extend(
                node.args[0]
                for node in ast.walk(statement.value)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "re"
                and node.func.attr == "compile"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            )
        for literal in literals:
            last = literal.end_lineno or literal.lineno
            for number in range(literal.lineno, last + 1):
                encoded = lines[number - 1].encode("utf-8")
                start = literal.col_offset if number == literal.lineno else 0
                end = literal.end_col_offset if number == last else len(encoded)
                if end is None:
                    end = len(encoded)
                span = (len(encoded[:start].decode("utf-8")), len(encoded[:end].decode("utf-8")))
                allowed.setdefault(number, []).append(span)
    return allowed


def _linked_source(root: Path, path: Path) -> bool:
    """Check every lexical component before a cached Git path can read outside."""
    candidate = root
    for part in path.relative_to(root).parts:
        candidate = candidate / part
        if is_content_link(candidate):
            return True
    return False


def scan_text(path: str, text: str) -> list[Finding]:
    findings = []
    fixture_next = False
    policy_spans = _policy_spans(text) if path == "scripts/check_public_release.py" else {}
    for number, line in enumerate(text.splitlines(), 1):
        fixture = "tests" in Path(path).parts and fixture_next
        fixture_next = (
            "tests" in Path(path).parts and line.lstrip().startswith("#") and FIXTURE_MARKER in line
        )
        if fixture:
            continue
        for category, pattern in RULES:
            for match in pattern.finditer(line):
                if category in {"assistant branding", "assistant transcript marker"} and any(
                    start <= match.start() and match.end() <= end
                    for start, end in policy_spans.get(number, [])
                ):
                    continue
                # Retain exact privacy exclusions, not branding in comments.
                if category == "assistant branding":
                    if path in {".dockerignore", ".gitignore"} and line.strip() in {
                        CREDENTIAL_DIRECTORY,
                        CREDENTIAL_DIRECTORY + "/",
                        "**/" + CREDENTIAL_DIRECTORY,
                    }:
                        continue
                    if path == "scripts/build_app.py" and line.strip().rstrip(",") in {
                        repr(CREDENTIAL_DIRECTORY),
                        json.dumps(CREDENTIAL_DIRECTORY),
                    }:
                        continue
                # Exempt only the individual documented placeholder match.
                if category == "personal Windows path" and re.fullmatch(
                    r"[A-Za-z]:\\Users\\(?:Ada|USERNAME)\\", match.group()
                ):
                    continue
                findings.append(Finding(path, number, category))
                break
    return findings


def scan(root: Path, *, payload: bool = False) -> tuple[list[Finding], int]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("Choose an existing source directory.")
    findings: list[Finding] = []
    count = 0
    for path in source_paths(root, payload=payload):
        relative = path.relative_to(root).as_posix()
        if _linked_source(root, path):
            findings.append(Finding(relative, 0, "linked source path"))
            continue
        if payload and path.is_dir() and path.name.casefold() in IGNORED_DIRECTORIES:
            findings.append(Finding(relative, 0, "private directory in distribution"))
            continue
        if not path.is_file():
            continue
        private_parts = {
            part.casefold() for part in path.relative_to(root).parts[:-1]
        } & IGNORED_DIRECTORIES
        portable_tool_config = relative in {".serena/project.yml", ".serena/.gitignore"}
        if private_parts and not portable_tool_config:
            findings.append(Finding(relative, 0, "tracked private runtime path"))
            continue
        if payload and sensitive_filename(path):
            findings.append(Finding(relative, 0, "private file in distribution"))
            continue
        count += 1
        if any(
            pattern.search(relative)
            for category, pattern in RULES
            if category == "assistant branding"
        ):
            findings.append(Finding(relative, 0, "branded source filename"))
        content = path.read_bytes()
        if b"\0" in content:
            continue
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            continue
        findings.extend(scan_text(relative, text))
    return findings, count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--payload",
        action="store_true",
        help="Reject private directories in a staged distribution.",
    )
    args = parser.parse_args()
    try:
        findings, count = scan(args.root, payload=args.payload)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Public-release scan could not finish: {type(error).__name__}")
        return 2
    report = {
        "passed": not findings,
        "files": count,
        "findings": [asdict(item) for item in findings],
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for finding in findings:
        print(f"FAIL {finding.path}:{finding.line}: {finding.category}")
    print(f"Public-release scan: {count} files; {len(findings)} findings.")
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
