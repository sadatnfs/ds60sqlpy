"""Actual SQLite checkpoint transactions bound to a finite source and reviewed program."""

import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path


def identity(events):
    return hashlib.sha256(json.dumps(events, separators=(",", ":")).encode()).hexdigest()


def connect(path, events, program_identity):
    if not isinstance(program_identity, str) or len(program_identity) != 64:
        raise ValueError("Declare the exact reviewed transformation SHA-256")
    if not isinstance(events, list) or len(events) > 100:
        raise ValueError("Use a bounded source tape")
    for event in events:
        if (
            not isinstance(event, list)
            or len(event) != 2
            or not isinstance(event[0], str)
            or not event[0].strip()
            or type(event[1]) is not int
        ):
            raise ValueError("Each source position needs a string identity and integer value")
    connection = sqlite3.connect(path)
    try:
        with connection:
            connection.execute(
                "create table if not exists metadata(key text primary key,value text not null)"
            )
            connection.execute(
                "create table if not exists cursor(id integer primary key,"
                "next_offset integer not null)"
            )
            connection.execute(
                "create table if not exists effects(event_id text primary key,"
                "value integer not null)"
            )
            expected = {
                "schema": "1",
                "source_sha": identity(events),
                "program_sha": program_identity,
            }
            stored = dict(connection.execute("select key,value from metadata"))
            if stored:
                if stored != expected:
                    raise ValueError("Checkpoint schema, source or transformation identity changed")
            else:
                connection.executemany("insert into metadata values(?,?)", expected.items())
                connection.execute("insert into cursor values(1,0)")
            offset = connection.execute("select next_offset from cursor where id=1").fetchone()
            if offset is None or type(offset[0]) is not int or not 0 <= offset[0] <= len(events):
                raise ValueError("Checkpoint offset is outside its bound source")
        expected_effects = {}
        for key, value in events[: offset[0]]:
            if key in expected_effects and expected_effects[key] != value:
                raise ValueError("Committed source prefix contains a conflicting replay")
            expected_effects[key] = value
        actual_effects = dict(connection.execute("select event_id,value from effects"))
        if actual_effects != expected_effects:
            raise ValueError("Checkpoint effects do not match the committed source prefix")
        return connection
    except BaseException:
        connection.close()
        raise


def resume(connection, events, interrupt_after=None, fail_after_effect=False):
    if connection.execute("select value from metadata where key='source_sha'").fetchone() != (
        identity(events),
    ):
        raise ValueError("Resume tape differs from the checkpoint source")
    commits = 0
    while True:
        with connection:
            connection.execute("begin immediate")
            offset = connection.execute("select next_offset from cursor where id=1").fetchone()[0]
            if offset == len(events):
                break
            key, value = events[offset]
            previous = connection.execute(
                "select value from effects where event_id=?", (key,)
            ).fetchone()
            if previous is not None and previous != (value,):
                raise ValueError("Repeated event identity has conflicting value")
            connection.execute("insert or ignore into effects values(?,?)", (key, value))
            if fail_after_effect:
                raise RuntimeError("Interrupted before offset and effect could commit together")
            connection.execute("update cursor set next_offset=? where id=1", (offset + 1,))
        commits += 1
        if interrupt_after == commits:
            raise RuntimeError("Controlled interruption after committed source position")
    return snapshot(connection)


def snapshot(connection):
    return {
        "next_offset": connection.execute("select next_offset from cursor").fetchone()[0],
        "effects": dict(connection.execute("select event_id,value from effects order by event_id")),
    }


def fixture():
    return [["A", 2], ["B", 3], ["A", 2], ["C", 1]]


def example_one():
    events = fixture()
    program = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "checkpoint.db"
        connection = connect(path, events, program)
        try:
            resume(connection, events, interrupt_after=2)
        except RuntimeError:
            assert snapshot(connection) == {"next_offset": 2, "effects": {"A": 2, "B": 3}}
        finally:
            connection.close()
        connection = connect(path, events, program)
        try:
            final = resume(connection, events)
            assert final == {"next_offset": 4, "effects": {"A": 2, "B": 3, "C": 1}}
            assert resume(connection, events) == final
            assert sum(final["effects"].values()) == 6
            return {"resumed": final, "unique_total": 6, "raw_tape_total": 8}
        finally:
            connection.close()


def example_two():
    events = fixture()
    program = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "checkpoint.db"
        connection = connect(path, events, program)
        try:
            try:
                resume(connection, events, fail_after_effect=True)
            except RuntimeError:
                pass
            else:
                raise AssertionError("Expected injected transaction failure")
            assert snapshot(connection) == {"next_offset": 0, "effects": {}}
            baseline = resume(connection, events)
        finally:
            connection.close()
        failures = []
        for candidate, transform in [(events + [["D", 4]], program), (events, "0" * 64)]:
            try:
                connect(path, candidate, transform)
            except ValueError:
                failures.append("identity-rejected")
            else:
                raise AssertionError("An incompatible checkpoint was admitted")
        connection = connect(path, events, program)
        try:
            assert snapshot(connection) == baseline
            with connection:
                connection.execute("update metadata set value='2' where key='schema'")
        finally:
            connection.close()
        try:
            connect(path, events, program)
        except ValueError:
            failures.append("schema-rejected")
        else:
            raise AssertionError("Unknown state schema was admitted")
        return {
            "rolled_back_effect_and_offset": True,
            "incompatible_resumes": failures,
            "baseline_preserved_before_schema_drill": baseline,
        }


def main():
    print("Durable restart with identified effects:", example_one())
    print("Atomic failure and incompatible state rejection:", example_two())


if __name__ == "__main__":
    main()
