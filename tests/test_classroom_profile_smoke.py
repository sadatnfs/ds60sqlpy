"""Protect the disposable CI qualification and its read-only persistence pass."""

from __future__ import annotations

import hashlib
from typing import Any

import pytest

from scripts import check_classroom_profiles as smoke


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1:8765/classroom",
        "http://localhost:8765/classroom",
        "http://192.0.2.1:8765/classroom",
        # secret-scan: allow-fixture
        "http://person:password@127.0.0.1:8765/classroom",
        "http://127.0.0.1:8765/classroom?token=private",
        "http://127.0.0.1:8765/classroom#private",
        "http://127.0.0.1:8765/arbitrary",
        "http://127.0.0.1:0/classroom",
    ],
)
def test_remote_credentials_and_non_classroom_urls_are_rejected(url: str) -> None:
    with pytest.raises(ValueError):
        smoke.classroom_origin(url)


def test_current_launcher_address_and_root_address_share_one_origin() -> None:
    assert smoke.classroom_origin("http://127.0.0.1:1234/classroom") == "http://127.0.0.1:1234"
    assert smoke.classroom_origin("http://127.0.0.1:1234") == "http://127.0.0.1:1234"


@pytest.mark.parametrize("profile", smoke.CASES)
def test_each_ordinary_profile_has_a_current_nonempty_cataloged_reference(profile: str) -> None:
    lesson_id, path, source = smoke.reference_source(profile)
    assert lesson_id and path.startswith("courses/") and source.strip()


class FakeClient(smoke.ClassroomClient):
    def __init__(self) -> None:
        self.actions: list[str] = []
        self.source = "print(42)\n"
        self.job: dict[str, Any] = {
            "job_id": "fixture-job",
            "lesson_id": "fixture-001",
            "profile": "python-core",
            "status": "succeeded",
            "returncode": 0,
            "source_sha256": hashlib.sha256(self.source.encode()).hexdigest(),
            "checks": [{"passed": True}],
            "output": "{'checks': 6, 'status': 'passed'}",
        }

    def call(self, action: str, **fields: Any) -> dict[str, Any]:
        self.actions.append(action)
        if action == "module-readiness":
            return {"profiles": [{"profile": "python-core", "ready": True}]}
        if action == "module-run":
            self.job["job_id"] = fields["request_id"]
        if action == "module-job":
            return self.job
        if action == "module-lesson":
            return {"session": {"source": self.source}, "history": [self.job]}
        return {}


def test_recreation_checks_original_source_bound_receipts_without_reexecution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeClient()
    monkeypatch.setattr(
        smoke, "reference_source", lambda *_: ("fixture-001", "courses/example.py", client.source)
    )
    initial = smoke.qualify(client, ["python-core"])
    assert initial["persistence_verified"] is False
    assert client.actions.count("module-run") == 1
    client.actions.clear()
    restored = smoke.qualify(client, ["python-core"], prior=initial)
    assert restored["receipts"] == initial["receipts"]
    assert restored["persistence_verified"] is True
    assert not {"module-run", "module-save", "module-cancel"} & set(client.actions)


@pytest.mark.parametrize(
    "change",
    [
        {"status": "failed"},
        {"returncode": 1},
        {"profile": "cpp20"},
        {"lesson_id": "different-001"},
        {"source_sha256": "different"},
        {"output": "missing expected result"},
        {"checks": [{"passed": False}]},
    ],
)
def test_success_requires_same_source_profile_lesson_and_real_passing_checks(
    change: dict[str, Any],
) -> None:
    client = FakeClient()
    with pytest.raises(ValueError, match="successful source-bound receipt"):
        smoke.verify_receipt({**client.job, **change}, "fixture-001", "python-core", client.source)


@pytest.mark.parametrize("profile", sorted(smoke.TYPED_PROFILES))
def test_specialized_contract_requires_nonempty_worker_checks(profile: str) -> None:
    client = FakeClient()
    job = {**client.job, "profile": profile, "checks": []}
    with pytest.raises(ValueError, match="successful source-bound receipt"):
        smoke.verify_receipt(job, "fixture-001", profile, client.source)


def test_generic_reference_is_not_misreported_as_independent_worker_verification() -> None:
    client = FakeClient()
    smoke.verify_receipt({**client.job, "checks": []}, "fixture-001", "python-core", client.source)


def test_every_profile_has_an_explicit_typed_or_reference_output_contract() -> None:
    assert smoke.CASES.keys() == smoke.EXPECTED_OUTPUT.keys() | smoke.TYPED_PROFILES
    assert not smoke.EXPECTED_OUTPUT.keys() & smoke.TYPED_PROFILES
