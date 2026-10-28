"""Actual bounded partition backfills with explicit half-open windows and source revisions."""

import hashlib
import json
from datetime import date, timedelta

import duckdb


def database():
    connection = duckdb.connect(":memory:")
    connection.execute(
        "create table partitions(day date primary key, packages integer,"
        "source_revision integer, input_sha varchar)"
    )
    return connection


def backfill(connection, events, start, end, revision):
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if not 0 < (last - first).days <= 10 or type(revision) is not int or revision < 1:
        raise ValueError("Use a bounded half-open day interval and positive source revision")
    if len({row["id"] for row in events}) != len(events):
        raise ValueError("The declared complete source snapshot has duplicated event IDs")
    buckets = {first + timedelta(days=index): [] for index in range((last - first).days)}
    for row in events:
        day = date.fromisoformat(row["day"])
        if type(row["packages"]) is not int or row["packages"] < 1:
            raise ValueError("Package events must be positive integer observations")
        if day in buckets:
            buckets[day].append((row["id"], row["packages"]))
    decisions = []
    connection.execute("begin")
    try:
        for day, rows in sorted(buckets.items()):
            identity = hashlib.sha256(
                json.dumps(sorted(rows), separators=(",", ":")).encode()
            ).hexdigest()
            total = sum(value for _, value in rows)
            prior = connection.execute(
                "select source_revision,input_sha from partitions where day=?", [day]
            ).fetchone()
            if prior is not None and revision < prior[0]:
                decisions.append((str(day), "stale-skipped"))
                continue
            if prior is not None and revision == prior[0]:
                if prior[1] != identity:
                    raise ValueError("One partition revision cannot name conflicting input")
                decisions.append((str(day), "replayed"))
                continue
            connection.execute(
                "insert into partitions values(?,?,?,?) on conflict(day) do update set "
                "packages=excluded.packages,source_revision=excluded.source_revision,"
                "input_sha=excluded.input_sha",
                [day, total, revision, identity],
            )
            decisions.append((str(day), "updated"))
        connection.execute("commit")
    except Exception:
        connection.execute("rollback")
        raise
    return decisions


def rows(connection):
    return [
        (str(day), packages, revision)
        for day, packages, revision in connection.execute(
            "select day,packages,source_revision from partitions order by day"
        ).fetchall()
    ]


def fixture():
    return [
        {"id": "A", "day": "2024-01-01", "packages": 2},
        {"id": "B", "day": "2024-01-02", "packages": 3},
        {"id": "C", "day": "2024-01-03", "packages": 1},
    ]


def example_one():
    with database() as connection:
        backfill(connection, fixture(), "2024-01-01", "2024-01-04", 1)
        corrected = [*fixture(), {"id": "D", "day": "2024-01-02", "packages": 4}]
        decision = backfill(connection, corrected, "2024-01-02", "2024-01-03", 2)
        replay = backfill(connection, corrected, "2024-01-02", "2024-01-03", 2)
        assert decision == [("2024-01-02", "updated")] and replay == [("2024-01-02", "replayed")]
        assert rows(connection) == [
            ("2024-01-01", 2, 1),
            ("2024-01-02", 7, 2),
            ("2024-01-03", 1, 1),
        ]
        return {
            "partitions": rows(connection),
            "exclusive_end_day_unchanged": True,
            "repeat": replay,
        }


def example_two():
    with database() as connection:
        backfill(connection, fixture(), "2024-01-01", "2024-01-04", 1)
        newest = [{**row, "packages": 9} if row["id"] == "C" else row for row in fixture()]
        backfill(connection, newest, "2024-01-03", "2024-01-04", 5)
        decision = backfill(connection, fixture(), "2024-01-01", "2024-01-04", 2)
        assert rows(connection) == [
            ("2024-01-01", 2, 2),
            ("2024-01-02", 3, 2),
            ("2024-01-03", 9, 5),
        ]
        assert decision[-1] == ("2024-01-03", "stale-skipped")
        before = rows(connection)
        conflicting = [{**row, "packages": 30} if row["id"] == "B" else row for row in fixture()]
        try:
            backfill(connection, conflicting, "2024-01-01", "2024-01-03", 2)
        except ValueError:
            pass
        else:
            raise AssertionError("Equal revision with changed input must be rejected")
        assert rows(connection) == before
        return {
            "decisions": decision,
            "retained_partition_versions": rows(connection),
            "conflicting_revision_rejected": True,
        }


def main():
    print("A bounded correction with an exclusive end:", example_one())
    print("Older backfill cannot overwrite newer accepted correction:", example_two())


if __name__ == "__main__":
    main()
