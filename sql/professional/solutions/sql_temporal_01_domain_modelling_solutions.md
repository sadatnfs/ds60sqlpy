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

- **Inputs/evidence:** For sql-temporal-01 Exercise 1, complete the retroactive correction written analysis and support its claims with read-only evidence from `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-temporal-01 Exercise 1, expected output: a completed the retroactive correction written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Independent verification:** For sql-temporal-01 Exercise 1, check the retroactive correction written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-temporal-01 Exercise 1, check the retroactive correction written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Clause check:** For sql-temporal-01 Exercise 1, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows` or label it as proposed policy.
- **Alternative/trade-off:** For sql-temporal-01 Exercise 1, the chosen form is justified by this lesson-specific rationale: Close the prior system period at April 1 and append a new version whose valid period still begins January 1. Evaluate another form against the concrete expected result (a completed the retroactive correction written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 2 — Boundaries

Test `lower`, just before upper, and exactly upper for both date and timestamp
ranges. `[lower,upper)` includes lower and excludes upper, so adjacent versions
can meet at one boundary without double matching. Assert match count at most one,
not merely choose one with ORDER/LIMIT.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 2, read from `pro_temporal_lab.facts`. Build the answer toward `valid_on`, `known_at`, and `matching_versions`; keep `valid_on`, and `known_at` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-temporal-01 Exercise 2, expected output: one row per `valid_on`, and `known_at`. The final columns are `valid_on`, `known_at`, and `matching_versions`. The final order is `probe.valid_on`.
- **Independent verification:** For sql-temporal-01 Exercise 2, independently aggregate `pro_temporal_lab.facts` by `valid_on`, and `known_at`; require one output row for every distinct `valid_on`, and `known_at` tuple and compare `matching_versions` tuple by tuple. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-temporal-01 Exercise 2, start with the first relation in `pro_temporal_lab.facts`; after each join, record total rows and distinct `valid_on`, and `known_at` so the exact fanout or loss is visible.
- **Clause check:** For sql-temporal-01 Exercise 2, the solution actually uses `FROM`, `JOIN ... ON`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_temporal_lab.facts`, preserve one row per `valid_on`, and `known_at`, and finish with `valid_on`, `known_at`, and `matching_versions` ordered by `probe.valid_on`.
- **Alternative/trade-off:** For sql-temporal-01 Exercise 2, the chosen form is justified by this lesson-specific rationale: Test `lower`, just before upper, and exactly upper for both date and timestamp ranges. Evaluate another form against the concrete expected result (one row per `valid_on`, and `known_at`) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.

## Exercise 3 — Exclusion versus fallback

With approved `btree_gist`, a partial GiST exclusion combines
`customer_key WITH =` and `valid_period WITH &&` for current system rows.
PostgreSQL enforces conflicts under concurrency. The fallback advisory-lock
trigger qualifies the query and serializes one hashed key before checking;
hash collisions reduce concurrency, and every write path/trigger enablement must
remain controlled.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 3, complete the overlap enforcement written analysis and support its claims with read-only evidence from `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-temporal-01 Exercise 3, expected output: a completed the overlap enforcement written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `btree_gist`, `customer_key`, and `valid_period`.
- **Independent verification:** For sql-temporal-01 Exercise 3, check the overlap enforcement written analysis against `btree_gist`, `customer_key`, and `valid_period`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-temporal-01 Exercise 3, check the overlap enforcement written analysis against `btree_gist`, `customer_key`, and `valid_period`.
- **Clause check:** For sql-temporal-01 Exercise 3, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows` or label it as proposed policy.
- **Alternative/trade-off:** For sql-temporal-01 Exercise 3, the chosen form is justified by this lesson-specific rationale: With approved `btree_gist`, a partial GiST exclusion combines `customer_key WITH =` and `valid_period WITH &&` for current system rows. Evaluate another form against the concrete expected result (a completed the overlap enforcement written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 4 — Reversal chain

Entries L-1 (+5), L-2 (-5 reversing L-1), and L-3 (+5 correcting/reversing L-2)
sum to +5 without UPDATE. Unique idempotency keys prevent duplicate append and
foreign keys preserve reversal references. Domain policy should prevent
multiple unauthorized reversals of one entry if that is invalid.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 4, read the target keys from `pro_temporal_lab.ledger` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-temporal-01 Exercise 4, expected output: the command tag and an independently counted set of affected `entry_id` values. The final columns are `entry_id`. The final order is `l.entry_id`.
- **Independent verification:** For sql-temporal-01 Exercise 4, materialize the intended `entry_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_temporal_lab.ledger` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `entry_id` values in both cases.
- **Intermediate relation check:** For sql-temporal-01 Exercise 4, materialize the intended `entry_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_temporal_lab.ledger` again and prove rollback or idempotent retry.
- **Clause check:** For sql-temporal-01 Exercise 4, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_temporal_lab.ledger`, preserve one row per `entry_id`, and finish with `entry_id` ordered by `l.entry_id`.
- **Alternative/trade-off:** For sql-temporal-01 Exercise 4, the chosen form is justified by this lesson-specific rationale: Entries L-1 (+5), L-2 (-5 reversing L-1), and L-3 (+5 correcting/reversing L-2) sum to +5 without UPDATE. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `entry_id` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `entry_id` values in both cases.

## Exercise 5 — Hold decisions

The decision log appends who, reason, action, and time. Current hold state is
derived from the latest authorized decision. Deletion still requires retention
age, no current hold, approval, dependency/backup review, and an immutable
execution audit. The course solution records decisions but deletes nothing.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 5, read the target keys from `pro_temporal_lab.retention_decisions`, `pro_temporal_lab.facts`, and `pro_temporal_lab.ledger` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-temporal-01 Exercise 5, expected output: the command tag and an independently counted set of affected `affected_row_count` values. The final columns are `affected_row_count`, and `command_tag`.
- **Independent verification:** For sql-temporal-01 Exercise 5, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `pro_temporal_lab.retention_decisions`, `pro_temporal_lab.facts`, and `pro_temporal_lab.ledger` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.
- **Intermediate relation check:** For sql-temporal-01 Exercise 5, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `pro_temporal_lab.retention_decisions`, `pro_temporal_lab.facts`, and `pro_temporal_lab.ledger` again and prove rollback or idempotent retry.
- **Clause check:** For sql-temporal-01 Exercise 5, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `pro_temporal_lab.retention_decisions`, `pro_temporal_lab.facts`, and `pro_temporal_lab.ledger`, preserve one row per `affected_row_count`, and finish with `affected_row_count`, and `command_tag`.
- **Alternative/trade-off:** For sql-temporal-01 Exercise 5, the chosen form is justified by this lesson-specific rationale: The decision log appends who, reason, action, and time. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `affected_row_count` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.

## Exercise 6 — Domain assumptions

Record business time zone and clock authority; valid/system boundary convention;
late-arrival/correction authority; allowed gaps/overlaps; customer identity;
money/unit semantics; ledger reconciliation and reversal policy; retention/legal
basis; hold ownership; deletion versus anonymization; and how replicas/backups
honor erasure and audit duties.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 6, complete the assumption register written analysis and support its claims with read-only evidence from `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-temporal-01 Exercise 6, expected output: a completed the assumption register written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Independent verification:** For sql-temporal-01 Exercise 6, check the assumption register written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-temporal-01 Exercise 6, check the assumption register written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Clause check:** For sql-temporal-01 Exercise 6, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows` or label it as proposed policy.
- **Alternative/trade-off:** For sql-temporal-01 Exercise 6, the chosen form is justified by this lesson-specific rationale: Record business time zone and clock authority; valid/system boundary convention; late-arrival/correction authority; allowed gaps/overlaps; customer identity; money/unit semantics; ledger reconciliation and reve. Evaluate another form against the concrete expected result (a completed the assumption register written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 7 — Civil time and daylight saving

Store the authoritative instant as `timestamptz` and retain the IANA zone name
used to interpret/display civil time. A fixed offset has no DST rules; a bare
timestamp cannot identify which occurrence an ambiguous fall-back time means.

Detect/reject nonexistent spring-forward times and require an explicit
earlier/later-offset policy for ambiguous input. Test both transitions for the
supported zone database/version.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 7, read from the inline `VALUES` fixture. Build the answer toward `local_time`, `zone_name`, and `interpreted_instant`; keep `zone_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-temporal-01 Exercise 7, expected output: one row per `zone_name`. The final columns are `local_time`, `zone_name`, and `interpreted_instant`. The final order is `local_time`.
- **Independent verification:** For sql-temporal-01 Exercise 7, reselect the returned keys directly from the source; require unique `zone_name` where the expected grain is one row per key and confirm the projected `local_time`, `zone_name`, and `interpreted_instant` against the inline `VALUES` fixture. Add one source row with a new `zone_name`; verify the result gains exactly one row carrying that `zone_name` value.
- **Intermediate relation check:** For sql-temporal-01 Exercise 7, check `local_time` before applying the row cap.
- **Clause check:** For sql-temporal-01 Exercise 7, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `zone_name`, and finish with `local_time`, `zone_name`, and `interpreted_instant` ordered by `local_time`.
- **Alternative/trade-off:** For sql-temporal-01 Exercise 7, the chosen form is justified by this lesson-specific rationale: Store the authoritative instant as `timestamptz` and retain the IANA zone name used to interpret/display civil time. Evaluate another form against the concrete expected result (one row per `zone_name`) and the verification above.
- **Edge case:** Add one source row with a new `zone_name`; verify the result gains exactly one row carrying that `zone_name` value.

## Exercise 8 — Event, ingestion, and processing clocks

Event time is source occurrence, ingestion time is arrival, and processing time
is computation. A watermark such as maximum observed event time minus allowed
lateness closes windows only under a documented source/partition policy.

Beyond-window data should be quarantined or applied as a versioned
correction/retraction. Publish metric version, as-of/watermark, changed keys, and
downstream recomputation/notification evidence.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 8, read from `pro_temporal_lab.timed_events`. Build the answer toward `maximum_event_time`, `example_watermark`, and `maximum_arrival_delay`; keep `example_watermark` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-temporal-01 Exercise 8, expected output: one row per `example_watermark`. The final columns are `maximum_event_time`, `example_watermark`, and `maximum_arrival_delay`.
- **Independent verification:** For sql-temporal-01 Exercise 8, reselect the returned keys directly from the source; require unique `example_watermark` where the expected grain is one row per key and confirm the projected `maximum_event_time`, `example_watermark`, and `maximum_arrival_delay` against `pro_temporal_lab.timed_events`. Add one source row with a new `example_watermark`; verify the result gains exactly one row carrying that `example_watermark` value.
- **Intermediate relation check:** For sql-temporal-01 Exercise 8, select `example_watermark` from `pro_temporal_lab.timed_events` before adding derived columns.
- **Clause check:** For sql-temporal-01 Exercise 8, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at `pro_temporal_lab.timed_events`, preserve one row per `example_watermark`, and finish with `maximum_event_time`, `example_watermark`, and `maximum_arrival_delay`.
- **Alternative/trade-off:** For sql-temporal-01 Exercise 8, the chosen form is justified by this lesson-specific rationale: Event time is source occurrence, ingestion time is arrival, and processing time is computation. Evaluate another form against the concrete expected result (one row per `example_watermark`) and the verification above.
- **Edge case:** Add one source row with a new `example_watermark`; verify the result gains exactly one row carrying that `example_watermark` value.

## Exercise 9 — Type-2 as-of dimension join

Give each version a surrogate key, stable business key, half-open effective
range, and correction metadata. Join a fact where business keys match and the
range contains fact time; persist the resolved surrogate when interpretation
must never drift.

Enforce/report no overlap and assert each fact has at most or exactly one match
according to missing-dimension policy. A current flag must agree with range
state.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 9, read from `pro_temporal_lab.customer_dimension`. Build the answer toward `order_key`, `ordered_on`, `customer_version_id`, and `segment`; keep `customer_version_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-temporal-01 Exercise 9, expected output: one row per `customer_version_id`. The final columns are `order_key`, `ordered_on`, `customer_version_id`, and `segment`. The final order is `order_fact.order_key`.
- **Independent verification:** For sql-temporal-01 Exercise 9, project `customer_version_id` plus the raw source columns from `pro_temporal_lab.customer_dimension` at each join stage; record row count and distinct `customer_version_id`, then assert the final `order_key`, `ordered_on`, `customer_version_id`, and `segment` values match those staged rows without unintended fanout or loss. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-temporal-01 Exercise 9, start with the first relation in `pro_temporal_lab.customer_dimension`; after each join, record total rows and distinct `customer_version_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-temporal-01 Exercise 9, the solution actually uses `FROM`, `JOIN ... ON`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_temporal_lab.customer_dimension`, preserve one row per `customer_version_id`, and finish with `order_key`, `ordered_on`, `customer_version_id`, and `segment` ordered by `order_fact.order_key`.
- **Alternative/trade-off:** For sql-temporal-01 Exercise 9, the chosen form is justified by this lesson-specific rationale: Give each version a surrogate key, stable business key, half-open effective range, and correction metadata. Evaluate another form against the concrete expected result (one row per `customer_version_id`) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.

## Exercise 10 — Temporal referential integrity

The child period must be contained by an allowed parent period, not merely share
a key. A trigger can lock a stable business-key namespace, query containment,
and reject gaps under concurrency.

Exclusion constraints prevent overlap but do not alone prove containment.
Deferred/bulk loading needs an explicit validation and quarantine/repair gate;
test parent shrink/delete and concurrent changes.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 10, complete the temporal parent written analysis and support its claims with read-only evidence from `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-temporal-01 Exercise 10, expected output: a completed the temporal parent written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Independent verification:** For sql-temporal-01 Exercise 10, check the temporal parent written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-temporal-01 Exercise 10, check the temporal parent written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Clause check:** For sql-temporal-01 Exercise 10, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows` or label it as proposed policy.
- **Alternative/trade-off:** For sql-temporal-01 Exercise 10, the chosen form is justified by this lesson-specific rationale: The child period must be contained by an allowed parent period, not merely share a key. Evaluate another form against the concrete expected result (a completed the temporal parent written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 11 — Gap and overlap report

Order nonempty periods by lower bound, upper bound, stable ID and compare each
lower bound with the running maximum prior upper. Lower means overlap, greater
means gap, equal means adjacency. Plain `lag(upper)` can miss overlap hidden by
an earlier long interval.

Multirange aggregation/subtraction can expose coverage compactly. Report
duplicates/empty/inverted periods separately and define adjacency policy.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 11, read from `periods`. Build the answer toward `period_id`, `valid_period`, and `relationship_to_prior_coverage`; keep `period_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-temporal-01 Exercise 11, expected output: one row per `period_id`. The final columns are `period_id`, `valid_period`, and `relationship_to_prior_coverage`. The final order is `lower(w.valid_period), upper(w.valid_period), w.period_id`.
- **Independent verification:** For sql-temporal-01 Exercise 11, reselect the returned keys directly from the source; require unique `period_id` where the expected grain is one row per key and confirm the projected `period_id`, `valid_period`, and `relationship_to_prior_coverage` against `periods`. Add duplicate source candidates for `period_id`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
- **Intermediate relation check:** For sql-temporal-01 Exercise 11, run `with_prior` one at a time. Record each CTE's row count and `period_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-temporal-01 Exercise 11, the solution actually uses `WITH`, `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `periods`, preserve one row per `period_id`, and finish with `period_id`, `valid_period`, and `relationship_to_prior_coverage` ordered by `lower(w.valid_period), upper(w.valid_period), w.period_id`.
- **Alternative/trade-off:** For sql-temporal-01 Exercise 11, the chosen form is justified by this lesson-specific rationale: Order nonempty periods by lower bound, upper bound, stable ID and compare each lower bound with the running maximum prior upper. Evaluate another form against the concrete expected result (one row per `period_id`) and the verification above.
- **Edge case:** Add duplicate source candidates for `period_id`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

## Exercise 12 — Partition archive under hold

Inventory retention and holds before detach. If one held row blocks an expirable
partition, move/repartition only through audited review. Verify counts/checksums,
dependencies, indexes, encryption/access, manifest, and test restore.

Keep archive discoverable to authorized recovery/legal processes, propagate hold
decisions to replicas/backups, and record deletion evidence. Partition age alone
is not authorization to erase.

### Reasoning and verification

- **Inputs/evidence:** For sql-temporal-01 Exercise 12, use `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-temporal-01 Exercise 12, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
- **Independent verification:** For sql-temporal-01 Exercise 12, restore into an isolated target and reconcile `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-temporal-01 Exercise 12, restore into an isolated target and reconcile `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-temporal-01 Exercise 12, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_temporal_lab.customer_terms`, `ON`, and `pro_temporal_lab.global_maintenance_windows` or label it as proposed policy.
- **Alternative/trade-off:** For sql-temporal-01 Exercise 12, the chosen form is justified by this lesson-specific rationale: Inventory retention and holds before detach. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Edge cases

- Infinity/open bounds need explicit API serialization.
- Clock corrections and transaction timestamp versus wall clock differ.
- Backdated facts can change previously published metrics.
- Temporal indexes and history retention grow write/storage cost.
