# web-036: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-036.md`.

## Exercise 1: Explain the difference between returning and echoing a value.

**Expected answer:** Returning supplies data to the caller; echo writes output as a side effect.

**Approach:** Ask where the value ends up: `return` hands it to the calling expression, while `echo` writes to output and the caller receives nothing.

**Why:** return hands a value back for further computation, while echo only writes output, which callers and tests cannot reuse.

**Plausible wrong approach:** Saying the echoed text can be stored in a variable fails because the function returns null and the text has already been printed.

**How to verify:** `var_dump(label(30))` for the echo version shows the text and then NULL, not the string.

## Exercise 2: Add a value-range guard to a typed function.

**Expected evidence:** The function rejects invalid integers even though they satisfy the declared type.

**Approach:** Keep the `int` parameter type and add `if ($minutes < 0) throw new InvalidArgumentException(...)` before the calculation.

**Why:** A type declaration accepts every int, so range rules need explicit checks.

**Plausible wrong approach:** Relying on the `int` type alone fails because -5 is a valid integer and passes the type check.

**How to verify:** Calling the function with -5 raises the exception, while 0 and 45 return results. The exception message names the rejected value, so the caller can show a precise correction.

## Exercise 3: Build reusable duration calculation and display functions.

**Expected evidence:** Calculations can be tested without capturing output, then formatted at the boundary.

**Approach:** Write `totalMinutes(array $sessions): int` for arithmetic and `formatMinutes(int $minutes): string` for display, and call echo only in the main script.

**Why:** Pure functions can be tested by comparing return values, and formatting happens once at the output boundary.

**Plausible wrong approach:** Putting `echo` inside `totalMinutes` fails because tests then need output capture and cannot simply compare returned integers.

**How to verify:** A test compares `totalMinutes([20, 30])` with 50, and only the final script line prints anything.

## Exercise 4: Diagnose a result depending on an undocumented global.

**Expected answer:** Pass the dependency explicitly or isolate the stateful boundary.

**Approach:** Search the function body for `global` or `$GLOBALS`, then add that dependency as a parameter and pass it from the caller.

**Why:** Hidden globals make results depend on outside state; passing values explicitly makes the function predictable.

**Plausible wrong approach:** Setting the global before every call fails because a forgotten setup step silently changes results in unrelated code.

**How to verify:** The function now gives the same result for the same arguments, whatever global variables exist. Running the function twice with different global values set no longer changes its output.

## Exercise 5: Test zero, a normal value and a negative input.

**Expected evidence:** Each follows the stated contract and the failure is intentional.

**Approach:** Call the function with 0, 45 and -1 in sequence, catching the expected exception only for the negative case.

**Why:** Zero and a normal value follow the contract, and -1 must raise the declared exception.

**Plausible wrong approach:** Testing only 45 fails because the boundary at 0 and the error path are where contracts usually break.

**How to verify:** The outputs are 0, 90 and one InvalidArgumentException message, matching the documented contract.

## Exercise 6: Explain when a closure improves a transformation.

**Expected answer:** A short callback can express a local operation while keeping its inputs and captured context clear.

**Approach:** Use a short arrow function when the operation is local to one `array_map` call and reads naturally inline.

**Why:** An arrow function suits a short, local operation and captures outer variables by value automatically.

**Plausible wrong approach:** Writing a long closure that captures many outer variables fails because its real inputs are hidden and hard to test.

**How to verify:** The arrow function `fn(int $value): int => $value * 2` maps [10, 20] to [20, 40]. The original input array still holds [10, 20] after the call, because `array_map` returns a new array.

## Reference comparison

Open `courses/web-development/solutions/web-036_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
