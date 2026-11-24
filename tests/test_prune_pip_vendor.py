"""Tests for the build-time pip vendor prune step (docker/prune_pip_vendor.py)."""

from __future__ import annotations

import base64
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "docker/prune_pip_vendor.py"
SPEC = importlib.util.spec_from_file_location("ds60_prune_pip_vendor_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
prune_pip_vendor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prune_pip_vendor)

BOM = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.6",
    "version": 1,
    "metadata": {"component": {"bom-ref": "bom-ref:pip", "name": "pip", "type": "library"}},
    "components": [
        {"bom-ref": "bom-ref:pip", "name": "pip", "type": "library"},
        {"bom-ref": "pkg:pypi/idna@3.20", "name": "idna", "version": "3.20"},
        {"bom-ref": "pkg:pypi/setuptools@70.3.0", "name": "setuptools", "version": "70.3.0"},
    ],
    "dependencies": [
        {
            "ref": "bom-ref:pip",
            "dependsOn": ["pkg:pypi/idna@3.20", "pkg:pypi/setuptools@70.3.0"],
        },
        {"ref": "pkg:pypi/idna@3.20"},
        {"ref": "pkg:pypi/setuptools@70.3.0"},
    ],
}
VENDOR_TXT = "idna==3.20\nsetuptools==70.3.0\nurllib3==2.8.0\n"


def _digest(data: bytes) -> str:
    return "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode(
        "ascii"
    )


def _fake_pip(site: Path) -> Path:
    vendor = site / "pip/_vendor"
    (vendor / "pkg_resources").mkdir(parents=True)
    (vendor / "pkg_resources/__init__.py").write_text("raise ImportError\n")
    (vendor / "idna").mkdir()
    (vendor / "idna/__init__.py").write_text("")
    (vendor / "bom.cdx.json").write_text(json.dumps(BOM))
    (vendor / "vendor.txt").write_text(VENDOR_TXT)
    info = site / "pip-26.3.dist-info"
    (info / "licenses/src/pip/_vendor/pkg_resources").mkdir(parents=True)
    (info / "licenses/src/pip/_vendor/pkg_resources/LICENSE").write_text("MIT\n")
    (info / "METADATA").write_text(
        "Name: pip\nLicense-File: src/pip/_vendor/idna/LICENSE.md\n"
        "License-File: src/pip/_vendor/pkg_resources/LICENSE\n"
    )
    rows = [
        ["pip/_vendor/idna/__init__.py", _digest(b""), "0"],
        ["pip/_vendor/pkg_resources/__init__.py", "sha256=x", "18"],
        ["pip/_vendor/bom.cdx.json", "sha256=old", "1"],
        ["pip/_vendor/vendor.txt", "sha256=old", "1"],
        ["pip/_internal/metadata/pkg_resources.py", "sha256=keep", "5"],
        ["pip-26.3.dist-info/METADATA", "sha256=old", "1"],
        ["pip-26.3.dist-info/licenses/src/pip/_vendor/pkg_resources/LICENSE", "sha256=x", "4"],
        ["pip-26.3.dist-info/RECORD", "", ""],
    ]
    with (info / "RECORD").open("w", newline="") as stream:
        csv.writer(stream, lineterminator="\n").writerows(rows)
    return info / "RECORD"


def test_prune_removes_vendored_setuptools_and_keeps_inventories_accurate(tmp_path: Path) -> None:
    record = _fake_pip(tmp_path)

    assert prune_pip_vendor.main([str(tmp_path)]) == 0

    vendor = tmp_path / "pip/_vendor"
    assert not (vendor / "pkg_resources").exists()
    assert (vendor / "idna/__init__.py").exists()
    bom = json.loads((vendor / "bom.cdx.json").read_text())
    assert [c["name"] for c in bom["components"]] == ["pip", "idna"]
    assert bom["dependencies"] == [
        {"ref": "bom-ref:pip", "dependsOn": ["pkg:pypi/idna@3.20"]},
        {"ref": "pkg:pypi/idna@3.20"},
    ]
    assert "setuptools" not in (vendor / "bom.cdx.json").read_text()
    assert (vendor / "vendor.txt").read_text() == "idna==3.20\nurllib3==2.8.0\n"
    rows = {row[0]: row for row in csv.reader(record.read_text().splitlines())}
    assert not any("_vendor/pkg_resources/" in path for path in rows)
    # pip's own metadata backend module is not the vendored package and stays.
    assert rows["pip/_internal/metadata/pkg_resources.py"][1] == "sha256=keep"
    info = tmp_path / "pip-26.3.dist-info"
    assert not (info / "licenses/src/pip/_vendor/pkg_resources").exists()
    assert (info / "METADATA").read_text() == (
        "Name: pip\nLicense-File: src/pip/_vendor/idna/LICENSE.md\n"
    )
    for name in (
        "pip/_vendor/bom.cdx.json",
        "pip/_vendor/vendor.txt",
        "pip-26.3.dist-info/METADATA",
    ):
        data = (tmp_path / name).read_bytes()
        assert rows[name][1:] == [_digest(data), str(len(data))]
    assert rows["pip-26.3.dist-info/RECORD"] == ["pip-26.3.dist-info/RECORD", "", ""]


def test_prune_is_idempotent(tmp_path: Path) -> None:
    _fake_pip(tmp_path)
    assert prune_pip_vendor.main([str(tmp_path)]) == 0
    first = (tmp_path / "pip/_vendor/bom.cdx.json").read_text()
    assert prune_pip_vendor.main([str(tmp_path)]) == 0
    assert (tmp_path / "pip/_vendor/bom.cdx.json").read_text() == first


def test_prune_fails_without_pip(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert prune_pip_vendor.main([str(tmp_path)]) == 1
    assert "no pip installation found" in capsys.readouterr().err


def test_verify_rejects_leftover_setuptools(tmp_path: Path) -> None:
    _fake_pip(tmp_path)
    with pytest.raises(prune_pip_vendor.PruneError, match="still exists"):
        prune_pip_vendor.verify(tmp_path)
    prune_pip_vendor.prune(tmp_path)
    (tmp_path / "pip/_vendor/bom.cdx.json").write_text(json.dumps(BOM))
    with pytest.raises(prune_pip_vendor.PruneError, match="still lists setuptools"):
        prune_pip_vendor.verify(tmp_path)


def test_prune_fails_when_record_is_missing(tmp_path: Path) -> None:
    record = _fake_pip(tmp_path)
    record.unlink()
    assert prune_pip_vendor.main([str(tmp_path)]) == 1


def test_app_image_prunes_learner_pip_and_pins_importlib_backend() -> None:
    dockerfile = (SCRIPT.parents[1] / "Dockerfile").read_text()
    assert "_PIP_USE_IMPORTLIB_METADATA=1" in dockerfile
    assert "/opt/course/.venv/bin/python docker/prune_pip_vendor.py" in dockerfile
