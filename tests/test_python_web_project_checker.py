"""Focused negative contracts for the owned native web-project orchestration."""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path
from types import ModuleType

import pytest

SOURCE = (
    Path(__file__).resolve().parents[1] / "courses/python-web/projects/web-lab/check_project.py"
)


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("web_project_check", SOURCE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_environment_does_not_inherit_emulation_project_or_registry_tokens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for key in [
        "DOCKER_DEFAULT_PLATFORM",
        "DOCKERHUB_TOKEN",
        "DOCKERHUB_USERNAME",
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "DOCKER_CONFIG",
        "COMPOSE_FILE",
        "WORKSHOP_IMAGE",
        "DS60_IMAGE",
    ]:
        monkeypatch.setenv(key, "synthetic-must-not-reach-child")
    monkeypatch.setenv("DOCKER_HOST", "unix:///synthetic-reviewed-engine")
    environment = load().clean_environment()
    assert "synthetic-must-not-reach-child" not in environment.values()
    assert environment["DOCKER_HOST"] == "unix:///synthetic-reviewed-engine"


def test_relative_browser_path_is_absolute_without_losing_venv_link(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = tmp_path / "venv/bin"
    directory.mkdir(parents=True)
    link = directory / "python"
    link.symlink_to(Path(sys.executable))
    monkeypatch.chdir(tmp_path)
    selected = load().browser_interpreter(Path("venv/bin/python"))
    assert selected == link and selected.is_absolute()
    assert selected != link.resolve()


@pytest.mark.parametrize(
    "architecture,system,image_arch",
    [("riscv64", "linux", "riscv64"), ("arm64", "linux", "amd64"), ("amd64", "windows", "amd64")],
)
def test_refuses_unsupported_or_non_native_images(
    architecture: str, system: str, image_arch: str
) -> None:
    with pytest.raises(ValueError, match="native Linux"):
        load().require_native_image({"system": system, "architecture": image_arch}, architecture)


def test_source_inventory_and_copy_ignore_the_same_caches(tmp_path: Path) -> None:
    module = load()
    source = tmp_path / "source"
    source.mkdir()
    (source / "app.py").write_text("print('public')\n")
    (source / ".DS_Store").write_bytes(b"not-source")
    (source / ".ruff_cache").mkdir()
    (source / ".ruff_cache/private").write_text("not-source")
    (source / "ignored.pyc").write_bytes(b"not-source")
    expected = module.digest_tree(source)
    assert set(expected) == {"app.py"}
    copied = tmp_path / "copied"
    shutil.copytree(
        source, copied, ignore=shutil.ignore_patterns(*module.IGNORED_SOURCE_NAMES, "*.pyc")
    )
    assert module.digest_tree(copied) == expected
    (source / "linked.py").symlink_to(source / "app.py")
    with pytest.raises(ValueError, match="symlinks"):
        module.digest_tree(source)
