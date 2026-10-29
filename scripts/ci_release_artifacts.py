"""Download bounded release receipts from this run's latest successful logical attempts."""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import stat
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.ci_profiles import RUNNERS, groups  # noqa: E402

MAX_JSON = 256 * 1024
MAX_ARCHIVE = 512 * 1024


@dataclass(frozen=True)
class Artifact:
    key: str
    attempt: int
    identifier: int
    name: str


def logical_keys(mode: str, architecture: str | None = None) -> list[str]:
    if mode == "gate":
        return ["gate"]
    if mode == "seed":
        if architecture not in RUNNERS:
            raise ValueError("Select a native seed architecture")
        return ["seed-" + str(architecture)]
    if mode == "scientific":
        if architecture is not None and architecture not in RUNNERS:
            raise ValueError("Select a native scientific architecture")
        return ["scientific-" + arch for arch in ([architecture] if architecture else RUNNERS)]
    if mode != "receipts":
        raise ValueError("Unknown release artifact selection")
    return ["seed-" + arch for arch in RUNNERS] + [
        group["id"] + "-" + arch
        for group in groups()
        if group["id"] != "python-core"
        for arch in RUNNERS
    ]


def select_artifacts(pages: Any, keys: list[str], current_attempt: int) -> list[Artifact]:
    if not isinstance(pages, list) or not pages or len(pages) > 100:
        raise ValueError("Invalid artifact pagination")
    selected = []
    for key in keys:
        prefix = (
            "release-gate"
            if key == "gate"
            else "scientific-projects-" + key.removeprefix("scientific-")
            if key.startswith("scientific-")
            else "release-receipt-" + key
        )
        pattern = re.compile(re.escape(prefix) + r"-attempt-([1-9][0-9]{0,5})\Z")
        candidates = []
        for page in pages:
            if not isinstance(page, dict) or not isinstance(page.get("artifacts"), list):
                raise ValueError("Invalid workflow artifact listing")
            for raw in page["artifacts"]:
                if not isinstance(raw, dict) or not isinstance(raw.get("name"), str):
                    raise ValueError("Invalid artifact metadata")
                match = pattern.fullmatch(raw["name"])
                if match is None or raw.get("expired") is not False:
                    continue
                attempt = int(match[1])
                if attempt > current_attempt:
                    continue
                if type(raw.get("id")) is not int or raw["id"] < 1:
                    raise ValueError("Invalid artifact identity")
                if (
                    type(raw.get("size_in_bytes")) is not int
                    or not 0 < raw["size_in_bytes"] <= MAX_ARCHIVE
                ):
                    raise ValueError("Release artifacts must contain only bounded JSON receipts")
                candidates.append(Artifact(key, attempt, raw["id"], raw["name"]))
        if not candidates:
            raise ValueError(
                "No unexpired successful receipt for "
                + key
                + "; rerun its failed qualification job"
            )
        latest = max(item.attempt for item in candidates)
        matches = [item for item in candidates if item.attempt == latest]
        if len(matches) != 1:
            raise ValueError("Ambiguous latest receipt for " + key)
        selected.append(matches[0])
    return selected


def unique_fields(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate receipt field")
        result[key] = value
    return result


def receipt_bytes(
    archive: bytes, artifact: Artifact, *, repository: str, revision: str, run_id: str
) -> bytes:
    if len(archive) > MAX_ARCHIVE:
        raise ValueError("Release artifact exceeds its archive bound")
    scientific = artifact.key.startswith("scientific-")
    filename = (
        "gate.json"
        if artifact.key == "gate"
        else "scientific-receipt.json"
        if scientific
        else "release-receipt.json"
    )
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        entries = bundle.infolist()
        if len(entries) != 1:
            raise ValueError("Release artifact must contain exactly one receipt")
        entry = entries[0]
        if (
            entry.filename != filename
            or stat.S_ISLNK(entry.external_attr >> 16)
            or entry.file_size > MAX_JSON
        ):
            raise ValueError("Unexpected or linked artifact member")
        with bundle.open(entry) as stream:
            raw = stream.read(MAX_JSON + 1)
        if len(raw) > MAX_JSON or len(raw) != entry.file_size:
            raise ValueError("Release receipt exceeds its bound")
    document = json.loads(raw, object_pairs_hook=unique_fields)
    if not isinstance(document, dict) or not isinstance(document.get("context"), dict):
        raise ValueError("Missing release receipt context")
    expected_kind = (
        "ds60-release-gate"
        if artifact.key == "gate"
        else "ds60-scientific-projects"
        if scientific
        else "ds60-staged-images"
    )
    if (
        document.get("kind") != expected_kind
        or type(document.get("schema_version")) is not int
        or document["schema_version"] != 1
    ):
        raise ValueError("Unexpected release receipt type")
    for field, expected in {
        "source_repository": repository,
        "revision": revision,
        "run_id": run_id,
        "run_attempt": str(artifact.attempt),
    }.items():
        if document["context"].get(field) != expected:
            raise ValueError("Receipt is not from the selected run, revision and attempt")
    if scientific:
        if document.get("architecture") != artifact.key.removeprefix("scientific-"):
            raise ValueError("Scientific receipt architecture differs from its artifact")
        if document.get("passed") is not True or document.get("complete") is not True:
            raise ValueError("Scientific receipt is not a successful complete qualification")
    elif artifact.key != "gate":
        group, architecture = artifact.key.rsplit("-", 1)
        if document.get("architecture") != architecture:
            raise ValueError("Receipt architecture differs from its logical artifact")
        required = (
            {"app", "python-core"}
            if group == "seed"
            else set(next(row["profiles"] for row in groups() if row["id"] == group))
        )
        images = document.get("images")
        if not isinstance(images, list) or any(not isinstance(row, dict) for row in images):
            raise ValueError("Invalid receipt image selection")
        listed = [row.get("profile") for row in images]
        if (
            any(not isinstance(item, str) for item in listed)
            or len(listed) != len(required)
            or set(listed) != required
        ):
            raise ValueError("Receipt images differ from its logical CI group")
    return raw


def gh(args: list[str], *, maximum: int) -> bytes:
    result = subprocess.run(["gh", *args], capture_output=True, check=False, timeout=120)
    if result.returncode or len(result.stdout) > maximum:
        raise ValueError("Could not read bounded artifacts from this workflow run")
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("gate", "seed", "receipts", "scientific"))
    parser.add_argument("--architecture", choices=tuple(RUNNERS))
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    revision = os.environ.get("GITHUB_SHA", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    if (
        re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is None
        or re.fullmatch(r"[a-f0-9]{40}", revision) is None
        or re.fullmatch(r"[1-9][0-9]{0,19}", run_id) is None
        or re.fullmatch(r"[1-9][0-9]{0,5}", attempt) is None
    ):
        parser.error("Use a specific GitHub workflow run and revision")
    destination = args.destination if args.destination.is_absolute() else ROOT / args.destination
    if not destination.absolute().is_relative_to(ROOT / "work"):
        raise ValueError("Keep downloaded release evidence under this checkout's work directory")
    for parent in (destination, *destination.parents):
        if parent.is_symlink():
            raise ValueError("Artifact destination ancestry must not contain links")
        if parent == ROOT:
            break
    pages = json.loads(
        gh(
            [
                "api",
                "--paginate",
                "--slurp",
                f"repos/{repository}/actions/runs/{run_id}/artifacts?per_page=100",
            ],
            maximum=8 * 1024 * 1024,
        )
    )
    selections = select_artifacts(pages, logical_keys(args.mode, args.architecture), int(attempt))
    # Resolve and validate every requested receipt before writing any local selection.
    payloads = []
    for artifact in selections:
        raw = gh(
            ["api", f"repos/{repository}/actions/artifacts/{artifact.identifier}/zip"],
            maximum=MAX_ARCHIVE,
        )
        payloads.append(
            (
                artifact,
                receipt_bytes(
                    raw, artifact, repository=repository, revision=revision, run_id=run_id
                ),
            )
        )
    for artifact, raw in payloads:
        directory = (
            destination / artifact.key if args.mode in {"receipts", "scientific"} else destination
        )
        directory.mkdir(parents=True, exist_ok=True)
        if directory.is_symlink():
            raise ValueError("Artifact destination must not be a link")
        filename = (
            "gate.json"
            if artifact.key == "gate"
            else "scientific-receipt.json"
            if artifact.key.startswith("scientific-")
            else "release-receipt.json"
        )
        path = directory / filename
        if path.exists() or path.is_symlink():
            raise ValueError("Use an empty artifact destination")
        path.write_bytes(raw)
        print(f"Selected {artifact.key} from this run's attempt {artifact.attempt}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, subprocess.SubprocessError) as error:
        print(f"Release artifact selection failed: {error}", file=sys.stderr)
        raise SystemExit(1) from None
