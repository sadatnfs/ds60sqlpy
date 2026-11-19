# web-011: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-011.md`.

## Exercise 1: Calculate outer widths for the two examples.

**Expected answer:** They are 244px and 200px, before margins.

**Why:** With content-box, 200px of content plus 2 × 20px padding plus 2 × 2px border gives 244px; with border-box, the padding and border fit inside the declared 200px.

## Exercise 2: Add border-box sizing to a document and inspect one card.

**Expected evidence:** The declared width matches the border-box width.

**Why:** With border-box, the declared width includes padding and border, so the number you write matches the rendered box.

## Exercise 3: Build a readable card that contains a long identifier.

**Expected evidence:** The identifier wraps or scrolls locally without overflowing the page.

**Why:** overflow-wrap: anywhere or a local overflow area stops an unbreakable string from widening the whole page.

## Exercise 4: Repair a fixed height that clips a validation message.

**Expected evidence:** Use content-driven height or an explicitly accessible bounded scroll region.

**Why:** A content-driven height grows when a message appears, while a fixed height clips or overlaps it.

## Exercise 5: Increase text size and inspect overflow.

**Expected evidence:** Essential text remains visible and controls remain reachable.

**Why:** Fixed heights and widths do not grow with text, so enlarged text exposes clipping that normal size hides.

## Exercise 6: Explain which dimensions margin does and does not affect.

**Expected answer:** Margins add external separation but are not included in either box-sizing width.

**Why:** Margin lies outside the border, so it changes the space between boxes but never counts toward width under either box-sizing value.

## Reference comparison

Open `courses/web-development/solutions/web-011_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
