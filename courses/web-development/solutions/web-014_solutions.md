# web-014: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-014.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Predict whether relative positioning frees the original space.

**Expected answer:** It does not; the original layout space remains.

**Approach:** Recall that `position: relative` offsets the painted box but leaves its original slot in normal flow untouched.

**Why:** position: relative offsets the painted box but keeps its original space in normal flow, so neighboring content does not move.

**Plausible wrong approach:** Expecting following siblings to slide up into the gap fails because only `absolute` or `fixed` removes an element from flow.

**How to verify:** Apply `top: 2rem` to the first paragraph; the second paragraph stays put and a gap appears above it.

## Exercise 2: Turn a group of inline links into a block navigation list.

**Expected evidence:** Display changes the arrangement without changing navigation semantics.

**Approach:** Set the `ul` to `display: flex` or the links to `display: block` and keep the list and anchor elements unchanged.

**Why:** display changes only the layout; a list of links inside nav keeps its navigation semantics.

**Plausible wrong approach:** Replacing the list with `div` elements for easier styling fails because the navigation loses its list item count for assistive technology.

**How to verify:** The links render in the new arrangement and the accessibility tree still shows a list with the same items.

## Exercise 3: Build a card with an intentional positioned badge and flowing content.

**Expected evidence:** Long body text expands the card while the badge stays in its reserved corner.

**Approach:** Make the card `position: relative`, place the badge absolutely in a corner, and add padding so body text never runs under the badge.

**Why:** The relatively positioned card becomes the containing block for the absolute badge, and the reserved padding keeps text from flowing under it.

**Plausible wrong approach:** Positioning the body text absolutely as well fails because the card then has no in-flow content and collapses to its padding height.

**How to verify:** Add three more sentences; the card grows taller and the badge stays in its corner without covering text.

## Exercise 4: Diagnose an absolute label overlapping enlarged text.

**Expected answer:** Provide sufficient reserved space or return the label to normal flow.

**Approach:** Measure the badge's size at enlarged text and reserve at least that much padding on the side where it sits.

**Why:** An absolutely positioned element leaves normal flow, so it cannot push text away; reserve space or return the label to the flow.

**Plausible wrong approach:** Shrinking the label's font to make it fit fails because the overlap returns at higher zoom and the label becomes hard to read.

**How to verify:** At 200 percent zoom, the badge and the first line of text do not overlap in the inspector.

## Exercise 5: Add a long paragraph and narrow the preview.

**Expected evidence:** Content remains readable and the badge does not obscure it.

**Approach:** Paste a long paragraph and switch to the narrow preset, reading the card from top to bottom.

**Why:** Normal flow rewraps text as the width shrinks, while a positioned element stays put, so overlap appears at narrow widths.

**Plausible wrong approach:** Testing only the short sample text fails because the badge collision appears when the first line wraps under it.

**How to verify:** At the narrow preset every line of the long paragraph is fully visible beside or below the badge.

## Exercise 6: Explain the containing block used by an absolute element.

**Expected answer:** Identify the actual ancestor that establishes it, rather than assuming it is always the viewport.

**Approach:** Walk up from the absolute element to the nearest ancestor whose `position` is not `static`, or that has a transform, and use its padding box.

**Why:** An absolutely positioned element is placed against its nearest positioned ancestor, or against the initial containing block when there is none.

**Plausible wrong approach:** Assuming the viewport is always the reference fails as soon as any ancestor has `position: relative` or a transform.

**How to verify:** Toggling `position: relative` on the card in developer tools moves the badge between the card corner and the page corner.

## Reference comparison

The reference reads the card's computed position and requires relative, which catches a badge with no containing block on the card. It does not measure where the badge lands, test a long paragraph or check that the badge leaves the text readable, so narrow the preview and enlarge the text to compare.

Open `courses/web-development/solutions/web-014_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
