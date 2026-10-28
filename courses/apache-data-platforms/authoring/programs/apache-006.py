import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path


def apply(connection, event):
    digest = hashlib.sha256(
        json.dumps(event, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    with connection:
        prior = connection.execute(
            "SELECT digest FROM receipts WHERE id=?", (event["id"],)
        ).fetchone()
        if prior:
            if prior[0] != digest:
                raise ValueError("Conflicting operation identity")
            return "duplicate"
        connection.execute("INSERT INTO receipts VALUES (?,?)", (event["id"], digest))
        connection.execute(
            "UPDATE accounts SET balance=balance+? WHERE account=?",
            (event["amount"], event["account"]),
        )
        return "applied"


with tempfile.TemporaryDirectory() as temporary:
    path = Path(temporary) / "operations.db"
    with sqlite3.connect(path) as connection:
        connection.executescript(
            "CREATE TABLE receipts(id TEXT PRIMARY KEY,digest TEXT NOT NULL); "
            "CREATE TABLE accounts(account TEXT PRIMARY KEY,balance INTEGER NOT NULL); "
            "INSERT INTO accounts VALUES ('demo',0);"
        )
        event = {"id": "order-1", "account": "demo", "amount": 7}
        assert apply(connection, event) == "applied"
        assert apply(connection, event) == "duplicate"
        try:
            apply(connection, event | {"amount": 99})
        except ValueError as error:
            print(error)
        else:
            raise AssertionError("Conflict accepted")
        assert connection.execute("SELECT balance FROM accounts").fetchone() == (7,)
        assert connection.execute("SELECT COUNT(*) FROM receipts").fetchone() == (1,)
    with sqlite3.connect(path) as reopened:
        assert reopened.execute("SELECT balance FROM accounts").fetchone() == (7,)
        assert apply(reopened, event | {"id": "order-2"}) == "applied"
        assert reopened.execute("SELECT balance FROM accounts").fetchone() == (14,)
print("Two attempts, one effect; a distinct operation produces a second effect.")
