# Day 28: JSON/JSONB and XML in PostgreSQL (Companion Guide)

## How to run this lesson

In `./classroom`, pick **sql-28** and run **Whole SQL lesson (psql)**. The
file it runs,
`.learning/sql/sql-28/lesson/workspace/sql/postgres-60day/day28_json_xml.sql`,
only reads `events`, `customers` and `xml_docs` in `advanced_sql_training`
and ends with `ROLLBACK`. Example 1 prints 50 rows; widen your terminal so
the JSON columns do not wrap. See
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom)
for the steps every lesson shares.

### Optional contributor notebook route

A notebook shows `jsonb` and `xml` values as plain strings, which makes
comparing `->` with `->>` easy
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-28
```

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 27; pivoting and unpivoting](day27_pivot_unpivot.md)
- **Artifacts:** [learner SQL](../day28_json_xml.sql) ·
  [solution reasoning](../solutions/day28_solutions.md) ·
  [executable solution](../solutions/day28_solutions.sql)

## A beginner's mental model for this lesson

Two columns in this database hold documents instead of plain values:
`events.metadata` is `jsonb` and `xml_docs.payload` is `xml`. SQL cannot see
inside them until you extract a value, and every extraction answers three
questions:

1. **Which path?** `metadata ->> 'device'` follows one key. In XML,
   `xpath('/order/status', payload)` follows an element path.
2. **What type comes back?** `->` returns `jsonb`, `->>` returns `text`, and
   `xpath` returns an array of `xml`. You usually need `[1]` and one or two
   casts before you have a number or a plain string.
3. **What if it is missing?** A missing JSON key gives `NULL`. A missing XML
   element gives an empty array, or an empty string when you use
   `string(...)`. A value that exists but has the wrong format makes a cast
   fail.

The fixture is very regular, which makes these rules easy to check. All
20,000 events have the same three keys, `path`, `device` and `campaign`, and
each campaign value covers 4,000 events. Each of the 500 customers has an
`attributes` object with `channel` and `referrer`, and each of the 1,000 XML
documents is a small `<order>` with an `<id>` and a `<status>`. Real data is
rarely this tidy, so the answers still guard against missing keys and bad
values.

## Two worked SQL examples

### Example 1

```sql
SELECT
  event_id,
  event_type,
  metadata ->> 'path' AS path,
  metadata ->> 'device' AS device,
  metadata ->> 'campaign' AS campaign
FROM
  events
ORDER BY
  event_id DESC
LIMIT 50;
```

**How to read it:** Each `->>` pulls one key out of `metadata` as
text, so `path`, `device` and `campaign` are ordinary text columns.
`ORDER BY event_id DESC LIMIT 50` keeps the newest 50 events by id; the
`event_type` column is a real table column, not part of the JSON.

**Expected result/shape:** 50 rows from event 20000 down to 19951.
The first is a `support` event with `/help`, `web` and `none`; the next is a
`purchase` with `/cart`, `android` and `winter`. No cell is `NULL`, because
every event has all three keys.

### Example 2

```sql
SELECT
  metadata ->> 'device' AS device,
  COUNT(*) AS cnt
FROM
  events
WHERE
  metadata ->> 'campaign' IN ('spring', 'summer')
GROUP BY
  device
ORDER BY
  cnt DESC,
  device NULLS LAST;
```

**How to read it:** The `WHERE` compares extracted text, so only
events whose campaign is exactly `spring` or `summer` remain. Grouping by the
`device` alias then counts those events per device; `cnt DESC` puts the
largest group first and `device` breaks ties.

**Expected result/shape:** Three rows that add to 8,000, the two
campaigns at 4,000 each: `android` 2,667, `web` 2,667 and `ios` 2,666.
`android` comes before `web` only because of the alphabetical tie-break.

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
- **Review loop:** before trusting an extraction, list the keys that
  actually occur with `SELECT DISTINCT jsonb_object_keys(...)` and count how
  many rows have each one.

## Exercises

Query JSONB and XML with explicit path, type, missing-key, and safe-cast behavior instead of assuming semi-structured data is schema-free.

For each answer, write down the operator you will use and the
type it returns before you run it: `->>` gives text, `@>` and `?` give
booleans, `xpath` gives an array. The last answer is the only one where a
cast can fail, so plan its guard first.

1. **Query writing:** Extract customer acquisition channel and referrer from JSONB attributes.
   **Progressive hint:** `->>` returns text and naturally yields NULL for a missing key.
   **Inputs/evidence:** For sql-28 Exercise 1, read the 500 rows of `customers` and pull two text values out of the `attributes` JSONB column with `->>`: `attributes ->> 'channel'` and `attributes ->> 'referrer'`.
   **Expected result/shape:** For sql-28 Exercise 1, expected output: exactly 500 rows, one per customer, with no NULL in either extracted column; `channel` splits into 167 `mobile`, 166 `store`, and 167 `web`, and `referrer` into 125 each of `ad`, `direct`, `email`, and `seo`. The final columns are `customer_id`, `channel`, and `referrer`. The final order is `c.customer_id`.
   **Verify:** For sql-28 Exercise 1, confirm 500 rows and that customer 1 shows `web` and `seo`, matching `SELECT attributes FROM customers WHERE customer_id = 1`; then compare `'{"channel": "web"}'::jsonb ->> 'referrer'`, which returns NULL for the missing key, with `-> 'channel'`, which returns the JSONB value `"web"` with its quotes instead of plain text.
2. **Query writing:** Find mobile-channel customers using JSONB containment.
   **Progressive hint:** `@>` tests whether the left JSONB contains the declared object.
   **Inputs/evidence:** For sql-28 Exercise 2, read `customers` and keep the rows whose `attributes` JSONB contains the pair `{"channel": "mobile"}`, tested with the containment operator `@>`.
   **Expected result/shape:** For sql-28 Exercise 2, expected output: exactly 167 rows, customer IDs 2 through 500, each with `attributes ->> 'channel'` equal to `mobile`. The final columns are `customer_id`, `full_name`, and `attributes`. The final order is `c.customer_id`.
   **Verify:** For sql-28 Exercise 2, confirm that the text filter `WHERE attributes ->> 'channel' = 'mobile'` also returns 167 rows and that `WHERE NOT attributes @> '{"channel": "mobile"}'` returns the other 333; then check that containment is exact: `'{"channel": "Mobile"}'` matches 0 customers, and `'{"channel": ["mobile", "web"]}'::jsonb @> '{"channel": "mobile"}'` returns false because an array does not contain a bare string.
3. **Query writing:** Count event rows with missing device metadata separately from present values.
   **Progressive hint:** Use `?` to test key existence rather than comparing extracted text to NULL.
   **Inputs/evidence:** For sql-28 Exercise 3, read from `events` and count rows whose `metadata` contains the key `device` (`metadata ? 'device'`), rows without that key, and all rows.
   **Expected result/shape:** For sql-28 Exercise 3, expected output: One summary row. The final columns are `has_device_key`, `missing_device_key`, and `all_events`.
   **Verify:** For sql-28 Exercise 3, confirm one row with `has_device_key` 20000, `missing_device_key` 0, and `all_events` 20000; then test `VALUES ('{"device": null}'::jsonb), ('{}'::jsonb)`: `?` returns true and false, while `->> 'device' IS NULL` is true for both, so only `?` separates a present JSON null from a missing key.
4. **Prediction:** Aggregate event-type counts into a JSONB object per customer and predict key ordering expectations.
   **Progressive hint:** JSON objects are mappings; do not treat key order as a semantic contract.
   **Inputs/evidence:** For sql-28 Exercise 4, read the 20000 `events` rows, count them per `customer_id` and `event_type` in `event_counts`, then fold each customer's counts into one JSONB object with `jsonb_object_agg(event_type, event_count ORDER BY event_type)`.
   **Expected result/shape:** For sql-28 Exercise 4, expected output: exactly 500 rows, and in this seed all 500 objects are the same, `{"support": 8, "checkout": 8, "purchase": 8, "page_view": 8, "add_to_cart": 8}`, because every customer has 8 events of each of the 5 types; JSONB stores shorter keys first, so the `ORDER BY` does not fix the printed key order. The final columns are `customer_id`, and `counts_by_type`. The final order is `customer_id`.
   **Verify:** For sql-28 Exercise 4, confirm every object has 5 keys and that summing `jsonb_each_text` values over all rows gives 20000, the `events` row count; then, inside `BEGIN ... ROLLBACK`, insert `(1, 'refund')` and `(NULL, 'page_view')` into `events (customer_id, event_type)` and confirm 501 rows: customer 1 gains `"refund": 1`, and a NULL `customer_id` row appears holding `{"page_view": 1}`.
5. **Debugging:** Extract order ID and status text from XML documents without assuming XPath returns a scalar.
   **Progressive hint:** Index the XML array returned by `xpath`, cast through text, and strip element markup with `string(...)` XPath.
   **Inputs/evidence:** For sql-28 Exercise 5, read the 1000 rows of `xml_docs`, take the first element of `xpath('string(/order/id)', payload)` and of `xpath('string(/order/status)', payload)`, and cast the XML results through `text` to `integer` and `text`.
   **Expected result/shape:** For sql-28 Exercise 5, expected output: exactly 1000 rows, where `order_id` equals `doc_id` in every row and `order_status` splits into 199 `delivered`, 201 `paid`, 202 `placed`, 199 `returned`, and 199 `shipped`. The final columns are `doc_id`, `order_id`, and `order_status`. The final order is `xd.doc_id`.
   **Verify:** For sql-28 Exercise 5, confirm that joining the result to `orders` on `order_id` matches all 1000 rows with `o.status = order_status`; then show why the subscript matters: `xpath('/order/id/text()', payload)::text::integer` fails with `invalid input syntax for type integer: "{1}"`, and `string(/order/missing)` returns an empty string, so its integer cast fails with `invalid input syntax for type integer: ""`.
6. **Extension:** Safely cast a numeric JSON text field from sample payloads, returning NULL for missing or malformed values.
   **Progressive hint:** Validate extracted text with a numeric regex before casting.
   **Inputs/evidence:** For sql-28 Exercise 6, read three sample documents from the inline `payloads` relation: `{"amount": "12.50"}`, `{"amount": "bad"}`, and `{}`, and cast `payload ->> 'amount'` to `numeric` only when the text passes the numeric pattern.
   **Expected result/shape:** For sql-28 Exercise 6, expected output: three rows with columns `payload` and `safe_amount`, one per sample document: `12.50`, `NULL`, and `NULL`. No row is removed, and no cast error stops the query.
   **Verify:** For sql-28 Exercise 6, confirm that a bare `(payload ->> 'amount')::numeric` over the same rows fails with SQLSTATE `22P02` (`invalid input syntax for type numeric: "bad"`); then add `{"amount": "1e3"}` and observe that the pattern returns `NULL` although `pg_input_is_valid('1e3', 'numeric')` returns `true`.

## Common mistakes and how to recover

- **Casting extracted text without a check.** `('{"amount": "bad"}'::jsonb
  ->> 'amount')::numeric` fails with
  `invalid input syntax for type numeric: "bad"`, and one bad row stops the
  whole query. Test the text first, as the last answer does.
- **Using `->` where you need `->>`.** `metadata -> 'device'` returns
  `"web"` as `jsonb`, with quotes; comparing it to the text `'web'` will not
  work. Use `->>` to compare with text.
- **Treating `IS NULL` as "key missing".** For `'{"device": null}'`,
  `? 'device'` is true but `->> 'device'` is `NULL`. Use `?` when the
  question is whether the key exists.
- **Casting a raw XPath element.** `(xpath('/order/id', payload))[1]::text`
  is `<id>1</id>`, so casting it to `integer` fails. Wrap the path in
  `string(...)` or select `text()` to get the bare value.
- **Matching case that is not there.** `@> '{"channel": "Mobile"}'` finds
  no customers, because JSON comparison is case-sensitive and the data uses
  `mobile`.
- More recovery steps are in
  [Recover from common failures](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Is every cast protected by an existence/type/format check?
- Are frequently joined keys kept relational rather than hidden in documents?

## Next step

Continue to [Day 29; pattern matching](day29_pattern_matching.md).

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
  - `jsonb_path_ops` builds a smaller GIN index that supports only `@>`, `@?`, and `@@`
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

Further reading
- JSON functions: https://www.postgresql.org/docs/17/functions-json.html
- JSONB indexing: https://www.postgresql.org/docs/17/datatype-json.html#JSON-INDEXING
- XML: https://www.postgresql.org/docs/17/functions-xml.html

## Ask an AI tutor about this lesson

A tutor can write malformed JSON or XML for you to test your guards
against, which this tidy fixture never provides
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-28: JSONB and XML in PostgreSQL.

I have completed the direct catalog prerequisite: `sql-27`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day28_json_xml.md
- Answer-free learner SQL: sql/postgres-60day/day28_json_xml.sql

Key terms to teach in context: JSONB, Containment, Path extraction. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Extract `metadata->>'campaign'` as text, keep the raw JSONB beside it, and group missing values separately. For XML, extract the first XPath result, validate its text form, cast to integer, and left-join orders so malformed or unmatched documents remain visible.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
