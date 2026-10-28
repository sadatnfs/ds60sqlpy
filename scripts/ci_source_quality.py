"""Run complete source formatting/lint across separately hosted toolchain shards."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.format_repo import LANGUAGES, ensure_publication_paths  # noqa: E402


def languages(toolchain: str) -> tuple[str, ...]:
    if toolchain in {"r", "julia"}:
        return (toolchain,)
    if toolchain == "main":
        return tuple(name for name in LANGUAGES if name not in {"r", "julia"})
    raise ValueError("Unknown source-quality toolchain")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toolchain", required=True, choices=("main", "r", "julia"))
    args = parser.parse_args()
    ensure_publication_paths(ROOT)
    options = [option for name in languages(args.toolchain) for option in ("--language", name)]
    subprocess.run(["bash", "scripts/format-repo", "--check", *options], cwd=ROOT, check=True)
    subprocess.run(["bash", "scripts/lint-repo", *options], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--exit-code"], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
