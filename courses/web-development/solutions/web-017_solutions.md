# web-017: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-017.md`.

## Exercise 1: Predict the base layout below the breakpoint.

**Expected answer:** The layout stays in one column.

**Why:** Rules outside the query apply at every width, and the min-width query only adds the two-column layout when there is room.

## Exercise 2: Choose a breakpoint by resizing actual content.

**Expected answer:** Record where labels or article width become uncomfortable rather than choosing a device name.

**Why:** Content-driven breakpoints follow the design's real limits, while device-named widths go out of date as screens change.

## Exercise 3: Build a responsive course outline with a readable article.

**Expected evidence:** The page adapts between stacked and two-column layouts without losing content.

**Why:** A small-screen baseline works everywhere, and the enhancement applies only when the measured space allows it.

## Exercise 4: Diagnose a mobile page rendered as a tiny desktop screenshot.

**Expected answer:** Check viewport metadata and inflexible widths.

**Why:** Without width=device-width the mobile browser lays out a wide virtual page and scales it down, and fixed widths prevent reflow.

## Exercise 5: Test narrow width together with enlarged text.

**Expected evidence:** All controls and text remain reachable with no required two-axis page scrolling.

**Why:** Larger text needs more space, so a layout that fits at default size can force horizontal scrolling when zoomed.

## Exercise 6: Explain why responsive design is more than media queries.

**Expected answer:** Intrinsic sizing, wrapping, content order and user settings are fundamental parts of the behavior.

**Why:** Intrinsic sizing, wrapping, flexible units and source order already respond to space and user settings; media queries only adjust the remaining cases.

## Reference comparison

Open `courses/web-development/solutions/web-017_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
