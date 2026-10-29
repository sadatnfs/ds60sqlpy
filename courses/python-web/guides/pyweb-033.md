# pyweb-033: Transactions, optimistic concurrency and idempotency keys

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-032`.

## Starting point and result

Two different problems often appear as duplicate requests. Competing clients can overwrite each other's updates, while a retry can repeat a command whose first result was lost. This chapter handles them separately with a resource version and an idempotency key, using real atomic SQL operations.

## Mechanism: compare versions and identify commands

Optimistic concurrency attaches a version to a resource representation. A client submits the version it observed, commonly through an If-Match precondition. The update changes the row only if its current version still matches. The database evaluates the predicate and mutation together, preventing a gap between checking and writing.

An idempotency key identifies one logical command. The service stores the key, a digest or canonical representation of the relevant input, and the resulting outcome in the same transaction as the effect. Repeating the same key and input returns the earlier result. Reusing the key with different input is a conflict, not permission to silently substitute a new command.

These mechanisms serve different purposes. A version belongs to mutable resource state; a command identity belongs to an attempted operation. Neither should be an unbounded global dictionary in a multi-worker service. The fixture uses SQLite transactions and bounded inputs to make the storage semantics inspectable.

## Worked case: reject a stale update

The first update supplies the current version and succeeds. A later update using the old version receives a precondition failure. A request without the required precondition receives a distinct refusal. The program checks both statuses and the stored value after the sequence.

The crucial SQL shape is an UPDATE with both identifier and expected version in its WHERE clause. A separate SELECT followed by an unconditional UPDATE would allow another writer to intervene. The affected-row count tells the application whether the conditional change occurred.

A missing row and a stale version may require different public handling depending on disclosure policy. The lesson keeps the fixture behavior explicit rather than implying that one status convention fits every API. Authorization must happen within the same resource scope as the update.

## Worked case: replay one command and reject conflicting reuse

The second case submits a command with an idempotency key, then repeats it. The database stores one effect, and the replay returns the recorded result. Reusing that key with a different payload receives a conflict response. The final row count verifies that no extra effect slipped through.

The fixture uses BEGIN IMMEDIATE to make its SQLite write ownership explicit. This is not a universal PostgreSQL recipe. A PostgreSQL implementation can use unique constraints, transaction retries and suitable locking or upsert semantics, but must preserve the same command/result invariant.

An idempotency record also needs a retention policy. Deleting it too soon can turn an old retry into a new effect. Keeping all keys forever without bounds creates another operational problem. The correct window depends on the client retry contract and the cost of duplicate effects.

## Failure diagnosis and discussion

**Does a timeout mean the command failed?** No. The response may have been lost after commit. Reconcile using the operation identity before issuing a logically new command.

**Why compare payloads when keys match?** Otherwise a client bug can reuse a key for a different operation and receive an unrelated result, hiding a serious semantic error.

If duplicate effects appear, inspect whether the key record and effect commit atomically. If stale writes succeed, inspect whether the version condition is inside the UPDATE itself. Continue with response contracts, which control what successful and failed operations expose to callers.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    import hashlib
    import sqlite3
    import tempfile
    from pathlib import Path
    from typing import Annotated

    from fastapi import FastAPI, Header, HTTPException
    from fastapi.responses import JSONResponse
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, ConfigDict, Field

    class Input(BaseModel):
        model_config = ConfigDict(extra="forbid")
        title: str = Field(min_length=1, max_length=50)

    with tempfile.TemporaryDirectory(prefix="pyweb-idempotence-") as directory:
        path = Path(directory) / "app.sqlite3"
        with sqlite3.connect(path) as db:
            db.executescript(
                "CREATE TABLE items(id INTEGER PRIMARY KEY,title TEXT NOT NULL,version INTEGER);"
                "INSERT INTO items VALUES(1,'initial',1);"
                "CREATE TABLE jobs(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL);"
                "CREATE TABLE requests(key TEXT PRIMARY KEY NOT NULL,"
                "digest TEXT NOT NULL,body TEXT NOT NULL);"
            )
        app = FastAPI(docs_url=None, redoc_url=None)

        @app.get("/item")
        def read():
            with sqlite3.connect(path) as db:
                row = db.execute("SELECT title,version FROM items WHERE id=1").fetchone()
            return JSONResponse({"title": row[0]}, headers={"ETag": f'"v{row[1]}"'})

        @app.patch("/item")
        def update(payload: Input, if_match: Annotated[str | None, Header()] = None):
            if if_match is None:
                raise HTTPException(status_code=428, detail="If-Match required")
            if (
                not if_match.startswith('"v')
                or not if_match.endswith('"')
                or not if_match[2:-1].isdigit()
            ):
                raise HTTPException(status_code=400, detail="invalid version validator")
            with sqlite3.connect(path) as db:
                changed = db.execute(
                    "UPDATE items SET title=?,version=version+1 WHERE id=1 AND version=?",
                    (payload.title, int(if_match[2:-1])),
                )
                if changed.rowcount != 1:
                    raise HTTPException(status_code=412, detail="stale version")
            return {"updated": True}

        @app.post("/jobs")
        def create_job(
            payload: Input, idempotency_key: Annotated[str, Header(min_length=1, max_length=64)]
        ):
            digest = hashlib.sha256(
                json.dumps(payload.model_dump(), sort_keys=True).encode()
            ).hexdigest()
            with sqlite3.connect(path) as db:
                db.execute("BEGIN IMMEDIATE")
                previous = db.execute(
                    "SELECT digest,body FROM requests WHERE key=?", (idempotency_key,)
                ).fetchone()
                if previous:
                    if previous[0] != digest:
                        raise HTTPException(
                            status_code=409, detail="key reused for different command"
                        )
                    return JSONResponse(json.loads(previous[1]), status_code=201)
                created = db.execute("INSERT INTO jobs(title) VALUES(?)", (payload.title,))
                body = {"id": created.lastrowid, "title": payload.title}
                db.execute(
                    "INSERT INTO requests(key,digest,body) VALUES(?,?,?)",
                    (idempotency_key, digest, json.dumps(body)),
                )
            return JSONResponse(body, status_code=201)

        with TestClient(app) as client:
            version = client.get("/item").headers["ETag"]
            assert (
                client.patch(
                    "/item", json={"title": "new"}, headers={"If-Match": version}
                ).status_code
                == 200
            )
            assert (
                client.patch(
                    "/item", json={"title": "lost update"}, headers={"If-Match": version}
                ).status_code
                == 412
            )
            first = client.post(
                "/jobs", json={"title": "report"}, headers={"Idempotency-Key": "command-1"}
            )
            repeated = client.post(
                "/jobs", json={"title": "report"}, headers={"Idempotency-Key": "command-1"}
            )
            assert (
                first.json() == repeated.json() and first.status_code == repeated.status_code == 201
            )
            assert (
                client.post(
                    "/jobs", json={"title": "different"}, headers={"Idempotency-Key": "command-1"}
                ).status_code
                == 409
            )
        with sqlite3.connect(path) as db:
            assert db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1
            assert db.execute("SELECT title FROM items").fetchone()[0] == "new"
        return {
            "stale_update_refused": True,
            "one_job_after_retry": True,
            "conflicting_reuse_refused": True,
            "scope": "single-principal fixture; production keys need principal/operation scope",
        }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
