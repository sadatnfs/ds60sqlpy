## Starting point and result

A service can commit a business change and crash before notifying another component. It can also send a notification successfully and lose the acknowledgement. This chapter implements a small transactional outbox and an idempotent consumer using actual SQLite transactions to expose both problems clearly.

## Mechanism: commit intent alongside the business effect

An outbox stores a message or event in the same database transaction as the business operation. If the transaction commits, both the operation and the notification intent exist. If it rolls back, neither exists. A separate dispatcher can later read the outbox and deliver its entries.

This pattern does not make external delivery exactly once. A dispatcher can deliver and crash before marking completion, causing a retry. The consumer therefore records an event identity in the same transaction as its own effect. Repeated delivery of that identity has no second effect.

The fixture uses one SQLite connection with separate tables for orders, outbox entries, applied identities and a total. This is a real transaction test but not a distributed broker demonstration. The owned workshop extends the principle to a persistent PostgreSQL-backed job ledger and an independently running worker.

## Worked case: fail between the order and outbox insert

The accept function inserts an order, then deliberately raises before writing the outbox entry. The transaction context rolls the order back. The program asserts that the orders table remains empty and that the expected controlled failure actually occurred.

A later successful command inserts both the order and its outbox entry. Repeating the same identity and amount returns the recorded outcome without another insert. Reusing the identity with a different amount raises a conflict instead of silently treating a new command as an old one.

The payload comparison is part of the identity contract. A key alone does not tell the service whether a retry is semantically identical. Canonicalization or a stable digest can be used for larger inputs, but the fields included in that identity must be documented.

## Worked case: deliver twice, apply once

The consumer first inserts the event identity into the applied table. Only when that insert is new does it update the total. Both actions occur in one transaction. Two deliveries produce inserted counts 1 and 0, and the total increases only once.

The order of those operations matters. Recording the identity and then updating the total in separate transactions could lose the effect after a crash. Updating the total first and recording the identity later could duplicate it after a retry. Atomicity joins the decision and effect.

An external effect that cannot participate in the consumer's transaction needs its own idempotency/reconciliation mechanism. The outbox pattern does not magically make an arbitrary email or third-party API call transactional with the local database.

## Failure diagnosis and discussion

**Does at-least-once delivery mean duplicate business effects are inevitable?** No. A consumer can make its effect idempotent with a stable identity and atomic storage rule, as this fixture demonstrates.

**Can outbox entries be deleted immediately after sending?** Only under a deliberate delivery and retention policy. A lost acknowledgement, delayed retry or audit requirement may need the identity and outcome to remain available.

If an accepted operation has no notification intent, inspect transaction placement. If totals increase twice, inspect whether deduplication and the effect commit together. Continue with database plans and contention to understand the storage costs and concurrency behavior behind these guarantees.
