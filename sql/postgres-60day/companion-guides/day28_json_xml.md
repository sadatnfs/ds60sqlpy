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
   **Expected shape:** One row per customer.
2. **Query writing:** Find mobile-channel customers using JSONB containment.
   **Progressive hint:** `@>` tests whether the left JSONB contains the declared object.
   **Expected shape:** Customer rows whose channel is mobile.
3. **Query writing:** Count event rows with missing device metadata separately from present values.
   **Progressive hint:** Use `?` to test key existence rather than comparing extracted text to NULL.
   **Expected shape:** One summary row.
4. **Prediction:** Aggregate event-type counts into a JSONB object per customer and predict key ordering expectations.
   **Progressive hint:** JSON objects are mappings; do not treat key order as a semantic contract.
   **Expected shape:** One row per customer with events.
5. **Debugging:** Extract order ID and status text from XML documents without assuming XPath returns a scalar.
   **Progressive hint:** Index the XML array returned by `xpath`, cast through text, and strip element markup with `string(...)` XPath.
   **Expected shape:** One row per XML document.
6. **Extension:** Safely cast a numeric JSON text field from sample payloads, returning NULL for missing or malformed values.
   **Progressive hint:** Validate extracted text with a numeric regex before casting.
   **Expected shape:** One row per sample payload.

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
