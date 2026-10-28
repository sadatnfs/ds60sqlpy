"""Real SQLite producer/outbox and consumer/inbox transactions; transport is a local call."""

import sqlite3
import tempfile
from pathlib import Path


def producer(path):
    connection = sqlite3.connect(path)
    connection.execute(
        "create table if not exists state(id integer primary key,units integer not null)"
    )
    connection.execute(
        "create table if not exists outbox(event_id text primary key,"
        "units integer not null,sent integer not null)"
    )
    connection.execute("insert or ignore into state values(1,0)")
    connection.commit()
    return connection


def consumer(path):
    connection = sqlite3.connect(path)
    connection.execute(
        "create table if not exists inbox(event_id text primary key,units integer not null)"
    )
    connection.execute(
        "create table if not exists projection(id integer primary key,units integer not null)"
    )
    connection.execute("insert or ignore into projection values(1,0)")
    connection.commit()
    return connection


def create_event(connection, identity, units, fail_between=False):
    if not isinstance(identity, str) or not identity.strip() or type(units) is not int or units < 1:
        raise ValueError("Use an identified positive-unit operation")
    with connection:
        connection.execute("begin immediate")
        prior = connection.execute(
            "select units from outbox where event_id=?", (identity,)
        ).fetchone()
        if prior is not None:
            if prior != (units,):
                raise ValueError("Operation identity has conflicting content")
            return "replayed"
        connection.execute("update state set units=units+? where id=1", (units,))
        if fail_between:
            raise RuntimeError("Deliberate failure before the outbox row")
        connection.execute("insert into outbox values(?,?,0)", (identity, units))
    return "created"


def consume(connection, identity, units):
    with connection:
        connection.execute("begin immediate")
        prior = connection.execute(
            "select units from inbox where event_id=?", (identity,)
        ).fetchone()
        if prior is not None:
            if prior != (units,):
                raise ValueError("Replayed event differs from accepted content")
            return "replayed"
        connection.execute("insert into inbox values(?,?)", (identity, units))
        connection.execute("update projection set units=units+? where id=1", (units,))
    return "applied"


def dispatch(source, destination, fail_after_effect=False):
    results = []
    for identity, units in source.execute(
        "select event_id,units from outbox where sent=0 order by event_id"
    ).fetchall():
        outcome = consume(destination, identity, units)
        if fail_after_effect:
            raise RuntimeError(
                "Consumer committed, but the producer has no observed acknowledgement"
            )
        with source:
            source.execute("update outbox set sent=1 where event_id=?", (identity,))
        results.append((identity, outcome))
    return results


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        source = producer(Path(directory) / "producer.db")
        try:
            try:
                create_event(source, "event-a", 3, fail_between=True)
            except RuntimeError:
                pass
            else:
                raise AssertionError("The deliberate atomicity failure was not observed")
            assert source.execute("select units from state").fetchone() == (0,)
            assert source.execute("select count(*) from outbox").fetchone() == (0,)
            assert create_event(source, "event-a", 3) == "created"
            assert create_event(source, "event-a", 3) == "replayed"
            assert source.execute("select units from state").fetchone() == (3,)
            return {"failed_transaction_left_units": 0, "accepted_units": 3, "outbox_rows": 1}
        finally:
            source.close()


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source, destination = producer(root / "producer.db"), consumer(root / "consumer.db")
        try:
            create_event(source, "event-a", 3)
            try:
                dispatch(source, destination, fail_after_effect=True)
            except RuntimeError:
                pass
            else:
                raise AssertionError("The acknowledgement boundary must be visible")
            assert source.execute("select sent from outbox").fetchone() == (0,)
            assert destination.execute("select units from projection").fetchone() == (3,)
            destination.close()
            destination = consumer(root / "consumer.db")
            replay = dispatch(source, destination)
            assert replay == [("event-a", "replayed")]
            assert destination.execute("select units from projection").fetchone() == (3,)
            assert destination.execute("select count(*) from inbox").fetchone() == (1,)
            assert source.execute("select sent from outbox").fetchone() == (1,)
            return {
                "retry": replay,
                "consumer_units_after_retry": 3,
                "unique_applied_effects": 1,
                "scope": "two real local databases; no broker or external notification was run",
            }
        finally:
            source.close()
            destination.close()


def main():
    print("Atomic state plus outbox acceptance:", example_one())
    print("Replay across an uncertain acknowledgement:", example_two())


if __name__ == "__main__":
    main()
