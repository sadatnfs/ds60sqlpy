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
