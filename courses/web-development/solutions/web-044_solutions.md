# web-044: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-044.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Classify a pure-function check and a real database transaction check.

**Expected answer:** The first is unit evidence; the second is integration evidence.

**Approach:** Ask what each check needs: the pure function needs only inputs and outputs, while the transaction check needs a real database and its rules.

**Why:** A pure function check is unit evidence, while a real transaction exercises the database and is integration evidence.

**Plausible wrong approach:** Calling the database check a unit test fails because its result depends on schema, driver and connection behavior outside the function.

**How to verify:** The pure check runs with no database file present, while the transaction check fails if the database is missing.

## Exercise 2: Add an empty-input test with an explicit expected result.

**Expected evidence:** The test records the domain policy rather than guessing from the implementation.

**Approach:** Decide the domain rule for an empty list first, such as a total of 0, then add `check(totalMinutes([]) === 0, ...)`.

**Why:** Writing the expectation first records the domain policy instead of copying whatever the implementation returns.

**Plausible wrong approach:** Running the function and copying whatever it returns into the expected value fails because the test then records current behavior, bugs included.

**How to verify:** The test names 0 because the policy says so, and it fails if the function returns null.

## Exercise 3: Create a test table for a bounded study-duration function.

**Expected evidence:** Normal, zero, invalid and boundary cases have independently justified outcomes.

**Approach:** List normal, zero, boundary and invalid inputs in a table with an expected result each, worked out by hand before running.

**Why:** A table with independently justified outcomes catches more defects than examples chosen to match the code.

**Plausible wrong approach:** Testing only [20, 30] fails because boundaries and invalid input, where bugs cluster, are never exercised.

**How to verify:** The table has at least one row for each category, and every row passes against the reference.

## Exercise 4: Diagnose a test that catches the wrong exception as success.

**Expected answer:** Catch the declared exception narrowly and let unexpected failures remain failures.

**Approach:** Replace `catch (Exception)` with `catch (InvalidArgumentException)` so unrelated exceptions escape and fail the run.

**Why:** A broad catch turns any failure into a pass, so the test must catch only the declared exception.

**Plausible wrong approach:** Adding a message string check inside the broad catch fails because messages change often while the exception type is the real contract.

**How to verify:** Throwing a `RuntimeException` inside the function now fails the run instead of setting `$rejected`.

## Exercise 5: Temporarily introduce a known bug in a learner copy.

**Expected evidence:** A meaningful test fails for the intended reason, then passes after the repair.

**Approach:** Change `>= 0` to `> 0` in a learner copy, run the tests, confirm the zero case fails, then restore the original.

**Why:** A test is meaningful when it fails for the injected bug and passes again after the fix.

**Plausible wrong approach:** Introducing a bug that no test covers and seeing all tests pass fails as evidence, because it only shows a gap.

**How to verify:** The failing test names the zero case, and it passes again once the comparison is restored.

## Exercise 6: Explain why a passing reference is not a bug-free guarantee.

**Expected answer:** It qualifies the tested contract and cases; untested integration and environment behavior remain separate.

**Approach:** Name what the reference run covers, the listed cases in the CLI worker, and what it does not, such as HTTP and storage.

**Why:** A passing reference covers only its cases and environment; integration, configuration and other inputs remain unverified.

**Plausible wrong approach:** Calling the code bug free because the reference passes fails because untested inputs and environments may still break it.

**How to verify:** Your answer lists at least two behaviors the current tests never exercise. Each listed behavior is paired with the kind of test that would cover it.

## Reference comparison

The reference runs three valid values through boundedMinutes, requires -1 and 121 to throw InvalidArgumentException and prints a count. That catches off-by-one bounds and a missing guard. It does not show your empty-input case or a planted bug, so run your own table against a broken copy too.

Open `courses/web-development/solutions/web-044_solution.php` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
