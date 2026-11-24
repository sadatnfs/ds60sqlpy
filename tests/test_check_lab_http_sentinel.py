"""Exercise the check_lab_http SQL sentinel option against a fake lab API."""

from __future__ import annotations

import json
import sys
from typing import Any

import pytest

from scripts import check_lab_http

NAME = "p7_0123456789ab"
TOKEN = "Abc123Def456Ghi789Jkl012"
SOURCE = "print(6 * 7)"
NOTE = "HTTP smoke fixture; this is not learner mastery."


class Response:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> Response:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self) -> bytes:
        return self.body


def sql_output(rows: list[list[Any]]) -> str:
    return json.dumps({"results": [{"columns": ["c"], "rows": rows, "truncated": False}]})


class FakeLab:
    def __init__(self, sentinel_rows: list[list[Any]] | None = None) -> None:
        self.actions: list[dict[str, Any]] = []
        self.http_calls = 0
        self.pad = SOURCE
        self.sentinel_rows = [[TOKEN]] if sentinel_rows is None else sentinel_rows

    def open(self, target: Any, timeout: float = 0) -> Response:
        self.http_calls += 1
        if isinstance(target, str):
            return Response(b'<script>const SERVER_TOKEN = "session";</script>')
        payload: dict[str, Any] = json.loads(target.data)
        self.actions.append(payload)
        return Response(json.dumps(self.answer(payload)).encode())

    def answer(self, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload["action"]
        if action == "classroom-index":
            tracks = ["python", "sql", "cpp", "java", "javascript-typescript"]
            return {"tracks": [{"id": track} for track in tracks]}
        if action == "paths":
            return {"paths": {"python-foundations": {"targets": ["x"]}}, "lesson_count": 200}
        if action == "plan":
            return {"lessons": [{"id": "python-foundations-01"}]}
        if action == "save-pad":
            self.pad = payload["code"]
            return {}
        if action == "read-pad":
            return {"saved": True, "code": self.pad}
        if action == "pad-history":
            return {"history": [{"id": "h1"}]}
        if action == "read-history":
            return {"code": SOURCE}
        if action == "lesson":
            return {"session": {"read": NOTE}}
        if action == "classroom-history":
            return {"history": [{"id": "r1"}]}
        if action == "classroom-run-result":
            return {"receipt": {"source": SOURCE, "result": {"output": "42"}}}
        if action == "run":
            return self.run(payload)
        return {}

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        code = payload["code"]
        if payload["language"] == "python":
            return {"returncode": 0, "output": "42\n", "receipt_saved": True}
        if code == "SELECT 42 AS answer;":
            return {"returncode": 0, "output": sql_output([[42]])}
        if code == "SELECT current_user;":
            return {"returncode": 0, "output": sql_output([["admin"]])}
        if "pg_read_file" in code:
            return {"returncode": 1, "output": json.dumps({"sqlstate": "42501"})}
        if "training.customers" in code:
            return {"returncode": 0, "output": sql_output([[5]])}
        if code.startswith("CREATE TABLE IF NOT EXISTS"):
            return {"returncode": 0, "output": json.dumps({"results": [{"status": "INSERT 0 1"}]})}
        if code.startswith("SELECT token FROM"):
            return {"returncode": 0, "output": sql_output(self.sentinel_rows)}
        raise AssertionError("unexpected SQL")


def run_main(monkeypatch: pytest.MonkeyPatch, lab: FakeLab, *extra: str) -> int:
    monkeypatch.setattr(check_lab_http, "build_opener", lambda *_: lab)
    argv = ["check_lab_http.py", "--url", "http://127.0.0.1:8765", "--confirm-disposable"]
    monkeypatch.setattr(sys, "argv", [*argv, *extra])
    return check_lab_http.main()


def sentinel_runs(lab: FakeLab) -> list[dict[str, Any]]:
    return [
        item
        for item in lab.actions
        if item["action"] == "run" and "public.p7_" in item.get("code", "")
    ]


@pytest.mark.parametrize(
    "value",
    [
        "p7_ok",
        "x7_name:Abcdefgh1",
        "p7_:Abcdefgh1",
        "p7_Name:Abcdefgh1",
        "p7_name;drop:Abcdefgh1",
        "p7_" + "a" * 41 + ":Abcdefgh1",
        "p7_name:short1",
        "p7_name:has'quote1",
        "p7_name:" + "a" * 65,
    ],
)
def test_invalid_sentinel_is_rejected_before_any_http(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    lab = FakeLab()
    with pytest.raises(SystemExit) as raised:
        run_main(monkeypatch, lab, "--sql-sentinel", value)
    assert raised.value.code == 2
    assert lab.http_calls == 0


def test_seed_creates_sentinel_table_as_learner_sql(monkeypatch: pytest.MonkeyPatch) -> None:
    lab = FakeLab()
    assert run_main(monkeypatch, lab, "--sql-sentinel", f"{NAME}:{TOKEN}") == 0
    runs = sentinel_runs(lab)
    assert len(runs) == 1
    assert runs[0]["lesson_id"] == "sql-start-01" and runs[0]["language"] == "sql"
    code = runs[0]["code"]
    assert f"CREATE TABLE IF NOT EXISTS public.{NAME} (token text primary key);" in code
    assert f"INSERT INTO public.{NAME} (token) VALUES ('{TOKEN}') ON CONFLICT DO NOTHING;" in code


def test_persistence_requires_exactly_the_sentinel_row(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    lab = FakeLab()
    assert (
        run_main(monkeypatch, lab, "--check-persistence", "--sql-sentinel", f"{NAME}:{TOKEN}") == 0
    )
    runs = sentinel_runs(lab)
    assert [item["code"] for item in runs] == [f"SELECT token FROM public.{NAME} ORDER BY token;"]
    output = capsys.readouterr().out
    assert "SQL sentinel survived." in output
    assert TOKEN not in output


@pytest.mark.parametrize("rows", [[], [["other1234"]], [[TOKEN], [TOKEN + "x"]]])
def test_persistence_fails_when_sentinel_row_is_lost(
    monkeypatch: pytest.MonkeyPatch, rows: list[list[Any]]
) -> None:
    lab = FakeLab(sentinel_rows=rows)
    with pytest.raises(RuntimeError, match="SQL sentinel"):
        run_main(monkeypatch, lab, "--check-persistence", "--sql-sentinel", f"{NAME}:{TOKEN}")


def test_absent_option_keeps_existing_behavior(monkeypatch: pytest.MonkeyPatch) -> None:
    lab = FakeLab()
    assert run_main(monkeypatch, lab) == 0
    assert sentinel_runs(lab) == []
