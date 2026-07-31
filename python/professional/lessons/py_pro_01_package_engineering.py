"""python-pro-01 learner lab: package engineering and local releases.

Run this file from the repository root. The worked example reads the fixture
metadata without building anything. Complete the TODO functions in your own
copy, then use the companion guide's temporary-directory build procedure.

Professional learner deep dive (python-pro-01)
------------------------------------------------

Mental model:
A source tree is not the deliverable. The build backend reads `pyproject.toml` and creates a
wheel containing import packages plus distribution metadata. The **distribution name** used by
installers may differ from the Python **import name**. A src layout prevents an accidental
import from the repository root from masquerading as a successful installation.  A release check
therefore builds a wheel, inspects its contents and metadata, installs it into a clean
environment, imports it from outside the source tree, runs tests, and records hashes. Editable
installs are useful for development but do not prove the wheel.

API/boundary anatomy:
* `[build-system]`: declares the backend and bootstrap requirements that turn source into a
  distribution artifact.
* `[project]` metadata: defines distribution identity, version, Python range, dependencies, and
  entry points.
* `python -m build` then clean install: proves the built wheel, not repository-path import
  behavior.

Micro-example A — distinguish distribution and import identities::

    import importlib.util

    distribution_name = "beautiful-soup4"
    import_name = "bs4"
    print({"installer_name": distribution_name, "import_name": import_name})
    # The names are contracts for different tools and need not match.
    assert distribution_name.replace("-", "_") != import_name
    print("installed import available:", importlib.util.find_spec(import_name) is not None)

Expected: Installer and import identifiers can differ; availability must be checked through the
          intended interface.

Micro-example B — create a deterministic source manifest digest::

    import hashlib

    files = {
        "src/tiny/__init__.py": b'__version__ = "1.0.0"\n',
        "src/tiny/core.py": b"def add(a, b): return a + b\n",
    }
    manifest = "\n".join(
        f"{path}:{hashlib.sha256(content).hexdigest()}"
        for path, content in sorted(files.items())
    )
    digest = hashlib.sha256(manifest.encode("utf-8")).hexdigest()
    print(manifest, digest, sep="\n")
    assert len(digest) == 64

Expected: Sorting paths and hashing exact bytes gives a repeatable content identity, not a claim
          about package quality.

Debugging rule: Inspect wheel ZIP paths/METADATA/RECORD, install into a new environment, change
                the working directory, and print `module.__file__` plus distribution version.

The snippets demonstrate mechanics only. They do not complete the
numbered TODOs below; implement those from their stated contracts and
prove normal, boundary, and failure behavior.
"""

from __future__ import annotations

import tomllib
from collections.abc import Callable
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

    checks: tuple[tuple[str, Callable[[], object]], ...] = (
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


# === Numbered professional practice ===
#
# Attempt every exercise before opening solutions. Keep evidence in a copy
# under .learning/ or in tests; do not overwrite the reference solution.
# Full acceptance checks and progressive hints:
# companion-guides/py_pro_01_package_engineering.md
#
# Exercise 1 — classify artifacts
# Prompt: Implement `classify_artifact`. Use complete final suffixes and reject
# `package.whl.txt`. Add checks for one wheel, one sdist, and one unsupported file.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 2 — create an offline build command
# Prompt: Implement `offline_build_command` as an argument list. Use the running
# interpreter, invoke the `build` module, request both formats, disable isolation, and
# choose an explicit output directory. Why an argument list? It avoids a second round of
# shell parsing and behaves the same way in PowerShell, Command Prompt, Bash, and zsh.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 3 — inspect dependency intent
# Prompt: For each fixture entry, decide whether it is: 1. a runtime dependency, 2. an
# optional installed feature, 3. a development-only dependency group, or 4. a build
# bootstrap requirement. Explain when `colorama`'s environment marker is true. Confirm
# that building metadata does not install the `test` or `quality` groups.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 4 — build in a disposable directory
# Prompt: Use a temporary or ignored directory. A production-quality helper should first
# copy the source tree to a disposable staging directory because some backends write
# metadata beside the source even when `--outdir` is elsewhere. These commands
# intentionally prevent online build isolation. Invoke the running interpreter with
# `-m build --no-isolation --sdist --wheel --outdir <temporary-dir> <fixture>`. If a
# backend requirement is missing, return to connected setup instead of relaxing policy.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 5 — prove the installed origin
# Prompt: Install the wheel into a fresh target using `pip install --no-index --no-deps
# --target <directory> <wheel>`. Start Python from outside the fixture source tree, put
# only that target on `PYTHONPATH`, and print: - `ds60_tiny_greeter.__file__`, - the
# installed distribution version, - its `console_scripts` entry points, and -
# `greeting("wheel")`. Implement `installed_origin_is_safe` so it accepts only a resolved
# import path under the fresh installation target, never the fixture source tree.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 6 — build a wheel from the source distribution
# Prompt: Build the fixture sdist in disposable storage, unpack it, build a wheel from
# that unpacked sdist with `--no-isolation`, and compare the result with the direct wheel
# build. Record every required local tool.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 7 — inspect installed metadata without importing
# Prompt: Use `importlib.metadata` against the fresh target to inspect name, version,
# requirements, extras, and console scripts before importing the package. Reject
# unexpected or missing metadata.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 8 — separate reproducibility from equivalence
# Prompt: Build twice from the same clean staged source. Compare file hashes, archive
# member lists, metadata contents, and installed behavior. Explain which differences are
# harmless and which invalidate the release.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 9 — test dependency markers across targets
# Prompt: Create a review matrix for the fixture's build, runtime, optional, development,
# and environment-marked dependencies across Windows, macOS, Linux, Python 3.11, and
# Python 3.12.
# Verify: add a boundary check and explain the failure policy.
#
# Exercise 10 — design a local release gate
# Prompt: Write an offline release checklist that verifies clean source, tests, type/lint
# checks, sdist-to-wheel build, artifact contents, fresh install, metadata, hashes, and
# secret scan without publishing anything.
# Verify: add a boundary check and explain the failure policy.
#
# === End numbered professional practice ===

if __name__ == "__main__":
    self_check()
