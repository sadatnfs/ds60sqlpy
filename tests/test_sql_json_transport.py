"""Independent JSON value and transaction-outcome regressions for SQL_WORKER."""

from __future__ import annotations

import io
import json
import math
import shutil
import subprocess
import sys
from collections.abc import Callable
from contextlib import redirect_stdout
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from types import ModuleType, SimpleNamespace, TracebackType
from typing import Any, Literal, NoReturn, Protocol, Self, TypedDict, cast

import pytest

from ds60sqlpy.execution import COURSE_ROLE_QUERY, SQL_WORKER


class JsonText(str):
    pass


class DatabaseFailure(Exception):
    sqlstate: str | None = "22012"
    diag: SimpleNamespace | None = SimpleNamespace(statement_position="1")


class OperationalFailure(DatabaseFailure):
    sqlstate: str | None = None
    diag: SimpleNamespace | None = None


JsonLoader = Callable[[str], Any]


class CursorContract(Protocol):
    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        kind: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]: ...

    def execute(self, query: str, *, prepare: bool) -> None: ...

    @property
    def description(self) -> list[SimpleNamespace] | None: ...

    @property
    def statusmessage(self) -> str: ...

    def fetchmany(self, size: int) -> list[tuple[Any, ...]]: ...

    def nextset(self) -> bool: ...


class WorkerFailures(TypedDict, total=False):
    failure: Exception
    commit_failure: Exception


class Connection:
    def __init__(
        self,
        result_sets: list[dict[str, Any]],
        failure: Exception | None = None,
        commit_failure: Exception | None = None,
    ) -> None:
        self.info = SimpleNamespace(dbname="advanced_sql_training", backend_pid=1234)
        self.result_sets = result_sets
        self.failure = failure
        self.commit_failure = commit_failure
        self.committed = False
        self.rolled_back = False
        self.executions: list[tuple[str, bool]] = []
        self.fetch_sizes: list[int] = []
        self.metadata_queries: list[str] = []
        self.index = 0
        self.json_loader: JsonLoader | None = None

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        if kind is None and self.commit_failure is not None:
            raise self.commit_failure
        self.committed = kind is None
        self.rolled_back = kind is not None
        return False

    def execute(self, query: str) -> SimpleNamespace:
        self.metadata_queries.append(query)
        if query == COURSE_ROLE_QUERY:
            return SimpleNamespace(fetchone=lambda: (False,))
        assert (
            query.strip()
            == "SELECT backend_start::text FROM pg_stat_activity WHERE pid=pg_backend_pid()"
        )
        return SimpleNamespace(fetchone=lambda: ("2026-01-01 00:00:00+00",))

    def cursor(self) -> CursorContract:
        owner = self

        class Cursor:
            def __enter__(self) -> Self:
                return self

            def __exit__(
                self,
                kind: type[BaseException] | None,
                value: BaseException | None,
                traceback: TracebackType | None,
            ) -> Literal[False]:
                return False

            def execute(self, query: str, *, prepare: bool) -> None:
                owner.executions.append((query, prepare))
                if owner.failure is not None:
                    raise owner.failure

            @property
            def description(self) -> list[SimpleNamespace] | None:
                result = owner.result_sets[owner.index]
                return (
                    [SimpleNamespace(name=name) for name in result["columns"]]
                    if "columns" in result
                    else None
                )

            @property
            def statusmessage(self) -> str:
                return cast(str, owner.result_sets[owner.index]["status"])

            def fetchmany(self, size: int) -> list[tuple[Any, ...]]:
                owner.fetch_sizes.append(size)
                return [
                    tuple(
                        cast(JsonLoader, owner.json_loader)(value)
                        if isinstance(value, JsonText)
                        else value
                        for value in row
                    )
                    for row in owner.result_sets[owner.index]["rows"][:size]
                ]

            def nextset(self) -> bool:
                owner.index += 1
                return owner.index < len(owner.result_sets)

        return Cursor()


class ConnectContract(Protocol):
    def __call__(self, target: str, *, options: str) -> Connection: ...


class SetJsonLoadsContract(Protocol):
    def __call__(self, callback: JsonLoader, *, context: Connection) -> None: ...


class PsycopgModule(ModuleType):
    Error: type[DatabaseFailure]
    connect: ConnectContract


class JsonModule(ModuleType):
    set_json_loads: SetJsonLoadsContract


def worker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    rows: list[tuple[Any, ...]],
    *,
    result_sets: list[dict[str, Any]] | None = None,
    failure: Exception | None = None,
    commit_failure: Exception | None = None,
) -> SimpleNamespace:
    if result_sets is None:
        result_sets = [{"columns": [f"c{index}" for index in range(len(rows[0]))], "rows": rows}]
    connection = Connection(result_sets, failure, commit_failure)
    module = PsycopgModule("psycopg")
    module.Error = DatabaseFailure
    module.__path__ = []
    types_module = ModuleType("psycopg.types")
    types_module.__path__ = []
    json_module = JsonModule("psycopg.types.json")

    def set_json_loads(callback: JsonLoader, *, context: Connection) -> None:
        assert context is connection
        context.json_loader = callback

    json_module.set_json_loads = set_json_loads
    monkeypatch.setitem(sys.modules, "psycopg.types", types_module)
    monkeypatch.setitem(sys.modules, "psycopg.types.json", json_module)
    calls: list[bool] = []

    def connect(target: str, *, options: str) -> Connection:
        assert target == ""
        assert options == "-c statement_timeout=5000 -c lock_timeout=2000"
        calls.append(True)
        return connection

    module.connect = connect
    monkeypatch.setitem(sys.modules, "psycopg", module)
    query = tmp_path / "query.sql"
    query.write_text("SELECT constants;", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["sql-worker", str(query)])
    monkeypatch.setenv("DS60_PAD_BACKEND_PID", str(tmp_path / "backend.pid"))
    monkeypatch.setenv("DS60_PAD_BACKEND_START", str(tmp_path / "backend.start"))
    output = io.StringIO()
    status: int | str | None = 0
    with redirect_stdout(output):
        try:
            exec(compile(SQL_WORKER, "<SQL_WORKER>", "exec"), {"__name__": "__main__"})
        except SystemExit as error:
            status = error.code
    raw = output.getvalue()

    def reject_constant(value: str) -> NoReturn:
        raise AssertionError(f"Nonstandard JSON constant {value}")

    payload = json.loads(raw, parse_constant=reject_constant)
    assert len(calls) == 1
    assert connection.executions == [("SELECT constants;", False)]
    assert connection.metadata_queries[0] == COURSE_ROLE_QUERY
    return SimpleNamespace(status=status, payload=payload, raw=raw, connection=connection)


def test_safe_integer_boundaries_bools_null_and_nested_values_are_exact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    safe = 2**53 - 1
    nested: dict[str, Any] = {
        "integer": 9007199254740993,
        "negative": -9007199254740993,
        "array": [True, False, None, {"deep": (safe, safe + 1, -safe - 1)}],
    }
    original = [(None, True, False, "", -safe, safe, safe + 1, -safe - 1, 9007199254740993, nested)]
    result = worker(tmp_path, monkeypatch, original)
    assert result.status == 0 and result.connection.committed
    assert result.payload["results"][0]["rows"] == [
        [
            None,
            True,
            False,
            "",
            -9007199254740991,
            9007199254740991,
            "9007199254740992",
            "-9007199254740992",
            "9007199254740993",
            {
                "integer": "9007199254740993",
                "negative": "-9007199254740993",
                "array": [
                    True,
                    False,
                    None,
                    {"deep": [9007199254740991, "9007199254740992", "-9007199254740992"]},
                ],
            },
        ]
    ]
    assert type(result.payload["results"][0]["rows"][0][1]) is bool
    assert type(result.payload["results"][0]["rows"][0][5]) is int
    assert nested["integer"] == 9007199254740993 and type(nested["integer"]) is int
    assert isinstance(nested["array"][-1]["deep"], tuple)


def test_float_values_and_nested_nonfinite_values_use_strict_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = worker(
        tmp_path,
        monkeypatch,
        [
            (
                0.5,
                -0.0,
                1e308,
                5e-324,
                float("nan"),
                float("inf"),
                float("-inf"),
                {"floats": [float("nan"), (float("inf"), float("-inf"))]},
            )
        ],
    )
    row = result.payload["results"][0]["rows"][0]
    assert row == [
        0.5,
        -0.0,
        1e308,
        5e-324,
        "NaN",
        "Infinity",
        "-Infinity",
        {"floats": ["NaN", ["Infinity", "-Infinity"]]},
    ]
    assert math.copysign(1, row[1]) == -1
    assert all(type(value) is float for value in row[:4])
    assert result.connection.committed and result.status == 0


def test_decimal_and_date_time_fallbacks_preserve_existing_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    values = (
        Decimal("12345678901234567890.00100"),
        Decimal("NaN"),
        date(2024, 2, 29),
        time(12, 3, 4),
        datetime(2024, 2, 29, 12, 3, 4, tzinfo=timezone(timedelta(hours=5, minutes=30))),
    )
    result = worker(tmp_path, monkeypatch, [values])
    assert result.payload["results"][0]["rows"] == [
        ["12345678901234567890.00100", "NaN", "2024-02-29", "12:03:04", "2024-02-29 12:03:04+05:30"]
    ]


def test_result_set_status_order_and_existing_101_to_100_bound_stay_intact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sets: list[dict[str, Any]] = [
        {"status": "SET"},
        {"columns": ["n"], "rows": [(value,) for value in range(101)]},
        {"columns": ["big"], "rows": [(9007199254740993,)]},
    ]
    result = worker(tmp_path, monkeypatch, [], result_sets=sets)
    assert result.payload["results"][0] == {"status": "SET"}
    assert result.payload["results"][1] == {
        "columns": ["n"],
        "rows": [[value] for value in range(100)],
        "truncated": True,
    }
    assert result.payload["results"][2] == {
        "columns": ["big"],
        "rows": [["9007199254740993"]],
        "truncated": False,
    }
    assert result.connection.fetch_sizes == [101, 101]
    assert (
        result.payload["transaction"]
        == "Committed success; explicit COMMIT/ROLLBACK change boundaries."
    )


class Unrepresentable:
    def __str__(self) -> str:
        raise RuntimeError("This value must not be interpolated into an error response")


@pytest.mark.parametrize("kind", ["string-fallback", "dictionary-key", "cycle"])
def test_format_failure_after_commit_never_claims_rollback_or_replays(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    value: Any
    if kind == "string-fallback":
        value = Unrepresentable()
    elif kind == "dictionary-key":
        value = {("invalid", "key"): "value"}
    else:
        value = []
        value.append(value)
    result = worker(tmp_path, monkeypatch, [(value,)])
    assert result.status == 1 and result.connection.committed and not result.connection.rolled_back
    assert set(result.payload) == {"error_type", "sqlstate", "error_line", "message", "transaction"}
    assert result.payload["sqlstate"] is None and result.payload["error_line"] is None
    assert "committed" in result.payload["message"]
    assert "could not be represented" in result.payload["message"]
    assert "Do not automatically rerun" in result.payload["message"]
    assert "rolled back" not in result.payload["transaction"].lower()
    assert "must not be interpolated" not in result.raw
    assert result.connection.executions == [("SELECT constants;", False)]


def test_query_failure_still_reports_current_rollback_and_previous_explicit_commits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = worker(tmp_path, monkeypatch, [(1,)], failure=DatabaseFailure("division by zero"))
    assert result.status == 1 and result.connection.rolled_back and not result.connection.committed
    assert result.payload["sqlstate"] == "22012" and result.payload["error_line"] == 1
    assert (
        result.payload["transaction"]
        == "Current transaction rolled back; earlier explicit commits are preserved."
    )
    assert result.payload["message"] == "division by zero"


def test_actual_javascript_json_parse_retains_nested_values_and_types(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for the actual JavaScript JSON.parse check")
    result = worker(
        tmp_path,
        monkeypatch,
        [
            (
                9007199254740993,
                -9007199254740993,
                True,
                9007199254740991,
                -0.0,
                {
                    "array": [
                        9007199254740993,
                        {"n": float("nan"), "p": float("inf"), "m": float("-inf")},
                    ]
                },
            )
        ],
    )
    program = r"""
const raw = require('node:fs').readFileSync(0, 'utf8');
const row = JSON.parse(raw).results[0].rows[0];
const assert = require('node:assert/strict');
assert.equal(row[0], '9007199254740993');
assert.equal(row[1], '-9007199254740993');
assert.equal(typeof row[0], 'string');
assert.equal(typeof row[2], 'boolean');
assert.equal(row[2], true);
assert.equal(typeof row[3], 'number');
assert.equal(row[3], 9007199254740991);
assert.ok(Object.is(row[4], -0));
assert.equal(row[5].array[0], '9007199254740993');
assert.deepEqual(row[5].array[1], {n:'NaN', p:'Infinity', m:'-Infinity'});
for (const bad of ['{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}']) {
  assert.throws(() => JSON.parse(bad), SyntaxError);
}
process.stdout.write('Strict JSON.parse transport checks passed.\n');
"""
    parsed = subprocess.run(
        [node, "-e", program], input=result.raw, capture_output=True, text=True, timeout=10
    )
    assert parsed.returncode == 0, parsed.stderr
    assert parsed.stdout == "Strict JSON.parse transport checks passed.\n"


def test_connection_local_json_numeric_decoder_retains_only_lossy_values_as_exact_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw = JsonText(
        '{"precise":0.100000000000000000001,"ordinary":[0.1,0.5],"underflow":1e-400,"overflow":1e400,"zero":-0.0,"integer":7,"nested":{"negative":-0.100000000000000000001}}'
    )
    result = worker(tmp_path, monkeypatch, [(raw,)])
    decoded = result.payload["results"][0]["rows"][0][0]
    assert decoded == {
        "precise": "0.100000000000000000001",
        "ordinary": [0.1, 0.5],
        "underflow": "1E-400",
        "overflow": "1E+400",
        "zero": -0.0,
        "integer": 7,
        "nested": {"negative": "-0.100000000000000000001"},
    }
    assert all(type(value) is float for value in decoded["ordinary"])
    assert type(decoded["integer"]) is int
    assert math.copysign(1, decoded["zero"]) == -1
    assert json.loads(raw)["precise"] == 0.1
    assert type(json.loads(raw)["precise"]) is float
    assert result.connection.json_loader is not None


@pytest.mark.parametrize(
    "phase", ["statement-connection-loss", "commit-connection-loss", "sqlstate-connection-class"]
)
def test_unconfirmed_connection_or_commit_outcomes_never_claim_rollback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str
) -> None:
    error = OperationalFailure("private connection detail must not appear")
    if phase == "sqlstate-connection-class":
        error.sqlstate = "08006"
    arguments: WorkerFailures = (
        {"commit_failure": error} if phase == "commit-connection-loss" else {"failure": error}
    )
    result = worker(tmp_path, monkeypatch, [(1,)], **arguments)
    assert result.status == 1
    assert "outcome is unknown" in result.payload["transaction"]
    assert "Do not automatically rerun" in result.payload["transaction"]
    assert "Current transaction rolled back" not in result.payload["transaction"]
    assert "private connection detail" not in result.raw
    assert len(result.connection.executions) == 1


@pytest.mark.parametrize("phase", ["statement", "commit"])
@pytest.mark.parametrize("sqlstate", ["40003", "08007"])
def test_indeterminate_sqlstates_never_claim_confirmed_rollback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str, sqlstate: str
) -> None:
    error = OperationalFailure("private connection detail must not appear")
    error.sqlstate = sqlstate
    arguments: WorkerFailures = (
        {"commit_failure": error} if phase == "commit" else {"failure": error}
    )
    result = worker(tmp_path, monkeypatch, [(1,)], **arguments)
    assert result.status == 1
    assert result.payload["sqlstate"] == sqlstate
    assert result.payload["error_line"] is None
    assert "outcome is unknown" in result.payload["transaction"]
    assert "Do not automatically rerun" in result.payload["transaction"]
    assert "Current transaction rolled back" not in result.payload["transaction"]
    assert result.payload["message"] == (
        "SQL transaction outcome is unknown. "
        "Do not automatically rerun; inspect the database state first."
    )
    assert "private connection detail" not in result.raw
    assert len(result.connection.executions) == 1
    if phase == "commit":
        assert not result.connection.committed and not result.connection.rolled_back
