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
