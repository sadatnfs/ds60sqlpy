# Day 12 solutions: String Functions and Text Processing

<!-- beginner-solution-enrichment -->
## How to study and run this solution

Each answer below is followed by the counts it produced on the course fixture. Because the fixture's text is already clean, several answers show that a transformation changed nothing; the notes explain how to prove that rather than assume it. Run the companion file after your attempt:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day12_solutions.sql
```

It runs six read-only queries inside `BEGIN`/`ROLLBACK`. In order you should see 500 rows, 1 row, 6 rows, 3 rows, 0 rows and 500 rows. The prompts match [the learner file](../day12_string_functions.sql) one for one, and the study guide's [solution reading notes](../../STUDY-GUIDE.md#read-a-solution) describe how to compare your version.

## Reading contract

- **Focus:** Normalize and parse text with explicit locale/case assumptions, preserving original values when a transformation may be lossy.
- **Assumptions:** Course emails use one `@`; Unicode/collation behavior can vary. Text ordering is deterministic only with an explicit sort and tie-breaker.
- **Primary pitfall:** Regex is not a complete email or HTML parser; leading-wildcard searches may not use a normal b-tree index.
- **Safety:** six `SELECT` statements and no writes; the surrounding `BEGIN`/`ROLLBACK` matters only if you add an `UPDATE` to experiment with.

## Exercise 1: Query writing

**Prompt:** Return normalized customer names and lowercase emails.

**Reasoning:** Use `btrim` for outer whitespace and `lower` for a declared case-normalized display value.

**Clause-by-clause reading:**

- `c.full_name AS original_name`: the raw value, kept for comparison.
- `btrim(c.full_name) AS trimmed_name`: removes spaces from both ends only; inner spaces stay.
- `lower(c.email) AS normalized_email`: the lower-case comparison form.
- `ORDER BY c.customer_id`: all 500 customers in key order.

```sql
SELECT
  c.customer_id,
  c.full_name AS original_name,
  btrim(c.full_name) AS trimmed_name,
  lower(c.email) AS normalized_email
FROM
  customers AS c
ORDER BY
  c.customer_id;
```

**Expected shape:** One row per customer.

### Reasoning and verification

- **Inputs/evidence:** For sql-12 Exercise 1, read `full_name` and `email` from the 500 `customers` rows, wrapping the name in `btrim` and the email in `lower`.
- **Expected result/shape:** For sql-12 Exercise 1, return 500 rows, one per customer, from customer 1 (`Customer 1`, `customer1@example.com`) to customer 500; on the fixture no name has extra spaces and no email has uppercase letters, so the cleaned columns match the originals. The final columns are `customer_id`, `original_name`, `trimmed_name`, and `normalized_email`. The final order is `c.customer_id`.
- **Independent verification:** For sql-12 Exercise 1, confirm 500 rows and 0 rows where `full_name <> btrim(full_name)` or `email <> lower(email)`. Inside a rolled-back transaction, set customer 1's name to `' Customer 1 '` and email to `Customer1@EXAMPLE.com`; the row must still show `Customer 1` and `customer1@example.com` in the cleaned columns.
- **What prints:** 500 rows, `Customer 1` through `Customer 500`. `trimmed_name` equals `original_name` and `normalized_email` equals the stored email in every row.
- **Counting the changes:** `SELECT COUNT(*) FROM customers WHERE full_name <> btrim(full_name) OR email <> lower(email)` returns 0. That turns "looks the same" into a fact.
- **Why keep both columns:** if a future load adds `'  Ada Lovelace '`, this result shows the before and after side by side, so a reviewer can see what the rule did.
- **What `btrim` leaves:** `btrim('Ada  Lovelace')` keeps the double space in the middle. Collapsing inner whitespace is Exercise 4's job.
- **Case and duplicates:** `COUNT(DISTINCT lower(email))` and `COUNT(DISTINCT email)` are both 500 here. If the first were smaller, two customers would share an address that differs only in capital letters.
- **Length as a second witness:** names run from 10 characters (`Customer 1`) to 12 (`Customer 500`), and `length(btrim(full_name))` gives the same number in every row, so no hidden leading or trailing space exists.
- **Display versus storage:** `trimmed_name` and `normalized_email` exist only in this result set. Selecting customer 1 again afterwards returns the stored values untouched, because a function call in a `SELECT` list never writes back to the table.

## Exercise 2: Query writing

**Prompt:** Extract the email domain and count customers by domain, preserving missing emails.

**Reasoning:** `split_part` parses the second component; CASE keeps NULL distinct.

**Clause-by-clause reading:**

- `CASE WHEN c.email IS NULL THEN '(missing)' ...`: gives absent emails a visible label.
- `ELSE lower(split_part(c.email, '@', 2))`: the part after the `@`, in lower case.
- `GROUP BY email_domain` and `COUNT(*)`: customers per domain.
- `ORDER BY customer_count DESC, email_domain`: biggest domain first, name as tie-breaker.

```sql
SELECT
  CASE WHEN c.email IS NULL THEN
    '(missing)'
  ELSE
    lower(split_part(c.email, '@', 2))
  END AS email_domain,
  COUNT(*) AS customer_count
FROM
  customers AS c
GROUP BY
  email_domain
ORDER BY
  customer_count DESC,
  email_domain;
```

**Expected shape:** One row per domain label.

### Reasoning and verification

- **Inputs/evidence:** For sql-12 Exercise 2, take the part of each `customers.email` after `@` with `split_part`, lower-case it, label a `NULL` email as `(missing)`, and count customers per resulting domain.
- **Expected result/shape:** For sql-12 Exercise 2, return one row, `example.com` with 500 customers, because every fixture email uses that domain and none is `NULL`. The final columns are `email_domain`, and `customer_count`. The final order is `customer_count DESC, email_domain`.
- **Independent verification:** For sql-12 Exercise 2, confirm the single count equals `SELECT COUNT(*) FROM customers` (500). Inside a rolled-back transaction, set customer 1's email to `Customer1@EXAMPLE.com` and customer 2's email to `NULL`; the result must become two rows, `example.com` 499 and `(missing)` 1, so the uppercase domain still groups with the rest.
- **What prints:** one row, `example.com` with 500. No email is `NULL`, so the `(missing)` label never appears.
- **Why the label still matters:** without the `CASE`, a missing email would group under `NULL`, which `psql` prints as a blank cell that is easy to misread as an empty domain.
- **Malformed input:** an address with no `@` returns `''` from `split_part`, not `NULL`, so it would form a group with an empty label. Test it with `SELECT split_part('no-at-sign', '@', 2) = ''`.
- **Count to compare:** the counts must add to 500, the row count of `customers`.
- **Case in domains:** `lower` is applied after the split, so `Example.COM` and `example.com` would fall into one group. Remove it and such addresses would split into two rows.

## Exercise 3: Query writing

**Prompt:** Create an ordered comma-separated list of department employee names.

**Reasoning:** Put `ORDER BY` inside `string_agg` so concatenation order is deliberate.

**Clause-by-clause reading:**

- `departments AS d LEFT JOIN employees AS e`: keeps every department, even one with no staff.
- `string_agg(e.full_name, ', ' ORDER BY e.full_name, e.employee_id)`: joins the names with a comma and space in text order.
- `GROUP BY d.department_id, d.name`: one row per department.
- `ORDER BY d.department_id`: departments 1 to 6.

```sql
SELECT
  d.department_id,
  d.name AS department_name,
  string_agg(e.full_name, ', ' ORDER BY e.full_name, e.employee_id) AS employees
FROM
  departments AS d
  LEFT JOIN employees AS e ON e.department_id = d.department_id
GROUP BY
  d.department_id,
  d.name
ORDER BY
  d.department_id;
```

**Expected shape:** One row per department.

### Reasoning and verification

- **Inputs/evidence:** For sql-12 Exercise 3, read from `departments` left-joined to `employees` and list each department's employee names with `string_agg(e.full_name, ', ' ORDER BY e.full_name, e.employee_id)`.
- **Expected result/shape:** For sql-12 Exercise 3, return 6 rows, `Sales` through `Operations`; names are sorted as text, so department 1's list runs `Employee 1, Employee 13, Employee 19, ...` with `Employee 7` after `Employee 67`. The final columns are `department_id`, `department_name`, and `employees`. The final order is `d.department_id`.
- **Independent verification:** For sql-12 Exercise 3, confirm 6 rows, one per `department_id`, matching `SELECT COUNT(*) FROM departments`; for one department, compare the number of names in `employees` with `SELECT COUNT(*) FROM employees WHERE department_id = <that id>` (17 for departments 1 to 4 and 16 for departments 5 and 6).
- **What prints:** six rows. Sales begins `Employee 1, Employee 13, Employee 19, ...` and Finance begins `Employee 10, Employee 100, Employee 16, ...`.
- **Text order, not number order:** names compare character by character, so `Employee 13` comes before `Employee 7`. For numeric order inside the list, use `ORDER BY e.employee_id`.
- **Counting the names:** departments 1 to 4 list 17 names and departments 5 and 6 list 16, which adds up to the 100 employees.
- **Empty departments:** every department has staff here. If one did not, the `LEFT JOIN` would keep it and `string_agg` would return `NULL` for its list.

## Exercise 4: Prediction

**Prompt:** Normalize repeated internal whitespace in sample text and predict how tabs/newlines are handled.

**Reasoning:** Use a POSIX whitespace class and the global regex flag.

**Clause-by-clause reading:**

- `VALUES (...) AS sample (source_text)`: three test strings typed into the query.
- `regexp_replace(source_text, '[[:space:]]+', ' ', 'g')`: replaces each run of spaces, tabs or newlines with one space; `'g'` means every run, not just the first.
- `btrim(...)`: removes the single space left at either end.

```sql
SELECT
  source_text,
  btrim(regexp_replace(source_text, '[[:space:]]+', ' ', 'g')) AS normalized_text
FROM (
  VALUES ('  Data   Tools  '),
    (E'one\ttwo'),
    (E'line1\nline2')) AS sample (source_text);
```

**Expected shape:** Three input/output rows.

### Reasoning and verification

- **Inputs/evidence:** For sql-12 Exercise 4, normalize three strings in an inline `VALUES` fixture (`Data Tools` with two spaces on each side and three between the words, `E'one\ttwo'`, and `E'line1\nline2'`) with `regexp_replace(source_text, '[[:space:]]+', ' ', 'g')` wrapped in `btrim`.
- **Expected result/shape:** For sql-12 Exercise 4, return 3 rows with `normalized_text` values `Data Tools`, `one two`, and `line1 line2`; the query has no `ORDER BY`. The final columns are `source_text`, and `normalized_text`.
- **Independent verification:** For sql-12 Exercise 4, confirm 3 rows with no tab, newline, or double space left in `normalized_text`. Change the pattern to `' +'` and the tab row must come back unchanged; drop `btrim` and the first row must keep one space at each end of `Data Tools`.
- **What prints:** three rows. `' Data Tools '` (12 characters) becomes `Data Tools` (10). `one`, tab, `two` becomes `one two` and `line1`, newline, `line2` becomes `line1 line2`; both keep their length because one character is swapped for one space.
- **Reading the display:** `psql` expands the tab to spaces and shows the newline as a `+` at the end of the cell followed by a second line. The raw value has not changed; only the display wraps.
- **Without `'g'`:** only the first whitespace run is replaced, so a string with two gaps would keep the second one.
- **The tempting shortcut:** the pattern `' +'` fixes the first row but leaves the tab and newline untouched.

## Exercise 5: Debugging

**Prompt:** Safely find customer names containing a literal percent or underscore rather than treating them as wildcards.

**Reasoning:** Escape wildcard characters and declare the escape character.

**Clause-by-clause reading:**

- `c.full_name LIKE '%\%%' ESCAPE '\'`: a real percent sign anywhere in the name.
- `OR c.full_name LIKE '%\_%' ESCAPE '\'`: a real underscore anywhere in the name.
- `ORDER BY c.customer_id`: matches in key order.

```sql
SELECT
  c.customer_id,
  c.full_name
FROM
  customers AS c
WHERE
  c.full_name LIKE '%\%%' ESCAPE '\'
  OR c.full_name LIKE '%\_%' ESCAPE '\'
ORDER BY
  c.customer_id;
```

**Expected shape:** Rows only when the literal character occurs.

### Reasoning and verification

- **Inputs/evidence:** For sql-12 Exercise 5, search the 500 `customers.full_name` values for a literal `%` or `_` with `LIKE '%\%%' ESCAPE '\'` and `LIKE '%\_%' ESCAPE '\'`.
- **Expected result/shape:** For sql-12 Exercise 5, return 0 rows, because every fixture name has the form `Customer N`. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
- **Independent verification:** For sql-12 Exercise 5, confirm the unescaped pattern `LIKE '%_%'` matches all 500 names, because `_` alone is a one-character wildcard. Inside a rolled-back transaction, rename customer 3 to `Customer_3`; the escaped query must return exactly that 1 row.
- **What prints:** zero rows. Every name is `Customer N`, so neither character occurs, and an empty result is the correct answer.
- **Seeing the bug:** remove the escape and write `LIKE '%_%'`. That returns all 500 customers, because `_` matches any one character and every name has at least one.
- **Proving the zero is real:** add a test row inside the transaction, such as a customer named `Ann_Lee`, and rerun. Exactly that row should come back.
- **Index note:** a pattern that starts with `%` cannot use a normal b-tree index, so on a large table this query reads every row.

## Exercise 6: Extension

**Prompt:** Parse the numeric suffix from names like `Customer 42`, returning NULL for nonmatching text.

**Reasoning:** Use a captured regex replacement only after a match predicate establishes the format.

**Clause-by-clause reading:**

- `c.full_name ~ '^Customer [0-9]+$'`: checks the whole name has the expected shape.
- `substring(c.full_name FROM '([0-9]+)$')`: returns the digits captured at the end.
- `::integer`: turns the captured text into a number.
- `ELSE NULL`: names in any other shape get no number.

```sql
SELECT
  c.customer_id,
  c.full_name,
  CASE WHEN c.full_name ~ '^Customer [0-9]+$' THEN
    substring(c.full_name FROM '([0-9]+)$')::integer
  ELSE
    NULL
  END AS parsed_customer_number
FROM
  customers AS c
ORDER BY
  c.customer_id;
```

**Expected shape:** One row per customer with a numeric suffix.

### Reasoning and verification

- **Inputs/evidence:** For sql-12 Exercise 6, test each of the 500 `customers.full_name` values against `'^Customer [0-9]+$'` and, only when it matches, cast `substring(full_name FROM '([0-9]+)$')` to `integer`.
- **Expected result/shape:** For sql-12 Exercise 6, return 500 rows, one per customer, where `parsed_customer_number` equals `customer_id`, from 1 to 500. The final columns are `customer_id`, `full_name`, and `parsed_customer_number`. The final order is `c.customer_id`.
- **Independent verification:** For sql-12 Exercise 6, confirm 500 rows where `parsed_customer_number = customer_id`. Inside a rolled-back transaction, rename customer 3 to `Customer_3` and customer 4 to `Customer 4b`; both rows must stay in the result with a `NULL` `parsed_customer_number` instead of raising a cast error.
- **What prints:** 500 rows, and every one matches the pattern. `parsed_customer_number` equals `customer_id` in all 500, which you can confirm with `COUNT(*) FILTER (WHERE parsed_customer_number = customer_id)`.
- **Why the guard:** without the `CASE`, a name like `Order 42` would also yield 42, because the capture only looks at the trailing digits. The full-shape check stops that.
- **Edge case:** a name such as `Customer 99999999999` passes the pattern but fails the cast with `value "99999999999" is out of range for type integer`. Cast to `bigint` or limit the digit count if such names are possible.
- **`NULL` names:** `NULL ~ pattern` is `NULL`, so the `CASE` falls to `ELSE NULL` and the row is kept with no number.

## Final self-check

- Why does Example 2 show the same text in `name` and `short_name`, and where in the table does that stop being true?
- What does `split_part` return for an address with no `@`?
- Why does `Employee 13` come before `Employee 7` in Exercise 3?
- Why is zero rows the right answer to Exercise 5, and how would you prove it?
- What stops Exercise 6 from parsing a number out of a name with the wrong shape?
