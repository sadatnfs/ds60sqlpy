# web-041: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-041.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Identify the dependency hidden by the interface.

**Expected answer:** The application depends on progress-reading behavior, not a specific database implementation.

**Approach:** Read what the interface method promises, an integer count of completed lessons, and notice it says nothing about tables, files or connections.

**Why:** The service depends only on the ability to count completed lessons, so any implementation of that method can be used.

**Plausible wrong approach:** Naming SQLite as the dependency fails because the service only calls `completedCount()` and would work unchanged with any store that implements it.

**How to verify:** Searching `Summary` for `PDO`, `sqlite` or SQL text finds nothing, while `ProgressStore` appears in its constructor.

## Exercise 2: Supply an in-memory store with a known count.

**Expected evidence:** The service output is deterministic and requires no external connection.

**Approach:** Write `final class MemoryStore implements ProgressStore` that returns a count passed to its constructor, and pass it into `Summary`.

**Why:** An in-memory implementation makes the output deterministic and needs no database.

**Plausible wrong approach:** Using a store that returns `random_int(0, 10)` fails because each run prints a different label and no expected value can be written.

**How to verify:** Passing `new MemoryStore(3)` makes `label()` return 3 complete on every run. Changing the argument to 0 changes the label to 0 complete with no other edits.

## Exercise 3: Build a summary service with an injected repository.

**Expected evidence:** The same service works with two controlled implementations that satisfy the interface.

**Approach:** Define the interface, a `Summary` that receives it through the constructor, and two implementations whose counts differ, then print both labels.

**Why:** Constructor injection lets the same service run against different stores without code changes.

**Plausible wrong approach:** Adding an `if ($store instanceof MemoryStore)` branch inside `Summary` fails because the service then knows about concrete classes again.

**How to verify:** Both implementations produce correct labels through the same `Summary` code, with no type checks inside it.

## Exercise 4: Diagnose a test double that returns impossible domain values.

**Expected answer:** The double should preserve the relevant contract instead of making invalid states look normal.

**Approach:** Check the double's returned values against the real contract, such as a count that can never be negative, and fix the double first.

**Why:** A test double should respect the domain rules; impossible values make tests pass for states that can never occur.

**Plausible wrong approach:** Keeping a double that returns -2 fails because tests then pass for situations the real store can never produce. The suite stays green while production data would have failed.

**How to verify:** The memory store's constructor rejects negative counts, and every test uses values the real store could return.

## Exercise 5: Test zero completed lessons.

**Expected evidence:** The summary handles an empty state without a special external dependency.

**Approach:** Construct `MemoryStore(0)` and check that the label reads 0 complete, without any special branch for the empty case.

**Why:** The service must handle an empty state, and a controlled double makes that case easy to test.

**Plausible wrong approach:** Returning an empty string for zero fails because the reader cannot tell a missing summary from a learner with no completions.

**How to verify:** The label for zero prints 0 complete, and the same code path handles 0 and 5.

## Exercise 6: Explain what remains untested by an in-memory repository.

**Expected answer:** Database queries, schema constraints, transactions and connection behavior require integration tests.

**Approach:** List what the memory store skips: SQL text, schema constraints, transaction behavior and connection failures, each needing a real database test.

**Why:** SQL correctness, constraints, transactions and connection failures need integration tests against the real database.

**Plausible wrong approach:** Claiming the PDO store works because the memory tests pass fails because no SQL statement ran in those tests.

**How to verify:** Your list names at least three behaviors and the integration test that would exercise each one.

## Reference comparison

The reference requires an empty store to give 0 complete and two lesson ids to give 2 complete. That catches a summary that ignores its injected store. It does not exercise a real database or a malformed id, so state which evidence would show the production repository behaves the same.

Open `courses/web-development/solutions/web-041_solution.php` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
