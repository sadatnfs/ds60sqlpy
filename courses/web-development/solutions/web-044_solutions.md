# web-044: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-044.md`.

## Exercise 1: Classify a pure-function check and a real database transaction check.

**Expected answer:** The first is unit evidence; the second is integration evidence.

**Why:** A pure function check is unit evidence, while a real transaction exercises the database and is integration evidence.

## Exercise 2: Add an empty-input test with an explicit expected result.

**Expected evidence:** The test records the domain policy rather than guessing from the implementation.

**Why:** Writing the expectation first records the domain policy instead of copying whatever the implementation returns.

## Exercise 3: Create a test table for a bounded study-duration function.

**Expected evidence:** Normal, zero, invalid and boundary cases have independently justified outcomes.

**Why:** A table with independently justified outcomes catches more defects than examples chosen to match the code.

## Exercise 4: Diagnose a test that catches the wrong exception as success.

**Expected answer:** Catch the declared exception narrowly and let unexpected failures remain failures.

**Why:** A broad catch turns any failure into a pass, so the test must catch only the declared exception.

## Exercise 5: Temporarily introduce a known bug in a learner copy.

**Expected evidence:** A meaningful test fails for the intended reason, then passes after the repair.

**Why:** A test is meaningful when it fails for the injected bug and passes again after the fix.

## Exercise 6: Explain why a passing reference is not a bug-free guarantee.

**Expected answer:** It qualifies the tested contract and cases; untested integration and environment behavior remain separate.

**Why:** A passing reference covers only its cases and environment; integration, configuration and other inputs remain unverified.

## Reference comparison

Open `courses/web-development/solutions/web-044_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
