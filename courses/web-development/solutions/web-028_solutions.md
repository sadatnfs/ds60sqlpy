# web-028: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-028.md`.

## Exercise 1: Predict the rows retained for a forty-minute threshold.

**Expected answer:** Only the records whose minutes are at least forty remain.

**Approach:** Apply `row.minutes >= 40` to each record and keep only those where it is true, counting rows equal to 40 as retained.

**Why:** filter keeps records whose minutes are at least forty and leaves the original array unchanged.

**Plausible wrong approach:** Using `>` instead of `>=` fails because a record with exactly 40 minutes is then dropped, contradicting the stated threshold.

**How to verify:** The retained rows all show at least 40 minutes, and a record with 40 appears in the result.

## Exercise 2: Add a clear filter label and a result count.

**Expected evidence:** The user can identify the active condition and its effect.

**Approach:** Render a visible label for the threshold and a count such as 3 of 7 sessions shown from `visible.length` and `rows.length`.

**Why:** A visible condition and count tell the user why rows disappeared.

**Plausible wrong approach:** Showing only the number of visible rows fails because the reader cannot tell how many records the filter hid.

**How to verify:** After changing the threshold, the label and both numbers update together and match the table rows.

## Exercise 3: Build a filterable local study table with an explicit empty state.

**Expected evidence:** Changing the selection updates rows and count while preserving the original data.

**Approach:** Keep `rows` constant, build `visible` with `filter` on each change, rebuild the `tbody` with `createElement` and `textContent`, and show an empty message for zero rows.

**Why:** Deriving each view from the original data makes every filter reversible.

**Plausible wrong approach:** Removing rows from the DOM one by one without rebuilding fails because a later looser threshold has no rows to restore.

**How to verify:** Switching from 60 back to 0 shows every original row again and the count equals `rows.length`.

## Exercise 4: Diagnose a filter that permanently removes source records.

**Expected answer:** Keep immutable input and derive a new view for each render.

**Approach:** Search for assignments to the source array and replace them with a separate derived variable computed from the original.

**Why:** Mutating the source loses records permanently, so later filters cannot bring them back.

**Plausible wrong approach:** Copying the array once at startup fails if the filter still reassigns that copy on every change.

**How to verify:** Applying three thresholds in a row and then the lowest one shows the full expected set of rows.

## Exercise 5: Test a threshold that returns no records.

**Expected evidence:** The interface explains the empty result and allows the filter to be cleared.

**Approach:** Set a threshold above the largest value, confirm the table body is empty, and check that a message and a clear action appear.

**Why:** An explicit empty state explains the result and offers a way back, instead of an unexplained blank table.

**Plausible wrong approach:** Leaving an empty table with headers only fails because the reader cannot tell a filter result from a loading error.

**How to verify:** The message names the active threshold, and clearing the filter brings back every row.

## Exercise 6: Explain how this table connects to D3 without changing the statistical claim.

**Expected answer:** The same validated records can drive a visual encoding with explicit scales, units and an accessible equivalent.

**Approach:** Reuse the validated `visible` records as the data join for a D3 chart with labeled axes, units and an equivalent table.

**Why:** The same validated records, units and filter must drive the visual encoding, and an accessible table keeps the exact values available.

**Plausible wrong approach:** Starting the y axis at a value other than zero for bar lengths fails because bar heights then exaggerate differences.

**How to verify:** The chart and the table show the same records and values, and the axis labels state minutes.

## Reference comparison

Open `courses/web-development/solutions/web-028_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
