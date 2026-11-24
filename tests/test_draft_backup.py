"""Check the browser draft backup helpers using the actual offline JavaScript block."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

ASSET = Path(__file__).parents[1] / "src/ds60sqlpy/assets/classroom.js"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node is an optional developer UI check")

SERVER = {"source": "print(2)\n", "prediction": "two", "explanation": "saved"}


def evaluate(expression: str, **values: Any) -> Any:
    document = ASSET.read_text(encoding="utf-8")
    source = document.split("// BEGIN DRAFT BACKUP PURE HELPERS", 1)[1].split(
        "// END DRAFT BACKUP PURE HELPERS", 1
    )[0]
    program = (
        "const vm = require('node:vm');\n"
        'let input = "";\n'
        "process.stdin.setEncoding('utf8');\n"
        "process.stdin.on('data', chunk => input += chunk);\n"
        "process.stdin.on('end', () => {\n"
        "const value = JSON.parse(input);\n"
        "const sandbox = value.values; vm.createContext(sandbox);\n"
        "vm.runInContext(value.source, sandbox);\n"
        "console.log(JSON.stringify(vm.runInContext(value.expression, sandbox)));\n"
        "});\n"
    )
    result = subprocess.run(
        [str(NODE), "-e", program],
        input=json.dumps({"source": source, "expression": expression, "values": values}),
        text=True,
        capture_output=True,
        timeout=5,
        check=True,
    )
    return json.loads(result.stdout)


def fingerprint(fields: dict[str, Any]) -> str:
    value = evaluate("draftFingerprint(fields)", fields=fields)
    assert isinstance(value, str)
    return value


def decide(backup: Any, server: dict[str, Any] = SERVER) -> str:
    value = evaluate("backupDecision(backup, server)", backup=backup, server=server)
    assert isinstance(value, str)
    return value


def test_fingerprint_is_stable_lowercase_hex_and_detects_change() -> None:
    first = fingerprint({"source": "a"})
    assert first == fingerprint({"source": "a"})
    assert first == first.lower()
    int(first, 16)
    assert first != fingerprint({"source": "b"})


def test_missing_or_malformed_backup_is_ignored() -> None:
    assert decide(None) == "none"
    assert decide({"source": 3, "prediction": "", "explanation": ""}) == "none"
    assert decide({"source": "x" * 2_000_001, "prediction": "", "explanation": ""}) == "none"


def test_backup_equal_to_server_draft_is_discarded() -> None:
    backup = {**SERVER, "stash_meta": {"base_sha256": "old", "saved_at": "2026-01-01"}}
    assert decide(backup) == "discard"


def test_backup_based_on_the_loaded_server_draft_restores() -> None:
    backup = {
        "source": "print(3)\n",
        "prediction": "three",
        "explanation": "newer",
        "stash_meta": {"base_sha256": fingerprint(SERVER), "saved_at": "2026-01-01"},
    }
    assert decide(backup) == "restore"


def test_backup_with_another_base_or_no_fingerprint_is_a_conflict() -> None:
    fields = {"source": "print(3)\n", "prediction": "three", "explanation": "older"}
    other = {**SERVER, "source": "print(1)\n"}
    assert decide({**fields, "stash_meta": {"base_sha256": fingerprint(other)}}) == "conflict"
    assert decide(fields) == "conflict"
    assert decide({**fields, "stash_meta": None}) == "conflict"
