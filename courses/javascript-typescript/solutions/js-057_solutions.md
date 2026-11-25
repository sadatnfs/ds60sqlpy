# js-057: explanatory solutions

Compare after your own attempt; the separate `.js` file is the complete reference program.

## Mechanism review

A brush lets a user choose a spatial interval or rectangle. The brush selection is expressed in display coordinates. The analytical selection is usually expressed in data values or record IDs. Convert between those spaces explicitly and decide which boundary values count as selected.

Linked views share application state: selecting a range in one chart changes the records or emphasis in another. If each chart keeps an unrelated hidden selection, the dashboard can contradict itself. A small state object and a pure filter function make coordination easier to inspect.

A drag gesture is not an accessible interface by itself. Provide a reset and a keyboard-friendly way to choose a meaningful preset or numeric interval. Show the selected range and count as text so the effect is understandable without interpreting color alone.

`d3.brushX()` defines a horizontal brush with an explicit extent. Its event selection is null when cleared, otherwise a pair of pixel coordinates. Use `x.invert` to recover data values. Handle null as an intentional full or empty selection according to the documented policy.

The reference uses inclusive data bounds and a preset range from 2 to 4. It calls the same brush move path used by interaction, then asserts selected IDs. Programmatic movement proves state wiring; manual pointer and keyboard checks remain separate.

## Exercise 1: Predict the selected values for range 2..4.

Boundary policy is part of the analytical contract. Test exact endpoints instead of relying on visual proximity. Brushing from x(2) = 230 to x(4) = 410 and inverting gives roughly 2 and 4; the filter uses `d.x >= range[0] - 1e-9` and `d.x <= range[1] + 1e-9`, so 2, 3 and 4 are selected. Without the tolerance, floating-point inversion could return 2.0000000001 and drop the 2. The reference checks the ids join to "2,3,4".

**Expected:** Values 2, 3, 4 under inclusive bounds.

## Exercise 2: Clear the brush.

Null is an intentional state, not an error to ignore. Stale filters are a common linked-view bug. Clearing gives event.selection null, so range is undefined and selected falls back to all five rows. Leaving selected as the last brushed set would keep stale filters. Press "Reset selection" and confirm the status lists 1 through 5.

**Expected:** The full dataset returns under the stated policy.

## Exercise 3: Link a brush to a textual record list.

Both views should derive from one selection state so they cannot drift independently. One selected array drives both the circle fill and the status text "Selected: 2, 3, 4". Updating fill in the brush handler and text in a separate click handler would let them disagree. Compare the blue circles against the listed ids.

**Expected:** The list and visual selection describe the same IDs.

## Exercise 4: Diagnose filtering with raw pixels against data values.

Invert through the same scale that positioned the marks. Changing chart size then remains meaningful. Filtering d.x >= 230 compares data values 1 to 5 with pixels, so nothing matches. Apply x.invert to the selection first, as the reference does.

**Expected:** The coordinate spaces were mixed.

## Exercise 5: Add a keyboard-accessible preset and reset.

The alternative should preserve the actual analytical action, not merely display a decorative button. "Select 2 through 4" calls brush.move with [x(2), x(4)], the same path as dragging, so keyboard users reach identical state. Tab to it and press Enter. The status text should then read "Selected: 2, 3, 4".

**Expected:** Native controls reach the same state update as brushing.

## Exercise 6: Design a two-chart coordination rule.

Keep data filtering and rendering separate. This makes interactions testable without depending on exact pixel appearance. A second chart should read the same set of selected ids rather than run its own filter; verify both show "2,3,4" after one brush. Write the selection logic as a pure function from a range to ids so it can be unit tested without a browser.

**Expected:** One shared selected-ID set drives both views.

## After comparison

Link a brush on a time axis to a bar chart of counts per category and a text list, and add a keyboard preset for the last seven days. Check that the bars, the list and the announced count describe the same selected IDs after every change.
