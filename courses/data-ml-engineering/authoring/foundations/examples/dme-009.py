"""Actual CSV delivery validation and transactional DuckDB ingestion."""

import csv
import hashlib
import io
import re
import tempfile
from pathlib import Path

import duckdb


def delivery(path, batch_id, text, expected_rows):
    raw = text.encode("utf-8")
    path.write_bytes(raw)
    return {
        "batch_id": batch_id,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "expected_rows": expected_rows,
        "transform": "positive-package-csv-v1",
    }


def database():
    connection = duckdb.connect(":memory:")
    connection.execute(
        "create table deliveries(delivery_id varchar primary "
        "key, route_id integer, packages "
        "integer)"
    )
    connection.execute(
        "create table batches(batch_id varchar primary key, input_sha varchar, transform varchar)"
    )
    return connection


def ingest(connection, path, manifest):
    if (
        not isinstance(manifest, dict)
        or set(manifest) != {"batch_id", "sha256", "expected_rows", "transform"}
        or not isinstance(manifest["batch_id"], str)
        or not manifest["batch_id"].strip()
        or type(manifest["expected_rows"]) is not int
        or not 0 <= manifest["expected_rows"] <= 100
        or manifest["transform"] != "positive-package-csv-v1"
    ):
        raise ValueError("Use this bounded, versioned delivery contract")
    with path.open("rb") as stream:
        raw = stream.read(4097)
    if len(raw) > 4096 or hashlib.sha256(raw).hexdigest() != manifest["sha256"]:
        raise ValueError("Delivery bytes do not match the bounded manifest")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    if reader.fieldnames != ["delivery_id", "route_id", "packages"]:
        raise ValueError("Unexpected CSV header contract")
    rows = []
    for record in reader:
        if set(record) != {"delivery_id", "route_id", "packages"} or any(
            value is None for value in record.values()
        ):
            raise ValueError("Unexpected row width")
        if not record["delivery_id"].strip():
            raise ValueError("Missing delivery identity")
        if any(
            re.fullmatch(r"[1-9][0-9]*", record[name]) is None for name in ("route_id", "packages")
        ):
            raise ValueError("Declared numeric text must be a canonical positive integer")
        rows.append((record["delivery_id"], int(record["route_id"]), int(record["packages"])))
    if len(rows) != manifest["expected_rows"]:
        raise ValueError("Delivery row count differs from its declared population")
    existing = connection.execute(
        "select input_sha, transform from batches where batch_id=?", [manifest["batch_id"]]
    ).fetchone()
    identity = (manifest["sha256"], manifest["transform"])
    if existing is not None:
        if existing != identity:
            raise ValueError("An accepted batch identity cannot name different input or logic")
        return "already-applied"
    connection.execute("begin transaction")
    try:
        if rows:
            connection.executemany("insert into deliveries values (?, ?, ?)", rows)
        connection.execute(
            "insert into batches values (?, ?, ?)", [manifest["batch_id"], *identity]
        )
        connection.execute("commit")
    except Exception:
        connection.execute("rollback")
        raise
    return "accepted"


def example_one():
    with tempfile.TemporaryDirectory() as directory, database() as connection:
        path = Path(directory) / "delivery.csv"
        manifest = delivery(
            path, "batch-a", "delivery_id,route_id,packages\nA,10,2\nB,10,3\nC,20,1\n", 3
        )
        first = ingest(connection, path, manifest)
        replay = ingest(connection, path, manifest)
        rows, packages = connection.execute(
            "select count(*),sum(packages) from deliveries"
        ).fetchone()
        assert (first, replay, rows, packages) == ("accepted", "already-applied", 3, 6)
        return {"first": first, "replay": replay, "accepted_rows": rows, "packages": packages}


def example_two():
    with tempfile.TemporaryDirectory() as directory, database() as connection:
        path = Path(directory) / "delivery.csv"
        good = delivery(
            path, "batch-a", "delivery_id,route_id,packages\nA,10,2\nB,10,3\nC,20,1\n", 3
        )
        ingest(connection, path, good)
        path.write_bytes(path.read_bytes()[:-4])
        try:
            ingest(connection, path, good)
        except ValueError:
            checksum_rejected = True
        else:
            raise AssertionError("Changed input must not reuse the old delivery receipt")
        short = delivery(path, "batch-b", "delivery_id,route_id,packages\nD,20,4\n", 2)
        try:
            ingest(connection, path, short)
        except ValueError:
            population_rejected = True
        else:
            raise AssertionError("A matching byte hash cannot prove declared row completeness")
        conflict = delivery(path, "batch-c", "delivery_id,route_id,packages\nD,20,4\nA,10,9\n", 2)
        try:
            ingest(connection, path, conflict)
        except duckdb.ConstraintException:
            transaction_rejected = True
        else:
            raise AssertionError("The existing delivery identity must not be overwritten")
        identities = connection.execute(
            "select delivery_id from deliveries order by delivery_id"
        ).fetchall()
        assert identities == [("A",), ("B",), ("C",)]
        assert connection.execute("select count(*) from batches").fetchone() == (1,)
        return {
            "checksum_rejected": checksum_rejected,
            "population_rejected": population_rejected,
            "transaction_rejected": transaction_rejected,
            "retained_accepted_ids": identities,
        }


def main():
    print("Validated actual ingestion and replay:", example_one())
    print("Bad deliveries do not replace accepted state:", example_two())


if __name__ == "__main__":
    main()
