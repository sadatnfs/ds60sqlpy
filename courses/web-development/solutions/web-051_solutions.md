# web-051: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-051.md`.

## Exercise 1: Explain what a prepared value parameter can and cannot replace.

**Expected answer:** It represents data values, not arbitrary table names, column names or SQL keywords.

**Why:** A bound parameter is always a value, so it cannot name a table, a column or an SQL keyword.

## Exercise 2: Insert a title containing an apostrophe.

**Expected evidence:** The stored value round-trips exactly through a bound parameter.

**Why:** The driver sends the value separately from the SQL text, so the apostrophe needs no manual escaping.

## Exercise 3: Build a local PDO note store with prepared insert and lookup.

**Expected evidence:** The expected record is retrieved and SQL-looking text remains data.

**Why:** Prepared statements keep SQL structure fixed while values vary, so SQL-looking text stays data.

## Exercise 4: Diagnose concatenating an untrusted sort key into SQL.

**Expected answer:** Map the choice through an explicit trusted allowlist rather than treating it as a bindable value.

**Why:** Identifiers cannot be bound, so an allowlist that maps user choices to fixed column names is the safe boundary.

## Exercise 5: Test an empty result and an attack-shaped title.

**Expected evidence:** No-match behavior is explicit and the table remains intact after storing the title.

**Why:** fetch returns false for no row, which must be handled, and the attack-shaped title is stored as plain text.

## Exercise 6: Explain which checks must be repeated when moving to PostgreSQL.

**Expected answer:** Driver behavior, schema types, SQL syntax, transactions and concurrency need engine-specific integration evidence.

**Why:** Types, SQL dialect, isolation levels, locking and connection behavior differ, so PostgreSQL needs its own integration tests.

## Reference comparison

Open `courses/web-development/solutions/web-051_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
