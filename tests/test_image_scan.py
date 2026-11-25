"""DS60 image scan gate: policy, decision rules and evidence, offline with trimmed Trivy JSON."""

from __future__ import annotations

import copy
import json
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from scripts import image_scan as scan

FIXTURES = Path(__file__).parent / "fixtures/trivy"
PROFILES = scan.policy_profiles()
VERSION = json.loads((FIXTURES / "version.json").read_text("utf-8"))
DB_TIME = scan.parse_time(VERSION["VulnerabilityDB"]["UpdatedAt"])
NOW = DB_TIME + timedelta(hours=1)
TODAY = NOW.date()
LAB_ID = "sha256:" + "a" * 64
WORKER_ID = "sha256:" + "b" * 64
PG_ID = "sha256:" + "c" * 64
REVISION = "1" * 40
OUTSIDE_CACHE = Path("/tmp/ds60-image-scan-test-cache")

# CLI tests that read the committed policy run on the day of its newest review, so adding an
# entry reviewed after the fixture DB date cannot make it look future-dated; the fake Trivy DB
# times move by the same whole days to stay fresh.
_COMMITTED = json.loads((scan.ROOT / "docker/cve-policy.json").read_text("utf-8"))
_NEWEST_REVIEW = max(
    (date.fromisoformat(item["reviewed_at"]) for item in _COMMITTED["entries"]), default=TODAY
)
POLICY_SHIFT = timedelta(days=max(0, (_NEWEST_REVIEW - TODAY).days))
POLICY_NOW = NOW + POLICY_SHIFT
POLICY_VERSION = copy.deepcopy(VERSION)
for _db in ("VulnerabilityDB", "JavaDB"):
    _updated = scan.parse_time(VERSION[_db]["UpdatedAt"]) + POLICY_SHIFT
    POLICY_VERSION[_db]["UpdatedAt"] = scan.iso(_updated)


def fixture(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((FIXTURES / f"{name}.json").read_text("utf-8"))
    return data


def entry(**overrides: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "id": "CVE-2025-7458",
        "kind": "vulnerability",
        "package": "libsqlite3-0",
        "images": ["app"],
        "justification": "No Debian 12 fix; base moves to trixie in 08-03.",
        "reviewer": "pending-owner",
        "reviewed_at": TODAY.isoformat(),
        "expires_at": (TODAY + timedelta(days=90)).isoformat(),
    }
    value.update(overrides)
    return value


def policy(*entries: dict[str, Any]) -> scan.Policy:
    problems, loaded = scan.policy_problems(
        {"schema": 1, "entries": list(entries)}, TODAY, PROFILES
    )
    assert problems == []
    return scan.Policy(entries=loaded, sha256="0" * 64)


EMPTY = policy()


def evaluate(name: str, profile: str = "app", rules: scan.Policy = EMPTY, **kw: Any) -> Any:
    return scan.evaluate(fixture(name), profile, rules, NOW, **kw)


def reasons(found: list[dict[str, Any]]) -> list[tuple[str, str, str]]:
    return [(item["id"], item["package"], item["reason"]) for item in found]


class FakeDocker:
    """Answers the read-only Docker and Trivy commands the scanner issues."""

    def __init__(
        self,
        reports: dict[str, str],
        *,
        labels: dict[str, str] | None = None,
        architecture: str = "arm64",
        version: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
    ) -> None:
        self.reports = reports
        self.labels = labels or {}
        self.architecture = architecture
        self.version = version or VERSION
        self.tags = tags or {}
        self.calls: list[list[str]] = []

    def __call__(self, argv: list[str]) -> str:
        self.calls.append(argv)
        if argv[:3] == ["docker", "image", "inspect"]:
            image_id = self.tags.get(argv[3], argv[3])
            config = {"Labels": {scan.REVISION_LABEL: self.labels.get(image_id, "")}}
            body = {"Id": image_id, "Architecture": self.architecture, "Config": config}
            return json.dumps([body])
        if argv[-3:] == ["version", "--format", "json"]:
            return json.dumps(self.version)
        if "--download-db-only" in argv or "--download-java-db-only" in argv:
            return ""
        assert argv[:3] == ["docker", "run", "--rm"]
        return json.dumps(fixture(self.reports[argv[-1]]))


def run_scan(
    runner: Callable[[list[str]], str],
    targets: list[scan.Target],
    tmp_path: Path,
    rules: scan.Policy = EMPTY,
    now: datetime = NOW,
    **kw: Any,
) -> dict[str, Any]:
    return scan.scan_targets(
        runner,
        targets,
        policy=rules,
        cache=OUTSIDE_CACHE,
        reports=tmp_path / "reports",
        now=now,
        **kw,
    )


# Task 1: tracer -----------------------------------------------------------------------------


def test_trivy_argv_runs_pinned_container_read_only() -> None:
    argv = scan.trivy_argv(Path("/cache/trivy"), LAB_ID, "vuln,secret,misconfig")
    assert argv[:3] == ["docker", "run", "--rm"]
    assert "/var/run/docker.sock:/var/run/docker.sock:ro" in argv
    assert "/cache/trivy:/root/.cache/trivy" in argv
    assert scan.TRIVY_IMAGE in argv
    assert scan.TRIVY_IMAGE.endswith(
        "@sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb"
    )
    tail = " ".join(argv[argv.index(scan.TRIVY_IMAGE) + 1 :])
    for flag in (
        "--exit-code 0",
        "--format json",
        "--skip-db-update",
        "--skip-java-db-update",
        "--scanners vuln,secret,misconfig",
    ):
        assert flag in tail
    assert "--ignorefile" not in tail
    assert argv[-1] == LAB_ID


def test_download_argvs_fetch_both_databases_without_socket() -> None:
    first, second = scan.download_argvs(Path("/cache/trivy"))
    assert "--download-db-only" in first
    assert "--download-java-db-only" in second
    assert not any("docker.sock" in part for part in first + second)


def test_scanner_has_no_github_action_reference() -> None:
    source = (scan.ROOT / "scripts/image_scan.py").read_text("utf-8")
    assert "trivy-action" not in source
    assert "setup-trivy" not in source


def test_cache_inside_repository_is_refused(tmp_path: Path) -> None:
    with pytest.raises(scan.ScanError, match="outside the repository"):
        scan.resolve_cache(scan.ROOT / "work/trivy")
    assert scan.resolve_cache(OUTSIDE_CACHE, root=tmp_path / "repo") == OUTSIDE_CACHE.resolve()


def test_scanners_per_profile() -> None:
    assert scan.scanners_for("app") == "vuln,secret,misconfig"
    assert scan.scanners_for("cpp20") == "vuln,secret"
    assert scan.scanners_for("postgres") == "vuln,secret"
    assert scan.scanners_for("postgres", reference=True) == "vuln"


def test_database_is_a_built_in_published_profile(tmp_path: Path) -> None:
    assert scan.DATABASE_PROFILE in scan.catalog_profiles(scan.ROOT)
    (tmp_path / "docker").mkdir()
    (tmp_path / "docker/classroom-images.tsv").write_text(
        "app lab ds60sqlpy-lab lab DS60_LAB_IMAGE app\n"
        "postgres db ds60sqlpy-postgres postgres DS60_POSTGRES_IMAGE ordinary\n"
    )
    with pytest.raises(scan.ScanError, match="built in"):
        scan.catalog_profiles(tmp_path)


def test_clean_report_has_no_blocking() -> None:
    result = evaluate("clean")
    assert result["blocking"] == []
    assert result["counts"] == dict.fromkeys(scan.SEVERITIES, 0)


def test_fixable_low_finding_blocks() -> None:
    result = evaluate("fixable")
    assert reasons(result["blocking"]) == [("CVE-2026-112907", "filelock", "fixable")]
    assert result["blocking"][0]["severity"] == "LOW"
    assert result["blocking"][0]["fixed"] == "4.2.1"
    assert result["counts"]["LOW"] == 1


def test_tracer_scan_writes_bound_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    runner = FakeDocker(
        {LAB_ID: "fixable"}, tags={"ds60sqlpy-lab:1.4.3": LAB_ID}, version=POLICY_VERSION
    )
    monkeypatch.setattr(scan, "utc_now", lambda: POLICY_NOW)
    output = tmp_path / "evidence.json"
    code = scan.main(
        [
            "scan",
            "--image",
            "ds60sqlpy-lab:1.4.3",
            "--profile",
            "app",
            "--cache",
            str(OUTSIDE_CACHE),
            "--output",
            str(output),
            "--reports",
            str(tmp_path / "reports"),
        ],
        runner,
    )
    assert code == 2
    evidence = json.loads(output.read_text("utf-8"))
    assert evidence["schema"] == 1
    assert evidence["kind"] == "ds60-scan-evidence"
    assert evidence["context"] is None
    assert evidence["architecture"] == "arm64"
    assert evidence["passed"] is False
    assert evidence["scanner"] == {
        "image": scan.TRIVY_IMAGE,
        "version": "0.76.2",
        "db_updated_at": scan.iso(DB_TIME + POLICY_SHIFT),
        "java_db_updated_at": scan.iso(
            POLICY_SHIFT + scan.parse_time(VERSION["JavaDB"]["UpdatedAt"])
        ),
    }
    policy_bytes = (scan.ROOT / "docker/cve-policy.json").read_bytes()
    assert evidence["policy_sha256"] == scan.sha256_bytes(policy_bytes)
    (image,) = evidence["images"]
    assert image["tested_image_id"] == LAB_ID
    assert image["profile"] == "app"
    raw = (tmp_path / "reports/app.json").read_bytes()
    assert image["report_sha256"] == scan.sha256_bytes(raw)
    assert reasons(image["blocking"]) == [("CVE-2026-112907", "filelock", "fixable")]
    scanned = [call for call in runner.calls if "--scanners" in call]
    assert scanned[0][-1] == LAB_ID
    assert "FAIL app" in capsys.readouterr().out


def test_clean_scan_exits_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = FakeDocker({LAB_ID: "clean"}, tags={"lab:clean": LAB_ID}, version=POLICY_VERSION)
    monkeypatch.setattr(scan, "utc_now", lambda: POLICY_NOW)
    args = ["scan", "--image", "lab:clean", "--cache", str(OUTSIDE_CACHE)]
    args += ["--output", str(tmp_path / "e.json"), "--reports", str(tmp_path / "r")]
    assert scan.main(args, runner) == 0


# Task 2: policy -----------------------------------------------------------------------------


def test_policy_starter_file_is_valid(capsys: pytest.CaptureFixture[str]) -> None:
    raw = json.loads((scan.ROOT / "docker/cve-policy.json").read_text("utf-8"))
    assert raw["schema"] == 1 and isinstance(raw["entries"], list)
    assert all(e["kind"] in scan.POLICY_KINDS and e["justification"] for e in raw["entries"])
    # D-06: configuration findings are accepted only as Trivy DS rules on named files.
    misconfig = [e for e in raw["entries"] if e["kind"] == "misconfig"]
    assert all(e["id"].startswith("DS-") and "/" in e["package"] for e in misconfig)
    assert scan.main(["validate-policy"]) == 0
    assert "policy valid" in capsys.readouterr().out


def test_policy_accepts_pending_owner_entry() -> None:
    problems, loaded = scan.policy_problems({"schema": 1, "entries": [entry()]}, TODAY, PROFILES)
    assert problems == []
    assert loaded[0].reviewer == "pending-owner"


def test_policy_accepts_reference_and_coverage_entries() -> None:
    entries = [
        entry(images=["postgres"]),
        entry(
            id="unsupported-os",
            kind="coverage",
            package="debian forky/sid",
            images=["r-statistics"],
        ),
        entry(id="DS-0002", kind="misconfig", package="opt/course/Dockerfile"),
        entry(id="DLA-4000-1", package="curl"),
        entry(id="TEMP-0841856-B18BAF", package="libc6"),
        entry(id="GHSA-3cv2-h65g-fgmm", package="astral-tokio-tar"),
    ]
    problems, _ = scan.policy_problems({"schema": 1, "entries": entries}, TODAY, PROFILES)
    assert problems == []


EXPIRED_REVIEW = (TODAY - timedelta(days=60)).isoformat()

BAD_ENTRIES: list[tuple[str, dict[str, Any], str]] = [
    ("unknown-key", {**entry(), "owner": "x"}, "unknown keys"),
    ("missing-key", {k: v for k, v in entry().items() if k != "reviewer"}, "missing keys"),
    ("wildcard-id", entry(id="CVE-2025-*"), "wildcards"),
    ("wildcard-package", entry(package="lib*"), "wildcards"),
    ("wildcard-image", entry(images=["*"]), "unknown image profile"),
    ("empty-id", entry(id=""), "non-empty"),
    ("bad-id", entry(id="cve 2025"), "exact advisory"),
    ("empty-justification", entry(justification=" "), "justification"),
    ("empty-reviewer", entry(reviewer=""), "reviewer"),
    ("unknown-kind", entry(kind="accepted_risk"), "kind"),
    ("bad-coverage-id", entry(kind="coverage", id="CVE-2025-7458"), "coverage id"),
    ("unknown-profile", entry(images=["cuda-cpp"]), "unknown image profile"),
    ("empty-images", entry(images=[]), "non-empty list"),
    ("duplicate-image", entry(images=["app", "app"]), "twice"),
    ("bad-date", entry(expires_at="2026/12/01"), "ISO date"),
    (
        "expired",
        entry(reviewed_at=EXPIRED_REVIEW, expires_at=(TODAY - timedelta(days=1)).isoformat()),
        "expired",
    ),
    ("over-90-days", entry(expires_at=(TODAY + timedelta(days=91)).isoformat()), "90 days"),
    ("future-review", entry(reviewed_at=(TODAY + timedelta(days=1)).isoformat()), "future"),
]


@pytest.mark.parametrize(("name", "bad", "message"), BAD_ENTRIES, ids=[b[0] for b in BAD_ENTRIES])
def test_policy_rejects_malformed_entry(name: str, bad: dict[str, Any], message: str) -> None:
    problems, _ = scan.policy_problems({"schema": 1, "entries": [bad]}, TODAY, PROFILES)
    assert any(message in problem for problem in problems), problems


@pytest.mark.parametrize(
    "raw",
    [{"schema": 2, "entries": []}, {"schema": True, "entries": []}, {"entries": []}, []],
    ids=["schema-2", "schema-bool", "no-schema", "not-object"],
)
def test_policy_rejects_bad_document(raw: Any) -> None:
    problems, _ = scan.policy_problems(raw, TODAY, PROFILES)
    assert problems


def test_policy_rejects_duplicate_triples() -> None:
    entries = [entry(), entry(images=["app", "python-core"])]
    problems, _ = scan.policy_problems({"schema": 1, "entries": entries}, TODAY, PROFILES)
    assert any("duplicate" in problem for problem in problems)


def test_policy_expired_entry_fails_scan_and_validation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "policy.json"
    stale = entry(reviewed_at="2026-01-01", expires_at="2026-03-01")
    path.write_text(json.dumps({"schema": 1, "entries": [stale]}), "utf-8")
    with pytest.raises(scan.ScanError, match="expired"):
        scan.load_policy(path, TODAY, PROFILES)
    assert scan.main(["validate-policy", "--policy", str(path)]) == 2
    assert "expired" in capsys.readouterr().err
    code = scan.main(
        ["scan", "--image", "x", "--policy", str(path), "--cache", str(OUTSIDE_CACHE)],
        FakeDocker({}),
    )
    assert code == 2


def test_policy_hash_is_recorded(tmp_path: Path) -> None:
    path = tmp_path / "policy.json"
    path.write_text(json.dumps({"schema": 1, "entries": [entry()]}), "utf-8")
    loaded = scan.load_policy(path, TODAY, PROFILES)
    assert loaded.sha256 == scan.sha256_bytes(path.read_bytes())


# Task 2: decision rules ---------------------------------------------------------------------


def test_unresolved_serious_findings_block_without_policy() -> None:
    result = evaluate("unfixed")
    assert ("CVE-2025-7458", "libsqlite3-0", "unaccepted") in reasons(result["blocking"])
    assert ("CVE-2026-53613", "bsdutils", "unaccepted") in reasons(result["blocking"])
    reported = {item["severity"] for item in result["reported"]}
    assert reported == {"MEDIUM", "LOW", "UNKNOWN"}
    assert all(item["reason"] == "unfixed" for item in result["reported"])
    assert result["counts"] == {"CRITICAL": 2, "HIGH": 1, "MEDIUM": 1, "LOW": 1, "UNKNOWN": 1}


def test_unresolved_live_entries_suppress_exact_matches() -> None:
    rules = policy(entry(), entry(id="CVE-2026-53613", package="bsdutils"))
    result = evaluate("unfixed", rules=rules)
    assert reasons(result["blocking"]) == [("CVE-2026-112393", "pillow", "fixable")]
    assert {item["id"] for item in result["suppressed"]} == {"CVE-2025-7458", "CVE-2026-53613"}
    assert all(
        item["expires_at"] == rules.entries[0].expires_at.isoformat()
        for item in result["suppressed"]
    )
    assert all(item["reviewer"] == "pending-owner" for item in result["suppressed"])


def test_unresolved_entry_must_match_profile_and_package() -> None:
    rules = policy(entry(images=["python-core"]), entry(id="CVE-2026-53613", package="util-linux"))
    result = evaluate("unfixed", rules=rules)
    blocked = {item["id"] for item in result["blocking"] if item["reason"] == "unaccepted"}
    assert blocked == {"CVE-2025-7458", "CVE-2026-53613"}
    assert result["suppressed"] == []


def test_fixed_version_entry_does_not_suppress_fixable_finding() -> None:
    rules = policy(entry(id="CVE-2026-112393", package="pillow"))
    result = evaluate("unfixed", rules=rules)
    assert ("CVE-2026-112393", "pillow", "fixable") in reasons(result["blocking"])
    assert all(item["package"] != "pillow" for item in result["suppressed"])


def test_fixed_version_rust_binary_findings_block_at_any_severity() -> None:
    result = evaluate("rustbinary")
    assert {item["severity"] for item in result["blocking"]} == {"MEDIUM", "LOW"}
    assert all(item["reason"] == "fixable" for item in result["blocking"])
    assert all(item["target"] == "usr/local/bin/uv" for item in result["blocking"])


def test_coverage_unsupported_os_fails_closed() -> None:
    result = evaluate("unsupported-os", "r-statistics")
    assert reasons(result["blocking"]) == [("unsupported-os", "debian forky/sid", "coverage")]


def test_coverage_entry_allows_unsupported_os() -> None:
    rules = policy(
        entry(
            id="unsupported-os",
            kind="coverage",
            package="debian forky/sid",
            images=["r-statistics"],
        )
    )
    result = evaluate("unsupported-os", "r-statistics", rules)
    assert result["blocking"] == []
    assert reasons(result["suppressed"]) == [("unsupported-os", "debian forky/sid", "accepted")]


def test_coverage_zero_packages_and_missing_os_block() -> None:
    report = fixture("clean")
    report["Results"] = []
    del report["Metadata"]["OS"]
    result = scan.evaluate(report, "app", EMPTY, NOW)
    assert {item["id"] for item in result["blocking"]} == {"os-not-detected", "no-packages"}


def test_coverage_eosl_os_blocks() -> None:
    report = fixture("clean")
    report["Metadata"]["OS"]["EOSL"] = True
    assert reasons(scan.evaluate(report, "app", EMPTY, NOW)["blocking"])[0][2] == "coverage"


def test_secret_findings_block_and_misconfig_split_by_severity() -> None:
    result = evaluate("secret-misconfig")
    assert ("github-pat", "GitHub", "secret") in reasons(result["blocking"])
    misconfig = [item for item in result["blocking"] if item["kind"] == "misconfig"]
    assert [(item["id"], item["target"]) for item in misconfig] == [
        ("DS-0002", "opt/course/docker/workers/Dockerfile.c")
    ]
    assert reasons(result["reported"]) == [("DS-0026", "opt/course/Dockerfile", "misconfig-low")]


def test_secret_cannot_be_accepted_but_misconfig_can() -> None:
    rules = policy(
        entry(id="DS-0002", kind="misconfig", package="opt/course/docker/workers/Dockerfile.c")
    )
    result = evaluate("secret-misconfig", rules=rules)
    assert reasons(result["blocking"]) == [("github-pat", "GitHub", "secret")]
    assert [item["id"] for item in result["suppressed"]] == ["DS-0002"]


def test_reference_image_blocks_only_fixable_serious(tmp_path: Path) -> None:
    result = evaluate("unfixed", "postgres", reference=True)
    assert reasons(result["blocking"]) == [("CVE-2026-112393", "pillow", "fixable")]
    assert all(item["reason"] == "reference-unfixed" for item in result["reported"])
    rust = evaluate("rustbinary", "postgres", reference=True)
    assert rust["blocking"] == []
    assert {item["reason"] for item in rust["reported"]} == {"reference-fixable"}


def test_reference_requires_postgres_name() -> None:
    assert scan.parse_reference("postgres=postgres:17").reference is True
    with pytest.raises(scan.ScanError):
        scan.parse_reference("mysql=mysql:8")


def test_freshness_stale_db_blocks_every_image(tmp_path: Path) -> None:
    runner = FakeDocker({LAB_ID: "clean", WORKER_ID: "clean"})
    targets = [scan.Target("app", LAB_ID), scan.Target("python-core", WORKER_ID)]
    later = DB_TIME + timedelta(hours=25)
    evidence = run_scan(runner, targets, tmp_path, now=later)
    assert evidence["passed"] is False
    for image in evidence["images"]:
        assert reasons(image["blocking"]) == [("stale-db", "trivy-db", "stale-db")]
    fresh = run_scan(runner, targets, tmp_path)
    assert fresh["passed"] is True


def test_freshness_missing_java_db_fails(tmp_path: Path) -> None:
    version = {k: v for k, v in VERSION.items() if k != "JavaDB"}
    with pytest.raises(scan.ScanError, match="download-db"):
        run_scan(FakeDocker({}, version=version), [scan.Target("app", LAB_ID)], tmp_path)


def test_freshness_wrong_scanner_version_fails(tmp_path: Path) -> None:
    version = {**VERSION, "Version": "0.69.4"}
    with pytest.raises(scan.ScanError, match="0.69.4"):
        run_scan(FakeDocker({}, version=version), [scan.Target("app", LAB_ID)], tmp_path)


# Task 2: tested-images mode -----------------------------------------------------------------


def snapshot_file(tmp_path: Path) -> Path:
    snapshot = {
        "schema_version": 1,
        "kind": "ds60-tested-images",
        "context": {
            "namespace": "sadatnfs",
            "repository": "sadatnfs/ds60sqlpy",
            "source_repository": "sadatnfs/ds60sqlpy",
            "version": "2.1.0",
            "revision": REVISION,
            "run_id": "1",
            "run_attempt": "1",
        },
        "architecture": "arm64",
        "group": "python-core",
        "seed_receipt": None,
        "images": [
            {
                "profile": "app",
                "local_repository": "ds60sqlpy-lab",
                "tested_image_id": LAB_ID,
                "local_descriptor": None,
            },
            {
                "profile": "python-core",
                "local_repository": "ds60sqlpy-worker-python-core",
                "tested_image_id": WORKER_ID,
                "local_descriptor": None,
            },
        ],
    }
    path = tmp_path / "tested-images.json"
    path.write_text(json.dumps(snapshot), "utf-8")
    return path


def snapshot_args(tmp_path: Path, path: Path) -> list[str]:
    return [
        "scan",
        "--tested",
        str(path),
        "--cache",
        str(OUTSIDE_CACHE),
        "--output",
        str(tmp_path / "evidence.json"),
        "--reports",
        str(tmp_path / "reports"),
    ]


def test_revision_tested_mode_scans_ids_and_copies_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(scan, "utc_now", lambda: POLICY_NOW)
    runner = FakeDocker(
        {LAB_ID: "clean", WORKER_ID: "clean"}, labels={LAB_ID: REVISION}, version=POLICY_VERSION
    )
    path = snapshot_file(tmp_path)
    assert scan.main(snapshot_args(tmp_path, path), runner) == 0
    evidence = json.loads((tmp_path / "evidence.json").read_text("utf-8"))
    assert evidence["context"]["revision"] == REVISION
    assert evidence["architecture"] == "arm64"
    assert [image["tested_image_id"] for image in evidence["images"]] == [LAB_ID, WORKER_ID]
    assert [image["revision_label"] for image in evidence["images"]] == [REVISION, ""]
    targets = [call[-1] for call in runner.calls if "--scanners" in call]
    assert targets == [LAB_ID, WORKER_ID]
    assert [
        call[call.index("--scanners") + 1] for call in runner.calls if "--scanners" in call
    ] == [
        "vuln,secret,misconfig",
        "vuln,secret",
    ]


def test_revision_mismatch_fails_scan(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(scan, "utc_now", lambda: POLICY_NOW)
    runner = FakeDocker(
        {LAB_ID: "clean", WORKER_ID: "clean"}, labels={WORKER_ID: "2" * 40}, version=POLICY_VERSION
    )
    assert scan.main(snapshot_args(tmp_path, snapshot_file(tmp_path)), runner) == 2
    evidence = json.loads((tmp_path / "evidence.json").read_text("utf-8"))
    assert evidence["images"][0]["blocking"] == []
    assert reasons(evidence["images"][1]["blocking"]) == [
        ("revision-mismatch", scan.REVISION_LABEL, "revision")
    ]


def test_revision_architecture_mismatch_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(scan, "utc_now", lambda: NOW)
    runner = FakeDocker({LAB_ID: "clean", WORKER_ID: "clean"}, architecture="amd64")
    assert scan.main(snapshot_args(tmp_path, snapshot_file(tmp_path)), runner) == 2


@pytest.mark.parametrize(
    "mutate",
    [
        lambda s: s.update(schema_version=2),
        lambda s: s.update(extra=1),
        lambda s: s["images"].append(copy.deepcopy(s["images"][0])),
        lambda s: s["images"][0].update(tested_image_id="ds60sqlpy-lab:1.4.3"),
        lambda s: s["images"][0].update(profile="cuda-cpp"),
        lambda s: s["context"].update(revision="main"),
        lambda s: s.update(architecture="s390x"),
    ],
    ids=["schema", "extra-key", "duplicate", "tag-not-id", "gpu", "revision", "arch"],
)
def test_revision_snapshot_shape_is_strict(tmp_path: Path, mutate: Callable[[Any], None]) -> None:
    path = snapshot_file(tmp_path)
    raw = json.loads(path.read_text("utf-8"))
    mutate(raw)
    path.write_text(json.dumps(raw), "utf-8")
    with pytest.raises(scan.ScanError):
        scan.load_tested(path, scan.catalog_profiles())


def test_reference_scan_in_evidence(tmp_path: Path) -> None:
    runner = FakeDocker({LAB_ID: "clean", PG_ID: "rustbinary"}, tags={"postgres:17": PG_ID})
    targets = [scan.Target("app", LAB_ID), scan.parse_reference("postgres=postgres:17")]
    evidence = run_scan(runner, targets, tmp_path)
    assert evidence["passed"] is True
    pg = evidence["images"][1]
    assert (pg["profile"], pg["reference"], pg["tested_image_id"]) == ("postgres", True, PG_ID)
    assert pg["scanners"] == "vuln"


def test_unused_policy_entries_are_listed(tmp_path: Path) -> None:
    runner = FakeDocker({LAB_ID: "clean"})
    evidence = run_scan(runner, [scan.Target("app", LAB_ID)], tmp_path, rules=policy(entry()))
    assert evidence["passed"] is True
    assert evidence["unused_policy_entries"] == [
        {
            "id": "CVE-2025-7458",
            "kind": "vulnerability",
            "package": "libsqlite3-0",
            "images": ["app"],
        }
    ]


# Task 2: proposals --------------------------------------------------------------------------


def test_policy_propose_entries_skips_fixable(tmp_path: Path) -> None:
    runner = FakeDocker({LAB_ID: "unfixed", WORKER_ID: "unfixed"})
    targets = [scan.Target("app", LAB_ID), scan.Target("python-core", WORKER_ID)]
    evidence = run_scan(runner, targets, tmp_path)
    proposed, refused = scan.propose_entries(evidence, TODAY, 90)
    assert refused == 2
    assert [(item["id"], item["images"]) for item in proposed] == [
        ("CVE-2025-7458", ["app", "python-core"]),
        ("CVE-2026-53613", ["app", "python-core"]),
    ]
    assert all(item["reviewer"] == "pending-owner" for item in proposed)
    assert all(item["justification"] == "" for item in proposed)
    assert proposed[0]["expires_at"] == (TODAY + timedelta(days=90)).isoformat()
    filled = [{**item, "justification": "No upstream fix."} for item in proposed]
    problems, _ = scan.policy_problems({"schema": 1, "entries": filled}, TODAY, PROFILES)
    assert problems == []
    with pytest.raises(scan.ScanError):
        scan.propose_entries(evidence, TODAY, 91)


def test_policy_propose_cli_prints_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    evidence = run_scan(FakeDocker({LAB_ID: "unfixed"}), [scan.Target("app", LAB_ID)], tmp_path)
    path = tmp_path / "evidence.json"
    scan.write_json(path, evidence)
    monkeypatch.setattr(scan, "utc_now", lambda: NOW)
    assert scan.main(["propose-entries", "--evidence", str(path), "--days", "30"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert {item["expires_at"] for item in out["entries"]} == {
        (TODAY + timedelta(days=30)).isoformat()
    }


def test_download_db_runs_both_downloads(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    runner = FakeDocker({})
    cache = tmp_path / "cache"
    monkeypatch.setattr(scan, "resolve_cache", lambda path, root=scan.ROOT: path)
    assert scan.main(["download-db", "--cache", str(cache)], runner) == 0
    assert cache.is_dir()
    flags = [arg for call in runner.calls for arg in call if arg.startswith("--download")]
    assert flags == ["--download-db-only", "--download-java-db-only"]


def test_parse_time_handles_nanoseconds() -> None:
    parsed = scan.parse_time("2026-11-24T01:05:31.383410241Z")
    assert parsed == datetime(2026, 11, 24, 1, 5, 31, 383410, tzinfo=UTC)
    assert scan.iso(parsed) == "2026-11-24T01:05:31Z"
    assert isinstance(TODAY, date)
