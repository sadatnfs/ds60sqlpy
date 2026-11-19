# web-037: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-037.md`.

## Exercise 1: Predict the UTF-8 byte length of é.

**Expected answer:** It occupies two bytes in the supplied source encoding.

**Why:** é is U+00E9, which UTF-8 stores as two bytes, so strlen returns 2.

## Exercise 2: Encode a Unicode label as JSON with explicit error handling.

**Expected evidence:** The output is valid JSON or a visible encoding exception.

**Why:** Without the flag json_encode returns false on invalid UTF-8; with it, the failure is visible.

## Exercise 3: Build a text inspection report that labels bytes honestly.

**Expected evidence:** The program does not present strlen as a count of user-perceived characters.

**Why:** Labeling each count prevents a byte count from being presented as characters.

## Exercise 4: Diagnose a truncated string that splits a multibyte sequence.

**Expected answer:** Byte slicing can create invalid UTF-8; use a suitable text-aware operation for the intended unit.

**Why:** substr can split a multibyte sequence and produce invalid UTF-8, while mb_strcut moves the cut back to a character boundary.

## Exercise 5: Compare a plain ASCII label and a Unicode label.

**Expected answer:** The byte counts differ from intuitive character counts when multibyte data appears.

**Why:** ASCII characters use one byte each, so the counts match; café differs because é uses two bytes.

## Exercise 6: Explain validation, normalization and output escaping separately.

**Expected answer:** Validation checks a contract, normalization chooses an equivalent representation, and escaping protects a destination context.

**Why:** Validation asks whether the value is allowed, normalization chooses one representation of equivalent text, and escaping makes the value safe for a specific output context.

## Reference comparison

Open `courses/web-development/solutions/web-037_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
