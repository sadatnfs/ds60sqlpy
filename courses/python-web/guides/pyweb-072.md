# pyweb-072: End-to-end Python web engineering review

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-068`, `pyweb-070`, `pyweb-071`.

## Starting point and result

The three frameworks solve overlapping problems with different abstractions. This final chapter compares them through concrete request, state and lifecycle contracts rather than declaring one universally best. The review uses the finite references and the owned service lab to explain what each layer contributes and what remains outside the local qualification boundary.

## Key terms

- **WSGI:** The synchronous Python web server interface that Flask is built on, in which one call handles one request.
- **ASGI:** The asynchronous Python server interface that FastAPI uses, which also supports long-lived connections such as WebSockets.
- **Integrated framework:** A framework such as Django that ships its own ORM, migrations, authentication, forms and admin.
- **Ownership map:** A record of which component owns each piece of state: the database owns jobs, the worker owns progress and the browser owns its connection.

## Mechanism: choose abstractions around the application

Flask provides a compact WSGI application model with explicit extension choices. FastAPI centers typed request/response contracts and ASGI capabilities. Django supplies an integrated application structure, ORM, migrations, authentication, forms and admin. All three still need correct authorization, transaction ownership, error handling and deployment configuration.

The shared lab gives each framework separate sessions and notes while using the same local PostgreSQL service. Flask/FastAPI use the original small session/store boundary; Django uses its framework auth/session/CSRF and ORM. Comparing those implementations makes the amount of explicit application code visible without assuming fewer lines imply better behavior.

Long-lived work is separated from request serving. The FastAPI job endpoint commits durable intent, the worker owns calculation progress, and SSE exposes committed events. The browser owns its connection and selected job identity, not the database job itself. That ownership map is more durable than memorizing individual decorators.

## Worked case: trace one authorized note from browser to storage

Sign in as Alice on one framework page, create a note and inspect the HTTP result. The input boundary accepts a bounded title. Authentication establishes identity. CSRF/origin checks admit the browser write. The server assigns owner and commits the database operation. The response exposes the intended public fields.

Then sign in as Bob and request the same identifier through a controlled client. The server must refuse disclosure even though the identifier is known. Compare that result with the collection endpoint, which must apply the same owner scope. A good review covers every entrypoint rather than only the happy path visible in the UI.

The finite tests help diagnose the individual mechanism when this integrated flow fails. The service receipt establishes actual local HTTP/database behavior, while browser observations establish rendering and asset delivery. Neither should be substituted for the other.

## Worked case: lose a connection and replace a process

Create a held FastAPI job, observe an event, disconnect the stream and release the job. Reconnect using the stored identity and observe the completed result. Stop/resume or replace the owned application containers, then use verify to read the earlier receipt's note/job identities.

This case distinguishes transient connection state, process state and persistent data. It also explains why retries need identities: a client can lose the response even when the effect committed. Repeating creation is not a valid substitute for reading the prior outcome when proving recovery.

The local lab does not establish public TLS, a distributed queue cluster, cross-region failover or production-scale throughput. Those are legitimate extensions with their own topology, workload and failure evidence. Naming those boundaries is part of sound engineering, not a reduction in the value of the local tests.

## Worked example: the layer that refuses each request in the note flow

```python
def review(request, notes):
    if not request.get("user"):
        return 401, "authentication"
    if request["method"] == "POST":
        if request.get("csrf") != "issued-token":
            return 403, "csrf"
        if set(request["form"]) != {"title"} or not 1 <= len(request["form"]["title"]) <= 40:
            return 400, "input"
        notes.append({"owner": request["user"], "title": request["form"]["title"]})
        return 201, "storage"
    visible = [n["title"] for n in notes if n["owner"] == request["user"]]
    return 200, visible


notes = []
cases = [
    {"user": None, "method": "GET"},
    {"user": "alice", "method": "POST", "csrf": None, "form": {"title": "Private"}},
    {
        "user": "alice",
        "method": "POST",
        "csrf": "issued-token",
        "form": {"title": "Private", "owner": "bob"},
    },
    {"user": "alice", "method": "POST", "csrf": "issued-token", "form": {"title": "Private"}},
    {"user": "bob", "method": "GET"},
    {"user": "alice", "method": "GET"},
]
for case in cases:
    print(review(case, notes))
```

Expected output:

```text
(401, 'authentication')
(403, 'csrf')
(400, 'input')
(201, 'storage')
(200, [])
(200, ['Private'])
```

Each request is stopped by a different boundary, and the second value names it, which is the habit the review asks for when the integrated flow fails: say which layer decided. The order matters too. The CSRF check runs before input validation, so a cross site page learns nothing about which fields the form accepts, and the owner comes from the session, never the body. Bob's collection read returns an empty list rather than Alice's note because the listing applies the same owner scope as storage. Map each line to the framework you choose: Flask, FastAPI and Django all have a distinct place for every one of these decisions.

## Interview discussion and transfer

**How would you choose a framework for a new service?** Start with required interfaces, team familiarity, data model, administrative needs, async/streaming demands and operational constraints. Demonstrate a representative workflow and evaluate maintenance and failure behavior rather than comparing slogans.

**What evidence would you require before shipping a change?** Identify its affected contract, run meaningful accepted/refused cases, inspect side effects and recovery, then qualify the actual serving surface and saved state when those layers change.

For future work, extend the owned project deliberately: add one domain operation, define its identity and authorization, write the expected transaction behavior, and test failure/recovery before claiming delivery. The original Python, SQL, Docker and data-engineering routes provide the deeper language, storage and systems foundations behind these web decisions.

## Worked project reference

This is a complete reading/project reference. It has no ordinary pad Run action. Prepare and execute any linked project through its own documented entrypoint. A command reference or hand calculation is not an execution receipt. Runtime: `reading`.

Compare the [Flask/FastAPI/Django web-lab source](../projects/web-lab/README.md)
against the completed finite reference programs.

| Claim | Required evidence |
| --- | --- |
| Request/schema rule | Real finite framework client and rejected/accepted cases |
| Database invariant | Actual transaction/constraint result and side-effect inspection |
| HTTP/WS/SSE delivery | Owned server acceptance with actual socket observations |
| Offline UI/docs | Browser asset requests and visible interaction |
| Durable notes/jobs | Prior identity readback after stop/resume and replacement |
| Public TLS/multi-host scale | Separate deployment evidence, not supplied by this local lab |

Run `./workshop check` once to create synthetic acceptance records. After stopping,
resuming or replacing the owned services, run `./workshop verify` to read those
same records. Explain which component owns each request, connection, transaction,
job and durable state item, and identify the test that would expose a lost effect.

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/)
