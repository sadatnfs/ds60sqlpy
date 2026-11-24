# pyweb-016: Flask and SQLAlchemy transaction ownership

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-015`, `python-12`, `sql-found-01`.

## Starting point and result

A database transaction groups changes that must succeed or fail together. An ORM session coordinates Python objects with that database work, but its lifecycle must still be explicit. This chapter uses real SQLAlchemy sessions and SQLite to compare a committed batch with a batch that violates a uniqueness constraint.

## Key terms

- **Transaction:** A group of database changes that commit together or roll back together, so a batch never partially succeeds.
- **ORM session:** The SQLAlchemy object that tracks Python objects and issues their SQL; this example creates one per operation from a session factory.
- **Session.begin():** A SQLAlchemy context manager that commits when its block exits normally and rolls back when an exception escapes.
- **Flush:** Sending pending changes to the database inside the current transaction without committing them, which can surface a constraint failure early.
- **IntegrityError:** The SQLAlchemy exception raised when a statement violates a database constraint, translated here into a 409 Conflict response.

## Mechanism: transaction boundaries belong around the operation

The Item table has a generated primary key and a unique title. A session factory creates a session for each operation. `Session.begin()` supplies a transaction context: normal exit commits, while an exception rolls back. The handler catches an IntegrityError outside that context and translates it to a controlled 409 response.

`flush()` sends pending changes to the database before the context exits. It can expose a constraint failure while the handler still controls the operation. Flushing is not the same as committing. A later failure within the transaction can still roll back earlier flushed statements.

The fixture uses a single shared in-memory SQLite connection through StaticPool. This keeps the tiny database available across its request sessions. It is a deliberate test arrangement, not a production concurrency/pooling recommendation. PostgreSQL connection pools and transaction behavior receive their own workshop acceptance.

## Worked case: a complete batch commits

The program first creates an existing title, then submits the distinct titles `one` and `two` together. Both requests return 201. A read through a fresh session sees all three titles in ID order, proving that the data survived beyond the write session.

The input is also bounded before database work: the handler accepts one to three nonempty title strings within the configured length. Those checks provide a useful public error contract, while the unique constraint remains the authoritative database rule for duplicates. Concurrent callers must not rely on a separate “does this title already exist?” query as a replacement for that constraint.

## Worked case: a duplicate rolls back the whole batch

The next request contains `temporary` followed by the already existing title. The database rejects the duplicate. The handler returns 409, and a subsequent read confirms that `temporary` was not committed either. This is the important invariant: failure of the operation does not leave a partial result that looks like a successful creation.

A transaction is not an automatic solution for effects outside the database. Sending an email between two statements would not be undone by rolling back those statements. The later outbox chapter addresses that coordination problem explicitly.

## Worked example: one transaction versus a commit per row

```python
from sqlalchemy import String, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40), unique=True)


def titles(engine):
    with Session(engine) as db:
        return list(db.scalars(select(Item.title).order_by(Item.id)))


for style in ("per_row", "one_transaction"):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db, db.begin():
        db.add(Item(title="existing"))
    batch = ["temporary", "existing"]
    try:
        if style == "per_row":
            for title in batch:
                with Session(engine) as db, db.begin():
                    db.add(Item(title=title))
        else:
            with Session(engine) as db, db.begin():
                db.add_all([Item(title=t) for t in batch])
    except IntegrityError:
        pass
    print(style, titles(engine))
```

Expected output:

```text
per_row ['existing', 'temporary']
one_transaction ['existing']
```

Both runs submitted the same batch, `temporary` followed by the duplicate `existing`, and both hit the unique constraint. Committing each row separately left `temporary` behind, a half-applied request that the client was told had failed. Wrapping the whole batch in one `db.begin()` block made the failure roll back everything, so the table returned to its prior single row. That is the ownership rule the lesson's `/batch` view follows: one HTTP request owns one transaction, and the handler translates `IntegrityError` into 409 only after the rollback has happened. Reordering the batch to put `existing` first would make the per-row version fail before inserting anything, which is why a passing test with one ordering does not prove the per-row design is safe.

## Failure diagnosis

A session left in a failed transaction may reject further operations until rolled back or closed. Reusing one global session across unrelated requests can therefore produce confusing failures and concurrency problems. A context-managed per-operation session makes its lifecycle easier to reason about.

A database exception should not be returned wholesale to the client. It can contain SQL, parameters or internal names. Translate known domain conflicts to a stable public response and retain appropriate diagnostics separately. Unexpected failures need a separate server-error path.

## Interview discussion

**Why keep the unique constraint if the application validates first?** Application checks improve feedback, but another transaction can change the database between a check and an insert. The database constraint enforces the invariant at the point of mutation.

**Does `flush()` make changes durable?** It sends statements within the current transaction. Commit establishes the transaction outcome; a later rollback can still discard flushed changes.

## Next step

Design deterministic queries and pagination. Correct transactions do not prevent a client from seeing an inconsistent sequence if page boundaries depend on changing offsets.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    from flask import Flask, request
    from sqlalchemy import String, create_engine, select
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
    from sqlalchemy.pool import StaticPool

    class Base(DeclarativeBase):
        pass

    class Item(Base):
        __tablename__ = "items"
        id: Mapped[int] = mapped_column(primary_key=True)
        title: Mapped[str] = mapped_column(String(40), unique=True)

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    app = Flask(__name__)

    @app.post("/batch")
    def batch():
        payload = request.get_json(silent=True)
        if (
            not isinstance(payload, dict)
            or not isinstance(payload.get("titles"), list)
            or not 1 <= len(payload["titles"]) <= 3
            or any(not isinstance(x, str) or not 1 <= len(x) <= 40 for x in payload["titles"])
        ):
            return {"error": "one to three bounded titles required"}, 422
        try:
            with Session.begin() as db:
                db.add_all([Item(title=title) for title in payload["titles"]])
                db.flush()
        except IntegrityError:
            return {"error": "duplicate title; batch rolled back"}, 409
        return {"created": len(payload["titles"])}, 201

    @app.get("/items")
    def items():
        with Session() as db:
            return {"titles": list(db.scalars(select(Item.title).order_by(Item.id)))}

    try:
        with app.test_client() as client:
            assert client.post("/batch", json={"titles": ["existing"]}).status_code == 201
            assert client.post("/batch", json={"titles": ["one", "two"]}).status_code == 201
            failed = client.post("/batch", json={"titles": ["temporary", "existing"]})
            assert failed.status_code == 409
            kept = client.get("/items").json["titles"]
            assert kept == ["existing", "one", "two"]
        return {
            "committed_titles": kept,
            "partial_batch_rolled_back": True,
            "database": "actual bounded SQLite transaction",
            "postgresql_executed": False,
        }
    finally:
        engine.dispose()


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Flask documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
