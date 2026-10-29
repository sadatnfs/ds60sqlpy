"""Finite cross-framework engineering investigation with explicit scope."""

import json
import sqlite3


def run_cases():
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        "CREATE TABLE orders(id TEXT PRIMARY KEY, amount INTEGER NOT NULL);"
        "CREATE TABLE outbox(id TEXT PRIMARY KEY, payload TEXT NOT NULL);"
        "CREATE TABLE applied(id TEXT PRIMARY KEY);"
        "CREATE TABLE totals(value INTEGER NOT NULL); INSERT INTO totals VALUES(0);"
    )

    def accept(identifier, amount, fail=False):
        with connection:
            previous = connection.execute(
                "SELECT amount FROM orders WHERE id=?", (identifier,)
            ).fetchone()
            if previous is not None:
                if previous[0] != amount:
                    raise ValueError("Conflicting identity reuse")
                return "replayed"
            connection.execute("INSERT INTO orders VALUES(?,?)", (identifier, amount))
            if fail:
                raise RuntimeError("Failure before outbox record")
            connection.execute(
                "INSERT INTO outbox VALUES(?,?)", (identifier, json.dumps({"amount": amount}))
            )
        return "created"

    try:
        accept("failed", 7, fail=True)
    except RuntimeError as error:
        assert str(error) == "Failure before outbox record"
    else:
        raise AssertionError("Controlled failure did not occur")
    assert connection.execute("SELECT count(*) FROM orders").fetchone()[0] == 0
    assert accept("order-1", 5) == "created"
    assert accept("order-1", 5) == "replayed"
    try:
        accept("order-1", 9)
    except ValueError:
        pass
    else:
        raise AssertionError("Conflicting payload accepted")
    identifier, payload = connection.execute("SELECT id,payload FROM outbox").fetchone()

    def deliver():
        with connection:
            inserted = connection.execute(
                "INSERT OR IGNORE INTO applied VALUES(?)", (identifier,)
            ).rowcount
            if inserted:
                connection.execute(
                    "UPDATE totals SET value=value+?", (json.loads(payload)["amount"],)
                )
        return inserted

    assert [deliver(), deliver()] == [1, 0]
    assert connection.execute("SELECT value FROM totals").fetchone()[0] == 5
    connection.close()
    return {
        "acceptance_and_outbox_atomic": True,
        "duplicate_delivery_effects": 1,
        "scope": "one actual SQLite transaction system; external broker not used",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True))
