# js-065: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A dashboard coordinates multiple views around shared analytical state. Filters, selected IDs and display options belong in an explicit model. Each chart should derive its visible records from that model rather than mutating another chart’s DOM as an informal message bus.

Cross-filtering can change denominators. If a category chart selects one group, a rate chart must state whether its denominator is the filtered group or the full population. A dashboard can be internally consistent in code while making a misleading comparison because the analytical universe changed silently.

Pure transformation functions are easier to test than event-heavy code. A filter function takes rows and state and returns a derived result without editing the source. Rendering then consumes that result. This separation helps preserve reproducibility, reset behavior and a clear explanation of what the current view means.

Use one `state` object and an `update(nextState)` function that derives data and renders every view. Native controls dispatch state changes. Keep the original rows immutable by convention or freeze them in a small example. A reset restores a known initial state.

The reference links a category filter to bars and a numeric summary. Programmatic control activation checks state wiring, while manual keyboard review checks the actual user experience. Saving a dashboard view should record filter values and data identity, not only a screenshot.

## Exercise 1: Predict selected IDs for groupA.

A filter is a precise predicate. Check IDs before trusting a changed chart. Clicking "Show A" sets state.group to "A", and the filter keeps A1 (2) and A2 (3), so the summary reads "A: 2 records; total 5". A filter written as d.group.includes(state.group) would still work for A but would also match a future group "AA". The reference checks the summary text and two rects.

**Expected:** Only records whose group isA remain.

## Exercise 2: Reset the dashboard to all groups.

Reset must update shared state and all derived views, not merely clear one control’s visual highlight. "Show all" sets state.group back to "all" and calls render, which restores three bars and "all: 3 records; total 9". Clearing only the button highlight would leave the old filter in state. The reference checks render().length is 3.

**Expected:** Every view returns to the same initial analytical universe.

## Exercise 3: Build two coordinated views from one state.

Derive once or use the same pure predicate. Independent hidden filters can create contradictory outputs. One render function computes visible and uses it for both the bars and the summary, so they cannot disagree. A second filter inside the summary code could drift if someone edits only one. Click each button and compare bar count to the record count in the text.

**Expected:** Bars and summary report the same selected records and total.

## Exercise 4: Diagnose a rate denominator changing silently.

Display the current population or denominator and decide whether filtering should alter it. If a share were computed as value / sum(visible), filtering to A would change the denominator from 9 to 5. Show the denominator in the summary. Keep counts like "2 records" visible so readers know which population a rate refers to after filtering.

**Expected:** The analytical question changed without a visible label.

## Exercise 5: Verify the source rows are unchanged.

Shared immutable input makes reset and comparison predictable. Copy before sorting when needed. rows and each row are frozen with Object.freeze, so an accidental sort in place would throw in strict mode. The check confirms `rows[0].value` is still 2 after reset.

**Expected:** Filtering and rendering do not mutate original values or order.

## Exercise 6: Design a reproducible saved view.

A screenshot lacks enough information to reconstruct the analysis. Save the decisions that generated the view. Save { group: "A" } plus the dataset name and aggregation rule; reloading that state should reproduce "A: 2 records; total 5". A screenshot of the A view would not record that the total is a sum of value over frozen rows.

**Expected:** Record data identity, filters, units and aggregation policy.
