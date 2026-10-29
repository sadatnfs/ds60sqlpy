"""Complete finite FastAPI investigation with original bounded fixtures."""

import json
from typing import Annotated


def run_cases():
    from fastapi import Depends, FastAPI, HTTPException, Security
    from fastapi.security import OAuth2PasswordBearer, SecurityScopes
    from fastapi.testclient import TestClient

    app = FastAPI(docs_url=None, redoc_url=None)
    oauth = OAuth2PasswordBearer(
        tokenUrl="fixture-only",
        scopes={"notes:read": "Read owned notes", "notes:write": "Write owned notes"},
    )
    credentials = {
        "alice-reader": {"subject": "alice", "tenant": "a", "scopes": {"notes:read"}},
        "alice-writer": {
            "subject": "alice",
            "tenant": "a",
            "scopes": {"notes:read", "notes:write"},
        },
        "bob-writer": {"subject": "bob", "tenant": "b", "scopes": {"notes:read", "notes:write"}},
    }
    notes = {1: {"tenant": "a", "owner": "alice", "title": "Draft"}}

    def authorize(scopes: SecurityScopes, token: Annotated[str, Depends(oauth)]):
        user = credentials.get(token)
        if user is None:
            raise HTTPException(401, "Invalid fixture credential")
        if not set(scopes.scopes).issubset(user["scopes"]):
            raise HTTPException(403, "Insufficient scope")
        return user

    @app.put("/notes/{identifier}")
    def update(identifier: int, user: Annotated[dict, Security(authorize, scopes=["notes:write"])]):
        note = notes.get(identifier)
        if note is None or note["tenant"] != user["tenant"] or note["owner"] != user["subject"]:
            raise HTTPException(404, "Note not found")
        note["title"] = "Reviewed"
        return {"title": note["title"]}

    with TestClient(app) as client:
        statuses = [
            client.put("/notes/1", headers={"Authorization": "Bearer " + token}).status_code
            for token in ["unknown", "alice-reader", "bob-writer", "alice-writer"]
        ]
        assert statuses == [401, 403, 404, 200]
        assert notes[1]["title"] == "Reviewed"
    return {
        "statuses": statuses,
        "scope_is_not_object_ownership": True,
        "credentials": "synthetic fixed tokens, not an OAuth server",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
