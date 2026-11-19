# web-045: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-045.md`.

## Exercise 1: Predict the escaped form of a name containing < and &.

**Expected answer:** The special syntax characters become HTML character references.

**Why:** < becomes &lt; and & becomes &amp;, and with ENT_QUOTES both quote characters are converted as well.

## Exercise 2: Add an escaping helper with an explicit UTF-8 contract.

**Expected evidence:** The helper names its HTML context and handles quotes as well as angle brackets.

**Why:** Fixing the flags and encoding in one helper prevents call sites from forgetting them.

## Exercise 3: Render a study-card template from synthetic untrusted labels.

**Expected evidence:** The structure stays fixed while labels are escaped at output.

**Why:** Escaping at output protects the HTML context no matter where the label came from.

## Exercise 4: Explain why the same helper is insufficient for a JavaScript string.

**Expected answer:** JavaScript has a different parser and escaping rules; use a dedicated serialization boundary.

**Why:** JavaScript strings need different escaping, so data for scripts should be serialized with json_encode and safe flags.

## Exercise 5: Test quotes, ampersands and an attack-shaped tag string.

**Expected evidence:** The resulting HTML string contains escaped data rather than an additional live element.

**Why:** Escaped output contains character references, so the browser shows the text and creates no new element.

## Exercise 6: Explain why validated text still needs output escaping.

**Expected answer:** A valid name can contain syntax characters that are meaningful in the destination context.

**Why:** Validation can allow syntax characters such as & in a company name, so output escaping is still required.

## Reference comparison

Open `courses/web-development/solutions/web-045_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
