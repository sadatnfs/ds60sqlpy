# dax-048: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-048_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Ascending month snapshot

A supplied flat visual snapshot in ascending month order; arithmetic expansion only.

| Position | Month | Revenue | RunningRevenue |
| --- | --- | --- | --- |
| 1 | January2025 | 67 | 67 |
| 2 | February2025 | 56 | 123 |

The snapshot values are already monthly aggregates. Reaching back to individual Sales rows would change the scope and require model-level logic.

- The first position contains January revenue 67.
- The second position includes 67 plus February 56.
- Running values are 67 and 123.

### Case B: Reversed visual order

The same monthly values in descending month order; no change to their underlying amounts.

| Position | Month | Revenue | RunningRevenue |
| --- | --- | --- | --- |
| 1 | February2025 | 56 | 56 |
| 2 | January2025 | 67 | 123 |

A cumulative-looking line can therefore change meaning when sort order changes. State its axis and ordering contract in the report.

- February 56 is now the first visible position.
- January 67 is added at the second position.
- The intermediate running value changes from 67 to 56 while the final sum remains 123.

## Explained practice answers

### Exercise 1

Predict the running result if the visual includes only February.

The running value is 56, not all-year 123, unless another explicit semantic-model measure supplies a different value.

**Why it fits this model:** A visual calculation sees only the visual's rows. With February alone, the running sum has one row to add.

**Tempting mistake:** Expecting 123 because February 3 YTD was 123 in an earlier lesson. That total came from a model measure using the Date table, not from visual rows.

**How to confirm:** A one-row snapshot of February 2025 at 56 returns RunningRevenue 56.

### Exercise 2

Add a third observed month with revenue 10 at the end.

The running values become 67, 123, 133 for that expanded snapshot.

**Why it fits this model:** With a third row at position 3, each running value adds every row at or before its position: 67, 67 + 56 and 123 + 10.

**Tempting mistake:** Appending the new row at position 1 changes every running value, as reversing the order did in case B.

**How to confirm:** The three-row DATATABLE returns 67, 123 and 133.

### Exercise 3

Write the intended visual expression and its scope contract.

RUNNINGSUM([Revenue]) on a flat monthly visual, ascending calendar order, with a stated reset policy and the required Revenue field present.

**Why it fits this model:** `RUNNINGSUM ( [Revenue] )` on a flat visual with Month on the axis, sorted by month key ascending, with no reset and Revenue in the visual.

**Tempting mistake:** Sorting by the Month text. "February2025" sorts before "January2025", which produces case B's 56 then 123.

**How to confirm:** With the axis sorted by MonthKey, January 2025 shows 67 and February 2025 shows 123.

### Exercise 4

Diagnose using USERELATIONSHIP inside this visual calculation.

Move the date-role calculation into a semantic-model measure, then place that measure's results in the visual.

**Why it fits this model:** Visual calculations work on the visual's grid and cannot activate relationships. Date roles belong in model measures.

**Tempting mistake:** Writing USERELATIONSHIP inside the visual calculation for a shipped running total. It is not allowed in that scope.

**How to confirm:** A model measure for shipped revenue gives January 2025 47 and February 2025 76; RUNNINGSUM over those cells gives 47 and 123.

### Exercise 5

Explain why a hierarchical subtotal requires additional review.

Specify axis, partition and reset semantics; the flat two-row expansion does not prove hierarchical behavior.

**Why it fits this model:** With Year and Month on the axis, January 2024 at 64 and January and February 2025 at 67 and 56, a running sum can reset at each year or carry on.

**Tempting mistake:** Assuming the flat result carries over. Resetting gives 64, then 67 and 123; continuing gives 64, 131 and 187.

**How to confirm:** Specify the reset policy, then check both year subtotals (64 and 123) and the final 187 or 123.

### Exercise 6

Transfer the distinction to a report-specific moving average.

Use it only when the visual grain and order match the intended metric; retain reusable model measures for cross-report semantics.

**Why it fits this model:** A two-month moving average on visual rows averages displayed cells: (67 + 56) / 2 = 61.5 for February 2025.

**Tempting mistake:** Hiding empty months makes the window jump. If only months with sales appear, January 2025's window pairs it with January 2024 and gives (64 + 67) / 2 = 65.5.

**How to confirm:** Confirm that the visual shows every month in order. For averages reused across reports, build a model measure over the Date table.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
