# js-066: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

The final D3 project combines a validated dataset, explicit transformations, consistent scales, keyed rendering and accessible controls. Its goal is an analytical explanation that a reader can inspect, not merely an attractive screenshot. Every visible claim should have a named source row grain, unit and aggregation policy.

Testing a visualization has several layers. Pure data tests verify filters and summaries. DOM or Canvas checks verify mark count and geometry. Interaction tests verify state changes and keyboard routes. Visual review catches clipping, illegible labels and misleading emphasis. No single screenshot or assertion covers all of these.

The reference is a small category dashboard with a filter, sorted bars, exact text values and a total summary. It uses no network input and offers a deterministic completion marker. Your independent project should change the dataset and question, then defend the encoding and limitations without copying the reference blindly.

Keep the chart’s source data, derived data and view state separate. This capstone measures its container width and uses that width in its viewBox, keeping labels at a readable 14-pixel logical size instead of shrinking a fixed 640-unit chart. A ResizeObserver schedules geometry writes on a guarded animation frame when the container changes width. Keeping writes outside the observer callback avoids a resize-notification feedback loop. It disconnects and cancels pending animation work when the preview page leaves. The table adds explicit cell padding and alignment so headers and values remain distinct. Validate IDs and finite nonnegative values before rendering. Reconcile marks by stable ID. Add a native group selector and reset. Provide a text table that remains useful without interpreting color.

The reference asserts baseline totals, filtered totals, mark counts, reset behavior and source preservation. It intentionally does not claim to automate screen-reader usability or statistical validity. Perform the manual narrow-screen, keyboard and interpretation checks before calling your own project complete.

## Exercise 1: Predict baseline and filtered totals.

Calculate from the source rows before running. The expected values should be independent of the render code.

**Expected:** All records total 20; groupA totals 8.

## Exercise 2: Change one value and update the independent expectations.

A coordinated update should preserve identity and affect only derived values implied by the source change.

**Expected:** The corresponding bar, text row and total change together.

## Exercise 3: Build a complete accessible dashboard from a blank pad.

The project integrates earlier mechanisms. A usable nonvisual or exact-value route is part of the deliverable.

**Expected:** Controls, marks, text values and summary agree.

## Exercise 4: Introduce a duplicate-ID failure and repair the input.

Do not remove the identity check to obtain a success marker. Keep the failure as a regression case.

**Expected:** Validation refuses ambiguous identity before rendering.

## Exercise 5: Perform keyboard and narrow-screen review.

Automated checks cannot prove the full human experience. Record actual observations and unresolved issues.

**Expected:** All controls are reachable, labels readable and essential information available without hover.

## Exercise 6: Defend the finished analysis and its evidence limits.

Expert practice includes knowing what the chart does not establish. Separate software correctness from statistical inference and usability evidence.

**Expected:** Explain data grain, cleaning, scales, aggregation, interactions and untested surfaces.
