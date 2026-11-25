# web-047: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-047.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Predict what happens when a caller sends topic[]=HTML.

**Expected answer:** The server can receive an array, so a string-shape check is required.

**Approach:** Recall that PHP turns `name[]=value` into an array element, so `$input['topic']` holds an array instead of a string.

**Why:** PHP turns topic[]=HTML into an array, so code that assumes a string can crash or misbehave.

**Plausible wrong approach:** Expecting the string HTML fails because the bracket syntax in the field name changes the parsed type.

**How to verify:** Dumping the synthetic input shows `topic` as an array containing one string. Sending `topic=HTML` without brackets shows a plain string in the same dump.

## Exercise 2: Add an allowlist for supported topics.

**Expected evidence:** Only explicitly declared topic values are accepted.

**Approach:** Map the raw string through `Topic::tryFrom` from the backed enum and record an error when it returns null.

**Why:** An allowlist, here a backed enum, rejects every value that was not explicitly declared.

**Plausible wrong approach:** Using `in_array($raw, $topics)` without the strict flag fails because loose comparison can accept unexpected values.

**How to verify:** Topic::tryFrom('HTML') returns the enum case, while 'Rust' produces the Choose a topic error.

## Exercise 3: Build a validator returning cleaned values and field-specific errors.

**Expected evidence:** Valid data has a complete domain value; invalid data has actionable errors and no partial write.

**Approach:** Return `['value' => ..., 'errors' => [...]]`, filling value only when every field passes and keeping one message per field.

**Why:** Returning either a complete value or a set of errors prevents partial writes and tells the user what to fix.

**Plausible wrong approach:** Returning a half filled value with some errors fails because a caller might store the valid fields and lose the rest.

**How to verify:** Invalid input returns an empty value and two keyed errors, and valid input returns a complete value and no errors. The caller can redisplay the submitted text next to each message without losing it.

## Exercise 4: Diagnose trimming an array-shaped request value.

**Expected answer:** Validate its type before calling a string function.

**Approach:** Move the `is_string` check before `trim` and return a field error when the value has any other type.

**Why:** In PHP 8, passing an array to trim throws a TypeError, so the shape check must come first.

**Plausible wrong approach:** Casting with `(string)` before trimming fails because converting an array to string produces Array and a warning.

**How to verify:** The array shaped input now returns Choose a topic. as an error, and no TypeError reaches the caller.

## Exercise 5: Test missing fields, arrays, out-of-range minutes and valid data.

**Expected evidence:** Each case returns a deliberate validation result without an uncaught type error.

**Approach:** Run four synthetic inputs: no fields, array fields, minutes of 500 and a valid record, and print each result.

**Why:** Each case should return a deliberate error or value; none should throw an uncaught TypeError.

**Plausible wrong approach:** Testing only the valid record fails because the uncaught type errors appear only with unusual shapes.

**How to verify:** Each of the four inputs returns a result array, and only the valid record has an empty errors map. Minutes of 500 produce a range message rather than a syntax message.

## Exercise 6: Explain the limits of POST redirect GET.

**Expected answer:** It helps refresh behavior but does not replace authorization, CSRF checks or duplicate-operation design.

**Approach:** Describe what the redirect does, turning a refresh into a GET, and list protections it leaves to other code.

**Why:** It stops a browser refresh from resubmitting a form, but it does not check who sent the request or whether the operation already happened.

**Plausible wrong approach:** Treating the redirect as a defense against forged submissions fails because the original POST is still processed first.

**How to verify:** Your answer names authorization, a CSRF token check and an idempotency key as separate measures.

## Reference comparison

The reference requires a valid plan to give integer minutes 30 and requires array input, missing input and the lowercase topic html to be rejected. That catches shape errors and a case-insensitive allow list. It does not test field-specific error text or redisplay, so read the printed 121 minute result.

Open `courses/web-development/solutions/web-047_solution.php` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
