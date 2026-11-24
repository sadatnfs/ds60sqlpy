#!/usr/bin/env python3
"""Check the curated per-track qualification ledger against the coverage matrix.

`curriculum/track-qualification.json` records judgments (rubric statuses,
justifications, accepted lesson lists) and a runtime capability ledger for
every track. Every measured value is recomputed here from
`curriculum/coverage-matrix.json` and the runtime profile registry, so a record
cannot claim more than the matrix and the registry support. This script is
read-only: it never writes the ledger, the matrix or any course file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from ds60sqlpy.modules import ModuleCatalog  # noqa: E402
from ds60sqlpy.walkthroughs import load_walkthroughs  # noqa: E402
from scripts.check_module_references import (  # noqa: E402
    BROWSER_PROFILES,
    EXTERNAL_REASONS,
    GPU_PROFILES,
    ORDINARY_PROFILES,
)
from scripts.ci_profiles import groups  # noqa: E402

LEDGER = "curriculum/track-qualification.json"
MATRIX = "curriculum/coverage-matrix.json"
CRITERIA = tuple(f"R{number}" for number in range(1, 12))
MEASURED: dict[str, tuple[str, ...]] = {
    "R1": ("missing-path", "unknown-prerequisite"),
    "R2": ("missing-outcome", "weak-outcome"),
    "R3": ("few-terms",),
    "R4": ("few-examples",),
    "R5": ("thin-guide",),
    "R6": ("few-exercises",),
    "R7": ("missing-solution", "thin-solution"),
}
STATUSES = frozenset({"pass", "na", "accepted-gap", "gap", "not-assessed"})
MUST_PASS = frozenset({"R1", "R2", "R10"})
MIN_JUSTIFICATION = 40
CRITERION_KEYS = frozenset(
    {
        "status",
        "justification",
        "lessons",
        "reviewer",
        "date",
        "templated_baseline",
        "templated_baseline_source",
    }
)
RECORD_KEYS = frozenset(
    {"track", "family", "rows", "runtime", "walkthrough", "criteria", "reviewed"}
)
RUNTIME_KEYS = frozenset(
    {"profiles", "unavailable", "guide_examples", "walkthrough_outputs_checked"}
)
# `evidence` is present exactly when `walkthrough_outputs_checked` is true.
EVIDENCE_KEYS = frozenset({"ci_run", "commit", "groups"})
CI_RUN = re.compile(r"[0-9]{1,20}")
COMMIT = re.compile(r"[0-9a-f]{40}")
RESULT_LABELS = (
    "structure validated",
    "representative behavior executed",
    "complete artifact executed",
    "offline verified after setup",
    "not validated on this platform",
)
# The narrowest result label each route can honestly claim.
ROUTE_LABELS = {
    "course-check": "complete artifact executed",
    "reference-corpus": "complete artifact executed",
    "browser-workflow": "representative behavior executed",
    "kubernetes-workflow": "representative behavior executed",
    "hand-derived": "structure validated",
    "reading-only": "structure validated",
    "gpu-separate": "not validated on this platform",
}
WALKTHROUGH_ROUTES = frozenset({"live-python", "live-sql", "hand-derived", "authored", "na"})
NOT_EXECUTED = "are not executed in this phase"
GUIDE_PREFIX = {
    "core": (
        "Lesson and solution files are checked by the core course checks; guide code "
        "blocks are covered by content rendering checks and " + NOT_EXECUTED + "."
    ),
    "reference": (
        "Executable reference checked by the CI corpus; guide code blocks are covered "
        "by content rendering checks and " + NOT_EXECUTED + "."
    ),
    "none": (
        "No ordinary executable reference exists for this track; guide code blocks are "
        "covered by content rendering checks and " + NOT_EXECUTED + "."
    ),
}
DASHES = ("\u2014", "\u2013")
TRACK_NAME = re.compile(r"[a-z][a-z0-9-]{0,60}")


def load_matrix(root: Path = ROOT) -> dict[str, Any]:
    payload = json.loads((root / MATRIX).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("lessons"), list):
        raise ValueError("The coverage matrix has no lesson rows.")
    return payload


def load_ledger(root: Path = ROOT) -> dict[str, Any]:
    payload = json.loads((root / LEDGER).read_text(encoding="utf-8"))
    if (
        not isinstance(payload, dict)
        or set(payload) != {"schema_version", "rubric_version", "tracks"}
        or payload["schema_version"] != 1
        or payload["rubric_version"] != 1
        or not isinstance(payload["tracks"], list)
    ):
        raise ValueError(
            "The qualification ledger needs schema_version 1, rubric_version 1 and tracks."
        )
    return payload


def track_rows(matrix: dict[str, Any], track: str) -> list[dict[str, Any]]:
    return [row for row in matrix["lessons"] if row["track"] == track]


def measured_rows(matrix: dict[str, Any], track: str, codes: tuple[str, ...]) -> list[str]:
    wanted = set(codes)
    return sorted(row["id"] for row in track_rows(matrix, track) if wanted & set(row["gaps"]))


def expected_route(family: str, profile: str) -> str:
    if family == "core":
        return "course-check"
    if profile in ORDINARY_PROFILES:
        return "reference-corpus"
    if profile in BROWSER_PROFILES:
        return "browser-workflow"
    if profile == "k8s-kind":
        return "kubernetes-workflow"
    if profile == "dax-offline":
        return "hand-derived"
    if profile == "reading":
        return "reading-only"
    if profile in GPU_PROFILES:
        return "gpu-separate"
    raise ValueError(f"Runtime profile {profile} has no registered route.")


def ci_group_by_profile(root: Path = ROOT) -> dict[str, str]:
    return {profile: row["id"] for row in groups(root) for profile in row["profiles"]}


def ordinary_stages(matrix: dict[str, Any], track: str) -> set[str]:
    return {
        row["stage"] for row in track_rows(matrix, track) if row["runtime"] in ORDINARY_PROFILES
    }


def expected_walkthrough_route(matrix: dict[str, Any], track: str) -> str:
    rows = track_rows(matrix, track)
    if rows and rows[0]["family"] == "core":
        return "live-sql" if track == "sql" else "live-python"
    if any(row["runtime"] == "dax-offline" for row in rows):
        return "hand-derived"
    return "authored" if ordinary_stages(matrix, track) else "na"


def guide_prefix(matrix: dict[str, Any], track: str) -> str:
    rows = track_rows(matrix, track)
    if rows and rows[0]["family"] == "core":
        return GUIDE_PREFIX["core"]
    return GUIDE_PREFIX["reference" if ordinary_stages(matrix, track) else "none"]


@lru_cache(maxsize=4)
def _catalog(root: str) -> ModuleCatalog:
    return ModuleCatalog(Path(root))


def validated_walkthroughs(root: Path, track: str) -> tuple[set[str], str | None]:
    """Lesson IDs with a walkthrough that passes `ds60sqlpy.walkthroughs`, plus any error.

    An invalid walkthrough file counts as zero coverage, so R9 cannot pass on it.
    """
    if TRACK_NAME.fullmatch(track) is None:
        return set(), f"{track}: not a valid track name."
    if not (root / "courses" / track / "walkthroughs.json").is_file():
        return set(), None
    try:
        return set(load_walkthroughs(root, _catalog(str(root.resolve())), track)), None
    except (OSError, ValueError) as error:
        return set(), str(error)


def walkthrough_stages(root: Path, matrix: dict[str, Any], track: str) -> set[str]:
    """Stages covered by validated walkthroughs in `courses/<track>/walkthroughs.json`."""
    lesson_ids, _error = validated_walkthroughs(root, track)
    stages = {row["id"]: row["stage"] for row in track_rows(matrix, track)}
    return {stages[lesson_id] for lesson_id in lesson_ids if lesson_id in stages}


def required_ci_groups(record: dict[str, Any]) -> list[str]:
    """CI groups whose qualify jobs must pass before walkthrough outputs count as checked."""
    profiles = record.get("runtime", {}).get("profiles", {})
    if not isinstance(profiles, dict):
        return []
    return sorted(
        {
            entry["ci_group"]
            for entry in profiles.values()
            if isinstance(entry, dict) and isinstance(entry.get("ci_group"), str)
        }
    )


def evidence_errors(record: dict[str, Any], root: Path = ROOT) -> list[str]:
    """`walkthrough_outputs_checked` true needs a cited CI run covering every ordinary group."""
    track = record.get("track")
    runtime = record["runtime"]
    checked = runtime.get("walkthrough_outputs_checked")
    evidence = runtime.get("evidence")
    if checked is not True:
        if "evidence" in runtime:
            return [f"{track} runtime: evidence is recorded only with walkthrough_outputs_checked."]
        return []
    required = required_ci_groups(record)
    if not required:
        return [f"{track} runtime: no ordinary CI group exists, so outputs cannot be CI checked."]
    if not isinstance(evidence, dict) or set(evidence) != EVIDENCE_KEYS:
        return [
            f"{track} runtime: walkthrough_outputs_checked needs evidence {sorted(EVIDENCE_KEYS)}."
        ]
    errors: list[str] = []
    run, commit, listed = evidence["ci_run"], evidence["commit"], evidence["groups"]
    if not isinstance(run, str) or CI_RUN.fullmatch(run) is None:
        errors.append(f"{track} runtime: evidence ci_run must be a string of digits.")
    if not isinstance(commit, str) or COMMIT.fullmatch(commit) is None:
        errors.append(f"{track} runtime: evidence commit must be 40 lowercase hex characters.")
    if (
        not isinstance(listed, list)
        or not all(isinstance(group, str) for group in listed)
        or listed != sorted(set(listed))
    ):
        errors.append(f"{track} runtime: evidence groups must be a sorted list of unique names.")
        return errors
    known = {row["id"] for row in groups(root)}
    if set(listed) - known:
        errors.append(
            f"{track} runtime: evidence names unknown groups {sorted(set(listed) - known)}."
        )
    missing = sorted(set(required) - set(listed))
    if missing:
        errors.append(f"{track} runtime: evidence lacks the ordinary CI groups {missing}.")
    return errors


def templated_total(matrix: dict[str, Any], track: str) -> int | None:
    rows = track_rows(matrix, track)
    if not rows or any("templated_words" not in row.get("metrics", {}) for row in rows):
        return None
    return sum(int(row["metrics"]["templated_words"]) for row in rows)


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for key, item in value.items() for text in _strings(key) + _strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    return []


def runtime_errors(matrix: dict[str, Any], record: dict[str, Any], root: Path = ROOT) -> list[str]:
    track = record.get("track")
    rows = track_rows(matrix, str(track))
    runtime = record.get("runtime")
    if not rows or not isinstance(runtime, dict) or set(runtime) - {"evidence"} != RUNTIME_KEYS:
        return [f"{track} runtime: needs exactly {sorted(RUNTIME_KEYS)} and optional evidence."]
    errors: list[str] = []
    family = rows[0]["family"]
    profiles = runtime["profiles"]
    used = {row["runtime"] for row in rows}
    if not isinstance(profiles, dict) or set(profiles) != used:
        return [f"{track} runtime: profiles must equal the matrix runtimes {sorted(used)}."]
    group_of = ci_group_by_profile(root)
    for profile in sorted(used):
        entry = profiles[profile]
        route = expected_route(family, profile)
        wanted: dict[str, Any] = {"route": route, "label": ROUTE_LABELS[route]}
        if route == "reference-corpus":
            wanted["ci_group"] = group_of[profile]
        if entry != wanted:
            errors.append(f"{track} runtime {profile}: expected {wanted}.")
        elif entry["label"] not in RESULT_LABELS:
            errors.append(f"{track} runtime {profile}: unknown result label.")
    unavailable = [
        {"profile": profile, "reason": EXTERNAL_REASONS[profile]}
        for profile in sorted(used)
        if family != "core" and profile not in ORDINARY_PROFILES
    ]
    if runtime["unavailable"] != unavailable:
        errors.append(
            f"{track} runtime: unavailable must name "
            f"{[x['profile'] for x in unavailable]} with their registered reasons."
        )
    if any(not item["reason"].strip() for item in unavailable):
        errors.append(f"{track} runtime: an unavailable profile has an empty registered reason.")
    guide = runtime["guide_examples"]
    if not isinstance(guide, str) or not guide.startswith(guide_prefix(matrix, str(track))):
        errors.append(f"{track} runtime: guide_examples must start with the registered statement.")
    if not isinstance(runtime["walkthrough_outputs_checked"], bool):
        errors.append(f"{track} runtime: walkthrough_outputs_checked must be true or false.")
    else:
        errors += evidence_errors(record, root)
    return errors


def _walkthrough_errors(matrix: dict[str, Any], record: dict[str, Any], root: Path) -> list[str]:
    track = str(record.get("track"))
    block = record.get("walkthrough")
    route = expected_walkthrough_route(matrix, track)
    wanted: dict[str, Any] = {"route": route}
    if route == "authored":
        wanted["floor"] = len(ordinary_stages(matrix, track))
    if block != wanted:
        return [f"{track} walkthrough: expected {wanted}."]
    status = record["criteria"].get("R9", {}).get("status")
    if route == "na" and status != "na":
        return [f"{track} R9: a track with no ordinary runnable lessons records na."]
    if route in {"live-python", "live-sql", "hand-derived"} and status != "pass":
        return [f"{track} R9: the {route} adapter already exists, so record pass."]
    if route == "authored":
        if status not in {"pass", "gap"}:
            return [f"{track} R9: an authored track records pass or gap."]
        _ids, invalid = validated_walkthroughs(root, track)
        if status == "pass" and invalid:
            return [f"{track} R9: pass needs a valid walkthrough file: {invalid}"]
        missing = ordinary_stages(matrix, track) - walkthrough_stages(root, matrix, track)
        if status == "pass" and missing:
            return [f"{track} R9: pass needs walkthroughs for stages {sorted(missing)}."]
    return []


def _criterion_errors(
    matrix: dict[str, Any], record: dict[str, Any], criterion: str, entry: Any
) -> list[str]:
    track = str(record.get("track"))
    where = f"{track} {criterion}"
    if not isinstance(entry, dict) or "status" not in entry or not set(entry) <= CRITERION_KEYS:
        return [f"{where}: needs a status and only known fields."]
    status = entry["status"]
    if status not in STATUSES:
        return [f"{where}: unknown status {status!r}."]
    errors: list[str] = []
    justification = entry.get("justification")
    if status != "pass" and (
        not isinstance(justification, str) or len(justification.strip()) < MIN_JUSTIFICATION
    ):
        errors.append(
            f"{where}: {status} needs a justification of at least {MIN_JUSTIFICATION} characters."
        )
    if status == "not-assessed" and criterion != "R11":
        errors.append(f"{where}: not-assessed is allowed only on R11.")
    if "lessons" in entry and status != "accepted-gap":
        errors.append(f"{where}: only accepted-gap lists lessons; the matrix is the open queue.")
    rows = track_rows(matrix, track)
    if criterion in MEASURED:
        measured = measured_rows(matrix, track, MEASURED[criterion])
        if status == "pass" and measured:
            errors.append(
                f"{where}: pass but the matrix measures {len(measured)} rows, first {measured[0]}."
            )
        if status == "accepted-gap" and entry.get("lessons") != measured:
            errors.append(f"{where}: accepted lessons must equal the measured rows {measured[:5]}.")
        if status == "na":
            if measured:
                errors.append(
                    f"{where}: na cannot hide {len(measured)} measured rows, first {measured[0]}."
                )
            practice = any(row["learning_mode"] == "practice" for row in rows)
            reading = all(row["runtime"] == "reading" for row in rows)
            if not (
                (criterion in {"R6", "R7"} and not practice) or (criterion == "R4" and reading)
            ):
                errors.append(f"{where}: na is not allowed for this criterion on this track.")
    else:
        if status == "accepted-gap":
            errors.append(f"{where}: accepted-gap applies only to measured criteria R1 to R7.")
        if status == "na" and criterion != "R9":
            errors.append(f"{where}: na is allowed only on R4, R6, R7 and R9.")
    if criterion != "R8" and {"templated_baseline", "templated_baseline_source"} & set(entry):
        errors.append(f"{where}: only R8 records a templated baseline.")
    if criterion == "R8" and status == "pass":
        total = templated_total(matrix, track)
        baseline = entry.get("templated_baseline")
        source = entry.get("templated_baseline_source")
        if total is None:
            errors.append(
                f"{where}: pass needs the templated_words metric, which the matrix lacks."
            )
        elif isinstance(baseline, bool) or not isinstance(baseline, int) or baseline < 0:
            errors.append(f"{where}: pass needs an integer templated_baseline.")
        elif total > baseline:
            errors.append(f"{where}: templated_words {total} exceeds the recorded baseline.")
        if not isinstance(source, str) or COMMIT.search(source) is None:
            errors.append(f"{where}: pass needs a templated_baseline_source citing a commit.")
    if criterion == "R11" and status == "pass":
        reviewer, when = entry.get("reviewer"), entry.get("date")
        if not isinstance(reviewer, str) or not reviewer.strip() or not _is_date(when):
            errors.append(f"{where}: pass needs a named reviewer and an ISO date.")
    return errors


def _is_date(value: Any) -> bool:
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return True


def evaluate_track(matrix: dict[str, Any], record: dict[str, Any], root: Path = ROOT) -> list[str]:
    """Return every inconsistency between one record and the measured sources."""
    track = record.get("track") if isinstance(record, dict) else None
    if not isinstance(record, dict) or set(record) != RECORD_KEYS:
        return [f"{track}: record needs exactly {sorted(RECORD_KEYS)}."]
    rows = track_rows(matrix, str(track))
    if not rows:
        return [f"{track}: not a track in the coverage matrix."]
    errors: list[str] = []
    if record["family"] != rows[0]["family"]:
        errors.append(f"{track}: family must be {rows[0]['family']}.")
    if record["rows"] != len(rows):
        errors.append(f"{track}: rows must be {len(rows)}.")
    if not _is_date(record["reviewed"]):
        errors.append(f"{track}: reviewed must be an ISO date.")
    if any(dash in text for text in _strings(record) for dash in DASHES):
        errors.append(f"{track}: em and en dashes are not allowed.")
    criteria = record["criteria"]
    if not isinstance(criteria, dict) or set(criteria) != set(CRITERIA):
        return [*errors, f"{track}: criteria must be exactly R1 to R11."]
    for criterion in CRITERIA:
        errors += _criterion_errors(matrix, record, criterion, criteria[criterion])
    ledger = runtime_errors(matrix, record, root)
    errors += ledger
    if ledger and criteria["R10"].get("status") == "pass":
        errors.append(f"{track} R10: pass requires a complete and consistent runtime ledger.")
    elif (
        not ledger
        and criteria["R10"].get("status") == "pass"
        and required_ci_groups(record)
        and record["runtime"]["walkthrough_outputs_checked"] is not True
    ):
        errors.append(
            f"{track} R10: pass requires recorded CI evidence for groups "
            f"{required_ci_groups(record)}."
        )
    errors += _walkthrough_errors(matrix, record, root)
    return errors


def meets_threshold(matrix: dict[str, Any], record: dict[str, Any]) -> list[str]:
    """Reasons a consistent record is still below the track acceptance threshold."""
    track = str(record["track"])
    total = len(track_rows(matrix, track))
    reasons: list[str] = []
    for criterion in CRITERIA:
        entry = record["criteria"][criterion]
        status = entry["status"]
        if criterion in MUST_PASS and status != "pass":
            reasons.append(f"{track} {criterion}: must be pass, found {status}.")
        elif status == "gap":
            reasons.append(f"{track} {criterion}: open gap.")
        elif status == "not-assessed" and criterion != "R11":
            reasons.append(f"{track} {criterion}: not-assessed is allowed only on R11.")
        elif status == "accepted-gap" and len(entry.get("lessons", [])) * 10 > total:
            reasons.append(
                f"{track} {criterion}: {len(entry.get('lessons', []))} accepted lessons exceed "
                f"10 percent of {total}."
            )
    return reasons


def evidence_pending(matrix: dict[str, Any], record: dict[str, Any]) -> bool:
    """True when the only reason below threshold is R10 awaiting recorded CI evidence."""
    track = str(record["track"])
    return (
        bool(required_ci_groups(record))
        and record["runtime"]["walkthrough_outputs_checked"] is False
        and record["criteria"]["R10"]["status"] == "gap"
        and meets_threshold(matrix, record) == [f"{track} R10: must be pass, found gap."]
    )


def report(matrix: dict[str, Any], record: dict[str, Any], root: Path = ROOT) -> str:
    track = str(record["track"])
    lines = [
        f"{track} ({record['family']}, {record['rows']} lessons, reviewed {record['reviewed']})"
    ]
    for criterion in CRITERIA:
        status = record["criteria"][criterion]["status"]
        if criterion in MEASURED:
            count = len(measured_rows(matrix, track, MEASURED[criterion]))
            detail = f"measured rows {count} ({', '.join(MEASURED[criterion])})"
        elif criterion == "R8":
            total = templated_total(matrix, track)
            detail = (
                "templated_words absent from matrix"
                if total is None
                else f"templated_words {total}"
            )
        elif criterion == "R9":
            covered = sorted(walkthrough_stages(root, matrix, track))
            detail = f"route {record['walkthrough']['route']}, validated stages covered {covered}"
        else:
            detail = ""
        lines.append(f"  {criterion:<4} {status:<13} {detail}".rstrip())
    lines.append("  runtime:")
    for profile, entry in sorted(record["runtime"]["profiles"].items()):
        group = f", CI group {entry['ci_group']}" if "ci_group" in entry else ""
        lines.append(f"    {profile}: {entry['route']}, {entry['label']}{group}")
    for item in record["runtime"]["unavailable"]:
        lines.append(f"    unavailable {item['profile']}: {item['reason']}")
    lines.append(f"    guide examples: {record['runtime']['guide_examples']}")
    evidence = record["runtime"].get("evidence")
    if evidence:
        lines.append(
            f"    CI evidence: run {evidence['ci_run']}, commit {evidence['commit']}, "
            f"groups {evidence['groups']}"
        )
    elif required_ci_groups(record):
        lines.append(f"    CI evidence: pending for groups {required_ci_groups(record)}")
    errors = evaluate_track(matrix, record, root)
    below = meets_threshold(matrix, record)
    lines.append(f"  consistency: {'ok' if not errors else f'{len(errors)} errors'}")
    lines += [f"    {error}" for error in errors]
    lines.append(f"  threshold: {'met' if not below else f'below ({len(below)} reasons)'}")
    lines += [f"    {reason}" for reason in below]
    return "\n".join(lines)


def check(root: Path = ROOT) -> list[str]:
    matrix = load_matrix(root)
    records = load_ledger(root)["tracks"]
    errors: list[str] = []
    seen = [record.get("track") for record in records if isinstance(record, dict)]
    expected = {row["track"] for row in matrix["lessons"]}
    if len(seen) != len(records) or len(set(seen)) != len(seen) or set(seen) != expected:
        errors.append("Ledger must hold exactly one record per coverage matrix track.")
    for record in records:
        errors += evaluate_track(matrix, record, root)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--track", help="Print the recomputed rubric and runtime ledger for one track."
    )
    mode.add_argument(
        "--check", action="store_true", help="Validate every record; exit 1 on errors."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.check:
        errors = check(args.root)
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        if not errors:
            matrix = load_matrix(args.root)
            records = load_ledger(args.root)["tracks"]
            met = [r["track"] for r in records if not meets_threshold(matrix, r)]
            pending = [r["track"] for r in records if evidence_pending(matrix, r)]
            print(f"OK {len(records)} track records are consistent.")
            print(f"Threshold met by {len(met)} of {len(records)} tracks.")
            if pending:
                print(
                    f"Awaiting CI runtime evidence (R10) for {len(pending)} tracks: "
                    + ", ".join(pending)
                )
        return 1 if errors else 0
    matrix = load_matrix(args.root)
    found = [r for r in load_ledger(args.root)["tracks"] if r.get("track") == args.track]
    if len(found) != 1:
        print(f"FAIL no single record for track {args.track}", file=sys.stderr)
        return 1
    print(report(matrix, found[0], args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
