"""Actual child-process failure after a committed operation, followed by readback and rollback."""

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


def database(root):
    return sqlite3.connect(root / "state.db")


def initialize(root):
    connection = database(root)
    try:
        with connection:
            connection.execute(
                "create table products(version integer primary key,packages integer not null)"
            )
            connection.execute(
                "create table accepted(id integer primary key,version integer not null)"
            )
            connection.execute(
                "create table operations(id text primary key,source_sha text not null,"
                "version integer not null)"
            )
            connection.execute(
                "create table recovery(old_version integer,new_version integer,reason text)"
            )
            connection.execute("insert into products values(1,6)")
            connection.execute("insert into accepted values(1,1)")
    finally:
        connection.close()


def worker(root):
    source = root / "proposal.json"
    proposal = json.loads(source.read_text())
    values = proposal["values"]
    if (
        not isinstance(values, list)
        or not values
        or len(values) > 100
        or any(type(value) is not int or value < 1 for value in values)
        or sum(values) != proposal["claimed_total"]
    ):
        os.write(1, b"validation_rejected\n")
        os._exit(23)
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    connection = database(root)
    try:
        with connection:
            connection.execute("insert into products values(2,?)", (sum(values),))
            connection.execute("insert into operations values('candidate-a',?,2)", (source_sha,))
            connection.execute("update accepted set version=2 where id=1")
    finally:
        connection.close()
    os.write(1, b"database_commit_completed_before_response\n")
    os._exit(17)


def run_worker(root, claimed_total=9):
    (root / "proposal.json").write_text(
        json.dumps({"values": [2, 3, 4], "claimed_total": claimed_total}, sort_keys=True)
    )
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--commit-worker", str(root)],
        capture_output=True,
        text=True,
        timeout=10,
        stdin=subprocess.DEVNULL,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "source_sha256": hashlib.sha256((root / "proposal.json").read_bytes()).hexdigest(),
    }


def inspect(root):
    connection = database(root)
    try:
        selected = connection.execute(
            "select p.version,p.packages from accepted a join products p on a.version=p.version"
        ).fetchone()
        receipt = connection.execute(
            "select source_sha,version from operations where id='candidate-a'"
        ).fetchone()
        return {
            "accepted": selected,
            "receipt": receipt,
            "products": connection.execute(
                "select version,packages from products order by version"
            ).fetchall(),
        }
    finally:
        connection.close()


def rollback(root, expected, target, reason):
    connection = database(root)
    try:
        with connection:
            connection.execute("begin immediate")
            current = connection.execute("select version from accepted").fetchone()[0]
            if current != expected or connection.execute(
                "select count(*) from products where version=?", (target,)
            ).fetchone() != (1,):
                raise ValueError("Rollback precondition or retained target failed")
            connection.execute("update accepted set version=? where id=1", (target,))
            connection.execute("insert into recovery values(?,?,?)", (expected, target, reason))
    finally:
        connection.close()


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        initialize(root)
        attempt = run_worker(root)
        observed = inspect(root)
        assert attempt["returncode"] == 17 and observed["accepted"] == (2, 9)
        assert observed["receipt"] == (attempt["source_sha256"], 2)
        assert len(observed["products"]) == 2
        return {
            "child_exit": 17,
            "accepted_after_readback": list(observed["accepted"]),
            "receipt_matches_exact_source": True,
            "worker_invocations": 1,
            "recovery_decision": "accept the committed result without replay",
        }


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        initialize(root)
        attempt = run_worker(root)
        observed = inspect(root)
        assert attempt["returncode"] == 17 and observed["receipt"] == (attempt["source_sha256"], 2)
        consumer_limit = 8
        assert observed["accepted"][1] > consumer_limit
        rollback(root, expected=2, target=1, reason="synthetic downstream package-limit gate")
        recovered = inspect(root)
        assert recovered["accepted"] == (1, 6) and recovered["products"] == [(1, 6), (2, 9)]
        connection = database(root)
        try:
            assert connection.execute("select count(*) from recovery").fetchone() == (1,)
        finally:
            connection.close()
        return {
            "committed_candidate_failed_separate_consumer_gate": True,
            "accepted_after_explicit_rollback": list(recovered["accepted"]),
            "candidate_retained_for_investigation": True,
            "worker_invocations": 1,
            "power_loss_and_multi_host_recovery_not_tested": True,
        }


def main():
    print("Reconcile an actual process failure after commit:", example_one())
    print("Separate execution success from consumer acceptance and rollback:", example_two())


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--commit-worker":
        worker(Path(sys.argv[2]))
    else:
        main()
