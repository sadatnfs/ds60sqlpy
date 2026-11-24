# viz-004: explanatory solutions

Compare with your attempt when you choose to reveal the reference. These answers explain the six tasks in the guide. The complete Python and browser references use the same scientific fixture.

## Exercise 1

Group B contains u4,u5,u6,u7. Filtering by group should return those IDs regardless of row ordering.

## Exercise 2

The masks are `[true, true]`, `[true, false]` and `[false, true]`. Python serializes them in update menus; JavaScript applies them through named native buttons and restyle. Await browser updates before announcing state.

## Exercise 3

Sort complete records before building trace arrays and customdata. Hover text reads the persistent user ID from customdata rather than interpreting point position as identity.

## Exercise 4

Treat absent event data as an empty point list. Clear the status to No selected points. A stale list is incorrect state even when the chart itself clears visually.

## Exercise 5

In the browser, tab to a named group button and press Enter or Space. Confirm its pressed state and live status. The source table remains eight rows and is labeled as complete data. Python's table fallback remains readable without hover.

## Exercise 6

An empty group receives no points. Keep the group choice explicit and display an empty-state interpretation; do not reuse previously filtered arrays. The full table reflects the revised source collection.

## Solution reasoning

**Approach.** `case_04` creates eight records, u0 to u7, where the first four belong to group A and the rest to group B, with a baseline and an outcome for each. It draws one scatter trace per group, circles for A and squares for B, and stores the user ID and group in `customdata` so hover text names the record. A dropdown in `updatemenus` switches between All, A and B by sending visibility masks to the `update` method, and `uirevision` keeps the user's zoom while the figure updates. The source table always lists all eight records. The browser variant uses named buttons with `aria-pressed` and calls `Plotly.restyle` instead of a dropdown.

**Why it is correct.** Each button sends a two-element mask that lines up with the two traces: All is [true, true], A is [true, false] and B is [false, true]. Only visibility changes; the underlying arrays and the table do not, so filtering is an inspection step rather than a change to the dataset. The reference asserts that the two traces together hold eight points and that group B is exactly u4, u5, u6 and u7, which the printed table confirms. Because the hover reads the ID from `customdata`, the identity shown does not depend on the order in which points were drawn. The `uirevision` string, `viz-004-fixture-v1`, stays constant across updates, so Plotly treats each filter as the same view and does not reset the axes the reader chose.

**A plausible wrong approach.** A tempting implementation rebuilds the table from whatever is currently visible, so choosing B shrinks it to four rows. A reader then sees half the population and may report its summary as if it described everyone, which the caption warns against. Another error identifies points by their position in a trace, so after a re-sort point 0 of group B could refer to a different user. Exercise 4 adds a third: leaving the previous selection list on screen after a click that selects nothing, which shows stale state even though the chart has cleared. Building the mask by trace name rather than by position would also guard against a reordered trace list silently hiding the wrong group.

**How to verify.** Run `.venv/bin/python courses/data-visualization/references/viz-004.py` and confirm the table lists eight users with u4 to u7 in group B before `viz-004 Plotly complete`. In the browser, press Tab to reach the B button, press Enter, and check that its `aria-pressed` becomes true, the status text updates and the table still has eight rows. Zoom into one corner first and confirm the zoom survives the filter change, which is what `uirevision` promises. Hover a square and confirm the user ID matches its table row. For exercise 6, give one group no records and confirm the chart shows an empty-state message instead of the previous group's points.

## Complete references and evidence

[Python reference](../references/viz-004.py) and [JavaScript reference](../references/viz-004.js) are complete programs for their declared hosts. Python figure construction and browser rendering are separate observations. Test numerical values, real interaction, table access, narrow layouts and source persistence separately. No completion marker certifies scientific validity or learner mastery.
