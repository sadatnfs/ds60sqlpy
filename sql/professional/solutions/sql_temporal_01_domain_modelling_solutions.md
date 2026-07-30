# SQL-TEMPORAL-01 Solutions — Temporal and Domain Modelling

Run:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_temporal_01_domain_modelling_solutions.sql
```

The solution is fixed-time and rolls back.

## Exercise 1 — Retroactive correction

Close the prior system period at April 1 and append a new version whose valid
period still begins January 1. Valid February 15 as known March 15 returns the
March version; the same valid date as known April 2 returns the April correction.
This answers “what did we know then?” without rewriting knowledge history.

## Exercise 2 — Boundaries

Test `lower`, just before upper, and exactly upper for both date and timestamp
ranges. `[lower,upper)` includes lower and excludes upper, so adjacent versions
can meet at one boundary without double matching. Assert match count at most one,
not merely choose one with ORDER/LIMIT.

## Exercise 3 — Exclusion versus fallback

With approved `btree_gist`, a partial GiST exclusion combines
`customer_key WITH =` and `valid_period WITH &&` for current system rows.
PostgreSQL enforces conflicts under concurrency. The fallback advisory-lock
trigger qualifies the query and serializes one hashed key before checking;
hash collisions reduce concurrency, and every write path/trigger enablement must
remain controlled.

## Exercise 4 — Reversal chain

Entries L-1 (+5), L-2 (-5 reversing L-1), and L-3 (+5 correcting/reversing L-2)
sum to +5 without UPDATE. Unique idempotency keys prevent duplicate append and
foreign keys preserve reversal references. Domain policy should prevent
multiple unauthorized reversals of one entry if that is invalid.

## Exercise 5 — Hold decisions

The decision log appends who, reason, action, and time. Current hold state is
derived from the latest authorized decision. Deletion still requires retention
age, no current hold, approval, dependency/backup review, and an immutable
execution audit. The course solution records decisions but deletes nothing.

## Exercise 6 — Domain assumptions

Record business time zone and clock authority; valid/system boundary convention;
late-arrival/correction authority; allowed gaps/overlaps; customer identity;
money/unit semantics; ledger reconciliation and reversal policy; retention/legal
basis; hold ownership; deletion versus anonymization; and how replicas/backups
honor erasure and audit duties.

## Edge cases

- Infinity/open bounds need explicit API serialization.
- Clock corrections and transaction timestamp versus wall clock differ.
- Backdated facts can change previously published metrics.
- Temporal indexes and history retention grow write/storage cost.

