"""Preparation rejects tampered sources and unsafe archive layouts."""

import io
import sys
import tarfile
from pathlib import Path

import pytest

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))
import prepare  # noqa: E402
from build_native import inventory  # noqa: E402


def archive(entries):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w:gz") as output:
        for name, body, kind in entries:
            member = tarfile.TarInfo(name)
            member.type = kind
            member.size = len(body) if kind == tarfile.REGTYPE else 0
            output.addfile(member, io.BytesIO(body))
    return raw.getvalue()


def test_offline_requires_exact_bytes(tmp_path):
    name = "json.hpp"
    (tmp_path / name).write_bytes(b"wrong")
    with pytest.raises(ValueError, match="digest mismatch"):
        prepare.acquire(name, tmp_path, False)
    with pytest.raises(ValueError, match="Supply the verified"):
        prepare.acquire(name, tmp_path / "missing", False)


@pytest.mark.parametrize(
    "name,kind", [("prefix/../../escape", tarfile.REGTYPE), ("prefix/link", tarfile.SYMTYPE)]
)
def test_reject_unsafe_member(tmp_path, name, kind):
    with pytest.raises(ValueError, match="Unexpected"):
        prepare.extract_headers(archive([(name, b"x", kind)]), "prefix/", tmp_path / "out", 8)
    assert not (tmp_path / "escape").exists()


def test_reject_duplicate_and_count(tmp_path):
    entries = [("prefix/a", b"x", tarfile.REGTYPE), ("prefix/a", b"y", tarfile.REGTYPE)]
    with pytest.raises(ValueError, match="Unexpected"):
        prepare.extract_headers(archive(entries), "prefix/", tmp_path / "duplicate", 8)
    entries[1] = ("prefix/b", b"y", tarfile.REGTYPE)
    with pytest.raises(ValueError, match="bounds"):
        prepare.extract_headers(archive(entries), "prefix/", tmp_path / "count", 1)


def test_exact_extraction(tmp_path):
    prepare.extract_headers(
        archive([("prefix/sub/a", b"original", tarfile.REGTYPE)]), "prefix/", tmp_path / "out", 8
    )
    assert (tmp_path / "out/sub/a").read_bytes() == b"original"


def test_fresh_preparation_preserves_existing(tmp_path):
    sentinel = tmp_path / "sentinel"
    sentinel.write_text("preserve")
    with pytest.raises(ValueError, match="fresh"):
        prepare.prepare(tmp_path, None, False)
    assert sentinel.read_text() == "preserve"


def test_inventory_rejects_symlinks(tmp_path):
    (tmp_path / "source").write_text("original")
    (tmp_path / "alias").symlink_to(tmp_path / "source")
    with pytest.raises(ValueError, match="symlinks"):
        inventory(tmp_path)


def test_build_receipt_tampering_cannot_keep_identity():
    from build_native import BUILD_FIELDS, source_build_id

    original = {key: {} for key in BUILD_FIELDS}
    original["native_source"] = {"model.cpp": "original"}
    bound = source_build_id(original)
    receipt = {
        **original,
        "build_id": bound,
        "binary_sha256": "x",
        "compiled": True,
        "native_math_checks": True,
        "spark_execution": False,
    }
    assert source_build_id(receipt) == bound
    receipt["native_source"] = {"model.cpp": "changed"}
    assert source_build_id(receipt) != bound
    receipt["undeclared"] = "ignored?"
    with pytest.raises(ValueError, match="fields differ"):
        source_build_id(receipt)


def test_assemble_refuses_changed_provenance_before_creating_output(tmp_path, monkeypatch):
    import json

    import assemble
    from build_native import BUILD_FIELDS, source_build_id

    receipt = {key: {} for key in BUILD_FIELDS}
    receipt["flags"] = ["-O1"]
    receipt["build_id"] = source_build_id(receipt)
    receipt.update(
        binary_sha256="0" * 64, compiled=True, native_math_checks=True, spark_execution=False
    )
    receipt["flags"] = ["-O3"]
    native = tmp_path / "native"
    native.mkdir()
    (native / "build.json").write_text(json.dumps(receipt))
    out = tmp_path / "assembled"
    monkeypatch.setattr(assemble.platform, "system", lambda: "Linux")
    monkeypatch.setattr(assemble.platform, "machine", lambda: "aarch64")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "assemble",
            "--native-build",
            str(native),
            "--sdk",
            str(tmp_path / "sdk"),
            "--jar",
            str(tmp_path / "unread.jar"),
            "--output",
            str(out),
        ],
    )
    with pytest.raises(ValueError, match="reproduce its build identity"):
        assemble.main()
    assert not out.exists()
