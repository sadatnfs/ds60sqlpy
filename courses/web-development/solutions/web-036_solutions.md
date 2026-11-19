# web-036: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-036.md`.

## Exercise 1: Explain the difference between returning and echoing a value.

**Expected answer:** Returning supplies data to the caller; echo writes output as a side effect.

**Why:** return hands a value back for further computation, while echo only writes output, which callers and tests cannot reuse.

## Exercise 2: Add a value-range guard to a typed function.

**Expected evidence:** The function rejects invalid integers even though they satisfy the declared type.

**Why:** A type declaration accepts every int, so range rules need explicit checks.

## Exercise 3: Build reusable duration calculation and display functions.

**Expected evidence:** Calculations can be tested without capturing output, then formatted at the boundary.

**Why:** Pure functions can be tested by comparing return values, and formatting happens once at the output boundary.

## Exercise 4: Diagnose a result depending on an undocumented global.

**Expected answer:** Pass the dependency explicitly or isolate the stateful boundary.

**Why:** Hidden globals make results depend on outside state; passing values explicitly makes the function predictable.

## Exercise 5: Test zero, a normal value and a negative input.

**Expected evidence:** Each follows the stated contract and the failure is intentional.

**Why:** Zero and a normal value follow the contract, and -1 must raise the declared exception.

## Exercise 6: Explain when a closure improves a transformation.

**Expected answer:** A short callback can express a local operation while keeping its inputs and captured context clear.

**Why:** An arrow function suits a short, local operation and captures outer variables by value automatically.

## Reference comparison

Open `courses/web-development/solutions/web-036_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
