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
