"""Step-through helpers: a Python line tracer and a SQL clause-by-clause planner.

The worker scripts run in a child process launched by ``PadRunner.step_through``.
Everything else here is pure so the planner and response builders can be tested
without a database or a subprocess.
"""

from __future__ import annotations

import contextlib
import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MAX_STEPS = 400
OUTPUT_CAP = 65_536
RESULT_FILE_CAP = 2_000_000
STEP_BYTES_BUDGET = RESULT_FILE_CAP - 900_000
VALUE_LIMIT = 120
MAX_VARIABLES = 40
MAX_FRAMES = 8
PREVIEW_ROWS = 20
MAX_SQL_STEPS = 40
SQL_CELL_LIMIT = 1_000
SQL_LINE_CAP = 262_144
OUTPUT_NOTICE = "\n[Output stopped here: the program printed more than 64 KB.]\n"
# "auto" prefers sys.monitoring (Python 3.12+); tests set "settrace" to force the fallback.
PYTHON_TRACE_BACKEND = "auto"

NOT_A_QUERY = (
    "Step-through explains SELECT queries. This statement changes data or structure, "
    "so use Run for it."
)
NO_QUERY = "Write a SELECT query, or place the cursor inside one, then choose Step through."
LOCKING_QUERY = (
    "Step-through runs queries read-only, and FOR UPDATE or FOR SHARE needs to lock rows, "
    "so use Run for it."
)
READ_ONLY_STEP = (
    "This step calls something that changes data, and step-through runs read-only, "
    "so use Run to see it work."
)
UNBALANCED = "Check the parentheses in this query, then try Step through again."
UNSUPPORTED_SQL = (
    "Step-through can't split this query into clauses, so use Run for it. "
    "If Run reports an error, check that the clauses are complete and in order: "
    "SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT."
)
SOLUTION_NOT_A_QUERY = (
    "This worked solution changes data or structure and has no SELECT to take apart. "
    "Use Run solution to watch it work."
)
MAX_SQL_CONTEXT = 400
_TX_SAVEPOINT = "ds60_tx"
_SKIPPED_CONTEXT = {
    "ALTER SYSTEM",
    "CHECKPOINT",
    "CLUSTER",
    "COMMIT PREPARED",
    "COPY",
    "CREATE DATABASE",
    "DISCARD",
    "DROP DATABASE",
    "PREPARE TRANSACTION",
    "REINDEX",
    "ROLLBACK PREPARED",
    "SET SESSION",
    "SET TRANSACTION",
    "VACUUM",
}
_GUARDED_SETTINGS = {
    "idle_in_transaction_session_timeout",
    "lock_timeout",
    "statement_timeout",
    "transaction_read_only",
}

_PYTHON_TRACE_BODY = r"""
import io, json, sys, types, warnings, _thread

warnings.filterwarnings(
    'ignore',
    message=r'FigureCanvasAgg is non-interactive, and thus cannot be shown',
    category=UserWarning,
)

SOURCE_PATH, RESULT_PATH, BACKEND = sys.argv[1], sys.argv[2], sys.argv[3]
MAIN_THREAD = _thread.get_ident()
REAL_STDOUT, REAL_STDERR = sys.stdout, sys.stderr
result_file = open(RESULT_PATH, "w", encoding="utf-8")


class StepLimit(BaseException):
    pass


class Sink:
    def __init__(self):
        self.pending = []
        self.size = 0
        self.full = False
        self.paused = False

    def write(self, text):
        if self.paused or self.full or not text:
            return
        room = OUTPUT_CAP - self.size
        if len(text) >= room:
            text = text[:room]
            self.full = True
        self.pending.append(text)
        self.size += len(text)
        if self.full:
            self.pending.append(OUTPUT_NOTICE)

    def peek(self):
        if len(self.pending) > 1:
            self.pending = ["".join(self.pending)]
        return self.pending[0] if self.pending else ""

    def take(self):
        text = self.peek()
        self.pending = []
        return text


sink = Sink()


class LearnerOutput(io.TextIOBase):
    def __init__(self, name):
        super().__init__()
        self._name = name

    @property
    def encoding(self):
        return "utf-8"

    @property
    def errors(self):
        return "replace"

    @property
    def name(self):
        return self._name

    def writable(self):
        return True

    def readable(self):
        return False

    def isatty(self):
        return False

    def flush(self):
        pass

    def fileno(self):
        raise io.UnsupportedOperation("fileno")

    def write(self, text):
        if not isinstance(text, str):
            raise TypeError("write() argument must be str, not " + type(text).__name__)
        sink.write(text)
        return len(text)


state = {"steps": 0, "bytes": 0, "limit": False, "busy": False}
seen = {}
learner_codes = []
learner_ids = set()
module_code = None


def short(text, limit=VALUE_LIMIT):
    return text if len(text) <= limit else text[: limit - 3] + "..."


def plural(count, word):
    return format(count, ",") + " " + (word if count == 1 else word + "s")


def describe_function(value):
    code = getattr(value, "__code__", None)
    name = str(getattr(value, "__name__", "") or type(value).__name__)
    if not isinstance(code, types.CodeType):
        return "function " + name
    names = code.co_varnames
    positional = code.co_argcount
    keyword_only = code.co_kwonlyargcount
    parts = list(names[:positional])
    if code.co_posonlyargcount:
        parts.insert(code.co_posonlyargcount, "/")
    has_star = bool(code.co_flags & 0x04)
    if has_star:
        parts.append("*" + names[positional + keyword_only])
    elif keyword_only:
        parts.append("*")
    parts.extend(names[positional : positional + keyword_only])
    if code.co_flags & 0x08:
        parts.append("**" + names[positional + keyword_only + (1 if has_star else 0)])
    return "function " + name + "(" + ", ".join(parts) + ")"


def is_function(value):
    return isinstance(value, (types.FunctionType, types.BuiltinFunctionType, types.MethodType))


def type_label(value):
    if is_function(value):
        return "function"
    if isinstance(value, type):
        return "class"
    return type(value).__name__


def shape_text(value, kind):
    shape = getattr(value, "shape", None)
    if not (isinstance(shape, tuple) and shape and all(type(n) is int for n in shape)):
        return None
    name = kind.__name__
    if len(shape) == 2:
        text = name + " with " + plural(shape[0], "row") + " and " + plural(shape[1], "column")
        columns = getattr(value, "columns", None)
        if columns is not None and shape[1] <= 6:
            text += ": " + ", ".join(str(column) for column in list(columns)[:6])
        return text
    if len(shape) == 1:
        text = name + " with " + plural(shape[0], "value")
        if shape[0] <= 10 and hasattr(value, "tolist"):
            text += ": " + bounded(value.tolist(), 1)
        return text
    return name + " with shape (" + ", ".join(str(n) for n in shape) + ")"


def raw_bounded(value, depth):
    kind = type(value)
    if value is None or kind in (bool, float, complex):
        return repr(value)
    if kind is int:
        if value.bit_length() > 300:
            digits = int(value.bit_length() * 0.30103) + 1
            return "int with about " + format(digits, ",") + " digits"
        return repr(value)
    if kind in (str, bytes, bytearray):
        return repr(value[: VALUE_LIMIT + 1])
    if kind in (types.FunctionType, types.LambdaType):
        return describe_function(value) if depth == 0 else "function " + str(value.__name__)
    if is_function(value):
        return "function " + str(getattr(value, "__name__", kind.__name__))
    if isinstance(value, type):
        return "class " + str(value.__name__)
    if kind in (list, tuple, set, frozenset, dict):
        if not value:
            return repr(value)
        if depth >= 2:
            return {list: "[...]", tuple: "(...)", dict: "{...}"}.get(kind, "{...}")
        parts = []
        used = 0
        source = value.items() if kind is dict else value
        for index, item in enumerate(source):
            if index >= 12 or used > VALUE_LIMIT:
                parts.append("...")
                break
            if kind is dict:
                text = bounded(item[0], depth + 1) + ": " + bounded(item[1], depth + 1)
            else:
                text = bounded(item, depth + 1)
            parts.append(text)
            used += len(text) + 2
        body = ", ".join(parts)
        if kind is list:
            return "[" + body + "]"
        if kind is tuple:
            return "(" + body + ("," if len(value) == 1 else "") + ")"
        if kind is frozenset:
            return "frozenset({" + body + "})"
        return "{" + body + "}"
    module = getattr(kind, "__module__", "")
    if module == "__main__" and kind.__repr__ is object.__repr__:
        attributes = getattr(value, "__dict__", None)
        if isinstance(attributes, dict):
            parts = []
            for index, (name, item) in enumerate(attributes.items()):
                if index >= 12:
                    parts.append("...")
                    break
                parts.append(str(name) + "=" + bounded(item, depth + 1))
            return kind.__name__ + "(" + ", ".join(parts) + ")"
    if module not in ("builtins", "__main__"):
        text = shape_text(value, kind)
        if text is not None:
            return text
    if hasattr(kind, "__len__"):
        size = len(value)
        if type(size) is int and size > 200:
            return kind.__name__ + " with " + format(size, ",") + " items"
    return repr(value)


def bounded(value, depth=0):
    try:
        return short(raw_bounded(value, depth))
    except Exception:
        return "<unprintable " + type(value).__name__ + ">"


def exception_text(exc):
    name = type(exc).__name__
    try:
        message = str(exc)
    except Exception:
        message = ""
    return short(name + ": " + message if message else name, 300)


def variables(frame):
    found = []
    try:
        names = frame.f_globals if frame.f_code is module_code else frame.f_locals
        items = list(names.items())
    except Exception:
        return found
    is_module = frame.f_code is module_code
    for name, value in items:
        if len(found) >= MAX_VARIABLES:
            break
        if not isinstance(name, str) or name.startswith("."):
            continue
        if name.startswith("__") and name.endswith("__"):
            continue
        if is_module and isinstance(value, types.ModuleType):
            continue
        try:
            label = type_label(value)
        except Exception:
            label = "object"
        found.append({"name": short(name), "type": short(label), "value": bounded(value)})
    return found


def stack_for(frame, line):
    frames = []
    current = frame
    while current is not None:
        if id(current.f_code) in learner_ids:
            frames.append(current)
        current = current.f_back
    frames.reverse()
    start = max(0, len(frames) - MAX_FRAMES)
    stack = []
    for depth in range(start, len(frames)):
        item = frames[depth]
        stack.append({
            "function": item.f_code.co_name,
            "line": line if item is frame else item.f_lineno,
            "depth": depth,
            "variables": variables(item),
        })
    return stack


def record(frame, event, line, return_value=None, exception=None):
    if state["limit"]:
        return
    if state["steps"] >= MAX_STEPS:
        state["limit"] = True
        return
    state["busy"] = True
    sink.paused = True
    try:
        step = {
            "line": line,
            "event": event,
            "function": frame.f_code.co_name,
            "stack": stack_for(frame, line),
            "return_value": return_value,
            "exception": exception,
        }
        payload = json.dumps({"step": step, "out": sink.peek()}, ensure_ascii=True, default=str)
        if state["bytes"] + len(payload) + 1 > STEP_BYTES_BUDGET:
            state["limit"] = True
            return
        result_file.write(payload + "\n")
        result_file.flush()
        sink.take()
        state["steps"] += 1
        state["bytes"] += len(payload) + 1
    finally:
        sink.paused = False
        state["busy"] = False


def line_event(frame, line):
    if state["limit"]:
        raise StepLimit()
    record(frame, "line", line)
    if state["limit"]:
        raise StepLimit()


def exception_event(frame, exc):
    if isinstance(exc, StepLimit) or seen.get(id(frame)) is exc:
        return
    seen[id(frame)] = exc
    record(frame, "exception", frame.f_lineno, exception=exception_text(exc))


def ignored():
    return state["busy"] or _thread.get_ident() != MAIN_THREAD


def run_monitoring(code, namespace):
    monitoring = sys.monitoring
    tool = next(i for i in range(6) if monitoring.get_tool(i) is None)
    monitoring.use_tool_id(tool, "ds60-step-through")
    events = monitoring.events

    def on_start(code_object, offset):
        if ignored() or code_object is module_code:
            return
        record(sys._getframe(1), "call", code_object.co_firstlineno)

    def on_resume(code_object, offset):
        if ignored():
            return
        frame = sys._getframe(1)
        record(frame, "call", frame.f_lineno)

    def on_return(code_object, offset, value):
        if ignored():
            return
        frame = sys._getframe(1)
        shown = None if code_object is module_code else bounded(value)
        record(frame, "return", frame.f_lineno, return_value=shown)

    def on_line(code_object, line):
        if ignored():
            return
        line_event(sys._getframe(1), line)

    def on_raise(code_object, offset, exc):
        if ignored() or id(code_object) not in learner_ids:
            return
        exception_event(sys._getframe(1), exc)

    callbacks = {
        events.PY_START: on_start,
        events.PY_RESUME: on_resume,
        events.PY_RETURN: on_return,
        events.PY_YIELD: on_return,
        events.LINE: on_line,
        events.RAISE: on_raise,
    }
    for event, callback in callbacks.items():
        monitoring.register_callback(tool, event, callback)
    local = events.LINE | events.PY_START | events.PY_RETURN | events.PY_YIELD | events.PY_RESUME
    try:
        for code_object in learner_codes:
            monitoring.set_local_events(tool, code_object, local)
        monitoring.set_events(tool, events.RAISE)
        exec(code, namespace)
    finally:
        monitoring.set_events(tool, 0)
        for code_object in learner_codes:
            monitoring.set_local_events(tool, code_object, 0)
        for event in callbacks:
            monitoring.register_callback(tool, event, None)
        monitoring.free_tool_id(tool)


def run_settrace(code, namespace):
    raising = set()

    def local(frame, event, arg):
        if ignored():
            return local
        if event == "line":
            raising.discard(id(frame))
            line_event(frame, frame.f_lineno)
        elif event == "return":
            if id(frame) in raising:
                raising.discard(id(frame))
            else:
                shown = None if frame.f_code is module_code else bounded(arg)
                record(frame, "return", frame.f_lineno, return_value=shown)
        elif event == "exception":
            raising.add(id(frame))
            exception_event(frame, arg[1])
        return local

    def global_trace(frame, event, arg):
        if id(frame.f_code) not in learner_ids or ignored():
            return None
        if frame.f_code is not module_code:
            flags = frame.f_code.co_flags
            resumable = flags & (0x20 | 0x80 | 0x200)
            line = frame.f_lineno if resumable else frame.f_code.co_firstlineno
            record(frame, "call", line)
        return local

    sys.settrace(global_trace)
    try:
        exec(code, namespace)
    finally:
        sys.settrace(None)


def learner_line(exc):
    line = None
    traceback = exc.__traceback__
    while traceback is not None:
        if id(traceback.tb_frame.f_code) in learner_ids:
            line = traceback.tb_lineno
        traceback = traceback.tb_next
    return line


def collect(code_object):
    learner_codes.append(code_object)
    learner_ids.add(id(code_object))
    for constant in code_object.co_consts:
        if isinstance(constant, types.CodeType):
            collect(constant)


def finish(error):
    sys.stdout, sys.stderr = REAL_STDOUT, REAL_STDERR
    final = {"final": {"error": error, "step_limit_reached": state["limit"]}, "out": sink.take()}
    result_file.write(json.dumps(final, ensure_ascii=True, default=str) + "\n")
    result_file.flush()


def main():
    global module_code
    with open(SOURCE_PATH, "rb") as handle:
        source = handle.read()
    sys.stdout = LearnerOutput("<stdout>")
    sys.stderr = LearnerOutput("<stderr>")
    try:
        code = compile(source, "main.py", "exec", dont_inherit=True)
    except SyntaxError as exc:
        line = exc.lineno if type(exc.lineno) is int else None
        message = short(str(exc.msg or exc), 500)
        finish({"type": type(exc).__name__, "message": message, "line": line})
        return
    except (ValueError, OverflowError, MemoryError) as exc:
        finish({"type": type(exc).__name__, "message": short(str(exc), 500), "line": None})
        return
    module_code = code
    collect(code)
    module = types.ModuleType("__main__")
    module.__file__ = "main.py"
    sys.modules["__main__"] = module
    sys.argv = ["main.py"]
    use_monitoring = BACKEND == "auto" and hasattr(sys, "monitoring")
    if use_monitoring and all(sys.monitoring.get_tool(i) is not None for i in range(6)):
        use_monitoring = False
    error = None
    try:
        if use_monitoring:
            run_monitoring(code, module.__dict__)
        else:
            run_settrace(code, module.__dict__)
    except StepLimit:
        pass
    except SystemExit as exc:
        if not state["limit"] and exc.code not in (None, 0):
            message = short(str(exc.code), 500)
            error = {"type": "SystemExit", "message": message, "line": learner_line(exc)}
    except BaseException as exc:
        if not state["limit"]:
            try:
                message = str(exc)
            except Exception:
                message = ""
            message = short(message, 500)
            error = {"type": type(exc).__name__, "message": message, "line": learner_line(exc)}
    finish(error)


main()
"""

_SQL_STEP_BODY = r"""
import json, math, os, re, sys
from decimal import Decimal
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if isinstance(payload, dict):
    context = payload.get("context") or []
    steps = payload.get("steps") or []
else:
    context, steps = [], payload
out = open(sys.argv[2], "w", encoding="utf-8")


def emit(record):
    out.write(json.dumps(record, ensure_ascii=True, default=str, allow_nan=False) + "\n")
    out.flush()


try:
    import psycopg
    from psycopg.types import datetime as pg_datetime
    from psycopg.types.json import set_json_loads
except ImportError:
    emit({"fatal": "Install the Core/bridge profile in the selected Python backend."})
    sys.exit(1)


def tolerant(base):
    class Loader(base):
        def load(self, data):
            try:
                return super().load(data)
            except psycopg.DataError:
                return bytes(data).decode("utf-8", "replace")

    return Loader


def register_loaders(conn):
    # infinity, BC and year 10000+ values have no Python equivalent; show PostgreSQL's text.
    for name, base in (("date", pg_datetime.DateLoader),
            ("timestamp", pg_datetime.TimestampLoader),
            ("timestamptz", pg_datetime.TimestamptzLoader),
            ("interval", pg_datetime.IntervalLoader)):
        conn.adapters.register_loader(name, tolerant(base))


def json_float(token):
    value = float(token)
    if math.isfinite(value) and Decimal(str(value)) == Decimal(token):
        return value
    return Decimal(token)


def load_json(value):
    return json.loads(value, parse_float=json_float)


def transport_value(value):
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value if len(value) <= SQL_CELL_LIMIT else value[:SQL_CELL_LIMIT] + "..."
    if isinstance(value, int):
        return value if -(2**53 - 1) <= value <= 2**53 - 1 else str(value)
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        return value
    if isinstance(value, dict):
        return {key: transport_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [transport_value(item) for item in value]
    return value


def first_line(exc):
    if isinstance(exc, psycopg.errors.QueryCanceled):
        return "This step took longer than 5 seconds, so PostgreSQL stopped it."
    if isinstance(exc, psycopg.errors.ReadOnlySqlTransaction):
        return READ_ONLY_STEP
    lines = str(exc).strip().splitlines()
    text = lines[0] if lines else type(exc).__name__
    return text[:300]


def encode(record):
    return json.dumps(transport_value(record), ensure_ascii=True, default=str, allow_nan=False)


def run_step(conn, index, sql):
    record = {"index": index, "columns": [], "rows": [], "row_count": None,
        "rows_truncated": False, "error": None}
    conn.execute("SAVEPOINT ds60_step")
    try:
        with conn.cursor(name="ds60_step_" + str(index)) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchmany(PREVIEW_ROWS + 1)
            columns = [column.name for column in cursor.description or []]
        count = conn.execute("SELECT count(*) FROM (\n" + sql + "\n) AS ds60_step").fetchone()[0]
        conn.execute("RELEASE SAVEPOINT ds60_step")
    except psycopg.Error as exc:
        conn.execute("ROLLBACK TO SAVEPOINT ds60_step")
        conn.execute("RELEASE SAVEPOINT ds60_step")
        record["error"] = first_line(exc)
        return encode(record)
    record["columns"] = columns
    record["rows"] = [list(row) for row in rows[:PREVIEW_ROWS]]
    record["rows_truncated"] = len(rows) > PREVIEW_ROWS
    record["row_count"] = count
    line = encode(record)
    while len(line) > SQL_LINE_CAP and record["rows"]:
        record["rows"] = record["rows"][: len(record["rows"]) // 2]
        record["rows_truncated"] = True
        line = encode(record)
    return line


search_path = os.environ.get("DS60_PAD_SEARCH_PATH", "")
if search_path and not re.fullmatch(r"[a-z_][a-z0-9_]*(?:,[a-z_][a-z0-9_]*){0,7}", search_path):
    emit({"fatal": "Invalid lesson search path"})
    sys.exit(1)


class CourseRoleError(ValueError):
    pass


try:
    conn = psycopg.connect("",
        options="-c statement_timeout=5000 -c lock_timeout=2000"
        + " -c default_transaction_read_only=on"
        + (" -c search_path=" + search_path if search_path else ""))
except psycopg.Error as exc:
    emit({"fatal": first_line(exc)})
    sys.exit(1)


def replay(conn, item):
    sql = item.get("sql", "")
    if item.get("control"):
        conn.execute(sql)
        return
    conn.execute("SAVEPOINT ds60_ctx")
    try:
        conn.execute(sql)
    except psycopg.Error:
        conn.execute("ROLLBACK TO SAVEPOINT ds60_ctx")
    conn.execute("RELEASE SAVEPOINT ds60_ctx")


try:
    # A worked solution's trusted setup writes inside this transaction, which is never committed.
    conn.read_only = not context
    if conn.info.dbname != "advanced_sql_training":
        raise CourseRoleError("The SQL pad requires the disposable course database.")
    privileged = conn.execute(COURSE_ROLE_QUERY).fetchone()
    if not privileged or privileged[0]:
        raise CourseRoleError(
            "SQL pads require a limited course login. "
            "See docs/setup/postgresql.md for role setup."
        )
    set_json_loads(load_json, context=conn)
    register_loaders(conn)
    started = conn.execute(
        "SELECT backend_start::text FROM pg_stat_activity WHERE pid=pg_backend_pid()"
    ).fetchone()[0]
    Path(os.environ["DS60_PAD_BACKEND_START"]).write_text(started)
    Path(os.environ["DS60_PAD_BACKEND_PID"]).write_text(str(conn.info.backend_pid))
    if context:
        for item in context:
            replay(conn, item)
        conn.execute("SET LOCAL statement_timeout = 5000")
        conn.execute("SET LOCAL lock_timeout = 2000")
        conn.execute("SET LOCAL transaction_read_only = on")
    for index, sql in enumerate(steps):
        out.write(run_step(conn, index, sql) + "\n")
        out.flush()
    emit({"done": True})
except CourseRoleError as exc:
    emit({"fatal": str(exc)})
except psycopg.Error as exc:
    emit({"fatal": first_line(exc)})
finally:
    with __import__("contextlib").suppress(Exception):
        conn.rollback()
    with __import__("contextlib").suppress(Exception):
        conn.close()
"""


def python_trace_worker() -> str:
    """Return the tracer script, prefixed with the shared limits."""

    constants = {
        "MAX_STEPS": MAX_STEPS,
        "OUTPUT_CAP": OUTPUT_CAP,
        "STEP_BYTES_BUDGET": STEP_BYTES_BUDGET,
        "VALUE_LIMIT": VALUE_LIMIT,
        "MAX_VARIABLES": MAX_VARIABLES,
        "MAX_FRAMES": MAX_FRAMES,
        "OUTPUT_NOTICE": OUTPUT_NOTICE,
    }
    prefix = "".join(f"{name} = {value!r}\n" for name, value in constants.items())
    return prefix + _PYTHON_TRACE_BODY


def sql_step_worker(role_query: str) -> str:
    """Return the SQL step script, prefixed with the course role check and limits."""

    constants = {
        "COURSE_ROLE_QUERY": role_query,
        "PREVIEW_ROWS": PREVIEW_ROWS,
        "SQL_CELL_LIMIT": SQL_CELL_LIMIT,
        "SQL_LINE_CAP": SQL_LINE_CAP,
        "READ_ONLY_STEP": READ_ONLY_STEP,
    }
    prefix = "".join(f"{name} = {value!r}\n" for name, value in constants.items())
    return prefix + _SQL_STEP_BODY


def read_records(path: Path) -> list[dict[str, Any]]:
    """Read complete JSON lines from a bounded worker result file."""

    with contextlib.suppress(OSError):
        if path.is_symlink() or not path.is_file():
            return []
        with path.open("rb") as handle:
            data = handle.read(RESULT_FILE_CAP)
        records: list[dict[str, Any]] = []
        for raw in data.split(b"\n"):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw.decode("utf-8"))
            except ValueError:
                break
            if isinstance(value, dict):
                records.append(value)
        return records
    return []


def clean_text(text: str) -> str:
    """Replace lone surrogates so the HTTP response always encodes."""

    return text.encode("utf-8", "replace").decode("utf-8")


def _text(value: Any, redact: Callable[[str], str]) -> str | None:
    return clean_text(redact(value)) if isinstance(value, str) else None


def python_response(
    code: str,
    records: list[dict[str, Any]],
    *,
    stopped: str | None,
    elapsed_seconds: float,
    redact: Callable[[str], str],
) -> dict[str, Any]:
    """Assemble the documented Python step-through response from worker records."""

    steps: list[dict[str, Any]] = []
    lengths: list[int] = []
    raw_output = ""
    final: dict[str, Any] | None = None
    for item in records:
        delta = item.get("out")
        if "final" in item:
            if isinstance(delta, str):
                raw_output += delta
            final = item["final"] if isinstance(item["final"], dict) else {}
            break
        step = item.get("step")
        if not isinstance(step, dict):
            continue
        if isinstance(delta, str):
            raw_output += delta
        lengths.append(len(raw_output))
        steps.append(_python_step(step, redact))
    output = clean_text(redact(raw_output))
    if output != raw_output:
        lengths = [
            min(len(clean_text(redact(raw_output[:length]))), len(output)) for length in lengths
        ]
    for step, length in zip(steps, lengths, strict=True):
        step["output_length"] = length
    error: dict[str, Any] | None = None
    step_limit = False
    if final is not None:
        step_limit = final.get("step_limit_reached") is True
        reported = final.get("error")
        if isinstance(reported, dict):
            line = reported.get("line")
            error = {
                "type": _text(reported.get("type"), redact) or "Error",
                "message": _text(reported.get("message"), redact) or "",
                "line": line if type(line) is int else None,
            }
    elif stopped is None:
        error = {
            "type": "RuntimeError",
            "message": "Step-through stopped before the program finished.",
            "line": None,
        }
    if len(steps) >= MAX_STEPS and final is None and stopped is None:
        step_limit = True
    return {
        "kind": "python",
        "code": code,
        "steps": steps,
        "output": output,
        "step_limit_reached": step_limit,
        "stopped": stopped,
        "error": error,
        "elapsed_seconds": elapsed_seconds,
    }


def _python_step(step: dict[str, Any], redact: Callable[[str], str]) -> dict[str, Any]:
    stack: list[dict[str, Any]] = []
    for frame in step.get("stack") or []:
        if not isinstance(frame, dict):
            continue
        variables = [
            {
                "name": _text(item.get("name"), redact) or "",
                "type": _text(item.get("type"), redact) or "",
                "value": _text(item.get("value"), redact) or "",
            }
            for item in frame.get("variables") or []
            if isinstance(item, dict)
        ]
        line = frame.get("line")
        depth = frame.get("depth")
        stack.append(
            {
                "function": _text(frame.get("function"), redact) or "",
                "line": line if type(line) is int else None,
                "depth": depth if type(depth) is int else len(stack),
                "variables": variables,
            }
        )
    line = step.get("line")
    event = step.get("event")
    return {
        "line": line if type(line) is int else None,
        "event": event if event in {"line", "call", "return", "exception"} else "line",
        "function": _text(step.get("function"), redact) or "",
        "stack": stack,
        "output_length": 0,
        "return_value": _text(step.get("return_value"), redact),
        "exception": _text(step.get("exception"), redact),
    }


# SQL planning: tokenizer, statement selection and clause steps.

_WORD = re.compile(r"[^\W\d]\w*\$*\w*", re.UNICODE)
_NUMBER = re.compile(r"(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?")
_DOLLAR = re.compile(r"\$([^\W\d]\w*)?\$", re.UNICODE)


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    start: int
    end: int
    depth: int

    @property
    def upper(self) -> str:
        return self.text.upper() if self.kind == "word" else ""


def tokenize(sql: str) -> list[Token]:
    """Split SQL into tokens, tracking parenthesis depth outside quotes and comments."""

    tokens: list[Token] = []
    index = 0
    depth = 0
    length = len(sql)
    while index < length:
        char = sql[index]
        if char.isspace():
            index += 1
            continue
        start = index
        if char == "-" and sql.startswith("--", index):
            end = sql.find("\n", index)
            index = length if end < 0 else end
            tokens.append(Token("comment", sql[start:index], start, index, depth))
            continue
        if char == "/" and sql.startswith("/*", index):
            nesting = 0
            while index < length:
                if sql.startswith("/*", index):
                    nesting += 1
                    index += 2
                elif sql.startswith("*/", index):
                    nesting -= 1
                    index += 2
                    if nesting == 0:
                        break
                else:
                    index += 1
            tokens.append(Token("comment", sql[start:index], start, index, depth))
            continue
        if char == "\\":
            end = sql.find("\n", index)
            index = length if end < 0 else end
            tokens.append(Token("meta", sql[start:index], start, index, depth))
            continue
        if char == "'":
            index = _quoted_end(sql, index + 1, "'", backslash=False)
            tokens.append(Token("string", sql[start:index], start, index, depth))
            continue
        if char == '"':
            index = _quoted_end(sql, index + 1, '"', backslash=False)
            tokens.append(Token("quoted", sql[start:index], start, index, depth))
            continue
        if char == "$":
            match = _DOLLAR.match(sql, index)
            if match:
                close = sql.find(match.group(0), match.end())
                index = length if close < 0 else close + len(match.group(0))
                tokens.append(Token("string", sql[start:index], start, index, depth))
                continue
        word = _WORD.match(sql, index)
        if word:
            text = word.group(0)
            index = word.end()
            if text in {"e", "E"} and index < length and sql[index] == "'":
                index = _quoted_end(sql, index + 1, "'", backslash=True)
                tokens.append(Token("string", sql[start:index], start, index, depth))
                continue
            tokens.append(Token("word", text, start, index, depth))
            continue
        number = _NUMBER.match(sql, index)
        if number and char != ".":
            index = number.end()
            tokens.append(Token("number", sql[start:index], start, index, depth))
            continue
        if number and char == "." and number.end() > index + 1:
            index = number.end()
            tokens.append(Token("number", sql[start:index], start, index, depth))
            continue
        index += 1
        if char == "(":
            tokens.append(Token("open", char, start, index, depth))
            depth += 1
        elif char == ")":
            depth -= 1
            tokens.append(Token("close", char, start, index, depth))
        elif char == ",":
            tokens.append(Token("comma", char, start, index, depth))
        elif char == ";":
            tokens.append(Token("semicolon", char, start, index, depth))
        else:
            tokens.append(Token("op", char, start, index, depth))
    return tokens


def _quoted_end(sql: str, index: int, quote: str, *, backslash: bool) -> int:
    length = len(sql)
    while index < length:
        char = sql[index]
        if backslash and char == "\\":
            index += 2
            continue
        if char == quote:
            if index + 1 < length and sql[index + 1] == quote:
                index += 2
                continue
            return index + 1
        index += 1
    return length


@dataclass(frozen=True)
class PlannedStep:
    clause: str
    title: str
    sql: str
    highlight: tuple[int, int]
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SqlPlan:
    statement: str
    statement_offset: int
    steps: tuple[PlannedStep, ...]
    unsupported: str | None


def _significant(tokens: list[Token]) -> list[Token]:
    return [token for token in tokens if token.kind != "comment"]


def split_statements(code: str) -> list[tuple[int, int, int]]:
    """Return (start, end, stop) for each statement: trimmed span and separator end."""

    spans: list[tuple[int, int, int]] = []
    current: list[Token] = []
    for token in tokenize(code):
        separator = token.kind == "meta" or (token.kind == "semicolon" and token.depth <= 0)
        if separator:
            significant = _significant(current)
            if significant:
                stop = token.end if token.kind == "semicolon" else significant[-1].end
                spans.append((significant[0].start, significant[-1].end, stop))
            current = []
            continue
        current.append(token)
    significant = _significant(current)
    if significant:
        spans.append((significant[0].start, significant[-1].end, significant[-1].end))
    return spans


def _savepoint_name(token: Token | None) -> str | None:
    if token is None:
        return None
    if token.kind == "quoted":
        return token.text[1:-1].replace('""', '"')
    return token.text.lower() if token.kind == "word" else None


def _chains(words: list[str]) -> bool:
    return "CHAIN" in words and "NO" not in words


def sanitize_sql_context(text: str) -> list[dict[str, Any]]:
    """Turn a worked solution's setup into statements one uncommitted transaction can replay.

    Transaction boundaries become a ``ds60_tx`` savepoint so nothing commits, savepoint
    commands run only when the simulated stack proves they cannot fail, and statements
    that stream through a client, leave the transaction or loosen the walk's limits are
    dropped. Control items run directly; the rest are isolated by the worker.
    """

    items: list[dict[str, Any]] = []
    stack: list[str] = []

    def control(sql: str) -> None:
        items.append({"sql": sql, "control": True})

    def open_tx() -> None:
        control(f"SAVEPOINT {_TX_SAVEPOINT}")
        stack.append(_TX_SAVEPOINT)

    def close_tx(*, rollback: bool) -> None:
        if rollback:
            control(f"ROLLBACK TO SAVEPOINT {_TX_SAVEPOINT}")
        control(f"RELEASE SAVEPOINT {_TX_SAVEPOINT}")
        del stack[stack.index(_TX_SAVEPOINT) :]

    for start, end, _ in split_statements(text):
        if len(items) >= MAX_SQL_CONTEXT:
            break
        sql = text[start:end]
        tokens = _significant(tokenize(sql))
        words = [token.upper for token in tokens if token.kind == "word"]
        head = " ".join(words[:2])
        first = words[0] if words else ""
        if first in _SKIPPED_CONTEXT or head in _SKIPPED_CONTEXT:
            continue
        if first in {"SET", "RESET"}:
            names = [w for w in words[1:] if w not in {"LOCAL", "SESSION"}]
            if names and names[0].lower() in _GUARDED_SETTINGS:
                continue
        in_tx = _TX_SAVEPOINT in stack
        if first == "BEGIN" or head == "START TRANSACTION":
            if not in_tx:
                open_tx()
            continue
        if first in {"COMMIT", "END", "ROLLBACK", "ABORT"} and "TO" not in words:
            if in_tx:
                close_tx(rollback=first in {"ROLLBACK", "ABORT"})
                if _chains(words):
                    open_tx()
            continue
        if first in {"SAVEPOINT", "RELEASE", "ROLLBACK"}:
            name_token = tokens[-1] if len(tokens) > 1 else None
            name = _savepoint_name(name_token)
            if name_token is None or name is None or name.startswith("ds60_"):
                continue
            if first == "SAVEPOINT":
                control(f"SAVEPOINT {name_token.text}")
                stack.append(name)
            elif name in stack:
                position = len(stack) - 1 - stack[::-1].index(name)
                if first == "RELEASE":
                    control(f"RELEASE SAVEPOINT {name_token.text}")
                    del stack[position:]
                else:
                    control(f"ROLLBACK TO SAVEPOINT {name_token.text}")
                    del stack[position + 1 :]
            continue
        items.append({"sql": sql, "control": False})
    return items


def _is_query(tokens: list[Token]) -> bool:
    for token in tokens:
        if token.kind == "open":
            continue
        return token.upper in {"SELECT", "WITH", "VALUES", "TABLE"}
    return False


def plan_sql(code: str, cursor_offset: int | None = None) -> SqlPlan:
    """Choose one statement and plan its clause-by-clause steps."""

    spans = split_statements(code)
    chosen: tuple[int, int, int] | None = None
    if cursor_offset is not None:
        for span in spans:
            if span[0] <= cursor_offset <= span[2]:
                chosen = span
                break
    if chosen is None:
        for span in reversed(spans):
            if _is_query(_significant(tokenize(code[span[0] : span[1]]))):
                chosen = span
                break
    if chosen is None:
        if spans:
            start, end, _ = spans[-1]
            return SqlPlan(code[start:end], start, (), NOT_A_QUERY)
        return SqlPlan("", 0, (), NO_QUERY)
    start, end, _ = chosen
    statement = code[start:end]
    tokens = _significant(tokenize(statement))
    if not _is_query(tokens):
        return SqlPlan(statement, start, (), NOT_A_QUERY)
    if any(token.kind == "semicolon" for token in tokens) or not _balanced(tokens):
        return SqlPlan(statement, start, (), UNBALANCED)
    try:
        steps, unsupported = _Planner(statement, tokens).plan()
    except _Fallback:
        return SqlPlan(statement, start, (), UNSUPPORTED_SQL)
    if unsupported is not None:
        return SqlPlan(statement, start, (), unsupported)
    return SqlPlan(statement, start, tuple(_finalize(statement, steps)), None)


def _balanced(tokens: list[Token]) -> bool:
    depth = 0
    for token in tokens:
        if token.kind == "open":
            depth += 1
        elif token.kind == "close":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def _whole_step(statement: str) -> PlannedStep:
    return PlannedStep(
        "select", "Run the whole query", statement, (0, len(statement)), {"kind": "whole"}
    )


def _normalized(sql: str) -> str:
    return " ".join(token.text for token in _significant(tokenize(sql)))


def _finalize(statement: str, steps: list[PlannedStep]) -> list[PlannedStep]:
    kept: list[PlannedStep] = []
    for step in steps:
        if kept and _normalized(kept[-1].sql) == _normalized(step.sql):
            continue
        kept.append(step)
    if not kept:
        kept.append(_whole_step(statement))
    last = kept[-1]
    if last.sql != statement:
        kept[-1] = PlannedStep(last.clause, last.title, statement, last.highlight, last.detail)
    if len(kept) > MAX_SQL_STEPS:
        kept = kept[: MAX_SQL_STEPS - 1] + [kept[-1]]
    return kept


class _Fallback(Exception):
    pass


_CLAUSES = {"SELECT", "FROM", "WHERE", "GROUP", "HAVING", "WINDOW", "ORDER", "LIMIT", "OFFSET"}
_JOIN_MODIFIERS = {"NATURAL", "INNER", "LEFT", "RIGHT", "FULL", "OUTER", "CROSS"}
_SET_OPERATORS = {"UNION", "INTERSECT", "EXCEPT"}
_DATA_CHANGING = {"INSERT", "UPDATE", "DELETE", "MERGE"}
_AGGREGATES = {
    "count",
    "sum",
    "avg",
    "min",
    "max",
    "string_agg",
    "array_agg",
    "bool_and",
    "bool_or",
    "every",
    "json_agg",
    "jsonb_agg",
    "json_object_agg",
    "jsonb_object_agg",
    "stddev",
    "stddev_pop",
    "stddev_samp",
    "variance",
    "var_pop",
    "var_samp",
    "percentile_cont",
    "percentile_disc",
    "mode",
    "corr",
    "covar_pop",
    "covar_samp",
    "bit_and",
    "bit_or",
}
_ORDINALS = (
    "First",
    "Second",
    "Third",
    "Fourth",
    "Fifth",
    "Sixth",
    "Seventh",
    "Eighth",
    "Ninth",
    "Tenth",
)


@dataclass
class _Clause:
    name: str
    first: int
    body: int
    last: int


class _Planner:
    def __init__(self, statement: str, tokens: list[Token]) -> None:
        self.statement = statement
        self.tokens = tokens
        self.prefix = ""

    def text(self, first: int, last: int) -> str:
        return self.statement[self.tokens[first].start : self.tokens[last].end]

    def span(self, first: int, last: int) -> tuple[int, int]:
        return (self.tokens[first].start, self.tokens[last].end)

    def with_prefix(self, sql: str) -> str:
        return self.prefix.rstrip() + "\n" + sql if self.prefix else sql

    def matching(self, index: int) -> int:
        depth = self.tokens[index].depth
        for position in range(index + 1, len(self.tokens)):
            token = self.tokens[position]
            if token.kind == "close" and token.depth == depth:
                return position
        raise _Fallback

    def plan(self) -> tuple[list[PlannedStep], str | None]:
        steps: list[PlannedStep] = []
        main = 0
        if self.tokens[0].upper == "WITH":
            main, cte_steps, unsupported = self.parse_with()
            if unsupported is not None:
                return [], unsupported
            steps.extend(cte_steps)
            self.prefix = self.statement[: self.tokens[main].start]
        first = self.tokens[main]
        if first.upper in _DATA_CHANGING:
            return [], NOT_A_QUERY
        if first.upper not in {"SELECT", "VALUES", "TABLE"} and first.kind != "open":
            return [], NOT_A_QUERY
        for token in self.tokens[main:]:
            if token.depth == 0 and token.upper == "FOR":
                return [], LOCKING_QUERY
        operators = [
            index
            for index in range(main, len(self.tokens))
            if self.tokens[index].depth == 0 and self.tokens[index].upper in _SET_OPERATORS
        ]
        if operators:
            steps.extend(self.plan_set(main, operators))
            return steps, None
        if first.upper != "SELECT":
            steps.append(_whole_step(self.statement))
            return steps, None
        main_steps, unsupported = self.plan_select(main)
        if unsupported is not None:
            return [], unsupported
        steps.extend(main_steps)
        return steps, None

    def parse_with(self) -> tuple[int, list[PlannedStep], str | None]:
        tokens = self.tokens
        index = 1
        if index < len(tokens) and tokens[index].upper == "RECURSIVE":
            index += 1
        steps: list[PlannedStep] = []
        while True:
            if index >= len(tokens) or tokens[index].kind not in {"word", "quoted"}:
                raise _Fallback
            name_index = index
            index += 1
            if index < len(tokens) and tokens[index].kind == "open":
                index = self.matching(index) + 1
            if index >= len(tokens) or tokens[index].upper != "AS":
                raise _Fallback
            index += 1
            if index < len(tokens) and tokens[index].upper == "NOT":
                index += 1
            if index < len(tokens) and tokens[index].upper == "MATERIALIZED":
                index += 1
            if index >= len(tokens) or tokens[index].kind != "open":
                raise _Fallback
            close = self.matching(index)
            if index + 1 < len(tokens) and tokens[index + 1].upper in _DATA_CHANGING:
                return 0, [], NOT_A_QUERY
            index = close + 1
            while (
                index < len(tokens)
                and not (tokens[index].kind == "comma" and tokens[index].depth == 0)
                and tokens[index].upper not in {"SELECT", "VALUES", "TABLE"} | _DATA_CHANGING
                and tokens[index].kind != "open"
            ):
                index += 1
            item_end = index - 1
            name = tokens[name_index]
            display = name.text.strip('"') if name.kind == "quoted" else name.text
            prefix = self.statement[: tokens[item_end].end]
            steps.append(
                PlannedStep(
                    "cte",
                    f"Build the CTE {display}",
                    prefix + "\nSELECT * FROM " + name.text,
                    self.span(name_index, item_end),
                    {"kind": "cte", "name": display},
                )
            )
            if index < len(tokens) and tokens[index].kind == "comma":
                index += 1
                continue
            break
        if index >= len(tokens):
            raise _Fallback
        return index, steps, None

    def plan_set(self, main: int, operators: list[int]) -> list[PlannedStep]:
        tokens = self.tokens
        bounds: list[tuple[int, int]] = []
        start = main
        labels: list[str] = []
        for operator in operators:
            if operator - 1 < start:
                raise _Fallback
            bounds.append((start, operator - 1))
            label = tokens[operator].upper
            start = operator + 1
            if start < len(tokens) and tokens[start].upper in {"ALL", "DISTINCT"}:
                label += " " + tokens[start].upper
                start += 1
            labels.append(label)
        last = len(tokens) - 1
        tail: list[str] = []
        for index in range(start, len(tokens)):
            token = tokens[index]
            if token.depth == 0 and token.upper in {"ORDER", "LIMIT", "OFFSET", "FETCH"}:
                last = index - 1
                tail = [
                    t.upper + (" BY" if t.upper == "ORDER" else "")
                    for t in tokens[index:]
                    if t.depth == 0 and t.upper in {"ORDER", "LIMIT", "OFFSET", "FETCH"}
                ]
                break
        if last < start:
            raise _Fallback
        bounds.append((start, last))
        steps: list[PlannedStep] = []
        for number, (first, final) in enumerate(bounds):
            ordinal = _ORDINALS[number] if number < len(_ORDINALS) else f"Query {number + 1}"
            title = f"{ordinal} query" if number < len(_ORDINALS) else ordinal
            steps.append(
                PlannedStep(
                    "select",
                    title,
                    self.with_prefix(self.text(first, final)),
                    self.span(first, final),
                    {"kind": "branch", "ordinal": title.lower()},
                )
            )
        same = all(label == labels[0] for label in labels)
        steps.append(
            PlannedStep(
                "select",
                f"Combine with {labels[0]}" if same else "Combine the queries",
                self.statement,
                (tokens[main].start, len(self.statement)),
                {
                    "kind": "combine",
                    "operator": labels[0] if same else None,
                    "branches": len(bounds),
                    "tail": tail,
                },
            )
        )
        return steps

    def clauses(self, main: int) -> list[_Clause]:
        tokens = self.tokens
        found: list[_Clause] = []
        index = main
        while index < len(tokens):
            token = tokens[index]
            word = token.upper
            following = tokens[index + 1].upper if index + 1 < len(tokens) else ""
            name = None
            body = index + 1
            if token.depth == 0 and word in _CLAUSES | {"FETCH"}:
                if word in {"GROUP", "ORDER"}:
                    if following == "BY":
                        name, body = word, index + 2
                elif word == "FROM":
                    before = [t.upper for t in tokens[max(main, index - 3) : index]]
                    if not (before[-1:] == ["DISTINCT"] and "IS" in before[-3:-1]):
                        name = word
                else:
                    name = word
            if name is not None:
                if found:
                    found[-1].last = index - 1
                found.append(_Clause(name, index, body, len(tokens) - 1))
            index += 1
        return found

    def plan_select(self, main: int) -> tuple[list[PlannedStep], str | None]:
        tokens = self.tokens
        clauses = self.clauses(main)
        if not clauses or clauses[0].name != "SELECT" or clauses[0].first != main:
            raise _Fallback
        order = ["SELECT", "FROM", "WHERE", "GROUP", "HAVING", "WINDOW", "ORDER"]
        rank = {name: position for position, name in enumerate(order)}
        tail_names = {"LIMIT", "OFFSET", "FETCH"}
        previous = -1
        seen: set[str] = set()
        for clause in clauses:
            if clause.name in seen:
                raise _Fallback
            seen.add(clause.name)
            position = rank.get(clause.name, len(order))
            if position < previous or (previous == len(order) and clause.name not in tail_names):
                raise _Fallback
            previous = position
        by_name = {clause.name: clause for clause in clauses}
        select = by_name["SELECT"]
        for index in range(select.body, select.last + 1):
            if tokens[index].depth == 0 and tokens[index].upper == "INTO":
                return [], NOT_A_QUERY
        steps: list[PlannedStep] = []
        source = by_name.get("FROM")
        if source is None or source.last < source.body:
            return [self.select_step(select, by_name, no_from=True)], None
        steps.extend(self.from_steps(source))
        from_text = self.text(source.first, source.last)
        where = by_name.get("WHERE")
        where_text = ""
        if where is not None and where.last >= where.body:
            where_text = "\n" + self.text(where.first, where.last)
            steps.append(
                PlannedStep(
                    "where",
                    "Keep rows with WHERE",
                    self.with_prefix("SELECT * " + from_text + where_text),
                    self.span(where.first, where.last),
                    {"kind": "where"},
                )
            )
        group = by_name.get("GROUP")
        if group is not None and group.last >= group.body:
            group_sql = self.group_query(select, group, from_text + where_text)
            steps.append(
                PlannedStep(
                    "group",
                    "Group rows with GROUP BY",
                    self.with_prefix(group_sql),
                    self.span(group.first, group.last),
                    {"kind": "group"},
                )
            )
            having = by_name.get("HAVING")
            if having is not None and having.last >= having.body:
                steps.append(
                    PlannedStep(
                        "having",
                        "Filter groups with HAVING",
                        self.with_prefix(group_sql + "\n" + self.text(having.first, having.last)),
                        self.span(having.first, having.last),
                        {"kind": "having"},
                    )
                )
        steps.append(self.select_step(select, by_name, no_from=False))
        order_clause = by_name.get("ORDER")
        if order_clause is not None:
            steps.append(
                PlannedStep(
                    "order",
                    "Sort with ORDER BY",
                    self.with_prefix(self.text(main, order_clause.last)),
                    self.span(order_clause.first, order_clause.last),
                    {"kind": "order"},
                )
            )
        tail = [clause for clause in clauses if clause.name in tail_names]
        if tail:
            names = {clause.name for clause in tail}
            if "LIMIT" in names:
                title = "Keep the first rows with LIMIT"
            elif "FETCH" in names:
                title = "Keep the first rows with FETCH"
            else:
                title = "Skip rows with OFFSET"
            steps.append(
                PlannedStep(
                    "limit",
                    title,
                    self.statement,
                    (tokens[tail[0].first].start, tokens[tail[-1].last].end),
                    {
                        "kind": "limit",
                        "limit": "LIMIT" in names,
                        "offset": "OFFSET" in names,
                        "fetch": "FETCH" in names,
                        "ordered": order_clause is not None,
                    },
                )
            )
        return steps, None

    def select_step(
        self, select: _Clause, by_name: dict[str, _Clause], *, no_from: bool
    ) -> PlannedStep:
        tokens = self.tokens
        ends = [
            by_name[name].first - 1
            for name in ("ORDER", "LIMIT", "OFFSET", "FETCH")
            if name in by_name
        ]
        last = min(ends) if ends else len(tokens) - 1
        items = range(select.body, select.last + 1)
        distinct = select.body <= select.last and tokens[select.body].upper == "DISTINCT"
        aggregate = False
        window = False
        for index in items:
            token = tokens[index]
            if token.upper == "OVER":
                window = True
            if (
                token.kind == "word"
                and token.text.lower() in _AGGREGATES
                and index + 1 <= select.last
                and tokens[index + 1].kind == "open"
                and token.depth == tokens[select.first].depth
            ):
                close = self.matching(index + 1)
                trailing = tokens[close + 1].upper if close + 1 < len(tokens) else ""
                if trailing == "FILTER" and close + 2 < len(tokens):
                    close = self.matching(close + 2)
                    trailing = tokens[close + 1].upper if close + 1 < len(tokens) else ""
                if trailing != "OVER":
                    aggregate = True
        return PlannedStep(
            "select",
            "Compute the columns with SELECT",
            self.with_prefix(self.text(select.first, last)),
            self.span(select.first, select.last),
            {
                "kind": "select",
                "grouped": "GROUP" in by_name,
                "aggregate": aggregate,
                "distinct": distinct,
                "window": window,
                "no_from": no_from,
            },
        )

    def from_steps(self, source: _Clause) -> list[PlannedStep]:
        tokens = self.tokens
        indexes = range(source.body, source.last + 1)
        if any(tokens[i].kind == "comma" and tokens[i].depth == 0 for i in indexes):
            return [self.from_step(source, source.last, len(indexes) > 0)]
        joins: list[tuple[int, int]] = []
        for index in indexes:
            if tokens[index].depth == 0 and tokens[index].upper == "JOIN":
                first = index
                while first - 1 > source.body and tokens[first - 1].upper in _JOIN_MODIFIERS:
                    first -= 1
                joins.append((first, index))
        if not joins:
            return [self.from_step(source, source.last, False)]
        if joins[0][0] - 1 < source.body:
            raise _Fallback
        steps = [self.from_step(source, joins[0][0] - 1, False)]
        for number, (first, keyword) in enumerate(joins):
            last = joins[number + 1][0] - 1 if number + 1 < len(joins) else source.last
            if last <= keyword:
                raise _Fallback
            modifiers = [tokens[i].upper for i in range(first, keyword)]
            target = keyword + 1
            if target <= last and tokens[target].upper == "LATERAL":
                target += 1
            name = self.source_name(target, last)
            label = " ".join([*modifiers, "JOIN"])
            kind = "inner"
            for candidate in ("CROSS", "LEFT", "RIGHT", "FULL"):
                if candidate in modifiers:
                    kind = candidate.lower()
            natural = "NATURAL" in modifiers
            using = any(
                tokens[i].depth == 0 and tokens[i].upper == "USING"
                for i in range(keyword, last + 1)
            )
            display = "a subquery" if name is None else name
            steps.append(
                PlannedStep(
                    "join",
                    f"Join {display}",
                    self.with_prefix("SELECT * " + self.text(source.first, last)),
                    self.span(first, last),
                    {
                        "kind": "join",
                        "label": label,
                        "name": display,
                        "join": kind,
                        "natural": natural,
                        "using": using,
                    },
                )
            )
        return steps

    def from_step(self, source: _Clause, last: int, listed: bool) -> PlannedStep:
        name = self.source_name(source.body, last)
        function = (
            name is not None
            and last >= source.body + 1
            and any(
                self.tokens[i].kind == "open" and self.tokens[i].depth == 0
                for i in range(source.body, last + 1)
            )
            and self.tokens[source.body].kind != "open"
        )
        if listed:
            title, kind = "Start from the FROM list", "list"
        elif name is None:
            title, kind = "Start from a subquery", "subquery"
        elif function:
            title, kind = f"Start from {name}", "function"
        else:
            title, kind = f"Start from {name}", "table"
        return PlannedStep(
            "from",
            title,
            self.with_prefix("SELECT * " + self.text(source.first, last)),
            self.span(source.first, last),
            {"kind": "from", "source": kind, "name": name},
        )

    def source_name(self, first: int, last: int) -> str | None:
        tokens = self.tokens
        index = first
        while index <= last and tokens[index].upper in {"ONLY", "LATERAL"}:
            index += 1
        if index > last or tokens[index].kind not in {"word", "quoted"}:
            return None
        end = index
        while (
            end + 2 <= last
            and tokens[end + 1].text == "."
            and tokens[end + 2].kind in {"word", "quoted"}
        ):
            end += 2
        return self.text(index, end)

    def group_query(self, select: _Clause, group: _Clause, source: str) -> str:
        tokens = self.tokens
        group_text = self.text(group.body, group.last)
        fallback = f"SELECT count(*) AS rows_in_group {source}\nGROUP BY {group_text}"
        if tokens[group.body].upper in {"ALL", "DISTINCT"}:
            return fallback
        items = self.split_items(group.body, group.last)
        select_items = self.split_items(select.body, select.last)
        if select_items and tokens[select_items[0][0]].upper in {"DISTINCT", "ALL"}:
            first, last = select_items[0]
            if (
                tokens[first].upper == "DISTINCT"
                and first + 1 <= last
                and tokens[first + 1].upper == "ON"
            ):
                return fallback
            select_items[0] = (first + 1, last)
        keys: list[str] = []
        rewritten: list[str] = []
        for position, (first, last) in enumerate(items):
            head = tokens[first]
            if head.kind == "open" or head.upper in {"ROLLUP", "CUBE", "GROUPING"}:
                return fallback
            if first == last and head.kind == "number" and head.text.isdigit():
                ordinal = int(head.text)
                if not 1 <= ordinal <= len(select_items):
                    return fallback
                if any(self.is_star(*select_items[i]) for i in range(ordinal)):
                    return fallback
                keys.append(self.text(*select_items[ordinal - 1]))
                rewritten.append(str(position + 1))
                continue
            if first == last and head.kind in {"word", "quoted"}:
                alias = self.find_alias(head, select_items)
                if alias is not None:
                    keys.append(self.text(*alias))
                    rewritten.append(head.text)
                    continue
            keys.append(self.text(first, last))
            rewritten.append(self.text(first, last))
        return (
            f"SELECT {', '.join(keys)}, count(*) AS rows_in_group {source}\n"
            f"GROUP BY {', '.join(rewritten)}"
        )

    def split_items(self, first: int, last: int) -> list[tuple[int, int]]:
        items: list[tuple[int, int]] = []
        start = first
        for index in range(first, last + 1):
            if self.tokens[index].kind == "comma" and self.tokens[index].depth == 0:
                if index - 1 < start:
                    raise _Fallback
                items.append((start, index - 1))
                start = index + 1
        if start > last:
            raise _Fallback
        items.append((start, last))
        return items

    def is_star(self, first: int, last: int) -> bool:
        return self.tokens[last].text == "*"

    def find_alias(self, name: Token, items: list[tuple[int, int]]) -> tuple[int, int] | None:
        for first, last in items:
            if last - first < 1:
                continue
            alias = self.tokens[last]
            if alias.kind not in {"word", "quoted"}:
                continue
            before = self.tokens[last - 1]
            if before.upper != "AS" and (
                alias.upper in {"END", "NULL", "TRUE", "FALSE"}
                or before.kind not in {"word", "quoted", "number", "string", "close"}
            ):
                continue
            if alias.kind == "quoted" or name.kind == "quoted":
                same = alias.text == name.text
            else:
                same = alias.text.lower() == name.text.lower()
            if same:
                return (first, last)
        return None


# Explanations: plain sentences built from the measured row counts.


def _count(value: int, word: str = "row") -> str:
    return f"{value:,} {word if value == 1 else word + 's'}"


def _change(count: int, previous: int | None) -> str:
    if previous is None:
        return ""
    if count > previous:
        return f" (up from {previous:,})"
    if count < previous:
        return f" (down from {previous:,})"
    return " (the same as before)"


def explain(detail: dict[str, Any], count: int | None, previous: int | None, failed: bool) -> str:
    """Describe one step for a beginner, mentioning how the row count changed."""

    kind = detail.get("kind")
    known = count is not None and not failed
    if kind == "cte":
        name = detail.get("name")
        if not known or count is None:
            return f"The CTE {name} is a named query that later parts of the query can read."
        return (
            f"The CTE {name} returns {_count(count)}. "
            "Later parts of the query can read it like a table."
        )
    if kind == "branch":
        ordinal = detail.get("ordinal", "query")
        if not known or count is None:
            return f"The {ordinal} runs on its own first."
        return f"The {ordinal} runs on its own and returns {_count(count)}."
    if kind == "combine":
        return _explain_combine(detail, count if known else None)
    if kind == "from":
        source = detail.get("source")
        if source == "list":
            lead = (
                "FROM lists several sources, and every row of one is paired with every row "
                "of the next."
            )
            return lead if not known or count is None else f"{lead} That gives {_count(count)}."
        if source == "subquery":
            lead = "FROM runs the subquery and reads its rows."
        elif source == "function":
            lead = f"FROM reads the rows that {detail.get('name')} returns."
        else:
            lead = "FROM picks the table the query reads."
        if not known or count is None:
            return lead
        return (
            f"{lead} It has {_count(count)}."
            if source == "table"
            else f"{lead} That gives {_count(count)}."
        )
    if kind == "join":
        return _explain_join(detail, count if known else None, previous)
    if kind == "where":
        tail = "Rows where the condition is false or NULL are dropped."
        if not known or count is None:
            return f"WHERE keeps only rows where the condition is true. {tail}"
        if previous is None:
            return f"WHERE kept {_count(count)}. {tail}"
        return f"WHERE kept {count:,} of the {_count(previous)}. {tail}"
    if kind == "group":
        note = "The rows_in_group column counts the rows in each group."
        if not known or count is None:
            return f"GROUP BY puts rows with the same values into one group. {note}"
        source = "" if previous is None else f" from {_count(previous)}"
        return f"GROUP BY formed {_count(count, 'group')}{source}. {note}"
    if kind == "having":
        tail = "Groups where the condition is false or NULL are dropped."
        if not known or count is None:
            return f"HAVING keeps only groups where the condition is true. {tail}"
        if previous is None:
            return f"HAVING kept {_count(count, 'group')}. {tail}"
        return f"HAVING kept {count:,} of the {_count(previous, 'group')}. {tail}"
    if kind == "select":
        return _explain_select(detail, count if known else None, previous)
    if kind == "order":
        if not known or count is None:
            return "ORDER BY sorts the rows. Sorting does not change the row count."
        return (
            "ORDER BY sorted the rows. Sorting does not change the row count, so there are "
            f"still {_count(count)}."
        )
    if kind == "limit":
        return _explain_limit(detail, count if known else None, previous)
    if not known or count is None:
        return "Step-through could not split this query into clauses, so it runs as one step."
    return (
        "Step-through could not split this query into clauses, so it runs as one step. "
        f"It returns {_count(count)}."
    )


def _explain_combine(detail: dict[str, Any], count: int | None) -> str:
    operator = detail.get("operator")
    both = "both queries" if detail.get("branches") == 2 else "the queries"
    if operator == "UNION ALL":
        lead = f"UNION ALL stacks the rows from {both} and keeps duplicates"
    elif operator is not None and operator.startswith("UNION"):
        lead = f"{operator} stacks the rows from {both} and removes duplicate rows"
    elif operator is not None and operator.startswith("INTERSECT"):
        lead = f"{operator} keeps only rows that appear in {both}"
    elif operator is not None and operator.startswith("EXCEPT"):
        lead = f"{operator} keeps rows from the first query that do not appear in the next one"
    else:
        lead = "The set operators combine the query results from left to right"
    text = lead + ("." if count is None else f", giving {_count(count)}.")
    tail = detail.get("tail") or []
    if tail:
        names = " and ".join(dict.fromkeys(tail))
        verb = "applies" if len(dict.fromkeys(tail)) == 1 else "apply"
        text += f" Then {names} {verb} to the combined rows."
    return text


def _explain_join(detail: dict[str, Any], count: int | None, previous: int | None) -> str:
    label = detail.get("label", "JOIN")
    name = detail.get("name")
    kind = detail.get("join")
    giving = "" if count is None else f", giving {_count(count)}{_change(count, previous)}"
    if kind == "cross":
        return f"{label} {name} paired every row with every row of {name}{giving}."
    if kind == "left":
        return (
            f"{label} {name} kept every row from the left side and added the matching "
            f"columns from {name}{giving}. Left rows with no match get NULL in those columns."
        )
    if kind == "right":
        return (
            f"{label} {name} kept every row from {name} and added the matching rows "
            f"from the left side{giving}. Rows with no match get NULL in the left columns."
        )
    if kind == "full":
        return (
            f"{label} {name} kept every row from both sides and matched them where it could"
            f"{giving}. Rows with no match get NULL on the other side."
        )
    if detail.get("natural"):
        condition = "the columns that share a name"
    elif detail.get("using"):
        condition = "the USING columns"
    else:
        condition = "the ON condition"
    return f"{label} {name} matched rows on {condition}{giving}."


def _explain_select(detail: dict[str, Any], count: int | None, previous: int | None) -> str:
    if detail.get("no_from"):
        if count is None:
            return "SELECT computes the values without reading any table."
        return f"SELECT computed the values without reading any table, giving {_count(count)}."
    if detail.get("grouped"):
        text = "SELECT computed the output columns, one row per group"
        text += "." if count is None else f", giving {_count(count)}."
    elif detail.get("aggregate") and not detail.get("distinct"):
        if count is None:
            text = (
                "SELECT computed the output columns. The aggregate functions collapse the rows "
                "into one row."
            )
        elif previous is None:
            text = (
                "SELECT computed the output columns. The aggregate functions collapsed the rows "
                f"into {_count(count)}."
            )
        else:
            text = (
                "SELECT computed the output columns. The aggregate functions collapsed "
                f"the {_count(previous)} into {_count(count)}."
            )
    elif detail.get("distinct"):
        if count is None:
            text = "SELECT computed the output columns, and DISTINCT removed duplicate rows."
        elif previous is None:
            text = (
                "SELECT computed the output columns, and DISTINCT removed duplicate rows, "
                f"leaving {_count(count)}."
            )
        else:
            text = (
                "SELECT computed the output columns, and DISTINCT removed duplicate rows, "
                f"leaving {count:,} of the {_count(previous)}."
            )
    elif count is None:
        text = "SELECT computed the output columns for each row."
    else:
        text = f"SELECT computed the output columns for each of the {_count(count)}."
    if detail.get("window"):
        text += " Window functions looked at related rows without merging them."
    return text


def _explain_limit(detail: dict[str, Any], count: int | None, previous: int | None) -> str:
    if detail.get("limit") and detail.get("offset"):
        lead = "OFFSET skipped the first rows and LIMIT kept the next ones"
    elif detail.get("offset") and not detail.get("limit") and not detail.get("fetch"):
        lead = "OFFSET skipped the first rows"
    else:
        lead = ("FETCH" if detail.get("fetch") and not detail.get("limit") else "LIMIT") + (
            " kept the first rows"
        )
    if count is None:
        text = lead + "."
    elif previous is None:
        text = f"{lead}, giving {_count(count)}."
    else:
        text = f"{lead}, giving {count:,} of the {_count(previous)}."
    if not detail.get("ordered"):
        text += " Without ORDER BY, which rows come first is not guaranteed."
    return text


def sql_unsupported_response(plan: SqlPlan, *, solution: bool = False) -> dict[str, Any] | None:
    """Return the shared no-database reply when a plan cannot be walked through."""

    if plan.unsupported is None and plan.steps:
        return None
    unsupported = plan.unsupported or NO_QUERY
    if solution and unsupported == NOT_A_QUERY:
        unsupported = SOLUTION_NOT_A_QUERY
    return {
        "kind": "sql",
        "statement": plan.statement,
        "statement_offset": plan.statement_offset,
        "steps": [],
        "unsupported": unsupported,
        "elapsed_seconds": 0.0,
        "error": None,
    }


def sql_response(
    plan: SqlPlan,
    records: list[dict[str, Any]],
    *,
    stopped: str | None,
    elapsed_seconds: float,
    redact: Callable[[str], str],
) -> dict[str, Any]:
    """Combine the plan with worker results into the documented SQL response."""

    results: dict[int, dict[str, Any]] = {}
    fatal: str | None = None
    done = False
    for record in records:
        if "fatal" in record:
            fatal = _text(record.get("fatal"), redact) or "Step-through could not reach PostgreSQL."
        elif record.get("done") is True:
            done = True
        elif type(record.get("index")) is int:
            results[record["index"]] = record
    steps: list[dict[str, Any]] = []
    previous: int | None = None
    for index, planned in enumerate(plan.steps):
        result = results.get(index)
        if result is None:
            break
        error = _text(result.get("error"), redact)
        count = result.get("row_count")
        count = count if type(count) is int and error is None else None
        kind = planned.detail.get("kind")
        reference = None if kind in {"cte", "branch"} else previous
        raw_columns, raw_rows = result.get("columns"), result.get("rows")
        columns: list[Any] = raw_columns if isinstance(raw_columns, list) else []
        rows: list[Any] = raw_rows if isinstance(raw_rows, list) else []
        steps.append(
            {
                "clause": planned.clause,
                "title": planned.title,
                "explanation": explain(planned.detail, count, reference, error is not None),
                "sql": planned.sql,
                "highlight": list(planned.highlight),
                "columns": [_text(str(column), redact) for column in columns]
                if error is None
                else [],
                "rows": [_redact_value(row, redact) for row in rows] if error is None else [],
                "row_count": count,
                "rows_truncated": result.get("rows_truncated") is True and error is None,
                "error": error,
            }
        )
        if kind not in {"cte", "branch"}:
            previous = count
    error_text: str | None = fatal
    if error_text is None and len(steps) < len(plan.steps):
        if stopped == "time limit":
            error_text = (
                f"Step-through reached the time limit after {len(steps)} of {len(plan.steps)} "
                "steps. Choose a longer run limit and try again."
            )
        elif not done or stopped is not None:
            error_text = "Step-through stopped before every step ran."
    return {
        "kind": "sql",
        "statement": plan.statement,
        "statement_offset": plan.statement_offset,
        "steps": steps,
        "unsupported": None,
        "elapsed_seconds": elapsed_seconds,
        "error": error_text,
    }


def _redact_value(value: Any, redact: Callable[[str], str]) -> Any:
    if isinstance(value, str):
        return clean_text(redact(value))
    if isinstance(value, list):
        return [_redact_value(item, redact) for item in value]
    if isinstance(value, dict):
        return {
            clean_text(redact(str(key))): _redact_value(item, redact) for key, item in value.items()
        }
    return value
