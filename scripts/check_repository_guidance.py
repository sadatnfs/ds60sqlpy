#!/usr/bin/env python3
"""Check maintained contributor guidance without network access or source writes.

Checks repository-local Markdown targets, registered subject guides, skill identity
and retired command paths. Fragment IDs remain owned by check_published_links.py.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "src"))

from ds60sqlpy.checks import MARKDOWN_LINK, _markdown_link_text  # noqa: E402
from ds60sqlpy.curriculum_framework import is_content_link  # noqa: E402
from ds60sqlpy.modules import ModuleCatalog  # noqa: E402

REQUIRED_SKILLS = ("add-learning-path", "guide-ds60sqlpy-learning")
EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        ".venv",
        ".learning",
        ".classroom",
        ".module-runtime",
        ".app-build",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
        "node_modules",
        "build",
        "dist",
        "work",
        "artifacts",
        "mlruns",
        "lesson-pages",
        "reference-pages",
    }
)
# Exact retired repository paths, not generic terms such as "native" or "CMake".
# This gate scans guidance only, never lesson programs or negative test fixtures.
RETIRED_PATHS = frozenset(
    {
        "START_DS60.cmd",
        "START_LEARNING_LAB.cmd",
        "START_MODULE_LAB.cmd",
        "START_DOCKER_LAB.cmd",
        "START_DOCKER_LAB.command",
        "scripts/bootstrap_windows.ps1",
        "scripts/setup.ps1",
        "scripts/start_ds60.ps1",
        "scripts/start_docker_windows.ps1",
        "scripts/build_app.py",
        "scripts/build_windows_starter.py",
        "scripts/build_journey_preview.py",
        "scripts/learning_portal.py",
        "scripts/learning_lab.py",
        "scripts/docker_lab.py",
        "scripts/docker_lab.sh",
        "scripts/docker_lab.ps1",
        "scripts/module_lab.sh",
        "scripts/module_lab.ps1",
        "src/ds60sqlpy/desktop.py",
        "src/ds60sqlpy/portal.py",
        "src/ds60sqlpy/journey_design.py",
    }
)
RETIRED_PATTERN = re.compile(
    r"(?<![\w./-])(?:"
    + "|".join(re.escape(path) for path in sorted(RETIRED_PATHS))
    + r")(?![\w.-])"
)


def guidance_paths(root: Path) -> list[Path]:
    """Inventory guidance, excluding generated readers, private state and fixtures."""
    paths: list[Path] = []
    for directory, children, names in os.walk(root, followlinks=False):
        children[:] = sorted(
            name
            for name in children
            if name not in EXCLUDED_DIRECTORIES and not is_content_link(Path(directory) / name)
        )
        for name in names:
            path = Path(directory) / name
            relative = path.relative_to(root)
            parts = relative.parts
            if (
                name == "AGENTS.md"
                or relative.as_posix() in {"README.md", "CONTRIBUTING.md"}
                or (parts[0] == "docs" and path.suffix == ".md")
                or (parts[:2] == (".agents", "skills") and path.suffix == ".md")
                or (
                    parts[0] == "courses"
                    and name == "README.md"
                    and (len(parts) == 3 or "authoring" in parts)
                )
                or relative.as_posix() == "docker/formatting/README.md"
            ):
                paths.append(path)
    return sorted(paths)


def inspect_guidance(root: Path, *, subject_ids: Iterable[str] | None = None) -> dict[str, Any]:
    """Inspect a clone/staged package; explicit subject IDs only support small test fixtures."""
    root = root.resolve()
    failures: list[dict[str, Any]] = []
    documents: dict[Path, str] = {}
    links_checked = 0
    external_skipped = 0
    fragments_skipped = 0

    def fail(path: Path, kind: str, target: str = "", line: int = 0) -> None:
        failures.append(
            {
                "path": path.relative_to(root).as_posix(),
                "line": line,
                "kind": kind,
                "target": target,
            }
        )

    def safe_path(path: Path) -> bool:
        candidate = root
        for part in path.relative_to(root).parts:
            candidate /= part
            if is_content_link(candidate):
                return False
        return True

    subjects: list[str] = []
    if subject_ids is None:
        try:
            subjects = [str(plan["id"]) for plan in ModuleCatalog(root).plans]
        except (OSError, UnicodeError, ValueError) as exc:
            fail(root, "invalid_module_catalog", type(exc).__name__)
    else:
        subjects = sorted(set(subject_ids))
    required = [root / name for name in ("README.md", "CONTRIBUTING.md", "AGENTS.md")]
    required += [root / ".agents/skills" / name / "SKILL.md" for name in REQUIRED_SKILLS]
    required += [
        root / "courses" / subject / name
        for subject in subjects
        for name in ("README.md", "AGENTS.md")
    ]
    for path in sorted(set(guidance_paths(root)) | set(required)):
        if not safe_path(path):
            fail(path, "linked_guidance_source")
            continue
        if not path.is_file():
            fail(path, "missing_guidance_source")
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            fail(path, "unreadable_guidance_source", type(exc).__name__)
            continue
        documents[path] = source
        # Commands in shell fences are still instructions. Link-shaped teaching
        # examples are excluded separately by the shared Markdown literal parser.
        for match in RETIRED_PATTERN.finditer(source.replace("\\", "/")):
            fail(path, "retired_command_path", match[0], source.count("\n", 0, match.start()) + 1)
        visible = _markdown_link_text(source)
        for match in MARKDOWN_LINK.finditer(visible):
            raw = match["target"].strip()
            # Common inline destinations may have an optional quoted title.
            if raw.startswith("<"):
                target = raw.partition(">")[0][1:]
            else:
                target = re.split(r"\s+[\"']", raw, maxsplit=1)[0]
            line = visible.count("\n", 0, match.start()) + 1
            try:
                parsed = urlsplit(target)
                if parsed.scheme.lower() == "file" or re.match(r"^[A-Za-z]:", target):
                    fail(path, "external_filesystem_target", target, line)
                    continue
                if parsed.scheme or parsed.netloc:
                    external_skipped += 1
                    continue
                local = unquote(parsed.path)
                if "\\" in local or local.startswith(("/", "~")):
                    fail(path, "external_filesystem_target", target, line)
                    continue
                destination = (path.parent / local).resolve()
                if not destination.is_relative_to(root):
                    fail(path, "external_filesystem_target", target, line)
                    continue
                links_checked += 1
                fragments_skipped += bool(parsed.fragment)
                if not safe_path(path.parent / local):
                    fail(path, "linked_local_target", target, line)
                elif not destination.exists():
                    fail(path, "missing_local_target", target, line)
            except (OSError, ValueError):
                fail(path, "invalid_local_target", target, line)

    identities: dict[str, Path] = {}
    skills_checked = 0
    for path, source in documents.items():
        if path.name != "SKILL.md" or path.relative_to(root).parts[:2] != (".agents", "skills"):
            continue
        skills_checked += 1
        # This is intentionally a narrow identity contract, not a second YAML
        # implementation. The skill-authoring validator owns the full schema.
        lines = source.splitlines()
        if not lines or lines[0] != "---" or "---" not in lines[1:]:
            fail(path, "missing_skill_frontmatter")
            continue
        header = lines[1 : lines[1:].index("---") + 1]
        names = [line.partition(":")[2].strip() for line in header if line.startswith("name:")]
        descriptions = [
            line.partition(":")[2].strip() for line in header if line.startswith("description:")
        ]
        if len(names) != 1:
            fail(path, "invalid_skill_identity")
            continue
        identity = names[0]
        if identity.startswith(("'", '"')) and identity.endswith(identity[0]):
            identity = identity[1:-1]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identity) or identity != path.parent.name:
            fail(path, "invalid_skill_identity", identity)
        if identity in identities:
            fail(path, "duplicate_skill_identity", identity)
        identities[identity] = path
        if len(descriptions) != 1 or not descriptions[0].strip("'\" "):
            fail(path, "missing_skill_description")

    return {
        "schema_version": 1,
        "guidance_files_checked": len(documents),
        "module_subjects_checked": len(subjects),
        "skills_checked": skills_checked,
        "local_links_checked": links_checked,
        "external_urls_skipped": external_skipped,
        "fragments_deferred": fragments_skipped,
        "failure_count": len(failures),
        "failures": failures,
        "limitations": [
            "External URLs are not fetched or validated.",
            "Fragments are checked in generated HTML by check_published_links.py, not here.",
            "Only inline Markdown links are parsed; raw HTML and reference-style links are not.",
            "Code examples are excluded from links; exact retired command paths are checked.",
            "Skill identity and description are checked; full YAML validation is a separate gate.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true", help="print the complete JSON report")
    parser.add_argument("--report", type=Path, help="explicit optional JSON report destination")
    args = parser.parse_args(argv)
    report = inspect_guidance(args.root)
    serialized = json.dumps(report, indent=2) + "\n"
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(serialized, encoding="utf-8")
    if args.json:
        print(serialized, end="")
    else:
        print(
            f"Repository guidance: {report['guidance_files_checked']} documents; "
            f"{report['module_subjects_checked']} module subjects; "
            f"{report['failure_count']} failures."
        )
        for failure in report["failures"]:
            print(f"- {failure['path']}:{failure['line']}: {failure['kind']}: {failure['target']}")
    return int(bool(report["failure_count"]))


if __name__ == "__main__":
    raise SystemExit(main())
