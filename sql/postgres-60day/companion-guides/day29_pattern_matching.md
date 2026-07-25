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

## Exercises

Complete the prompts in the [learner SQL](../day29_pattern_matching.sql). Build
a small valid/invalid `VALUES` suite and return every expected versus observed
match.

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

Exercises from the learner script
1) Find customer emails that begin with `customer1`, followed by exactly two
   digits.
2) Use full-text search to find products matching both `home` and `product`.

The maintained regex assumes the seeded `@example.com` domain and anchors the
whole string: `^customer1[0-9]{2}@example\.com$`. In the full-text query, `&`
means both lexemes are required; `|` would change the prompt to OR.

Further reading
- Pattern matching: https://www.postgresql.org/docs/current/functions-matching.html
- pg_trgm: https://www.postgresql.org/docs/current/pgtrgm.html
