# Day 29: Pattern Matching: LIKE/ILIKE, SIMILAR TO, and Regular Expressions (Companion Guide)

## How to run this lesson

Choose **sql-29** in `./classroom` and run **Whole SQL lesson (psql)**. It
executes
`.learning/sql/sql-29/lesson/workspace/sql/postgres-60day/day29_pattern_matching.sql`
against `advanced_sql_training` inside `BEGIN`/`ROLLBACK`, reading only
`customers`, `products` and `events`. Each example stops at 20 rows, so the
row counts below come from rerunning the filters without `LIMIT`. Shared
steps are in [Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

### Optional contributor notebook route

In a notebook you can test a pattern against a handful of literal strings
before pointing it at a table
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-29
```

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 28; JSONB and XML](day28_json_xml.md)
- **Artifacts:** [learner SQL](../day29_pattern_matching.sql) ·
  [solution reasoning](../solutions/day29_solutions.md) ·
  [executable solution](../solutions/day29_solutions.sql)

## A beginner's mental model for this lesson

PostgreSQL offers three pattern languages, and each fits a different job:

| Operator | Wildcards | Matches | Typical use |
|---|---|---|---|
| `LIKE` / `ILIKE` | `%` any run, `_` one character | the whole value | prefixes, suffixes, simple contains |
| `SIMILAR TO` | `LIKE` wildcards plus `{2,3}`, `[0-9]`, `|` | the whole value | rarely needed |
| `~` / `~*` | full POSIX regex | any part, unless anchored | grammar checks and capture |

The column that trips people up is "Matches". `LIKE` and `SIMILAR TO` must
match the entire string, so `'Product 12' SIMILAR TO 'Product [0-9]{2,3}'`
is true but `'Product 1'` is false. A regex only needs to match somewhere,
which is why Example 2 writes `^` and `$` around the pattern.

Case is the second choice. `LIKE` and `~` are case-sensitive; `ILIKE` and
`~*` are not. In this fixture every name starts with `Customer` and every
email is lowercase, so `full_name LIKE 'customer 1%'` finds nothing while
`ILIKE` finds 111 rows: `Customer 1`, `Customer 10` to `19`, and
`Customer 100` to `199`. That third group is a reminder that `'Customer 1%'`
is a text prefix, not a test for the number 1.

The fixture is also perfectly clean: all 500 emails look like
`customerN@example.com` and all 500 names like `Customer N`. The answers
still guard against `NULL` and malformed values, and the inline samples in
the fourth and sixth answers are where you see those branches fire.

## Two worked SQL examples

### Example 1

```sql
SELECT
  customer_id,
  full_name,
  email
FROM
  customers
WHERE
  email ILIKE '%@example.com' ESCAPE '\'
  AND full_name ILIKE 'customer %' ESCAPE '\'
ORDER BY
  customer_id
LIMIT 20;
```

**How to read it:** Both conditions use `ILIKE`, so case does not
matter. `'%@example.com'` means "ends with `@example.com`" (the `.` is a
plain dot in `LIKE`), and `'customer %'` means "starts with `customer` and a
space". `ESCAPE '\'` declares the escape character even though neither
pattern uses it.

**Expected result/shape:** Every one of the 500 customers passes
both tests, so the query returns the first 20 by id, customers 1 to 20, each
with an email such as `customer1@example.com`. Removing `LIMIT` would return
all 500 rows.

### Example 2

```sql
SELECT
  product_id,
  name,
  category
FROM
  products
WHERE
  name ~ '^Product [0-9]{2,3}$'
ORDER BY
  product_id
LIMIT 20;
```

**How to read it:** `~` is a case-sensitive regex match. `^` and `$`
pin the pattern to the whole name, `[0-9]{2,3}` requires two or three
digits, and the single space must be present. Without the anchors,
`Product 1234` would also match because `Product 123` appears inside it.

**Expected result/shape:** 291 of the 300 products match; the nine
with one-digit numbers, `Product 1` to `Product 9`, do not. The first row is
product 10, so the 20 rows run from `Product 10` to `Product 29`.

## Learning objectives

- Select the simplest matching operator that expresses a search or validation.
- Anchor validation patterns and reason about index support.

## Vocabulary and concepts

- **Wildcard:** `%` or `_` in a `LIKE` pattern.
- **Anchor:** `^` or `$`, which binds a regular expression to a string boundary.
- **Sargable predicate:** a search condition an index can support directly.

## Worked example / walkthrough

Compare `email ~ 'customer1[0-9]{2}'` with the anchored
`email ~ '^customer1[0-9]{2}@example[.]com$'`. Add surrounding text to a test
value and show why an unanchored validation can accept only a matching
substring.

## Practice assumptions and review method

- **Focus:** Choose literal, wildcard, or regular-expression matching from the text grammar and make case, escaping, and anchoring explicit.
- **Assumptions:** PostgreSQL `LIKE` is case-sensitive, `ILIKE` is case-insensitive, and POSIX regex operators use `~`/`~*`. Collation can affect text behavior.
- **Failure to watch for:** Leading wildcards can prevent ordinary b-tree use; unanchored or overly broad regex patterns can match more text than intended.
- **Review loop:** test every new pattern on three hand-written strings, one
  that should match, one that should not and one edge case, before running
  it against a table.

## Exercises

Choose literal, wildcard, or regular-expression matching from the text grammar and make case, escaping, and anchoring explicit.

For each answer, say whether the pattern checks a prefix, a
substring or the whole value, and whether case matters. Then predict the
count: in this data the answer is usually all 500 customers or a clean
subset such as 111 names or 6,667 product paths.

1. **Query writing:** Find customer names beginning with `Customer 1` case-insensitively.
   **Progressive hint:** `ILIKE 'Customer 1%'` uses `%` for any suffix.
   **Inputs/evidence:** For sql-29 Exercise 1, read the 500 rows of `customers` and keep those whose `full_name` starts with `Customer 1` under the case-insensitive `ILIKE 'Customer 1%'` prefix test.
   **Expected result/shape:** For sql-29 Exercise 1, expected output: exactly 111 rows, IDs 1, 10 through 19, and 100 through 199, because the prefix also matches longer numbers that start with 1. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
   **Verify:** For sql-29 Exercise 1, confirm that `WHERE NOT full_name ILIKE 'Customer 1%'` returns the other 389 customers, and that case-sensitive `LIKE 'Customer 1%'` also returns 111 because every seeded name is capitalized the same way; then compare `'customer 1' ILIKE 'Customer 1%'` (true) with `'customer 1' LIKE 'Customer 1%'` (false), and note that `'Customer 21'` does not match.
2. **Query writing:** Find emails that match the course's simple lowercase example.com pattern.
   **Progressive hint:** Anchor both ends and escape the literal dot in the POSIX regex.
   **Inputs/evidence:** For sql-29 Exercise 2, read `customers` and keep rows whose `email` matches the case-sensitive regular expression `^customer[0-9]+@example[.]com$`, anchored at both ends with the dot written as `[.]`.
   **Expected result/shape:** For sql-29 Exercise 2, expected output: exactly 500 rows, every customer from 1 to 500, since no seeded email is NULL or off-pattern. The final columns are `customer_id`, and `email`. The final order is `c.customer_id`.
   **Verify:** For sql-29 Exercise 2, confirm that `WHERE email !~ '^customer[0-9]+@example[.]com$'` returns 0 rows; then test the pattern on literals: `'Customer7@example.com'` fails because `~` is case-sensitive, `'customer7@example.com.au'` fails because of `$`, and `'customer7@exampleXcom'` fails with `[.]` but matches if the dot is left unescaped.
3. **Query writing:** Return event paths under `/p/` using JSON extraction and an anchored pattern.
   **Progressive hint:** Extract path text, then anchor the literal prefix.
   **Inputs/evidence:** For sql-29 Exercise 3, read the 20000 `events` rows, extract `metadata ->> 'path'` as text, and keep paths that start with `/p/` under `LIKE '/p/%'`.
   **Expected result/shape:** For sql-29 Exercise 3, expected output: exactly 6667 rows, event IDs from 1 to 19997, with only two distinct paths: `/p/1` (3333 rows) and `/p/2` (3334 rows). The final columns are `event_id`, and `path`. The final order is `e.event_id`.
   **Verify:** For sql-29 Exercise 3, confirm with `SELECT metadata ->> 'path', COUNT(*) FROM events GROUP BY 1` that the other 13333 rows carry `/`, `/cart`, `/help`, or `/search` and none has a NULL path; then check the prefix rule on literals: `'/p/'` matches, while `'/p'`, `'/P/1'`, and `'/shop/p/1'` do not.
4. **Prediction:** Match literal percent and underscore characters in sample text and contrast them with wildcard behavior.
   **Progressive hint:** Declare an escape character and prefix each literal wildcard.
   **Inputs/evidence:** For sql-29 Exercise 4, no table is read: the inline `VALUES` fixture holds `'100%'`, `'a_b'`, and `'plain'`, and the filter uses `LIKE '%\%%' ESCAPE '\'` and `LIKE '%\_%' ESCAPE '\'` so the escaped `%` and `_` are literal characters.
   **Expected result/shape:** For sql-29 Exercise 4, expected output: exactly 2 rows, `100%` and `a_b`; `plain` is filtered out. The final columns are `value`. The final order is `value`.
   **Verify:** For sql-29 Exercise 4, confirm 2 rows, then remove the escapes and confirm that `value LIKE '%%%' OR value LIKE '%_%'` returns all 3 rows, because unescaped `%` and `_` are wildcards; adding `'ab'`, `'50 percent'`, and `'a\b'` to the fixture still returns only the original 2 rows.
5. **Debugging:** Extract the captured numeric suffix from a valid customer name without replacing the entire string blindly.
   **Progressive hint:** First assert the anchored grammar, then use `substring(... FROM regex)`.
   **Inputs/evidence:** For sql-29 Exercise 5, read from `customers`, keep only names that match the anchored pattern `^Customer [0-9]+$`, and extract the number with `substring(full_name FROM '^Customer ([0-9]+)$')::integer`.
   **Expected result/shape:** For sql-29 Exercise 5, expected output: exactly 500 rows, one per customer, with `name_number` running from 1 to 500. The final columns are `customer_id`, and `name_number`. The final order is `c.customer_id`.
   **Verify:** For sql-29 Exercise 5, confirm 500 rows, because every seeded name matches, and that `name_number` equals `customer_id` on every row; the same `substring` returns NULL for `'Customer 12a'` and 7 for `'Customer 7'`.
6. **Extension:** Classify emails as course example, other valid-looking, missing, or malformed using ordered patterns.
   **Progressive hint:** Handle NULL first, then most specific anchored pattern, then a bounded general pattern.
   **Inputs/evidence:** For sql-29 Exercise 6, read from `customers` and classify each `email` with ordered `CASE` branches: `missing` for NULL, `course_example` for an address at `example.com`, `other_valid_looking` for any other `name@domain.tld`, otherwise `malformed`.
   **Expected result/shape:** For sql-29 Exercise 6, expected output: exactly 500 rows, one per customer, all labeled `course_example` in this seed, so the `missing`, `other_valid_looking`, and `malformed` branches are reached only by the fixture in the check. The final columns are `customer_id`, `email`, and `email_class`. The final order is `c.customer_id`.
   **Verify:** For sql-29 Exercise 6, confirm 500 rows, one per customer, all `course_example` on the seed; then run the same `CASE` on `VALUES (NULL), ('ann@example.com'), ('ann@school.org'), ('ann@examplexcom'), ('not-an-email')` and expect `missing`, `course_example`, `other_valid_looking`, `malformed`, and `malformed`.

## Common mistakes and how to recover

- **Reading `'Customer 1%'` as "customer number 1".** It is a text prefix,
  so it also matches `Customer 10` and `Customer 199`, 111 rows in all. Use
  `full_name = 'Customer 1'` or a regex with `$` for one exact value.
- **Forgetting that `.` is a wildcard in regex.** `'^[a-z]+@example.com$'`
  accepts `x@examplexcom`. Write `[.]` or `\.` for a literal dot, as the
  second answer does.
- **Leaving `%` and `_` unescaped.** `LIKE '%%%'` matches every string, and
  `LIKE '%_%'` matches anything with at least one character. With
  `ESCAPE '\'`, `'%\%%'` means "contains a percent sign".
- **Expecting an index to serve every `LIKE`.** In a database with the
  `en_US.utf8` collation, even the prefix test `email LIKE 'customer1%'`
  uses a `Seq Scan`; the unique index on `email` serves only equality. A
  leading `%` can never use an ordinary B-tree.
- **Capturing from an unanchored regex.**
  `substring('Customer 12a' FROM 'Customer ([0-9]+)')` returns `12` and
  hides the bad suffix. Anchor with `^` and `$`, which returns `NULL`
  instead.
- See [Recover from common failures](../../STUDY-GUIDE.md#recover-from-common-failures)
  for general recovery steps.

## Self-check

- Is the pattern a substring search or a whole-value validation?
- Could a leading wildcard or function-wrapped column prevent ordinary B-tree
  index use?

## Next step

Continue to [Day 30; Phase 2 project](day30_phase2_project.md).

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

Further reading
- Pattern matching: https://www.postgresql.org/docs/17/functions-matching.html
- pg_trgm: https://www.postgresql.org/docs/17/pgtrgm.html

## Ask an AI tutor about this lesson

A tutor is a good source of tricky test strings, such as emails
with two dots or names with trailing spaces, to check your anchors and
escapes against
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-29: Pattern Matching: LIKE, Regular Expressions, and Full-Text Search.

I have completed the direct catalog prerequisite: `sql-28`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day29_pattern_matching.md
- Answer-free learner SQL: sql/postgres-60day/day29_pattern_matching.sql

Key terms to teach in context: Wildcard, Anchor, Sargable predicate. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Compare `email ~ 'customer1[0-9]{2}'` with the anchored `email ~ '^customer1[0-9]{2}@example[.]com$'`. Add surrounding text to a test value and show why an unanchored validation can accept only a matching substring.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-29/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
