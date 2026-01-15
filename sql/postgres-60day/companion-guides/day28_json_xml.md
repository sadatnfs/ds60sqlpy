# Day 28 — JSON/JSONB and XML in PostgreSQL (Companion Guide)

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
  - Event filtering: WHERE payload @> '{"channel":"Web"}'
  - Attribute extraction: (payload->>'referrer')::text AS ref
  - Flatten arrays: CROSS JOIN LATERAL jsonb_array_elements(payload->'items') AS item
  - Aggregation: jsonb_agg(obj) to reassemble nested results

XML (brief)
- xml type; xpath(text, xml) returns array of xml nodes; unnest to rows
- Use when XML is required; otherwise prefer JSONB for ergonomics and performance

Pitfalls
- Leading wildcard text search in JSONB values needs GIN + trigram or full text search
- Casting: ->> returns text; cast to numeric/date before arithmetic/comparison
- Overusing schemaless: retain core relational columns for keys, dates, and major filters; use JSONB for optional/rare attributes

Practice exercises
1) Extract campaign and channel from events.payload and compute conversion by channel.
2) Create a GIN index and compare performance of @> queries before/after.
3) Flatten line items embedded in an orders document and compute item-level revenue.

Further reading
- JSON functions: https://www.postgresql.org/docs/current/functions-json.html
- GIN indexing: https://www.postgresql.org/docs/current/textsearch-indexes.html
- XML: https://www.postgresql.org/docs/current/functions-xml.html
