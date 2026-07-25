# Day 28 — JSON/JSONB and XML in PostgreSQL (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 27 — pivoting and unpivoting](day27_pivot_unpivot.md)
- **Artifacts:** [learner SQL](../day28_json_xml.sql) ·
  [solution reasoning](../solutions/day28_solutions.md) ·
  [executable solution](../solutions/day28_solutions.sql)

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

## Exercises

Complete the prompts in the [learner SQL](../day28_json_xml.sql). Add one row
with a missing key and one with the wrong JSON value type; define the expected
result before running the query.

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

Exercises from the learner script
1) Count events by the first directory in `metadata->>'path'`.
2) Extract order IDs from `xml_docs.payload`, cast them to integers, and join
   to `orders` to validate each stored status.

`xpath` returns an XML array. Extract element `[1]`, cast the ID through text to
integer, and use a left join so malformed or unmatched documents remain
visible.

Further reading
- JSON functions: https://www.postgresql.org/docs/current/functions-json.html
- GIN indexing: https://www.postgresql.org/docs/current/textsearch-indexes.html
- XML: https://www.postgresql.org/docs/current/functions-xml.html
