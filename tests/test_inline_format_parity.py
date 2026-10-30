"""Inline parity preserves historical evidence and rejects forged formatting claims."""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import zlib
from pathlib import Path
from typing import Any

import pytest

from scripts import source_format_parity as parity

BEFORE = (
    b'Prose \\(x^2\\).\n```python title=case\n# exact  comment\nx={"value":1}\n```\nExpected one.\n'
)
AFTER = (
    b"Prose \\(x^2\\).\n```python title=case\n# exact  comment\n"
    b'x = {"value": 1}\n```\nExpected one.\n'
)
PATH = "courses/example/guides/example-001.md"


def receipt(root: Path, records: list[dict[str, Any]]) -> Path:
    path = root / parity.INLINE_RECEIPT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema_version": 1, "evidence_kind": parity.INLINE_KIND, "records": records})
    )
    return path


def test_inline_record_reconstructs_exact_guide_and_ordered_block_proof() -> None:
    record = parity.create_inline_record(PATH, BEFORE, AFTER)
    assert parity.verify_inline_record(record, AFTER) == BEFORE
    assert record["historical_sha256"] == hashlib.sha256(BEFORE).hexdigest()
    assert record["formatted_sha256"] == hashlib.sha256(AFTER).hexdigest()
    assert record["changed_python_blocks"][0]["ordinal"] == 0
    assert len(record["changed_python_blocks"]) == 1


@pytest.mark.parametrize(
    "changed",
    [
        AFTER.replace(b'"value": 1', b'"value": 2'),
        AFTER.replace(b'"value"', b'"different"'),
        AFTER.replace(b"# exact  comment", b"# edited comment"),
        AFTER.replace(b"Prose", b"Different prose"),
        AFTER.replace(b"title=case", b"title=other"),
        AFTER.replace(b"```python", b"```py"),
        AFTER.replace(b"Expected one.", b"Expected two."),
    ],
)
def test_forged_current_hash_cannot_authorize_semantic_prose_or_identity_change(
    changed: bytes,
) -> None:
    record = parity.create_inline_record(PATH, BEFORE, AFTER)
    record["formatted_sha256"] = hashlib.sha256(changed).hexdigest()
    with pytest.raises(ValueError):
        parity.verify_inline_record(record, changed)


def test_type_comments_and_ordered_comment_content_are_significant() -> None:
    before = b"```python\n# first\n# second\nx=[] # type: list[int]\n```\n"
    after = b"```python\n# first\n# second\nx = [] # type: list[int]\n```\n"
    assert (
        parity.verify_inline_record(parity.create_inline_record(PATH, before, after), after)
        == before
    )
    for changed in (
        after.replace(b"# first\n# second", b"# second\n# first"),
        after.replace(b"list[int]", b"list[str]"),
    ):
        with pytest.raises(ValueError):
            parity.create_inline_record(PATH, before, changed)


@pytest.mark.parametrize("tag", ["text", "java", "sh", "json"])
def test_other_protected_blocks_are_exact_even_if_change_looks_like_layout(tag: str) -> None:
    before = BEFORE + f"```{tag}\na  b\n```\n".encode()
    after = AFTER + f"```{tag}\na b\n```\n".encode()
    with pytest.raises(ValueError, match="byte-identical"):
        parity.create_inline_record(PATH, before, after)


def test_unchanged_non_python_block_can_be_retained_in_a_python_binding() -> None:
    suffix = b"```text\nExpected   exact output\n```\n"
    record = parity.create_inline_record(PATH, BEFORE + suffix, AFTER + suffix)
    assert parity.verify_inline_record(record, AFTER + suffix) == BEFORE + suffix


def test_unclosed_fence_and_fence_count_change_are_rejected() -> None:
    with pytest.raises(ValueError, match="byte-identical"):
        parity.create_inline_record(PATH, b"```python\nx=1\n", b"```python\nx = 1\n")
    with pytest.raises(ValueError, match="fence identities"):
        parity.create_inline_record(PATH, BEFORE, AFTER + b"```python\ny = 2\n```\n")


def test_forged_original_or_proof_digest_is_rejected() -> None:
    original = parity.create_inline_record(PATH, BEFORE, AFTER)
    for field in ("historical_sha256", "formatted_sha256"):
        changed = {**original, field: "0" * 64}
        with pytest.raises(ValueError):
            parity.verify_inline_record(changed, AFTER)
    changed = copy.deepcopy(original)
    changed["changed_python_blocks"][0]["semantic_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="independently computed"):
        parity.verify_inline_record(changed, AFTER)


def test_duplicate_block_bindings_and_unknown_metadata_are_rejected() -> None:
    record = parity.create_inline_record(PATH, BEFORE, AFTER)
    duplicated = copy.deepcopy(record)
    duplicated["changed_python_blocks"].append(duplicated["changed_python_blocks"][0])
    with pytest.raises(ValueError, match="Duplicate"):
        parity.verify_inline_record(duplicated, AFTER)
    with pytest.raises(ValueError, match="Malformed"):
        parity.verify_inline_record({**record, "execution_passed": True}, AFTER)


@pytest.mark.parametrize("payload", ["not base64!", base64.b64encode(b"invalid zlib").decode()])
def test_malformed_compressed_source_is_rejected(payload: str) -> None:
    record = parity.create_inline_record(PATH, BEFORE, AFTER)
    record["original_zlib_base64"] = payload
    with pytest.raises(ValueError, match="compressed"):
        parity.verify_inline_record(record, AFTER)


def test_trailing_compressed_stream_is_not_ignored() -> None:
    record = parity.create_inline_record(PATH, BEFORE, AFTER)
    raw = base64.b64decode(record["original_zlib_base64"]) + zlib.compress(b"hidden extra source")
    record["original_zlib_base64"] = base64.b64encode(raw).decode()
    with pytest.raises(ValueError, match="stream bound"):
        parity.verify_inline_record(record, AFTER)


def test_compressed_expansion_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    record = parity.create_inline_record(PATH, BEFORE, AFTER)
    monkeypatch.setattr(parity, "MAX_INLINE_GUIDE", len(AFTER) + 1)
    record["original_zlib_base64"] = base64.b64encode(zlib.compress(b"x" * 100_000)).decode()
    with pytest.raises(ValueError, match="bound"):
        parity.verify_inline_record(record, AFTER)


def test_lookup_verifies_historical_hash_and_missing_bindings_fail(tmp_path: Path) -> None:
    expected = hashlib.sha256(BEFORE).hexdigest()
    with pytest.raises(ValueError, match="Missing"):
        parity.markdown_before_formatting(tmp_path, PATH, AFTER, expected_sha256=expected)
    target = receipt(tmp_path, [parity.create_inline_record(PATH, BEFORE, AFTER)])
    assert (
        parity.markdown_before_formatting(tmp_path, PATH, AFTER, expected_sha256=expected) == BEFORE
    )
    target.unlink()
    with pytest.raises(ValueError, match="Missing"):
        parity.markdown_before_formatting(tmp_path, PATH, AFTER, expected_sha256=expected)
    assert (
        parity.markdown_before_formatting(tmp_path, PATH, BEFORE, expected_sha256=expected)
        == BEFORE
    )


def test_duplicate_receipts_and_duplicate_json_keys_fail(tmp_path: Path) -> None:
    record = parity.create_inline_record(PATH, BEFORE, AFTER)
    target = receipt(tmp_path, [record, record])
    with pytest.raises(ValueError, match="Duplicate"):
        parity.load_inline_records(tmp_path)
    target.write_text('{"schema_version":1,"schema_version":1,"evidence_kind":"x","records":[]}')
    with pytest.raises(ValueError, match="Duplicate"):
        parity.load_inline_records(tmp_path)


@pytest.mark.parametrize(
    "path", ["../escape.md", "/absolute.md", "a//b.md", "a\\b.md", "source.py"]
)
def test_unsafe_inline_paths_are_rejected(path: str) -> None:
    with pytest.raises(ValueError, match="safe relative"):
        parity.create_inline_record(path, BEFORE, AFTER)


def test_inline_proof_does_not_execute_its_program(tmp_path: Path) -> None:
    marker = tmp_path / "must-not-exist"
    before = (
        "```python\nfrom pathlib import Path\nPath("
        + repr(str(marker))
        + ').write_text("executed")\nx=1\n```\n'
    ).encode()
    after = before.replace(b"x=1", b"x = 1")
    record = parity.create_inline_record(PATH, before, after)
    assert parity.verify_inline_record(record, after) == before
    assert not marker.exists()


def test_receipt_symlink_and_size_bound_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = receipt(tmp_path, [])
    monkeypatch.setattr(parity, "MAX_INLINE_RECEIPT", 1)
    with pytest.raises(ValueError, match="byte bound"):
        parity.load_inline_records(tmp_path)
    target.unlink()
    target.symlink_to(tmp_path / "elsewhere")
    with pytest.raises(ValueError, match="symlink"):
        parity.load_inline_records(tmp_path)


def test_receipt_bounds_actual_read_even_when_stat_size_is_stale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from types import SimpleNamespace

    target = receipt(tmp_path, [parity.create_inline_record(PATH, BEFORE, AFTER)])
    original_stat = Path.stat
    mode = target.stat().st_mode

    def stale(path: Path, *args: Any, **kwargs: Any) -> Any:
        return (
            SimpleNamespace(st_size=1, st_mode=mode)
            if path == target
            else original_stat(path, *args, **kwargs)
        )

    monkeypatch.setattr(Path, "stat", stale)
    monkeypatch.setattr(parity, "MAX_INLINE_RECEIPT", 128)
    with pytest.raises(ValueError, match="byte bound"):
        parity.load_inline_records(tmp_path)


def test_type_ignore_cannot_move_to_a_different_statement() -> None:
    before = b"```python\na=missing # type: ignore[name-defined]\nb=missing\n```\n"
    after = b"```python\na = missing\nb = missing # type: ignore[name-defined]\n```\n"
    with pytest.raises(ValueError, match="syntax"):
        parity.create_inline_record(PATH, before, after)


def test_snapshot_collector_preserves_first_historical_bytes_and_never_writes_source(
    tmp_path: Path,
) -> None:
    from scripts import record_inline_format_parity as collector

    root, old = tmp_path / "current", tmp_path / "before"
    for directory, data in ((root, AFTER), (old, BEFORE)):
        target = directory / PATH
        target.parent.mkdir(parents=True)
        target.write_bytes(data)
    payload = collector.collect(root, old, [PATH])
    collector.publish(root, root / parity.INLINE_RECEIPT, payload)
    assert collector.verify(root) == 1
    second = AFTER.replace(b'x = {"value": 1}', b'x = {\n    "value": 1,\n}')
    (old / PATH).write_bytes(AFTER)
    (root / PATH).write_bytes(second)
    updated = collector.collect(root, old, [PATH])
    assert parity.verify_inline_record(updated["records"][0], second) == BEFORE
    assert (old / PATH).read_bytes() == AFTER and (root / PATH).read_bytes() == second
    with pytest.raises(ValueError, match="unique"):
        collector.collect(root, old, [PATH, PATH])


def test_collector_failure_does_not_replace_existing_receipt(tmp_path: Path) -> None:
    from scripts import record_inline_format_parity as collector

    root, old = tmp_path / "current", tmp_path / "before"
    for directory, data in ((root, AFTER.replace(b'"value": 1', b'"value": 2')), (old, AFTER)):
        target = directory / PATH
        target.parent.mkdir(parents=True)
        target.write_bytes(data)
    target = receipt(root, [parity.create_inline_record(PATH, BEFORE, AFTER)])
    baseline = target.read_bytes()
    with pytest.raises(ValueError, match="syntax"):
        collector.collect(root, old, [PATH])
    assert target.read_bytes() == baseline


def test_leading_and_later_unattached_type_ignore_scopes_are_distinct() -> None:
    before = b"```python\n# type: ignore[name-defined]\na=missing\nb=missing\n```\n"
    after = b"```python\na = missing\n# type: ignore[name-defined]\nb = missing\n```\n"
    with pytest.raises(ValueError, match="syntax"):
        parity.create_inline_record(PATH, before, after)


def test_type_ignore_attachment_survives_multiline_formatting() -> None:
    before = b"```python\na=missing # type: ignore[name-defined]\n```\n"
    after = b"```python\na = (\n    missing\n) # type: ignore[name-defined]\n```\n"
    record = parity.create_inline_record(PATH, before, after)
    assert parity.verify_inline_record(record, after) == before
