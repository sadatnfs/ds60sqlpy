"""Original-source license and separate native dependency notice contracts."""

import ast
from pathlib import Path

JVM = Path(__file__).resolve().parents[1]


def metadata() -> dict[str, str]:
    values: dict[str, str] = {}
    for node in ast.parse((JVM / "build.py").read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"LICENSE_TEXT", "NOTICE_TEXT"}:
                    value = ast.literal_eval(node.value)
                    assert isinstance(value, str)
                    values[target.id] = value
    return values


def test_jar_original_source_license_matches_package() -> None:
    assert metadata()["LICENSE_TEXT"] == (JVM.parent / "LICENSE").read_text()


def test_jar_notice_preserves_separate_native_dependency_terms() -> None:
    notice = metadata()["NOTICE_TEXT"]
    assert "TMB GPL-2" in notice
    assert "does not\nrelicense the compiled native worker" in notice
    assert "not bundled in this JAR" in notice
    assert "Eigen/RcppEigen" in notice and "nlohmann/json" in notice
