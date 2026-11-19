# web-041: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-041.md`.

## Exercise 1: Identify the dependency hidden by the interface.

**Expected answer:** The application depends on progress-reading behavior, not a specific database implementation.

**Why:** The service depends only on the ability to count completed lessons, so any implementation of that method can be used.

## Exercise 2: Supply an in-memory store with a known count.

**Expected evidence:** The service output is deterministic and requires no external connection.

**Why:** An in-memory implementation makes the output deterministic and needs no database.

## Exercise 3: Build a summary service with an injected repository.

**Expected evidence:** The same service works with two controlled implementations that satisfy the interface.

**Why:** Constructor injection lets the same service run against different stores without code changes.

## Exercise 4: Diagnose a test double that returns impossible domain values.

**Expected answer:** The double should preserve the relevant contract instead of making invalid states look normal.

**Why:** A test double should respect the domain rules; impossible values make tests pass for states that can never occur.

## Exercise 5: Test zero completed lessons.

**Expected evidence:** The summary handles an empty state without a special external dependency.

**Why:** The service must handle an empty state, and a controlled double makes that case easy to test.

## Exercise 6: Explain what remains untested by an in-memory repository.

**Expected answer:** Database queries, schema constraints, transactions and connection behavior require integration tests.

**Why:** SQL correctness, constraints, transactions and connection failures need integration tests against the real database.

## Reference comparison

Open `courses/web-development/solutions/web-041_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
