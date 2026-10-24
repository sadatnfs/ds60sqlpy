# js-065: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A dashboard coordinates multiple views around shared analytical state. Filters, selected IDs and display options belong in an explicit model. Each chart should derive its visible records from that model rather than mutating another chart’s DOM as an informal message bus.

Cross-filtering can change denominators. If a category chart selects one group, a rate chart must state whether its denominator is the filtered group or the full population. A dashboard can be internally consistent in code while making a misleading comparison because the analytical universe changed silently.

Pure transformation functions are easier to test than event-heavy code. A filter function takes rows and state and returns a derived result without editing the source. Rendering then consumes that result. This separation helps preserve reproducibility, reset behavior and a clear explanation of what the current view means.

Use one `state` object and an `update(nextState)` function that derives data and renders every view. Native controls dispatch state changes. Keep the original rows immutable by convention or freeze them in a small example. A reset restores a known initial state.

The reference links a category filter to bars and a numeric summary. Programmatic control activation checks state wiring, while manual keyboard review checks the actual user experience. Saving a dashboard view should record filter values and data identity, not only a screenshot.

## Exercise 1: Predict selected IDs for groupA.

A filter is a precise predicate. Check IDs before trusting a changed chart.

**Expected:** Only records whose group isA remain.

## Exercise 2: Reset the dashboard to all groups.

Reset must update shared state and all derived views, not merely clear one control’s visual highlight.

**Expected:** Every view returns to the same initial analytical universe.

## Exercise 3: Build two coordinated views from one state.

Derive once or use the same pure predicate. Independent hidden filters can create contradictory outputs.

**Expected:** Bars and summary report the same selected records and total.

## Exercise 4: Diagnose a rate denominator changing silently.

Display the current population or denominator and decide whether filtering should alter it.

**Expected:** The analytical question changed without a visible label.

## Exercise 5: Verify the source rows are unchanged.

Shared immutable input makes reset and comparison predictable. Copy before sorting when needed.

**Expected:** Filtering and rendering do not mutate original values or order.

## Exercise 6: Design a reproducible saved view.

A screenshot lacks enough information to reconstruct the analysis. Save the decisions that generated the view.

**Expected:** Record data identity, filters, units and aggregation policy.
