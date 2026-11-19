# web-013: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-013.md`.

## Exercise 1: Identify the missing information in a red-only error dot.

**Expected answer:** The user needs a textual error meaning and a useful recovery action.

**Why:** Color alone fails people with color-vision differences and screen-reader users, so the error needs words and a recovery instruction.

## Exercise 2: Add a focus-visible style without removing focus support.

**Expected evidence:** Keyboard focus is visibly distinguishable from hover.

**Why:** :focus-visible matches when the browser decides a focus indicator is needed, such as keyboard navigation, so keyboard users get a clear ring.

## Exercise 3: Build status cards whose meaning does not depend on color.

**Expected evidence:** Each card contains a clear label, readable text and visible interactive focus.

**Why:** Text carries the meaning, so color only reinforces it and the cards remain understandable in monochrome or forced colors.

## Exercise 4: Diagnose a focus ring clipped by overflow.

**Expected answer:** Inspect the ancestor clipping boundary and provide space or a different visible indicator.

**Why:** An overflow boundary clips anything drawn outside it, including an outline, so the fix is space inside the boundary or an inset indicator.

## Exercise 5: Inspect the page in a forced-colors or high-contrast setting.

**Expected evidence:** Native boundaries and meaningful labels remain available; document actual browser behavior.

**Why:** Forced colors replace author colors with system colors, so information carried only by a background color disappears while borders and text remain.

## Exercise 6: Compute the contrast of #94a3b8 text on #ffffff and explain why one palette check does not qualify every interaction state.

**Expected answer:** About 2.56:1, below the 4.5:1 minimum for normal text, so it fails; hover, focus, disabled and error states change the foreground or background, so each important pair needs its own check.

**Why:** Relative luminance is about 0.36 for #94a3b8 and 1.0 for white, so the ratio is (1.0 + 0.05) / (0.36 + 0.05), about 2.56:1. That fails both the 4.5:1 normal-text and the 3:1 large-text minimums, and because hover, focus, disabled and error states each change a color pair, each pair needs its own measurement.

## Reference comparison

Open `courses/web-development/solutions/web-013_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
