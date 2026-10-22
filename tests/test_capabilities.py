"""Check readiness without installing packages or running learner source."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.capabilities import CapabilityService, _probe, probe_python, probe_sql
from ds60sqlpy.catalog import Catalog


def course(tmp_path: Path, *, runner: str = "python", group: str = "core") -> Catalog:
    lesson = replace(Catalog.load().get("python-01"), runner=runner, dependency_group=group)
    return Catalog(tmp_path, (lesson,))


def test_real_package_discovery_uses_fixed_top_level_names() -> None:
    result = probe_python(sys.executable, ("json", "_ds60_nonexistent_package_fixture"))
    assert result["available"] is True
    assert result["missing_modules"] == ["_ds60_nonexistent_package_fixture"]


def test_optional_profile_warning_does_not_block_standard_library_snippets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "ds60sqlpy.capabilities.probe_python",
        lambda *args: {"available": True, "missing_modules": ["torch"], "python_version": "3.12"},
    )
    result = CapabilityService(course(tmp_path, group="deep-learning"), sys.executable).runner(
        "python-01", "python"
    )
    assert result["can_run"] and result["available"]
    assert result["profile_ready"] is False and result["missing_modules"] == ["torch"]
    assert "DS60_DOCKER_PROFILES=deep-learning" in result["setup"]
    assert result["allowed_timeout_seconds"] == [15, 60, 120]
    assert "magics" in result["notebook_guidance"]
    assert not (tmp_path / ".learning").exists()


@pytest.mark.parametrize("runner", ["none", "cpp", "scala", "kubernetes"])
def test_future_and_reading_runners_do_not_probe_or_claim_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: str
) -> None:
    def unexpected(*args: object, **kwargs: object) -> None:
        raise AssertionError("An unimplemented runner attempted native discovery.")

    monkeypatch.setattr("ds60sqlpy.capabilities._probe", unexpected)
    result = CapabilityService(course(tmp_path, runner=runner), None).lesson("python-01")
    assert result["default_runner"] == runner
    assert len(result["runners"]) == 1
    descriptor = result["runners"][0]
    assert descriptor["can_run"] is False and descriptor["implemented"] is False
    assert descriptor["available"] is (runner == "none")
    assert not (tmp_path / ".learning").exists()


def test_missing_interpreter_is_reported_without_creating_a_workspace(tmp_path: Path) -> None:
    result = CapabilityService(course(tmp_path), None).runner("python-01", "python")
    assert not result["available"] and not result["can_run"]
    assert "DS60_PYTHON" in result["reason"]
    assert list(tmp_path.iterdir()) == []


def test_missing_ipython_warns_for_notebooks_but_keeps_plain_snippets_runnable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def probe(python: str, modules: tuple[str, ...]) -> dict[str, Any]:
        assert "IPython" in modules
        return {"available": True, "missing_modules": ["IPython"]}

    monkeypatch.setattr("ds60sqlpy.capabilities.probe_python", probe)
    result = CapabilityService(course(tmp_path), sys.executable).runner("python-01", "python")
    assert result["can_run"] and not result["profile_ready"]
    assert result["notebook_cells_ready"] is False
    assert "# %%" in result["notebook_guidance"]
    assert "Install the notebooks profile" in result["notebook_guidance"]
    assert not (tmp_path / ".learning").exists()


def test_unknown_dependency_label_does_not_invent_an_install_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "ds60sqlpy.capabilities.probe_python",
        lambda *args: {"available": True, "missing_modules": []},
    )
    result = CapabilityService(course(tmp_path, group="custom-topic"), sys.executable).runner(
        "python-01", "python"
    )
    assert result["profile_ready"] is False
    assert "no built-in installer" in result["setup"]
    assert "DS60_DOCKER_PROFILES=" not in result["setup"]


def test_sql_probe_rejects_a_remote_target_before_starting_any_child(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DS60_DATABASE_URL", "postgresql://remote.invalid/advanced_sql_training")

    def unexpected(*args: object, **kwargs: object) -> None:
        raise AssertionError("A remote database was probed.")

    monkeypatch.setattr("ds60sqlpy.capabilities._probe", unexpected)
    available, reason = probe_sql(sys.executable)
    assert not available and "local disposable" in reason


def test_sql_probe_hides_credentials_and_removes_routing_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = "postgresql://student:" + "fixture-password@127.0.0.1:5432/advanced_sql_training"
    monkeypatch.setenv("DS60_DATABASE_URL", target)
    monkeypatch.setenv("PGHOST", "remote.invalid")
    monkeypatch.setenv("PGSERVICE", "do-not-use")
    seen: list[dict[str, str]] = []

    def probe(python: str, code: str, environment: dict[str, str]) -> dict[str, bool]:
        seen.append(environment)
        return {"connected": True, "limited_role": False}

    monkeypatch.setattr("ds60sqlpy.capabilities._probe", probe)
    available, reason = probe_sql(sys.executable)
    assert not available and "limited course login" in reason
    assert "fixture-password" not in reason and target not in reason
    assert seen[0]["PGHOST"] == "127.0.0.1" and "PGSERVICE" not in seen[0]
    assert seen[0]["PGCONNECT_TIMEOUT"] == "2"


def test_discovery_timeout_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout(*args: object, **kwargs: Any) -> None:
        assert kwargs["stdin"] == subprocess.DEVNULL
        assert kwargs["timeout"] == 4
        raise subprocess.TimeoutExpired("fixed readiness probe", 4)

    monkeypatch.setattr("ds60sqlpy.capabilities.subprocess.run", timeout)
    assert _probe(sys.executable, "fixed source", {}) == {}
