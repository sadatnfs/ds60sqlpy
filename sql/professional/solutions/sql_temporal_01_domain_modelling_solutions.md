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

## Exercise 7 — Civil time and daylight saving

Store the authoritative instant as `timestamptz` and retain the IANA zone name
used to interpret/display civil time. A fixed offset has no DST rules; a bare
timestamp cannot identify which occurrence an ambiguous fall-back time means.

Detect/reject nonexistent spring-forward times and require an explicit
earlier/later-offset policy for ambiguous input. Test both transitions for the
supported zone database/version.

## Exercise 8 — Event, ingestion, and processing clocks

Event time is source occurrence, ingestion time is arrival, and processing time
is computation. A watermark such as maximum observed event time minus allowed
lateness closes windows only under a documented source/partition policy.

Beyond-window data should be quarantined or applied as a versioned
correction/retraction. Publish metric version, as-of/watermark, changed keys, and
downstream recomputation/notification evidence.

## Exercise 9 — Type-2 as-of dimension join

Give each version a surrogate key, stable business key, half-open effective
range, and correction metadata. Join a fact where business keys match and the
range contains fact time; persist the resolved surrogate when interpretation
must never drift.

Enforce/report no overlap and assert each fact has at most or exactly one match
according to missing-dimension policy. A current flag must agree with range
state.

## Exercise 10 — Temporal referential integrity

The child period must be contained by an allowed parent period, not merely share
a key. A trigger can lock a stable business-key namespace, query containment,
and reject gaps under concurrency.

Exclusion constraints prevent overlap but do not alone prove containment.
Deferred/bulk loading needs an explicit validation and quarantine/repair gate;
test parent shrink/delete and concurrent changes.

## Exercise 11 — Gap and overlap report

Order nonempty periods by lower bound, upper bound, stable ID and compare each
lower bound with the running maximum prior upper. Lower means overlap, greater
means gap, equal means adjacency. Plain `lag(upper)` can miss overlap hidden by
an earlier long interval.

Multirange aggregation/subtraction can expose coverage compactly. Report
duplicates/empty/inverted periods separately and define adjacency policy.

## Exercise 12 — Partition archive under hold

Inventory retention and holds before detach. If one held row blocks an expirable
partition, move/repartition only through audited review. Verify counts/checksums,
dependencies, indexes, encryption/access, manifest, and test restore.

Keep archive discoverable to authorized recovery/legal processes, propagate hold
decisions to replicas/backups, and record deletion evidence. Partition age alone
is not authorization to erase.

## Edge cases

- Infinity/open bounds need explicit API serialization.
- Clock corrections and transaction timestamp versus wall clock differ.
- Backdated facts can change previously published metrics.
- Temporal indexes and history retention grow write/storage cost.
