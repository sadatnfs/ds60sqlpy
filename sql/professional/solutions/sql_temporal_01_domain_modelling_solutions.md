# SQL-TEMPORAL-01 Solutions — Temporal and Domain Modelling


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_temporal_01_domain_modelling_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_temporal_01_domain_modelling_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Valid time, System time, Bitemporal, As-of query, Half-open interval, Exclusion constraint. Its worked-model focus is:
The term-version grain is one recorded version of one customer's fact. A February-valid rate first enters the system March 1. On March 10, the old system period is closed and a corrected row begins. Querying valid February 15 as known March 5 returns 10; as known March 15 returns 12. History is appended/closed, not overwritten.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 1, Close only the current `CUS-100` row whose `valid_period` contains `2026-02-15` at system time `2026-04-01 00:00+00`, then append the corrected rate as a new current `pro_temporal_lab.customer_terms` row.
- **Expected result/shape:** For sql-temporal-01 Exercise 1, One row per `(valid_on, system_as_of)` probe, with `valid_on`, `system_as_of`, `term_version_id`, `monthly_rate`, and `recorded_reason`, ordered by `system_as_of`; March 15 returns the prior rate and April 2 returns the retroactive correction.
- **Independent verification:** For sql-temporal-01 Exercise 1, Group the as-of join by both probe columns and require exactly one match per probe. Prove the earlier system-period row still exists and that no current valid periods overlap for `CUS-100`.

## Exercise 2 — Boundaries

Test `lower`, just before upper, and exactly upper for both date and timestamp
ranges. `[lower,upper)` includes lower and excludes upper, so adjacent versions
can meet at one boundary without double matching. Assert match count at most one,
not merely choose one with ORDER/LIMIT.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 2, Build an inline probe relation around every lower and upper bound in `pro_temporal_lab.customer_terms`: immediately before, exactly at, and immediately after each valid-date or system-time boundary.
- **Expected result/shape:** For sql-temporal-01 Exercise 2, One row per `probe_id`, with `valid_on`, `known_at`, `matching_versions`, and `expected_matches`, ordered by `probe_id`; no `matching_versions` value is greater than one.
- **Independent verification:** For sql-temporal-01 Exercise 2, Independently count matching `term_version_id` values for every probe. Require the old version to stop at the upper bound and an adjacent successor, when present, to begin there without a double match.

## Exercise 3 — Exclusion versus fallback

With approved `btree_gist`, a partial GiST exclusion combines
`customer_key WITH =` and `valid_period WITH &&` for current system rows.
PostgreSQL enforces conflicts under concurrency. The fallback advisory-lock
trigger qualifies the query and serializes one hashed key before checking;
hash collisions reduce concurrency, and every write path/trigger enablement must
remain controlled.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 3, Use the read-only `pg_available_extensions` result, the existing advisory-lock trigger, and a written (not executed) `btree_gist` exclusion constraint design for `customer_key WITH =, valid_period WITH &&`.
- **Expected result/shape:** For sql-temporal-01 Exercise 3, One comparison row per enforcement approach, with `approach`, `enforcement_mechanism`, `assumption_or_limit`, and `concurrent_failure_behavior`.
- **Independent verification:** For sql-temporal-01 Exercise 3, Explain which writes each approach locks or constrains, how a conflicting concurrent transaction fails, and what happens if an application writer bypasses the agreed advisory-lock protocol.

## Exercise 4 — Reversal chain

Entries L-1 (+5), L-2 (-5 reversing L-1), and L-3 (+5 correcting/reversing L-2)
sum to +5 without UPDATE. Unique idempotency keys prevent duplicate append and
foreign keys preserve reversal references. Domain policy should prevent
multiple unauthorized reversals of one entry if that is invalid.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 4, Append `LEDGER-102` to `pro_temporal_lab.change_ledger` as the exact same-subject, same-currency negation of `LEDGER-101`; set `reverses_entry_id` from the referenced row instead of hard-coding it.
- **Expected result/shape:** For sql-temporal-01 Exercise 4, One row per `ledger_entry_id`, with `idempotency_key`, `event_kind`, signed amount, `reverses_entry_id`, and a scalar reconciled amount, ordered by `ledger_entry_id`.
- **Independent verification:** For sql-temporal-01 Exercise 4, Require three rows and a reconciled amount of `5.00`. Prove an UPDATE, DELETE, duplicate `LEDGER-102` retry, second reversal of the same entry, and wrong-sign reversal all fail without changing the row count.

## Exercise 5 — Hold decisions

The decision log appends who, reason, action, and time. Current hold state is
derived from the latest authorized decision. Deletion still requires retention
age, no current hold, approval, dependency/backup review, and an immutable
execution audit. The course solution records decisions but deletes nothing.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 5, Create append-only `pro_temporal_lab.retention_decisions` with a stable decision idempotency key, `record_key`, decision, approver, reason, and authoritative `decided_at`. Lock per record and reject backdated decisions or a deletion approval while the latest decision is a hold.
- **Expected result/shape:** For sql-temporal-01 Exercise 5, One row per retained `record_key`, with the latest decision event/key, approver, reason, decision time, and `eligible_for_deletion_review`, ordered by `record_key`.
- **Independent verification:** For sql-temporal-01 Exercise 5, Prove decision UPDATE/DELETE and duplicate/backdated appends fail. Keep a held fixture ineligible, release another through an ordered event, and confirm no `retained_records` row is actually deleted.

## Exercise 6 — Domain assumptions

Record business time zone and clock authority; valid/system boundary convention;
late-arrival/correction authority; allowed gaps/overlaps; customer identity;
money/unit semantics; ledger reconciliation and reversal policy; retention/legal
basis; hold ownership; deletion versus anonymization; and how replicas/backups
honor erasure and audit duties.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 6, Use observed lesson behavior plus explicitly labeled assumptions for time zone, clock authority, lateness, overlap/gaps, correction authority, ledger units, retention/holds, and replicas/backups.
- **Expected result/shape:** For sql-temporal-01 Exercise 6, One row per assumption topic, with `topic`, `decision_or_assumption`, `evidence`, `owner`, and `failure_response`.
- **Independent verification:** For sql-temporal-01 Exercise 6, Every row names an accountable owner and an operational response; every claimed fact cites a query/catalog result, while policy not present in the repository is labeled as an assumption needing approval.

## Exercise 7 — Civil time and daylight saving

Store the authoritative instant as `timestamptz` and retain the IANA zone name
used to interpret/display civil time. A fixed offset has no DST rules; a bare
timestamp cannot identify which occurrence an ambiguous fall-back time means.

Detect/reject nonexistent spring-forward times and require an explicit
earlier/later-offset policy for ambiguous input. Test both transitions for the
supported zone database/version.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 7, Use three keyed civil-time cases in `America/Los_Angeles`: spring `2026-03-08 02:30`, fall `2026-11-01 01:30`, and one ordinary time. Round-trip candidate UTC instants rather than trusting one silent `AT TIME ZONE` default.
- **Expected result/shape:** For sql-temporal-01 Exercise 7, One row per `case_id`, with `local_time`, `zone_name`, `civil_time_status`, candidate instants, PostgreSQL's default interpreted instant, and `resolution_policy`, ordered by `case_id`.
- **Independent verification:** For sql-temporal-01 Exercise 7, Require exactly one `nonexistent`, one `ambiguous`, and one `ordinary` case. A nonexistent time has zero round-trip candidates; an ambiguous time has more than one and requires explicit disambiguation.

## Exercise 8 — Event, ingestion, and processing clocks

Event time is source occurrence, ingestion time is arrival, and processing time
is computation. A watermark such as maximum observed event time minus allowed
lateness closes windows only under a documented source/partition policy.

Beyond-window data should be quarantined or applied as a versioned
correction/retraction. Publish metric version, as-of/watermark, changed keys, and
downstream recomputation/notification evidence.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 8, Create `pro_temporal_lab.timed_events(event_key, event_at, ingested_at, processed_at)` with one on-time and one late event. Use a fixed 15-minute example lateness allowance.
- **Expected result/shape:** For sql-temporal-01 Exercise 8, Exactly one summary row with `event_count`, `maximum_event_time`, `example_watermark`, `maximum_arrival_delay`, `maximum_processing_delay`, `events_behind_watermark`, and the correction policy.
- **Independent verification:** For sql-temporal-01 Exercise 8, Recompute arrival and processing delays row by row, require the late fixture to fall behind the watermark, and describe a stable window/version identity for the corrected aggregate.

## Exercise 9 — Type-2 as-of dimension join

Give each version a surrogate key, stable business key, half-open effective
range, and correction metadata. Join a fact where business keys match and the
range contains fact time; persist the resolved surrogate when interpretation
must never drift.

Enforce/report no overlap and assert each fact has at most or exactly one match
according to missing-dimension policy. A current flag must agree with range
state.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 9, Create `pro_temporal_lab.customer_dimension` with surrogate `customer_version_id`, business key, half-open `effective_period`, `is_current`, segment, correction reason, and record time; join `pro_temporal_lab.order_facts` on business key plus range containment.
- **Expected result/shape:** For sql-temporal-01 Exercise 9, One row per `order_key`, with `ordered_on`, `customer_version_id`, segment, effective period, current marker, and correction metadata, ordered by `order_key`.
- **Independent verification:** For sql-temporal-01 Exercise 9, Require output count to equal fact count and group by `order_key` with `HAVING count(customer_version_id) > 1` returning no rows. Inject one overlapping dimension row, prove the diagnostic catches it, then roll it back.

## Exercise 10 — Temporal referential integrity

The child period must be contained by an allowed parent period, not merely share
a key. A trigger can lock a stable business-key namespace, query containment,
and reject gaps under concurrency.

Exclusion constraints prevent overlap but do not alone prove containment.
Deferred/bulk loading needs an explicit validation and quarantine/repair gate;
test parent shrink/delete and concurrent changes.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 10, Cover child insert/update, parent shrink/delete, bulk historical repair, and deferred validation. State the shared business-key locking namespace and containment predicate for each write path.
- **Expected result/shape:** For sql-temporal-01 Exercise 10, One row per write path, with `write_path`, `concurrency_or_validation_control`, and `failure_response`.
- **Independent verification:** For sql-temporal-01 Exercise 10, Walk through two concurrent transactions for both child insertion and parent shrink. Identify the lock acquired first and show that cutover is blocked whenever the final containment diagnostic is nonempty.

## Exercise 11 — Gap and overlap report

Order nonempty periods by lower bound, upper bound, stable ID and compare each
lower bound with the running maximum prior upper. Lower means overlap, greater
means gap, equal means adjacency. Plain `lag(upper)` can miss overlap hidden by
an earlier long interval.

Multirange aggregation/subtraction can expose coverage compactly. Report
duplicates/empty/inverted periods separately and define adjacency policy.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 11, Use keyed fixtures containing duplicate, overlapping, adjacent, gapped, empty, and unbounded-upper `daterange` values. Preserve unbounded prior coverage with `upper_inf()` or an explicit infinity sentinel.
- **Expected result/shape:** For sql-temporal-01 Exercise 11, One row per `period_id`, with `business_key`, `valid_period`, `has_unbounded_upper`, duplicate count, prior maximum upper bound, and `relationship_to_prior_coverage`, ordered by bounds and `period_id`.
- **Independent verification:** For sql-temporal-01 Exercise 11, Require explicit `duplicate`, `empty`, `gap`, `adjacent`, and `overlap` outcomes. Add a bounded period after an unbounded range and prove it is classified as overlap rather than first/gap.

## Exercise 12 — Partition archive under hold

Inventory retention and holds before detach. If one held row blocks an expirable
partition, move/repartition only through audited review. Verify counts/checksums,
dependencies, indexes, encryption/access, manifest, and test restore.

Keep archive discoverable to authorized recovery/legal processes, propagate hold
decisions to replicas/backups, and record deletion evidence. Partition age alone
is not authorization to erase.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 12, Design ordered phases for inventory, hold gate, detach, encrypted archive, reconciliation, restore test, and eventual source deletion.
- **Expected result/shape:** For sql-temporal-01 Exercise 12, One row per `step_number`, with `phase`, `required_control`, and `required_evidence`, ordered by `step_number`.
- **Independent verification:** For sql-temporal-01 Exercise 12, Each phase names a stop condition. Trace one active-hold fixture through every maintained copy and require a successful isolated restore plus source/archive count and checksum reconciliation before deletion.

## Edge cases

- Infinity/open bounds need explicit API serialization.
- Clock corrections and transaction timestamp versus wall clock differ.
- Backdated facts can change previously published metrics.
- Temporal indexes and history retention grow write/storage cost.
