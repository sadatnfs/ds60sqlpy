# Day 28 — JSON/JSONB and XML in PostgreSQL (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 27 — pivoting and unpivoting](day27_pivot_unpivot.md)
- **Artifacts:** [learner SQL](../day28_json_xml.sql) ·
  [solution reasoning](../solutions/day28_solutions.md) ·
  [executable solution](../solutions/day28_solutions.sql)

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-28 — JSON XML** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-28/lesson/workspace/sql/postgres-60day/day28_json_xml.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day28_json_xml.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day28_json_xml.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is JSONB, Containment, Path extraction. Its worked SQL reads or creates `events`, `xml_docs`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Extract metadata->>'campaign' as text, keep the raw JSONB beside it, and group missing values separately. For XML, extract the first XPath result, validate its text form, cast to integer, and left-join orders so malformed or unmatched documents remain visible.
The expected contract is that One row per customer. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day28_json_xml.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT event_id,
       event_type,
       metadata->>'path' AS path,
       metadata->>'device' AS device,
       metadata->>'campaign' AS campaign
FROM events
ORDER BY event_id DESC
LIMIT 50;
```

**How to read it:** Example 1: Start with `events` in `FROM`/`JOIN`. The final `SELECT` displays `event_id`, `event_type`, `path`, `device`, and `campaign`. `ORDER BY` determines presentation order and the final `LIMIT 50` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `event_id`, capped at 50 rows with columns `event_id`, `event_type`, `path`, `device`, and `campaign` from `events`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT metadata->>'device' AS device,
       COUNT(*) AS cnt
FROM events
WHERE metadata->>'campaign' IN ('spring','summer')
GROUP BY device
ORDER BY cnt DESC, device NULLS LAST;
```

**How to read it:** Example 2: Start with `events` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `device`, and `cnt`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `device` with columns `device`, and `cnt` from `events`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Extract and validate semi-structured values before casting or joining them.
- Choose relational columns for stable keys and JSONB for genuinely flexible
  attributes.

## Vocabulary and concepts

- **JSONB:** PostgreSQL's decomposed binary JSON representation.
- **Containment:** a structural match tested with JSONB `@>`.
- **Path extraction:** navigation to a nested value with operators such as
  `#>>`.

## Worked example / walkthrough

Extract `metadata->>'campaign'` as text, keep the raw JSONB beside it, and group
missing values separately. For XML, extract the first XPath result, validate its
text form, cast to integer, and left-join orders so malformed or unmatched
documents remain visible.

## Practice assumptions and review method

- **Focus:** Query JSONB and XML with explicit path, type, missing-key, and safe-cast behavior instead of assuming semi-structured data is schema-free.
- **Assumptions:** JSON text extraction with `->>` returns text or NULL. XML XPath results are arrays. Course metadata keys are small and deterministic.
- **Failure to watch for:** Casting missing or malformed JSON text directly raises; broad JSON containment or regex extraction needs validation and appropriate indexing evidence.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Query JSONB and XML with explicit path, type, missing-key, and safe-cast behavior instead of assuming semi-structured data is schema-free.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Extract customer acquisition channel and referrer from JSONB attributes.
   **Progressive hint:** `->>` returns text and naturally yields NULL for a missing key.
   **Inputs/evidence:** For sql-28 Exercise 1, read from `customers`. Build the answer toward `customer_id`, `channel`, and `referrer`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-28 Exercise 1, expected output: One row per customer. The final columns are `customer_id`, `channel`, and `referrer`. The final order is `c.customer_id`.
   **Verify:** For sql-28 Exercise 1, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `channel`, and `referrer` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
2. **Query writing:** Find mobile-channel customers using JSONB containment.
   **Progressive hint:** `@>` tests whether the left JSONB contains the declared object.
   **Inputs/evidence:** For sql-28 Exercise 2, read from `customers`. Build the answer toward `customer_id`, `full_name`, and `attributes`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-28 Exercise 2, expected output: Customer rows whose channel is mobile. The final columns are `customer_id`, `full_name`, and `attributes`. The final order is `c.customer_id`.
   **Verify:** For sql-28 Exercise 2, run an anti-check that counts rows where NOT ((c.attributes @> '{"channel": "mobile"}'::jsonb)); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `full_name`, and `attributes` against `customers`. Add one row for which `(c.attributes @> '{"channel": "mobile"}'::jsonb)` is true and one for which it is false; verify only the matching `customer_id` value is returned.
3. **Query writing:** Count event rows with missing device metadata separately from present values.
   **Progressive hint:** Use `?` to test key existence rather than comparing extracted text to NULL.
   **Inputs/evidence:** For sql-28 Exercise 3, read from `events`. Build the answer toward `has_device_key`, `missing_device_key`, and `all_events`; keep `has_device_key` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-28 Exercise 3, expected output: One summary row. The final columns are `has_device_key`, `missing_device_key`, and `all_events`.
   **Verify:** For sql-28 Exercise 3, reselect the returned keys directly from the source; require unique `has_device_key` where the expected grain is one row per key and confirm the projected `has_device_key`, `missing_device_key`, and `all_events` against `events`. Add one source row with a new `has_device_key`; verify the result gains exactly one row carrying that `has_device_key` value.
4. **Prediction:** Aggregate event-type counts into a JSONB object per customer and predict key ordering expectations.
   **Progressive hint:** JSON objects are mappings; do not treat key order as a semantic contract.
   **Inputs/evidence:** For sql-28 Exercise 4, read from `events`. Build the answer toward `customer_id`, and `counts_by_type`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-28 Exercise 4, expected output: One row per customer with events. The final columns are `customer_id`, and `counts_by_type`. The final order is `customer_id`.
   **Verify:** For sql-28 Exercise 4, independently aggregate `events` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `counts_by_type` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `counts_by_type` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
5. **Debugging:** Extract order ID and status text from XML documents without assuming XPath returns a scalar.
   **Progressive hint:** Index the XML array returned by `xpath`, cast through text, and strip element markup with `string(...)` XPath.
   **Inputs/evidence:** For sql-28 Exercise 5, read from `xml_docs`. Build the answer toward `doc_id`, `order_id`, and `order_status`; keep `doc_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-28 Exercise 5, expected output: One row per XML document. The final columns are `doc_id`, `order_id`, and `order_status`. The final order is `xd.doc_id`.
   **Verify:** For sql-28 Exercise 5, reselect the returned keys directly from the source; require unique `doc_id` where the expected grain is one row per key and confirm the projected `doc_id`, `order_id`, and `order_status` against `xml_docs`. Add one source row with a new `doc_id`; verify the result gains exactly one row carrying that `doc_id` value.
6. **Extension:** Safely cast a numeric JSON text field from sample payloads, returning NULL for missing or malformed values.
   **Progressive hint:** Validate extracted text with a numeric regex before casting.
   **Inputs/evidence:** For sql-28 Exercise 6, read from `payloads`. Build the answer toward `payload`, and `safe_amount`; keep `payload` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-28 Exercise 6, expected output: One row per sample payload. The final columns are `payload`, and `safe_amount`.
   **Verify:** For sql-28 Exercise 6, reselect the returned keys directly from the source; require unique `payload` where the expected grain is one row per key and confirm the projected `payload`, and `safe_amount` against `payloads`. Repeat with `NULL` in `payload`, and `safe_amount` and state whether the row is kept, rejected, or classified.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Casting missing or malformed JSON text directly raises; broad JSON containment or regex extraction needs validation and appropriate indexing evidence.
- **Unexpected row count:** display keys before aggregates, count rows after
  each join/filter stage, and find the first stage whose grain differs from the
  contract. Do not hide fanout with `DISTINCT`.
- **Unexpected `NULL` or missing row:** decide whether the fact is unknown,
  inapplicable, zero, or absent before using `COALESCE`; inspect outer-join
  predicate placement and empty-input aggregate behavior.
- **Unstable top/first/last output:** add `ORDER BY` with a unique final
  tie-breaker before `LIMIT` or order-sensitive windows/aggregates.
- **`psql` stops on an error:** fix the first error shown by
  `ON_ERROR_STOP`, restore the declared transaction/setup state, and rerun the
  complete file. A later successful statement does not validate a partial run.

## Self-check

- Is every cast protected by an existence/type/format check?
- Are frequently joined keys kept relational rather than hidden in documents?

## Next step

Continue to [Day 29 — pattern matching](day29_pattern_matching.md).

## Deep dive and reference

Learning objectives
- Store and query semi-structured data with JSONB; compare to JSON (text)
- Use JSONB operators/functions to extract, transform, and index
- Parse and query XML; know when to prefer JSONB instead

Why this matters
Real-world data often arrives as nested documents (events, APIs). Postgres’s JSONB lets you combine document flexibility with relational power and indexing.

Core concepts and deep dive (JSONB)
- Types: JSON (text-validated on insert) vs JSONB (binary, decomposed; supports indexing; preferred)
- Operators
  - -> returns JSON; ->> returns text; #>/#>> follow paths; @> containment; ? key exists; ?| any key; ?& all keys
  - || concatenation/merge; - remove key; #- remove path
- Functions
  - jsonb_build_object/array, jsonb_agg, jsonb_object_agg, jsonb_each/keys/array_elements
  - jsonb_set(target, path, value[, create_missing])
- Indexing
  - GIN on jsonb_col with default jsonb_ops supports @>, ?, ?|, ?& efficiently
  - Expression indexes on jsonb_col->>'field' for selective predicates
- Patterns
  - Event filtering: `WHERE metadata @> '{"device":"web"}'`
  - Attribute extraction: `metadata->>'campaign' AS campaign`
  - Optional arrays: `jsonb_array_elements_text(metadata->'tags')` after
    checking that the key exists and contains an array
  - Aggregation: jsonb_agg(obj) to reassemble nested results

XML (brief)
- xml type; xpath(text, xml) returns array of xml nodes; unnest to rows
- Use when XML is required; otherwise prefer JSONB for ergonomics and performance

Pitfalls
- Leading wildcard text search in JSONB values needs GIN + trigram or full text search
- Casting: ->> returns text; cast to numeric/date before arithmetic/comparison
- Overusing schemaless: retain core relational columns for keys, dates, and major filters; use JSONB for optional/rare attributes

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- JSON functions: https://www.postgresql.org/docs/current/functions-json.html
- GIN indexing: https://www.postgresql.org/docs/current/textsearch-indexes.html
- XML: https://www.postgresql.org/docs/current/functions-xml.html

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-28 — JSON XML.

I have completed the direct catalog prerequisite: `sql-27`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day28_json_xml.md
- Answer-free learner SQL: sql/postgres-60day/day28_json_xml.sql

Key terms to teach in context: JSONB, Containment, Path extraction. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Extract metadata->>'campaign' as text, keep the raw JSONB beside it, and group missing values separately. For XML, extract the first XPath result, validate its text form, cast to integer, and left-join orders so malformed or unmatched documents remain visible.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-28/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
