"""Regenerate optional Linux CPU dependency locks with the installed uv tool."""

from __future__ import annotations

import subprocess
from pathlib import Path


def main() -> None:
    folder = Path(__file__).resolve().parent
    for arch, platform in (
        ("arm64", "aarch64-unknown-linux-gnu"),
        ("amd64", "x86_64-unknown-linux-gnu"),
    ):
        temporary = folder / f"requirements.{arch}.lock.tmp"
        subprocess.run(
            [
                "uv",
                "pip",
                "compile",
                "pyproject.toml",
                "--python-version",
                "3.12",
                "--python-platform",
                platform,
                "--generate-hashes",
                "--emit-index-url",
                "--output-file",
                temporary.name,
            ],
            cwd=folder,
            check=True,
        )
        content = temporary.read_text().replace(
            "--index-url https://pypi.org/simple",
            "--index-url https://pypi.org/simple\n"
            "--extra-index-url https://download.pytorch.org/whl/cpu",
        )
        content = content.replace(temporary.name, f"requirements.{arch}.lock")
        (folder / f"requirements.{arch}.lock").write_text(content)
        temporary.unlink()
        print(f"Wrote requirements.{arch}.lock; build and qualify this platform next.")


if __name__ == "__main__":
    main()
