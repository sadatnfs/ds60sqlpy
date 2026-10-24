# js-060: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A treemap divides a rectangular area into nested regions whose areas represent nonnegative values. It is useful for part-to-whole structure when many categories must fit in a compact view. Exact comparisons are harder than aligned position or length, so a table or labels should support precise reading.

Hierarchy sums need a clear grain. If a parent value already includes its children and you also sum the children, the total can be double-counted. A common input supplies values only at leaves and uses hierarchy.sum to aggregate upward. Missing or negative values require an explicit policy.

Padding and rounding change visible rectangle area, so pixel area may not exactly preserve ratios in tiny charts. This is a rendering tradeoff, not a reason to claim numerical precision from a treemap. The reference checks the hierarchy’s numeric total and nonnegative geometry separately.

Create the hierarchy, call `.sum(d => d.value || 0)` only under a validated nonnegative-value contract, then apply a treemap layout. Each leaf receives x0,y0,x1,y1 bounds. Width is x1-x0 and height is y1-y0.

Sort deliberately if stable ordering matters. Updating values can substantially rearrange a treemap, making entity tracking difficult. Use stable keys and consider whether a bar chart would better serve the comparison task.

## Exercise 1: Predict the hierarchy total.

The aggregate should match the known leaf sum. Adding a duplicated parent amount would overstate the total.

**Expected:** 5 from leaf values 2 and 3.

## Exercise 2: Add a zero-valued leaf.

Zero area can make a category invisible. Preserve its name in a table or explanation if it belongs to the analytical universe.

**Expected:** The numeric total stays unchanged and its representation needs an explicit policy.

## Exercise 3: Render labeled leaf rectangles.

Validate geometry separately from numeric sums. Padding can alter visible area without changing the underlying values.

**Expected:** Bounds are finite and widths/heights are nonnegative.

## Exercise 4: Diagnose parent-plus-child double counting.

Choose one source of truth for the sum. A layout cannot infer that one value already includes another.

**Expected:** The input mixes aggregate and leaf grain.

## Exercise 5: Compare treemap and bars for precise ranking.

Treemaps prioritize compact hierarchy and composition. State the task that justifies the area encoding.

**Expected:** Bars usually offer easier aligned magnitude comparison.

## Exercise 6: Design a changing treemap with identity preserved.

Large layout changes can disorient viewers. Identity and textual values help them follow the same entity across updates.

**Expected:** Stable keys, explicit updates and a readable alternate value list.
