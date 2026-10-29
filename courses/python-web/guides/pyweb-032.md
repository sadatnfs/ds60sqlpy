# pyweb-032: FastAPI asynchronous database sessions

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-031`, `sql-found-01`.

## Starting point and result

An asynchronous database session is a unit of work, not a shared global connection that every request can mutate. This chapter creates an async SQLAlchemy engine during lifespan, borrows a session for each request and checks a uniqueness failure followed by successful recovery.

## Mechanism: engine, session and transaction are different objects

The engine manages database connectivity and pooling. A session tracks a unit of work and its transaction state. A transaction defines which changes commit together. Sharing an engine is normal; sharing one mutable session concurrently across requests is not a substitute for a pool.

The fixture uses SQLite through aiosqlite so it can run offline and terminate. It performs real SQL and constraint checks, but SQLite concurrency and locking are not identical to PostgreSQL. The larger workshop prepares PostgreSQL and qualifies service-level behavior separately instead of presenting this small fixture as a production database benchmark.

A uniqueness constraint belongs in the database because concurrent requests can both pass an earlier application-level existence check. Application validation still improves error messages, but the database must decide whether the final write preserves its invariant. When the database rejects a write, the failed session transaction needs rollback before further use.

## Worked case: create and read within owned lifetimes

At startup the engine prepares the fixture schema. The route opens a new async session, executes its insert and commits. A successful response follows the committed operation. The program checks the returned value and the database-backed effect through subsequent client interaction.

The context managers express ownership. The request returns its session resources; application shutdown disposes the engine. This separation prevents one request from destroying the shared pool and prevents a leaked session from retaining a transaction indefinitely.

A real application usually manages schema changes through versioned migrations rather than creating tables during every server startup. This lesson's schema creation is an explicitly disposable fixture. Later deployment chapters put migration ownership outside normal request serving.

## Worked case: duplicate write and recovery

The program submits a value that violates the unique constraint. It converts the expected integrity failure into a conflict response and rolls the transaction back. A later valid request succeeds, proving that the earlier failure did not leave the application permanently poisoned.

The final assertion is essential. An error response alone does not establish recovery. If the session remains in a failed state or the engine was closed accidentally, subsequent operations will fail for reasons unrelated to the new input. Testing success after failure exposes that lifecycle defect.

Do not catch every database exception and label it a duplicate. A network outage, malformed SQL or unexpected schema mismatch is not the same business condition. Map only understood failures to a public domain response, retain safe diagnostics internally and let unexpected defects remain visible to operators.

## Failure diagnosis and discussion

**Why is a pre-insert existence query insufficient?** Another transaction can insert between the query and the write. The final constraint is the authority; the application must handle its refusal.

**Can one AsyncSession be used by all concurrently running tasks?** No. Its mutable transaction state belongs to a unit of work. Give independent concurrent operations their own sessions or deliberately serialize a shared transaction.

If an operation works once and then fails after a conflict, inspect rollback and session disposal. If the process hangs at exit, inspect engine disposal and outstanding tasks. Continue with optimistic concurrency and idempotency, which define what repeated or competing HTTP commands mean beyond basic transaction cleanup.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from contextlib import asynccontextmanager
    from typing import Annotated

    from fastapi import Depends, FastAPI, HTTPException
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, Field
    from sqlalchemy import Column, Integer, MetaData, String, Table, insert, select
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    metadata = MetaData()
    items = Table(
        "items",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(40), nullable=False, unique=True),
    )

    @asynccontextmanager
    async def lifespan(app):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
        app.state.sessions = async_sessionmaker(engine, expire_on_commit=False)
        try:
            yield
        finally:
            await engine.dispose()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)

    class Input(BaseModel):
        name: str = Field(min_length=1, max_length=40)

    async def session():
        async with app.state.sessions() as db:
            yield db

    @app.post("/items", status_code=201)
    async def create(payload: Input, db: Annotated[AsyncSession, Depends(session)]):
        try:
            async with db.begin():
                result = await db.execute(insert(items).values(name=payload.name))
                identifier = result.inserted_primary_key[0]
        except IntegrityError:
            raise HTTPException(status_code=409, detail="duplicate name") from None
        return {"id": identifier, "name": payload.name}

    @app.get("/items")
    async def listing(db: Annotated[AsyncSession, Depends(session)]):
        result = await db.execute(select(items).order_by(items.c.id))
        return {"items": [dict(row) for row in result.mappings()]}

    with TestClient(app) as client:
        assert client.post("/items", json={"name": "one"}).status_code == 201
        assert client.post("/items", json={"name": "one"}).status_code == 409
        assert client.post("/items", json={"name": "two"}).status_code == 201
        result = client.get("/items").json()
        assert result == {"items": [{"id": 1, "name": "one"}, {"id": 2, "name": "two"}]}
    return {
        "rows": result["items"],
        "async_transaction_recovery": True,
        "engine_owned_by_lifespan": True,
        "postgresql_executed": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
