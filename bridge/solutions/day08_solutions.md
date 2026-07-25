# Bridge Day 8 — Solution notes

Complete the [capstone starter](../lessons/day08_production_capstone.py) before
reviewing [day08_solution.py](day08_solution.py).

## Recovery invariant

The reference loads one checkpoint, validates the complete extracted sequence,
and handles bounded batches in this order:

1. write the batch;
2. save the batch's last sequence;
3. record the successful write count.

If the second batch fails, the first batch's checkpoint remains durable. A
restart asks the extractor only for later sequences. The sink still needs an
idempotency key because a network failure can make write outcome uncertain.

Input validation occurs before the first effect. Sequences must be positive and
strictly increasing after the checkpoint, IDs unique within a run, and amounts
finite.

## Observability and security

Metrics use stable job and exception-type tags. Logs contain job name, counts,
and exception type—never the exception message, records, or connection strings.
The runner re-raises failure so an external scheduler can mark the run failed.

`validate_database_transport()` checks scheme, host, and remote TLS mode without
returning or echoing the URL. Local course connections may omit TLS; remote
hosts require `require`, `verify-ca`, or `verify-full`.

## Tradeoffs

- Saving a checkpoint after every batch reduces replay but increases checkpoint
  writes. Larger checkpoint intervals trade recovery work for throughput.
- The runner validates all extracted records in memory. A streaming design
  needs incremental order checks and bounded extraction.
- Omitting exception messages and tracebacks at this boundary protects secrets
  but reduces diagnostics. A protected error store can retain richer traces
  under an explicit access and retention policy.
- URL query validation is a minimum transport guard, not full security.
  Certificate validation, secret storage, role privileges, rotation, network
  policy, statement timeouts, and audit requirements belong in deployment.
- Exactly-once processing is not claimed. Checkpoint ordering plus an
  idempotent sink provides recoverable at-least-once behavior.

The strongest capstone evidence is the failure test: the second batch fails,
checkpoint `2` remains, and the next run processes only sequences `3` and `4`.
