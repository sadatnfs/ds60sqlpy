# Day 12: String Functions and Text Processing (Companion Guide)

## How to run this lesson

Open `./classroom`, pick the PostgreSQL track and lesson **sql-12**, and press **Whole SQL lesson (psql)**. The file opens a transaction on `advanced_sql_training`, sets the search path, and has `psql` print two 50-row result blocks: customers 1 to 50 with a cleaned email and its domain, then products 1 to 50 with a renamed and a ten-character label. It finishes with `ROLLBACK`, and nothing in it writes.

The copy you can edit lives at
`.learning/sql/sql-12/lesson/workspace/sql/postgres-60day/day12_string_functions.sql`.
Change a function argument there (for example the `10` in `substr`) and rerun the whole file to see the effect on every row at once.

If the customers and products tables are missing, so that `lower`, `split_part` and `substr` have nothing to read, the study guide's [notes on preparing the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) cover loading them; the [notebook path for contributors](../../STUDY-GUIDE.md#optional-contributor-notebook-route) is not needed for this lesson.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 11; CASE expressions](day11_case_expressions.md)
- **Artifacts:** [learner SQL](../day12_string_functions.sql) ·
  [solution reasoning](../solutions/day12_solutions.md) ·
  [executable solution](../solutions/day12_solutions.sql)

## A beginner's mental model for this lesson

Every string function in this lesson returns a new value and leaves the column alone. `lower(trim(email))` does not change `customers.email`; it computes a cleaned copy for this one result set. That is why the lesson keeps the raw column beside the cleaned one: when the two differ you can see exactly what changed, and nothing is lost. Turning text into one comparable form like this is **normalization**.

The course fixture is unusually tidy. All 500 customers are named `Customer N`, all 500 emails look like `customerN@example.com` in lower case with no spaces, and all 300 products are named `Product N`. So many of today's cleanups change nothing, and that is useful evidence in itself: a query that reports zero changed rows tells you the data was already clean, as long as you check that zero deliberately.

Two kinds of tool appear. Positional and **delimiter** functions (`split_part`, `substr`, `replace`) work on fixed characters such as `@` or a position count. A **regular expression** describes a pattern, such as "one or more whitespace characters" or "digits at the end", and is used with `~`, `regexp_replace` and `substring(... FROM ...)`. Patterns are more flexible but easier to get subtly wrong, so each exercise pairs them with a check you can count.

## Two worked SQL examples

### Example 1

```sql
SELECT
  customer_id,
  email,
  lower(trim(email)) AS email_clean,
  split_part(email, '@', 2) AS domain
FROM
  customers
ORDER BY
  customer_id
LIMIT 50;
```

**How to read it:** `trim` removes leading and trailing spaces and `lower` folds upper case, so `email_clean` is the comparison form of the address. `split_part(email, '@', 2)` cuts the string at each `@` and returns the second piece, the domain. `ORDER BY customer_id LIMIT 50` shows customers 1 to 50.

**Expected result/shape:** 50 rows, from `customer1@example.com` to `customer50@example.com`. `email_clean` is identical to `email` in every row, and `domain` is `example.com` every time. That holds for the full table too: no email of the 500 changes under `lower(trim(email))`, and there are 500 distinct addresses before and after cleaning. A transformation that changes nothing is still worth running once, because it proves there are no case or spacing duplicates hiding in the column.

### Example 2

```sql
SELECT
  product_id,
  name,
  replace(name, 'Product', 'Item') AS renamed,
  substr(name, 1, 10) AS short_name
FROM
  products
ORDER BY
  product_id
LIMIT 50;
```

**How to read it:** `replace(name, 'Product', 'Item')` swaps every occurrence of the word, and `substr(name, 1, 10)` keeps characters 1 to 10. Both return new text; `name` is still printed unchanged so you can compare.

**Expected result/shape:** 50 rows: `Product 1` becomes `Item 1`, and so on. `short_name` matches `name` in all 50 rows, because the longest name shown, `Product 50`, is exactly ten characters. The cut only bites later in the table: product 100 becomes `Product 10`, which is also product 10's full name. Across all 300 products there are only 99 distinct short names, so a ten-character label could never serve as a key.

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
- **Review loop:** pick two or three rows, work out by hand what each function should return for them, then find those rows in the output; after that, count how many rows the transformation actually changed.

## Exercises

Normalize and parse text with explicit locale/case assumptions, preserving original values when a transformation may be lossy.

Most of these answers can be checked by counting: how many rows changed, how many matched, how many groups formed. Before running each one, write down the count you expect, especially for Exercise 5, whose correct answer on this fixture is surprising.

1. **Query writing:** Return normalized customer names and lowercase emails.
   **Estimate:** the fixture names are all `Customer N`. In how many of the 500 rows will `trimmed_name` differ from `original_name`?
   **Progressive hint:** Use `btrim` for outer whitespace and `lower` for a declared case-normalized display value.
   **Inputs/evidence:** For sql-12 Exercise 1, read `full_name` and `email` from the 500 `customers` rows, wrapping the name in `btrim` and the email in `lower`.
   **Expected result/shape:** For sql-12 Exercise 1, return 500 rows, one per customer, from customer 1 (`Customer 1`, `customer1@example.com`) to customer 500; on the fixture no name has extra spaces and no email has uppercase letters, so the cleaned columns match the originals. The final columns are `customer_id`, `original_name`, `trimmed_name`, and `normalized_email`. The final order is `c.customer_id`.
   **Verify:** For sql-12 Exercise 1, confirm 500 rows and 0 rows where `full_name <> btrim(full_name)` or `email <> lower(email)`. Inside a rolled-back transaction, set customer 1's name to `' Customer 1 '` and email to `Customer1@EXAMPLE.com`; the row must still show `Customer 1` and `customer1@example.com` in the cleaned columns.
2. **Query writing:** Extract the email domain and count customers by domain, preserving missing emails.
   **Estimate:** every address ends in the same domain. How many rows will this print, and will a `(missing)` row appear?
   **Progressive hint:** `split_part` parses the second component; CASE keeps NULL distinct.
   **Inputs/evidence:** For sql-12 Exercise 2, take the part of each `customers.email` after `@` with `split_part`, lower-case it, label a `NULL` email as `(missing)`, and count customers per resulting domain.
   **Expected result/shape:** For sql-12 Exercise 2, return one row, `example.com` with 500 customers, because every fixture email uses that domain and none is `NULL`. The final columns are `email_domain`, and `customer_count`. The final order is `customer_count DESC, email_domain`.
   **Verify:** For sql-12 Exercise 2, confirm the single count equals `SELECT COUNT(*) FROM customers` (500). Inside a rolled-back transaction, set customer 1's email to `Customer1@EXAMPLE.com` and customer 2's email to `NULL`; the result must become two rows, `example.com` 499 and `(missing)` 1, so the uppercase domain still groups with the rest.
3. **Query writing:** Create an ordered comma-separated list of department employee names.
   **Estimate:** the names are sorted as text, not as numbers. Which employee name will come second in the Sales list, `Employee 7` or `Employee 13`?
   **Progressive hint:** Put `ORDER BY` inside `string_agg` so concatenation order is deliberate.
   **Inputs/evidence:** For sql-12 Exercise 3, read from `departments` left-joined to `employees` and list each department's employee names with `string_agg(e.full_name, ', ' ORDER BY e.full_name, e.employee_id)`.
   **Expected result/shape:** For sql-12 Exercise 3, return 6 rows, `Sales` through `Operations`; names are sorted as text, so department 1's list runs `Employee 1, Employee 13, Employee 19, ...` with `Employee 7` after `Employee 67`. The final columns are `department_id`, `department_name`, and `employees`. The final order is `d.department_id`.
   **Verify:** For sql-12 Exercise 3, confirm 6 rows, one per `department_id`, matching `SELECT COUNT(*) FROM departments`; for one department, compare the number of names in `employees` with `SELECT COUNT(*) FROM employees WHERE department_id = <that id>` (17 for departments 1 to 4 and 16 for departments 5 and 6).
4. **Prediction:** Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled.
   **Estimate:** which of the three inputs gets shorter, and by how many characters?
   **Progressive hint:** Use a POSIX whitespace class and the global regex flag.
   **Inputs/evidence:** For sql-12 Exercise 4, normalize three strings in an inline `VALUES` fixture (`Data Tools` with two spaces on each side and three between the words, `E'one\ttwo'`, and `E'line1\nline2'`) with `regexp_replace(source_text, '[[:space:]]+', ' ', 'g')` wrapped in `btrim`.
   **Expected result/shape:** For sql-12 Exercise 4, return 3 rows with `normalized_text` values `Data Tools`, `one two`, and `line1 line2`; the query has no `ORDER BY`. The final columns are `source_text`, and `normalized_text`.
   **Verify:** For sql-12 Exercise 4, confirm 3 rows with no tab, newline, or double space left in `normalized_text`. Change the pattern to `' +'` and the tab row must come back unchanged; drop `btrim` and the first row must keep one space at each end of `Data Tools`.
5. **Debugging:** Safely find customer names containing a literal percent or underscore rather than treating them as wildcards.
   **Estimate:** no customer name contains `%` or `_`. How many rows should the correct query return, and how many would `LIKE '%_%'` without an escape return?
   **Progressive hint:** Escape wildcard characters and declare the escape character.
   **Inputs/evidence:** For sql-12 Exercise 5, search the 500 `customers.full_name` values for a literal `%` or `_` with `LIKE '%\%%' ESCAPE '\'` and `LIKE '%\_%' ESCAPE '\'`.
   **Expected result/shape:** For sql-12 Exercise 5, return 0 rows, because every fixture name has the form `Customer N`. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
   **Verify:** For sql-12 Exercise 5, confirm the unescaped pattern `LIKE '%_%'` matches all 500 names, because `_` alone is a one-character wildcard. Inside a rolled-back transaction, rename customer 3 to `Customer_3`; the escaped query must return exactly that 1 row.
6. **Extension:** Parse the numeric suffix from names like `Customer 42`, returning NULL for nonmatching text.
   **Estimate:** will `parsed_customer_number` ever differ from `customer_id` on this fixture?
   **Progressive hint:** Use a captured regex replacement only after a match predicate establishes the format.
   **Inputs/evidence:** For sql-12 Exercise 6, test each of the 500 `customers.full_name` values against `'^Customer [0-9]+$'` and, only when it matches, cast `substring(full_name FROM '([0-9]+)$')` to `integer`.
   **Expected result/shape:** For sql-12 Exercise 6, return 500 rows, one per customer, where `parsed_customer_number` equals `customer_id`, from 1 to 500. The final columns are `customer_id`, `full_name`, and `parsed_customer_number`. The final order is `c.customer_id`.
   **Verify:** For sql-12 Exercise 6, confirm 500 rows where `parsed_customer_number = customer_id`. Inside a rolled-back transaction, rename customer 3 to `Customer_3` and customer 4 to `Customer 4b`; both rows must stay in the result with a `NULL` `parsed_customer_number` instead of raising a cast error.

## Common mistakes and how to recover

- **Overwriting the raw text:** an `UPDATE customers SET email = lower(trim(email))` destroys the evidence of what the address looked like. Keep the cleaned form in a separate column or a view until you have proved the rule is right.
- **Forgetting that `_` is a wildcard:** in `LIKE`, `_` matches any single character, so `full_name LIKE '%_%'` matches all 500 customers. Write `'%\_%' ESCAPE '\'` to look for a real underscore.
- **Assuming `split_part` returns NULL:** for an address with no `@`, `split_part(email, '@', 2)` returns an empty string, not `NULL`. A malformed address then lands in a group with a blank label rather than in a missing group.
- **Sorting numbers stored in text:** `ORDER BY full_name` puts `Employee 100` right after `Employee 10` and before `Employee 16`. Order by the numeric key when you mean numeric order.
- **Collapsing only spaces:** the pattern `' +'` leaves tabs and newlines alone. `[[:space:]]+` covers all of them.
- **Truncating labels into keys:** `substr(name, 1, 10)` maps 300 product names onto only 99 short names.

When `psql` stops on an error partway through, use the study guide's [failure recovery notes](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Do text transformations define behavior for `NULL` and malformed input?
- Can the normalized output be traced back to the original value?

## Next step

Continue to [Day 13; date, time, and time zones](day13_date_time_functions.md).

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

Further reading
- String functions: https://www.postgresql.org/docs/17/functions-string.html
- Regex: https://www.postgresql.org/docs/17/functions-matching.html
- pg_trgm: https://www.postgresql.org/docs/17/pgtrgm.html

## Ask an AI tutor about this lesson

You can finish this lesson without a tutor. If you use one, a productive request is to have it invent a few messy strings (mixed case, a tab, a stray `%`) and ask you what each function returns before checking in `psql`. The prompt below keeps the answers out of the session; setup is in the study guide's [tutor section](../../STUDY-GUIDE.md#use-an-ai-tutor-optional).

```text
Tutor me through sql-12: String Functions and Text Processing.

I have completed the direct catalog prerequisite: `sql-11`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day12_string_functions.md
- Answer-free learner SQL: sql/postgres-60day/day12_string_functions.sql

Key terms to teach in context: Normalization, Delimiter, Regular expression. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Compare a raw email with `lower(trim(email))`. Use the normalized expression for duplicate grouping, but keep the original column visible so a reviewer can audit what changed. Explain why silently overwriting the raw value would lose evidence.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-12/ working copy. Never point setup, reset, DDL, or DML
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
