from __future__ import annotations

import tomllib
from pathlib import Path

from ds60sqlpy.advanced_imports import (
    ADVANCED_IMPORT_TARGETS,
    ImportResult,
    ImportTarget,
    build_probe_code,
    validate_target_manifest,
)


def test_advanced_import_manifest_is_complete_and_unique() -> None:
    assert validate_target_manifest() == []
    assert {target.group for target in ADVANCED_IMPORT_TARGETS} == {
        "bridge",
        "professional",
        "sql-notebooks",
        "ml",
        "production",
        "deep-learning",
        "nlp",
        "geo",
    }
    assert len(ADVANCED_IMPORT_TARGETS) == 34
    assert ImportTarget("ml", "numba", "numba") in ADVANCED_IMPORT_TARGETS


def test_ml_extra_has_cross_platform_numba_compatibility_bounds() -> None:
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    ml_requirements = pyproject["project"]["optional-dependencies"]["ml"]
    numba_requirements = {
        requirement for requirement in ml_requirements if requirement.startswith("numba")
    }

    assert numba_requirements == {
        "numba>=0.62.1,<0.63; sys_platform == 'darwin' and platform_machine == 'x86_64'",
        "numba>=0.66; sys_platform != 'darwin' or platform_machine != 'x86_64'",
    }


def test_deep_learning_extra_retains_wheels_for_both_mac_architectures() -> None:
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    requirements = set(pyproject["project"]["optional-dependencies"]["deep-learning"])

    assert requirements == {
        "numpy>=1.26.4,<2; sys_platform == 'darwin' and platform_machine == 'x86_64'",
        "torch==2.2.2; sys_platform == 'darwin' and platform_machine == 'x86_64'",
        "torch==2.11.0; sys_platform == 'darwin' and platform_machine == 'arm64'",
        "torch>=2.3; sys_platform != 'darwin'",
        "torchvision==0.17.2; sys_platform == 'darwin' and platform_machine == 'x86_64'",
        "torchvision==0.26.0; sys_platform == 'darwin' and platform_machine == 'arm64'",
        "torchvision>=0.18; sys_platform != 'darwin'",
    }


def test_probe_code_uses_distribution_and_module_names() -> None:
    target = ImportTarget("example", "example-dist", "example_module")
    code = build_probe_code(target)

    assert "import_module('example_module')" in code
    assert "version('example-dist')" in code
    compile(code, "<advanced-import-probe>", "exec")


def test_import_result_passes_only_for_zero_exit_status() -> None:
    target = ImportTarget("example", "example-dist", "example_module")

    assert ImportResult(target, 0, "1.0").passed
    assert not ImportResult(target, 1, "boom").passed
