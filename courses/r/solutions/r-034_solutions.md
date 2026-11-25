# r-034: reference reasoning

Run the [complete reference](r-034_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The unique id/visit key determines one value per output cell. No aggregation is necessary.

The missing B visit 2 cell means no supplied record here. Keeping the original long rows or a separate presence table preserves that distinction.

## Explained practice

### Exercise 1

Identify the cell key for person/visit/value data.

The key is person plus visit.

**Approach:** Name the cell key as id plus visit, and check it with `anyDuplicated(long[c("id", "visit")])`.

**Why it holds here:** Each value belongs to one person at one visit. The four rows have four distinct pairs, so they fill the 2 by 2 grid of wide cells exactly once each.

**Tempting mistake:** Using id alone as the key. A appears twice and B appears twice, so the check would fail on correct data, and visit alone repeats in the same way.

**Verify:** `anyDuplicated(long[c("id", "visit")])` returns 0.

### Exercise 2

Add a third visit for every person.

The wide schema gains the declared third-visit value column.

**Approach:** Add long rows for A and B at visit 3 and rerun the same reshape call.

**Why it holds here:** reshape creates one value column per distinct visit, so a third visit becomes value.3, filled by matching on id. Both people have the visit, so the new column has no missing cells.

**Tempting mistake:** Appending a vector straight onto the wide table. Its values land by row position, and the order A then B exists only because of how the input happened to be sorted.

**Verify:** `names(wide)` shows "id" "value.1" "value.2" "value.3" after the reshape.

### Exercise 3

Reverse a complete wide table to long form.

The unique measurement records are recovered under the stated complete-table contract.

**Approach:** Reshape back with varying value.1 and value.2, times 1 and 2, then sort by id and visit, drop row names and compare with all.equal ignoring attributes.

**Why it holds here:** The values return unchanged, but reshape adds row names such as A.1 and a record of the reshape, and lists visit 1 rows first. Sorting and resetting removes those differences, leaving only the data to compare.

**Tempting mistake:** Comparing with `identical(restored, long)`. It returns FALSE because of row names, row order and the attribute, even though every measurement came back correctly.

**Verify:** `isTRUE(all.equal(restored, long, check.attributes = FALSE))` returns TRUE.

### Exercise 4

Diagnose two values for one person/visit.

Reject duplicates or perform an explicitly justified aggregation first.

**Approach:** Check the key before reshaping, then reject the batch or apply a stated aggregation rule to the duplicate pair.

**Why it holds here:** `rbind(long, long[1, ])` adds a second row for A at visit 1. A wide cell can hold one value, so without a rule reshape keeps the first and drops the other.

**Tempting mistake:** Reshaping anyway. The second value disappears with only a warning, so the wide table looks complete while missing a reading.

**Verify:** `anyDuplicated(duplicate[c("id", "visit")])` returns 5, the position of the repeated row.

### Exercise 5

Distinguish an absent visit from an observed NA.

Retain presence metadata when the difference matters.

**Approach:** Carry a presence flag in long form, one TRUE per recorded row, and reshape it alongside the value.

**Why it holds here:** Removing B's visit 2 row leaves value.2 missing for B. A recorded row with value NA would look the same in wide form, so the value alone cannot tell absent from unknown.

**Tempting mistake:** Reading every NA in the wide table as a skipped visit. Some of those cells are recorded measurements whose value is unknown, and the visit counts come out wrong.

**Verify:** `is.na(incomplete_wide$value.2[incomplete_wide$id == "B"])` returns TRUE, and the reshaped flag shows NA for the absent visit and TRUE for a recorded one.

### Exercise 6

Choose a shape for a model or chart.

Document the chosen observation grain and avoid treating reshaping as an implicit aggregation.

**Approach:** Choose the shape from the next operation: wide for a per person difference between visits, long for a chart or model with one row per measurement.

**Why it holds here:** In wide form `value.2 - value.1` is 2 for A and 3 for B in one vectorized line. A chart with visit on the x axis needs visit as a column, which is the long layout.

**Tempting mistake:** Folding an aggregation into the reshape, such as averaging duplicates without saying so, and calling the result the same data.

**Verify:** `wide$value.2 - wide$value.1` returns 2 and 3, and `nrow(long)` returns 4 measurements.

## What the checks establish

The checks confirm that id and visit form a unique key, that reshaping to wide and back restores the original long table apart from attributes, that a duplicated key is detected before reshaping, and that removing B's second visit produces an NA in its `value.2` cell rather than a dropped row. They do not decide whether such an NA should later be imputed.

The reference makes 4 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
