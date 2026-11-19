# web-039: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-039.md`.

## Exercise 1: Trace the statements executed after requirePositive(0).

**Expected answer:** The function throws, the matching catch runs and finally executes.

**Why:** requirePositive(0) throws before returning, the InvalidArgumentException catch runs, and finally always executes.

## Exercise 2: Add a specific catch around a recoverable validation error.

**Expected evidence:** The caller presents a correction without hiding unrelated failures.

**Why:** A narrow catch handles the expected validation error and lets unrelated errors surface.

## Exercise 3: Build a failure-aware parser with explicit success and error paths.

**Expected evidence:** Valid data returns a result; invalid data produces a clear classified failure.

**Why:** Distinct exception types let callers react to each failure and keep successful results clearly separate.

## Exercise 4: Diagnose a catch-all that returns zero for every failure.

**Expected answer:** A fabricated normal value hides the difference between valid zero and broken processing.

**Why:** Returning a normal-looking value on failure hides errors and corrupts later results.

## Exercise 5: Test cleanup after both success and exception.

**Expected evidence:** Owned resources are released in either path.

**Why:** finally runs on both paths, so resources released there are always released.

## Exercise 6: Explain the difference between learner diagnostics and public production errors.

**Expected answer:** Detailed local diagnostics support learning, while public responses should avoid sensitive internal detail.

**Why:** Detailed diagnostics help locally, but public errors should give a safe message without stack traces, paths or secrets.

## Reference comparison

Open `courses/web-development/solutions/web-039_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
