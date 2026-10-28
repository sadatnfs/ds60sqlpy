"""Owned ML project's contracts; real Docker HTTP qualification is check.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "courses/ml-engineering/projects/local-system"


def load_module(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"local_ml_{name}", PROJECT / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[ModuleType, dict[str, Any]]:
    common = load_module("common")
    monkeypatch.setattr(common, "STATE", tmp_path)
    monkeypatch.setenv("DS60_WORKSHOP_OWNER", "owned-fixture")
    (tmp_path / "owner.json").write_text(json.dumps({"owner": "owned-fixture"}))
    model = {
        "version": "v1",
        "features": ["usage", "tickets", "north"],
        "feature_schema": "customer-v1",
        "mean": [10, 1, 0],
        "scale": [2, 1, 1],
        "coefficients": [0.4, -0.3, 0.2],
        "intercept": 0.1,
        "approved_for_local_demo": True,
    }
    directory = tmp_path / "models/v1"
    directory.mkdir(parents=True)
    (directory / "model.json").write_text(json.dumps(model))
    common.activate("v1")
    return common, model


def test_safe_inference_matches_independent_logistic_equation(
    state: tuple[ModuleType, dict[str, Any]],
) -> None:
    common, model = state
    expected_logit = 0.1 + ((14 - 10) / 2) * 0.4 + (2 - 1) * -0.3 + 0.2
    assert common.probability(
        model, {"usage": 14, "tickets": 2, "region": "north"}
    ) == pytest.approx(1 / (1 + math.exp(-expected_logit)))
    assert common.load_model()[1] == model


@pytest.mark.parametrize("raw", [b"[]", b'{"x":NaN}', b'{"x":Infinity}', b"x" * 200_001])
def test_state_rejects_invalid_or_unbounded_json(raw: bytes) -> None:
    with pytest.raises(ValueError):
        load_module("common").decode_document(raw)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), True, -1, 10_001])
def test_feature_domain_fails_before_inference(
    state: tuple[ModuleType, dict[str, Any]], bad: Any
) -> None:
    common, model = state
    with pytest.raises(ValueError):
        common.probability(model, {"usage": bad, "tickets": 1, "region": "north"})


def test_rejected_activation_leaves_pointer_bytes_unchanged(
    state: tuple[ModuleType, dict[str, Any]],
) -> None:
    common, model = state
    before = (common.STATE / "current.json").read_bytes()
    candidate = dict(model, version="v2", scale=[0, 1, 1])
    path = common.STATE / "models/v2"
    path.mkdir()
    (path / "model.json").write_text(json.dumps(candidate))
    with pytest.raises(ValueError, match="scaling"):
        common.activate("v2")
    assert (common.STATE / "current.json").read_bytes() == before
    assert not (common.STATE / "current.pending").exists()


def test_exact_model_integrity_and_state_ownership(
    state: tuple[ModuleType, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    common, _ = state
    path = common.STATE / "models/v1/model.json"
    original = path.read_bytes()
    assert common.load_model()[0]["sha256"] == hashlib.sha256(original).hexdigest()
    path.write_bytes(original + b" ")
    with pytest.raises(ValueError, match="integrity"):
        common.load_model()
    path.write_bytes(original)
    monkeypatch.setenv("DS60_WORKSHOP_OWNER", "someone-else")
    with pytest.raises(ValueError, match="ownership"):
        common.load_model()


def test_service_schema_and_offline_page(
    state: tuple[ModuleType, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    TestClient = pytest.importorskip(
        "fastapi.testclient", reason="Prepared API runtime required"
    ).TestClient

    common, _ = state
    monkeypatch.setitem(sys.modules, "common", common)
    service = load_module("service")
    with TestClient(service.app) as client:
        for payload in ({"customer_id": True}, {"customer_id": 12}, {"customer_id": 1, "label": 1}):
            assert client.post("/predict", json=payload).status_code == 422
        page = client.get("/")
        assert page.status_code == 200
        assert '<form id="prediction-form">' in page.text
        assert "https://" not in page.text
        assert page.headers["x-content-type-options"] == "nosniff"
        assert client.get("/docs").status_code == 404
        assert set(client.get("/openapi.json").json()["paths"]) == {
            "/",
            "/health",
            "/predict",
            "/metrics",
        }


def test_checker_rejects_preexisting_project_before_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checker = load_module("check")
    monkeypatch.setattr(
        checker, "resources", lambda *_: {"containers": ["existing"], "networks": [], "volumes": []}
    )

    def no_command(*args: Any, **kwargs: Any) -> str:
        raise AssertionError("No command is authorized after preexisting resources are found")

    monkeypatch.setattr(checker, "command", no_command)
    with pytest.raises(ValueError, match="already owns resources"):
        checker.run_checks("docker", "ds60-mle-existing", "local:test", tmp_path / "report.json")


def test_checker_rejects_remote_context_before_creating_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checker = load_module("check")
    monkeypatch.setattr(
        checker, "resources", lambda *_: {"containers": [], "networks": [], "volumes": []}
    )
    monkeypatch.setenv("DOCKER_HOST", "tcp://remote.example:2376")
    monkeypatch.delenv("DOCKER_CONTEXT", raising=False)
    with pytest.raises(ValueError, match="local Unix-socket"):
        checker.run_checks("docker", "ds60-mle-remote", "local:test", tmp_path / "report.json")
    assert not (tmp_path / "report.json").exists()
