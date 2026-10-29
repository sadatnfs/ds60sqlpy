# pyweb-064: Retries, idempotency and transactional outboxes

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-063`.

## Starting point and result

A service can commit a business change and crash before notifying another component. It can also send a notification successfully and lose the acknowledgement. This chapter implements a small transactional outbox and an idempotent consumer using actual SQLite transactions to expose both problems clearly.

## Mechanism: commit intent alongside the business effect

An outbox stores a message or event in the same database transaction as the business operation. If the transaction commits, both the operation and the notification intent exist. If it rolls back, neither exists. A separate dispatcher can later read the outbox and deliver its entries.

This pattern does not make external delivery exactly once. A dispatcher can deliver and crash before marking completion, causing a retry. The consumer therefore records an event identity in the same transaction as its own effect. Repeated delivery of that identity has no second effect.

The fixture uses one SQLite connection with separate tables for orders, outbox entries, applied identities and a total. This is a real transaction test but not a distributed broker demonstration. The owned workshop extends the principle to a persistent PostgreSQL-backed job ledger and an independently running worker.

## Worked case: fail between the order and outbox insert

The accept function inserts an order, then deliberately raises before writing the outbox entry. The transaction context rolls the order back. The program asserts that the orders table remains empty and that the expected controlled failure actually occurred.

A later successful command inserts both the order and its outbox entry. Repeating the same identity and amount returns the recorded outcome without another insert. Reusing the identity with a different amount raises a conflict instead of silently treating a new command as an old one.

The payload comparison is part of the identity contract. A key alone does not tell the service whether a retry is semantically identical. Canonicalization or a stable digest can be used for larger inputs, but the fields included in that identity must be documented.

## Worked case: deliver twice, apply once

The consumer first inserts the event identity into the applied table. Only when that insert is new does it update the total. Both actions occur in one transaction. Two deliveries produce inserted counts 1 and 0, and the total increases only once.

The order of those operations matters. Recording the identity and then updating the total in separate transactions could lose the effect after a crash. Updating the total first and recording the identity later could duplicate it after a retry. Atomicity joins the decision and effect.

An external effect that cannot participate in the consumer's transaction needs its own idempotency/reconciliation mechanism. The outbox pattern does not magically make an arbitrary email or third-party API call transactional with the local database.

## Failure diagnosis and discussion

**Does at-least-once delivery mean duplicate business effects are inevitable?** No. A consumer can make its effect idempotent with a stable identity and atomic storage rule, as this fixture demonstrates.

**Can outbox entries be deleted immediately after sending?** Only under a deliberate delivery and retention policy. A lost acknowledgement, delayed retry or audit requirement may need the identity and outcome to remain available.

If an accepted operation has no notification intent, inspect transaction placement. If totals increase twice, inspect whether deduplication and the effect commit together. Continue with database plans and contention to understand the storage costs and concurrency behavior behind these guarantees.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/)
