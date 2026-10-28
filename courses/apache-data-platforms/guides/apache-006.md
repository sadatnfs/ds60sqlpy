# apache-006: Delivery, retries and idempotence

Tutorial mode. Stage: beginner. Direct prerequisites: `apache-005`.

## A retry repeats an attempt, not necessarily a business action

A caller can time out after a server has accepted a request. Retrying is then
reasonable for availability but dangerous for side effects. Delivery guarantees
must identify a boundary: a message may be delivered twice while a destination
records one business mutation, or delivered once while an uncommitted effect is
lost. The phrase exactly once is incomplete without naming the source, state,
transaction and external effects covered by that guarantee.

Idempotence means applying an operation repeatedly has the same intended effect
as applying it once: \(f(f(s,x),x)=f(s,x)\) for state \(s\) and operation
\(x\). Setting a value to a desired state is often naturally idempotent.
Incrementing a balance is not. A stable operation identifier can make an increment
safe by recording the identifier and effect atomically. It must identify the
business operation, rather than a fresh network attempt.

This example uses actual SQLite transactions in a temporary local database.
SQLite supplies the atomic database transaction; the program does not simulate a
Kafka transaction or distributed commit. The narrow scope is useful: it shows
exactly which writes share one transaction and which assumptions an application
must enforce around it. The same reasoning later applies when a consumer chooses
when to commit its Kafka offsets.

## Worked case A: acknowledge the same operation twice

An event has an identifier, account, integer amount and canonical payload digest.
The first transaction inserts the receipt and updates the balance. A retry finds
the same identifier with the same digest and returns the previous outcome without
incrementing again. The independent oracle expects balance 7 after two attempts,
not 14. The receipt and balance update commit together, so no visible receipt
can claim a mutation that the database transaction did not retain.

The payload digest uses deterministic JSON encoding and a fixed field set.
An arbitrary dictionary string representation is unsuitable as a cross-language
identity. Integer amounts represent a declared smallest currency unit in this
fixture; a production ledger would additionally define currency, scale, signs,
authorization and accounting rules. A checksum is not a signature and supplies
no proof that a caller is allowed to perform the operation.

The database is reopened after the first pair of attempts. Reading the retained
balance and receipt establishes local disk persistence across connection lifetime.
It does not establish replicated durability, survival of a destroyed volume, or
correctness under every storage failure. Those claims require different topology
and failure experiments.

## Worked case B: the identifier is reused for different data

The second case reuses the same event identifier with amount 99. Silently returning
success would conceal a client error or malicious collision. Silently applying
the replacement would make a retry mutate history. The application instead rejects
the mismatch and rolls back, leaving the balance and original receipt unchanged.
The code checks both values after rejection, rather than relying only on a raised
exception.

A second distinct identifier with the original amount is a different operation
and is therefore applied. This distinguishes deduplicating one operation from
removing legitimate identical purchases. Content-only deduplication could merge
two real orders with the same amount and customer. Identity design is part of
the business contract, not a database optimization that can be selected later.

Atomicity does not automatically include an email, HTTP request or another
database. If the program committed a balance and then called an external system,
a crash could leave one effect without the other. An outbox pattern records the
intent in the same local transaction and delivers it separately with recipient
idempotence. It still requires explicit retention, retries and reconciliation.

## Diagnosis and interview discussion

Track operation IDs, attempts, outcomes and conflicting retries separately. A
unique database constraint prevents two concurrent inserts from winning, but the
application must handle the resulting conflict by checking the stored payload.
Never catch every database exception and report it as a duplicate: disk errors,
invalid schemas and permission failures are different failures.

**Interview discussion: does an idempotent Kafka producer make a payment API
exactly once?** No. Producer sequence tracking applies to a defined Kafka producer
retry boundary. It does not automatically deduplicate a new business request or
atomically commit an unrelated payment database. This local example demonstrates
one explicit transaction boundary and rejects conflicting identity reuse, which
are prerequisites for a credible end-to-end argument.

## Complete worked source

This is a complete editable worked program for the declared prepared runtime. It uses bounded local fixtures and does not install packages or start distributed services.

```python
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
```

## Primary references

- [SQLite transactions](https://www.sqlite.org/lang_transaction.html)
- [Kafka delivery guarantees](https://kafka.apache.org/44/design/design/)
