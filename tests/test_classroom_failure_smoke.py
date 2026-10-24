"""Failure qualification proves diagnostics without losing saved learner state."""

from __future__ import annotations

import copy
import hashlib
import json
import time
from pathlib import Path
from typing import Any
from urllib.request import OpenerDirector

import pytest

from scripts import check_classroom_failures as smoke
from scripts.check_classroom_profiles import CASES, ClassroomClient, reference_source


class Clock:
    value = 100.0

    def now(self) -> float:
        return self.value


class FakeClient(ClassroomClient):
    def __init__(self, clock: Clock) -> None:
        self.opener = OpenerDirector()
        self.clock = clock
        self.actions: list[tuple[str, dict[str, Any]]] = []
        self.sources = {lesson: f"original {profile}" for profile, (_, lesson) in CASES.items()}
        self.notes = {"prediction": "keep prediction", "explanation": "keep explanation"}
        self.jobs: dict[str, dict[str, Any]] = {}
        self.transport_error = False
        self.restore_error = False
        self.bad_result: dict[str, Any] = {}
        self.elapsed_ids: set[str] = set()
        for profile, (_, lesson) in CASES.items():
            identity = "previous-" + profile
            self.jobs[identity] = {
                "job_id": identity,
                "lesson_id": lesson,
                "profile": profile,
                "source_sha256": hashlib.sha256(self.sources[lesson].encode()).hexdigest(),
                "status": "succeeded",
                "returncode": 0,
            }

    def call(self, action: str, **fields: Any) -> dict[str, Any]:
        self.actions.append((action, fields))
        if action == "module-readiness":
            return {"profiles": [{"profile": profile, "ready": True} for profile in CASES]}
        if action == "module-lesson":
            lesson = fields["lesson_id"]
            return {
                "source": self.sources[lesson],
                "session": {"source": self.sources[lesson], **self.notes},
                "history": copy.deepcopy(
                    [j for j in self.jobs.values() if j["lesson_id"] == lesson]
                ),
            }
        if action == "module-run":
            lesson, source, key = fields["lesson_id"], fields["source"], fields["request_id"]
            profile = next(p for p, (_, identity) in CASES.items() if identity == lesson)
            self.sources[lesson] = source
            timeout = source == smoke.TIMEOUT_SOURCE
            invalid = source == smoke.INVALID_SOURCE[profile]
            self.jobs[key] = {
                "job_id": key,
                "lesson_id": lesson,
                "profile": profile,
                "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "status": "timed_out" if timeout else "failed" if invalid else "succeeded",
                "returncode": -15 if timeout else 1 if invalid else 0,
                "timeout_seconds": fields["timeout_seconds"],
                "elapsed_seconds": 15 if timeout else 0.1,
                "output": "timeout-probe-started\n"
                if timeout
                else " ".join(smoke.DIAGNOSTICS[profile])
                if invalid
                else "{'checks': 6, 'status': 'passed'}\n",
                "detail": "Total execution deadline exceeded; child processes reaped."
                if timeout
                else "",
                "truncated": False,
                "checks": [],
            }
            if self.transport_error:
                raise OSError("private-transport-value must never reach a report")
            return self.jobs[key]
        if action == "module-job":
            key = fields["job_id"]
            job = copy.deepcopy(self.jobs[key])
            if not key.startswith("previous-"):
                if job["status"] == "timed_out" and key not in self.elapsed_ids:
                    self.clock.value += 15
                    self.elapsed_ids.add(key)
                job.update(self.bad_result)
            return job
        if action == "module-cancel":
            self.jobs[fields["job_id"]]["status"] = "cancelled"
            return self.jobs[fields["job_id"]]
        if action == "module-save":
            assert set(fields["fields"]) == {"source"}
            if self.restore_error:
                raise OSError("private-restore-value must never reach a report")
            self.sources[fields["lesson_id"]] = fields["fields"]["source"]
            return {}
        raise AssertionError(action)


def run_probe(
    monkeypatch: pytest.MonkeyPatch,
    client: FakeClient,
    profiles: list[str],
    *,
    timeout: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    monkeypatch.setattr(time, "monotonic", client.clock.now)

    def advance(seconds: float) -> None:
        client.clock.value += seconds

    monkeypatch.setattr(time, "sleep", advance)
    report: dict[str, Any] = {"cases": [], "errors": [], "passed": False}
    snapshots: list[dict[str, Any]] = []
    smoke.qualify(
        client,
        profiles,
        report,
        lambda: snapshots.append(copy.deepcopy(report)),
        check_timeout=timeout,
    )
    return report, snapshots


def test_all_selected_syntax_failures_restore_source_notes_and_existing_receipts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeClient(Clock())
    source_before, jobs_before = copy.deepcopy(client.sources), copy.deepcopy(client.jobs)
    report, snapshots = run_probe(monkeypatch, client, list(CASES))
    assert report["passed"] and len(report["cases"]) == len(CASES)
    assert client.sources == source_before
    assert client.notes == {"prediction": "keep prediction", "explanation": "keep explanation"}
    assert all(client.jobs[key] == value for key, value in jobs_before.items())
    assert all(row["source_and_notes_restored"] for row in report["cases"])
    assert all(row["previous_receipt_preserved"] for row in report["cases"])
    assert any(row["cases"] and not row["cases"][-1]["passed"] for row in snapshots)
    saves = [fields for action, fields in client.actions if action == "module-save"]
    assert all(fields["fields"]["source"] == source_before[fields["lesson_id"]] for fields in saves)


def test_timeout_uses_supported_deadline_then_exact_reference_recovery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeClient(Clock())
    originals = copy.deepcopy(client.sources)
    report, _ = run_probe(monkeypatch, client, ["python-core"], timeout=True)
    assert report["passed"] and report["cases"][-1]["recovery_verified"]
    jobs = report["cases"][-1]["jobs"]
    assert [job["purpose"] for job in jobs] == ["timeout", "recovery"]
    submitted = [fields for action, fields in client.actions if action == "module-run"]
    assert submitted[-2]["timeout_seconds"] == 15
    _, _, reference = reference_source("python-core")
    assert submitted[-1]["source"] == reference
    assert client.sources == originals


@pytest.mark.parametrize(
    "bad_result",
    [
        {"status": "succeeded", "returncode": 0},
        {"source_sha256": "wrong"},
        {"profile": "java21"},
        {"lesson_id": "different-lesson"},
        {"status": "interrupted"},
        {"output": ""},
        {"output": "x" * (smoke.MAX_OUTPUT_BYTES + 1)},
        {"truncated": True},
        {"returncode": None},
    ],
)
def test_wrong_results_fail_and_saved_source_is_restored(
    monkeypatch: pytest.MonkeyPatch,
    bad_result: dict[str, Any],
) -> None:
    client = FakeClient(Clock())
    client.bad_result = bad_result
    before = copy.deepcopy(client.sources)
    report, _ = run_probe(monkeypatch, client, ["python-core"])
    assert not report["passed"] and report["cases"][0]["errors"]
    assert client.sources == before
    assert report["cases"][0]["source_and_notes_restored"]


def test_transport_loss_after_submission_cancels_and_restores_without_exposing_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeClient(Clock())
    client.transport_error = True
    originals = copy.deepcopy(client.sources)
    report, snapshots = run_probe(monkeypatch, client, ["python-core"])
    assert not report["passed"] and report["cases"][0]["cancellation_requested"]
    assert client.sources == originals
    assert any(row["cases"] and row["cases"][0]["jobs"] for row in snapshots)
    assert "private-transport-value" not in json.dumps(report)


def test_failed_restoration_stops_further_cases_and_reports_partial_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeClient(Clock())
    client.restore_error = True
    report, snapshots = run_probe(monkeypatch, client, ["python-core", "java21"])
    assert not report["passed"] and len(report["cases"]) == 1
    assert report["unattempted"] == ["java21"]
    assert report["cases"][0]["jobs"][0]["status"] == "failed"
    assert snapshots[-1] == report and "private-restore-value" not in json.dumps(report)


def test_no_profile_can_be_added_without_a_failure_case() -> None:
    assert CASES.keys() == smoke.INVALID_SOURCE.keys() == smoke.DIAGNOSTICS.keys()


def test_confirmation_required_before_transport_or_report_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(_: str) -> None:
        raise AssertionError("No request without explicit disposable confirmation")

    monkeypatch.setattr(smoke, "ClassroomClient", forbidden)
    report = tmp_path / "report.json"
    with pytest.raises(SystemExit) as error:
        smoke.main(
            [
                "--url",
                "http://127.0.0.1:1234/classroom",
                "--profiles",
                "python-core",
                "--report",
                str(report),
            ]
        )
    assert error.value.code == 2 and not report.exists()


def test_connection_failure_still_writes_a_safe_failure_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unavailable(_: str) -> None:
        raise OSError("private-connection-value")

    monkeypatch.setattr(smoke, "ClassroomClient", unavailable)
    report = tmp_path / "report.json"
    result = smoke.main(
        [
            "--url",
            "http://127.0.0.1:1234/classroom",
            "--profiles",
            "python-core",
            "--report",
            str(report),
            "--confirm-disposable",
        ]
    )
    value = json.loads(report.read_text(encoding="utf-8"))
    assert result == 1 and not value["passed"] and value["errors"]
    assert "private-connection-value" not in report.read_text(encoding="utf-8")


def test_http_transport_timeout_respects_remaining_operation_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Delegate(OpenerDirector):
        observed: float | None = None

        def open(self, fullurl: Any, data: Any = None, timeout: float | None = None) -> Any:
            self.observed = timeout
            return object()

    clock = Clock()
    monkeypatch.setattr(time, "monotonic", clock.now)
    delegate = Delegate()
    opener = smoke.BoundedOpener(delegate)
    opener.deadline = clock.value + 2
    opener.open("http://127.0.0.1:1234", timeout=45)
    assert delegate.observed == 2
    clock.value += 3
    with pytest.raises(TimeoutError):
        opener.open("http://127.0.0.1:1234", timeout=45)


@pytest.mark.parametrize(
    "changes,observed",
    [
        ({}, 0.1),
        ({"elapsed_seconds": 0.1}, 15),
        ({"timeout_seconds": 1}, 15),
    ],
)
def test_timeout_receipt_cannot_claim_an_instant_or_unsupported_deadline(
    changes: dict[str, Any],
    observed: float,
) -> None:
    client = FakeClient(Clock())
    identity = "a" * 32
    lesson = CASES["python-core"][1]
    job = client.call(
        "module-run",
        lesson_id=lesson,
        source=smoke.TIMEOUT_SOURCE,
        request_id=identity,
        timeout_seconds=15,
    )
    with pytest.raises(smoke.QualificationError, match="real 15-second timeout"):
        smoke.verify_failure(
            {**job, **changes},
            profile="python-core",
            lesson_id=lesson,
            job_id=identity,
            source=smoke.TIMEOUT_SOURCE,
            timeout_case=True,
            observed_seconds=observed,
        )


@pytest.mark.parametrize("eventually_terminal", [True, False])
def test_cancel_acknowledgement_waits_for_terminal_before_next_profile(
    monkeypatch: pytest.MonkeyPatch, eventually_terminal: bool
) -> None:
    class PendingCancel(FakeClient):
        cancelling: str | None = None

        def call(self, action: str, **fields: Any) -> dict[str, Any]:
            if action == "module-run" and fields["lesson_id"] == CASES["python-core"][1]:
                self.transport_error = True
                try:
                    return super().call(action, **fields)
                finally:
                    self.transport_error = False
            if action == "module-cancel":
                self.actions.append((action, fields))
                self.cancelling = fields["job_id"]
                self.jobs[self.cancelling]["status"] = "running"
                return self.jobs[self.cancelling]
            if action == "module-job" and fields["job_id"] == self.cancelling:
                self.actions.append((action, fields))
                self.clock.value += 6
                job = self.jobs[fields["job_id"]]
                if eventually_terminal:
                    job["status"] = "cancelled"
                return copy.deepcopy(job)
            return super().call(action, **fields)

    client = PendingCancel(Clock())
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    report, _ = run_probe(monkeypatch, client, ["python-core", "java21"])
    assert report["passed"] is False  # The original transport failure is still a failure.
    first = report["cases"][0]
    if eventually_terminal:
        assert first["cancellation_confirmed"] is True
        assert first["cancellation_outcome"] == "cancelled"
        assert len(report["cases"]) == 2
        assert report["cases"][1]["passed"] is True
    else:
        assert not first.get("cancellation_confirmed")
        assert len(report["cases"]) == 1
        assert report["unattempted"] == ["java21"]
        assert report["errors"][0]["type"] == "CleanupUnconfirmed"
    assert sum(action == "module-run" for action, _ in client.actions) == (
        2 if eventually_terminal else 1
    )


@pytest.mark.parametrize("field", ["job_id", "lesson_id", "profile", "source_sha256"])
def test_cancellation_cannot_confirm_another_submission(field: str) -> None:
    client = FakeClient(Clock())
    key = "previous-python-core"
    expected = dict(client.jobs[key])
    client.jobs[key][field] = "another-submission"
    with pytest.raises(smoke.QualificationError, match="different submission"):
        smoke.confirm_cancellation(client, expected)


@pytest.mark.parametrize("available", [True, False])
def test_failure_probe_startup_uses_normal_readiness_budget_before_strict_job_budget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    available: bool,
) -> None:
    import io
    from urllib.request import Request

    requests: list[tuple[str, float | None]] = []
    report = tmp_path / "failures.json"

    class Transport(OpenerDirector):
        def open(self, fullurl: Any, data: Any = None, timeout: float | None = None) -> Any:
            assert isinstance(fullurl, Request)
            request_data = fullurl.data
            assert isinstance(request_data, bytes)
            action = json.loads(request_data)["action"]
            requests.append((action, timeout))
            payload: dict[str, Any]
            if action == "module-readiness":
                assert json.loads(report.read_text(encoding="utf-8"))["passed"] is False
                if timeout is None or timeout < 6:
                    raise TimeoutError("Aggregate readiness needs more than a job poll")
                payload = {"profiles": [{"profile": "python-core", "ready": available}]}
            else:
                assert action == "module-job" and timeout is not None and 0 < timeout <= 2
                payload = {"status": "failed"}
            return io.BytesIO(json.dumps(payload).encode("utf-8"))

    class Client(ClassroomClient):
        def __init__(self) -> None:
            self.origin = "http://127.0.0.1:1234"
            self.token = "fixture"
            self.opener = Transport()

    client = Client()
    original_opener = client.opener
    monkeypatch.setattr(smoke, "ClassroomClient", lambda _: client)

    def case(
        current: ClassroomClient,
        profile: str,
        record: dict[str, Any],
        checkpoint: Any,
        *,
        timeout_case: bool = False,
    ) -> None:
        assert isinstance(current.opener, smoke.BoundedOpener)
        smoke.budget(current, 2)
        current.call("module-job", job_id="b" * 32)
        record.update(passed=True, source_and_notes_restored=True)
        checkpoint()

    monkeypatch.setattr(smoke, "exercise_case", case)
    result = smoke.main(
        [
            "--url",
            client.origin,
            "--profiles",
            "python-core",
            "--report",
            str(report),
            "--confirm-disposable",
        ]
    )
    saved = json.loads(report.read_text(encoding="utf-8"))
    assert result == (0 if available else 1) and saved["passed"] is available
    assert requests[0] == ("module-readiness", 45)
    assert client.opener is original_opener
    if available:
        assert requests[1][0] == "module-job"
    else:
        assert len(requests) == 1 and saved["cases"] == []
        assert saved["errors"][0]["type"] == "QualificationError"
