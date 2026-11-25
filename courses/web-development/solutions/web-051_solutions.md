# web-051: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-051.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Explain what a prepared value parameter can and cannot replace.

**Expected answer:** It represents data values, not arbitrary table names, column names or SQL keywords.

**Approach:** Separate the parts of a query into structure, such as table and column names and keywords, and values that the statement compares or stores.

**Why:** A bound parameter is always a value, so it cannot name a table, a column or an SQL keyword.

**Plausible wrong approach:** Writing `ORDER BY :column` and binding a column name fails because the database treats the bound value as a constant, so the sort never changes.

**How to verify:** Binding 'title' to an ORDER BY placeholder sorts every row by the same constant, so titles are not ordered, while a mapped column name sorts them.

## Exercise 2: Insert a title containing an apostrophe.

**Expected evidence:** The stored value round-trips exactly through a bound parameter.

**Approach:** Prepare `INSERT INTO notes (title) VALUES (:title)`, execute it with the apostrophe title, then select it back by id.

**Why:** The driver sends the value separately from the SQL text, so the apostrophe needs no manual escaping.

**Plausible wrong approach:** Doubling the apostrophe by hand before binding fails because the stored title then contains two apostrophes instead of one.

**How to verify:** The fetched title equals the original string Ada's notes exactly, compared with `===`.

## Exercise 3: Build a local PDO note store with prepared insert and lookup.

**Expected evidence:** The expected record is retrieved and SQL-looking text remains data.

**Approach:** Create the schema in a memory database, insert through a prepared statement, and look up by title with a second prepared statement.

**Why:** Prepared statements keep SQL structure fixed while values vary, so SQL-looking text stays data.

**Plausible wrong approach:** Reusing one statement string built with `sprintf` for both values fails because the formatted text is concatenation under another name.

**How to verify:** Storing the title `'; DROP TABLE notes; --` and fetching it returns that exact text, and the table still exists.

## Exercise 4: Diagnose concatenating an untrusted sort key into SQL.

**Expected answer:** Map the choice through an explicit trusted allowlist rather than treating it as a bindable value.

**Approach:** Map the requested sort name through an array of reviewed column names and fall back to id for anything else.

**Why:** Identifiers cannot be bound, so an allowlist that maps user choices to fixed column names is the safe boundary.

**Plausible wrong approach:** Escaping the sort key with `$db->quote()` fails because the result is a quoted string literal, not a column name.

**How to verify:** A request for `title; DELETE FROM notes` sorts by id, and the row count is unchanged.

## Exercise 5: Test an empty result and an attack-shaped title.

**Expected evidence:** No-match behavior is explicit and the table remains intact after storing the title.

**Approach:** Search for a title that does not exist, then store and fetch an attack shaped title, and count rows after each step.

**Why:** fetch returns false for no row, which must be handled, and the attack-shaped title is stored as plain text.

**Plausible wrong approach:** Checking only that no exception occurred fails because an injected condition can return wrong rows without any error.

**How to verify:** The missing title returns an empty array, and the row count rises by exactly one after the insert.

## Exercise 6: Explain which checks must be repeated when moving to PostgreSQL.

**Expected answer:** Driver behavior, schema types, SQL syntax, transactions and concurrency need engine-specific integration evidence.

**Approach:** List engine specific behavior the SQLite run never checked: column types, placeholder emulation, SQL syntax and locking.

**Why:** Types, SQL dialect, isolation levels, locking and connection behavior differ, so PostgreSQL needs its own integration tests.

**Plausible wrong approach:** Assuming the same tests prove PostgreSQL behavior fails because SQLite accepts values in columns of any declared type.

**How to verify:** Your list names a PostgreSQL integration test for each item, run against that engine.

## Reference comparison

The reference inserts and reads back a title through prepared statements, requires the stored value to round trip exactly and requires the table to hold one row. That catches concatenation and accidental extra statements. It does not test the sort allow list or an empty lookup, so add those cases.

Open `courses/web-development/solutions/web-051_solution.php` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
