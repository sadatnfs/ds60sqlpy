# pyweb-038: API scopes, roles and tenant boundaries

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-037`.

## Starting point and result

Authentication establishes who is calling. Authorization determines what that caller may do to a particular resource. This chapter separates permission scopes from tenant and owner predicates, demonstrating why a broadly capable token must not grant access to another tenant's object.

## Key terms

- **Authorization:** Deciding what an identified caller may do to a particular resource, which is separate from authenticating who the caller is.
- **Scope:** A permission for a class of operation, such as writing notes, carried by a credential and checked by the endpoint.
- **SecurityScopes:** The FastAPI object that passes the scopes an endpoint requires into the dependency that checks the credential.
- **Tenant boundary:** The separation of one customer or workspace's data from another's, enforced in the lookup even for a caller with the right scope.
- **Ownership predicate:** A query condition that limits results to objects the caller owns, so an object outside that scope behaves as missing.

## Mechanism: combine operation and resource checks

A scope expresses permission for a class of operation, such as writing notes. A role often groups permissions for an organizational function. A tenant boundary separates customer or workspace data. Ownership identifies the principal responsible for a particular object. These dimensions can overlap, but none should be assumed to imply all the others.

FastAPI's SecurityScopes carries the scopes required by the endpoint into a dependency. The dependency verifies that the synthetic credential includes those scopes. The route then looks up the object within the verified tenant and owner context. That second check is necessary even when the scope is correct.

The example uses fixed opaque fixture tokens to focus on authorization. They are not JWTs, and the tokenUrl declaration does not create an OAuth server. Cryptographic authentication was tested in the preceding chapter. Keeping that boundary explicit prevents a short teaching fixture from being mistaken for a production identity implementation.

## Worked case: the owner with the required scope

The owner has a credential containing both read and write scopes. The dependency admits the write operation. The route finds the note, checks its tenant and owner against the verified identity, then updates the title. The program asserts the successful response and the final stored title.

The identity comes from the credential mapping, not a request field named owner or tenant. A client may choose which resource to request, but it cannot choose the authority under which the server performs that request. Real database queries should include the authorized scope in their predicates rather than fetching a globally visible row and hoping later code remembers to filter it.

For batch operations, apply the same rule to every affected row. Checking the first object and assuming the rest share its owner is a common source of partial unauthorized writes.

## Worked case: distinguish three refusals

An unknown credential receives 401 because identity is not established. The owner's read-only credential receives 403 because its operation scope is insufficient. Another tenant's writer receives 404 because the requested note is outside that caller's visible resource scope.

The 404 policy avoids revealing whether another tenant's identifier exists. Some APIs use 403 under a different disclosure policy; the choice must be consistent and documented. What matters here is that the operation has no unauthorized side effect and that the tests exercise all three boundaries.

A numerical identifier is not an authorization secret. Sequential or guessable IDs can be perfectly acceptable when every access is scoped correctly. Replacing them with random IDs can reduce enumeration convenience, but it does not repair a missing ownership predicate.

## Worked example: checking scopes as a set, not as a substring

```python
granted_claim = "notes:read notes:write-drafts"
required = "notes:write"

print(required in granted_claim)
print(required in granted_claim.split())
granted = set(granted_claim.split())
print({"notes:read"} <= granted, {"notes:read", "notes:write"} <= granted)
```

Expected output:

```text
True
False
True False
```

An OAuth access token usually carries its scopes as one space separated string. Testing `required in granted_claim` searches characters, so `notes:write` matched inside `notes:write-drafts` and a draft-only token would pass a full write check. Splitting the claim into tokens and comparing sets fixes it, which is exactly what the lesson's `authorize` dependency does with `issubset`. Even a correct scope check only says what kind of action the token may attempt; the ownership and tenant comparison inside `update` still decides which note it may touch.

## Failure diagnosis and discussion

**Why does a write scope not authorize every write?** The scope names a capability class. Resource ownership, tenant membership and business state further restrict where that capability applies.

**Should authorization live only in the UI?** No. The server must enforce it for every entrypoint, including direct HTTP calls, background jobs and administrative paths that share the same domain operation.

If one tenant can see another's data, inspect query scoping and cached-result keys. A cache keyed only by resource ID can bypass otherwise correct per-request filtering. Continue with files and streaming, where filesystem identity and response lifetime create additional resource boundaries.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
