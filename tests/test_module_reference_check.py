"""The corpus gate executes authored references, preserves failures and fails closed."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.modules import ModuleCatalog
from scripts import check_module_references as probe

ROOT = Path(__file__).resolve().parents[1]


def reference(key: str = "example-001", verifier: str | None = None) -> probe.ReferenceCase:
    return probe.ReferenceCase(
        key,
        "example",
        "python-core",
        "python",
        "practice",
        verifier,
        f"courses/example/solutions/{key}.py",
        "assert 6 * 7 == 42\nprint(42)\n",
    )


class FakeClient:
    def __init__(self, cases: list[probe.ReferenceCase]) -> None:
        self.cases = {case.lesson_id: case for case in cases}
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.jobs: dict[str, dict[str, Any]] = {}
        self.fail_lessons: set[str] = set()
        self.metadata_change: dict[str, Any] = {}
        self.ready = True
        self.cancelled = False
        self.stuck = False

    def call(self, action: str, **fields: Any) -> dict[str, Any]:
        self.calls.append((action, fields))
        if action == "module-readiness":
            return {"profiles": [{"profile": "python-core", "ready": self.ready}]}
        if action == "module-lesson":
            case = self.cases[fields["lesson_id"]]
            return {
                "id": case.lesson_id,
                "runtime_profile": case.profile,
                "language": case.language,
                "learning_mode": case.learning_mode,
                "verification_id": case.verification_id,
                **self.metadata_change,
            }
        if action == "module-save":
            return {"session": fields["fields"]}
        if action == "module-run":
            case = self.cases[fields["lesson_id"]]
            assert fields["source"] == case.source
            key = fields["request_id"]
            failed = case.lesson_id in self.fail_lessons
            self.jobs[key] = {
                "job_id": key,
                "lesson_id": case.lesson_id,
                "profile": case.profile,
                "source_sha256": case.source_sha256,
                "status": "failed" if failed else "succeeded",
                "returncode": 1 if failed else 0,
                "checks": [{"passed": True}] if case.verification_id else [],
                "truncated": False,
                "output": "AssertionError: wrong numerical result" if failed else "42\n",
                "worker_token": "must-not-appear-in-report",
            }
            return self.jobs[key]
        if action == "module-job":
            if self.stuck and not self.cancelled:
                return {"status": "running"}
            if self.cancelled:
                return {"status": "cancelled"}
            return self.jobs[fields["job_id"]]
        if action == "module-cancel":
            self.cancelled = True
            return {"status": "cancelled"}
        raise AssertionError(action)


def report_for(cases: list[probe.ReferenceCase]) -> dict[str, Any]:
    return {"results": [{**case.metadata(), "status": "pending"} for case in cases]}


def test_corpus_covers_all_admitted_runnable_implementations_and_book_examples() -> None:
    catalog = ModuleCatalog(ROOT)
    cases, report = probe.collect_cases(ROOT, sorted(probe.ORDINARY_PROFILES))
    assert {case.lesson_id for case in cases} == {
        key
        for key, lesson in catalog.lessons.items()
        if lesson.runtime_profile in probe.ORDINARY_PROFILES
    }
    by_id = {case.lesson_id: case for case in cases}
    assert by_id["statistics-001"].learning_mode == "tutorial"
    assert by_id["statistics-001"].source_path == catalog.get("statistics-001").source_path
    assert "/solutions/" in by_id["java-029"].source_path
    assert by_id["spark-036"].profile == "spark-local-python"
    assert by_id["spark-036@scala"].profile == "spark-local-scala"
    assert by_id["spark-013@pyspark"].language == "python"
    assert report["passed"] is False and report["complete"] is False
    assert {row["profile"] for row in report["excluded_external_or_reading"]} == {
        "reading",
        "k8s-kind",
        "javascript-browser",
        "html-browser",
        "cuda-cpp",
        "cuda-python",
        "pytorch-cuda",
        "tensorflow-cuda",
        "dax-offline",
    }
    assert all(case.source.strip() for case in cases)


@pytest.mark.parametrize(
    "profile", ["html-browser", "cuda-cpp", "cuda-python", "pytorch-cuda", "tensorflow-cuda"]
)
def test_specialized_backends_are_not_silently_qualified_as_ordinary_cpu_workers(
    profile: str,
) -> None:
    assert profile not in probe.ORDINARY_PROFILES
    with pytest.raises(ValueError, match="ordinary"):
        probe.collect_cases(ROOT, [profile])


def test_browser_exclusions_have_complete_real_ui_qualification_and_retained_reports() -> None:
    from scripts.check_d3_browser import references
    from scripts.check_plotly_browser import references as plotly_references

    catalog = ModuleCatalog(ROOT)
    cases, report = probe.collect_cases(ROOT, sorted(probe.ORDINARY_PROFILES))
    browser_ids = {
        key
        for key, lesson in catalog.lessons.items()
        if lesson.runtime_profile == "javascript-browser"
    }
    excluded = {
        row["lesson_id"]: row
        for row in report["excluded_external_or_reading"]
        if row["profile"] == "javascript-browser"
    }
    assert (
        browser_ids
        == set(excluded)
        == {row["id"] for row in [*references(ROOT), *plotly_references(ROOT)]}
    )
    assert len(browser_ids) == 32
    assert not browser_ids & {case.lesson_id for case in cases}
    assert all(
        "real Chromium D3 and Plotly workflows" in row["reason"] for row in excluded.values()
    )
    from scripts.ci_classroom import CORE_BROWSER

    workflow = (ROOT / ".github/workflows/app-build.yml").read_text()
    required = {
        "scripts/check_classroom_browser.py": "browser-receipts.json",
        "courses/web-development/authoring/check_browser.py": "web-browser-receipts.json",
        "courses/web-development/authoring/check_live_preview.py": "live-preview-receipts.json",
        "scripts/check_d3_browser.py": "d3-browser-receipts.json",
        "scripts/check_plotly_browser.py": "plotly-browser-receipts.json",
    }
    assert dict(CORE_BROWSER) == required
    assert "ci_classroom.py qualify" in workflow
    assert "work/*receipts.json" in workflow.split("Retain bounded runtime reports", 1)[1]
    # Execution-level CI tests separately assert these exact D3/Plotly calls
    # run again in read-only persistence mode after container replacement.
    assert CORE_BROWSER[-2:] == (
        ("scripts/check_d3_browser.py", "d3-browser-receipts.json"),
        ("scripts/check_plotly_browser.py", "plotly-browser-receipts.json"),
    )


@pytest.mark.parametrize(
    "profiles", [[], ["k8s-kind"], ["reading"], ["javascript-browser"], ["invented-runtime"]]
)
def test_corpus_does_not_silently_accept_unsupported_profiles(profiles: list[str]) -> None:
    with pytest.raises(ValueError, match="ordinary profiles"):
        probe.collect_cases(ROOT, profiles)


def test_successful_runs_are_source_bound_and_report_no_private_worker_fields(
    tmp_path: Path,
) -> None:
    cases = [reference(), reference("example-002", "fixture-contract")]
    client = FakeClient(cases)
    report = report_for(cases)
    path = tmp_path / "results.json"
    assert probe.run_cases(client, cases, report, path)
    saved = json.loads(path.read_text())
    assert saved["summary"] == {"passed": 2}
    assert saved["complete"] is True
    assert [row["typed_worker_checks"] for row in saved["results"]] == [0, 1]
    assert saved["results"][0]["verification_kind"] == "reference_execution"
    assert saved["results"][1]["verification_kind"] == "typed_contract_and_reference_execution"
    assert "must-not-appear-in-report" not in path.read_text()
    assert len([item for item in client.calls if item[0] == "module-run"]) == 2


def test_reference_assertion_failure_is_retained_and_later_cases_still_execute(
    tmp_path: Path,
) -> None:
    cases = [reference(), reference("example-002")]
    client = FakeClient(cases)
    client.fail_lessons.add("example-001")
    report = report_for(cases)
    assert not probe.run_cases(client, cases, report, tmp_path / "results.json")
    assert report["summary"] == {"failed": 1, "passed": 1}
    assert report["complete"] is True
    assert "AssertionError" in report["results"][0]["output_tail"]
    assert len([call for call in client.calls if call[0] == "module-run"]) == 2


@pytest.mark.parametrize(
    "change",
    [
        {"job_id": "different"},
        {"lesson_id": "different"},
        {"profile": "java21"},
        {"source_sha256": "0" * 64},
        {"status": "failed"},
        {"returncode": 9},
        {"truncated": True},
        {"checks": [{"passed": False}]},
        {"checks": [{"passed": 1}]},
        {"checks": None},
    ],
)
def test_exit_success_cannot_hide_wrong_identity_or_failed_contracts(
    change: dict[str, Any],
) -> None:
    case = reference()
    client = FakeClient([case])
    job = client.call("module-run", lesson_id=case.lesson_id, source=case.source, request_id="job")
    with pytest.raises(ValueError, match="source-bound receipt"):
        probe.verify_result(case, "job", {**job, **change})


def test_declared_typed_verifier_must_actually_return_checks() -> None:
    case = reference(verifier="fixture-contract")
    client = FakeClient([case])
    job = client.call("module-run", lesson_id=case.lesson_id, source=case.source, request_id="job")
    with pytest.raises(ValueError, match="source-bound receipt"):
        probe.verify_result(case, "job", {**job, "checks": []})


def test_mismatched_served_lesson_is_rejected_before_saving_or_executing(tmp_path: Path) -> None:
    case = reference()
    client = FakeClient([case])
    client.metadata_change = {"verification_id": "unexpected-contract"}
    assert not probe.run_cases(client, [case], report_for([case]), tmp_path / "report.json")
    assert not any(action in {"module-save", "module-run"} for action, _ in client.calls)


def test_readiness_failure_leaves_a_truthful_incomplete_report(tmp_path: Path) -> None:
    case = reference()
    client = FakeClient([case])
    client.ready = False
    with pytest.raises(ValueError, match="not ready"):
        probe.run_cases(client, [case], report_for([case]), tmp_path / "report.json")
    assert not any(action == "module-run" for action, _ in client.calls)
    assert json.loads((tmp_path / "report.json").read_text())["results"][0]["status"] == "pending"


def test_deadline_cancels_only_its_job_and_does_not_resubmit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeClient([reference()])
    client.stuck = True
    times = iter(range(100))
    monkeypatch.setattr(
        "scripts.check_module_references.time.monotonic", lambda: float(next(times))
    )
    monkeypatch.setattr("scripts.check_module_references.time.sleep", lambda _seconds: None)
    with pytest.raises(TimeoutError, match="bounded execution deadline"):
        probe.wait_for_job(client, "owned-job", 0)
    assert ("module-cancel", {"job_id": "owned-job"}) in client.calls
    assert not any(action == "module-run" for action, _ in client.calls)


def test_overall_budget_keeps_unrun_cases_pending_instead_of_claiming_success(
    tmp_path: Path,
) -> None:
    case = reference()
    client = FakeClient([case])
    report = report_for([case])
    assert not probe.run_cases(client, [case], report, tmp_path / "report.json", max_seconds=0)
    assert report["summary"] == {"pending": 1}
    assert report["complete"] is False and report["passed"] is False
    assert not any(action == "module-run" for action, _ in client.calls)


def test_cli_requires_disposable_confirmation_before_client_construction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("No client should be created")

    monkeypatch.setattr(probe, "ClassroomClient", forbidden)
    with pytest.raises(SystemExit) as error:
        probe.main(["--profiles", "python-core", "--report", str(tmp_path / "report.json")])
    assert error.value.code == 2


def test_inventory_mode_performs_no_http_and_does_not_claim_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("Inventory must not contact a classroom")

    monkeypatch.setattr(probe, "ClassroomClient", forbidden)
    path = tmp_path / "report.json"
    assert probe.main(["--profiles", "java21", "--report", str(path), "--list-only"]) == 0
    report = json.loads(path.read_text())
    assert report["selected_cases"] > 1
    assert report["passed"] is False and report["complete"] is False
    assert all(result["status"] == "pending" for result in report["results"])


@pytest.mark.parametrize("confirm_cleanup", [True, False])
def test_transport_failure_cancels_owned_job_before_another_case(
    tmp_path: Path, confirm_cleanup: bool
) -> None:
    cases = [reference(), reference("example-002")]

    class BrokenPoll(FakeClient):
        failed_once = False

        def call(self, action: str, **fields: Any) -> dict[str, Any]:
            if action == "module-job" and not self.failed_once:
                self.failed_once = True
                self.calls.append((action, fields))
                raise OSError("Synthetic disconnected poll")
            if action == "module-cancel":
                self.calls.append((action, fields))
                if not confirm_cleanup:
                    raise OSError("Synthetic unavailable cancellation")
                return {**self.jobs[fields["job_id"]], "status": "cancelled"}
            return super().call(action, **fields)

    client = BrokenPoll(cases)
    report = report_for(cases)
    assert not probe.run_cases(client, cases, report, tmp_path / "report.json")
    first = report["results"][0]
    assert first["cleanup"]["confirmed"] is confirm_cleanup
    actions = [action for action, _ in client.calls]
    assert actions.count("module-cancel") == 1
    if confirm_cleanup:
        assert actions.count("module-run") == 2
        assert actions.index("module-cancel") < len(actions) - 1 - actions[::-1].index("module-run")
        assert report["results"][1]["status"] == "passed"
    else:
        assert actions.count("module-run") == 1
        assert report["results"][1]["status"] == "pending"
        assert report["complete"] is False
        assert "unknown" in report["failure"]


@pytest.mark.parametrize("status", ["blocked", "interrupted"])
def test_unresolved_receipts_do_not_confirm_cleanup_or_start_later_cases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, status: str
) -> None:
    cases = [reference(), reference("example-002")]

    class Unresolved(FakeClient):
        def call(self, action: str, **fields: Any) -> dict[str, Any]:
            if action in {"module-job", "module-cancel"}:
                self.calls.append((action, fields))
                return {**self.jobs[fields["job_id"]], "status": status}
            return super().call(action, **fields)

    ticks = iter(range(500))
    monkeypatch.setattr("scripts.check_module_references.time.monotonic", lambda: next(ticks))
    monkeypatch.setattr("scripts.check_module_references.time.sleep", lambda _seconds: None)
    client = Unresolved(cases)
    report = report_for(cases)
    assert not probe.run_cases(client, cases, report, tmp_path / "report.json")
    assert report["results"][0]["cleanup"] == {"confirmed": False, "outcome": "unknown"}
    assert report["results"][1]["status"] == "pending"
    assert not report["complete"]
    assert sum(action == "module-run" for action, _ in client.calls) == 1
    assert any(action == "module-cancel" for action, _ in client.calls)


@pytest.mark.parametrize("field", ["job_id", "lesson_id", "profile", "source_sha256"])
def test_another_terminal_receipt_cannot_bypass_owned_job_cancellation(
    tmp_path: Path, field: str
) -> None:
    case = reference()

    class WrongReceipt(FakeClient):
        def call(self, action: str, **fields: Any) -> dict[str, Any]:
            if action == "module-job":
                self.calls.append((action, fields))
                return {**self.jobs[fields["job_id"]], "status": "failed", field: "other"}
            if action == "module-cancel":
                self.calls.append((action, fields))
                return {**self.jobs[fields["job_id"]], "status": "cancelled"}
            return super().call(action, **fields)

    client = WrongReceipt([case])
    report = report_for([case])
    assert not probe.run_cases(client, [case], report, tmp_path / "report.json")
    assert report["results"][0]["cleanup"] == {"confirmed": True, "outcome": "cancelled"}
    assert any(action == "module-cancel" for action, _ in client.calls)
    assert sum(action == "module-run" for action, _ in client.calls) == 1
