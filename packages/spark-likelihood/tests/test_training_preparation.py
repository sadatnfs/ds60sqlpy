"""Explicit Spark wrapper preparation is checked, local and never implicit."""

import hashlib
from zipfile import ZipFile

import pytest
from ds60_spark_likelihood.integrations import prepare_spark


def test_read_only_status_and_explicit_patch_are_source_bound(tmp_path, monkeypatch):
    original = b"if __name__ == '__main__':\n    task = None\n"
    monkeypatch.setattr(prepare_spark, "ORIGINAL_SHA256", hashlib.sha256(original).hexdigest())
    archive = tmp_path / "pyspark.zip"
    with ZipFile(archive, "w") as output:
        output.writestr(prepare_spark.MEMBER, original)
        output.writestr("other.py", b"unchanged\n")
    before = archive.read_bytes()
    assert prepare_spark.wrapper_status(archive)["status"] == "needs-explicit-preparation"
    assert archive.read_bytes() == before
    prepare_spark.patch_archive(archive)
    assert prepare_spark.wrapper_status(archive)["status"] == "prepared"
    with ZipFile(archive) as content:
        assert content.read("other.py") == b"unchanged\n"
    assert (
        prepare_spark.patch_archive(archive)["original_sha256"]
        == hashlib.sha256(original).hexdigest()
    )


def test_unknown_plain_wrapper_is_never_modified(tmp_path):
    source = tmp_path / "wrapper.py"
    source.write_bytes(b"unreviewed source\n")
    with pytest.raises(ValueError, match="unreviewed"):
        prepare_spark.patch_file(source)
    assert source.read_bytes() == b"unreviewed source\n"
