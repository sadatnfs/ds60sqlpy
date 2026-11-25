# web-018: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-018.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Predict which card inherits a scoped token override.

**Expected answer:** Only the element with the override and its relevant descendants use that scope.

**Approach:** Locate the element where `--surface` is redefined and remember custom properties inherit down the tree from that element only.

**Why:** Custom properties inherit like normal properties, so an override applies to its element and descendants but not to siblings.

**Plausible wrong approach:** Expecting sibling cards to change fails because a scoped override affects the element and its descendants, never its siblings.

**How to verify:** Only the `.featured` card shows #e0f2fe in Computed, while the other cards still resolve `--surface` to white.

## Exercise 2: Replace repeated spacing literals with a semantic token.

**Expected evidence:** A deliberate single token change updates the related spacing.

**Approach:** Search for repeated spacing literals such as `1rem` used for the same purpose and replace them with `var(--space)`.

**Why:** A token defined once changes every use together, which keeps related spacing consistent.

**Plausible wrong approach:** Replacing every `1rem` blindly fails because some values mean font size or border radius and should not change with spacing.

**How to verify:** Changing `--space` to 1.25rem updates all related paddings and gaps while font sizes stay unchanged.

## Exercise 3: Build two themed cards using one component rule.

**Expected evidence:** The variants preserve content labels, contrast and focus while sharing structure.

**Approach:** Write one `.card` rule that reads tokens and a variant class that only overrides tokens, keeping the HTML labels identical.

**Why:** The component rule stays the same while the variant changes values, so structure, labels and focus styles are shared.

**Plausible wrong approach:** Copying the whole `.card` rule for the variant fails because later fixes to one rule are easily forgotten in the other.

**How to verify:** Both cards share one rule in the Styles panel, and each variant passes a contrast check for text and focus.

## Exercise 4: Diagnose a custom property used with an incompatible value.

**Expected answer:** Inspect the final property and computed-value validity, not only the variable's existence.

**Approach:** Inspect the property that consumes the token in Computed and check whether the substituted value is valid for that property.

**Why:** var() is substituted at computed-value time; if the result is invalid for that property, the declaration becomes invalid at computed-value time and falls back to the inherited or initial value.

**Plausible wrong approach:** Checking only that `--space` is defined fails because invalid substitution makes the property unset while the variable looks fine.

**How to verify:** The Computed panel reports the expected padding after you correct the token to a length.

## Exercise 5: Remove an optional variable and inspect its fallback.

**Expected evidence:** The component remains usable with its declared fallback.

**Approach:** Delete the optional token's definition and confirm the fallback in `var(--surface, white)` takes over.

**Why:** The fallback argument in var(--name, value) is used when the property is not defined, so the component stays usable.

**Plausible wrong approach:** Writing `var(--surface)` without a fallback fails because a missing token leaves the property at its inherited or initial value.

**How to verify:** With the token removed, the card background computes to white and the text remains readable.

## Exercise 6: Explain a token name that survives a palette change.

**Expected answer:** A role such as --error-text is more durable than a name tied only to a particular red value.

**Approach:** Name tokens for the role they play, such as `--error-text`, rather than the specific hue currently assigned.

**Why:** A role name such as --error-text still makes sense after the palette changes, while --red-500 becomes misleading.

**Plausible wrong approach:** Naming a token `--red-600` fails because a palette change to a darker orange leaves a misleading name across the code.

**How to verify:** Changing the value of `--error-text` updates every error message without renaming any token.

## Reference comparison

The reference reads the --surface custom property on the featured card and requires #e0f2fe, so it catches a token defined at the wrong scope or with another value. It does not check that the standard card keeps its default, that spacing uses tokens or that colors still contrast, so compare both cards side by side.

Open `courses/web-development/solutions/web-018_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
