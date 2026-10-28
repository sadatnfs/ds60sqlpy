"""Reviewed offline fixtures must survive copied pads without widening file access."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from ds60sqlpy.teaching_data import load_teaching_frame, teaching_fixture

ROOT = Path(__file__).resolve().parents[1]


def fake_course(root: Path) -> None:
    (root / "python/ds-60day").mkdir(parents=True)
    (root / "sql/postgres-60day").mkdir(parents=True)
    (root / "pyproject.toml").write_text('[project]\nname="ds60sqlpy"\n')
    shutil.copytree(ROOT / "python/fixtures", root / "python/fixtures")


def test_import_does_not_load_pandas_or_a_catalog() -> None:
    code = (
        "import sys; sys.path.insert(0, " + repr(str(ROOT / "src")) + "); "
        "import ds60sqlpy.teaching_data; "
        "assert 'pandas' not in sys.modules; "
        "assert 'ds60sqlpy.catalog' not in sys.modules; "
        "assert 'ds60sqlpy.course_paths' not in sys.modules"
    )
    subprocess.run([sys.executable, "-I", "-c", code], check=True, timeout=10)


@pytest.mark.parametrize(
    "name", ["../sales.csv", "https://example.invalid/data.csv", "tips", "", None]
)
def test_fixture_names_cannot_select_arbitrary_paths(name: str | None) -> None:
    with pytest.raises(ValueError, match="registered"):
        teaching_fixture(name)  # type: ignore[arg-type]


def test_copied_pad_resolves_reviewed_source_fixture(tmp_path: Path) -> None:
    script = tmp_path / "unrelated/saved/pad.py"
    script.parent.mkdir(parents=True)
    script.write_text(
        "from ds60sqlpy.teaching_data import teaching_fixture\n"
        "print(teaching_fixture('professional-sales').name)\n"
        "print(teaching_fixture('tiny-package-project').parent.name)\n"
    )
    process = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src"), "DS60_REPO_ROOT": str(ROOT)},
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    assert process.stdout.splitlines() == ["sales.csv", "tiny_package"]


def test_dataset_identity_population_and_independent_frame_state() -> None:
    pytest.importorskip("pandas")
    restaurant = load_teaching_frame("restaurant-bills")
    passengers = load_teaching_frame("passenger-outcomes")
    birds = load_teaching_frame("bird-measurements")
    assert restaurant.shape == (240, 7) and passengers.shape == (360, 15)
    assert birds.shape == (180, 7) and len(birds.dropna()) == 163
    assert restaurant.attrs["dataset_kind"] == passengers.attrs["dataset_kind"] == "synthetic"
    assert restaurant["day"].cat.categories.tolist() == ["Thur", "Fri", "Sat", "Sun"]
    assert passengers["class"].cat.categories.tolist() == ["First", "Second", "Third"]
    assert passengers.age.isna().sum() == 28 and passengers.fare.isna().sum() == 12
    assert (restaurant.total_bill > 0).all() and (restaurant.tip >= 0).all()
    original = float(restaurant.loc[0, "tip"])
    restaurant.loc[0, "tip"] = 999
    assert load_teaching_frame("restaurant-bills").loc[0, "tip"] == original


def test_digest_guard_rejects_changed_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("pandas")
    fake_course(tmp_path)
    monkeypatch.setenv("DS60_REPO_ROOT", str(tmp_path))
    path = tmp_path / "python/fixtures/restaurant-bills.csv"
    path.write_bytes(path.read_bytes() + b"changed\n")
    with pytest.raises(ValueError, match="content identity"):
        load_teaching_frame("restaurant-bills")


def test_configured_wrong_root_does_not_fall_back(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("DS60_REPO_ROOT", str(tmp_path))
    with pytest.raises(FileNotFoundError, match="assets are unavailable"):
        teaching_fixture("professional-sales")


def test_fixture_symlink_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    course = tmp_path / "course"
    fake_course(course)
    monkeypatch.setenv("DS60_REPO_ROOT", str(course))
    path = course / "python/fixtures/restaurant-bills.csv"
    path.unlink()
    outside = tmp_path / "outside.csv"
    outside.write_text("owned test data\n")
    path.symlink_to(outside)
    with pytest.raises(ValueError, match="symbolic"):
        teaching_fixture("restaurant-bills")


def test_manifest_rejects_boolean_row_count(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("pandas")
    fake_course(tmp_path)
    monkeypatch.setenv("DS60_REPO_ROOT", str(tmp_path))
    path = tmp_path / "python/fixtures/manifest.json"
    payload = json.loads(path.read_text())
    payload["datasets"]["restaurant-bills"]["rows"] = True
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="metadata"):
        load_teaching_frame("restaurant-bills")
