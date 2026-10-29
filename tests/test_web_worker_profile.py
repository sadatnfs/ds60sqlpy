"""Contracts for the isolated, terminating Python web lesson worker."""

from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

from ds60sqlpy.module_jobs import SERVICES, WorkerClient
from ds60sqlpy.module_service import RUNTIME_GUIDANCE
from ds60sqlpy.modules import LANGUAGES
from ds60sqlpy.worker_operations import PROFILES, execute_operation, validate_operation
from scripts.ci_profiles import groups, matrix
from scripts.docker_release import catalog

ROOT = Path(__file__).resolve().parents[1]


def test_web_profile_has_one_fixed_python_execution_boundary() -> None:
    assert PROFILES["python-web"].language == "python"
    assert PROFILES["python-web"].filename == "main.py"
    assert PROFILES["python-web"].verification_ids == ()
    assert LANGUAGES["python-web"] == {"python"}
    assert SERVICES["python-web"] == "python-web-worker"
    assert "do not start a public HTTP server" in RUNTIME_GUIDANCE["python-web"]


def test_web_profile_runs_real_python_and_preserves_failure_status(tmp_path: Path) -> None:
    for number, source in enumerate(("print('web fixture')", "raise SystemExit(7)")):
        result = execute_operation(
            "python-web",
            source,
            tmp_path / str(number),
            15,
            threading.Event(),
            lambda phase: None,
            None,
        )
        assert result.returncode == (0 if number == 0 else 7)
        assert result.status == ("succeeded" if number == 0 else "failed")
        assert result.checks == []


def test_web_worker_endpoint_cannot_point_at_an_arbitrary_host() -> None:
    client = WorkerClient(
        {"DS60_MODULE_ENDPOINTS": json.dumps({"python-web": "http://python-web-worker:8081"})}
    )
    assert client.endpoints["python-web"] == "http://python-web-worker:8081"
    with pytest.raises(ValueError):
        WorkerClient(
            {"DS60_MODULE_ENDPOINTS": json.dumps({"python-web": "http://example.test:80"})}
        )


def test_web_image_is_an_explicit_complete_native_ci_group() -> None:
    rows = groups(ROOT)
    assert [row for row in rows if "python-web" in row["profiles"]] == [
        {"id": "python-web", "profiles": ["python-web"]}
    ]
    entries = [
        row
        for row in matrix(native=True, workers_only=True)["include"]
        if row["group"] == "python-web"
    ]
    assert {row["architecture"] for row in entries} == {"amd64", "arm64"}
    images = catalog(ROOT)
    assert len(images) == 26 and "python-web" in images


def test_web_image_uses_only_prepared_packages_and_one_probe_source() -> None:
    recipe = (ROOT / "docker/workers/Dockerfile.python-web").read_text()
    assert "python -m venv /opt/web" in recipe
    assert "--require-hashes --only-binary=:all:" in recipe
    assert "courses/python-web/runtime_probe.py" in recipe
    for architecture in ("amd64", "arm64"):
        lock = (ROOT / f"docker/workers/requirements-python-web.{architecture}.lock").read_text()
        assert "/Users/" not in lock and "--hash=sha256:" in lock
        assert "django==6.1.2" in lock and "fastapi==0.162.0" in lock


@pytest.mark.parametrize("language, verifier", [("r", None), ("python", "llm-causal-attention-v1")])
def test_web_worker_rejects_wrong_language_or_foreign_verifier(
    language: str, verifier: str | None
) -> None:
    with pytest.raises(ValueError):
        validate_operation("python-web", language, verifier)
