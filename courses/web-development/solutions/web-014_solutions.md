# web-014: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-014.md`.

## Exercise 1: Predict whether relative positioning frees the original space.

**Expected answer:** It does not; the original layout space remains.

**Why:** position: relative offsets the painted box but keeps its original space in normal flow, so neighboring content does not move.

## Exercise 2: Turn a group of inline links into a block navigation list.

**Expected evidence:** Display changes the arrangement without changing navigation semantics.

**Why:** display changes only the layout; a list of links inside nav keeps its navigation semantics.

## Exercise 3: Build a card with an intentional positioned badge and flowing content.

**Expected evidence:** Long body text expands the card while the badge stays in its reserved corner.

**Why:** The relatively positioned card becomes the containing block for the absolute badge, and the reserved padding keeps text from flowing under it.

## Exercise 4: Diagnose an absolute label overlapping enlarged text.

**Expected answer:** Provide sufficient reserved space or return the label to normal flow.

**Why:** An absolutely positioned element leaves normal flow, so it cannot push text away; reserve space or return the label to the flow.

## Exercise 5: Add a long paragraph and narrow the preview.

**Expected evidence:** Content remains readable and the badge does not obscure it.

**Why:** Normal flow rewraps text as the width shrinks, while a positioned element stays put, so overlap appears at narrow widths.

## Exercise 6: Explain the containing block used by an absolute element.

**Expected answer:** Identify the actual ancestor that establishes it, rather than assuming it is always the viewport.

**Why:** An absolutely positioned element is placed against its nearest positioned ancestor, or against the initial containing block when there is none.

## Reference comparison

Open `courses/web-development/solutions/web-014_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
