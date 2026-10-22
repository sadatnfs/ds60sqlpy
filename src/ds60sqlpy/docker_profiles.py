"""Select declared optional packages only during an explicit image build."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tomllib
from collections.abc import Iterable
from pathlib import Path

CORE_EXTRAS = ("notebooks", "data", "bridge", "quality", "professional", "sql-notebooks")
ADVANCED_EXTRAS = ("ml", "production", "deep-learning", "nlp", "geo")


def select_extras(profiles: str, declared: Iterable[str]) -> tuple[str, ...]:
    """Expand named bundles and reject undeclared package/source arguments."""

    available = set(declared)
    if not set(CORE_EXTRAS).issubset(available):
        raise ValueError("The course project is missing a required Core extra.")
    selected = set(CORE_EXTRAS)
    requested = re.split(r"[,\s]+", profiles.strip().casefold())
    for profile in filter(None, requested):
        if profile == "core":
            continue
        if profile == "advanced":
            if not set(ADVANCED_EXTRAS).issubset(available):
                raise ValueError("The course project is missing a declared Advanced extra.")
            selected.update(ADVANCED_EXTRAS)
        elif profile in available:
            selected.add(profile)
        else:
            raise ValueError(
                f"Unknown image profile {profile!r}. Use core, advanced, "
                "or an optional extra declared in pyproject.toml."
            )
    return tuple(sorted(selected))


def install_command(extras: tuple[str, ...], *, uv: str, python: str) -> list[str]:
    command = [
        uv,
        "sync",
        "--frozen",
        "--python",
        python,
        "--no-dev",
        "--no-install-project",
    ]
    for extra in extras:
        command.extend(("--extra", extra))
    return command


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", default="core")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        project = args.project.resolve()
        configuration = tomllib.loads((project / "pyproject.toml").read_text(encoding="utf-8"))
        declared = configuration["project"]["optional-dependencies"]
        extras = select_extras(args.profiles, declared)
        if not (project / "uv.lock").is_file():
            raise ValueError("The image requires the checked-in uv.lock.")
        if args.dry_run:
            print(json.dumps({"profiles": args.profiles, "extras": extras}))
            return 0
        uv = shutil.which("uv")
        if uv is None:
            raise ValueError("Install the pinned image build tool before selecting profiles.")
        print("Building image package profiles: " + ", ".join(extras), flush=True)
        return subprocess.run(
            install_command(extras, uv=uv, python=sys.executable), cwd=project, check=False
        ).returncode
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Cannot select image profiles: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
