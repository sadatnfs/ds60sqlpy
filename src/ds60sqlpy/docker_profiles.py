"""Select declared optional packages only during an explicit image build."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import urlsplit

CORE_EXTRAS = ("notebooks", "data", "bridge", "quality", "professional", "sql-notebooks")
ADVANCED_EXTRAS = ("ml", "production", "deep-learning", "nlp", "geo")
MIRROR_VARIABLE = "DS60_PYTHON_INDEX_URL"


def mirror_index(value: str | None) -> str | None:
    """Validate an optional anonymous HTTPS simple index used only for downloads."""

    if not value:
        return None
    parts = urlsplit(value)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or parts.query
        or parts.fragment
        or any(character.isspace() for character in value)
    ):
        raise ValueError(
            f"{MIRROR_VARIABLE} must be an anonymous HTTPS simple-index URL without "
            "credentials, a query or a fragment."
        )
    return value


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


def mirror_commands(
    extras: tuple[str, ...], *, uv: str, python: str, index_url: str, requirements: Path
) -> tuple[list[str], list[str], list[str]]:
    """Export the exact locked set with hashes, then install it from a mirror.

    ``uv sync --frozen`` downloads from the URLs recorded in uv.lock. A mirror
    therefore installs the same exported pins with every recorded hash required.
    """

    export = [
        uv,
        "export",
        "--frozen",
        "--no-dev",
        "--no-emit-project",
        "--format",
        "requirements-txt",
        "--output-file",
        str(requirements),
    ]
    for extra in extras:
        export.extend(("--extra", extra))
    environment = [uv, "venv", "--python", python, ".venv"]
    install = [
        uv,
        "pip",
        "install",
        "--python",
        ".venv/bin/python",
        "--require-hashes",
        "--no-deps",
        "--index-url",
        index_url,
        "--requirements",
        str(requirements),
    ]
    return export, environment, install


def reject_non_index_pins(requirements: str) -> None:
    """Refuse local-version pins, which a public simple-index mirror cannot serve."""

    local = sorted(
        {
            line.split("==", 1)[0]
            for line in requirements.splitlines()
            if re.match(r"^[A-Za-z0-9_.\-]+==[^\s;]*\+", line)
        }
    )
    if local:
        raise ValueError(
            f"{MIRROR_VARIABLE} supports packages hosted on the default index only. "
            "These selected pins come from another index: " + ", ".join(local) + ". "
            "Build this profile without the mirror setting."
        )


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
        index_url = mirror_index(os.environ.get(MIRROR_VARIABLE))
        print("Building image package profiles: " + ", ".join(extras), flush=True)
        if index_url is None:
            return subprocess.run(
                install_command(extras, uv=uv, python=sys.executable), cwd=project, check=False
            ).returncode
        print("Installing the exact locked packages from the configured mirror.", flush=True)
        with tempfile.TemporaryDirectory(prefix="ds60-mirror-") as directory:
            requirements = Path(directory) / "requirements.txt"
            export, environment, install = mirror_commands(
                extras, uv=uv, python=sys.executable, index_url=index_url, requirements=requirements
            )
            exported = subprocess.run(export, cwd=project, check=False)
            if exported.returncode:
                return exported.returncode
            reject_non_index_pins(requirements.read_text(encoding="utf-8"))
            for command in (environment, install):
                completed = subprocess.run(command, cwd=project, check=False)
                if completed.returncode:
                    return completed.returncode
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Cannot select image profiles: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
