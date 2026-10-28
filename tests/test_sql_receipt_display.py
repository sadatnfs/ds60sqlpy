"""Historical SQL table views must not rewrite or replay validated receipts."""

from __future__ import annotations

import json
import shutil
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any, NoReturn

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.classroom import ClassroomService

ROOT = Path(__file__).resolve().parents[1]


def stored(
    tmp_path: Path,
    output: str,
    *,
    language: str = "sql",
    mode: str = "snippet",
    extras: dict[str, Any] | None = None,
) -> tuple[ClassroomService, dict[str, Any], Path, dict[str, Any], list[dict[str, Any]]]:
    calls: list[dict[str, Any]] = []

    def dispatch(payload: dict[str, Any]) -> NoReturn:
        calls.append(payload)
        raise AssertionError("Historical reads cannot dispatch execution or save actions")

    service = ClassroomService(Catalog.load(ROOT), dispatch, {}, runs_directory=tmp_path / "runs")
    lesson = "sql-01" if language == "sql" else "python-01"
    result: dict[str, Any] = {
        "language": language,
        "returncode": 0,
        "output": output,
        "elapsed_seconds": 0.125,
        "stopped": None,
        "output_truncated": False,
        "figures": [],
        **(extras or {}),
    }
    receipt = service.runs.record(
        lesson, language, mode, "SELECT 9007199254740993::bigint;", result
    )
    path = next((tmp_path / "runs").rglob("*.json"))
    request = {
        "action": "classroom-run-result",
        "lesson_id": lesson,
        "language": language,
        "mode": mode,
        "receipt_id": receipt["id"],
    }
    return service, receipt, path, request, calls


def table(rows: list[list[Any]], columns: list[str] | None = None) -> str:
    return json.dumps(
        {
            "results": [{"columns": columns or ["value"], "rows": rows, "truncated": False}],
            "transaction": "Committed success; explicit COMMIT/ROLLBACK change boundaries.",
        }
    )


def test_historical_projection_is_exact_derived_and_read_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw = table(
        [
            [
                9007199254740993,
                -9007199254740993,
                {"deep": [9007199254740992, True, None]},
                9007199254740991,
                -9007199254740991,
                0.5,
                "NaN",
                "Infinity",
                "-Infinity",
            ]
        ],
        [
            "positive",
            "negative",
            "nested",
            "safe",
            "negative_safe",
            "float",
            "nan",
            "positive_infinity",
            "negative_infinity",
        ],
    )
    forged = {
        "results": [
            {"columns": ["wrong"], "rows": [["not from the transcript"]], "truncated": False}
        ]
    }
    service, receipt, path, request, calls = stored(tmp_path, raw, extras={"sql_display": forged})
    original = path.read_bytes()

    def forbidden(*args: Any, **kwargs: Any) -> NoReturn:
        raise AssertionError("Readback must not save or overwrite")

    monkeypatch.setattr(service.runs, "record", forbidden)
    monkeypatch.setattr("ds60sqlpy.classroom_runs.atomic_json_write", forbidden)
    response = service.action(request)
    assert response["receipt"] == receipt
    row = response["sql_display"]["results"][0]["rows"][0]
    assert row == [
        "9007199254740993",
        "-9007199254740993",
        {"deep": ["9007199254740992", True, None]},
        9007199254740991,
        -9007199254740991,
        0.5,
        "NaN",
        "Infinity",
        "-Infinity",
    ]
    assert type(row[3]) is int and type(row[5]) is float and type(row[2]["deep"][1]) is bool
    assert response["receipt"]["source"] == receipt["source"]
    assert response["receipt"]["result"]["output"] == raw
    assert response["receipt"]["result"]["returncode"] == 0
    assert response["receipt"]["result"]["sql_display"] == forged
    assert path.read_bytes() == original and not calls
    assert set(path.parent.glob("*.json")) == {path}
    response["sql_display"]["results"][0]["rows"][0][0] = "caller mutation"
    again = service.action(request)
    assert again["sql_display"]["results"][0]["rows"][0][0] == "9007199254740993"
    assert path.read_bytes() == original


@pytest.mark.parametrize(
    "raw",
    [
        "plain psql transcript",
        '{"results":[]}',
        '{"unknown":[],"transaction":"done"}',
        '{"results":[{"columns":["n"],"rows":[[NaN]],"truncated":false}],"transaction":"done"}',
        '{"results":[{"columns":["n"],"rows":[[1e400]],"truncated":false}],"transaction":"done"}',
        '{"results":[{"columns":["n"],"rows":[[0.100000000000000000001]],"truncated":false}],"transaction":"done"}',
        '{"results":[],"results":[],"transaction":"done"}',
        table([[1, 2]]),
        table([[1]] * 101),
    ],
)
def test_unknown_or_lossy_inner_output_remains_raw_only(tmp_path: Path, raw: str) -> None:
    service, receipt, path, request, calls = stored(tmp_path, raw)
    original = path.read_bytes()
    response = service.action(request)
    assert response == {"receipt": receipt, "sql_display": None}
    assert response["receipt"]["result"]["output"] == raw
    assert path.read_bytes() == original and not calls


def test_deep_inner_output_keeps_original_receipt_without_unsafe_table_view(tmp_path: Path) -> None:
    value: Any = 9007199254740993
    for _ in range(40):
        value = [value]
    raw = table([[value]])
    service, receipt, path, request, calls = stored(tmp_path, raw)
    original = path.read_bytes()
    assert service.action(request) == {"receipt": receipt, "sql_display": None}
    assert path.read_bytes() == original and not calls


@pytest.mark.parametrize(("language", "mode"), [("python", "snippet"), ("sql", "lesson")])
def test_python_and_whole_psql_receipts_have_no_derived_table_field(
    tmp_path: Path, language: str, mode: str
) -> None:
    raw = table([[9007199254740993]])
    service, receipt, path, request, calls = stored(tmp_path, raw, language=language, mode=mode)
    original = path.read_bytes()
    assert service.action(request) == {"receipt": receipt}
    assert path.read_bytes() == original and not calls


def test_outer_validation_still_precedes_projection_and_preserves_corrupt_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, receipt, path, request, calls = stored(tmp_path, table([[9007199254740993]]))
    payload = json.loads(path.read_text())
    payload["source_sha256"] = "0" * 64
    path.write_text(json.dumps(payload))
    damaged = path.read_bytes()
    projection_calls: list[dict[str, Any]] = []

    def forbidden(receipt: dict[str, Any]) -> NoReturn:
        projection_calls.append(receipt)
        raise AssertionError("Projection ran before receipt validation")

    monkeypatch.setattr("ds60sqlpy.classroom._sql_display_view", forbidden)
    with pytest.raises(ValueError, match="fingerprint"):
        service.action(request)
    assert path.read_bytes() == damaged and not projection_calls and not calls


def test_plotly_artifacts_and_other_result_metadata_are_not_number_normalized(
    tmp_path: Path,
) -> None:
    artifact = {
        "kind": "plotly",
        "figure": {"data": [{"type": "scatter", "x": [0.1, 0.5], "y": [1.25, 2.75]}], "layout": {}},
    }
    opaque = {"number": 9007199254740993, "finite_float": 1e20}
    service, receipt, path, request, calls = stored(
        tmp_path,
        table([[9007199254740993]]),
        extras={"artifacts": [artifact], "opaque_metadata": opaque},
    )
    expected = deepcopy(receipt["result"])
    original = path.read_bytes()
    response = service.action(request)
    assert response["receipt"]["result"] == expected
    assert response["receipt"]["result"]["opaque_metadata"] == opaque
    assert type(response["receipt"]["result"]["opaque_metadata"]["number"]) is int
    assert response["receipt"]["result"]["artifacts"] == [artifact]
    assert response["sql_display"]["results"][0]["rows"] == [["9007199254740993"]]
    assert path.read_bytes() == original and not calls


def test_javascript_parses_exact_historical_display_values_without_touching_raw_output(
    tmp_path: Path,
) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is needed for real JSON.parse verification")
    raw = table(
        [
            [
                9007199254740993,
                -9007199254740993,
                True,
                0.5,
                "NaN",
                "Infinity",
                "-Infinity",
                {"deep": [9007199254740993]},
            ]
        ],
        ["positive", "negative", "bool", "finite", "nan", "plus", "minus", "nested"],
    )
    service, receipt, path, request, calls = stored(tmp_path, raw)
    response = service.action(request)
    program = r"""
const assert=require('node:assert/strict');
const value=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
const row=value.sql_display.results[0].rows[0];
assert.deepEqual(row,['9007199254740993','-9007199254740993',true,0.5,'NaN','Infinity','-Infinity',{deep:['9007199254740993']}]);
assert.equal(typeof row[0],'string');
assert.equal(typeof row[2],'boolean');
assert.equal(typeof row[3],'number');
assert.match(value.receipt.result.output,/9007199254740993/);
process.stdout.write('Historical SQL projection parsed exactly.\n');
"""
    result = subprocess.run(
        [node, "-e", program],
        input=json.dumps(response),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert not calls
