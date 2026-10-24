"""Bounded CI probe contracts; real cluster execution belongs to its workflow."""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.request import OpenerDirector

import pytest

from ds60sqlpy.kubernetes_module import parse_manifests
from scripts import check_kubernetes_classroom as smoke
from scripts.check_classroom_profiles import ClassroomClient


@pytest.mark.parametrize("case", smoke.CASES, ids=lambda case: case.name)
def test_reviewed_live_probe_sources_match_actual_catalog_and_manifest_boundary(
    case: smoke.Case,
) -> None:
    documents = parse_manifests(smoke.source_for(case))
    assert documents
    if case.unready:
        assert (
            documents[0]["spec"]["template"]["spec"]["containers"][0]["readinessProbe"]["httpGet"][
                "path"
            ]
            == "/missing"
        )


def receipt(case: smoke.Case) -> tuple[str, dict[str, Any]]:
    source = smoke.source_for(case)
    checks = [{"name": name, "passed": True} for name in (*case.required_checks, "owned-cleanup")]
    if case.status == "failed":
        checks.append(
            {
                "name": "operation",
                "passed": False,
                "detail": "The bounded owned Job reached a Failed condition; synthetic failure.",
            }
        )
    elif case.status != "succeeded":
        checks.append({"name": "operation-interrupted", "passed": False, "detail": case.status})
    return source, {
        "job_id": "a" * 32,
        "lesson_id": case.lesson_id,
        "profile": "k8s-kind",
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "status": case.status,
        "returncode": 0 if case.status == "succeeded" else 1,
        "checks": checks,
    }


@pytest.mark.parametrize("case", smoke.CASES, ids=lambda case: case.name)
def test_receipt_accepts_only_expected_outcome_and_passing_cleanup(case: smoke.Case) -> None:
    source, job = receipt(case)
    verified = smoke.verify_receipt(case, job, source, job["job_id"])
    assert verified["owned_cleanup_verified"] is True
    job["checks"] = [check for check in job["checks"] if check["name"] != "owned-cleanup"]
    with pytest.raises(ValueError, match="owned-cleanup was not proved"):
        smoke.verify_receipt(case, job, source, job["job_id"])


@pytest.mark.parametrize(
    "change",
    [
        {"source_sha256": "different"},
        {"job_id": "different"},
        {"lesson_id": "different"},
        {"profile": "python-core"},
        {"status": "failed"},
        {"returncode": 1},
        {"truncated": True},
        {"checks": []},
        {"checks": [{"name": "owned-cleanup", "passed": True}]},
    ],
)
def test_mismatched_or_incomplete_receipts_cannot_qualify(change: dict[str, Any]) -> None:
    case = smoke.CASES[0]
    source, job = receipt(case)
    with pytest.raises(ValueError):
        smoke.verify_receipt(case, {**job, **change}, source, job["job_id"])


def test_any_generic_runtime_failure_is_not_the_expected_negative_job_evidence() -> None:
    case = next(case for case in smoke.CASES if case.status == "failed")
    source, job = receipt(case)
    job["checks"][-1]["detail"] = "worker unavailable"
    with pytest.raises(ValueError, match="deliberate finite Job failure"):
        smoke.verify_receipt(case, job, source, job["job_id"])


class CancellationClient(ClassroomClient):
    def __init__(self, case: smoke.Case, *, finish_early: bool = False) -> None:
        self.case = case
        self.actions: list[str] = []
        _, self.job = receipt(case)
        self.cancelled = False
        self.finish_early = finish_early

    def call(self, action: str, **fields: Any) -> dict[str, Any]:
        self.actions.append(action)
        if action == "module-run":
            self.job["job_id"] = fields["request_id"]
        if action == "module-cancel":
            self.cancelled = True
        if action == "module-job":
            if self.cancelled or self.finish_early:
                return self.job
            return {"status": "verifying", "output": smoke.SUBMITTED}
        return {}


def test_cancellation_is_sent_only_after_real_submission_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(time, "sleep", lambda _: None)
    case = next(case for case in smoke.CASES if case.cancel_after_submission)
    client = CancellationClient(case)
    result = smoke.run_case(client, case)
    assert result["status"] == "cancelled"
    assert client.actions == ["module-run", "module-job", "module-cancel", "module-job"]


def test_early_terminal_job_cannot_fake_post_creation_cancellation() -> None:
    case = next(case for case in smoke.CASES if case.cancel_after_submission)
    with pytest.raises(ValueError, match="after actual resource submission"):
        smoke.run_case(CancellationClient(case, finish_early=True), case)


def test_probe_retains_partial_sanitized_report_after_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class ReadyClient(ClassroomClient):
        def __init__(self) -> None:
            self.opener = OpenerDirector()

        def call(self, action: str, **fields: Any) -> dict[str, Any]:
            assert action == "module-readiness"
            return {"profiles": [{"profile": "k8s-kind", "ready": True}]}

    def run_case(
        client: Any,
        case: smoke.Case,
        *,
        on_observation: Callable[[dict[str, Any]], None],
    ) -> dict[str, Any]:
        if case is smoke.CASES[0]:
            return {"case": case.name, "owned_cleanup_verified": True}
        raise ValueError("fixture failure")

    monkeypatch.setattr(smoke, "run_case", run_case)
    report = tmp_path / "report.json"
    with pytest.raises(ValueError, match="fixture failure"):
        smoke.qualify(ReadyClient(), report)
    assert '"complete": false' in report.read_text()
    assert '"case": "reference-k8s-003"' in report.read_text()


def test_every_registered_runnable_reference_is_qualified_with_specific_observations() -> None:
    cases = smoke.reference_cases()
    assert {case.lesson_id for case in cases} == smoke.REFERENCE_CHECKS.keys()
    assert len(cases) == 12
    for case in cases:
        assert case.source_path.startswith("courses/kubernetes/solutions/")
        assert case.required_checks


@pytest.mark.parametrize("terminal_after_cancel", [True, False])
def test_lost_submit_response_cancels_known_job_and_stops_further_cases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, terminal_after_cancel: bool
) -> None:
    case = smoke.CASES[0]

    class LostSubmission(ClassroomClient):
        def __init__(self) -> None:
            self.opener = OpenerDirector()
            self.actions: list[tuple[str, dict[str, Any]]] = []
            _, self.job = receipt(case)

        def call(self, action: str, **fields: Any) -> dict[str, Any]:
            self.actions.append((action, fields))
            if action == "module-readiness":
                return {"profiles": [{"profile": "k8s-kind", "ready": True}]}
            if action == "module-run":
                self.job["job_id"] = fields["request_id"]
                self.job["status"] = "running"
                raise OSError("Synthetic response loss after request acceptance")
            if action == "module-cancel":
                assert fields["job_id"] == self.job["job_id"]
                return self.job
            if action == "module-job":
                assert fields["job_id"] == self.job["job_id"]
                if terminal_after_cancel:
                    self.job["status"] = "cancelled"
                return self.job
            raise AssertionError(action)

    monkeypatch.setattr(smoke, "CANCEL_SECONDS", 0)
    client = LostSubmission()
    report = tmp_path / "receipts.json"
    expected_error = OSError if terminal_after_cancel else RuntimeError
    with pytest.raises(expected_error):
        smoke.qualify(client, report)
    actions = [action for action, _ in client.actions]
    assert actions.count("module-run") == 1
    assert actions.count("module-cancel") == 1
    assert actions.index("module-cancel") < actions.index("module-job")
    saved = json.loads(report.read_text())
    assert saved["complete"] is False
    assert saved["failed_case"] == case.name
    assert saved["receipts"] == []
    assert saved["failure_type"] == expected_error.__name__


@pytest.mark.parametrize("field", ["job_id", "lesson_id", "profile", "source_sha256"])
def test_kubernetes_cancellation_requires_exact_submission_identity(field: str) -> None:
    case = smoke.CASES[0]
    source, job = receipt(case)
    expected_job_id = job["job_id"]
    job[field] = "another-submission"

    class WrongIdentity(ClassroomClient):
        def __init__(self) -> None:
            pass

        def call(self, action: str, **fields: Any) -> dict[str, Any]:
            return job

    with pytest.raises(ValueError, match="different submission"):
        smoke.confirm_cancelled_submission(WrongIdentity(), case, source, expected_job_id)


@pytest.mark.parametrize("readiness_failure", [None, "timeout", "unavailable"])
def test_startup_readiness_keeps_api_budget_and_writes_report_before_request(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    readiness_failure: str | None,
) -> None:
    import io
    from urllib.request import Request

    from scripts.check_classroom_failures import BoundedOpener, budget

    report = tmp_path / "receipts.json"
    requests: list[tuple[str, float | None]] = []

    class Transport(OpenerDirector):
        def open(self, fullurl: Any, data: Any = None, timeout: float | None = None) -> Any:
            assert isinstance(fullurl, Request)
            request_data = fullurl.data
            assert isinstance(request_data, bytes)
            action = json.loads(request_data)["action"]
            requests.append((action, timeout))
            payload: dict[str, Any]
            if action == "module-readiness":
                initial = json.loads(report.read_text(encoding="utf-8"))
                assert initial["complete"] is False and initial["failed_case"] == "readiness"
                assert initial["receipts"] == []
                # Model a valid aggregate response slower than a job poll. No
                # real delay or cluster is required to reproduce the old cap.
                if timeout is None or timeout < 6 or readiness_failure == "timeout":
                    raise TimeoutError("Synthetic readiness deadline")
                payload = {
                    "profiles": [{"profile": "k8s-kind", "ready": readiness_failure is None}]
                }
            else:
                assert action == "module-job" and timeout is not None and 0 < timeout <= 2
                payload = {"status": "succeeded"}
            return io.BytesIO(json.dumps(payload).encode("utf-8"))

    class Client(ClassroomClient):
        def __init__(self) -> None:
            self.origin = "http://127.0.0.1:1234"
            self.token = "fixture"
            self.opener = Transport()

    client = Client()
    original_opener = client.opener
    monkeypatch.setattr(smoke, "ClassroomClient", lambda _: client)
    monkeypatch.setattr(smoke, "CASES", (smoke.CASES[0],))

    def run_case(
        current: ClassroomClient,
        case: smoke.Case,
        *,
        on_observation: Callable[[dict[str, Any]], None],
    ) -> dict[str, Any]:
        assert isinstance(current.opener, BoundedOpener)
        budget(current, 2)
        current.call("module-job", job_id="a" * 32)
        return {"case": case.name, "owned_cleanup_verified": True}

    monkeypatch.setattr(smoke, "run_case", run_case)
    arguments = ["--url", client.origin, "--report", str(report), "--confirm-disposable"]
    if readiness_failure is None:
        assert smoke.main(arguments) == 0
        assert json.loads(report.read_text(encoding="utf-8"))["complete"] is True
        assert requests[1][0] == "module-job"
    else:
        expected = TimeoutError if readiness_failure == "timeout" else ValueError
        with pytest.raises(expected):
            smoke.main(arguments)
        saved = json.loads(report.read_text(encoding="utf-8"))
        assert saved["complete"] is False and saved["receipts"] == []
        assert saved["failed_case"] == "readiness"
        assert saved["failure_type"] == expected.__name__
        assert len(requests) == 1
    assert requests[0] == ("module-readiness", 45)
    assert client.opener is original_opener


class ReceiptClient(ClassroomClient):
    def __init__(
        self, case: smoke.Case, change: dict[str, Any], *, cleanup_fails: bool = False
    ) -> None:
        self.opener = OpenerDirector()
        self.actions: list[str] = []
        _, self.job = receipt(case)
        self.change = change
        self.cancelled = False
        self.cleanup_fails = cleanup_fails

    def call(self, action: str, **fields: Any) -> dict[str, Any]:
        self.actions.append(action)
        if action == "module-readiness":
            return {"profiles": [{"profile": "k8s-kind", "ready": True}]}
        if action == "module-run":
            self.job["job_id"] = fields["request_id"]
            return {}
        if action == "module-cancel":
            self.cancelled = True
            return {"status": "running"}
        assert action == "module-job"
        assert fields["job_id"] == self.job["job_id"]
        if self.cancelled:
            if self.cleanup_fails:
                raise OSError("private cancellation transport diagnostic")
            return self.job
        return {**self.job, **self.change}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("job_id", "private-remote-identity"),
        ("lesson_id", "private-remote-identity"),
        ("profile", "private-remote-identity"),
        ("source_sha256", "private-remote-identity"),
        ("status", "failed"),
        ("returncode", 1),
        ("truncated", True),
    ],
)
def test_each_terminal_mismatch_is_saved_before_validation_and_cleanup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str, value: Any
) -> None:
    case = smoke.CASES[0]
    monkeypatch.setattr(smoke, "CASES", (case,))
    report = tmp_path / "report.json"
    original_verify = smoke.verify_receipt
    observed_before_validation = []

    def verify(
        current: smoke.Case, job: dict[str, Any], source: str, job_id: str
    ) -> dict[str, Any]:
        saved = json.loads(report.read_text(encoding="utf-8"))
        observed_before_validation.append(saved["failed_job"])
        assert saved["failed_job"]["mismatched_fields"] == [field]
        assert saved["complete"] is False
        return original_verify(current, job, source, job_id)

    monkeypatch.setattr(smoke, "verify_receipt", verify)
    client = ReceiptClient(case, {field: value})
    with pytest.raises(ValueError, match="source-bound terminal receipt"):
        smoke.qualify(client, report)
    saved = json.loads(report.read_text(encoding="utf-8"))
    assert saved["failed_job"] == observed_before_validation[0]
    assert saved["failed_job"]["job_id"] == client.job["job_id"]
    assert saved["failed_job"]["source_sha256"] == client.job["source_sha256"]
    assert saved["failure_type"] == "ValueError"
    assert saved["failed_case"] == case.name and saved["receipts"] == []
    assert "private-remote-identity" not in report.read_text(encoding="utf-8")
    assert client.actions == [
        "module-readiness",
        "module-run",
        "module-job",
        "module-cancel",
        "module-job",
    ]


@pytest.mark.parametrize(
    "failure",
    [
        "non-list",
        "non-mapping",
        "non-string-name",
        "duplicate-name",
        "missing-required",
        "failed-required",
        "unexpected-failure",
        "wrong-negative-reason",
        "wrong-interruption-reason",
    ],
)
def test_every_typed_receipt_validation_failure_preserves_safe_observations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    case = smoke.CASES[0]
    if failure == "wrong-negative-reason":
        case = next(case for case in smoke.CASES if case.status == "failed")
    elif failure == "wrong-interruption-reason":
        case = next(case for case in smoke.CASES if case.status == "timed_out")
    _, job = receipt(case)
    checks: Any = job["checks"]
    if failure == "non-list":
        checks = "private-check-payload"
    elif failure == "non-mapping":
        checks = ["private-check-payload"]
    elif failure == "non-string-name":
        checks = [{"name": {"private-check-payload": True}, "passed": True}]
    elif failure == "duplicate-name":
        checks.append(dict(checks[0]))
    elif failure == "missing-required":
        checks = checks[1:]
    elif failure == "failed-required":
        checks[0]["passed"] = False
    elif failure == "unexpected-failure":
        checks.append({"name": "private-check-payload", "passed": False})
    else:
        checks[-1]["detail"] = "private-check-payload"
    monkeypatch.setattr(smoke, "CASES", (case,))
    client = ReceiptClient(case, {"checks": checks})
    report = tmp_path / "report.json"
    with pytest.raises(ValueError):
        smoke.qualify(client, report)
    saved = json.loads(report.read_text(encoding="utf-8"))
    observation = saved["failed_job"]
    assert saved["complete"] is False and saved["receipts"] == []
    assert saved["failure_type"] == "ValueError"
    assert observation["mismatched_fields"] == []
    assert observation["checks_shape_valid"] is (
        failure not in {"non-list", "non-mapping", "non-string-name"}
    )
    assert observation["duplicate_check_names"] is (failure == "duplicate-name")
    assert observation["unknown_check_names"] is (failure == "unexpected-failure")
    assert all(check["name"] in smoke.KNOWN_CHECKS for check in observation["checks"])
    assert "private-check-payload" not in report.read_text(encoding="utf-8")
    assert client.actions.count("module-run") == client.actions.count("module-cancel") == 1


def test_failure_snapshot_excludes_raw_source_output_details_and_unknown_fields() -> None:
    case = smoke.CASES[0]
    source, job = receipt(case)
    job_id = job["job_id"]
    private = "synthetic-private-material-never-publish"
    job.update(
        job_id=private,
        lesson_id=private,
        profile=private,
        source_sha256=private,
        status=private,
        source=private,
        output=private,
        detail=private,
        credentials={"value": private},
        returncode=private,
        elapsed_seconds=private,
        truncated=private,
        checks=[
            {"name": private, "passed": False, "detail": private},
            {"name": "owned-cleanup", "passed": private, "detail": private},
            {
                "name": "operation",
                "passed": False,
                "detail": "The bounded owned Job reached a Failed condition; " + private,
            },
        ],
    )
    observation = smoke.receipt_observation(case, job, source, job_id)
    encoded = json.dumps(observation)
    assert private not in encoded and source not in encoded
    assert set(observation) == {
        "case",
        "lesson_id",
        "profile",
        "job_id",
        "source_sha256",
        "expected_status",
        "status",
        "returncode",
        "elapsed_seconds",
        "truncated",
        "mismatched_fields",
        "checks_shape_valid",
        "duplicate_check_names",
        "unknown_check_names",
        "checks_truncated",
        "checks",
    }
    assert observation["job_id"] == job_id
    assert observation["source_sha256"] == hashlib.sha256(source.encode()).hexdigest()
    for field in ("status", "returncode", "elapsed_seconds", "truncated"):
        assert observation[field] is None
    assert observation["checks"] == [
        {"name": "owned-cleanup", "passed": None, "reason": None, "job_failure_reason": None},
        {
            "name": "operation",
            "passed": False,
            "reason": "owned-job-failed",
            "job_failure_reason": "Unknown",
        },
    ]


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("returncode", True, None),
        ("returncode", 2**500, None),
        ("returncode", -9, -9),
        ("elapsed_seconds", True, None),
        ("elapsed_seconds", 2**5000, None),
        ("elapsed_seconds", float("nan"), None),
        ("elapsed_seconds", float("inf"), None),
        ("elapsed_seconds", -1, None),
        ("elapsed_seconds", 3601, None),
        ("elapsed_seconds", 23.125, 23.125),
    ],
)
def test_failure_observation_bounds_numeric_fields(field: str, value: Any, expected: Any) -> None:
    case = smoke.CASES[0]
    source, job = receipt(case)
    job[field] = value
    observation = smoke.receipt_observation(case, job, source, job["job_id"])
    assert observation[field] == expected
    json.dumps(observation, allow_nan=False)


def test_failure_observation_bounds_checks_without_copying_overflow() -> None:
    case = smoke.CASES[0]
    source, job = receipt(case)
    job["checks"] = [{"name": "owned-cleanup", "passed": True}] * 101
    observation = smoke.receipt_observation(case, job, source, job["job_id"])
    assert observation["checks_truncated"] is True
    assert len(observation["checks"]) == 100
    assert observation["duplicate_check_names"] is True


def test_cancellation_confirmation_failure_keeps_original_terminal_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = smoke.CASES[0]
    monkeypatch.setattr(smoke, "CASES", (case,))
    report = tmp_path / "report.json"
    client = ReceiptClient(case, {"status": "failed", "returncode": 1}, cleanup_fails=True)
    with pytest.raises(RuntimeError, match="cleanup could not be confirmed"):
        smoke.qualify(client, report)
    saved = json.loads(report.read_text(encoding="utf-8"))
    assert saved["failure_type"] == "RuntimeError"
    assert saved["failed_job"]["status"] == "failed"
    assert saved["failed_job"]["mismatched_fields"] == ["status", "returncode"]
    assert "private cancellation transport diagnostic" not in report.read_text(encoding="utf-8")
    assert client.actions.count("module-run") == 1


def test_successful_receipt_clears_unverified_observation_from_final_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = smoke.CASES[0]
    monkeypatch.setattr(smoke, "CASES", (case,))
    report = tmp_path / "report.json"
    client = ReceiptClient(case, {})
    smoke.qualify(client, report)
    saved = json.loads(report.read_text(encoding="utf-8"))
    assert saved["complete"] is True and saved["failed_job"] is None
    assert saved["failed_case"] is None and saved["failure_type"] is None
    assert len(saved["receipts"]) == 1
    assert "module-cancel" not in client.actions


@pytest.mark.parametrize(
    ("remote_reason", "expected"),
    [
        ("DeadlineExceeded", "DeadlineExceeded"),
        ("BackoffLimitExceeded", "BackoffLimitExceeded"),
        ("PodFailurePolicy", "PodFailurePolicy"),
        ("Unknown", "Unknown"),
        ("private-api-reason", "Unknown"),
        ("DeadlineExceeded-private-api-reason", "Unknown"),
        ("", "Unknown"),
    ],
)
def test_snapshot_retains_only_exact_allowlisted_job_failure_reasons(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    remote_reason: str,
    expected: str,
) -> None:
    case = smoke.CASES[0]
    monkeypatch.setattr(smoke, "CASES", (case,))
    _, job = receipt(case)
    checks = [
        *job["checks"],
        {
            "name": "operation",
            "passed": False,
            "detail": "The bounded owned Job reached a Failed condition; "
            f"reason={remote_reason}; private-api-message",
        },
    ]
    client = ReceiptClient(case, {"status": "failed", "returncode": 1, "checks": checks})
    report = tmp_path / "report.json"
    with pytest.raises(ValueError, match="source-bound terminal receipt"):
        smoke.qualify(client, report)
    saved = json.loads(report.read_text(encoding="utf-8"))
    operation = saved["failed_job"]["checks"][-1]
    assert operation == {
        "name": "operation",
        "passed": False,
        "reason": "owned-job-failed",
        "job_failure_reason": expected,
    }
    assert "private-api" not in report.read_text(encoding="utf-8")
    assert saved["failed_job"]["checks"][0]["job_failure_reason"] is None
    assert client.actions.count("module-run") == client.actions.count("module-cancel") == 1
