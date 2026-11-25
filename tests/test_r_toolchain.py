"""Keep the R worker's compiler toolchain and its classroom qualification honest."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from scripts import check_r_toolchain

ROOT = Path(__file__).resolve().parents[1]
TOOLCHAIN = {"gcc", "g++", "gfortran", "make"}


class FakeClient:
    def __init__(self, *jobs: dict[str, Any]) -> None:
        self.jobs = list(jobs)
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.job_id = ""

    def call(self, action: str, **fields: Any) -> dict[str, Any]:
        self.calls.append((action, fields))
        if action == "module-readiness":
            return {"profiles": [{"profile": "r-statistics", "ready": True}]}
        if action == "module-run":
            self.job_id = fields["request_id"]
            return {"job_id": self.job_id, "status": "queued"}
        if action == "module-job":
            job = self.jobs.pop(0) if len(self.jobs) > 1 else self.jobs[0]
            return {"job_id": self.job_id, "profile": "r-statistics", **job}
        return {}


def test_r_worker_keeps_the_compilers_that_learner_packages_need() -> None:
    dockerfile = (ROOT / "docker/workers/Dockerfile.r").read_text(encoding="utf-8")
    install = re.search(r"apt-get install[^&]+", dockerfile)
    assert install is not None and set(install.group(0).split()) >= TOOLCHAIN
    assert not re.search(r"apt-get (?:purge|remove|autoremove)", dockerfile)


def test_probe_builds_every_compiled_language_into_a_per_job_library() -> None:
    source = check_r_toolchain.PROBE_SOURCE
    for fragment in (
        'src", "init.c',
        'src", "dot.cpp',
        'src", "scale.f90',
        "LinkingTo: cpp11",
        "PKG_LIBS = $(FLIBS)",
        '"CMD", "INSTALL"',
        '"-l", shQuote(lib)',
        "Rcpp::cppFunction",
        check_r_toolchain.MARKER,
    ):
        assert fragment in source
    assert "tempdir()" in source and "install.packages" not in source


def test_probe_runs_as_a_worked_solution_and_reports_success() -> None:
    client = FakeClient(
        {"status": "running"},
        {"status": "succeeded", "returncode": 0, "output": check_r_toolchain.MARKER + "\n"},
    )
    report = check_r_toolchain.run_probe(client)
    run = next(fields for action, fields in client.calls if action == "module-run")
    assert run["purpose"] == "solution" and run["timeout_seconds"] == 120
    assert run["lesson_id"] == "r-001" and run["source"] == check_r_toolchain.PROBE_SOURCE
    assert not any(action == "module-save" for action, _ in client.calls)
    assert report["job_id"] == client.job_id and report["status"] == "succeeded"


@pytest.mark.parametrize(
    "job",
    [
        {"status": "failed", "returncode": 1, "output": "make: not found"},
        {"status": "succeeded", "returncode": 0, "output": "no marker"},
    ],
)
def test_probe_rejects_failed_or_incomplete_builds(job: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="could not build"):
        check_r_toolchain.run_probe(FakeClient(job))


def test_probe_cancels_a_job_that_outlives_its_budget() -> None:
    client = FakeClient({"status": "running"})
    with pytest.raises(TimeoutError):
        check_r_toolchain.run_probe(client, budget=0)
    assert client.calls[-1] == ("module-cancel", {"job_id": client.job_id})
