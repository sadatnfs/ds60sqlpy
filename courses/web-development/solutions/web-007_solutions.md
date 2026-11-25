# web-007: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-007.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Explain what a single cell value means with both headers.

**Expected answer:** 40 means forty minutes of HTML study, not an unlabeled count.

**Approach:** Follow the cell left to its row header and up to its column header, then join them into one sentence with the unit.

**Why:** A data cell's meaning comes from its row and column headers, and th with scope makes that relationship explicit to screen readers.

**Plausible wrong approach:** Reading 40 as a score or a count fails because only the Minutes column header gives the number its unit.

**How to verify:** Your sentence names HTML, the value 40 and minutes, and each word comes from a header cell in the source.

## Exercise 2: Add a caption that states the reporting period.

**Expected evidence:** The visible caption explains the table's scope.

**Approach:** Add a `caption` as the first child of `table` that states the reporting period, such as week 1.

**Why:** caption names the whole table, so assistive technology announces its scope before any values.

**Plausible wrong approach:** Putting the period in a heading above the table fails because the heading is not programmatically tied to the table and may drift away.

**How to verify:** `document.querySelector('table').caption.textContent` in the console returns exactly the period text you wrote in the caption.

## Exercise 3: Build a three-row study table with correct header relationships.

**Expected evidence:** The caption, row headers and column headers identify every value.

**Approach:** Write a header row of `th scope="col"` cells, then three body rows that each start with `th scope="row"`.

**Why:** Scoped headers let assistive technology announce the matching row and column labels for every value.

**Plausible wrong approach:** Marking only the first row with `th` fails because row values then lack the subject label that identifies them.

**How to verify:** The console shows 2 column headers and 3 row headers, and every `td` sits in a row that begins with a `th`.

## Exercise 4: Replace a table used to align unrelated navigation and article content.

**Expected evidence:** Use semantic regions plus CSS layout rather than false data relationships.

**Approach:** Replace the layout table with `nav` and `article` elements and arrange them with CSS grid or flexbox.

**Why:** A layout table announces false row and column relationships; landmarks with CSS Grid or Flexbox create the same arrangement without false semantics.

**Plausible wrong approach:** Adding `role="presentation"` to the table and stopping fails because the layout still depends on table markup and resists narrow widths.

**How to verify:** The tree has no `table` around the page regions, and the regions sit side by side through CSS at a wide preset.

## Exercise 5: Inspect the table at a narrow width without deleting data.

**Expected evidence:** A bounded overflow region keeps all columns reachable.

**Approach:** Wrap the table in a container with `overflow-x: auto` and a focusable label so the columns scroll inside it.

**Why:** A scrolling wrapper, made focusable so keyboard users can scroll it, keeps every column reachable without shrinking text or deleting data.

**Plausible wrong approach:** Hiding columns with `display: none` at narrow widths fails because the data disappears for everyone on small screens.

**How to verify:** At the narrow preset every column is reachable by scrolling the container, and the page body itself does not overflow.

## Exercise 6: Explain when a chart should keep a supporting table.

**Expected answer:** Exact values and nonvisual interpretation often benefit from a tabular equivalent.

**Approach:** Keep a table whenever readers need exact values or cannot perceive the chart's shapes, and describe the trend in prose as well.

**Why:** A chart shows a pattern quickly, while a table gives exact numbers and a nonvisual route to the same information.

**Plausible wrong approach:** Relying on the chart plus hover tooltips fails because keyboard and screen reader users may never reach the values.

**How to verify:** Every value plotted in the chart also appears once in the table with matching units.

## Reference comparison

The reference requires three th elements with scope row inside tbody, so it catches a table whose first column is still plain td cells. It does not check the caption text, the column headers or the removal of the layout table, and it cannot prove how a screen reader announces a cell.

Open `courses/web-development/solutions/web-007_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
