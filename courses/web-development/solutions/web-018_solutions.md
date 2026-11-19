# web-018: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-018.md`.

## Exercise 1: Predict which card inherits a scoped token override.

**Expected answer:** Only the element with the override and its relevant descendants use that scope.

**Why:** Custom properties inherit like normal properties, so an override applies to its element and descendants but not to siblings.

## Exercise 2: Replace repeated spacing literals with a semantic token.

**Expected evidence:** A deliberate single token change updates the related spacing.

**Why:** A token defined once changes every use together, which keeps related spacing consistent.

## Exercise 3: Build two themed cards using one component rule.

**Expected evidence:** The variants preserve content labels, contrast and focus while sharing structure.

**Why:** The component rule stays the same while the variant changes values, so structure, labels and focus styles are shared.

## Exercise 4: Diagnose a custom property used with an incompatible value.

**Expected answer:** Inspect the final property and computed-value validity, not only the variable's existence.

**Why:** var() is substituted at computed-value time; if the result is invalid for that property, the declaration becomes invalid at computed-value time and falls back to the inherited or initial value.

## Exercise 5: Remove an optional variable and inspect its fallback.

**Expected evidence:** The component remains usable with its declared fallback.

**Why:** The fallback argument in var(--name, value) is used when the property is not defined, so the component stays usable.

## Exercise 6: Explain a token name that survives a palette change.

**Expected answer:** A role such as --error-text is more durable than a name tied only to a particular red value.

**Why:** A role name such as --error-text still makes sense after the palette changes, while --red-500 becomes misleading.

## Reference comparison

Open `courses/web-development/solutions/web-018_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
