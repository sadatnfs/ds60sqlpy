# js-066: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

The final D3 project combines a validated dataset, explicit transformations, consistent scales, keyed rendering and accessible controls. Its goal is an analytical explanation that a reader can inspect, not merely an attractive screenshot. Every visible claim should have a named source row grain, unit and aggregation policy.

Testing a visualization has several layers. Pure data tests verify filters and summaries. DOM or Canvas checks verify mark count and geometry. Interaction tests verify state changes and keyboard routes. Visual review catches clipping, illegible labels and misleading emphasis. No single screenshot or assertion covers all of these.

The reference is a small category dashboard with a filter, sorted bars, exact text values and a total summary. It uses no network input and offers a deterministic completion marker. Your independent project should change the dataset and question, then defend the encoding and limitations without copying the reference blindly.

Keep the chart’s source data, derived data and view state separate. This capstone measures its container width and uses that width in its viewBox, keeping labels at a readable 14-pixel logical size instead of shrinking a fixed 640-unit chart. A ResizeObserver schedules geometry writes on a guarded animation frame when the container changes width. Keeping writes outside the observer callback avoids a resize-notification feedback loop. It disconnects and cancels pending animation work when the preview page leaves. The table adds explicit cell padding and alignment so headers and values remain distinct. Validate IDs and finite nonnegative values before rendering. Reconcile marks by stable ID. Add a native group selector and reset. Provide a text table that remains useful without interpreting color.

The reference asserts baseline totals, filtered totals, mark counts, reset behavior and source preservation. It intentionally does not claim to automate screen-reader usability or statistical validity. Perform the manual narrow-screen, keyboard and interpretation checks before calling your own project complete.

## Exercise 1: Predict baseline and filtered totals.

Calculate from the source rows before running. The expected values should be independent of the render code. By hand: A1 3 + A2 5 + B1 4 + B2 8 = 20 hours, and A alone is 8. The reference expects "4 records; total 20 hours" and, after selecting A, "2 records; total 8 hours". Deriving these numbers by printing what render returns would make the test agree with any bug.

**Expected:** All records total 20; groupA totals 8.

## Exercise 2: Change one value and update the independent expectations.

A coordinated update should preserve identity and affect only derived values implied by the source change. Changing B2 from 8 to 6 should make the baseline 18 while A stays 8. Update the expected strings first, then run and confirm the bar, label "B2: 6" and table row all change.

**Expected:** The corresponding bar, text row and total change together.

## Exercise 3: Build a complete accessible dashboard from a blank pad.

The project integrates earlier mechanisms. A usable nonvisual or exact-value route is part of the deliverable. The reference builds a native select labeled "Learner group", bars, text labels such as "B2: 8", a captioned table and a status line, all from one render(group) call sorted by hours. A chart without the table would hide exact values from screen readers. After each change, confirm table rows and bars have equal counts.

**Expected:** Controls, marks, text values and summary agree.

## Exercise 4: Introduce a duplicate-ID failure and repair the input.

Do not remove the identity check to obtain a success marker. Keep the failure as a regression case. Duplicating id A1 fails the Set size check before rendering; renaming the second record fixes it, and the failing input stays as a test case. Removing the check to get the green marker would let two bars share one key and the join silently drop one.

**Expected:** Validation refuses ambiguous identity before rendering.

## Exercise 5: Perform keyboard and narrow-screen review.

Automated checks cannot prove the full human experience. Record actual observations and unresolved issues. Tab to the select, change it with arrow keys, and confirm the table rows stay readable at the 240-pixel minimum width.

**Expected:** All controls are reachable, labels readable and essential information available without hover.

## Exercise 6: Defend the finished analysis and its evidence limits.

Expert practice includes knowing what the chart does not establish. Separate software correctness from statistical inference and usability evidence. The fixture has four synthetic learners, so the chart proves the software path, not anything about study habits; say so, as the closing paragraph does.

**Expected:** Explain data grain, cleaning, scales, aggregation, interactions and untested surfaces.
