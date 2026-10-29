"""Integrity tests for the narrow Spark 4.0.1 child-exit correction."""

from __future__ import annotations

import hashlib
from pathlib import Path
from types import ModuleType
from zipfile import ZipFile

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "courses/advanced-spark-modeling/projects/spark-torch/patch_spark.py"


def module() -> ModuleType:
    from ds60_spark_likelihood.integrations import prepare_spark

    return prepare_spark


def test_checked_patch_preserves_archive_members_and_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    patch = module()
    original = b"if __name__ == '__main__':\n    task = None\n"
    monkeypatch.setattr(patch, "ORIGINAL_SHA256", hashlib.sha256(original).hexdigest())
    archive = tmp_path / "spark.zip"
    with ZipFile(archive, "w") as z:
        z.writestr(patch.MEMBER, original)
        z.writestr("unrelated.py", b"preserve me\n")
    first = patch.patch_archive(archive)
    second = patch.patch_archive(archive)
    assert first == second
    with ZipFile(archive) as z:
        assert z.read("unrelated.py") == b"preserve me\n"
        updated = z.read(patch.MEMBER)
        assert updated == original + patch.ADDITION
        compile(updated, patch.MEMBER, "exec")


@pytest.mark.parametrize("has_suffix", [False, True])
def test_unreviewed_upstream_or_forged_patch_is_refused_without_mutation(
    tmp_path: Path, has_suffix: bool
) -> None:
    patch = module()
    archive = tmp_path / "spark.zip"
    with ZipFile(archive, "w") as z:
        z.writestr(patch.MEMBER, b"unreviewed upstream" + (patch.ADDITION if has_suffix else b""))
    before = archive.read_bytes()
    with pytest.raises(ValueError):
        patch.patch_archive(archive)
    assert archive.read_bytes() == before
