#!/usr/bin/env python3
"""DS60 image vulnerability gate: digest-pinned Trivy via `docker run`, DS60 policy, evidence.

Trivy only produces JSON (`--exit-code 0`, no ignorefile). This module decides pass or fail:
fixable findings always block, unfixed CRITICAL/HIGH findings block unless an exact,
unexpired entry in `docker/cve-policy.json` covers them, secrets block, HIGH/CRITICAL
misconfig failures block unless accepted, and unscannable images fail closed. Evidence is
bound to each image ID, the scanner digest, the DB timestamps and the policy hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

TRIVY_VERSION = "0.76.2"
TRIVY_IMAGE = (
    "aquasec/trivy:0.76.2@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb"
)
DEFAULT_CACHE = Path("~/.cache/ds60sqlpy/trivy")
DEFAULT_POLICY = ROOT / "docker/cve-policy.json"
REFERENCE_PROFILES = frozenset({"postgres"})
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")
SERIOUS = frozenset({"CRITICAL", "HIGH"})
MAX_POLICY_DAYS = 90
MAX_DB_AGE = timedelta(hours=24)
MAX_REPORT = 1024 * 1024 * 1024
REVISION_LABEL = "org.opencontainers.image.revision"
ARCHITECTURES = ("amd64", "arm64")
POLICY_KINDS = ("vulnerability", "misconfig", "coverage")
ENTRY_KEYS = frozenset(
    {"id", "kind", "package", "images", "justification", "reviewer", "reviewed_at", "expires_at"}
)
COVERAGE_IDS = frozenset({"unsupported-os", "os-not-detected", "no-packages"})
ADVISORY = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Za-z0-9.]+)+\Z")
ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
IMAGE_ID = re.compile(r"sha256:[a-f0-9]{64}\Z")
SHA = re.compile(r"[a-f0-9]{40}\Z")
IDENTIFIER = re.compile(r"[a-z][a-z0-9-]{0,39}\Z")
CONTEXT_KEYS = frozenset(
    {"namespace", "repository", "source_repository", "version", "revision", "run_id", "run_attempt"}
)
TESTED_KEYS = frozenset(
    {"schema_version", "kind", "context", "architecture", "group", "seed_receipt", "images"}
)
TESTED_IMAGE_KEYS = frozenset(
    {"profile", "local_repository", "tested_image_id", "local_descriptor"}
)
WILDCARD = frozenset("*?[]")

Runner = Callable[[list[str]], str]


class ScanError(Exception):
    """Invalid input, policy or scanner state; the gate fails."""


@dataclass(frozen=True)
class Entry:
    id: str
    kind: str
    package: str
    images: tuple[str, ...]
    justification: str
    reviewer: str
    reviewed_at: date
    expires_at: date

    def covers(self, kind: str, finding_id: str, package: str, profile: str) -> bool:
        return (
            self.kind == kind
            and self.id == finding_id
            and self.package == package
            and profile in self.images
        )

    def key(self) -> dict[str, Any]:
        return {"id": self.id, "kind": self.kind, "package": self.package, "images": [*self.images]}


@dataclass(frozen=True)
class Policy:
    entries: tuple[Entry, ...]
    sha256: str


def default_runner(argv: list[str]) -> str:
    try:
        result = subprocess.run(argv, capture_output=True, text=True, check=False, timeout=3600)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ScanError(f"Cannot run {argv[0]}: {error}") from None
    if result.returncode:
        tail = (result.stderr or result.stdout).strip().splitlines()[-5:]
        raise ScanError(f"{' '.join(argv[:3])} failed: " + " | ".join(tail))
    return result.stdout


def utc_now() -> datetime:
    return datetime.now(UTC)


def iso(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(value: Any) -> datetime:
    """Parse an RFC 3339 timestamp; Trivy writes nanoseconds, which are truncated."""
    if not isinstance(value, str):
        raise ScanError("Scanner timestamp is missing")
    match = re.fullmatch(
        r"([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.([0-9]+))?(Z|[+-][0-9:]{5})",
        value,
    )
    if match is None:
        raise ScanError(f"Invalid scanner timestamp: {value!r}")
    fraction = (match.group(2) or "0")[:6].ljust(6, "0")
    zone = "+00:00" if match.group(3) == "Z" else match.group(3)
    return datetime.fromisoformat(f"{match.group(1)}.{fraction}{zone}").astimezone(UTC)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    data = json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    write_text(path, data)


def write_text(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ScanError(f"Output must not be a symbolic link: {path}")
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = stream.name
            stream.write(data)
        Path(temporary).replace(path)
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def read_json(path: Path, maximum: int = 16 * 1024 * 1024) -> Any:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > maximum:
        raise ScanError(f"Input must be a bounded ordinary file: {path}")
    try:
        return json.loads(path.read_text("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ScanError(f"Invalid JSON in {path}: {error}") from None


def resolve_cache(path: Path, root: Path = ROOT) -> Path:
    """Expand the Trivy cache path and refuse one inside the repository (D-01)."""
    cache = path.expanduser().resolve()
    if cache.is_relative_to(root.resolve()):
        raise ScanError(f"Trivy cache must live outside the repository: {cache}")
    return cache


def catalog_profiles(root: Path = ROOT) -> frozenset[str]:
    """Publishable (non-GPU) catalog profiles, as `docker_release.catalog` reads them."""
    path = root / "docker/classroom-images.tsv"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 64_000:
        raise ScanError("Invalid image catalog")
    result: set[str] = set()
    for line in path.read_text("utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 6 or IDENTIFIER.fullmatch(fields[0]) is None:
            raise ScanError("Image catalog rows must have six fields")
        if fields[5] != "gpu":
            result.add(fields[0])
    if "app" not in result:
        raise ScanError("Image catalog lacks the app profile")
    return frozenset(result)


def policy_profiles(root: Path = ROOT) -> frozenset[str]:
    return catalog_profiles(root) | REFERENCE_PROFILES


def scanners_for(profile: str) -> str:
    if profile == "app":
        return "vuln,secret,misconfig"
    if profile in REFERENCE_PROFILES:
        return "vuln"
    return "vuln,secret"


# Trivy invocation ---------------------------------------------------------------------------


def docker_base(cache: Path, *, socket: bool) -> list[str]:
    argv = ["docker", "run", "--rm"]
    if socket:
        argv += ["-v", "/var/run/docker.sock:/var/run/docker.sock:ro"]
    return [*argv, "-v", f"{cache}:/root/.cache/trivy", TRIVY_IMAGE]


def trivy_argv(cache: Path, target: str, scanners: str) -> list[str]:
    return [
        *docker_base(cache, socket=True),
        "image",
        "--image-src",
        "docker",
        "--scanners",
        scanners,
        "--format",
        "json",
        "--exit-code",
        "0",
        "--skip-db-update",
        "--skip-java-db-update",
        "--quiet",
        target,
    ]


def download_argvs(cache: Path) -> list[list[str]]:
    return [
        [*docker_base(cache, socket=False), "image", "--download-db-only", "--quiet"],
        [*docker_base(cache, socket=False), "image", "--download-java-db-only", "--quiet"],
    ]


def version_argv(cache: Path) -> list[str]:
    return [*docker_base(cache, socket=False), "version", "--format", "json"]


def scanner_info(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ScanError("Invalid `trivy version` output")
    if raw.get("Version") != TRIVY_VERSION:
        raise ScanError(f"Scanner reports version {raw.get('Version')!r}, not {TRIVY_VERSION}")
    db = raw.get("VulnerabilityDB")
    java = raw.get("JavaDB")
    if not isinstance(db, dict) or not isinstance(java, dict):
        raise ScanError("Trivy DB or Java DB missing from the cache; run `download-db` first")
    return {
        "image": TRIVY_IMAGE,
        "version": TRIVY_VERSION,
        "db_updated_at": iso(parse_time(db.get("UpdatedAt"))),
        "java_db_updated_at": iso(parse_time(java.get("UpdatedAt"))),
    }


def db_is_stale(scanner: dict[str, Any], now: datetime) -> bool:
    return bool(now - parse_time(scanner["db_updated_at"]) > MAX_DB_AGE)


# Policy -------------------------------------------------------------------------------------


def policy_date(value: Any) -> date | None:
    if not isinstance(value, str) or ISO_DATE.fullmatch(value) is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def has_wildcard(value: str) -> bool:
    return any(character in WILDCARD for character in value)


def entry_problems(
    index: int, raw: Any, today: date, profiles: frozenset[str]
) -> tuple[list[str], Entry | None]:
    where = f"entries[{index}]"
    if not isinstance(raw, dict):
        return [f"{where}: must be an object"], None
    problems: list[str] = []
    keys = set(raw)
    if keys != ENTRY_KEYS:
        missing = sorted(ENTRY_KEYS - keys)
        unknown = sorted(keys - ENTRY_KEYS)
        problems.append(f"{where}: missing keys {missing}, unknown keys {unknown}")
        return problems, None
    for name in ("id", "kind", "package", "justification", "reviewer"):
        value = raw[name]
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{where}: {name} must be a non-empty string")
        elif name in {"id", "package"} and has_wildcard(value):
            problems.append(f"{where}: {name} must not contain wildcards")
    if problems:
        return problems, None
    kind = raw["kind"]
    if kind not in POLICY_KINDS:
        problems.append(f"{where}: kind must be one of {list(POLICY_KINDS)}")
    elif kind == "coverage" and raw["id"] not in COVERAGE_IDS:
        problems.append(f"{where}: coverage id must be one of {sorted(COVERAGE_IDS)}")
    elif kind != "coverage" and ADVISORY.fullmatch(raw["id"]) is None:
        problems.append(f"{where}: id {raw['id']!r} is not an exact advisory or check id")
    images = raw["images"]
    if not isinstance(images, list) or not images:
        problems.append(f"{where}: images must be a non-empty list")
        images = []
    for image in images:
        if not isinstance(image, str) or has_wildcard(image) or image not in profiles:
            problems.append(f"{where}: unknown image profile {image!r}")
    if len(set(map(str, images))) != len(images):
        problems.append(f"{where}: images lists a profile twice")
    reviewed = policy_date(raw["reviewed_at"])
    expires = policy_date(raw["expires_at"])
    if reviewed is None:
        problems.append(f"{where}: reviewed_at must be an ISO date (YYYY-MM-DD)")
    if expires is None:
        problems.append(f"{where}: expires_at must be an ISO date (YYYY-MM-DD)")
    if reviewed is not None and expires is not None:
        if reviewed > today:
            problems.append(f"{where}: reviewed_at {reviewed} is in the future")
        if expires < today:
            problems.append(f"{where}: expired on {expires}")
        if expires < reviewed:
            problems.append(f"{where}: expires_at precedes reviewed_at")
        if expires - reviewed > timedelta(days=MAX_POLICY_DAYS):
            problems.append(
                f"{where}: expires_at is more than {MAX_POLICY_DAYS} days after reviewed_at"
            )
    if problems or reviewed is None or expires is None:
        return problems, None
    entry = Entry(
        id=raw["id"],
        kind=kind,
        package=raw["package"],
        images=tuple(images),
        justification=raw["justification"],
        reviewer=raw["reviewer"],
        reviewed_at=reviewed,
        expires_at=expires,
    )
    return [], entry


def policy_problems(
    raw: Any, today: date, profiles: frozenset[str]
) -> tuple[list[str], tuple[Entry, ...]]:
    if not isinstance(raw, dict) or set(raw) != {"schema", "entries"}:
        return ["policy must be an object with exactly `schema` and `entries`"], ()
    if type(raw["schema"]) is not int or raw["schema"] != 1:
        return ["policy schema must be 1"], ()
    if not isinstance(raw["entries"], list):
        return ["policy entries must be a list"], ()
    problems: list[str] = []
    entries: list[Entry] = []
    seen: set[tuple[str, str, str]] = set()
    for index, item in enumerate(raw["entries"]):
        found, entry = entry_problems(index, item, today, profiles)
        problems += found
        if entry is None:
            continue
        for image in entry.images:
            triple = (entry.id, entry.package, image)
            if triple in seen:
                problems.append(f"entries[{index}]: duplicate entry for {triple}")
            seen.add(triple)
        entries.append(entry)
    return problems, tuple(entries)


def load_policy(path: Path, today: date, profiles: frozenset[str]) -> Policy:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
        raise ScanError(f"Policy must be a bounded ordinary file: {path}")
    data = path.read_bytes()
    try:
        raw = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ScanError(f"Policy is not valid JSON: {error}") from None
    problems, entries = policy_problems(raw, today, profiles)
    if problems:
        raise ScanError("Invalid policy:\n  " + "\n  ".join(problems))
    return Policy(entries=entries, sha256=sha256_bytes(data))


# Gate decision ------------------------------------------------------------------------------


def severity(value: Any) -> str:
    return value if isinstance(value, str) and value in SEVERITIES else "UNKNOWN"


def text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def item(
    finding_id: str,
    kind: str,
    package: str,
    installed: str,
    fixed: str,
    level: str,
    target: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "id": finding_id,
        "kind": kind,
        "package": package,
        "installed": installed,
        "fixed": fixed,
        "severity": level,
        "target": target,
        "reason": reason,
    }


def results(report: Any) -> list[dict[str, Any]]:
    if not isinstance(report, dict) or report.get("SchemaVersion") != 2:
        raise ScanError("Unsupported Trivy report (expected SchemaVersion 2)")
    raw = report.get("Results") or []
    if not isinstance(raw, list) or not all(isinstance(entry, dict) for entry in raw):
        raise ScanError("Trivy report Results must be a list of objects")
    return raw


def coverage_gaps(report: dict[str, Any], rows: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Fail closed when Trivy cannot map the OS or saw no packages (Pitfall 7)."""
    gaps: list[tuple[str, str]] = []
    metadata = report.get("Metadata")
    system = metadata.get("OS") if isinstance(metadata, dict) else None
    if not isinstance(system, dict) or not text(system.get("Family")):
        gaps.append(("os-not-detected", "unknown"))
    else:
        family = text(system.get("Family"))
        name = text(system.get("Name"))
        label = f"{family} {name}".strip()
        unmapped = family in {"debian", "ubuntu"} and re.match(r"[0-9]", name) is None
        no_os_result = not any(row.get("Class") == "os-pkgs" for row in rows)
        if unmapped or system.get("EOSL") is True or no_os_result:
            gaps.append(("unsupported-os", label))
    if not any(row.get("Packages") for row in rows):
        gaps.append(("no-packages", "none"))
    return gaps


def evaluate(
    report: Any,
    profile: str,
    policy: Policy,
    now: datetime,
    *,
    reference: bool = False,
    db_updated_at: str | None = None,
) -> dict[str, Any]:
    """Classify every finding of one image report as blocking, suppressed or reported."""
    rows = results(report)
    counts = dict.fromkeys(SEVERITIES, 0)
    blocking: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []
    reported: list[dict[str, Any]] = []
    used: set[Entry] = set()

    def accepted(kind: str, finding_id: str, package: str) -> Entry | None:
        for entry in policy.entries:
            if entry.covers(kind, finding_id, package, profile) and entry.expires_at >= now.date():
                used.add(entry)
                return entry
        return None

    def suppress(found: dict[str, Any], entry: Entry) -> None:
        found.update(
            reason="accepted", expires_at=entry.expires_at.isoformat(), reviewer=entry.reviewer
        )
        suppressed.append(found)

    if db_updated_at is not None and now - parse_time(db_updated_at) > MAX_DB_AGE:
        blocking.append(
            item("stale-db", "scanner", "trivy-db", db_updated_at, "", "", "", "stale-db")
        )

    for row in rows:
        target = text(row.get("Target"))
        for vulnerability in row.get("Vulnerabilities") or []:
            level = severity(vulnerability.get("Severity"))
            counts[level] += 1
            fixed = text(vulnerability.get("FixedVersion"))
            found = item(
                text(vulnerability.get("VulnerabilityID")),
                "vulnerability",
                text(vulnerability.get("PkgName")),
                text(vulnerability.get("InstalledVersion")),
                fixed,
                level,
                target,
                "",
            )
            if fixed:
                if reference and level not in SERIOUS:
                    reported.append({**found, "reason": "reference-fixable"})
                else:
                    blocking.append({**found, "reason": "fixable"})
            elif reference:
                reported.append({**found, "reason": "reference-unfixed"})
            elif level in SERIOUS:
                entry = accepted("vulnerability", found["id"], found["package"])
                if entry is None:
                    blocking.append({**found, "reason": "unaccepted"})
                else:
                    suppress(found, entry)
            else:
                reported.append({**found, "reason": "unfixed"})
        for secret in row.get("Secrets") or []:
            blocking.append(
                item(
                    text(secret.get("RuleID")),
                    "secret",
                    text(secret.get("Category")),
                    "",
                    "",
                    severity(secret.get("Severity")),
                    target,
                    "secret",
                )
            )
        for check in row.get("Misconfigurations") or []:
            if check.get("Status") != "FAIL":
                continue
            level = severity(check.get("Severity"))
            found = item(text(check.get("ID")), "misconfig", target, "", "", level, target, "")
            if level not in SERIOUS:
                reported.append({**found, "reason": "misconfig-low"})
                continue
            entry = accepted("misconfig", found["id"], target)
            if entry is None:
                blocking.append({**found, "reason": "misconfig"})
            else:
                suppress(found, entry)

    for gap, label in coverage_gaps(report, rows):
        found = item(gap, "coverage", label, "", "", "", "", "")
        entry = accepted("coverage", gap, label)
        if entry is None:
            blocking.append({**found, "reason": "coverage"})
        else:
            suppress(found, entry)

    return {
        "profile": profile,
        "counts": counts,
        "blocking": blocking,
        "suppressed": suppressed,
        "reported": reported,
        "used_entries": used,
    }


# Docker and snapshot inputs -----------------------------------------------------------------


def inspect_image(runner: Runner, ref: str) -> dict[str, Any]:
    """Read-only `docker image inspect`: image ID, architecture and revision label."""
    raw = json.loads(runner(["docker", "image", "inspect", ref]) or "null")
    if not isinstance(raw, list) or len(raw) != 1 or not isinstance(raw[0], dict):
        raise ScanError(f"Cannot inspect local image {ref}")
    image = raw[0]
    image_id = image.get("Id")
    if not isinstance(image_id, str) or IMAGE_ID.fullmatch(image_id) is None:
        raise ScanError(f"Local image {ref} has no sha256 image ID")
    config = image.get("Config")
    labels = config.get("Labels") if isinstance(config, dict) else None
    if not isinstance(labels, dict):
        labels = {}
    return {
        "id": image_id,
        "architecture": text(image.get("Architecture")),
        "revision": text(labels.get(REVISION_LABEL)),
    }


def load_tested(path: Path, profiles: frozenset[str]) -> dict[str, Any]:
    """Validate the `docker_release.py inspect` snapshot shape without registry context."""
    raw = read_json(path, 256 * 1024)
    if (
        not isinstance(raw, dict)
        or set(raw) != TESTED_KEYS
        or type(raw.get("schema_version")) is not int
        or raw["schema_version"] != 1
        or raw.get("kind") != "ds60-tested-images"
        or raw.get("architecture") not in ARCHITECTURES
    ):
        raise ScanError("Invalid pre-qualification image snapshot")
    context = raw["context"]
    if (
        not isinstance(context, dict)
        or set(context) != CONTEXT_KEYS
        or not all(isinstance(value, str) for value in context.values())
        or SHA.fullmatch(context["revision"]) is None
    ):
        raise ScanError("Invalid release context in image snapshot")
    images = raw["images"]
    if not isinstance(images, list) or not images:
        raise ScanError("Image snapshot is empty")
    seen: set[str] = set()
    for image in images:
        if not isinstance(image, dict) or set(image) != TESTED_IMAGE_KEYS:
            raise ScanError("Invalid tested image record")
        profile = image["profile"]
        if not isinstance(profile, str) or profile not in profiles or profile in seen:
            raise ScanError("Image snapshot has an unknown or duplicated profile")
        seen.add(profile)
        if not isinstance(image["tested_image_id"], str) or (
            IMAGE_ID.fullmatch(image["tested_image_id"]) is None
        ):
            raise ScanError("Tested image ID must be a sha256 image ID")
    return raw


@dataclass(frozen=True)
class Target:
    profile: str
    ref: str
    reference: bool = False


def scan_targets(
    runner: Runner,
    targets: Iterable[Target],
    *,
    policy: Policy,
    cache: Path,
    reports: Path,
    now: datetime,
    context: dict[str, Any] | None = None,
    architecture: str | None = None,
) -> dict[str, Any]:
    scanner = scanner_info(json.loads(runner(version_argv(cache)) or "null"))
    stale = db_is_stale(scanner, now)
    images: list[dict[str, Any]] = []
    used: set[Entry] = set()
    for target in targets:
        local = inspect_image(runner, target.ref)
        if target.ref.startswith("sha256:") and local["id"] != target.ref:
            raise ScanError(f"Image {target.ref} resolved to a different ID {local['id']}")
        if architecture is None:
            architecture = local["architecture"]
        elif local["architecture"] != architecture:
            raise ScanError(
                f"{target.profile} is {local['architecture']}, evidence is for {architecture}"
            )
        output = runner(trivy_argv(cache, local["id"], scanners_for(target.profile)))
        if len(output) > MAX_REPORT:
            raise ScanError(f"Trivy report for {target.profile} is too large")
        try:
            report = json.loads(output)
        except json.JSONDecodeError as error:
            raise ScanError(f"Trivy output for {target.profile} is not JSON: {error}") from None
        write_text(reports / f"{target.profile}.json", output)
        verdict = evaluate(
            report,
            target.profile,
            policy,
            now,
            reference=target.reference,
            db_updated_at=scanner["db_updated_at"] if stale else None,
        )
        used |= verdict.pop("used_entries")
        revision = local["revision"]
        if context is not None and revision and revision != context["revision"]:
            verdict["blocking"].append(
                item(
                    "revision-mismatch",
                    "revision",
                    REVISION_LABEL,
                    revision,
                    context["revision"],
                    "",
                    "",
                    "revision",
                )
            )
        images.append(
            {
                **verdict,
                "tested_image_id": local["id"],
                "revision_label": revision,
                "reference": target.reference,
                "scanners": scanners_for(target.profile),
                "report_sha256": sha256_bytes(output.encode("utf-8")),
            }
        )
    unused = [entry.key() for entry in policy.entries if entry not in used]
    return {
        "schema": 1,
        "kind": "ds60-scan-evidence",
        "context": context,
        "architecture": architecture,
        "scanner": scanner,
        "policy_sha256": policy.sha256,
        "scanned_at": iso(now),
        "passed": not any(image["blocking"] for image in images),
        "unused_policy_entries": unused,
        "images": images,
    }


def summary_line(image: dict[str, Any]) -> str:
    counts = " ".join(f"{name[0]}{image['counts'][name]}" for name in SEVERITIES)
    reasons: dict[str, int] = {}
    for found in image["blocking"]:
        reasons[found["reason"]] = reasons.get(found["reason"], 0) + 1
    detail = ", ".join(f"{reason} {count}" for reason, count in sorted(reasons.items()))
    state = "FAIL" if image["blocking"] else "pass"
    return (
        f"{state} {image['profile']} {image['tested_image_id'][:19]} [{counts}] "
        f"blocking {len(image['blocking'])}"
        + (f" ({detail})" if detail else "")
        + f", suppressed {len(image['suppressed'])}, reported {len(image['reported'])}"
    )


# Proposals ----------------------------------------------------------------------------------

PROPOSABLE = {"unaccepted": "vulnerability", "misconfig": "misconfig", "coverage": "coverage"}


def propose_entries(evidence: Any, today: date, days: int) -> tuple[list[dict[str, Any]], int]:
    """Draft `pending-owner` entries for acceptable blocking findings; never for fixable ones."""
    if not 1 <= days <= MAX_POLICY_DAYS:
        raise ScanError(f"--days must be between 1 and {MAX_POLICY_DAYS}")
    if not isinstance(evidence, dict) or evidence.get("kind") != "ds60-scan-evidence":
        raise ScanError("Not a DS60 scan evidence file")
    grouped: dict[tuple[str, str, str], list[str]] = {}
    refused = 0
    for image in evidence.get("images") or []:
        for found in image.get("blocking") or []:
            kind = PROPOSABLE.get(found.get("reason"))
            if kind is None:
                refused += 1
                continue
            profiles = grouped.setdefault((kind, found["id"], found["package"]), [])
            if image["profile"] not in profiles:
                profiles.append(image["profile"])
    entries = [
        {
            "id": finding_id,
            "kind": kind,
            "package": package,
            "images": profiles,
            "justification": "",
            "reviewer": "pending-owner",
            "reviewed_at": today.isoformat(),
            "expires_at": (today + timedelta(days=days)).isoformat(),
        }
        for (kind, finding_id, package), profiles in sorted(grouped.items())
    ]
    return entries, refused


# CLI ----------------------------------------------------------------------------------------


def parse_reference(value: str) -> Target:
    name, separator, ref = value.partition("=")
    if not separator or name not in REFERENCE_PROFILES or not ref:
        raise ScanError(f"--reference must be NAME=REF with NAME in {sorted(REFERENCE_PROFILES)}")
    return Target(profile=name, ref=ref, reference=True)


def command_scan(args: argparse.Namespace, runner: Runner, now: datetime) -> int:
    profiles = policy_profiles(ROOT)
    policy = load_policy(args.policy, now.date(), profiles)
    cache = resolve_cache(args.cache)
    targets: list[Target] = []
    context: dict[str, Any] | None = None
    architecture: str | None = None
    if args.tested is not None:
        if args.image is not None:
            raise ScanError("Use either --tested or --image, not both")
        snapshot = load_tested(args.tested, catalog_profiles(ROOT))
        context = snapshot["context"]
        architecture = snapshot["architecture"]
        targets += [
            Target(image["profile"], image["tested_image_id"]) for image in snapshot["images"]
        ]
    elif args.image is not None:
        if args.profile not in profiles - REFERENCE_PROFILES:
            raise ScanError(
                f"--profile must be a publishable catalog profile, not {args.profile!r}"
            )
        targets.append(Target(args.profile, args.image))
    targets += [parse_reference(value) for value in args.reference]
    if not targets:
        raise ScanError("Nothing to scan: give --image, --tested or --reference")
    if len({target.profile for target in targets}) != len(targets):
        raise ScanError("Each profile can be scanned once per evidence file")
    evidence = scan_targets(
        runner,
        targets,
        policy=policy,
        cache=cache,
        reports=args.reports,
        now=now,
        context=context,
        architecture=architecture,
    )
    write_json(args.output, evidence)
    if db_is_stale(evidence["scanner"], now):
        print(f"Trivy DB from {evidence['scanner']['db_updated_at']} is older than 24 hours")
    for image in evidence["images"]:
        print(summary_line(image))
    for entry in evidence["unused_policy_entries"]:
        print(f"warning: policy entry matched nothing: {entry['id']} {entry['package']}")
    print(f"evidence: {args.output}")
    return 0 if evidence["passed"] else 2


def command_download(args: argparse.Namespace, runner: Runner, now: datetime) -> int:
    cache = resolve_cache(args.cache)
    cache.mkdir(parents=True, exist_ok=True)
    for argv in download_argvs(cache):
        runner(argv)
    scanner = scanner_info(json.loads(runner(version_argv(cache)) or "null"))
    print(
        f"Trivy {scanner['version']} DB {scanner['db_updated_at']}, "
        f"Java DB {scanner['java_db_updated_at']} in {cache}"
    )
    return 0


def command_validate(args: argparse.Namespace, now: datetime) -> int:
    try:
        raw = json.loads(args.policy.read_text("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"policy unreadable: {error}", file=sys.stderr)
        return 2
    problems, entries = policy_problems(raw, now.date(), policy_profiles(ROOT))
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 2
    pending = sum(1 for entry in entries if entry.reviewer == "pending-owner")
    print(f"policy valid: {len(entries)} entries ({pending} pending-owner)")
    return 0


def command_propose(args: argparse.Namespace, now: datetime) -> int:
    entries, refused = propose_entries(
        read_json(args.evidence, 64 * 1024 * 1024), now.date(), args.days
    )
    print(json.dumps({"entries": entries}, indent=2))
    if refused:
        print(
            f"{refused} blocking findings (fixable, secret, stale DB or revision) "
            "cannot be accepted and must be fixed",
            file=sys.stderr,
        )
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="DS60 image vulnerability gate (Trivy via docker run)."
    )
    commands = root.add_subparsers(dest="command", required=True)

    scan = commands.add_parser("scan", help="scan local images and write gate evidence")
    scan.add_argument("--image", help="local image reference (single-image mode)")
    scan.add_argument("--profile", default="app", help="catalog profile for --image")
    scan.add_argument("--tested", type=Path, help="work/tested-images.json from docker_release")
    scan.add_argument("--reference", action="append", default=[], metavar="postgres=REF")
    scan.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    scan.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    scan.add_argument("--output", type=Path, default=Path("work/scan-evidence.json"))
    scan.add_argument("--reports", type=Path, default=Path("work/scan-reports"))

    download = commands.add_parser("download-db", help="download the Trivy DB and Java DB")
    download.add_argument("--cache", type=Path, default=DEFAULT_CACHE)

    validate = commands.add_parser("validate-policy", help="validate the DS60 CVE policy")
    validate.add_argument("--policy", type=Path, default=DEFAULT_POLICY)

    propose = commands.add_parser("propose-entries", help="draft pending-owner policy entries")
    propose.add_argument("--evidence", type=Path, required=True)
    propose.add_argument("--days", type=int, default=MAX_POLICY_DAYS)
    return root


def main(argv: list[str] | None = None, runner: Runner = default_runner) -> int:
    args = parser().parse_args(argv)
    now = utc_now()
    try:
        if args.command == "scan":
            return command_scan(args, runner, now)
        if args.command == "download-db":
            return command_download(args, runner, now)
        if args.command == "validate-policy":
            return command_validate(args, now)
        return command_propose(args, now)
    except ScanError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
