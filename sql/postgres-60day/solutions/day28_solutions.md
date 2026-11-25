# Day 28 solutions: JSON/JSONB and XML in PostgreSQL


<!-- beginner-solution-enrichment -->
## How to study and run this solution

The answers read `customers.attributes`, `events.metadata` and
`xml_docs.payload`, and the last one uses three inline sample payloads.
Nothing is written, and there is no index on the JSON columns, so every
filter is a sequential scan. [Read a solution](../../STUDY-GUIDE.md#read-a-solution)
covers the general approach.

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day28_solutions.sql
```

## How these answers fit together

The first three answers ask whether a key or value is present: `->>` returns
it or `NULL`, `@>` tests containment, and `?` tests that a key exists. The
fourth builds JSON instead of reading it. The fifth does the same extraction
work for XML, where every result arrives as an array. The sixth adds the
guard you need before turning extracted text into a number. The learner
file is [day28_json_xml.sql](../day28_json_xml.sql).

## Reading contract

- **Focus:** Query JSONB and XML with explicit path, type, missing-key, and safe-cast behavior instead of assuming semi-structured data is schema-free.
- **Assumptions:** JSON text extraction with `->>` returns text or NULL. XML XPath results are arrays. Course metadata keys are small and deterministic.
- **Primary pitfall:** Casting missing or malformed JSON text directly raises; broad JSON containment or regex extraction needs validation and appropriate indexing evidence.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** Extract customer acquisition channel and referrer from JSONB attributes.

**Reasoning:** `->>` returns text and naturally yields NULL for a missing key.

```sql
SELECT
  c.customer_id,
  c.attributes ->> 'channel' AS channel,
  c.attributes ->> 'referrer' AS referrer
FROM
  customers AS c
ORDER BY
  c.customer_id;
```

**Expected shape:** One row per customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-28 Exercise 1, read the 500 rows of `customers` and pull two text values out of the `attributes` JSONB column with `->>`: `attributes ->> 'channel'` and `attributes ->> 'referrer'`.
- **Expected result/shape:** For sql-28 Exercise 1, expected output: exactly 500 rows, one per customer, with no NULL in either extracted column; `channel` splits into 167 `mobile`, 166 `store`, and 167 `web`, and `referrer` into 125 each of `ad`, `direct`, `email`, and `seo`. The final columns are `customer_id`, `channel`, and `referrer`. The final order is `c.customer_id`.
- **Independent verification:** For sql-28 Exercise 1, confirm 500 rows and that customer 1 shows `web` and `seo`, matching `SELECT attributes FROM customers WHERE customer_id = 1`; then compare `'{"channel": "web"}'::jsonb ->> 'referrer'`, which returns NULL for the missing key, with `-> 'channel'`, which returns the JSONB value `"web"` with its quotes instead of plain text.
- **Intermediate relation check:** `customers` has 500 rows, and the result has one row per customer, ordered by `customer_id`. Customer 1 is `web` with referrer `seo`, and customer 2 is `mobile` with `email`.
- **Clause check:** `->>` returns text and gives `NULL` for a key that is absent. In this fixture every customer has both `channel` and `referrer`, so neither column contains `NULL`; the channels split 167 mobile, 166 store and 167 web.
- **Alternative/trade-off:** `c.attributes -> 'channel'` returns `jsonb` and prints `"web"` with quotes. Use it when you want to pass the value on as JSON, and `->>` when you want text to compare or display.
- **Edge case:** A key stored as JSON `null` and a missing key both come out as `NULL` with `->>`. If the difference matters, check `c.attributes ? 'referrer'` as well.

## Exercise 2: Query writing

**Prompt:** Find mobile-channel customers using JSONB containment.

**Reasoning:** `@>` tests whether the left JSONB contains the declared object.

```sql
SELECT
  c.customer_id,
  c.full_name,
  c.attributes
FROM
  customers AS c
WHERE
  c.attributes @> '{"channel": "mobile"}'::jsonb
ORDER BY
  c.customer_id;
```

**Expected shape:** Customer rows whose channel is mobile.

### Reasoning and verification

- **Inputs/evidence:** For sql-28 Exercise 2, read `customers` and keep the rows whose `attributes` JSONB contains the pair `{"channel": "mobile"}`, tested with the containment operator `@>`.
- **Expected result/shape:** For sql-28 Exercise 2, expected output: exactly 167 rows, customer IDs 2 through 500, each with `attributes ->> 'channel'` equal to `mobile`. The final columns are `customer_id`, `full_name`, and `attributes`. The final order is `c.customer_id`.
- **Independent verification:** For sql-28 Exercise 2, confirm that the text filter `WHERE attributes ->> 'channel' = 'mobile'` also returns 167 rows and that `WHERE NOT attributes @> '{"channel": "mobile"}'` returns the other 333; then check that containment is exact: `'{"channel": "Mobile"}'` matches 0 customers, and `'{"channel": ["mobile", "web"]}'::jsonb @> '{"channel": "mobile"}'` returns false because an array does not contain a bare string.
- **Intermediate relation check:** All 500 customers are tested, and 167 have `channel` set to `mobile`, from customer 2 up to customer 500.
- **Clause check:** `@>` is true when the left document contains every key and value of the right one. `'{"channel": "mobile"}'` matches any customer with that pair, whatever else is in `attributes`; the result keeps `full_name` and the whole document.
- **Alternative/trade-off:** `c.attributes ->> 'channel' = 'mobile'` returns the same 167 rows. `@>` is the form a GIN index on `attributes` can use; with no such index today, the plan is a `Seq Scan` with the containment test as its filter.
- **Edge case:** Containment compares JSON values exactly, so `"Mobile"` finds nothing, and `{"channel": "mobile", "referrer": "ad"}` would require both pairs.

## Exercise 3: Query writing

**Prompt:** Count event rows with missing device metadata separately from present values.

**Reasoning:** Use `?` to test key existence rather than comparing extracted text to NULL.

```sql
SELECT
  COUNT(*) FILTER (WHERE e.metadata ? 'device') AS has_device_key,
  COUNT(*) FILTER (WHERE NOT e.metadata ? 'device') AS missing_device_key,
  COUNT(*) AS all_events
FROM
  events AS e;
```

**Expected shape:** One summary row.

### Reasoning and verification

- **Inputs/evidence:** For sql-28 Exercise 3, read from `events` and count rows whose `metadata` contains the key `device` (`metadata ? 'device'`), rows without that key, and all rows.
- **Expected result/shape:** For sql-28 Exercise 3, expected output: One summary row. The final columns are `has_device_key`, `missing_device_key`, and `all_events`.
- **Independent verification:** For sql-28 Exercise 3, confirm one row with `has_device_key` 20000, `missing_device_key` 0, and `all_events` 20000; then test `VALUES ('{"device": null}'::jsonb), ('{}'::jsonb)`: `?` returns true and false, while `->> 'device' IS NULL` is true for both, so only `?` separates a present JSON null from a missing key.
- **Intermediate relation check:** The query has no `GROUP BY`, so all 20,000 events become one row with three counts.
- **Clause check:** `metadata ? 'device'` is true for all 20,000 events, so `has_device_key` is 20,000, `missing_device_key` is 0 and the two add to `all_events`. Checking that sum is the point of the third column.
- **Alternative/trade-off:** `metadata ->> 'device' IS NULL` also returns 0 here, but it cannot tell a missing key from a key whose value is JSON `null`. `?` answers only the existence question, which is what the prompt asks.
- **Edge case:** `NOT e.metadata ? 'device'` relies on `metadata` never being `NULL`. The column is `NOT NULL` with a default of `'{}'`, so every row is counted in exactly one of the two filtered columns.

## Exercise 4: Prediction

**Prompt:** Aggregate event-type counts into a JSONB object per customer and predict key ordering expectations.

**Reasoning:** JSON objects are mappings; do not treat key order as a semantic contract.

```sql
WITH event_counts AS (
  SELECT
    e.customer_id,
    e.event_type,
    COUNT(*) AS event_count
  FROM
    events AS e
  GROUP BY
    e.customer_id,
    e.event_type
)
SELECT
  customer_id,
  jsonb_object_agg(event_type, event_count ORDER BY event_type) AS counts_by_type
FROM
  event_counts
GROUP BY
  customer_id
ORDER BY
  customer_id;
```

**Expected shape:** One row per customer with events.

### Reasoning and verification

- **Inputs/evidence:** For sql-28 Exercise 4, read the 20000 `events` rows, count them per `customer_id` and `event_type` in `event_counts`, then fold each customer's counts into one JSONB object with `jsonb_object_agg(event_type, event_count ORDER BY event_type)`.
- **Expected result/shape:** For sql-28 Exercise 4, expected output: exactly 500 rows, and in this seed all 500 objects are the same, `{"support": 8, "checkout": 8, "purchase": 8, "page_view": 8, "add_to_cart": 8}`, because every customer has 8 events of each of the 5 types; JSONB stores shorter keys first, so the `ORDER BY` does not fix the printed key order. The final columns are `customer_id`, and `counts_by_type`. The final order is `customer_id`.
- **Independent verification:** For sql-28 Exercise 4, confirm every object has 5 keys and that summing `jsonb_each_text` values over all rows gives 20000, the `events` row count; then, inside `BEGIN ... ROLLBACK`, insert `(1, 'refund')` and `(NULL, 'page_view')` into `events (customer_id, event_type)` and confirm 501 rows: customer 1 gains `"refund": 1`, and a NULL `customer_id` row appears holding `{"page_view": 1}`.
- **Intermediate relation check:** `event_counts` has 2,500 rows: 500 customers times 5 event types, each with exactly 8 events. Every event has a `customer_id`, so no `NULL` group appears.
- **Clause check:** `jsonb_object_agg` turns each customer's five rows into one object with five keys, so the result has 500 rows. Customer 1 shows 8 for each of `support`, `checkout`, `purchase`, `page_view` and `add_to_cart`.
- **Alternative/trade-off:** The `ORDER BY event_type` inside the aggregate does not set the printed order, because `jsonb` stores keys shortest first. `json_object_agg` keeps the insertion order if a human will read the output.
- **Edge case:** A customer with no events gets no row at all. A customer missing one event type gets an object with four keys, not a key with 0, so readers should treat an absent key as zero.

## Exercise 5: Debugging

**Prompt:** Extract order ID and status text from XML documents without assuming XPath returns a scalar.

**Reasoning:** Index the XML array returned by `xpath`, cast through text, and strip element markup with `string(...)` XPath.

```sql
SELECT
  xd.doc_id,
  ((xpath('string(/order/id)', xd.payload))[1])::text::integer AS order_id,
  ((xpath('string(/order/status)', xd.payload))[1])::text AS order_status
FROM
  xml_docs AS xd
ORDER BY
  xd.doc_id;
```

**Expected shape:** One row per XML document.

### Reasoning and verification

- **Inputs/evidence:** For sql-28 Exercise 5, read the 1000 rows of `xml_docs`, take the first element of `xpath('string(/order/id)', payload)` and of `xpath('string(/order/status)', payload)`, and cast the XML results through `text` to `integer` and `text`.
- **Expected result/shape:** For sql-28 Exercise 5, expected output: exactly 1000 rows, where `order_id` equals `doc_id` in every row and `order_status` splits into 199 `delivered`, 201 `paid`, 202 `placed`, 199 `returned`, and 199 `shipped`. The final columns are `doc_id`, `order_id`, and `order_status`. The final order is `xd.doc_id`.
- **Independent verification:** For sql-28 Exercise 5, confirm that joining the result to `orders` on `order_id` matches all 1000 rows with `o.status = order_status`; then show why the subscript matters: `xpath('/order/id/text()', payload)::text::integer` fails with `invalid input syntax for type integer: "{1}"`, and `string(/order/missing)` returns an empty string, so its integer cast fails with `invalid input syntax for type integer: ""`.
- **Intermediate relation check:** `xml_docs` has 1,000 documents, and the result has one row per `doc_id`. Document 1 is `<order><id>1</id><status>paid</status></order>`.
- **Clause check:** `xpath('string(/order/id)', ...)` returns a one-element array holding the text `1`; `[1]` takes that element and `::text::integer` turns it into a number. The order ids run from 1 to 1,000, and the statuses split 202 placed, 201 paid and 199 each for shipped, delivered and returned.
- **Alternative/trade-off:** `xpath('/order/status/text()', payload)` also returns bare text. Without `string(...)` or `text()`, `[1]::text` is `<status>paid</status>`, and casting `<id>1</id>` to `integer` fails.
- **Edge case:** For a missing element, `string(...)` returns an empty string, and `''::integer` fails. Wrap the cast in `NULLIF(..., '')` if documents may lack an `<id>`.

## Exercise 6: Extension

**Prompt:** Safely cast a numeric JSON text field from sample payloads, returning NULL for missing or malformed values.

**Reasoning:** Validate extracted text with a numeric regex before casting.

```sql
WITH payloads (
  payload
) AS (
  VALUES ('{"amount": "12.50"}'::jsonb),
    ('{"amount": "bad"}'::jsonb),
    ('{}'::jsonb))
SELECT
  payload,
  CASE WHEN payload ->> 'amount' ~ '^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$' THEN
    (payload ->> 'amount')::numeric
  ELSE
    NULL
  END AS safe_amount
FROM
  payloads;
```

**Expected shape:** One row per sample payload.

### Reasoning and verification

- **Inputs/evidence:** For sql-28 Exercise 6, read three sample documents from the inline `payloads` relation: `{"amount": "12.50"}`, `{"amount": "bad"}`, and `{}`, and cast `payload ->> 'amount'` to `numeric` only when the text passes the numeric pattern.
- **Expected result/shape:** For sql-28 Exercise 6, expected output: three rows with columns `payload` and `safe_amount`, one per sample document: `12.50`, `NULL`, and `NULL`. No row is removed, and no cast error stops the query.
- **Independent verification:** For sql-28 Exercise 6, confirm that a bare `(payload ->> 'amount')::numeric` over the same rows fails with SQLSTATE `22P02` (`invalid input syntax for type numeric: "bad"`); then add `{"amount": "1e3"}` and observe that the pattern returns `NULL` although `pg_input_is_valid('1e3', 'numeric')` returns `true`.
- **Intermediate relation check:** `payloads` is three inline rows: a good amount, a bad one and an empty object.
- **Clause check:** The `CASE` casts only when the extracted text matches the decimal pattern. The result is 12.50, then `NULL` for `"bad"`, then `NULL` for `{}`, where `->>` already returns `NULL` and the regex test is not true.
- **Alternative/trade-off:** On PostgreSQL 16 and later, `pg_input_is_valid(payload ->> 'amount', 'numeric')` checks the text with the real numeric parser. It also accepts `1e3`, which the regex rejects.
- **Edge case:** If the JSON stores a number instead of a string, `->>` still returns its text, such as `12.5`, and the same guard works. Check `jsonb_typeof` when you must know which form the producer sent.

## Final self-check

- Which operator returns `jsonb` and which returns `text`?
- Why does `?` answer a different question from `->> ... IS NULL`?
- What extra step does an `xpath` result need before you can cast it?
- Which input in the last answer would raise an error without the guard?
