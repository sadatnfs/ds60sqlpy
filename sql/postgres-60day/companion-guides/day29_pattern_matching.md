# Day 29 — Pattern Matching: LIKE/ILIKE, SIMILAR TO, and Regular Expressions (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 28 — JSONB and XML](day28_json_xml.md)
- **Artifacts:** [learner SQL](../day29_pattern_matching.sql) ·
  [solution reasoning](../solutions/day29_solutions.md) ·
  [executable solution](../solutions/day29_solutions.sql)

## Learning objectives

- Select the simplest matching operator that expresses a search or validation.
- Anchor validation patterns and reason about index support.

## Vocabulary and concepts

- **Wildcard:** `%` or `_` in a `LIKE` pattern.
- **Anchor:** `^` or `$`, which binds a regular expression to a string boundary.
- **Sargable predicate:** a search condition an index can support directly.

## Worked example / walkthrough

Compare `email ~ 'customer1[0-9]{2}'` with the anchored
`email ~ '^customer1[0-9]{2}@example\\.com$'`. Add surrounding text to a test
value and show why an unanchored validation can accept only a matching
substring.

## Practice assumptions and review method

- **Focus:** Choose literal, wildcard, or regular-expression matching from the text grammar and make case, escaping, and anchoring explicit.
- **Assumptions:** PostgreSQL `LIKE` is case-sensitive, `ILIKE` is case-insensitive, and POSIX regex operators use `~`/`~*`. Collation can affect text behavior.
- **Failure to watch for:** Leading wildcards can prevent ordinary b-tree use; unanchored or overly broad regex patterns can match more text than intended.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Choose literal, wildcard, or regular-expression matching from the text grammar and make case, escaping, and anchoring explicit.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Find customer names beginning with `Customer 1` case-insensitively.
   **Progressive hint:** `ILIKE 'Customer 1%'` uses `%` for any suffix.
   **Expected shape:** Matching customer rows in stable ID order.
2. **Query writing:** Find emails that match the course's simple lowercase example.com pattern.
   **Progressive hint:** Anchor both ends and escape the literal dot in the POSIX regex.
   **Expected shape:** Only matching non-null email rows.
3. **Query writing:** Return event paths under `/p/` using JSON extraction and an anchored pattern.
   **Progressive hint:** Extract path text, then anchor the literal prefix.
   **Expected shape:** Events whose path begins `/p/`.
4. **Prediction:** Match literal percent and underscore characters in sample text and contrast them with wildcard behavior.
   **Progressive hint:** Declare an escape character and prefix each literal wildcard.
   **Expected shape:** Only the two rows containing the requested literal symbols.
5. **Debugging:** Extract the captured numeric suffix from a valid customer name without replacing the entire string blindly.
   **Progressive hint:** First assert the anchored grammar, then use `substring(... FROM regex)`.
   **Expected shape:** One row per valid course customer name.
6. **Extension:** Classify emails as course example, other valid-looking, missing, or malformed using ordered patterns.
   **Progressive hint:** Handle NULL first, then most specific anchored pattern, then a bounded general pattern.
   **Expected shape:** One row per customer with one classification.

## Self-check

- Is the pattern a substring search or a whole-value validation?
- Could a leading wildcard or function-wrapped column prevent ordinary B-tree
  index use?

## Next step

Continue to [Day 30 — Phase 2 project](day30_phase2_project.md).

## Deep dive and reference

Learning objectives
- Use LIKE/ILIKE for simple wildcard matching and understand index implications
- Apply SIMILAR TO and POSIX regular expressions (~, ~*, !~, !~*) for complex patterns
- Build robust text filters, validators, and extractors; know when to use trigram/FTS

Why this matters
User inputs, product codes, and free text require flexible matching. Good patterns minimize false matches and run fast on large tables.

Core concepts and deep dive
- LIKE/ILIKE
  - % any-length wildcard; _ single char; ILIKE is case-insensitive (Postgres extension)
  - Index use: prefix patterns (foo%) can use btree indexes; leading wildcard (%foo) cannot; consider pg_trgm or re-architecture
- SIMILAR TO
  - SQL standard regex-like; less commonly used in Postgres; prefer POSIX regex operators
- POSIX regex operators
  - ~ match case-sensitive; ~* case-insensitive; !~ negation; supports anchors ^$, character classes, quantifiers
  - SUBSTRING(str FROM 'regex') to extract; REGEXP_REPLACE for cleanup
- Performance aids
  - pg_trgm extension + GIN index for ILIKE/regex with wildcards on large text columns
  - Functional indexes on LOWER(col) to support case-insensitive equality
- Validation vs search
  - Validation uses ^...$ anchored patterns; search may be substring (no anchors)

Patterns
- Email-like validation: email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
- Domain filters: LOWER(email) LIKE '%@example.com'
- Product-name matching: `name ~ '^Product [0-9]{2,3}$'`

Pitfalls
- Unanchored regex in validation allows partial matches; use anchors
- Locale issues in case-folding; consider citext for equality semantics
- Regex backtracking on catastrophic patterns; keep patterns simple and specific

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Pattern matching: https://www.postgresql.org/docs/current/functions-matching.html
- pg_trgm: https://www.postgresql.org/docs/current/pgtrgm.html
