## Starting point and result

A database transaction groups changes that must succeed or fail together. An ORM session coordinates Python objects with that database work, but its lifecycle must still be explicit. This chapter uses real SQLAlchemy sessions and SQLite to compare a committed batch with a batch that violates a uniqueness constraint.

## Mechanism: transaction boundaries belong around the operation

The Item table has a generated primary key and a unique title. A session factory creates a session for each operation. `Session.begin()` supplies a transaction context: normal exit commits, while an exception rolls back. The handler catches an IntegrityError outside that context and translates it to a controlled 409 response.

`flush()` sends pending changes to the database before the context exits. It can expose a constraint failure while the handler still controls the operation. Flushing is not the same as committing. A later failure within the transaction can still roll back earlier flushed statements.

The fixture uses a single shared in-memory SQLite connection through StaticPool. This keeps the tiny database available across its request sessions. It is a deliberate test arrangement, not a production concurrency/pooling recommendation. PostgreSQL connection pools and transaction behavior receive their own workshop acceptance.

## Worked case: a complete batch commits

The program first creates an existing title, then submits the distinct titles `one` and `two` together. Both requests return 201. A read through a fresh session sees all three titles in ID order, proving that the data survived beyond the write session.

The input is also bounded before database work: the handler accepts one to three nonempty title strings within the configured length. Those checks provide a useful public error contract, while the unique constraint remains the authoritative database rule for duplicates. Concurrent callers must not rely on a separate “does this title already exist?” query as a replacement for that constraint.

## Worked case: a duplicate rolls back the whole batch

The next request contains `temporary` followed by the already existing title. The database rejects the duplicate. The handler returns 409, and a subsequent read confirms that `temporary` was not committed either. This is the important invariant: failure of the operation does not leave a partial result that looks like a successful creation.

A transaction is not an automatic solution for effects outside the database. Sending an email between two statements would not be undone by rolling back those statements. The later outbox chapter addresses that coordination problem explicitly.

## Failure diagnosis

A session left in a failed transaction may reject further operations until rolled back or closed. Reusing one global session across unrelated requests can therefore produce confusing failures and concurrency problems. A context-managed per-operation session makes its lifecycle easier to reason about.

A database exception should not be returned wholesale to the client. It can contain SQL, parameters or internal names. Translate known domain conflicts to a stable public response and retain appropriate diagnostics separately. Unexpected failures need a separate server-error path.

## Interview discussion

**Why keep the unique constraint if the application validates first?** Application checks improve feedback, but another transaction can change the database between a check and an insert. The database constraint enforces the invariant at the point of mutation.

**Does `flush()` make changes durable?** It sends statements within the current transaction. Commit establishes the transaction outcome; a later rollback can still discard flushed changes.

## Next step

Design deterministic queries and pagination. Correct transactions do not prevent a client from seeing an inconsistent sequence if page boundaries depend on changing offsets.
