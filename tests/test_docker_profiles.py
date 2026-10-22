from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

from ds60sqlpy.docker_profiles import (
    ADVANCED_EXTRAS,
    CORE_EXTRAS,
    install_command,
    main,
    select_extras,
)

ROOT = Path(__file__).resolve().parents[1]
DECLARED = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["optional-dependencies"]


def test_core_is_the_default_and_advanced_expands_without_model_download_commands() -> None:
    assert set(select_extras("core", DECLARED)) == set(CORE_EXTRAS)
    assert set(select_extras("advanced", DECLARED)) == set(CORE_EXTRAS + ADVANCED_EXTRAS)
    assert set(select_extras("deep-learning, nlp", DECLARED)) == set(
        CORE_EXTRAS + ("deep-learning", "nlp")
    )
    command = install_command(select_extras("deep-learning", DECLARED), uv="uv", python="python")
    assert "--frozen" in command and "--no-install-project" in command
    assert "pip" not in command and "--upgrade" not in command


@pytest.mark.parametrize("extra", list(DECLARED))
def test_every_declared_extra_can_be_selected_explicitly(extra: str) -> None:
    assert extra in select_extras(extra, DECLARED)


@pytest.mark.parametrize(
    "profile", ["unregistered", "--index-url", "https://example.invalid/x", "ml;echo"]
)
def test_unknown_or_command_like_profile_fails_before_an_installer(profile: str) -> None:
    with pytest.raises(ValueError, match="Unknown image profile"):
        select_extras(profile, DECLARED)


def test_dry_run_never_installs_packages(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def unexpected(*args: object, **kwargs: object) -> None:
        raise AssertionError("Dry-run started package installation.")

    monkeypatch.setattr("ds60sqlpy.docker_profiles.subprocess.run", unexpected)
    assert main(["--project", str(ROOT), "--profiles", "production", "--dry-run"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert "production" in result["extras"]
    assert set(CORE_EXTRAS).issubset(result["extras"])
