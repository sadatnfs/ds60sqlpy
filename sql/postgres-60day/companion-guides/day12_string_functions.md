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

## Exercises

Complete the prompts in the [learner SQL](../day12_string_functions.sql). Add
inputs with leading spaces, mixed case, a missing delimiter, and `NULL`.

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

Exercises from the learner script
1) Normalize `customers.country` to upper-case after trimming whitespace.
2) Build the product label `"<category> - <name> ($<price>)"`.

`FORMAT('%s - %s ($%s)', category, name, to_char(price, 'FM999999990.00'))`
avoids a dependency on `pg_trgm` or another extension and keeps two decimal
places in the displayed price.

Further reading
- String functions: https://www.postgresql.org/docs/current/functions-string.html
- Regex: https://www.postgresql.org/docs/current/functions-matching.html
- pg_trgm: https://www.postgresql.org/docs/current/pgtrgm.html
