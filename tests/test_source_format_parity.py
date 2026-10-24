"""Formatting evidence must independently reject behavior-changing edits."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.source_format_parity import (
    code_tokens,
    create_record,
    semantic_sha256,
    source_digest_before_formatting,
    verify_record,
)


def test_python_receipt_preserves_strings_and_rejects_forged_current_digest() -> None:
    original = b"def value(x):\n return x+1\n"
    styled = b"def value(x):\n    return x + 1\n"
    record = create_record("example.py", original, styled)
    assert verify_record(record, styled) == hashlib.sha256(original).hexdigest()
    changed = styled.replace(b"x + 1", b"x + 2")
    with pytest.raises(ValueError, match="Python syntax"):
        create_record("example.py", original, changed)
    forged = {**record, "formatted_sha256": hashlib.sha256(changed).hexdigest()}
    with pytest.raises(ValueError, match="Python syntax"):
        verify_record(forged, changed)
    with pytest.raises(ValueError, match="original bytes"):
        verify_record({**record, "historical_sha256": "0" * 64}, styled)
    assert semantic_sha256(b'value = "a b"') != semantic_sha256(b'value = "ab"')


def test_receipt_lookup_retains_exact_historical_identity(tmp_path: Path) -> None:
    original = b"value=1\n"
    current = b"value = 1\n"
    (tmp_path / "curriculum").mkdir()
    record = create_record("example.py", original, current)
    payload = {
        "schema_version": 1,
        "evidence_kind": "python_ast_formatting_parity",
        "records": [record],
    }
    target = tmp_path / "curriculum/source-format-parity.json"
    target.write_text(json.dumps(payload))
    assert (
        source_digest_before_formatting(tmp_path, "example.py", current)
        == hashlib.sha256(original).hexdigest()
    )
    payload["records"].append(record)
    target.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="Duplicate"):
        source_digest_before_formatting(tmp_path, "example.py", current)


def test_lexical_pairing_preserves_operator_and_literal_boundaries() -> None:
    assert code_tokens("int main(){/* explanation */return 1 + 2;}") == code_tokens(
        "int main() { return 1+2; }"
    )
    assert code_tokens("a + +b") != code_tokens("a++ + b")
    assert code_tokens('write("a b")') != code_tokens('write("ab")')
    assert code_tokens('write("// literal")') != code_tokens('write("literal")')
    assert code_tokens('auto s=R"x(a b)x";') != code_tokens('auto s=R"x(ab)x";')
    assert code_tokens("#define A 1\n+B") != code_tokens("#define A 1+B\n")
    with pytest.raises(ValueError, match="Unterminated"):
        code_tokens("int a; /*")


def test_published_parity_receipts_revalidate_original_and_current_sources() -> None:
    root = Path(__file__).resolve().parents[1]
    payload = json.loads((root / "curriculum/source-format-parity.json").read_text())
    assert payload["evidence_kind"] == "python_ast_formatting_parity"
    records = payload["records"]
    assert records and len({record["path"] for record in records}) == len(records)
    for record in records:
        assert (
            verify_record(record, (root / record["path"]).read_bytes())
            == record["historical_sha256"]
        )
