# web-007: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-007.md`.

## Exercise 1: Explain what a single cell value means with both headers.

**Expected answer:** 40 means forty minutes of HTML study, not an unlabeled count.

**Why:** A data cell's meaning comes from its row and column headers, and th with scope makes that relationship explicit to screen readers.

## Exercise 2: Add a caption that states the reporting period.

**Expected evidence:** The visible caption explains the table's scope.

**Why:** caption names the whole table, so assistive technology announces its scope before any values.

## Exercise 3: Build a three-row study table with correct header relationships.

**Expected evidence:** The caption, row headers and column headers identify every value.

**Why:** Scoped headers let assistive technology announce the matching row and column labels for every value.

## Exercise 4: Replace a table used to align unrelated navigation and article content.

**Expected evidence:** Use semantic regions plus CSS layout rather than false data relationships.

**Why:** A layout table announces false row and column relationships; landmarks with CSS Grid or Flexbox create the same arrangement without false semantics.

## Exercise 5: Inspect the table at a narrow width without deleting data.

**Expected evidence:** A bounded overflow region keeps all columns reachable.

**Why:** A scrolling wrapper, made focusable so keyboard users can scroll it, keeps every column reachable without shrinking text or deleting data.

## Exercise 6: Explain when a chart should keep a supporting table.

**Expected answer:** Exact values and nonvisual interpretation often benefit from a tabular equivalent.

**Why:** A chart shows a pattern quickly, while a table gives exact numbers and a nonvisual route to the same information.

## Reference comparison

Open `courses/web-development/solutions/web-007_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
