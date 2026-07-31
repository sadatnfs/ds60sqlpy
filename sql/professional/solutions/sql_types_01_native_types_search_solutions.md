# SQL-TYPES-01 Solutions — Native Types and Search


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_types_01_native_types_search_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_types_01_native_types_search_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Domain, Enum, UUID, Array, Range/multirange, JSONB. Its worked-model focus is:
The model uses a domain for a reusable email-shape rule and an enum for a small database-owned lifecycle. Enums are compact and clear, but adding/removing labels is migration work; a reference table is more flexible when labels carry metadata or change frequently.

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
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_types_01_native_types_search_solutions.sql
```

The solution creates and rolls back only `pro_types_lab`.

## Exercise 1 — Multi-tag containment

`tags @> ARRAY['postgresql','operations']` asks whether the stored array
contains both required values. Two scalar `ANY` predicates can express the same
fixture result, but containment maps directly to the set-like question and a
GIN array operator class.

Arrays preserve order and duplicates, so they are not literally mathematical
sets. If duplicate/order semantics matter, test them explicitly.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 1, complete the tag containment written analysis and support its claims with read-only evidence from `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-types-01 Exercise 1, expected output: a completed the tag containment written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `any`.
- **Independent verification:** For sql-types-01 Exercise 1, check the tag containment written analysis against `any`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-types-01 Exercise 1, check the tag containment written analysis against `any`.
- **Clause check:** For sql-types-01 Exercise 1, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions` or label it as proposed policy.
- **Alternative/trade-off:** For sql-types-01 Exercise 1, the chosen form is justified by this lesson-specific rationale: `tags @> ARRAY['postgresql','operations']` asks whether the stored array contains both required values. Evaluate another form against the concrete expected result (a completed the tag containment written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 2 — Availability minus blackout

The predicate combines:

```sql
availability @> DATE '2026-08-11'
AND NOT (blackout_windows @> DATE '2026-08-11')
```

The fixture uses `[start,end)`, including start and excluding end. The migration
document is generally available that day but specifically blacked out, so it is
excluded.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 2, complete the range subtraction written analysis and support its claims with read-only evidence from `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-types-01 Exercise 2, expected output: a completed the range subtraction written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Independent verification:** For sql-types-01 Exercise 2, check the range subtraction written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-types-01 Exercise 2, check the range subtraction written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Clause check:** For sql-types-01 Exercise 2, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions` or label it as proposed policy.
- **Alternative/trade-off:** For sql-types-01 Exercise 2, the chosen form is justified by this lesson-specific rationale: The predicate combines: The fixture uses `[start,end)`, including start and excluding end. Evaluate another form against the concrete expected result (a completed the range subtraction written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 3 — Numeric JSONPath

The JSONPath predicate checks both JSON number type and value above 30. The
selected cast is safe because this controlled fixture owns the metadata shape.
With untrusted JSON, use shape validation or a normalized typed column before
casting; SQL predicate evaluation order is not a universal error guard.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 3, complete the typed jsonpath written analysis and support its claims with read-only evidence from `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-types-01 Exercise 3, expected output: a completed the typed jsonpath written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Independent verification:** For sql-types-01 Exercise 3, check the typed jsonpath written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-types-01 Exercise 3, check the typed jsonpath written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Clause check:** For sql-types-01 Exercise 3, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions` or label it as proposed policy.
- **Alternative/trade-off:** For sql-types-01 Exercise 3, the chosen form is justified by this lesson-specific rationale: The JSONPath predicate checks both JSON number type and value above 30. Evaluate another form against the concrete expected result (a completed the typed jsonpath written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 4 — Phrase-aware full text

`websearch_to_tsquery('english', '"schema migration" verify')` builds a query
requiring the phrase plus `verify`. The generated vector weights titles above
bodies, and ordering uses rank then UUID to break ties deterministically.

Different configurations stem words differently. Always use the same explicit
configuration when generating vectors and queries.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 4, complete the full-text query written analysis and support its claims with read-only evidence from `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-types-01 Exercise 4, expected output: a completed the full-text query written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `websearch_to_tsquery`.
- **Independent verification:** For sql-types-01 Exercise 4, check the full-text query written analysis against `websearch_to_tsquery`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-types-01 Exercise 4, check the full-text query written analysis against `websearch_to_tsquery`.
- **Clause check:** For sql-types-01 Exercise 4, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions` or label it as proposed policy.
- **Alternative/trade-off:** For sql-types-01 Exercise 4, the chosen form is justified by this lesson-specific rationale: `websearch_to_tsquery('english', '"schema migration" verify')` builds a query requiring the phrase plus `verify`. Evaluate another form against the concrete expected result (a completed the full-text query written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 5 — Index choices

- Default `jsonb_ops` supports a wider operator family and indexes keys and
  values.
- `jsonb_path_ops` is typically smaller and focused on containment/jsonpath
  value paths.
- GIN over `tsvector` supports lexeme matching.
- `pg_trgm` supports similarity and many substring patterns, but requires an
  approved extension and adds index/write cost.

Choose from observed operators and workload, then measure plans and maintenance;
do not stack every candidate index.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 5, read from `pg_trgm`. Build the answer toward `jsonb_ops`, `jsonb_path_ops`, and `tsvector`; keep `jsonb_ops` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-types-01 Exercise 5, expected output: one row per `jsonb_ops`. The final columns are `jsonb_ops`, `jsonb_path_ops`, and `tsvector`.
- **Independent verification:** For sql-types-01 Exercise 5, reselect the returned keys directly from the source; require unique `jsonb_ops` where the expected grain is one row per key and confirm the projected `jsonb_ops`, `jsonb_path_ops`, and `tsvector` against `pg_trgm`. Add one source row with a new `jsonb_ops`; verify the result gains exactly one row carrying that `jsonb_ops` value.
- **Intermediate relation check:** For sql-types-01 Exercise 5, select `jsonb_ops` from `pg_trgm` before adding derived columns.
- **Clause check:** For sql-types-01 Exercise 5, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_trgm` or label it as proposed policy.
- **Alternative/trade-off:** For sql-types-01 Exercise 5, the chosen form is justified by this lesson-specific rationale: - Default `jsonb_ops` supports a wider operator family and indexes keys and values. Evaluate another form against the concrete expected result (one row per `jsonb_ops`) and the verification above.
- **Edge case:** Add one source row with a new `jsonb_ops`; verify the result gains exactly one row carrying that `jsonb_ops` value.

## Exercise 6 — Modelling choices

Use a domain for a stable reusable scalar rule, an enum for a small
database-owned closed lifecycle, a reference table when labels need metadata or
frequent change, an array for a small row-owned homogeneous collection, a range
for interval algebra, JSONB for genuinely variable document-shaped attributes,
and normalized relations for independently identified facts and cross-row
constraints.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 6, complete the type decision written analysis and support its claims with read-only evidence from `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-types-01 Exercise 6, expected output: a completed the type decision written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Independent verification:** For sql-types-01 Exercise 6, check the type decision written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-types-01 Exercise 6, check the type decision written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Clause check:** For sql-types-01 Exercise 6, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions` or label it as proposed policy.
- **Alternative/trade-off:** For sql-types-01 Exercise 6, the chosen form is justified by this lesson-specific rationale: Use a domain for a stable reusable scalar rule, an enum for a small database-owned closed lifecycle, a reference table when labels need metadata or frequent change, an array for a small row-owned homogeneous co. Evaluate another form against the concrete expected result (a completed the type decision written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 7 — Multirange normalization and gaps

Construct a `datemultirange` from input ranges; PostgreSQL canonicalizes and
merges overlapping or adjacent discrete date ranges. The August gap is the
bounded month range minus the normalized availability multirange. Expand only
for display/testing when the domain is small—range algebra avoids one row per
day.

Adjacency merging is correct when uninterrupted consecutive dates are one
availability period. If a handoff at the boundary has business meaning, store
separate identified periods rather than relying on a multirange that
canonicalizes them together.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 7, read from `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`. Compute `normalized_availability`, and `august_gaps` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-types-01 Exercise 7, expected output: one row per day. The final columns are `normalized_availability`, and `august_gaps`.
- **Independent verification:** For sql-types-01 Exercise 7, evaluate each of `normalized_availability`, and `august_gaps` in a separate control `SELECT` over `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`; require one final row and compare every value. Add one source row with a new `day`; verify the result gains exactly one row carrying that `day` value.
- **Intermediate relation check:** For sql-types-01 Exercise 7, run `schedule` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
- **Clause check:** For sql-types-01 Exercise 7, the solution actually uses `WITH`, `FROM`, and `SELECT`. Read only those operations: begin at `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`, preserve exactly one summary row, and finish with `normalized_availability`, and `august_gaps`.
- **Alternative/trade-off:** For sql-types-01 Exercise 7, the chosen form is justified by this lesson-specific rationale: Construct a `datemultirange` from input ranges; PostgreSQL canonicalizes and merges overlapping or adjacent discrete date ranges. Evaluate another form against the concrete expected result (one row per day) and the verification above.
- **Edge case:** Add one source row with a new `day`; verify the result gains exactly one row carrying that `day` value.

## Exercise 8 — Network containment

Store client endpoints as `inet` and rules as `cidr`. Join where the network
contains the address (`network >>= address`), then rank by
`masklen(network) DESC, rule_id` so the longest prefix wins deterministically.
GiST or SP-GiST network operator classes can support containment; confirm the
exact operator and plan.

Do not compare addresses as text: lexical order and spelling variants do not
express network containment. Explicitly define IPv4/IPv6 coexistence and the
default rule when no network matches.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 8, read from `clients`, and `rules`. Build the answer toward `client_id`, `address`, `rule_id`, and `network`; keep `client_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-types-01 Exercise 8, expected output: one row per `client_id`. The final columns are `client_id`, `address`, `rule_id`, and `network`. The final order is `client_id`.
- **Independent verification:** For sql-types-01 Exercise 8, project `client_id` plus the raw source columns from `clients`, and `rules` at each join stage; record row count and distinct `client_id`, then assert the final `client_id`, `address`, `rule_id`, and `network` values match those staged rows without unintended fanout or loss. Add one row for which `(match_rank = 1)` is true and one for which it is false; verify only the matching `client_id` value is returned.
- **Intermediate relation check:** For sql-types-01 Exercise 8, run `ranked` one at a time. Record each CTE's row count and `client_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-types-01 Exercise 8, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `clients`, and `rules`, preserve one row per `client_id`, and finish with `client_id`, `address`, `rule_id`, and `network` ordered by `client_id`.
- **Alternative/trade-off:** For sql-types-01 Exercise 8, the chosen form is justified by this lesson-specific rationale: Store client endpoints as `inet` and rules as `cidr`. Evaluate another form against the concrete expected result (one row per `client_id`) and the verification above.
- **Edge case:** Add one row for which `(match_rank = 1)` is true and one for which it is false; verify only the matching `client_id` value is returned.

## Exercise 9 — Monetary representation

`numeric(p,s)` gives exact decimal arithmetic and a declared scale; validate
rounding at ingestion and choose capacity from maximum business value. Bigint
minor units are exact and interoperable but require an explicit currency scale
that may differ by currency. Double precision is approximate and is unsuitable
for exact equality/accounting totals.

A domain can centralize nonnegative/range rules, but currency compatibility is
cross-column and usually needs a composite model or reference table. Test sum,
rounding, multiplication, overflow, serialization, and mixed-currency rejection.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 9, read from `pro_types_lab.nonnegative_money`. Compute `exact_decimal_sum`, and `declared_rounding_example` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-types-01 Exercise 9, expected output: exactly one aggregate summary row. The final columns are `exact_decimal_sum`, and `declared_rounding_example`.
- **Independent verification:** For sql-types-01 Exercise 9, evaluate each of `exact_decimal_sum` in a separate control `SELECT` over `pro_types_lab.nonnegative_money`; require one final row and compare every value. Add one source row with a new `declared_rounding_example`; verify the result gains exactly one row carrying that `declared_rounding_example` value.
- **Intermediate relation check:** For sql-types-01 Exercise 9, select `declared_rounding_example` from `pro_types_lab.nonnegative_money` before adding derived columns.
- **Clause check:** For sql-types-01 Exercise 9, the solution actually uses `WITH`, and `SELECT`. Read only those operations: begin at `pro_types_lab.nonnegative_money`, preserve exactly one summary row, and finish with `exact_decimal_sum`, and `declared_rounding_example`.
- **Alternative/trade-off:** For sql-types-01 Exercise 9, the chosen form is justified by this lesson-specific rationale: `numeric(p,s)` gives exact decimal arithmetic and a declared scale; validate rounding at ingestion and choose capacity from maximum business value. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Add one source row with a new `declared_rounding_example`; verify the result gains exactly one row carrying that `declared_rounding_example` value.

## Exercise 10 — Promote a JSON property

Validate that the payload property is a JSON number before casting it in a
generated expression, or constrain accepted payload shape first. Index the
stored typed column and query that column directly; this makes the frequently
used contract visible to statistics and tools.

The trade-off is stricter writes: a legacy string such as `"30"` may have been
accepted JSON but now fails the promoted contract. Inventory/backfill bad rows,
deploy compatible writers, validate, and only then enforce the generated value.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 10, read from `pro_types_lab.documents`, and `documents_estimated_minutes_idx`. Build the answer toward `document_id`, and `estimated_minutes`; keep `document_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-types-01 Exercise 10, expected output: one row per `document_id`. The final columns are `document_id`, and `estimated_minutes`. The final order is `d.document_id`.
- **Independent verification:** For sql-types-01 Exercise 10, run an anti-check that counts rows where NOT ((d.estimated_minutes > 30)); require unique `document_id` where the expected grain is one row per key and confirm the projected `document_id`, and `estimated_minutes` against `pro_types_lab.documents`, and `documents_estimated_minutes_idx`. Insert rows immediately before, exactly at, and immediately after `d.estimated_minutes > 30`; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-types-01 Exercise 10, inspect the source keys that survive `WHERE`; then check `d.document_id` before applying the row cap.
- **Clause check:** For sql-types-01 Exercise 10, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_types_lab.documents`, and `documents_estimated_minutes_idx`, preserve one row per `document_id`, and finish with `document_id`, and `estimated_minutes` ordered by `d.document_id`.
- **Alternative/trade-off:** For sql-types-01 Exercise 10, the chosen form is justified by this lesson-specific rationale: Validate that the payload property is a JSON number before casting it in a generated expression, or constrain accepted payload shape first. Evaluate another form against the concrete expected result (one row per `document_id`) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after `d.estimated_minutes > 30`; identify which rows pass each inclusive or exclusive comparison.

## Exercise 11 — Language-aware full text

`to_tsvector` reveals normalized lexemes and positions after parsing,
dictionary stop-word removal, and stemming. Weight title/body lexemes before
ranking. Generate and query with the same explicit configuration.

For multilingual data, store/validate a language configuration per row or route
rows into language-specific vectors/indexes. A generic `simple` configuration
avoids stemming but is not automatically better. Evaluate relevance against a
labeled corpus, including unsupported/mixed-language fallback.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 11, read from `pro_types_lab.documents`. Build the answer toward `document_id`, and `lexemes`; keep `document_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-types-01 Exercise 11, expected output: one row per `document_id`. The final columns are `document_id`, and `lexemes`. The final order is `d.document_id`.
- **Independent verification:** For sql-types-01 Exercise 11, reselect the returned keys directly from the source; require unique `document_id` where the expected grain is one row per key and confirm the projected `document_id`, and `lexemes` against `pro_types_lab.documents`. Add one source row with a new `document_id`; verify the result gains exactly one row carrying that `document_id` value.
- **Intermediate relation check:** For sql-types-01 Exercise 11, check `d.document_id` before applying the row cap.
- **Clause check:** For sql-types-01 Exercise 11, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_types_lab.documents`, preserve one row per `document_id`, and finish with `document_id`, and `lexemes` ordered by `d.document_id`.
- **Alternative/trade-off:** For sql-types-01 Exercise 11, the chosen form is justified by this lesson-specific rationale: `to_tsvector` reveals normalized lexemes and positions after parsing, dictionary stop-word removal, and stemming. Evaluate another form against the concrete expected result (one row per `document_id`) and the verification above.
- **Edge case:** Add one source row with a new `document_id`; verify the result gains exactly one row carrying that `document_id` value.

## Exercise 12 — Normalize tags

Create a `tags` vocabulary and a `document_tags(document_id, tag_id)` relation
with a composite primary key. Containment becomes grouping/HAVING or joins, and
foreign keys enforce vocabulary and prevent duplicates.

Arrays are simpler for a small row-owned list queried by containment, but cannot
foreign-key individual elements and preserve duplicates/order. Normalization
adds join/write cost while supporting tag metadata, independent identity,
cross-row constraints, and referential updates.

### Reasoning and verification

- **Inputs/evidence:** For sql-types-01 Exercise 12, read from `pro_types_lab.documents`, `pro_types_lab.tags`, and `pro_types_lab.document_tags`. Build the answer toward `tag_name`; keep `document_id`, and `title` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-types-01 Exercise 12, expected output: one row per `document_id`, and `title`. The final columns are `tag_name`. The final order is `d.document_id`.
- **Independent verification:** For sql-types-01 Exercise 12, independently aggregate `pro_types_lab.documents`, `pro_types_lab.tags`, and `pro_types_lab.document_tags` by `document_id`, and `title`; require one output row for every distinct `document_id`, and `title` tuple satisfying `(t.tag_name IN ('postgresql', 'operations'))` and compare `tag_name` tuple by tuple. Add duplicate source candidates for `document_id`, and `title`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
- **Intermediate relation check:** For sql-types-01 Exercise 12, start with the first relation in `pro_types_lab.documents`, `pro_types_lab.tags`, and `pro_types_lab.document_tags`; after each join, record total rows and distinct `document_id`, and `title` so the exact fanout or loss is visible.
- **Clause check:** For sql-types-01 Exercise 12, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_types_lab.documents`, `pro_types_lab.tags`, and `pro_types_lab.document_tags`, preserve one row per `document_id`, and `title`, and finish with `tag_name` ordered by `d.document_id`.
- **Alternative/trade-off:** For sql-types-01 Exercise 12, the chosen form is justified by this lesson-specific rationale: Create a `tags` vocabulary and a `document_tags(document_id, tag_id)` relation with a composite primary key. Evaluate another form against the concrete expected result (one row per `document_id`, and `title`) and the verification above.
- **Edge case:** Add duplicate source candidates for `document_id`, and `title`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

## Edge cases

- Empty arrays and empty ranges have distinct semantics.
- Multiranges normalize overlapping/adjacent members.
- Missing JSON, JSON null, and SQL NULL differ.
- Search ranking and phrase behavior require corpus-level relevance tests.
