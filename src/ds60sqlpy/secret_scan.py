"""Offline scanning for common credential material in repository files."""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Final

REPO_ROOT: Final = Path(__file__).resolve().parents[2]
ALLOW_MARKER: Final = "secret-scan: allow-fixture"
ALLOWED_LOCAL_AUTHORITIES: Final = frozenset(
    {
        "postgresql://ds60:ds60@",
        "postgresql://USER:PASSWORD@",
    }
)
SENSITIVE_FILENAMES: Final = frozenset(
    {
        ".env",
        ".npmrc",
        ".pypirc",
        "credentials",
        "credentials.json",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "id_rsa",
    }
)
SENSITIVE_SUFFIXES: Final = frozenset({".jks", ".key", ".p12", ".pfx", ".pem"})
GENERATED_DIRECTORIES: Final = frozenset(
    {
        ".git",
        ".hypothesis",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "artifacts",
        "build",
        "dist",
        "htmlcov",
        "mlruns",
    }
)
PATTERNS: Final = (
    (
        "private-key header",
        re.compile(r"-----BEGIN (?:DSA |EC |OPENSSH |PGP |RSA )?PRIVATE KEY-----"),
    ),
    ("AWS access key", re.compile(r"(?<![A-Z0-9])A[K]IA[0-9A-Z]{16}(?![A-Z0-9])")),
    ("AWS temporary access key", re.compile(r"(?<![A-Z0-9])A[S]IA[0-9A-Z]{16}(?![A-Z0-9])")),
    ("GitHub token", re.compile(r"g[h][pousr]_[A-Za-z0-9]{36,}")),
    ("GitLab token", re.compile(r"g[l]pat-[A-Za-z0-9_-]{20,}")),
    ("Slack token", re.compile(r"x[o]x[baprs]-[A-Za-z0-9-]{20,}")),
    ("Google API key", re.compile(r"A[I]za[0-9A-Za-z_-]{30,}")),
    ("OpenAI-style key", re.compile(r"s[k]-[A-Za-z0-9_-]{20,}")),
    (
        "credential-bearing URL",
        re.compile(
            r"[A-Za-z][A-Za-z0-9+.-]*://"
            r"[^/\s:@]+:[^@\s/]+@",
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class Finding:
    """One filename or content finding without reproducing the secret."""

    path: Path
    line: int
    kind: str


def tracked_and_untracked_paths(repo_root: Path) -> tuple[Path, ...]:
    """Return Git-visible files while respecting ignore rules."""

    completed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return tuple(
        repo_root / Path(raw.decode("utf-8", errors="surrogateescape"))
        for raw in completed.stdout.split(b"\0")
        if raw
    )


def sensitive_filename(path: Path) -> bool:
    """Return whether a Git-visible filename usually contains credentials."""

    if path.name == ".env.example":
        return False
    return path.name in SENSITIVE_FILENAMES or path.suffix.casefold() in SENSITIVE_SUFFIXES


def local_sensitive_paths(repo_root: Path) -> tuple[Path, ...]:
    """Find ignored credential-shaped files without traversing generated trees."""

    paths: list[Path] = []
    for directory, directory_names, filenames in os.walk(repo_root):
        directory_names[:] = [name for name in directory_names if name not in GENERATED_DIRECTORIES]
        for filename in filenames:
            path = Path(directory, filename)
            if sensitive_filename(path.relative_to(repo_root)):
                paths.append(path)
    return tuple(paths)


def scan_text(path: Path, text: str) -> list[Finding]:
    """Return likely-secret findings without exposing matched values."""

    findings: list[Finding] = []
    allow_next_line = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        if allow_next_line:
            allow_next_line = False
            continue
        if ALLOW_MARKER in line:
            if line.strip().startswith(("#", "//")):
                allow_next_line = True
            continue
        for kind, pattern in PATTERNS:
            for match in pattern.finditer(line):
                if kind == "credential-bearing URL" and any(
                    allowed in match.group(0) for allowed in ALLOWED_LOCAL_AUTHORITIES
                ):
                    continue
                findings.append(Finding(path=path, line=line_number, kind=kind))
    return findings


def scan_repository(repo_root: Path = REPO_ROOT) -> list[Finding]:
    """Scan non-ignored repository files and sensitive filenames."""

    root = repo_root.resolve()
    findings: list[Finding] = []
    paths = {*tracked_and_untracked_paths(root), *local_sensitive_paths(root)}
    for path in sorted(paths):
        relative = path.relative_to(root)
        if sensitive_filename(relative):
            findings.append(Finding(path=relative, line=0, kind="sensitive filename"))
            continue
        try:
            payload = path.read_bytes()
        except (FileNotFoundError, OSError):
            continue
        if b"\0" in payload:
            continue
        text = payload.decode("utf-8", errors="replace")
        findings.extend(scan_text(relative, text))
    return findings
