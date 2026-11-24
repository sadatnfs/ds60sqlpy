# web-037: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-037.md`.

## Exercise 1: Predict the UTF-8 byte length of é.

**Expected answer:** It occupies two bytes in the supplied source encoding.

**Approach:** Recall that é is encoded in UTF-8 as two bytes, so `strlen`, which counts bytes, returns 2 for that one visible character.

**Why:** é is U+00E9, which UTF-8 stores as two bytes, so strlen returns 2.

**Plausible wrong approach:** Answering 1 fails because `strlen` does not count characters, and using that number for limits truncates the text wrongly.

**How to verify:** `strlen('é')` prints 2 while `mb_strlen('é', 'UTF-8')` prints 1.

## Exercise 2: Encode a Unicode label as JSON with explicit error handling.

**Expected evidence:** The output is valid JSON or a visible encoding exception.

**Approach:** Call `json_encode` with `JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE` inside a `try` and catch `JsonException` to report a failure.

**Why:** Without the flag json_encode returns false on invalid UTF-8; with it, the failure is visible.

**Plausible wrong approach:** Checking only for a false return without the flag fails because callers often concatenate false and print an empty string.

**How to verify:** The output shows {"label":"café"} with readable é, and invalid input prints the caught exception.

## Exercise 3: Build a text inspection report that labels bytes honestly.

**Expected evidence:** The program does not present strlen as a count of user-perceived characters.

**Approach:** Print byte length with `strlen`, code point length with `mb_strlen`, and label each number with its unit in the report.

**Why:** Labeling each count prevents a byte count from being presented as characters.

**Plausible wrong approach:** Labeling the `strlen` result as characters fails because accented or emoji labels then report inflated counts.

**How to verify:** For 'café' the report shows 5 bytes and 4 code points on separate labeled lines.

## Exercise 4: Diagnose a truncated string that splits a multibyte sequence.

**Expected answer:** Byte slicing can create invalid UTF-8; use a suitable text-aware operation for the intended unit.

**Approach:** Replace `substr` with `mb_substr` for character limits, or with `mb_strcut` when the limit is a byte budget.

**Why:** substr can split a multibyte sequence and produce invalid UTF-8, while mb_strcut moves the cut back to a character boundary.

**Plausible wrong approach:** Trimming the broken byte with `rtrim` fails because it removes whitespace characters, not partial multibyte sequences.

**How to verify:** The truncated label encodes as JSON without an exception and displays complete characters. `mb_check_encoding($short, 'UTF-8')` returns true for the repaired value and false for the byte slice.

## Exercise 5: Compare a plain ASCII label and a Unicode label.

**Expected answer:** The byte counts differ from intuitive character counts when multibyte data appears.

**Approach:** Print `strlen` and `mb_strlen` for 'cafe' and 'café' side by side and compare both rows.

**Why:** ASCII characters use one byte each, so the counts match; café differs because é uses two bytes.

**Plausible wrong approach:** Testing only ASCII labels fails because byte and character counts agree there and hide the multibyte problem.

**How to verify:** The ASCII row shows 4 and 4, while the accented row shows 5 and 4. Adding an emoji label shows an even larger gap, with 4 bytes for that single code point.

## Exercise 6: Explain validation, normalization and output escaping separately.

**Expected answer:** Validation checks a contract, normalization chooses an equivalent representation, and escaping protects a destination context.

**Approach:** Assign each step its own purpose: validate that input meets the contract, normalize to one representation, and escape at output for its destination.

**Why:** Validation asks whether the value is allowed, normalization chooses one representation of equivalent text, and escaping makes the value safe for a specific output context.

**Plausible wrong approach:** Running `htmlspecialchars` on input before storing it fails because the stored text is then wrong for JSON, SQL and plain text.

**How to verify:** Your answer names one concrete function or check for each of the three steps and the stage where it runs.

## Reference comparison

Open `courses/web-development/solutions/web-037_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
