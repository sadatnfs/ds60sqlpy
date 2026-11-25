# js-060: explanatory solutions

Compare after your own attempt; the separate `.js` file is the complete reference program.

## Mechanism review

A treemap divides a rectangular area into nested regions whose areas represent nonnegative values. It is useful for part-to-whole structure when many categories must fit in a compact view. Exact comparisons are harder than aligned position or length, so a table or labels should support precise reading.

Hierarchy sums need a clear grain. If a parent value already includes its children and you also sum the children, the total can be double-counted. A common input supplies values only at leaves and uses hierarchy.sum to aggregate upward. Missing or negative values require an explicit policy.

Padding and rounding change visible rectangle area, so pixel area may not exactly preserve ratios in tiny charts. This is a rendering tradeoff, not a reason to claim numerical precision from a treemap. The reference checks the hierarchy’s numeric total and nonnegative geometry separately.

Create the hierarchy, call `.sum(d => d.value || 0)` only under a validated nonnegative-value contract, then apply a treemap layout. Each leaf receives x0,y0,x1,y1 bounds. Width is x1-x0 and height is y1-y0.

Sort deliberately if stable ordering matters. Updating values can substantially rearrange a treemap, making entity tracking difficult. Use stable keys and consider whether a bar chart would better serve the comparison task.

## Exercise 1: Predict the hierarchy total.

The aggregate should match the known leaf sum. Adding a duplicated parent amount would overstate the total. .sum(d => d.value || 0) adds leaf values upward. In the reference, Analysis 6, Engineering 3 and Design 1 give root.value 10, which the check asserts. If the root also carried value 10, the sum would become 20 because sum adds each node's own value to its children's.

**Expected:** 5 from leaf values 2 and 3.

## Exercise 2: Add a zero-valued leaf.

Zero area can make a category invisible. Preserve its name in a table or explanation if it belongs to the analytical universe. A leaf with value 0 keeps root.value at 10 but gets a zero-area rectangle, so its label vanishes. Removing it from the data would hide that the category exists; list it beside the chart as 0.

**Expected:** The numeric total stays unchanged and its representation needs an explicit policy.

## Exercise 3: Render labeled leaf rectangles.

Validate geometry separately from numeric sums. Padding can alter visible area without changing the underlying values. The reference draws leaves at (x0, y0) with width x1 - x0 and height y1 - y0 inside a 540 by 260 area with padding 3. Padding trims each rect slightly, so areas are close to but not exactly proportional to 6, 3 and 1. The check confirms no negative widths or heights.

**Expected:** Bounds are finite and widths/heights are nonnegative.

## Exercise 4: Diagnose parent-plus-child double counting.

Choose one source of truth for the sum. A layout cannot infer that one value already includes another. Giving the parent "Total" value 10 and also its children 6, 3 and 1 doubles the total. Put values only on leaves, or sum leaves and compare to a stored parent total as a test.

**Expected:** The input mixes aggregate and leaf grain.

## Exercise 5: Compare treemap and bars for precise ranking.

Treemaps prioritize compact hierarchy and composition. State the task that justifies the area encoding. Ranking Engineering 3 against Design 1 is quicker with aligned bars; the treemap's strength is showing that Analysis is 60% of the whole. If readers must rank three categories, show the numbers 6, 3 and 1 in labels, as the reference does, so area is not the only cue.

**Expected:** Bars usually offer easier aligned magnitude comparison.

## Exercise 6: Design a changing treemap with identity preserved.

Large layout changes can disorient viewers. Identity and textual values help them follow the same entity across updates. The reference keys leaves by d.data.name, so updates keep "Analysis" attached to the same cell group; show a text list of values when cells move. Expect cells to change aspect ratio when values change.

**Expected:** Stable keys, explicit updates and a readable alternate value list.

## After comparison

Build a treemap and a sorted bar chart from the same leaf data and ask a reader to name the third-largest leaf from each. Record which was easier, then animate one changing value with keyed rectangles and check that identities persist.
