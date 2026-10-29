"""Keep current classroom defaults coherent without rewriting historical versions."""

from __future__ import annotations

import ast
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION: str = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
OWN_IMAGE = re.compile(r"ds60sqlpy-(?:lab|worker-[a-z0-9-]+):(\d+\.\d+\.\d+)")


def test_python_distribution_and_editable_lock_share_current_version() -> None:
    module = ast.parse((ROOT / "src/ds60sqlpy/__init__.py").read_text())
    declared = [
        ast.literal_eval(node.value)
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets
        )
    ]
    locked = [
        package
        for package in tomllib.loads((ROOT / "uv.lock").read_text())["package"]
        if package["name"] == "ds60sqlpy"
    ]
    assert declared == [VERSION]
    assert len(locked) == 1 and locked[0]["version"] == VERSION
    assert locked[0]["source"] == {"editable": "."}


def test_app_launcher_compose_and_core_base_use_current_version() -> None:
    label = re.findall(
        r'org\.opencontainers\.image\.version="([^"]+)"', (ROOT / "Dockerfile").read_text()
    )
    release = re.findall(
        r"^release_version=([^\n]+)$",
        (ROOT / "scripts/classroom_images.sh").read_text(),
        re.MULTILINE,
    )
    assert label == release == [VERSION]
    for name in [
        "compose.yaml",
        "compose.classroom.yaml",
        "compose.modules.yaml",
        "compose.classroom.kubernetes.yaml",
        "docker/workers/Dockerfile.python-core",
    ]:
        versions = OWN_IMAGE.findall((ROOT / name).read_text())
        assert versions and set(versions) == {VERSION}, name


def test_maintained_owned_project_image_defaults_follow_current_release() -> None:
    paths = [ROOT / "examples/native-ad-core/Dockerfile"]
    for path in (ROOT / "courses").rglob("*"):
        if any(
            part in {".workshop", "__pycache__", "qualification-history"} for part in path.parts
        ):
            continue
        if path.is_file() and (
            path.name.startswith("Dockerfile") or path.name in {"run.sh", "workshop"}
        ):
            paths.append(path)
    seen = 0
    for path in paths:
        versions = OWN_IMAGE.findall(path.read_text())
        if versions:
            seen += 1
            assert set(versions) == {VERSION}, str(path.relative_to(ROOT))
    assert seen >= 20  # The current service-project surface must actually be inspected.
