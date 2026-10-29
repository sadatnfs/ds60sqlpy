# pyweb-044: FastAPI application walkthrough

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-043`.

## Starting point and result

The FastAPI branch now combines a typed write schema, identity dependency, SQL storage, response filtering and object-level access. This chapter walks through one complete note creation and read sequence, then proves that rejected writes and cross-user reads do not alter or expose the stored record.

## Mechanism: compose the request into one accountable operation

The request schema permits only a bounded title. A dependency maps a synthetic bearer credential to an identity. The database write assigns that identity as owner on the server and uses parameter binding. The response model exposes identifier and title while excluding the internal owner field.

The read path includes both identifier and owner in its SQL predicate. This makes visibility part of data access rather than a later formatting decision. A row outside the caller's scope appears missing under this fixture's disclosure policy.

The program uses a temporary SQLite database and fixed fixture credentials. It performs real SQL and framework request handling, but it is not a deployed identity provider, PostgreSQL service or network acceptance test. Those layers belong to the owned multi-file workshop and have separate receipts.

## Worked case: create and retrieve an owned note

Alice's credential creates a note and receives 201. The response contains exactly the public fields. A subsequent GET under Alice's identity returns the same representation. The final database query confirms one committed row with the server-assigned owner.

Follow the boundaries in order: validate the command, establish identity, execute the authorized parameterized write, commit, then serialize the allowed representation. An implementation that mutates storage before checking identity would violate this order even if its eventual error response looked correct.

The database stores owner because later authorization needs it, while the API response omits owner because this representation does not require it. Internal persistence shape and external representation are allowed to differ. Keeping them explicit makes future schema changes easier to review.

## Worked case: unauthorized reads and writes have no effect

Bob requests Alice's identifier and receives 404. A write that tries to provide owner is rejected by the strict request schema. An anonymous write receives 401. After all those requests, the database still contains only Alice's original note.

That final effect check is stronger than checking three refusal codes. It detects accidental writes performed before a validation or authentication exception. It also catches an implementation that silently creates a second record while returning an error.

The read predicate is important even when identifiers are difficult to guess. An identifier can leak through logs, links or browser history. Access control must continue to work when an attacker knows the identifier; obscurity is not a substitute for the owner condition.

## Failure diagnosis and discussion

**Which part changes when replacing fixture tokens with verified JWTs?** The authentication dependency changes, while the route should continue consuming a trusted principal. The ownership and transaction rules remain necessary.

**Which part changes when moving to PostgreSQL?** Connection management, migrations and concurrency behavior require review. Parameter binding and explicit ownership remain conceptual invariants, but driver syntax and transaction semantics must be tested in the real database.

If the response is correct but the final row count is wrong, inspect side-effect ordering. If Bob can read Alice's note, inspect SQL scoping rather than the response model. If a restart loses data, inspect where the database lives relative to the container.

The next branch introduces Django's project conventions and integrated components. The shared engineering chapters later compare these frameworks through the same operational questions: who owns a request, which state is durable, how failures are observed and how a service is resumed safely.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite FastAPI investigation with original bounded fixtures."""

import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Annotated


def run_cases():
    from fastapi import Depends, FastAPI, Header, HTTPException
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, ConfigDict, Field

    class Create(BaseModel):
        model_config = ConfigDict(extra="forbid")
        title: str = Field(min_length=1, max_length=60)

    class Note(BaseModel):
        identifier: int
        title: str

    with tempfile.TemporaryDirectory() as temporary:
        database = Path(temporary) / "notes.sqlite3"
        with sqlite3.connect(database) as connection:
            connection.execute(
                "CREATE TABLE notes(id INTEGER PRIMARY KEY, "
                "owner TEXT NOT NULL, title TEXT NOT NULL)"
            )
        app = FastAPI(docs_url=None, redoc_url=None)

        def identity(authorization: Annotated[str | None, Header()] = None):
            identities = {"Bearer alice": "alice", "Bearer bob": "bob"}
            if authorization not in identities:
                raise HTTPException(401, "Invalid fixture bearer credential")
            return identities[authorization]

        @app.post("/notes", response_model=Note, status_code=201)
        def create(payload: Create, owner: Annotated[str, Depends(identity)]):
            with sqlite3.connect(database) as connection:
                identifier = connection.execute(
                    "INSERT INTO notes(owner,title) VALUES(?,?)", (owner, payload.title)
                ).lastrowid
            return {"identifier": identifier, "title": payload.title, "owner": owner}

        @app.get("/notes/{identifier}", response_model=Note)
        def read(identifier: int, owner: Annotated[str, Depends(identity)]):
            with sqlite3.connect(database) as connection:
                row = connection.execute(
                    "SELECT id,title FROM notes WHERE id=? AND owner=?", (identifier, owner)
                ).fetchone()
            if row is None:
                raise HTTPException(404, "Note not found")
            return {"identifier": row[0], "title": row[1]}

        with TestClient(app) as client:
            alice, bob = {"Authorization": "Bearer alice"}, {"Authorization": "Bearer bob"}
            created = client.post("/notes", headers=alice, json={"title": "Integrated"})
            assert created.status_code == 201 and set(created.json()) == {"identifier", "title"}
            identifier = created.json()["identifier"]
            assert client.get(f"/notes/{identifier}", headers=alice).json() == created.json()
            assert client.get(f"/notes/{identifier}", headers=bob).status_code == 404
            assert (
                client.post(
                    "/notes", headers=alice, json={"title": "Bad", "owner": "bob"}
                ).status_code
                == 422
            )
            assert client.post("/notes", json={"title": "Anonymous"}).status_code == 401
        with sqlite3.connect(database) as connection:
            assert connection.execute("SELECT owner,title FROM notes").fetchall() == [
                ("alice", "Integrated")
            ]
    return {
        "created_and_read": True,
        "unauthorized_effects": 0,
        "scope": "real client and temporary SQL; synthetic tokens",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
