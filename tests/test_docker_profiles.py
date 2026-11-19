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
    mirror_index,
    reject_non_index_pins,
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


@pytest.mark.parametrize(
    "url",
    [
        "http://mirror.example/simple/",
        # secret-scan: allow-fixture
        "https://user:secret@mirror.example/simple/",
        "https://mirror.example/simple/?token=x",
        "https://mirror.example/simple/#frag",
        "https://mirror.example/simple/ extra",
        "file:///tmp/simple",
    ],
)
def test_mirror_requires_an_anonymous_https_index(url: str) -> None:
    with pytest.raises(ValueError, match="anonymous HTTPS"):
        mirror_index(url)
    assert mirror_index("") is None and mirror_index(None) is None
    assert mirror_index("https://mirror.example/simple/") == "https://mirror.example/simple/"


def test_mirror_install_keeps_locked_pins_and_hashes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    commands: list[list[str]] = []

    class Completed:
        returncode = 0

    def record(command: list[str], **kwargs: object) -> Completed:
        commands.append(command)
        if command[1] == "export":
            output = Path(command[command.index("--output-file") + 1])
            output.write_text("pygments==2.19.2 \\\n    --hash=sha256:" + "0" * 64 + "\n")
        return Completed()

    monkeypatch.setenv("DS60_PYTHON_INDEX_URL", "https://mirror.example/simple/")
    monkeypatch.setattr("ds60sqlpy.docker_profiles.shutil.which", lambda name: "/usr/bin/uv")
    monkeypatch.setattr("ds60sqlpy.docker_profiles.subprocess.run", record)
    assert main(["--project", str(ROOT), "--profiles", "core"]) == 0
    export, environment, install = commands
    assert export[1:3] == ["export", "--frozen"] and "--no-emit-project" in export
    assert set(CORE_EXTRAS) <= {export[i + 1] for i, part in enumerate(export) if part == "--extra"}
    assert environment[1] == "venv"
    assert install[1:3] == ["pip", "install"]
    assert {"--require-hashes", "--no-deps"} <= set(install)
    assert install[install.index("--index-url") + 1] == "https://mirror.example/simple/"
    assert "sync" not in (part for command in commands for part in command[1:2])


def test_mirror_refuses_pins_from_another_index() -> None:
    reject_non_index_pins("numpy==2.4.6 ; sys_platform == 'linux' \\\n")
    with pytest.raises(ValueError, match="torch"):
        reject_non_index_pins("torch==2.14.1+cpu ; sys_platform == 'linux' \\\n")
