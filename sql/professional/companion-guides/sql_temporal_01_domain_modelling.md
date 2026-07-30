# SQL-TEMPORAL-01 — Temporal and Domain Modelling

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisites:** `sql-found-01`, `sql-types-01`, `sql-prog-01`,
  `sql-test-01`, and `sql-39`
- **Prerequisites:** [SQL-FOUND-01](sql_found_01_relational_design.md),
  [SQL-TYPES-01](sql_types_01_native_types_search.md),
  [SQL-PROG-01](sql_prog_01_routines_triggers.md),
  [SQL-TEST-01](sql_test_01_contracts_migrations.md), ranges, triggers, and
  [SQL Day 39 transaction/advisory-lock concepts](../../postgres-60day/companion-guides/day39_locks_deadlocks.md).
- **Artifacts:** [learner SQL](../lessons/sql_temporal_01_domain_modelling.sql) ·
  [solution reasoning](../solutions/sql_temporal_01_domain_modelling_solutions.md) ·
  [executable solution](../solutions/sql_temporal_01_domain_modelling_solutions.sql)

Run:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_temporal_01_domain_modelling.sql
```

The default is offline, fixed-time, and rollback-safe. It inspects but never
enables `btree_gist`.

## Learning objectives

- Distinguish valid and system time and query bitemporal state as-of two clocks.
- Enforce half-open non-overlap and compare built-in/advisory with exclusion
  constraints.
- Model an append-only correction ledger and produce legal-hold-aware retention
  eligibility without silently deleting evidence.

## Vocabulary and concepts

- **Valid time:** when a fact is true in the modeled domain.
- **System time:** when the database recorded/believed that version.
- **Bitemporal:** tracks both valid and system intervals.
- **As-of query:** asks state at a chosen valid and/or system instant.
- **Half-open interval:** `[lower,upper)`, avoiding double membership at adjacent
  boundaries.
- **Exclusion constraint:** prevents rows whose indexed operators conflict.
- **Ledger:** append-only record where correction uses reversal/new entries.
- **Idempotency key:** stable uniqueness key preventing duplicate append.
- **Retention class:** approved minimum duration and policy basis.
- **Legal hold:** policy override preventing eligible deletion.

## Worked example / walkthrough

The term-version grain is one recorded version of one customer's fact. A
February-valid rate first enters the system March 1. On March 10, the old system
period is closed and a corrected row begins. Querying valid February 15 as known
March 5 returns 10; as known March 15 returns 12. History is appended/closed,
not overwritten.

Both periods use `[lower,upper)`. Adjacent valid terms ending/starting April 1
do not overlap. NULL upper system bound means currently believed. Production
models must define clock source, time zone, late arrival, whether valid gaps are
allowed, and who may correct history.

Per-key exclusion normally uses `btree_gist`:

```sql
-- Optional, only after btree_gist is approved and installed:
EXCLUDE USING gist (
    customer_key WITH =,
    valid_period WITH &&
) WHERE (upper_inf(system_period))
```

The default does not enable the extension. Its trigger obtains a transaction
advisory lock derived from customer key, then rejects overlaps among current
system rows. The lock closes a common concurrent check-then-insert race, though
hash collisions can serialize unrelated keys. Declarative exclusion is easier
to inspect and harder to bypass; either design needs migration/concurrency tests.

A global maintenance table demonstrates built-in range-only GiST exclusion.
Adjacent windows succeed while overlap would fail.

The change ledger rejects UPDATE/DELETE. A correction appends a reversal with
unique idempotency key and reference to the original. Append-only does not prove
truth or authorization; ownership, signing/tamper controls, reconciliations, and
retention still matter.

Retention rules are data with policy basis. The query produces candidates at a
fixed review timestamp and excludes legal holds. It does not delete. Actual
deletion/anonymization requires approved scope, referential impact, audit,
backup-copy handling, dry run, and bounded recoverability.

## Exercises

Complete all twelve prompts. Begin with retroactive bitemporal correction, boundary tests,
optional exclusion design, ledger reversal, held-retention workflow, and an
explicit domain-assumption record; then cover civil time, three clocks, Type-2
joins, temporal parents, gaps/overlaps, and hold-aware archival. Add negative
controls for overlap, mutation, duplicate idempotency, and held deletion.

For every temporal answer, name the clock, zone, lower/upper inclusivity,
late-arrival policy, overlap/gap rule, correction authority, and audit evidence:

1. **Retroactive correction:** compare valid-at/known-at answers before and
   after the recorded correction.
2. **Range boundaries:** test every upper endpoint and require at most one row.
3. **Overlap enforcement:** compare an optional exclusion constraint with the
   locking trigger fallback.
4. **Ledger reversal:** append rather than update and verify idempotency and
   reversal links.
5. **Retention decision:** preserve approver, reason, time, hold, and immutable
   audit without deleting fixtures.
6. **Assumption register:** document time, authority, lateness, gaps/overlaps,
   privacy/deletion, ledger meaning, and correction roles.
7. **Civil time:** test ambiguous/nonexistent DST times while retaining source
   zone and UTC instant.
8. **Three clocks:** separate event, ingestion, and processing time; define
   watermark, lateness, correction, and notification.
9. **Type-2 join:** use business/surrogate keys and half-open effective periods;
   require at most one match per fact.
10. **Temporal parent:** design period containment, concurrency protection,
    deferred checking, and repair.
11. **Gap/overlap report:** use deterministic window/multirange logic and define
    adjacency, duplicates, and empty periods.
12. **Archival:** plan partition detach, legal-hold exceptions, verification,
    protected storage, restore tests, and deletion proof.

## Self-check

- Can the same valid date return different facts at different system times?
- Does every adjacent upper boundary match at most one row?
- Is per-key overlap safe under concurrent writers?
- Is history corrected by append/close rather than overwrite?
- Are ledger idempotency and reversal references enforced?
- Is retention eligibility separate from destructive execution?
- Do legal hold and policy basis appear in evidence?
- Does rollback remove schema, triggers, locks, and fixture data?

## Common pitfalls

- One `updated_at` timestamp is not bitemporal history.
- Inclusive upper bounds double-count adjacent periods.
- `LIMIT 1` hides overlapping history instead of enforcing it.
- A trigger overlap check without serialization races under concurrency.
- System time based on application clocks can arrive out of order.
- Append-only data can still contain false/unauthorized events.
- Retention automation without holds and backup policy can violate obligations.
- “Delete after N days” ignores referential, audit, replica, and backup copies.
- Range/exclusion indexes add write/lock cost that needs measurement.

## Next step

Use [SQL-TEST-01](sql_test_01_contracts_migrations.md) to freeze boundary,
overlap, correction, and retention contracts; use
[SQL-REPL-01](sql_repl_01_cdc_high_availability.md) to propagate immutable
versioned events idempotently; and use
[SQL-OPS-02](sql_ops_02_backup_restore_recovery.md) to rehearse recovery without
erasing required historical evidence. This completes the shared PostgreSQL
professional specialization path.
