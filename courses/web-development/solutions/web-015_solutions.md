# web-015: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-015.md`.

## Exercise 1: Name the axes for flex-direction:column.

**Expected answer:** The main axis is vertical in the usual horizontal writing mode; the cross axis is horizontal.

**Approach:** Note that `flex-direction: column` sets the main axis along the block direction, so in horizontal writing it runs top to bottom.

**Why:** flex-direction: column makes the main axis vertical, so justify-content distributes items vertically and align-items aligns them horizontally.

**Plausible wrong approach:** Assuming `justify-content` still aligns horizontally fails because it always follows the main axis, which is now vertical.

**How to verify:** With a fixed container height, `justify-content: center` moves items vertically and `align-items: center` moves them horizontally.

## Exercise 2: Add gap between navigation items without per-item margins.

**Expected evidence:** Spacing is owned by the container and stays consistent when wrapping.

**Approach:** Remove per-item margins and set `gap: 0.75rem` on the flex container so spacing applies only between items.

**Why:** gap adds space only between items, including after wrapping, so the outer edges stay flush.

**Plausible wrong approach:** Keeping `margin-right` on every link fails because the last item gets extra trailing space and wrapped rows start misaligned.

**How to verify:** When the links wrap, the first link on each row lines up with the container edge and gaps look equal.

## Exercise 3: Build a wrapping navigation bar and flexible card row.

**Expected evidence:** Long labels stay reachable at narrow widths and DOM order remains logical.

**Approach:** Use a wrapping flex `ul` for navigation and a wrapping flex container for cards with `flex: 1 1 12rem` and `min-inline-size: 0`.

**Why:** Wrapping moves items to a new line instead of overflowing, while source order keeps reading and focus order logical.

**Plausible wrong approach:** Using the `order` property to move the last link first fails because keyboard focus still follows DOM order and seems to jump.

**How to verify:** At the narrow preset every link is visible, and pressing Tab visits them in the same order they appear.

## Exercise 4: Diagnose a flex child that refuses to shrink.

**Expected answer:** Inspect its minimum size, long content and flex-basis before forcing overflow hidden.

**Approach:** Inspect the child's computed `min-width`, its longest word and its `flex-basis` before changing anything.

**Why:** Flex items default to min-width: auto, so they will not shrink below their longest content until you set min-width: 0 or allow wrapping.

**Plausible wrong approach:** Adding `overflow: hidden` to the parent fails because it hides the overflow and the clipped text silently becomes unreadable.

**How to verify:** After setting `min-inline-size: 0`, the item's computed width is below its content width and nothing is clipped.

## Exercise 5: Test one item, many items and a very long label.

**Expected evidence:** The layout remains readable without relying on exactly three equal strings.

**Approach:** Run three fixtures: a single item, twelve items and one item with a very long label, at both wide and narrow widths.

**Why:** A layout tuned for three equal labels can overflow or wrap badly when the content changes.

**Plausible wrong approach:** Testing with three equal labels fails because it never exercises wrapping or the content-based minimum that real labels trigger.

**How to verify:** Each fixture shows no horizontal page scrollbar and every label is fully readable.

## Exercise 6: Explain when Flexbox fits better than Grid.

**Expected answer:** Use Flexbox for distributing items along one primary dimension; use Grid for explicit two-dimensional alignment.

**Approach:** Ask whether items only need to line up along one row or column, or whether rows and columns must align with each other.

**Why:** Flexbox distributes items along one axis based on their content, while Grid places items in explicit rows and columns.

**Plausible wrong approach:** Using Flexbox for a card grid with aligned columns fails because each wrapped row sizes independently, so columns drift.

**How to verify:** In a wrapped flex row of unequal cards, edges in different rows do not line up, while Grid aligns them.

## Reference comparison

Open `courses/web-development/solutions/web-015_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
