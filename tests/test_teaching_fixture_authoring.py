"""Fixture authoring checks must enforce the loader's raw-byte identity contract."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import runpy
import sys
from pathlib import Path
from typing import cast

import pytest

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = ROOT / "python/authoring/build_teaching_fixtures.py"
FIXTURES = ROOT / "python/fixtures"
NAMES = ("restaurant-bills.csv", "passenger-outcomes.csv", "bird-measurements.csv", "manifest.json")


def authored() -> dict[str, bytes]:
    module = runpy.run_path(str(AUTHOR))
    return {name: text.encode("utf-8") for name, text in module["outputs"]().items()}


def invoke(destination: Path, monkeypatch: pytest.MonkeyPatch, *, check: bool) -> int:
    module = runpy.run_path(str(AUTHOR))
    main = module["main"]
    monkeypatch.setitem(main.__globals__, "DESTINATION", destination)
    monkeypatch.setattr(sys, "argv", [str(AUTHOR), *(["--check"] if check else [])])
    return cast(int, main())


def test_generator_matches_checked_in_bytes_and_raw_manifest_identities() -> None:
    expected = authored()
    assert set(expected) == set(NAMES)
    assert expected == {name: (FIXTURES / name).read_bytes() for name in NAMES}
    manifest = json.loads(expected["manifest.json"])
    for name, entry in manifest["datasets"].items():
        content = expected[name + ".csv"]
        assert hashlib.sha256(content).hexdigest() == entry["sha256"]
        assert len(list(csv.reader(io.StringIO(content.decode("utf-8"))))) - 1 == entry["rows"]
        assert entry["kind"] == "synthetic"


@pytest.mark.parametrize("name", NAMES)
def test_check_rejects_crlf_bytes_without_rewriting_any_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], name: str
) -> None:
    expected = authored()
    for filename, content in expected.items():
        (tmp_path / filename).write_bytes(content)
    changed = expected[name].replace(b"\n", b"\r\n")
    assert changed != expected[name]
    (tmp_path / name).write_bytes(changed)
    before = {filename: (tmp_path / filename).read_bytes() for filename in NAMES}
    assert invoke(tmp_path, monkeypatch, check=True) == 1
    assert capsys.readouterr().out == f"Teaching fixture drift: {name}\n"
    assert before == {filename: (tmp_path / filename).read_bytes() for filename in NAMES}


def test_check_reports_non_utf8_drift_without_decoding_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    for name, content in authored().items():
        (tmp_path / name).write_bytes(content)
    changed = tmp_path / "restaurant-bills.csv"
    changed.write_bytes(b"\xff" + changed.read_bytes())
    assert invoke(tmp_path, monkeypatch, check=True) == 1
    assert capsys.readouterr().out == "Teaching fixture drift: restaurant-bills.csv\n"
    assert changed.read_bytes().startswith(b"\xff")


def test_write_restores_canonical_utf8_bytes_and_preserves_unrelated_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    expected = authored()
    for name, content in expected.items():
        (tmp_path / name).write_bytes(content.replace(b"\n", b"\r\n"))
    unrelated = tmp_path / "notes.txt"
    unrelated.write_bytes(b"preserve this unrelated file\r\n")
    assert invoke(tmp_path, monkeypatch, check=False) == 0
    assert {name: (tmp_path / name).read_bytes() for name in NAMES} == expected
    assert unrelated.read_bytes() == b"preserve this unrelated file\r\n"
    assert invoke(tmp_path, monkeypatch, check=True) == 0


def test_check_reports_missing_output_without_creating_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = authored()
    for name, content in expected.items():
        if name != "manifest.json":
            (tmp_path / name).write_bytes(content)
    assert invoke(tmp_path, monkeypatch, check=True) == 1
    assert capsys.readouterr().out == "Teaching fixture drift: manifest.json\n"
    assert not (tmp_path / "manifest.json").exists()
