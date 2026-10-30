"""Portable preparation guard for every local Docker COPY context input."""

from __future__ import annotations

import shlex
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[2]


def local_copy_sources(dockerfile: str) -> list[str]:
    logical = []
    pending = ""
    for line in dockerfile.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        pending += stripped.removesuffix("\\").rstrip() + " "
        if stripped.endswith("\\"):
            continue
        logical.append(pending.strip())
        pending = ""
    if pending:
        raise ValueError("Unfinished Dockerfile line continuation")
    sources = []
    for line in logical:
        words = shlex.split(line)
        if words[0].upper() != "COPY":
            continue
        options = [word for word in words[1:] if word.startswith("--")]
        if any(word.startswith("--from=") for word in options):
            continue
        operands = [word for word in words[1:] if not word.startswith("--")]
        if len(operands) < 2:
            raise ValueError("Local COPY needs source and destination")
        sources.extend(operands[:-1])
    return sources


def require_context(package: Path, dockerfile: str, rules: list[str]) -> None:
    if not rules or rules[0] != "**":
        raise ValueError("Expected the explicit Docker context deny-first policy")
    allowed = set(rules)
    for source in local_copy_sources(dockerfile):
        if source == ".":
            continue
        if source.startswith("/") or ".." in Path(source).parts:
            raise ValueError("Local COPY path escapes the package context")
        matches = list(package.glob(source))
        if not matches:
            raise ValueError("Local COPY source is missing: " + source)
        for path in matches:
            if path.is_symlink():
                raise ValueError("Local COPY source is a symlink: " + source)
            relative = path.relative_to(package)
            top = relative.parts[0]
            if len(relative.parts) == 1 and path.is_file():
                if "!" + top not in allowed:
                    raise ValueError("Local COPY file is omitted: " + source)
            elif "!" + top + "/" not in allowed or "!" + top + "/**" not in allowed:
                raise ValueError("Local COPY directory is omitted: " + source)


class DockerContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dockerfile = (PACKAGE / "Dockerfile").read_text()
        self.rules = [
            line.strip()
            for line in (PACKAGE / ".dockerignore").read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]

    def test_every_declared_local_copy_source_is_available(self) -> None:
        sources = local_copy_sources(self.dockerfile)
        self.assertIn("training-integration", sources)
        require_context(PACKAGE, self.dockerfile, self.rules)

    def test_omitted_training_directory_is_detected(self) -> None:
        missing = [
            rule
            for rule in self.rules
            if rule not in {"!training-integration/", "!training-integration/**"}
        ]
        with self.assertRaisesRegex(ValueError, "training-integration"):
            require_context(PACKAGE, self.dockerfile, missing)

    def test_private_and_generated_exclusions_remain(self) -> None:
        required = {
            "**/__pycache__",
            "**/*.pyc",
            "**/.pytest_cache",
            "**/.ruff_cache",
            "**/.env",
            "**/.env.*",
            "**/.aws",
            "**/.oci",
            "**/.ssh",
            "**/artifacts",
            "**/outputs",
            "**/work",
            "**/dist",
            "**/build",
        }
        self.assertTrue(required <= set(self.rules))


if __name__ == "__main__":
    unittest.main()
