# web-039: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-039.md`.

## Exercise 1: Trace the statements executed after requirePositive(0).

**Expected answer:** The function throws, the matching catch runs and finally executes.

**Approach:** Follow control flow: the `throw` skips the `return`, PHP finds the matching catch, runs it, and then runs `finally` either way.

**Why:** requirePositive(0) throws before returning, the InvalidArgumentException catch runs, and finally always executes.

**Plausible wrong approach:** Expecting the line after the call inside `try` to run fails because a throw exits the `try` block immediately.

**How to verify:** The output shows the error message followed by Attempt finished, and no result line. Changing the argument to 5 prints the result, skips the catch block and still prints Attempt finished.

## Exercise 2: Add a specific catch around a recoverable validation error.

**Expected evidence:** The caller presents a correction without hiding unrelated failures.

**Approach:** Catch `InvalidArgumentException` only, show its message to the user, and let other exception types continue upward.

**Why:** A narrow catch handles the expected validation error and lets unrelated errors surface.

**Plausible wrong approach:** Catching `Exception` here fails because a database or file error would then be shown as if it were a typing mistake.

**How to verify:** Invalid input prints the correction message, while a forced `RuntimeException` still stops the program.

## Exercise 3: Build a failure-aware parser with explicit success and error paths.

**Expected evidence:** Valid data returns a result; invalid data produces a clear classified failure.

**Approach:** Return either the parsed value or an error result with a message, and print each case on a separate labeled line.

**Why:** Distinct exception types let callers react to each failure and keep successful results clearly separate.

**Plausible wrong approach:** Returning null for every failure fails because the caller cannot tell an empty input from an out of range number.

**How to verify:** Inputs 30, '' and 500 produce a value, an empty input message and a range message respectively. Each failure line names the field and the rule it broke, so the reader can correct the input directly.

## Exercise 4: Diagnose a catch-all that returns zero for every failure.

**Expected answer:** A fabricated normal value hides the difference between valid zero and broken processing.

**Approach:** Replace `catch (Throwable)` with a specific catch and return a failure result instead of a valid looking number.

**Why:** Returning a normal-looking value on failure hides errors and corrupts later results.

**Plausible wrong approach:** Logging the error but still returning 0 fails because totals stay wrong even though a log line exists.

**How to verify:** With the repair, minutesOrZero('abc') no longer prints 0, and '0' still does. A deliberate TypeError inside `parseMinutes` now stops the run with a stack trace instead of becoming 0.

## Exercise 5: Test cleanup after both success and exception.

**Expected evidence:** Owned resources are released in either path.

**Approach:** Open a resource in `try`, release it in `finally`, and run the code once with valid input and once with input that throws.

**Why:** finally runs on both paths, so resources released there are always released.

**Plausible wrong approach:** Putting cleanup after the `try` block fails because an exception skips that line, so the resource stays open.

**How to verify:** A message printed in `finally` appears in both runs, once after the result and once after the error.

## Exercise 6: Explain the difference between learner diagnostics and public production errors.

**Expected answer:** Detailed local diagnostics support learning, while public responses should avoid sensitive internal detail.

**Approach:** Keep full messages and stack traces in local CLI output or server logs, and show public users only a short generic reference.

**Why:** Detailed diagnostics help locally, but public errors should give a safe message without stack traces, paths or secrets.

**Plausible wrong approach:** Printing database credentials or file paths to the public page fails because attackers learn the internal layout.

**How to verify:** The public error text contains no path, query or secret, while the local log entry has the details. Comparing the two messages side by side shows that only the log entry contains the exception class and line number.

## Reference comparison

Open `courses/web-development/solutions/web-039_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
