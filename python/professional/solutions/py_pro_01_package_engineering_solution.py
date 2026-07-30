"""Reference implementation for python-pro-01.

All build and installation output is confined to a caller-provided directory.
The default demonstration uses ``TemporaryDirectory`` and disables dependency
resolution, build isolation, bytecode generation, and network index access.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

ArtifactKind = Literal["wheel", "source distribution"]
FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "tiny_package"


class BuildToolUnavailable(RuntimeError):
    """Raised when the local bootstrap lacks a required build tool."""


@dataclass(frozen=True)
class ProjectSummary:
    """Selected metadata from a ``pyproject.toml`` document."""

    name: str
    version: str
    build_backend: str
    console_scripts: dict[str, str]
    dependency_groups: tuple[str, ...]
    optional_dependencies: tuple[str, ...]


@dataclass(frozen=True)
class InstallProof:
    """Evidence that a wheel—not the source tree—supplied the import."""

    wheel: Path
    import_origin: Path
    install_target: Path
    distribution_version: str
    console_scripts: tuple[str, ...]
    command_output: str


def load_pyproject(project_root: Path) -> dict[str, Any]:
    """Load a project's TOML document with the Python 3.11 standard library."""

    pyproject = project_root / "pyproject.toml"
    with pyproject.open("rb") as handle:
        return tomllib.load(handle)


def summarize_project(project_root: Path = FIXTURE) -> ProjectSummary:
    """Validate and summarize the fixture's important packaging tables."""

    document = load_pyproject(project_root)
    project = document.get("project")
    build_system = document.get("build-system")
    if not isinstance(project, dict):
        raise ValueError("pyproject.toml is missing [project]")
    if not isinstance(build_system, dict):
        raise ValueError("pyproject.toml is missing [build-system]")

    scripts = project.get("scripts", {})
    groups = document.get("dependency-groups", {})
    optional = project.get("optional-dependencies", {})
    if not isinstance(scripts, dict):
        raise ValueError("[project.scripts] must be a table")
    if not isinstance(groups, dict):
        raise ValueError("[dependency-groups] must be a table")
    if not isinstance(optional, dict):
        raise ValueError("[project.optional-dependencies] must be a table")

    return ProjectSummary(
        name=str(project["name"]),
        version=str(project["version"]),
        build_backend=str(build_system["build-backend"]),
        console_scripts={str(key): str(value) for key, value in scripts.items()},
        dependency_groups=tuple(sorted(str(key) for key in groups)),
        optional_dependencies=tuple(sorted(str(key) for key in optional)),
    )


def classify_artifact(path: Path) -> ArtifactKind:
    """Classify a Python distribution by its complete filename suffix."""

    if path.suffix == ".whl":
        return "wheel"
    if path.name.endswith(".tar.gz"):
        return "source distribution"
    raise ValueError(f"unsupported distribution artifact: {path.name}")


def require_local_build_tools() -> None:
    """Fail before a build if the connected bootstrap was not completed."""

    missing = [
        module
        for module in ("build", "setuptools", "wheel")
        if importlib.util.find_spec(module) is None
    ]
    if missing:
        names = ", ".join(missing)
        raise BuildToolUnavailable(
            f"missing local build tools: {names}; install them during bootstrap"
        )


def build_distributions(project_root: Path, output_dir: Path) -> tuple[Path, Path]:
    """Build an sdist and wheel without an isolated environment or downloads."""

    require_local_build_tools()
    project_root = project_root.resolve()
    output_dir = output_dir.resolve()
    if output_dir.is_relative_to(project_root):
        raise ValueError("build output must be outside the source project")
    output_dir.mkdir(parents=True, exist_ok=True)
    staged_project = output_dir.parent / "staged-project"
    if staged_project.exists():
        raise FileExistsError(f"staging path already exists: {staged_project}")
    shutil.copytree(project_root, staged_project)
    command = [
        sys.executable,
        "-m",
        "build",
        "--no-isolation",
        "--sdist",
        "--wheel",
        "--outdir",
        str(output_dir),
        str(staged_project),
    ]
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"local build failed: {detail}")

    wheels = sorted(output_dir.glob("*.whl"))
    sdists = sorted(output_dir.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise RuntimeError(
            f"expected one wheel and one sdist, found {len(wheels)} and {len(sdists)}"
        )
    return wheels[0], sdists[0]


def _proof_program(distribution_name: str, package_name: str) -> str:
    """Return a small subprocess program that prints install evidence as JSON."""

    return "\n".join(
        (
            "import importlib.metadata as metadata",
            "import json",
            f"import {package_name} as package",
            f"distribution = metadata.distribution({distribution_name!r})",
            "scripts = sorted(",
            "    entry.name for entry in distribution.entry_points",
            "    if entry.group == 'console_scripts'",
            ")",
            "print(json.dumps({",
            "    'origin': package.__file__,",
            "    'version': distribution.version,",
            "    'scripts': scripts,",
            "    'output': package.greeting('wheel'),",
            "}))",
        )
    )


def install_wheel_and_prove(
    wheel: Path,
    workspace: Path,
    *,
    distribution_name: str = "ds60-tiny-greeter",
    package_name: str = "ds60_tiny_greeter",
) -> InstallProof:
    """Install a wheel locally and prove import and entry-point metadata."""

    install_target = workspace / "site"
    install_target.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    install_command = [
        sys.executable,
        "-m",
        "pip",
        "--disable-pip-version-check",
        "install",
        "--no-index",
        "--no-deps",
        "--no-compile",
        "--target",
        str(install_target),
        str(wheel),
    ]
    installed = subprocess.run(
        install_command,
        check=False,
        capture_output=True,
        text=True,
        cwd=workspace,
        env=environment,
    )
    if installed.returncode != 0:
        detail = installed.stderr.strip() or installed.stdout.strip()
        raise RuntimeError(f"local wheel install failed: {detail}")

    proof_environment = environment.copy()
    proof_environment["PYTHONPATH"] = str(install_target)
    proof = subprocess.run(
        [sys.executable, "-c", _proof_program(distribution_name, package_name)],
        check=False,
        capture_output=True,
        text=True,
        cwd=workspace,
        env=proof_environment,
    )
    if proof.returncode != 0:
        raise RuntimeError(f"installed import proof failed: {proof.stderr.strip()}")
    payload = json.loads(proof.stdout)
    origin = Path(payload["origin"]).resolve()
    target = install_target.resolve()
    if not origin.is_relative_to(target):
        raise RuntimeError(f"import escaped install target: {origin}")

    return InstallProof(
        wheel=wheel.resolve(),
        import_origin=origin,
        install_target=target,
        distribution_version=str(payload["version"]),
        console_scripts=tuple(str(name) for name in payload["scripts"]),
        command_output=str(payload["output"]),
    )


def build_and_prove(project_root: Path = FIXTURE) -> InstallProof:
    """Complete the offline build/install proof in a temporary workspace."""

    with tempfile.TemporaryDirectory(prefix="ds60-package-proof-") as directory:
        workspace = Path(directory)
        wheel, sdist = build_distributions(project_root, workspace / "dist")
        assert classify_artifact(wheel) == "wheel"
        assert classify_artifact(sdist) == "source distribution"
        return install_wheel_and_prove(wheel, workspace)


def main() -> int:
    """Inspect the fixture and run the proof when build tools are available."""

    summary = summarize_project()
    print(f"{summary.name} {summary.version}")
    print(f"backend: {summary.build_backend}")
    print(f"console scripts: {', '.join(summary.console_scripts)}")
    print(f"dependency groups: {', '.join(summary.dependency_groups)}")
    try:
        proof = build_and_prove()
    except BuildToolUnavailable as exc:
        print(f"Build proof not run: {exc}")
        return 0
    print(f"wheel import: {proof.import_origin}")
    print(f"installed command metadata: {', '.join(proof.console_scripts)}")
    print(f"command behavior: {proof.command_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
