#!/usr/bin/env python3
"""Select one complete native Docker CI group from an exact push HEAD marker."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ci_release_artifacts as artifacts  # noqa: E402
from scripts.ci_profiles import RUNNERS, groups, project_group_slug  # noqa: E402

MARKER = re.compile(r"\[(publish|build-test)-([a-z][a-z0-9-]*)\]")
SHA = re.compile(r"[a-f0-9]{40}")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
IDENTITY = re.compile(r"[1-9][0-9]{0,19}")
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")


@dataclass(frozen=True)
class Intent:
    mode: str
    group: str | None
    marker: str | None


def aliases(root: Path = ROOT) -> dict[str, str]:
    """A profile alias selects its entire qualification group."""
    result: dict[str, str] = {}
    for row in groups(root):
        group = row["id"]
        for alias in [group, *row["profiles"]]:
            prior = result.setdefault(alias, group)
            if prior != group:
                raise ValueError("A targeted marker alias maps to multiple groups")
    if "javascript-typescript" in result:
        if result.get("js", "javascript-typescript") != "javascript-typescript":
            raise ValueError("The js marker alias conflicts with a declared group")
        result["js"] = "javascript-typescript"
    return result


def parse_marker(message: str, root: Path = ROOT) -> Intent | None:
    """Reject malformed, unknown and multiple Docker publication markers."""
    if not isinstance(message, str):
        raise ValueError("A push HEAD commit message is required")
    matches = list(MARKER.finditer(message))
    # A malformed token must not be treated as an ordinary unmarked commit.
    if message.count("[publish-") + message.count("[build-test-") != len(matches):
        raise ValueError("A Docker marker is malformed or ambiguous")
    if len(matches) > 1:
        raise ValueError("Use exactly one Docker intent marker in the HEAD commit")
    if not matches:
        return None
    match = matches[0]
    token = match.group(0)
    if token == "[publish-docker]":
        return Intent("full", None, token)
    alias = match.group(2)
    if alias == "docker":
        raise ValueError("The complete release uses only [publish-docker]")
    group = aliases(root).get(alias)
    if group is None:
        raise ValueError("Unknown targeted Docker group or profile marker")
    return Intent(match.group(1), group, token)


def git_output(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False, timeout=30
    )
    if result.returncode:
        raise ValueError("Could not verify the checked-out push revision")
    return result.stdout.strip()


def read_event(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError("A bounded GitHub push event is required")
    raw = json.loads(path.read_bytes())
    if not isinstance(raw, dict):
        raise ValueError("Invalid GitHub push event")
    return raw


def push_intent(root: Path = ROOT) -> Intent | None:
    """Read the exact event and checkout; branches are allowed for build-test."""
    if os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("GITHUB_EVENT_NAME") != "push":
        raise ValueError("Targeted Docker CI requires a GitHub push")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    revision = os.environ.get("GITHUB_SHA", "")
    reference = os.environ.get("GITHUB_REF", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if (
        REPOSITORY.fullmatch(repository) is None
        or SHA.fullmatch(revision) is None
        or not reference.startswith("refs/heads/")
        or not event_path
    ):
        raise ValueError("Targeted Docker CI requires a branch push and exact revision")
    event = read_event(Path(event_path))
    head = event.get("head_commit")
    if (
        event.get("ref") != reference
        or event.get("deleted") is True
        or not isinstance(head, dict)
        or head.get("id") != revision
        or not isinstance(head.get("message"), str)
        or not isinstance(event.get("repository"), dict)
        or event["repository"].get("full_name") != repository
        or git_output(root, ["rev-parse", "HEAD"]) != revision
    ):
        raise ValueError("The checked-out HEAD differs from the pushed HEAD")
    event_intent = parse_marker(head["message"], root)
    source_intent = parse_marker(git_output(root, ["log", "-1", "--format=%B"]), root)
    if event_intent != source_intent:
        raise ValueError("Docker intent differs between the push event and checkout")
    if git_output(root, ["status", "--porcelain", "--untracked-files=normal"]):
        raise ValueError("Targeted Docker CI requires a clean checkout")
    if (
        event_intent is not None
        and event_intent.mode == "publish"
        and reference != "refs/heads/main"
    ):
        raise ValueError("Targeted Docker publication requires main")
    return event_intent


def selected_matrix(group: str, root: Path = ROOT) -> dict[str, Any]:
    rows = groups(root)
    selected = next((row for row in rows if row["id"] == group), None)
    if selected is None:
        raise ValueError("Unknown targeted qualification group")
    slug = project_group_slug(group)
    return {
        "include": [
            {
                "group": group,
                "profiles": " ".join(selected["profiles"]),
                "project_group": slug,
                "architecture": architecture,
                "runner": runner,
            }
            for architecture, runner in RUNNERS.items()
        ]
    }


def write_intent(intent: Intent | None, output: Path, root: Path = ROOT) -> None:
    mode = intent.mode if intent is not None and intent.mode != "full" else "ignore"
    group = intent.group if intent is not None and intent.group is not None else ""
    version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    if VERSION.fullmatch(version) is None:
        raise ValueError("Targeted CI requires a checked-in major.minor.patch version")
    matrix = selected_matrix(group, root) if group else {"include": []}
    with output.open("a", encoding="utf-8") as stream:
        stream.write(f"mode={mode}\ngroup={group}\nversion={version}\n")
        stream.write("matrix=" + json.dumps(matrix, separators=(",", ":")) + "\n")
    print(f"Targeted Docker intent: {mode}" + (f" ({group})" if group else ""))


def write_app_build_intent(output: Path, root: Path = ROOT) -> None:
    """Route exact branch intent; tag pushes use ordinary application checks."""
    branch_push = os.environ.get("GITHUB_EVENT_NAME") == "push" and not os.environ.get(
        "GITHUB_REF", ""
    ).startswith("refs/tags/")
    intent = push_intent(root) if branch_push else None
    mode = intent.mode if intent is not None else "ordinary"
    with output.open("a", encoding="utf-8") as stream:
        stream.write(f"mode={mode}\n")
    print("Application build intent: " + mode)


def download_receipts(group: str, destination: Path, root: Path = ROOT) -> None:
    if group not in {row["id"] for row in groups(root)}:
        raise ValueError("Unknown targeted receipt group")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    revision = os.environ.get("GITHUB_SHA", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    if (
        REPOSITORY.fullmatch(repository) is None
        or SHA.fullmatch(revision) is None
        or IDENTITY.fullmatch(run_id) is None
        or IDENTITY.fullmatch(attempt) is None
    ):
        raise ValueError("Select receipts from one exact GitHub run and revision")
    target = destination if destination.is_absolute() else root / destination
    if not target.absolute().is_relative_to(root / "work"):
        raise ValueError("Keep release receipts in this checkout's work directory")
    for parent in (target, *target.parents):
        if parent.is_symlink():
            raise ValueError("Receipt destination ancestry must not contain links")
        if parent == root:
            break
    keys = ["seed-" + arch for arch in RUNNERS]
    if group != "python-core":
        keys.extend(group + "-" + arch for arch in RUNNERS)
    pages = json.loads(
        artifacts.gh(
            [
                "api",
                "--paginate",
                "--slurp",
                f"repos/{repository}/actions/runs/{run_id}/artifacts?per_page=100",
            ],
            maximum=8 * 1024 * 1024,
        )
    )
    selected = artifacts.select_artifacts(pages, keys, int(attempt))
    payloads = [
        (
            item,
            artifacts.receipt_bytes(
                artifacts.gh(
                    ["api", f"repos/{repository}/actions/artifacts/{item.identifier}/zip"],
                    maximum=artifacts.MAX_ARCHIVE,
                ),
                item,
                repository=repository,
                revision=revision,
                run_id=run_id,
            ),
        )
        for item in selected
    ]
    if target.exists() and any(target.iterdir()):
        raise ValueError("Choose an empty targeted receipt destination")
    for item, raw in payloads:
        folder = target / item.key
        folder.mkdir(parents=True, exist_ok=False)
        (folder / "release-receipt.json").write_bytes(raw)
        print(f"Selected {item.key} from this run's attempt {item.attempt}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    intent = commands.add_parser("intent")
    intent.add_argument("--github-output", type=Path, required=True)
    app_build = commands.add_parser("app-build-intent")
    app_build.add_argument("--github-output", type=Path, required=True)
    receipts = commands.add_parser("receipts")
    receipts.add_argument("--group", required=True)
    receipts.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "intent":
            write_intent(push_intent(), args.github_output)
        elif args.command == "app-build-intent":
            write_app_build_intent(args.github_output)
        else:
            download_receipts(args.group, args.destination)
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print("Targeted Docker CI rejected: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
