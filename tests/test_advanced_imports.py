from __future__ import annotations

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
        "ml",
        "production",
        "deep-learning",
        "nlp",
        "geo",
    }
    assert len(ADVANCED_IMPORT_TARGETS) == 25


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
