"""Exact-source qualification cannot be replaced by another event, job or attempt."""

from __future__ import annotations

from typing import Any

import pytest

from scripts import ci_release_status as gate

SHA = "a" * 40


def runs() -> list[dict[str, Any]]:
    return [
        {
            "workflow_runs": [
                {
                    "id": number,
                    "run_attempt": 1,
                    "path": path,
                    "event": "push",
                    "head_branch": "main",
                    "head_sha": SHA,
                    "status": "completed",
                    "conclusion": "success",
                }
                for number, path in enumerate(gate.WORKFLOWS, 10)
            ]
        }
    ]


@pytest.mark.parametrize(
    "field,value",
    [
        ("path", ".github/workflows/unreviewed.yml"),
        ("event", "pull_request"),
        ("head_branch", "topic"),
        ("head_sha", "b" * 40),
    ],
)
def test_wrong_source_workflow_or_event_cannot_qualify(field: str, value: str) -> None:
    pages = runs()
    pages[0]["workflow_runs"][0][field] = value
    assert len(gate.selected_runs(pages, SHA)) == 1


def test_newer_failed_attempt_blocks_prior_success() -> None:
    pages = runs()
    pages[0]["workflow_runs"].append(
        {**pages[0]["workflow_runs"][0], "run_attempt": 2, "conclusion": "failure"}
    )
    with pytest.raises(ValueError, match="not successful"):
        gate.selected_runs(pages, SHA)


def test_completed_workflow_without_required_starter_is_not_enough() -> None:
    with pytest.raises(ValueError, match="missing"):
        gate.successful_jobs(
            [
                {
                    "jobs": [
                        {
                            "id": 3,
                            "name": "Skipped Docker matrix",
                            "status": "completed",
                            "conclusion": "success",
                        }
                    ]
                }
            ],
            ("Portable Docker classroom starter",),
        )


def test_latest_job_result_is_used_while_prior_successful_jobs_survive_retry() -> None:
    pages = [
        {
            "jobs": [
                {"id": 1, "name": "source", "status": "completed", "conclusion": "success"},
                {"id": 2, "name": "starter", "status": "completed", "conclusion": "failure"},
                {"id": 3, "name": "starter", "status": "completed", "conclusion": "success"},
            ]
        }
    ]
    assert [row["id"] for row in gate.successful_jobs(pages, ("source", "starter"))] == [1, 3]
    pages[0]["jobs"].append(
        {"id": 4, "name": "source", "status": "completed", "conclusion": "skipped"}
    )
    with pytest.raises(ValueError, match="did not succeed"):
        gate.successful_jobs(pages, ("source", "starter"))


def test_waiter_checks_required_jobs_after_both_exact_runs_complete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[str] = []
    workflow_rows = runs()

    def api(path: str) -> Any:
        requests.append(path)
        if "head_sha=" in path:
            return workflow_rows
        run_id = int(path.split("/runs/", 1)[1].split("/", 1)[0])
        selected = workflow_rows[0]["workflow_runs"][run_id - 10]["path"]
        return [
            {
                "jobs": [
                    {"id": i, "name": name, "status": "completed", "conclusion": "success"}
                    for i, name in enumerate(gate.WORKFLOWS[selected], 1)
                ]
            }
        ]

    monkeypatch.setattr(gate, "api", api)
    result = gate.wait_for_qualification("example/classroom", SHA, timeout_seconds=1)
    assert result["passed"] is result["complete"] is True
    assert len(requests) == 3 and all("filter=all" in path for path in requests[1:])
    assert result["revision"] == SHA


def test_required_job_names_match_the_maintained_workflows() -> None:
    from pathlib import Path

    yaml = pytest.importorskip("yaml")
    root = Path(__file__).resolve().parents[1]
    ci = yaml.load((root / ".github/workflows/ci.yml").read_text(), Loader=yaml.BaseLoader)["jobs"]
    names = {
        ci["source-quality"]["name"].replace("${{ matrix.toolchain }}", value)
        for value in ("main", "r", "julia")
    }
    names.update(
        ci["core"]["name"].replace("${{ matrix.python-version }}", value)
        for value in ("3.11", "3.12")
    )
    names.update([ci["developer-bootstrap"]["name"], ci["postgres"]["name"]])
    assert names == set(gate.WORKFLOWS[".github/workflows/ci.yml"])
    app = yaml.load((root / ".github/workflows/app-build.yml").read_text(), Loader=yaml.BaseLoader)[
        "jobs"
    ]
    assert gate.WORKFLOWS[".github/workflows/app-build.yml"] == (app["docker-starter"]["name"],)
