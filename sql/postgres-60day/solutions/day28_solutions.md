# Day 28 — Solutions (JSON and XML in PostgreSQL)

We parse, filter, and aggregate semi‑structured data using Postgres’s JSON/JSONB operators and functions. We also touch on indexing and performance considerations. Examples translate directly to XML via xpath()/xmlelement() where applicable.

Setup
- Tables: events(id, occurred_at, payload jsonb), products(extra jsonb)
- Core JSONB operators: -> (field as json), ->> (field as text), #> (path), #>> (path text), @> (contains), ? (key), ?| (any keys), ?& (all keys)
- Useful functions: jsonb_extract_path_text, jsonb_array_elements, jsonb_each, jsonb_build_object, jsonb_set

Exercise 1 — Extract scalar fields and filter by nested path
```sql
-- Get user_id (text) and action (text) out of payload; filter where nested path meta.channel='email'
SELECT id,
       occurred_at,
       payload->>'user_id'   AS user_id,
       payload->>'action'    AS action,
       payload#>>'{meta,channel}' AS channel
FROM events
WHERE payload@> '{"meta": {"channel": "email"}}'::jsonb
ORDER BY occurred_at DESC
LIMIT 100;
```
Explanation
- ->> casts to text directly. #>> traverses a path and returns text. @> performs a containment test; create a GIN index for speed.
- Index: `CREATE INDEX ON events USING gin (payload jsonb_path_ops);`

Exercise 2 — Unnest arrays and aggregate
```sql
-- Suppose payload has an array of tag objects: {"tags": [{"k":"color","v":"red"}, ...]}
WITH tags AS (
  SELECT id,
         occurred_at,
         t->>'k' AS k,
         t->>'v' AS v
  FROM events e,
       LATERAL jsonb_array_elements(e.payload->'tags') AS t
)
SELECT k, v, COUNT(*) AS cnt
FROM tags
GROUP BY k, v
ORDER BY cnt DESC
LIMIT 50;
```
Line‑by‑line
- LATERAL jsonb_array_elements expands each tag into its own row. Use LATERAL to pass the current row’s JSONB to the set‑returning function.
- Aggregate the exploded rows as needed.

Exercise 3 — Update a JSONB document immutably
```sql
-- Set payload.meta.processed=true; if meta is missing, create it.
UPDATE events
SET payload = jsonb_set(
               payload,
               '{meta,processed}',
               'true'::jsonb,
               true  -- create missing
             )
WHERE occurred_at >= now() - interval '7 days';
```
Notes
- jsonb_set returns a new document; JSONB is immutable. The 4th arg controls creation of missing keys.
- For large updates, batch by time or key ranges to avoid long‑running transactions.

XML sketch
- Use xpath('//book/title/text()', xml_col) to extract; unnest with unnest(xpath(...)). Casting to text may require (xpath(...))[1]::text.

Performance tips
- Avoid repetitive extraction in WHERE and SELECT by projecting into a CTE first.
- Index common predicates with GIN (jsonb_ops or jsonb_path_ops); consider partial indexes for hot paths.
