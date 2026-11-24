# web-013: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-013.md`.

## Exercise 1: Identify the missing information in a red-only error dot.

**Expected answer:** The user needs a textual error meaning and a useful recovery action.

**Approach:** List what a reader needs from an error: what went wrong and what to do next, then check which of these the red dot conveys.

**Why:** Color alone fails people with color-vision differences and screen-reader users, so the error needs words and a recovery instruction.

**Plausible wrong approach:** Making the dot bigger or a brighter red fails because readers with color vision differences or a screen reader still get no words.

**How to verify:** The repaired status contains visible text such as Needs attention plus a recovery step, readable in grayscale.

## Exercise 2: Add a focus-visible style without removing focus support.

**Expected evidence:** Keyboard focus is visibly distinguishable from hover.

**Approach:** Add a `:focus-visible` outline with an offset and a color distinct from the hover style, without any `outline: none` rule.

**Why:** :focus-visible matches when the browser decides a focus indicator is needed, such as keyboard navigation, so keyboard users get a clear ring.

**Plausible wrong approach:** Styling focus identically to hover fails because a user cannot tell whether the highlighted control is focused or just under the pointer.

**How to verify:** Tab to a button and see the outline; hover another button and see a different, weaker change.

## Exercise 3: Build status cards whose meaning does not depend on color.

**Expected evidence:** Each card contains a clear label, readable text and visible interactive focus.

**Approach:** Give each card a text label like Ready or Needs attention, use color only as reinforcement, and keep interactive elements focusable with a visible ring.

**Why:** Text carries the meaning, so color only reinforces it and the cards remain understandable in monochrome or forced colors.

**Plausible wrong approach:** Encoding status in a colored left border alone fails because the meaning disappears in grayscale and is never announced.

**How to verify:** Switch the preview to grayscale with a filter in developer tools; every card's status is still readable as words.

## Exercise 4: Diagnose a focus ring clipped by overflow.

**Expected answer:** Inspect the ancestor clipping boundary and provide space or a different visible indicator.

**Approach:** Inspect ancestors of the focused control for `overflow: hidden` and either add padding inside the container or use an inset outline.

**Why:** An overflow boundary clips anything drawn outside it, including an outline, so the fix is space inside the boundary or an inset indicator.

**Plausible wrong approach:** Increasing `z-index` on the button fails because overflow clipping is applied by the ancestor regardless of stacking order.

**How to verify:** Tab to the button near the container's edge; the full outline is visible on all four sides.

## Exercise 5: Inspect the page in a forced-colors or high-contrast setting.

**Expected evidence:** Native boundaries and meaningful labels remain available; document actual browser behavior.

**Approach:** Turn on forced colors through the operating system or developer tools emulation, then tab through and read each status card.

**Why:** Forced colors replace author colors with system colors, so information carried only by a background color disappears while borders and text remain.

**Plausible wrong approach:** Relying on `background-color` for state fails because forced colors replace author colors, so a background-only state disappears.

**How to verify:** In forced colors the labels remain, focus rings are visible, and you write down what the browser actually showed.

## Exercise 6: Compute the contrast of #94a3b8 text on #ffffff and explain why one palette check does not qualify every interaction state.

**Expected answer:** About 2.56:1, below the 4.5:1 minimum for normal text, so it fails; hover, focus, disabled and error states change the foreground or background, so each important pair needs its own check.

**Approach:** Convert both colors to relative luminance, apply (L1 + 0.05) / (L2 + 0.05), then repeat for hover, focus, disabled and error pairs.

**Why:** Relative luminance is about 0.36 for #94a3b8 and 1.0 for white, so the ratio is (1.0 + 0.05) / (0.36 + 0.05), about 2.56:1. That fails both the 4.5:1 normal-text and the 3:1 large-text minimums, and because hover, focus, disabled and error states each change a color pair, each pair needs its own measurement.

**Plausible wrong approach:** Checking only the default text color fails because a hover background or error tint can push a different pair below 4.5:1.

**How to verify:** A contrast checker reports about 2.56:1 for #94a3b8 on #ffffff, and your table lists a ratio for each state pair.

## Reference comparison

Open `courses/web-development/solutions/web-013_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
