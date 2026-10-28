"""Actual durable event application reconciled with an independent full-history oracle."""

import sqlite3
import tempfile
from collections import defaultdict
from pathlib import Path


def database(path):
    connection = sqlite3.connect(path)
    connection.execute(
        "create table if not exists events(event_id text primary key not null,"
        "entity text not null,version integer not null,route integer not null,"
        "packages integer not null)"
    )
    connection.execute(
        "create table if not exists current(entity text primary key not null,"
        "version integer not null,route integer not null,packages integer not null)"
    )
    connection.commit()
    return connection


def apply(connection, events):
    if not isinstance(events, list) or not 1 <= len(events) <= 20:
        raise ValueError("Use a bounded identified event batch")
    for event in events:
        if (
            not isinstance(event, (list, tuple))
            or len(event) != 5
            or any(not isinstance(value, str) or not value for value in event[:2])
            or any(type(value) is not int for value in event[2:])
            or event[2] < 1
            or event[3] not in {10, 20}
            or event[4] < 1
        ):
            raise ValueError("Event schema, source version or route is invalid")
    decisions = []
    with connection:
        connection.execute("begin immediate")
        for event_id, entity, version, route, packages in events:
            event = (entity, version, route, packages)
            prior = connection.execute(
                "select entity,version,route,packages from events where event_id=?", (event_id,)
            ).fetchone()
            if prior is not None:
                if prior != event:
                    raise ValueError("Source event identity has conflicting content")
                decisions.append("replayed")
                continue
            historical = connection.execute(
                "select route,packages from events where entity=? and version=? limit 1",
                (entity, version),
            ).fetchone()
            if historical is not None and historical != (route, packages):
                raise ValueError("Historical entity revision has conflicting content")
            current = connection.execute(
                "select version,route,packages from current where entity=?", (entity,)
            ).fetchone()
            if (
                current is not None
                and version == current[0]
                and current != (version, route, packages)
            ):
                raise ValueError("Entity revision has conflicting content")
            connection.execute("insert into events values(?,?,?,?,?)", (event_id, *event))
            if current is None or version > current[0]:
                connection.execute(
                    "insert into current values(?,?,?,?) on conflict(entity) do update set "
                    "version=excluded.version,route=excluded.route,packages=excluded.packages",
                    (entity, version, route, packages),
                )
                decisions.append("updated")
            else:
                decisions.append("older-or-identical-state")
    return decisions


def totals(connection):
    return dict(
        connection.execute("select route,sum(packages) from current group by route order by route")
    )


def oracle(events):
    seen_events = {}
    revisions = {}
    for event_id, entity, version, route, packages in events:
        event = (entity, version, route, packages)
        if event_id in seen_events and seen_events[event_id] != event:
            raise ValueError("Oracle found an event identity conflict")
        seen_events[event_id] = event
        key = (entity, version)
        if key in revisions and revisions[key] != (route, packages):
            raise ValueError("Oracle found a revision conflict")
        revisions[key] = (route, packages)
    current = {}
    for (entity, _version), payload in sorted(revisions.items(), key=lambda row: row[0][1]):
        current[entity] = payload
    result = defaultdict(int)
    for route, packages in current.values():
        result[route] += packages
    return dict(sorted(result.items()))


def fixture():
    return [("A1", "A", 1, 10, 2), ("B1", "B", 1, 10, 3), ("C1", "C", 1, 20, 1)]


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        connection = database(Path(directory) / "state.db")
        try:
            history = [*fixture(), ("A2", "A", 2, 10, 4), fixture()[0]]
            apply(connection, history)
            assert totals(connection) == oracle(history) == {10: 7, 20: 1}
            before = totals(connection)
            assert apply(connection, history) == ["replayed"] * len(history)
            assert totals(connection) == before
            return {
                "current_totals": totals(connection),
                "unique_source_events": 4,
                "raw_arrival_positions": 5,
                "full_history_oracle_agrees": True,
            }
        finally:
            connection.close()


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "state.db"
        connection = database(path)
        apply(connection, fixture())
        connection.close()
        connection = database(path)
        try:
            history = [*fixture(), ("A2", "A", 2, 20, 4), fixture()[0]]
            apply(connection, history[3:])
            assert totals(connection) == oracle(history) == {10: 3, 20: 5}
            before = totals(connection)
            try:
                apply(connection, [("D1", "D", 1, 20, 5), ("B1", "B", 1, 10, 100)])
            except ValueError:
                pass
            else:
                raise AssertionError("Conflicting source event was admitted")
            assert totals(connection) == before
            assert connection.execute("select count(*) from events").fetchone() == (4,)
            assert connection.execute("select count(*) from current").fetchone() == (3,)
            return {
                "after_restart_and_route_correction": before,
                "partial_conflicting_batch_rolled_back": True,
                "event_log_count": 4,
                "current_entity_count": 3,
            }
        finally:
            connection.close()


def main():
    print("Replay-safe state matches a full recomputation:", example_one())
    print("Restart, late correction and atomic rejection:", example_two())


if __name__ == "__main__":
    main()
