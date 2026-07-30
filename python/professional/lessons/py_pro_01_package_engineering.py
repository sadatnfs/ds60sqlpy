"""python-pro-01 learner lab: package engineering and local releases.

Run this file from the repository root. The worked example reads the fixture
metadata without building anything. Complete the TODO functions in your own
copy, then use the companion guide's temporary-directory build procedure.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "tiny_package"


def read_project_table(project_root: Path = FIXTURE) -> dict[str, Any]:
    """Worked example: return the PEP 621 ``[project]`` metadata table."""

    with (project_root / "pyproject.toml").open("rb") as handle:
        document = tomllib.load(handle)
    project = document.get("project")
    if not isinstance(project, dict):
        raise ValueError("pyproject.toml is missing a [project] table")
    return project


def classify_artifact(filename: str) -> str:
    """Return ``wheel`` or ``source distribution`` for a distribution file.

    TODO:
    1. Inspect the final suffixes rather than searching the whole path.
    2. Accept ``.whl`` and ``.tar.gz``.
    3. Raise ``ValueError`` for an unknown artifact.
    """

    raise NotImplementedError("complete classify_artifact")


def offline_build_command(project_root: Path, output_dir: Path) -> list[str]:
    """Return a cross-platform argument list for an isolated-free local build.

    TODO: use the current interpreter, ``-m build``, both distribution formats,
    ``--no-isolation``, and an explicit output directory. Returning an argument
    list avoids shell quoting differences between PowerShell and POSIX shells.
    """

    raise NotImplementedError("complete offline_build_command")


def installed_origin_is_safe(origin: Path, target: Path) -> bool:
    """Decide whether an imported module came from the fresh install target.

    TODO: resolve both paths before comparing them. Do not accept the fixture's
    working-tree ``src`` directory as proof of an installation.
    """

    raise NotImplementedError("complete installed_origin_is_safe")


def self_check() -> None:
    """Run checks that become active as each exercise is completed."""

    project = read_project_table()
    assert project["name"] == "ds60-tiny-greeter"
    assert project["requires-python"] == ">=3.11"
    print("Worked example: project metadata loaded.")
    print(f"  name={project['name']!r}, version={project['version']!r}")

    checks = (
        ("artifact classification", lambda: classify_artifact("demo-1.0-py3-none-any.whl")),
        (
            "build command",
            lambda: offline_build_command(FIXTURE, Path(".learning") / "dist"),
        ),
        (
            "installed origin",
            lambda: installed_origin_is_safe(
                Path(".learning/site/demo/__init__.py"),
                Path(".learning/site"),
            ),
        ),
    )
    for label, check in checks:
        try:
            result = check()
        except NotImplementedError:
            print(f"TODO: {label}")
        else:
            print(f"Completed: {label} -> {result!r}")


if __name__ == "__main__":
    self_check()
