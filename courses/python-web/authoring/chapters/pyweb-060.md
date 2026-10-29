## Starting point and result

Framework interfaces often stay the same while their backends change the operational meaning. A cache can live in one process or a shared service; email can be captured in memory or delivered through a server; a task can execute eagerly or through a durable worker. This chapter makes those backend distinctions explicit.

## Mechanism: interface success has a scope

Django's cache API provides get, set and delete over a configured backend. A key should include the dimensions that affect its value, such as tenant, user or schema version. The local-memory backend is useful for finite tests but does not provide cross-process coordination or persistence.

The locmem email backend appends messages to an in-process outbox. Send_mail can therefore succeed without sending anything to an external address. This is desirable in a classroom fixture, but it proves message construction and backend acceptance rather than actual SMTP delivery.

Celery eager mode runs a registered task synchronously in the local process. Its task API remains real, yet no independent worker or durable broker is involved. The program prints those limitations directly to prevent a successful method call from being mistaken for service qualification.

## Worked case: cache a value and invalidate it

The program stores a small summary under a versioned user-specific key and retrieves the expected value. It then deletes the key and confirms a cache miss. This checks actual backend behavior and the application's intended invalidation operation.

A cached representation can become stale when underlying data changes. Deleting or versioning the key is part of the write/read contract, not an optional performance detail. A cache keyed only by a global name can also leak one user's result to another if identity affects the value.

The fixture does not claim a distributed cache. If several server processes use separate local-memory backends, each can retain a different value. A correct shared-state design must choose an appropriate backend and define consistency expectations.

## Worked case: inspect email and execute an eager task

Send_mail builds one synthetic message and the test inspects the in-memory outbox's subject and count. The address uses an invalid example domain, and no network mail is sent. A Celery task computes a deterministic summary and its eager result is checked against an independent expected dictionary.

These tests are valuable because message content and task logic can be wrong before any network integration is involved. They are incomplete for delivery and recovery. Actual email acceptance would require a controlled mail service, while durable task acceptance would require broker/worker lifecycle and duplicate-effect checks.

A task should receive serializable values or stable record identities. Passing request objects, database sessions or open files assumes a shared process lifetime that a real worker does not have. The later outbox and workshop chapters use durable identities to cross that boundary.

## Failure diagnosis and discussion

**Why did an email test pass but no message arrive?** The configured backend may capture messages locally, or the test may only prove server acceptance rather than final delivery. Identify the actual backend and observation point.

**Why does a task work eagerly but fail in a worker?** Serialization, imports, environment, process ownership and external dependencies differ. Eager execution bypasses those boundaries.

If cache results cross user boundaries, inspect key design before adding more invalidation. If tasks disappear on restart, inspect durable acceptance and unfinished-work discovery. Continue with deployment checks, which identify configuration risks but likewise need careful interpretation of what they do and do not establish.
