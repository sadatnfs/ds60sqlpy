# Day 28 solutions — JSON/JSONB and XML in PostgreSQL


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day28_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day28_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are JSONB, Containment, Path extraction. Its worked-model focus is:
Extract metadata->>'campaign' as text, keep the raw JSONB beside it, and group missing values separately. For XML, extract the first XPath result, validate its text form, cast to integer, and left-join orders so malformed or unmatched documents remain visible.

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

These answers align one-for-one with [day28_json_xml.sql](../day28_json_xml.sql).
Run only against the disposable `advanced_sql_training` database.
The executable companion wraps every answer in `BEGIN`/`ROLLBACK`.
The snippets below assume the lesson's
`SET search_path TO training, public;` statement. Run the complete
executable companion when you want a self-contained check.

## Reading contract

- **Focus:** Query JSONB and XML with explicit path, type, missing-key, and safe-cast behavior instead of assuming semi-structured data is schema-free.
- **Assumptions:** JSON text extraction with `->>` returns text or NULL. XML XPath results are arrays. Course metadata keys are small and deterministic.
- **Primary pitfall:** Casting missing or malformed JSON text directly raises; broad JSON containment or regex extraction needs validation and appropriate indexing evidence.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1 — Query writing

**Prompt:** Extract customer acquisition channel and referrer from JSONB attributes.

**Reasoning:** `->>` returns text and naturally yields NULL for a missing key.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.attributes ->> 'channel' AS channel,
       c.attributes ->> 'referrer' AS referrer
FROM customers AS c
ORDER BY c.customer_id;
```

**Expected shape:** One row per customer.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-28 Exercise 1, read from `customers`. Build the answer toward `customer_id`, `channel`, and `referrer`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-28 Exercise 1, expected output: One row per customer. The final columns are `customer_id`, `channel`, and `referrer`. The final order is `c.customer_id`.
- **Independent verification:** For sql-28 Exercise 1, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `channel`, and `referrer` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-28 Exercise 1, check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-28 Exercise 1, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_id`, `channel`, and `referrer` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-28 Exercise 1, the chosen form is justified by this lesson-specific rationale: `->>` returns text and naturally yields NULL for a missing key. Evaluate another form against the concrete expected result (One row per customer) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Exercise 2 — Query writing

**Prompt:** Find mobile-channel customers using JSONB containment.

**Reasoning:** `@>` tests whether the left JSONB contains the declared object.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT c.customer_id,
       c.full_name,
       c.attributes
FROM customers AS c
WHERE c.attributes @> '{"channel": "mobile"}'::jsonb
ORDER BY c.customer_id;
```

**Expected shape:** Customer rows whose channel is mobile.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-28 Exercise 2, read from `customers`. Build the answer toward `customer_id`, `full_name`, and `attributes`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-28 Exercise 2, expected output: Customer rows whose channel is mobile. The final columns are `customer_id`, `full_name`, and `attributes`. The final order is `c.customer_id`.
- **Independent verification:** For sql-28 Exercise 2, run an anti-check that counts rows where NOT ((c.attributes @> '{"channel": "mobile"}'::jsonb)); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `full_name`, and `attributes` against `customers`. Add one row for which `(c.attributes @> '{"channel": "mobile"}'::jsonb)` is true and one for which it is false; verify only the matching `customer_id` value is returned.
- **Intermediate relation check:** For sql-28 Exercise 2, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
- **Clause check:** For sql-28 Exercise 2, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `customers`, preserve one row per `customer_id`, and finish with `customer_id`, `full_name`, and `attributes` ordered by `c.customer_id`.
- **Alternative/trade-off:** For sql-28 Exercise 2, the chosen form is justified by this lesson-specific rationale: `@>` tests whether the left JSONB contains the declared object. Evaluate another form against the concrete expected result (Customer rows whose channel is mobile) and the verification above.
- **Edge case:** Add one row for which `(c.attributes @> '{"channel": "mobile"}'::jsonb)` is true and one for which it is false; verify only the matching `customer_id` value is returned.

## Exercise 3 — Query writing

**Prompt:** Count event rows with missing device metadata separately from present values.

**Reasoning:** Use `?` to test key existence rather than comparing extracted text to NULL.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.

```sql
SELECT COUNT(*) FILTER (WHERE e.metadata ? 'device') AS has_device_key,
       COUNT(*) FILTER (WHERE NOT e.metadata ? 'device') AS missing_device_key,
       COUNT(*) AS all_events
FROM events AS e;
```

**Expected shape:** One summary row.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-28 Exercise 3, read from `events`. Build the answer toward `has_device_key`, `missing_device_key`, and `all_events`; keep `has_device_key` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-28 Exercise 3, expected output: One summary row. The final columns are `has_device_key`, `missing_device_key`, and `all_events`.
- **Independent verification:** For sql-28 Exercise 3, reselect the returned keys directly from the source; require unique `has_device_key` where the expected grain is one row per key and confirm the projected `has_device_key`, `missing_device_key`, and `all_events` against `events`. Add one source row with a new `has_device_key`; verify the result gains exactly one row carrying that `has_device_key` value.
- **Intermediate relation check:** For sql-28 Exercise 3, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-28 Exercise 3, the solution actually uses `FROM`, `WHERE`, aggregate `FILTER`, and `SELECT`. Read only those operations: begin at `events`, preserve one row per `has_device_key`, and finish with `has_device_key`, `missing_device_key`, and `all_events`.
- **Alternative/trade-off:** For sql-28 Exercise 3, the chosen form is justified by this lesson-specific rationale: Use `?` to test key existence rather than comparing extracted text to NULL. Evaluate another form against the concrete expected result (One summary row) and the verification above.
- **Edge case:** Add one source row with a new `has_device_key`; verify the result gains exactly one row carrying that `has_device_key` value.

## Exercise 4 — Prediction

**Prompt:** Aggregate event-type counts into a JSONB object per customer and predict key ordering expectations.

**Reasoning:** JSON objects are mappings; do not treat key order as a semantic contract.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
WITH event_counts AS (
  SELECT e.customer_id,
         e.event_type,
         COUNT(*) AS event_count
  FROM events AS e
  GROUP BY e.customer_id, e.event_type
)
SELECT customer_id,
       jsonb_object_agg(event_type, event_count ORDER BY event_type) AS counts_by_type
FROM event_counts
GROUP BY customer_id
ORDER BY customer_id;
```

**Expected shape:** One row per customer with events.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-28 Exercise 4, read from `events`. Build the answer toward `customer_id`, and `counts_by_type`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-28 Exercise 4, expected output: One row per customer with events. The final columns are `customer_id`, and `counts_by_type`. The final order is `customer_id`.
- **Independent verification:** For sql-28 Exercise 4, independently aggregate `events` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `counts_by_type` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `counts_by_type` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-28 Exercise 4, run `event_counts` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-28 Exercise 4, the solution actually uses `WITH`, `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `events`, preserve one row per `customer_id`, and finish with `customer_id`, and `counts_by_type` ordered by `customer_id`.
- **Alternative/trade-off:** For sql-28 Exercise 4, the chosen form is justified by this lesson-specific rationale: JSON objects are mappings; do not treat key order as a semantic contract. Evaluate another form against the concrete expected result (One row per customer with events) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `counts_by_type` for the existing `customer_id` tuple and verify the new tuple appears exactly once.

## Exercise 5 — Debugging

**Prompt:** Extract order ID and status text from XML documents without assuming XPath returns a scalar.

**Reasoning:** Index the XML array returned by `xpath`, cast through text, and strip element markup with `string(...)` XPath.

**Clause-by-clause reading:**

- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.

```sql
SELECT xd.doc_id,
       ((xpath('string(/order/id)', xd.payload))[1])::text::integer AS order_id,
       ((xpath('string(/order/status)', xd.payload))[1])::text AS order_status
FROM xml_docs AS xd
ORDER BY xd.doc_id;
```

**Expected shape:** One row per XML document.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-28 Exercise 5, read from `xml_docs`. Build the answer toward `doc_id`, `order_id`, and `order_status`; keep `doc_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-28 Exercise 5, expected output: One row per XML document. The final columns are `doc_id`, `order_id`, and `order_status`. The final order is `xd.doc_id`.
- **Independent verification:** For sql-28 Exercise 5, reselect the returned keys directly from the source; require unique `doc_id` where the expected grain is one row per key and confirm the projected `doc_id`, `order_id`, and `order_status` against `xml_docs`. Add one source row with a new `doc_id`; verify the result gains exactly one row carrying that `doc_id` value.
- **Intermediate relation check:** For sql-28 Exercise 5, check `xd.doc_id` before applying the row cap.
- **Clause check:** For sql-28 Exercise 5, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `xml_docs`, preserve one row per `doc_id`, and finish with `doc_id`, `order_id`, and `order_status` ordered by `xd.doc_id`.
- **Alternative/trade-off:** For sql-28 Exercise 5, the chosen form is justified by this lesson-specific rationale: Index the XML array returned by `xpath`, cast through text, and strip element markup with `string(...)` XPath. Evaluate another form against the concrete expected result (One row per XML document) and the verification above.
- **Edge case:** Add one source row with a new `doc_id`; verify the result gains exactly one row carrying that `doc_id` value.

## Exercise 6 — Extension

**Prompt:** Safely cast a numeric JSON text field from sample payloads, returning NULL for missing or malformed values.

**Reasoning:** Validate extracted text with a numeric regex before casting.

**Clause-by-clause reading:**

- `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
- `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
- `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
- `FROM`: establishes the starting relation and therefore the initial row grain.
- `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
- pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.

```sql
WITH payloads(payload) AS (
  VALUES
    ('{"amount": "12.50"}'::jsonb),
    ('{"amount": "bad"}'::jsonb),
    ('{}'::jsonb)
)
SELECT payload,
       CASE
         WHEN payload ->> 'amount' ~ '^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$'
           THEN (payload ->> 'amount')::numeric
         ELSE NULL
       END AS safe_amount
FROM payloads;
```

**Expected shape:** One row per sample payload.

Check the result at the stated grain. An alternative formulation is
valid only if it preserves the same NULL, ordering, time, money, and
cardinality contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-28 Exercise 6, read from `payloads`. Build the answer toward `payload`, and `safe_amount`; keep `payload` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-28 Exercise 6, expected output: One row per sample payload. The final columns are `payload`, and `safe_amount`.
- **Independent verification:** For sql-28 Exercise 6, reselect the returned keys directly from the source; require unique `payload` where the expected grain is one row per key and confirm the projected `payload`, and `safe_amount` against `payloads`. Repeat with `NULL` in `payload`, and `safe_amount` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-28 Exercise 6, select `payload` from `payloads` before adding derived columns.
- **Clause check:** For sql-28 Exercise 6, the solution actually uses `WITH`, `FROM`, and `SELECT`. Read only those operations: begin at `payloads`, preserve one row per `payload`, and finish with `payload`, and `safe_amount`.
- **Alternative/trade-off:** For sql-28 Exercise 6, the chosen form is justified by this lesson-specific rationale: Validate extracted text with a numeric regex before casting. Evaluate another form against the concrete expected result (One row per sample payload) and the verification above.
- **Edge case:** Repeat with `NULL` in `payload`, and `safe_amount` and state whether the row is kept, rejected, or classified.

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
