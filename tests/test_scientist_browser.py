"""Contract tests for scientific browser acceptance; real Chromium remains separate."""

from __future__ import annotations

import copy
import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.plot_artifacts import output_directory, read_artifacts
from scripts import check_scientist_browser as gate
from scripts.check_scientific_artifacts import digest

ROOT = Path(__file__).resolve().parents[1]


def artifact_fixture(case: gate.Case) -> list[dict[str, Any]]:
    if case.id == "structured-small":
        return [
            {
                "kind": "table",
                "description": "Exact browser table",
                "table": copy.deepcopy(gate.TABLE),
            },
            {
                "kind": "json",
                "description": "Exact browser JSON",
                "data": copy.deepcopy(gate.SMALL_REPORT),
            },
        ]
    if case.id == "structured-large":
        return [
            {
                "kind": "json",
                "description": "Large plain JSON report",
                "data": copy.deepcopy(gate.LARGE_REPORT),
            }
        ]
    if case.id == "dbt-model":
        return [
            {
                "kind": "table",
                "description": "Actual model",
                "table": {
                    "columns": ["order_id", "customer_id", "amount"],
                    "rows": [[5, 20, 120], [1, 10, 100], [2, 20, 50]],
                },
            },
            {
                "kind": "json",
                "description": "Actual compile/run metadata",
                "data": {
                    "commands": [
                        {"command": "seed", "success": True},
                        {"command": "build", "success": True},
                    ],
                    "compiled_sql": "select * from raw_orders where status = 'paid'",
                    "row_count": 3,
                },
            },
        ]
    if case.id == "stan-reference":
        return [
            {
                "kind": "table",
                "description": "Actual summaries",
                "table": {
                    "columns": ["name", "Mean", "R_hat"],
                    "rows": [["mu", 1.9, 1.02], ["posterior_mean", 40 / 21, None]],
                },
            },
            {
                "kind": "plotly",
                "description": "Actual chains",
                "figure": {
                    "data": [
                        {"type": "scatter", "y": [1.0] * 100},
                        {"type": "scatter", "y": [2.0] * 100},
                    ],
                },
            },
        ]
    return [{"kind": kind, "description": "Fixture"} for kind in case.kinds]


def receipt(case: gate.Case, number: int) -> dict[str, Any]:
    return {
        "job_id": f"{number:032x}",
        "lesson_id": case.lesson_id,
        "profile": case.profile,
        "source": case.source,
        "source_sha256": case.source_sha256,
        "status": case.status,
        "returncode": 0 if case.status == "succeeded" else 1,
        "output": "\n".join(case.output_markers),
        "artifacts": artifact_fixture(case),
        "checks": [],
        "truncated": False,
        "created_at": f"2026-10-28T00:00:{number:02}+00:00",
        "worker_instance_id": "isolated-test-worker",
    }


class Client:
    def __init__(self, profiles: list[str] | None = None) -> None:
        self.actions: list[tuple[str, dict[str, Any]]] = []
        self.jobs = {
            row["job_id"]: row
            for number, case in enumerate(gate.cases(ROOT, profiles), 1)
            for row in [receipt(case, number)]
        }
        self.pads = {
            identity: {
                "source": "# Original source " + identity,
                "prediction": "An original prediction",
                "explanation": "Original explanation " + identity,
                "review": "read" if identity.startswith("bayes") else "",
            }
            for identity in gate.PAD_IDS
        }
        self.active: dict[str, Any] | None = None
        self.ready = set(gate.PROFILES)
        self.restore_error: str | None = None

    def call(self, action: str, **fields: Any) -> dict[str, Any]:
        self.actions.append((action, fields))
        if action == "module-job":
            return copy.deepcopy(self.jobs[fields["job_id"]])
        if action == "module-lesson":
            identity = fields["lesson_id"]
            return {
                "source": self.pads[identity]["source"],
                "session": copy.deepcopy(self.pads[identity]),
                "history": [
                    copy.deepcopy(row) for row in self.jobs.values() if row["lesson_id"] == identity
                ],
            }
        if action == "module-save":
            if fields["lesson_id"] == self.restore_error:
                raise OSError("deliberate storage failure")
            self.pads[fields["lesson_id"]].update(fields["fields"])
            return {"session": copy.deepcopy(self.pads[fields["lesson_id"]])}
        if action == "module-index":
            return {"active_job": self.active}
        if action == "module-readiness":
            return {
                "profiles": [
                    {"profile": profile, "ready": profile in self.ready}
                    for profile in gate.PROFILES
                ]
            }
        if action == "classroom-index":
            titles = gate.subject_titles(ROOT)
            titles.update(
                {
                    "python": "Python",
                    "sql": "SQL",
                    "bridge": "Bridge",
                    "statistics-ml": "Statistics",
                }
            )
            for path in (ROOT / "courses").glob("*/lessons.json"):
                identity = json.loads(path.read_text())["track_id"]
                titles.setdefault(identity, identity)
            return {"tracks": [{"id": key, "title": value} for key, value in titles.items()]}
        raise AssertionError("Unexpected action: " + action)

    def report(self, profiles: list[str] | None = None) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "passed": True,
            "profiles": sorted(profiles or gate.PROFILES),
            "receipts": [
                gate.validate_job(case, job)
                for case, job in zip(gate.cases(ROOT, profiles), self.jobs.values(), strict=True)
            ],
            "pads": [
                {"lesson_id": identity, "sha256": digest(self.pads[identity])}
                for identity in gate.PAD_IDS
            ],
        }


def test_complete_reviewed_inventory_and_profile_subsets() -> None:
    rows = gate.cases(ROOT)
    assert tuple(row.id for row in rows) == gate.CASE_IDS
    assert len({row.source_sha256 for row in rows}) == len(rows)
    assert {row.profile for row in rows} == set(gate.PROFILES)
    assert tuple(row.id for row in gate.cases(ROOT, ["python-core"])) == (
        "structured-small",
        "structured-large",
    )
    assert [row.id for row in gate.cases(ROOT, ["dbt-duckdb"])] == ["dbt-model"]
    assert [row.id for row in gate.cases(ROOT, ["data-engineering"])] == ["polars-reference"]
    assert all(len(row.source.encode()) < 48_000 for row in rows)
    assert all(row.source_path.startswith("synthetic:") for row in rows if row.diagnostic_line)
    for invalid in ([], ["cuda-cpp"], ["python-core", "unknown"]):
        with pytest.raises(ValueError, match="reviewed"):
            gate.cases(ROOT, invalid)


def test_actual_source_admission_rejects_runtime_changes_and_external_paths(tmp_path: Path) -> None:
    subject = tmp_path / "courses/example"
    subject.mkdir(parents=True)
    path = subject / "lessons.json"
    row: dict[str, Any] = {
        "id": "case-001",
        "runtime_profile": "python-core",
        "source_path": "outside.py",
        "solution_paths": [],
        "verification_id": None,
    }
    path.write_text(json.dumps({"lessons": [row]}))
    (tmp_path / "outside.py").write_text("print('outside')\n")
    with pytest.raises(ValueError, match="inside"):
        gate.admitted_source("example", "case-001", "python-core", tmp_path)
    with pytest.raises(ValueError, match="runtime"):
        gate.admitted_source("example", "case-001", "julia", tmp_path)


@pytest.mark.parametrize("identity", ["structured-small", "structured-large"])
def test_synthetic_report_probes_really_publish_exact_bounded_payloads(
    identity: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    case = next(row for row in gate.cases(ROOT) if row.id == identity)
    with output_directory(tmp_path):
        exec(compile(case.source, "reviewed-browser-probe.py", "exec"), {"__name__": "__main__"})
    artifacts, warning = read_artifacts(tmp_path)
    assert not warning and len(artifacts) == len(case.kinds)
    job = receipt(case, 1)
    job["artifacts"] = artifacts
    job["output"] = capsys.readouterr().out
    gate.validate_job(case, job)
    if identity == "structured-large":
        encoded = json.dumps(artifacts[0]["data"], indent=2).encode()
        assert 60_000 < len(encoded) < 180_000
    else:
        assert artifacts[0]["table"]["rows"][1][1] is False
        assert artifacts[0]["table"]["rows"][2][1] is None
        assert artifacts[1]["data"]["large_identifier"] == str(2**60)


@pytest.mark.parametrize(
    "field,value",
    [
        ("source", "different"),
        ("source_sha256", "0" * 64),
        ("lesson_id", "eval-999"),
        ("profile", "julia"),
        ("status", "running"),
        ("returncode", False),
        ("returncode", 9),
        ("output", ""),
        ("artifacts", []),
        ("truncated", True),
        ("job_id", "not-a-job"),
    ],
)
def test_receipt_validation_rejects_misattribution_and_incomplete_results(
    field: str, value: Any
) -> None:
    case = next(row for row in gate.cases(ROOT) if row.id == "structured-small")
    job = receipt(case, 1)
    job[field] = value
    with pytest.raises(ValueError):
        gate.validate_job(case, job)


def test_false_and_zero_are_not_interchangeable_in_json_evidence() -> None:
    case = next(row for row in gate.cases(ROOT) if row.id == "structured-small")
    job = receipt(case, 1)
    job["artifacts"][0]["table"]["rows"][1][1] = 0
    with pytest.raises(ValueError, match="Structured"):
        gate.validate_job(case, job)


def test_dbt_requires_executed_commands_and_compiled_sql() -> None:
    case = next(row for row in gate.cases(ROOT) if row.id == "dbt-model")
    job = receipt(case, 1)
    gate.validate_job(case, job)
    job["artifacts"][1]["data"]["compiled_sql"] = (
        "select * from {{ ref('raw_orders') }} where status='paid'"
    )
    with pytest.raises(ValueError, match="compilation"):
        gate.validate_job(case, job)
    job = receipt(case, 1)
    job["artifacts"][0]["table"]["rows"][0][2] = 121
    with pytest.raises(ValueError, match="three-row"):
        gate.validate_job(case, job)


def test_stan_requires_real_summary_quantity_and_both_complete_chains() -> None:
    case = next(row for row in gate.cases(ROOT) if row.id == "stan-reference")
    job = receipt(case, 1)
    gate.validate_job(case, job)
    job["artifacts"][0]["table"]["rows"][1][1] = 2.0
    with pytest.raises(ValueError, match="posterior mean"):
        gate.validate_job(case, job)
    job = receipt(case, 1)
    job["artifacts"][1]["figure"]["data"][1]["y"].pop()
    with pytest.raises(ValueError, match="short-chain"):
        gate.validate_job(case, job)


def test_persistence_reads_original_ids_without_any_mutation() -> None:
    client = Client()
    report = client.report()
    result = gate.verify_persistence(client, report, ROOT)
    assert len(result) == len(gate.CASE_IDS)
    assert {action for action, _ in client.actions} <= {"module-job", "module-lesson"}
    requested = [fields["job_id"] for action, fields in client.actions if action == "module-job"]
    assert requested == [row["job_id"] for row in report["receipts"]]


@pytest.mark.parametrize("change", ["source", "artifacts", "pad", "notes", "history", "incomplete"])
def test_persistence_detects_changed_original_evidence(change: str) -> None:
    client = Client(["python-core"])
    report = client.report(["python-core"])
    first = next(iter(client.jobs.values()))
    if change == "source":
        first["source"] += "# changed\n"
    elif change == "artifacts":
        first["artifacts"][1]["data"]["count"] = 1
    elif change == "pad":
        client.pads["eval-001"]["source"] = "changed"
    elif change == "notes":
        client.pads["dbt-002"]["explanation"] = "changed"
    elif change == "history":
        first["lesson_id"] = "eval-002"
    else:
        report["receipts"].pop()
    with pytest.raises(ValueError):
        gate.verify_persistence(client, report, ROOT)


@pytest.mark.parametrize(
    "action",
    [
        "module-run",
        "module-save",
        "module-cancel",
        "module-recover",
        "module-browser-record",
        "classroom-run",
        "unknown-action",
    ],
)
def test_readonly_client_cannot_execute_or_write(action: str) -> None:
    client = Client(["python-core"])
    with pytest.raises(ValueError, match="cannot write"):
        gate.ReadOnlyClient(client).call(action, lesson_id="eval-001")
    assert client.actions == []


class Request:
    def __init__(self, action: str) -> None:
        self.method = "POST"
        self.url = "http://127.0.0.1:9876/api/modules"
        self.post_data_json = {"action": action}


class Route:
    def __init__(self, action: str) -> None:
        self.request = Request(action)
        self.aborted = False
        self.continued = False

    def abort(self) -> None:
        self.aborted = True

    def fallback(self) -> None:
        self.continued = True


@pytest.mark.parametrize(
    "action,allowed",
    [
        ("module-job", True),
        ("module-lesson", True),
        ("classroom-highlight", True),
        ("module-save", False),
        ("module-run", False),
        ("module-recover", False),
    ],
)
def test_readonly_browser_route_blocks_mutations_before_transmission(
    action: str, allowed: bool
) -> None:
    network = gate.NetworkLog()
    route = Route(action)
    network.readonly_route(route)
    assert route.continued is allowed
    assert route.aborted is not allowed
    assert network.blocked == ([] if allowed else [action])


def test_restore_writes_only_edited_pads_and_verifies_every_sentinel() -> None:
    client = Client(["python-core"])
    originals = copy.deepcopy(client.pads)
    client.pads["eval-001"]["source"] = "synthetic probe"
    report: dict[str, Any] = {"pads": []}
    gate.restore_pads(client, originals, {"eval-001"}, report)
    assert client.pads == originals
    assert [
        fields["lesson_id"] for action, fields in client.actions if action == "module-save"
    ] == ["eval-001"]
    assert tuple(row["lesson_id"] for row in report["pads"]) == gate.PAD_IDS


def test_restore_does_not_hide_a_storage_failure() -> None:
    client = Client(["python-core"])
    originals = copy.deepcopy(client.pads)
    client.pads["eval-001"]["source"] = "synthetic probe"
    client.restore_error = "eval-001"
    report: dict[str, Any] = {"pads": []}
    with pytest.raises(RuntimeError, match="restoration"):
        gate.restore_pads(client, originals, {"eval-001"}, report)
    assert report["restoration_failures"]


def test_effective_source_restoration_handles_an_initially_unsaved_pad() -> None:
    fields = gate.fields_from_lesson({"source": "original starter", "session": {}})
    assert fields == {
        "source": "original starter",
        "prediction": "",
        "explanation": "",
        "review": "",
    }
    with pytest.raises(ValueError, match="text"):
        gate.fields_from_lesson({"source": "starter", "session": {"review": False}})


def test_preflight_rejects_an_unresolved_job_without_saving_anything() -> None:
    client = Client(["python-core"])
    client.active = {"status": "interrupted", "job_id": "a" * 32}
    with pytest.raises(ValueError, match="unresolved"):
        gate.preflight(client, ROOT, ["python-core"])
    assert all(action in gate.READ_ACTIONS for action, _ in client.actions)


class UnknownPage:
    def __init__(self, network: gate.NetworkLog, case: gate.Case) -> None:
        self.clicks = 0
        self.network = network
        self.case = case

    def locator(self, _: str) -> UnknownPage:
        return self

    def fill(self, _: str) -> None:
        pass

    def select_option(self, _: str) -> None:
        pass

    def click(self) -> None:
        self.clicks += 1
        self.network.submissions.append(
            {
                "lesson_id": self.case.lesson_id,
                "request_id": "f" * 32,
                "source_sha256": self.case.source_sha256,
            }
        )

    @contextmanager
    def expect_response(self, *_: Any, **__: Any) -> Iterator[None]:
        yield None
        raise TimeoutError("Deliberate lost response")


def test_unknown_submission_is_recorded_once_and_never_replayed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = next(row for row in gate.cases(ROOT) if row.id == "structured-small")
    network = gate.NetworkLog()
    page = UnknownPage(network, case)
    client = Client(["python-core"])
    report: dict[str, Any] = {"submissions": []}
    monkeypatch.setattr(gate, "save", lambda *_: None)
    with pytest.raises(RuntimeError, match="unconfirmed"):
        gate.submit_once(page, client, case, None, network, report)
    assert page.clicks == 1
    assert report["unconfirmed_submissions"][0]["request_id"] == "f" * 32
    assert all(action == "module-lesson" for action, _ in client.actions)


def test_cli_requires_disposable_authorization_before_browser_import() -> None:
    with pytest.raises(SystemExit) as error:
        gate.main(["--url", "http://127.0.0.1:9876/classroom", "--report", "unused.json"])
    assert error.value.code == 2


def test_persistence_failure_preserves_successful_original_acceptance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = Client(["python-core"])
    original = client.report(["python-core"])
    path = tmp_path / "report.json"
    path.write_text(json.dumps(original))

    def unavailable(_: str) -> None:
        raise OSError("Deliberate unavailable replacement")

    monkeypatch.setattr(gate, "ClassroomClient", unavailable)
    status = gate.main(
        [
            "--url",
            "http://127.0.0.1:9876/classroom",
            "--report",
            str(path),
            "--confirm-disposable",
            "--check-persistence",
        ]
    )
    saved = json.loads(path.read_text())
    assert status == 1
    assert saved["passed"] is True
    assert saved["receipts"] == original["receipts"]
    assert saved["persistence"]["passed"] is False


def test_tutorial_worked_example_ignores_preceding_hidden_tex(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The production math reader retains optional TeX source before the example.
    blocks = [
        {"language": "tex", "visible": False, "text": r"\\frac{1}{2}"},
        {"language": "python", "visible": True, "text": "print(42)"},
    ]
    observed: list[str] = []

    class Element:
        def __init__(self, selector: str) -> None:
            self.selector = selector

        @property
        def first(self) -> Element:
            return self

    class Page:
        def locator(self, selector: str) -> Element:
            return Element(selector)

    class Assertion:
        def __init__(self, element: Element) -> None:
            self.element = element

        def to_contain_text(self, _: str) -> None:
            pass

        def to_be_hidden(self) -> None:
            pass

        def to_have_text(self, _: str) -> None:
            pass

        def to_be_visible(self) -> None:
            if self.element.selector.startswith("#guide pre code"):
                language = self.element.selector.partition(".language-")[2]
                selected = [row for row in blocks if not language or row["language"] == language]
                assert selected and selected[0]["visible"], (
                    "A hidden TeX fence is not a worked program"
                )
                observed.append(str(selected[0]["text"]))

    monkeypatch.setattr(gate, "choose_lesson", lambda *_: None)
    monkeypatch.setattr(gate, "show_pad", lambda *_: None)
    gate.check_tutorial(Page(), "applied-science", "science-001", Assertion)
    assert observed == ["print(42)"]
