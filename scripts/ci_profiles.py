"""One complete grouping contract for ordinary CI and native publication jobs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNNERS = {"amd64": "ubuntu-24.04", "arm64": "ubuntu-24.04-arm"}
# ds60-{ci|pub}-{slug}-amd64-{15-digit run ID}-{2-digit attempt} must fit 49 characters.
MAX_PROJECT_GROUP_LENGTH = 15


def project_group_slug(group: str) -> str:
    """Fit a group in the 49-character native CI project name."""
    if len(group) <= MAX_PROJECT_GROUP_LENGTH:
        return group
    return group[:6] + "-" + hashlib.sha256(group.encode("ascii")).hexdigest()[:8]


def groups(root: Path = ROOT) -> list[dict[str, Any]]:
    payload = json.loads((root / "docker/ci-profile-groups.json").read_text())
    if set(payload) != {"schema_version", "groups"} or payload["schema_version"] != 1:
        raise ValueError("Invalid CI group registry")
    rows = payload["groups"]
    ordinary = {
        line.split()[0]
        for line in (root / "docker/classroom-images.tsv").read_text().splitlines()
        if line.strip() and not line.startswith("#") and line.split()[5] == "ordinary"
    }
    seen: set[str] = set()
    identities: set[str] = set()
    for row in rows:
        if (
            set(row) != {"id", "profiles"}
            or not isinstance(row["id"], str)
            or re.fullmatch(r"[a-z][a-z0-9-]{0,40}", row["id"]) is None
            or row["id"] in identities
            or not isinstance(row["profiles"], list)
            or not row["profiles"]
        ):
            raise ValueError("Invalid or repeated CI group")
        identities.add(row["id"])
        for profile in row["profiles"]:
            if profile not in ordinary or profile in seen:
                raise ValueError("CI profiles must be ordinary and appear exactly once")
            seen.add(profile)
    if seen != ordinary or next(
        (x["profiles"] for x in rows if x["id"] == "python-core"), None
    ) != ["python-core"]:
        raise ValueError("CI groups must cover every ordinary profile with a separate Core seed")
    return list(rows)


def selected(group: str, root: Path = ROOT) -> list[str]:
    matches = [row["profiles"] for row in groups(root) if row["id"] == group]
    if len(matches) != 1:
        raise ValueError("Unknown CI group")
    return list(matches[0])


def matrix(
    *, native: bool = False, workers_only: bool = False, root: Path = ROOT
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    project_groups: set[str] = set()
    for group in groups(root):
        if workers_only and group["id"] == "python-core":
            continue
        slug = project_group_slug(group["id"])
        if slug in project_groups:
            raise ValueError("CI project group slugs must be unique")
        project_groups.add(slug)
        item = {
            "group": group["id"],
            "profiles": " ".join(group["profiles"]),
            "project_group": slug,
        }
        if native:
            rows.extend(
                {**item, "architecture": arch, "runner": runner} for arch, runner in RUNNERS.items()
            )
        else:
            rows.append(item)
    return {"include": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", action="store_true")
    parser.add_argument("--workers-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(matrix(native=args.native, workers_only=args.workers_only)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
