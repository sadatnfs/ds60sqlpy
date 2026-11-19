# web-028: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-028.md`.

## Exercise 1: Predict the rows retained for a forty-minute threshold.

**Expected answer:** Only the records whose minutes are at least forty remain.

**Why:** filter keeps records whose minutes are at least forty and leaves the original array unchanged.

## Exercise 2: Add a clear filter label and a result count.

**Expected evidence:** The user can identify the active condition and its effect.

**Why:** A visible condition and count tell the user why rows disappeared.

## Exercise 3: Build a filterable local study table with an explicit empty state.

**Expected evidence:** Changing the selection updates rows and count while preserving the original data.

**Why:** Deriving each view from the original data makes every filter reversible.

## Exercise 4: Diagnose a filter that permanently removes source records.

**Expected answer:** Keep immutable input and derive a new view for each render.

**Why:** Mutating the source loses records permanently, so later filters cannot bring them back.

## Exercise 5: Test a threshold that returns no records.

**Expected evidence:** The interface explains the empty result and allows the filter to be cleared.

**Why:** An explicit empty state explains the result and offers a way back, instead of an unexplained blank table.

## Exercise 6: Explain how this table connects to D3 without changing the statistical claim.

**Expected answer:** The same validated records can drive a visual encoding with explicit scales, units and an accessible equivalent.

**Why:** The same validated records, units and filter must drive the visual encoding, and an accessible table keeps the exact values available.

## Reference comparison

Open `courses/web-development/solutions/web-028_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.
