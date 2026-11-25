"""Prove that local classroom images were built from one exact, clean source commit.

Inspects the selected local images and requires the OCI revision label to equal the
given 40-hex commit (empty and -dirty labels are rejected), the version label to equal
pyproject.toml, the source label to name the repository, and a native Linux platform.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REVISION = "org.opencontainers.image.revision"
VERSION = "org.opencontainers.image.version"
SOURCE = "org.opencontainers.image.source"
SOURCE_URL = "https://github.com/sadatnfs/ds60sqlpy"
DEFAULT_PROFILES = ("app", "python-core")
ARCHITECTURES = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}
REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")
# Same grammar as valid_image_version in scripts/classroom_images.sh.
TAG_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([.-][a-zA-Z0-9][a-zA-Z0-9.-]*)?$")

Runner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


class VerificationError(ValueError):
    """Raised for invalid arguments or catalog entries before any image is judged."""


def run_docker(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(command), check=False, capture_output=True, text=True, timeout=120)


def release_version(root: Path = ROOT) -> str:
    with (root / "pyproject.toml").open("rb") as handle:
        version = tomllib.load(handle)["project"]["version"]
    if not isinstance(version, str):
        raise VerificationError("pyproject.toml has no project version")
    return version


def local_repositories(root: Path = ROOT) -> dict[str, tuple[str, str]]:
    """Map profile to (local repository, kind) exactly as export_image_selection reads it."""
    result: dict[str, tuple[str, str]] = {}
    for line in (root / "docker/classroom-images.tsv").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 6:
            raise VerificationError(f"Malformed image catalog row: {line}")
        result[fields[0]] = (fields[2], fields[5])
    return result


def selected_profiles(requested: Sequence[str] | None, root: Path = ROOT) -> list[str]:
    catalog = local_repositories(root)
    ordered = ["app", *(requested or DEFAULT_PROFILES)]
    profiles: list[str] = []
    for profile in ordered:
        if profile in profiles:
            continue
        if profile not in catalog:
            raise VerificationError(f"Unknown image profile: {profile}")
        if catalog[profile][1] == "gpu":
            raise VerificationError(f"GPU profile {profile} is not a release image")
        profiles.append(profile)
    return profiles


def native_architecture(runner: Runner) -> str:
    result = runner(["docker", "info", "--format", "{{.Architecture}}"])
    engine = result.stdout.strip()
    if result.returncode != 0 or engine not in ARCHITECTURES:
        raise VerificationError(f"Could not determine a supported Docker architecture: {engine!r}")
    return ARCHITECTURES[engine]


def check_image(
    profile: str,
    reference: str,
    revision: str,
    version: str,
    architecture: str,
    runner: Runner,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "profile": profile,
        "reference": reference,
        "image_id": None,
        "labels": {"revision": None, "version": None, "source": None},
        "passed": False,
        "errors": [],
    }
    errors: list[str] = record["errors"]
    result = runner(["docker", "image", "inspect", "--format", "{{json .}}", reference])
    if result.returncode != 0:
        errors.append(f"{profile}: image {reference} is missing")
        return record
    try:
        raw = json.loads(result.stdout)
    except json.JSONDecodeError:
        errors.append(f"{profile}: docker returned unreadable inspect output")
        return record
    if not isinstance(raw, dict):
        errors.append(f"{profile}: docker returned unreadable inspect output")
        return record
    record["image_id"] = raw.get("Id")
    config = raw.get("Config") or {}
    labels = config.get("Labels") if isinstance(config, dict) else None
    labels = labels if isinstance(labels, dict) else {}
    found = {"revision": labels.get(REVISION), "version": labels.get(VERSION)}
    found["source"] = labels.get(SOURCE)
    record["labels"] = found
    label_revision = found["revision"]
    if not label_revision:
        errors.append(f"{profile}: revision label is empty or missing")
    elif str(label_revision).endswith("-dirty"):
        errors.append(f"{profile}: revision label {label_revision} was built from a dirty tree")
    elif label_revision != revision:
        errors.append(f"{profile}: revision label {label_revision} is not {revision}")
    if found["version"] != version:
        errors.append(f"{profile}: version label {found['version']!r} is not {version}")
    if found["source"] != SOURCE_URL:
        errors.append(f"{profile}: source label {found['source']!r} is not {SOURCE_URL}")
    if raw.get("Os") != "linux":
        errors.append(f"{profile}: operating system {raw.get('Os')!r} is not linux")
    if raw.get("Architecture") != architecture:
        errors.append(f"{profile}: architecture {raw.get('Architecture')!r} is not {architecture}")
    record["passed"] = not errors
    return record


def verify(
    revision: str,
    tag: str,
    profiles: Sequence[str] | None = None,
    architecture: str | None = None,
    runner: Runner = run_docker,
    root: Path = ROOT,
) -> dict[str, Any]:
    if not REVISION_PATTERN.fullmatch(revision):
        raise VerificationError("--revision must be a full 40 character lowercase hex commit")
    if not TAG_PATTERN.fullmatch(tag):
        raise VerificationError(f"Invalid image tag: {tag}")
    selection = selected_profiles(profiles, root)
    catalog = local_repositories(root)
    version = release_version(root)
    arch = architecture or native_architecture(runner)
    if arch not in {"amd64", "arm64"}:
        raise VerificationError(f"Unsupported architecture: {arch}")
    images = [
        check_image(profile, f"{catalog[profile][0]}:{tag}", revision, version, arch, runner)
        for profile in selection
    ]
    return {
        "schema_version": 1,
        "revision": revision,
        "tag": tag,
        "architecture": arch,
        "passed": all(image["passed"] for image in images),
        "images": images,
    }


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", required=True, help="Expected 40 hex commit")
    parser.add_argument(
        "--tag", required=True, help="Local image tag, for example 2.1.0-p7abcd1234"
    )
    parser.add_argument(
        "--profile",
        action="append",
        dest="profiles",
        help="Profile to verify (repeatable; app is always included)",
    )
    parser.add_argument("--architecture", choices=("amd64", "arm64"))
    parser.add_argument("--report", type=Path, default=ROOT / "work/image-revision.json")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None, runner: Runner = run_docker) -> int:
    args = parse_args(argv)
    try:
        report = verify(args.revision, args.tag, args.profiles, args.architecture, runner)
    except VerificationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    for image in report["images"]:
        status = "ok" if image["passed"] else "FAILED"
        print(f"{status}: {image['profile']} {image['reference']} {image['image_id']}")
        for message in image["errors"]:
            print(f"  {message}", file=sys.stderr)
    print(f"Report: {args.report}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
