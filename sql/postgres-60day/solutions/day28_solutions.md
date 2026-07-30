# Day 28 solutions — JSON/JSONB and XML in PostgreSQL

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

## Final self-check

- Can you explain the logical grain before and after every aggregation?
- Are missing values preserved or converted only by an explicit rule?
- Does every ordered result have a deterministic final tie-breaker?
- Are money and time assumptions visible beside the calculation?
- Does the complete executable solution finish with `ROLLBACK`?
