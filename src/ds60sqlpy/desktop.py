"""Launch the browser application from source or a frozen native bundle."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from ds60sqlpy.catalog import Catalog, find_repo_root
from ds60sqlpy.lab import serve_lab

BUNDLE_PATHS = (
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "pyproject.toml",
    "curriculum",
    "courses",
    "examples",
    "python",
    "sql",
    "bridge",
    "docs",
    "lesson-pages",
    "reference-pages",
    "START_HERE.html",
    "scripts",
    "src",
    ".agents",
    "requirements",
    "uv.lock",
    ".python-version",
    ".env.example",
    "compose.yaml",
    "compose.modules.yaml",
    "compose.kubernetes.yaml",
    "START_MODULE_LAB.cmd",
    "START_DS60.cmd",
    "START_LEARNING_LAB.cmd",
    "START_DOCKER_LAB.cmd",
    "START_DOCKER_LAB.command",
    ".vscode",
    "Makefile",
    "Dockerfile",
    ".dockerignore",
    ".gitignore",
    "docker",
    ".editorconfig",
    ".gitattributes",
    ".pre-commit-config.yaml",
    ".github",
    "tests",
)


def prepare_workspace(source: Path, destination: Path) -> Path:
    """Install course assets once, preserving every existing learner file.

    A valid existing course is reused as-is. Different releases should use
    different workspaces; silently overwriting either official exercises or
    edited learner artifacts would lose work.
    """

    source, destination = source.resolve(), destination.resolve()
    if source == destination:
        return source
    if (destination / "curriculum/catalog.json").is_file():
        return destination
    for name in BUNDLE_PATHS:
        origin = source / name
        if origin.is_dir() and destination.is_relative_to(origin):
            raise ValueError("Choose a workspace outside the course's copied content directories.")
    if destination.is_dir():
        remaining = list(destination.iterdir())
        if any(path.name != ".learning" or not path.is_dir() for path in remaining):
            raise ValueError("Choose an empty directory or an existing DS60 course workspace.")
    destination.mkdir(parents=True, exist_ok=True)
    for name in BUNDLE_PATHS:
        origin, target = source / name, destination / name
        if origin.is_dir():
            shutil.copytree(
                origin,
                target,
                ignore=shutil.ignore_patterns(
                    "__pycache__",
                    "*.pyc",
                    "*.egg-info",
                    "*.dist-info",
                    ".DS_Store",
                    "cache",
                    ".ipynb_checkpoints",
                ),
            )
        elif origin.is_file():
            shutil.copy2(origin, target)
    return destination


def main(argv: list[str] | None = None) -> int:
    """Run the self-contained UI; coding uses the configured native backend."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, help="Use an existing course checkout.")
    parser.add_argument(
        "--workspace", type=Path, help="Persistent course and learner-work directory."
    )
    parser.add_argument("--python", help="Executable path for the Python/SQL pad backend.")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument(
        "--container", action="store_true", help="Explicit image-only container bind."
    )
    parser.add_argument(
        "--self-check", action="store_true", help="Verify bundle assets without serving."
    )
    args = parser.parse_args(argv)
    try:
        frozen = bool(getattr(sys, "frozen", False))
        if args.repo:
            source = find_repo_root(args.repo)
        elif frozen:
            source = Path(sys._MEIPASS) / "course"  # type: ignore[attr-defined]
        else:
            source = find_repo_root()
        if args.self_check:
            catalog = Catalog.load(source)
            missing = [
                path
                for lesson in catalog
                for path in (lesson.lesson_path, lesson.guide_path, *lesson.solution_paths)
                if not catalog.resolve(path).is_file()
            ]
            missing.extend(
                f"lesson-pages/{lesson.id}.html"
                for lesson in catalog
                if not (source / f"lesson-pages/{lesson.id}.html").is_file()
            )
            if not (source / "START_HERE.html").is_file():
                missing.append("START_HERE.html")
            print(json.dumps({"lessons": len(catalog.lessons()), "missing": missing}))
            return int(bool(missing))
        destination = args.workspace
        if destination is None and frozen:
            destination = Path.home() / "DS60 Learning Lab" / "0.3"
        root = prepare_workspace(source, destination) if destination else source
        serve_lab(
            Catalog.load(root),
            port=args.port,
            python=args.python,
            open_browser=not args.no_browser,
            container=args.container,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"Could not start DS60 Learning Lab: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
