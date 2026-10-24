# js-057: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A brush lets a user choose a spatial interval or rectangle. The brush selection is expressed in display coordinates. The analytical selection is usually expressed in data values or record IDs. Convert between those spaces explicitly and decide which boundary values count as selected.

Linked views share application state: selecting a range in one chart changes the records or emphasis in another. If each chart keeps an unrelated hidden selection, the dashboard can contradict itself. A small state object and a pure filter function make coordination easier to inspect.

A drag gesture is not an accessible interface by itself. Provide a reset and a keyboard-friendly way to choose a meaningful preset or numeric interval. Show the selected range and count as text so the effect is understandable without interpreting color alone.

`d3.brushX()` defines a horizontal brush with an explicit extent. Its event selection is null when cleared, otherwise a pair of pixel coordinates. Use `x.invert` to recover data values. Handle null as an intentional full or empty selection according to the documented policy.

The reference uses inclusive data bounds and a preset range from 2 to 4. It calls the same brush move path used by interaction, then asserts selected IDs. Programmatic movement proves state wiring; manual pointer and keyboard checks remain separate.

## Exercise 1: Predict the selected values for range 2..4.

Boundary policy is part of the analytical contract. Test exact endpoints instead of relying on visual proximity.

**Expected:** Values 2, 3, 4 under inclusive bounds.

## Exercise 2: Clear the brush.

Null is an intentional state, not an error to ignore. Stale filters are a common linked-view bug.

**Expected:** The full dataset returns under the stated policy.

## Exercise 3: Link a brush to a textual record list.

Both views should derive from one selection state so they cannot drift independently.

**Expected:** The list and visual selection describe the same IDs.

## Exercise 4: Diagnose filtering with raw pixels against data values.

Invert through the same scale that positioned the marks. Changing chart size then remains meaningful.

**Expected:** The coordinate spaces were mixed.

## Exercise 5: Add a keyboard-accessible preset and reset.

The alternative should preserve the actual analytical action, not merely display a decorative button.

**Expected:** Native controls reach the same state update as brushing.

## Exercise 6: Design a two-chart coordination rule.

Keep data filtering and rendering separate. This makes interactions testable without depending on exact pixel appearance.

**Expected:** One shared selected-ID set drives both views.
