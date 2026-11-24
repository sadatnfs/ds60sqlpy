# web-045: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-045.md`.

## Exercise 1: Predict the escaped form of a name containing < and &.

**Expected answer:** The special syntax characters become HTML character references.

**Approach:** Apply the helper's mapping character by character: `<` becomes `&lt;`, `&` becomes `&amp;`, and `>` becomes `&gt;`.

**Why:** < becomes &lt; and & becomes &amp;, and with ENT_QUOTES both quote characters are converted as well.

**Plausible wrong approach:** Expecting the name to be removed or blanked fails because escaping keeps the text and only changes how syntax characters are written.

**How to verify:** The CLI output for '<Ada & Bea>' is &lt;Ada &amp; Bea&gt;. The output keeps every letter of the name, so no information is lost.

## Exercise 2: Add an escaping helper with an explicit UTF-8 contract.

**Expected evidence:** The helper names its HTML context and handles quotes as well as angle brackets.

**Approach:** Define `function e(string $text): string` that returns `htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')`.

**Why:** Fixing the flags and encoding in one helper prevents call sites from forgetting them.

**Plausible wrong approach:** Leaving out `ENT_QUOTES` in a helper meant for attributes fails because a single quote could end a single quoted value.

**How to verify:** Calling `e("O'Brien")` returns O&#039;Brien, and calling `e('"')` returns the reference &quot; instead of a raw quote.

## Exercise 3: Render a study-card template from synthetic untrusted labels.

**Expected evidence:** The structure stays fixed while labels are escaped at output.

**Approach:** Keep the card markup as fixed template text, insert each label with `e()`, and quote every attribute value.

**Why:** Escaping at output protects the HTML context no matter where the label came from.

**Plausible wrong approach:** Building the card with labels concatenated raw and escaping the whole HTML string afterward fails because the real tags then display as text.

**How to verify:** A label containing a tag prints as escaped text, while the card's own tags remain unescaped. Viewing the printed string shows quotes around every attribute value in the card.

## Exercise 4: Explain why the same helper is insufficient for a JavaScript string.

**Expected answer:** JavaScript has a different parser and escaping rules; use a dedicated serialization boundary.

**Approach:** Note that JavaScript string syntax uses backslashes and line terminators, and pass data with `json_encode` using the hex flags.

**Why:** JavaScript strings need different escaping, so data for scripts should be serialized with json_encode and safe flags.

**Plausible wrong approach:** Using `e()` inside a script string fails because HTML entities are not decoded there, so O&#039;Brien shows up literally.

**How to verify:** `json_encode($name, JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_HEX_AMP)` produces a quoted string with no raw `<` or quotes.

## Exercise 5: Test quotes, ampersands and an attack-shaped tag string.

**Expected evidence:** The resulting HTML string contains escaped data rather than an additional live element.

**Approach:** Run `e()` on a quote, an ampersand and a tag shaped string, then print the full template and inspect each value.

**Why:** Escaped output contains character references, so the browser shows the text and creates no new element.

**Plausible wrong approach:** Testing only plain words fails because they contain no syntax characters, so a missing escape would go unnoticed.

**How to verify:** Every special character appears as a character reference, and no unescaped `<` from data appears in the output. Removing the `e()` call from one value makes the raw `<` reappear in that spot.

## Exercise 6: Explain why validated text still needs output escaping.

**Expected answer:** A valid name can contain syntax characters that are meaningful in the destination context.

**Approach:** Recognize that a valid name can still contain `&`, `<` or quotes, so the output step must escape for its destination.

**Why:** Validation can allow syntax characters such as & in a company name, so output escaping is still required.

**Plausible wrong approach:** Rejecting names with apostrophes during validation fails because it blocks real people while the template is still unescaped. Validation and escaping answer different questions, so neither replaces the other.

**How to verify:** The name O'Brien passes validation and renders correctly once `e()` escapes it at output.

## Reference comparison

Open `courses/web-development/solutions/web-045_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
