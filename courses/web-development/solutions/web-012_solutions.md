# web-012: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-012.md`.

## Exercise 1: Explain the reference for rem and a typical em use.

**Expected answer:** Rem uses the root font size; em commonly scales with the relevant element's font size.

**Why:** rem always refers to the root element's font size, while em refers to the current element's font size, or to the parent's when it is used in font-size itself.

## Exercise 2: Apply a system font stack without network dependencies.

**Expected evidence:** The page remains readable offline on different operating systems.

**Why:** A system font stack uses fonts that are already installed, so text renders offline without network requests.

## Exercise 3: Build a reading page with bounded measure and scalable headings.

**Expected evidence:** Text stays comfortable at wide and narrow sizes without fixed-height clipping.

**Why:** A bounded measure keeps line length readable, and clamp scales headings between safe limits while respecting the reader's font size.

## Exercise 4: Diagnose text that overlaps after zooming.

**Expected answer:** Inspect fixed heights, line heights and positioned containers rather than disabling zoom.

**Why:** Zoom enlarges text but fixed boxes keep their size, so content spills out and overlaps.

## Exercise 5: Test at increased browser zoom with long content.

**Expected evidence:** Reading order, text visibility and controls remain intact.

**Why:** Text must remain usable when resized to 200 percent, which reveals fixed-size assumptions in the layout.

## Exercise 6: Explain why ch is a useful approximation rather than a word-count guarantee.

**Expected answer:** It measures the font's zero glyph, and actual character widths vary.

**Why:** 1ch is the advance width of the 0 glyph, so a line of narrow letters fits more characters and a line of wide letters fewer.

## Reference comparison

Open `courses/web-development/solutions/web-012_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
