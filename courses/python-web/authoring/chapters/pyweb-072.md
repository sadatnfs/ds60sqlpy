## Starting point and result

The three frameworks solve overlapping problems with different abstractions. This final chapter compares them through concrete request, state and lifecycle contracts rather than declaring one universally best. The review uses the finite references and the owned service lab to explain what each layer contributes and what remains outside the local qualification boundary.

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

## Interview discussion and transfer

**How would you choose a framework for a new service?** Start with required interfaces, team familiarity, data model, administrative needs, async/streaming demands and operational constraints. Demonstrate a representative workflow and evaluate maintenance and failure behavior rather than comparing slogans.

**What evidence would you require before shipping a change?** Identify its affected contract, run meaningful accepted/refused cases, inspect side effects and recovery, then qualify the actual serving surface and saved state when those layers change.

For future work, extend the owned project deliberately: add one domain operation, define its identity and authorization, write the expected transaction behavior, and test failure/recovery before claiming delivery. The original Python, SQL, Docker and data-engineering routes provide the deeper language, storage and systems foundations behind these web decisions.
