# web-011: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-011.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Calculate outer widths for the two examples.

**Expected answer:** They are 244px and 200px, before margins.

**Approach:** Add content width, both paddings and both borders for the content-box card, and for the border-box card treat 200px as the border box itself.

**Why:** With content-box, 200px of content plus two 20px paddings plus two 2px borders gives 244px; with border-box, the padding and border fit inside the declared 200px.

**Plausible wrong approach:** Adding padding to the border-box card as well gives 244px for both, because it ignores that border-box absorbs padding and border inside the declared width.

**How to verify:** Inspect each card's box model diagram in developer tools and read 244 and 200 as the border-box widths.

## Exercise 2: Add border-box sizing to a document and inspect one card.

**Expected evidence:** The declared width matches the border-box width.

**Approach:** Add `*, *::before, *::after { box-sizing: border-box; }` near the top of the stylesheet so every element and pseudo-element uses the same model.

**Why:** With border-box, the declared width includes padding and border, so the number you write matches the rendered box.

**Plausible wrong approach:** Setting border-box only on `.card` fails because nested elements and generated content keep content-box and disagree with the card's arithmetic.

**How to verify:** The Computed panel shows `box-sizing: border-box` on the card and its children, and the card's rendered width equals its declared width.

## Exercise 3: Build a readable card that contains a long identifier.

**Expected evidence:** The identifier wraps or scrolls locally without overflowing the page.

**Approach:** Give the card a `max-inline-size` in `ch` and let the long identifier break with `overflow-wrap: anywhere` or scroll in its own `code` box.

**Why:** overflow-wrap: anywhere or a local overflow area stops an unbreakable string from widening the whole page.

**Plausible wrong approach:** Setting `white-space: nowrap` on the identifier fails because the unbroken string pushes the card wider than the viewport.

**How to verify:** At the narrow preset the page has no horizontal scrollbar, and the full identifier is still readable inside the card.

## Exercise 4: Repair a fixed height that clips a validation message.

**Expected evidence:** Use content-driven height or an explicitly accessible bounded scroll region.

**Approach:** Replace the fixed `height` with `min-block-size` and let the content set the final height of the message box.

**Why:** A content-driven height grows when a message appears, while a fixed height clips or overlaps it.

**Plausible wrong approach:** Increasing the fixed height to 5rem fails because a larger font size or a longer message clips again at the new limit.

**How to verify:** Change the message to three lines and enlarge text; the entire message stays visible and the box grows.

## Exercise 5: Increase text size and inspect overflow.

**Expected evidence:** Essential text remains visible and controls remain reachable.

**Approach:** Raise the browser zoom or root font size in steps and watch every box that has a fixed `height` or `width`.

**Why:** Fixed heights and widths do not grow with text, so enlarged text exposes clipping that normal size hides.

**Plausible wrong approach:** Shrinking the viewport only fails because some clipping appears only when text grows while the layout width stays the same.

**How to verify:** At 200 percent zoom, each message, label and button remains visible and reachable with Tab.

## Exercise 6: Explain which dimensions margin does and does not affect.

**Expected answer:** Margins add external separation but are not included in either box-sizing width.

**Approach:** Draw the four layers (content, padding, border, margin) and mark that width and box-sizing describe only the first three.

**Why:** Margin lies outside the border, so it changes the space between boxes but never counts toward width under either box-sizing value.

**Plausible wrong approach:** Including margin in the 244px total fails because margin sits outside the border box and never counts in width calculations.

**How to verify:** Adding `margin: 10px` leaves the inspected border-box width unchanged while the spacing between cards grows.

## Reference comparison

The reference reads the card's computed box-sizing and requires border-box, so it catches a missing sizing rule or one that never matched the card. It does not measure the long identifier, test enlarged text or detect clipped content, so narrow the preview and zoom in to compare overflow behavior.

Open `courses/web-development/solutions/web-011_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
