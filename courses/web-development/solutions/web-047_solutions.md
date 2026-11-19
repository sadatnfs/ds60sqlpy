# web-047: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-047.md`.

## Exercise 1: Predict what happens when a caller sends topic[]=HTML.

**Expected answer:** The server can receive an array, so a string-shape check is required.

**Why:** PHP turns topic[]=HTML into an array, so code that assumes a string can crash or misbehave.

## Exercise 2: Add an allowlist for supported topics.

**Expected evidence:** Only explicitly declared topic values are accepted.

**Why:** An allowlist, here a backed enum, rejects every value that was not explicitly declared.

## Exercise 3: Build a validator returning cleaned values and field-specific errors.

**Expected evidence:** Valid data has a complete domain value; invalid data has actionable errors and no partial write.

**Why:** Returning either a complete value or a set of errors prevents partial writes and tells the user what to fix.

## Exercise 4: Diagnose trimming an array-shaped request value.

**Expected answer:** Validate its type before calling a string function.

**Why:** In PHP 8, passing an array to trim throws a TypeError, so the shape check must come first.

## Exercise 5: Test missing fields, arrays, out-of-range minutes and valid data.

**Expected evidence:** Each case returns a deliberate validation result without an uncaught type error.

**Why:** Each case should return a deliberate error or value; none should throw an uncaught TypeError.

## Exercise 6: Explain the limits of POST redirect GET.

**Expected answer:** It helps refresh behavior but does not replace authorization, CSRF checks or duplicate-operation design.

**Why:** It stops a browser refresh from resubmitting a form, but it does not check who sent the request or whether the operation already happened.

## Reference comparison

Open `courses/web-development/solutions/web-047_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
