# js-053: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

Grouped bars support comparison of categories within several groups using a shared baseline for each bar. Stacked bars emphasize totals and composition, but interior segments do not share a common baseline. The choice depends on whether the reader needs precise subgroup comparisons or an overview of parts and whole.

A stack layout computes interval endpoints for each series in each row. The rectangle represents the distance between the lower and upper endpoints, not the upper endpoint alone. A normalized stack transforms each row to shares, which can hide differences in total magnitude.

A zero total has no meaningful fraction composition unless a policy is stated. Missing components also differ from known zeros. Preserve the original totals alongside a 100% chart so the reader can see whether a large-looking share represents two observations or two million.

`d3.stack().keys(['a','b'])` reads the named components from each record and returns one series for each key. A point is `[lower, upper]` and retains its original row in `.data`. Use y(lower)-y(upper) for positive vertical height.

`stackOffsetExpand` normalizes each row to unit total when appropriate. Validate finite nonnegative components for this introductory positive stack. Signed values need a different design, such as a diverging stack with explicit positive and negative baselines.

## Exercise 1: Predict the stack endpoints.

Endpoints are cumulative positions. The second segment height represents3, not5.

**Expected:** First segment 0..2, second 2..5.

## Exercise 2: Normalize two proportional rows.

Normalization removes absolute scale. Preserve totals if they matter to the analytical question.

**Expected:** Both have 40% and 60% shares despite different totals.

## Exercise 3: Build a two-series stacked chart.

Check both component and total invariants. A plausible total can hide an incorrect internal segment calculation.

**Expected:** Segment heights match component values and total heights match row sums.

## Exercise 4: Diagnose using upper endpoint as segment height.

Compute the interval length in scale coordinates. Stack output is geometry input, not a direct height field.

**Expected:** Later segments are exaggerated because the lower endpoint was ignored.

## Exercise 5: Handle a zero-total group.

Dividing by zero does not produce an interpretable percentage. Do not invent shares to fill the chart.

**Expected:** Show an explicit no-composition state or documented zero representation.

## Exercise 6: Choose grouped or stacked bars for subgroup comparison.

A stack can still be useful for total composition, but the tradeoff should be explicit.

**Expected:** Use shared baselines when precise subgroup comparison is the primary task.
