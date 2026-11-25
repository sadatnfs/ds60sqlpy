from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_no_dashes", ROOT / "scripts/check_no_dashes.py"
)
assert SPEC is not None and SPEC.loader is not None
check_no_dashes = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check_no_dashes
SPEC.loader.exec_module(check_no_dashes)


def test_reports_each_dash_with_position_and_skips_vendor_and_binary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "guide.md").write_text("Days 1\u201315\nok\nA \u2014 B\n", encoding="utf-8")
    vendor = tmp_path / "src/ds60sqlpy/assets/vendor/textbook"
    vendor.mkdir(parents=True)
    (vendor / "katex.js").write_text("x\u2014y", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"\x89PNG\0\xe2\x80\x94")
    (tmp_path / "clean.py").write_text("DASH = '\\u2014'\n", encoding="utf-8")

    paths = [
        "guide.md",
        "src/ds60sqlpy/assets/vendor/textbook/katex.js",
        "image.png",
        "clean.py",
    ]
    assert check_no_dashes.main(["--root", str(tmp_path), *paths]) == 1

    out = capsys.readouterr().out.splitlines()
    assert out == ["guide.md:1:7: en dash", "guide.md:3:3: em dash"]


def test_clean_tree_passes(tmp_path: Path) -> None:
    (tmp_path / "notes.md").write_text("Days 1-15: setup, then practice.\n", encoding="utf-8")
    assert check_no_dashes.main(["--root", str(tmp_path), "notes.md"]) == 0


def test_repository_has_no_dashes_outside_vendored_bundles() -> None:
    if not (ROOT / ".git").exists():
        pytest.skip("requires a Git checkout")
    findings = check_no_dashes.scan(ROOT, check_no_dashes.tracked_files(ROOT))
    assert findings == [], [str(finding) for finding in findings[:20]]
