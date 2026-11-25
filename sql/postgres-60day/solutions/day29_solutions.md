# Day 29 solutions: Pattern Matching: LIKE/ILIKE, SIMILAR TO, and Regular Expressions


<!-- beginner-solution-enrichment -->
## How to study and run this solution

The answers read `customers` and `events`, and one uses a three-row inline
sample. Nothing is changed. The general approach is in
[Read a solution](../../STUDY-GUIDE.md#read-a-solution).

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day29_solutions.sql
```

## How these answers fit together

The answers move from the simplest pattern language to the richest. The
first and third use `LIKE`/`ILIKE` for a prefix, the fourth escapes `LIKE`
wildcards, and the second, fifth and sixth use anchored regular expressions
to check a whole value or capture part of it. Because this fixture is clean,
the classification and validation branches only show their value when you
try them on bad strings as well. The learner file is
[day29_pattern_matching.sql](../day29_pattern_matching.sql).

## Reading contract

- **Focus:** Choose literal, wildcard, or regular-expression matching from the text grammar and make case, escaping, and anchoring explicit.
- **Assumptions:** PostgreSQL `LIKE` is case-sensitive, `ILIKE` is case-insensitive, and POSIX regex operators use `~`/`~*`. Collation can affect text behavior.
- **Primary pitfall:** Leading wildcards can prevent ordinary b-tree use; unanchored or overly broad regex patterns can match more text than intended.
- **Safety:** all writes are bounded and rollback-protected; read-only
  queries still use deterministic ordering whenever row order is claimed.

## Exercise 1: Query writing

**Prompt:** Find customer names beginning with `Customer 1` case-insensitively.

**Reasoning:** `ILIKE 'Customer 1%'` uses `%` for any suffix.

```sql
SELECT
  c.customer_id,
  c.full_name
FROM
  customers AS c
WHERE
  c.full_name ILIKE 'Customer 1%'
ORDER BY
  c.customer_id;
```

**Expected shape:** Matching customer rows in stable ID order.

### Reasoning and verification

- **Inputs/evidence:** For sql-29 Exercise 1, read the 500 rows of `customers` and keep those whose `full_name` starts with `Customer 1` under the case-insensitive `ILIKE 'Customer 1%'` prefix test.
- **Expected result/shape:** For sql-29 Exercise 1, expected output: exactly 111 rows, IDs 1, 10 through 19, and 100 through 199, because the prefix also matches longer numbers that start with 1. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
- **Independent verification:** For sql-29 Exercise 1, confirm that `WHERE NOT full_name ILIKE 'Customer 1%'` returns the other 389 customers, and that case-sensitive `LIKE 'Customer 1%'` also returns 111 because every seeded name is capitalized the same way; then compare `'customer 1' ILIKE 'Customer 1%'` (true) with `'customer 1' LIKE 'Customer 1%'` (false), and note that `'Customer 21'` does not match.
- **Intermediate relation check:** `customers` has 500 rows named `Customer 1` to `Customer 500`. The filter keeps 111 of them, from customer 1 to customer 199.
- **Clause check:** `ILIKE 'Customer 1%'` is a case-insensitive prefix test, so it matches `Customer 1`, the ten names `Customer 10` to `19` and the hundred names `Customer 100` to `199`. The same pattern with case-sensitive `LIKE 'customer 1%'` returns no rows.
- **Alternative/trade-off:** `c.full_name ~* '^Customer 1'` gives the same 111 rows. `ILIKE` is easier to read for a plain prefix; the regex form helps once you need character classes.
- **Edge case:** If "customer number 1" was intended, the prefix is wrong; `c.full_name = 'Customer 1'` returns a single row. A name with a leading space would not match, because the prefix must start at the first character.

## Exercise 2: Query writing

**Prompt:** Find emails that match the course's simple lowercase example.com pattern.

**Reasoning:** Anchor both ends and escape the literal dot in the POSIX regex.

```sql
SELECT
  c.customer_id,
  c.email
FROM
  customers AS c
WHERE
  c.email ~ '^customer[0-9]+@example[.]com$'
ORDER BY
  c.customer_id;
```

**Expected shape:** Only matching non-null email rows.

### Reasoning and verification

- **Inputs/evidence:** For sql-29 Exercise 2, read `customers` and keep rows whose `email` matches the case-sensitive regular expression `^customer[0-9]+@example[.]com$`, anchored at both ends with the dot written as `[.]`.
- **Expected result/shape:** For sql-29 Exercise 2, expected output: exactly 500 rows, every customer from 1 to 500, since no seeded email is NULL or off-pattern. The final columns are `customer_id`, and `email`. The final order is `c.customer_id`.
- **Independent verification:** For sql-29 Exercise 2, confirm that `WHERE email !~ '^customer[0-9]+@example[.]com$'` returns 0 rows; then test the pattern on literals: `'Customer7@example.com'` fails because `~` is case-sensitive, `'customer7@example.com.au'` fails because of `$`, and `'customer7@exampleXcom'` fails with `[.]` but matches if the dot is left unescaped.
- **Intermediate relation check:** All 500 customers have an email, and all 500 match the pattern, so the result is every customer in id order.
- **Clause check:** `^customer[0-9]+@example[.]com$` requires the literal `customer`, at least one digit, and `@example.com` with a real dot, with nothing before or after. `~` is case-sensitive, so `Customer1@example.com` would fail.
- **Alternative/trade-off:** `c.email LIKE 'customer%@example.com'` is close but accepts `customerX@example.com`, because `%` allows any characters. The regex is stricter where it matters, on the digits.
- **Edge case:** Writing `example.com` without the brackets would also accept `x@examplexcom`. A `NULL` email returns `NULL` from `~`, so the `WHERE` drops it without an explicit test.

## Exercise 3: Query writing

**Prompt:** Return event paths under `/p/` using JSON extraction and an anchored pattern.

**Reasoning:** Extract path text, then anchor the literal prefix.

```sql
SELECT
  e.event_id,
  e.metadata ->> 'path' AS path
FROM
  events AS e
WHERE
  e.metadata ->> 'path' LIKE '/p/%'
ORDER BY
  e.event_id;
```

**Expected shape:** Events whose path begins `/p/`.

### Reasoning and verification

- **Inputs/evidence:** For sql-29 Exercise 3, read the 20000 `events` rows, extract `metadata ->> 'path'` as text, and keep paths that start with `/p/` under `LIKE '/p/%'`.
- **Expected result/shape:** For sql-29 Exercise 3, expected output: exactly 6667 rows, event IDs from 1 to 19997, with only two distinct paths: `/p/1` (3333 rows) and `/p/2` (3334 rows). The final columns are `event_id`, and `path`. The final order is `e.event_id`.
- **Independent verification:** For sql-29 Exercise 3, confirm with `SELECT metadata ->> 'path', COUNT(*) FROM events GROUP BY 1` that the other 13333 rows carry `/`, `/cart`, `/help`, or `/search` and none has a NULL path; then check the prefix rule on literals: `'/p/'` matches, while `'/p'`, `'/P/1'`, and `'/shop/p/1'` do not.
- **Intermediate relation check:** `events` has 20,000 rows and six distinct paths. `/p/1` and `/p/2` together cover 6,667 events, and the first match is event 1.
- **Clause check:** `metadata ->> 'path'` returns text, and `LIKE '/p/%'` keeps paths that start with `/p/`. The other four paths, `/`, `/cart`, `/help` and `/search`, lack the second slash after `p` and drop out.
- **Alternative/trade-off:** `left(e.metadata ->> 'path', 3) = '/p/'` and `e.metadata ->> 'path' ~ '^/p/'` give the same rows. `LIKE` with a fixed prefix is the most readable of the three.
- **Edge case:** `'/p%'` without the second slash would also match a path such as `/promo`. An event without a `path` key gives `NULL`, which `LIKE` treats as not matching.

## Exercise 4: Prediction

**Prompt:** Match literal percent and underscore characters in sample text and contrast them with wildcard behavior.

**Reasoning:** Declare an escape character and prefix each literal wildcard.

```sql
SELECT
  value
FROM (
  VALUES ('100%'),
    ('a_b'),
    ('plain')) AS sample (value)
WHERE
  value LIKE '%\%%' ESCAPE '\'
    OR value LIKE '%\_%' ESCAPE '\'
  ORDER BY
    value;
```

**Expected shape:** Only the two rows containing the requested literal symbols.

### Reasoning and verification

- **Inputs/evidence:** For sql-29 Exercise 4, no table is read: the inline `VALUES` fixture holds `'100%'`, `'a_b'`, and `'plain'`, and the filter uses `LIKE '%\%%' ESCAPE '\'` and `LIKE '%\_%' ESCAPE '\'` so the escaped `%` and `_` are literal characters.
- **Expected result/shape:** For sql-29 Exercise 4, expected output: exactly 2 rows, `100%` and `a_b`; `plain` is filtered out. The final columns are `value`. The final order is `value`.
- **Independent verification:** For sql-29 Exercise 4, confirm 2 rows, then remove the escapes and confirm that `value LIKE '%%%' OR value LIKE '%_%'` returns all 3 rows, because unescaped `%` and `_` are wildcards; adding `'ab'`, `'50 percent'`, and `'a\b'` to the fixture still returns only the original 2 rows.
- **Intermediate relation check:** `sample` has three values: `100%`, `a_b` and `plain`.
- **Clause check:** `ESCAPE '\'` makes `\%` a literal percent sign and `\_` a literal underscore, so `'%\%%'` means "contains `%`" and `'%\_%'` means "contains `_`". The result is `100%` and `a_b`; `plain` has neither character.
- **Alternative/trade-off:** `strpos(value, '%') > 0 OR strpos(value, '_') > 0` avoids wildcards completely. That is often clearer when you search for a fixed character instead of a pattern.
- **Edge case:** Without the backslashes, `LIKE '%%%' OR LIKE '%_%'` returns all three rows, because unescaped `%` and `_` are wildcards. The mistake is silent, so always test with a value that should not match.

## Exercise 5: Debugging

**Prompt:** Extract the captured numeric suffix from a valid customer name without replacing the entire string blindly.

**Reasoning:** First assert the anchored grammar, then use `substring(... FROM regex)`.

```sql
SELECT
  c.customer_id,
  substring(c.full_name FROM '^Customer ([0-9]+)$')::integer AS name_number
FROM
  customers AS c
WHERE
  c.full_name ~ '^Customer [0-9]+$'
ORDER BY
  c.customer_id;
```

**Expected shape:** One row per valid course customer name.

### Reasoning and verification

- **Inputs/evidence:** For sql-29 Exercise 5, read from `customers`, keep only names that match the anchored pattern `^Customer [0-9]+$`, and extract the number with `substring(full_name FROM '^Customer ([0-9]+)$')::integer`.
- **Expected result/shape:** For sql-29 Exercise 5, expected output: exactly 500 rows, one per customer, with `name_number` running from 1 to 500. The final columns are `customer_id`, and `name_number`. The final order is `c.customer_id`.
- **Independent verification:** For sql-29 Exercise 5, confirm 500 rows, because every seeded name matches, and that `name_number` equals `customer_id` on every row; the same `substring` returns NULL for `'Customer 12a'` and 7 for `'Customer 7'`.
- **Intermediate relation check:** All 500 names pass `^Customer [0-9]+$`, so the result has 500 rows.
- **Clause check:** `substring(... FROM '^Customer ([0-9]+)$')` returns only the part inside the parentheses, the digits. Cast to `integer`, they equal `customer_id` on every row, from 1 to 500.
- **Alternative/trade-off:** `regexp_replace(full_name, '[^0-9]', '', 'g')` deletes every non-digit and would turn `Customer 12a` into `12` without complaint. Validating the whole value first keeps bad names out.
- **Edge case:** The `WHERE` matters: without it, a name such as `Customer 12a` gives `NULL` from the anchored `substring`, which the cast keeps as `NULL`. An unanchored pattern would instead return `12` and hide the problem.

## Exercise 6: Extension

**Prompt:** Classify emails as course example, other valid-looking, missing, or malformed using ordered patterns.

**Reasoning:** Handle NULL first, then most specific anchored pattern, then a bounded general pattern.

```sql
SELECT
  c.customer_id,
  c.email,
  CASE WHEN c.email IS NULL THEN
    'missing'
  WHEN c.email ~* '^[a-z0-9._%+-]+@example[.]com$' THEN
    'course_example'
  WHEN c.email ~* '^[a-z0-9._%+-]+@[a-z0-9.-]+[.][a-z]{2,}$' THEN
    'other_valid_looking'
  ELSE
    'malformed'
  END AS email_class
FROM
  customers AS c
ORDER BY
  c.customer_id;
```

**Expected shape:** One row per customer with one classification.

### Reasoning and verification

- **Inputs/evidence:** For sql-29 Exercise 6, read from `customers` and classify each `email` with ordered `CASE` branches: `missing` for NULL, `course_example` for an address at `example.com`, `other_valid_looking` for any other `name@domain.tld`, otherwise `malformed`.
- **Expected result/shape:** For sql-29 Exercise 6, expected output: exactly 500 rows, one per customer, all labeled `course_example` in this seed, so the `missing`, `other_valid_looking`, and `malformed` branches are reached only by the fixture in the check. The final columns are `customer_id`, `email`, and `email_class`. The final order is `c.customer_id`.
- **Independent verification:** For sql-29 Exercise 6, confirm 500 rows, one per customer, all `course_example` on the seed; then run the same `CASE` on `VALUES (NULL), ('ann@example.com'), ('ann@school.org'), ('ann@examplexcom'), ('not-an-email')` and expect `missing`, `course_example`, `other_valid_looking`, `malformed`, and `malformed`.
- **Intermediate relation check:** The result has one row per customer, 500 rows, and every one is classified `course_example`, because every email matches the first pattern.
- **Clause check:** `CASE` stops at the first true branch, so the `NULL` test runs first and the most specific pattern second. `~*` ignores case, so `A.B@Example.COM` would also be `course_example`.
- **Alternative/trade-off:** Tested on inline samples, `x@shop.co.uk` is `other_valid_looking`, while `x@examplexcom` and `no-at-sign` are `malformed`. Running those samples is the quickest way to see the lower branches work.
- **Edge case:** If the general pattern came before the specific one, every `@example.com` address would be labelled `other_valid_looking`. Without the first branch, a `NULL` email would fall through to `malformed`, because `NULL ~* ...` is not true.

## Final self-check

- Which of the three pattern languages must match the whole value?
- Why does `'Customer 1%'` match 111 names?
- What does `[.]` protect against in an email pattern?
- Why must the `NULL` test come first in the email classification?
