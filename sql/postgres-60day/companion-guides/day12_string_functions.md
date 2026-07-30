# Day 12 — String Functions and Text Processing (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 11 — CASE expressions](day11_case_expressions.md)
- **Artifacts:** [learner SQL](../day12_string_functions.sql) ·
  [solution reasoning](../solutions/day12_solutions.md) ·
  [executable solution](../solutions/day12_solutions.sql)

## Learning objectives

- Normalize, split, concatenate, replace, and extract text with explicit
  assumptions.
- Distinguish display cleanup from a safe persistent data-quality rule.

## Vocabulary and concepts

- **Normalization:** converting equivalent text forms to one comparison form.
- **Delimiter:** a character or string separating parts of a value.
- **Regular expression:** a pattern language for matching or replacing text.

## Worked example / walkthrough

Compare a raw email with `lower(trim(email))`. Use the normalized expression for
duplicate grouping, but keep the original column visible so a reviewer can
audit what changed. Explain why silently overwriting the raw value would lose
evidence.

## Practice assumptions and review method

- **Focus:** Normalize and parse text with explicit locale/case assumptions, preserving original values when a transformation may be lossy.
- **Assumptions:** Course emails use one `@`; Unicode/collation behavior can vary. Text ordering is deterministic only with an explicit sort and tie-breaker.
- **Failure to watch for:** Regex is not a complete email or HTML parser; leading-wildcard searches may not use a normal b-tree index.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Normalize and parse text with explicit locale/case assumptions, preserving original values when a transformation may be lossy.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Return normalized customer names and lowercase emails.
   **Progressive hint:** Use `btrim` for outer whitespace and `lower` for a declared case-normalized display value.
   **Expected shape:** One row per customer.
2. **Query writing:** Extract the email domain and count customers by domain, preserving missing emails.
   **Progressive hint:** `split_part` parses the second component; CASE keeps NULL distinct.
   **Expected shape:** One row per domain label.
3. **Query writing:** Create an ordered comma-separated list of department employee names.
   **Progressive hint:** Put `ORDER BY` inside `string_agg` so concatenation order is deliberate.
   **Expected shape:** One row per department.
4. **Prediction:** Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled.
   **Progressive hint:** Use a POSIX whitespace class and the global regex flag.
   **Expected shape:** Three input/output rows.
5. **Debugging:** Safely find customer names containing a literal percent or underscore rather than treating them as wildcards.
   **Progressive hint:** Escape wildcard characters and declare the escape character.
   **Expected shape:** Rows only when the literal character occurs.
6. **Extension:** Parse the numeric suffix from names like `Customer 42`, returning NULL for nonmatching text.
   **Progressive hint:** Use a captured regex replacement only after a match predicate establishes the format.
   **Expected shape:** One row per customer with a numeric suffix.

## Self-check

- Do text transformations define behavior for `NULL` and malformed input?
- Can the normalized output be traced back to the original value?

## Next step

Continue to [Day 13 — date, time, and time zones](day13_date_time_functions.md).

## Deep dive and reference

Learning objectives
- Clean and standardize text: TRIM, UPPER/LOWER, REPLACE, REGEXP_REPLACE
- Parse text: SPLIT_PART, SUBSTRING, POSITION, regular expressions
- Compare case-insensitively: ILIKE, citext, trigram similarity (pg_trgm)

Core concepts and deep dive
- Normalization: trim whitespace, unify case, collapse repeated spaces with regex.
- Parsing: SPLIT_PART(email,'@',2) to get domain; SUBSTRING with regex for flexible extraction.
- Regular expressions: ~ (match), ~* (case-insensitive), !~ (not match); capture groups in SUBSTRING.
- Performance: Function on column may prevent index use; consider functional indexes or store normalized columns.

Examples
- Standardize emails: lower(trim(email)).
- Extract an email domain: `split_part(email, '@', 2)`.
- Build labels from `products.category`, `products.name`, and formatted
  `products.price`.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- String functions: https://www.postgresql.org/docs/current/functions-string.html
- Regex: https://www.postgresql.org/docs/current/functions-matching.html
- pg_trgm: https://www.postgresql.org/docs/current/pgtrgm.html
