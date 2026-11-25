# r-035: reference reasoning

Run the [complete reference](r-035_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The negative and missing amounts remain distinct original inputs, even though both violate the same finite-nonnegative amount rule.

The validator does not silently rename an unexpected field or guess that value must mean amount. Structural drift gets an explicit failure.

## Explained practice

### Exercise 1

Count admitted records in the first example.

Only A is admitted.

**Approach:** Evaluate both rules for every row and admit only rows where neither flag is TRUE.

**Why it holds here:** A has a nonempty id and amount 2. The second row has an empty id, C has amount -1, and D has NA, which fails is.finite. That leaves only A, so the mask is TRUE, FALSE, FALSE, FALSE.

**Tempting mistake:** Filtering with `raw[raw$amount >= 0, ]`. It keeps the empty id row, which has a valid amount, and returns an extra row of NA for D.

**Verify:** `identical(admitted, c(TRUE, FALSE, FALSE, FALSE))` returns TRUE, and `sum(admitted)` returns 1.

### Exercise 2

Make the empty-ID row also have a negative amount.

The row has both missing_id and invalid_amount flags.

**Approach:** Keep each rule in its own logical column, computed independently, so a row can carry several reasons.

**Why it holds here:** With amount -3, the empty id row fails both rules. The reference input does exactly that, and its first rejected row shows TRUE under missing_id and TRUE under invalid_amount.

**Tempting mistake:** Recording a single reason from an if and else chain where the first failing rule wins. The row would list only the missing id, so after that fix the resubmitted record would be rejected again for its amount.

**Verify:** `result$rejected$missing_id[[1]]` and `result$rejected$invalid_amount[[1]]` both return TRUE.

### Exercise 3

Return admitted and quarantined tables with stable IDs.

Their counts reconcile to the input count.

**Approach:** Build both tables from one mask, `data[keep, ]` and `data[!keep, ]`, and attach the flags to the rejected rows.

**Why it holds here:** One mask makes the two sets disjoint and complete: 1 admitted plus 3 rejected equals 4 input rows. The row names 2, 3 and 4 tie each rejection back to its position, which matters for the row with no id.

**Tempting mistake:** Writing the rejected condition separately, for example `data[data$amount < 0, ]`. It misses D and the empty id row, so the counts no longer add up to 4.

**Verify:** `nrow(result$admitted) + nrow(result$rejected) == nrow(raw)` returns TRUE.

### Exercise 4

Diagnose replacing every invalid numeric parse with zero.

Preserve a parse-failure signal and apply an explicit admission policy.

**Approach:** Keep a parse failure flag next to the parsed value and treat it as a rejection reason under an explicit policy.

**Why it holds here:** A zero would pass this lesson's `amount < 0` rule, so a value that could not be read would be admitted as a real measurement and lower every total it enters.

**Tempting mistake:** Replacing every NA from as.numeric with 0. Blank fields and malformed text both become valid looking zeros, and the original problem is no longer visible anywhere.

**Verify:** In the worked example, `parse_failed` returns TRUE only for the text 1,5, and the admitted mean returns 9.75.

### Exercise 5

Validate a zero-row table with the correct schema.

An empty but correctly typed batch can be admitted under a stated empty-batch policy.

**Approach:** Run the full schema check on a zero row batch, then admit it if the empty batch policy allows empty days.

**Why it holds here:** `raw[integer(0), , drop = FALSE]` keeps id as character and amount as numeric, so the type checks pass and both tables are empty. Schema validity and row validity are separate questions.

**Tempting mistake:** Skipping validation when `nrow(data) == 0`. A broken export that yields zero rows with amount read as character would pass, and the type problem would surface on a later, nonempty day.

**Verify:** `nrow(empty$admitted)` and `nrow(empty$rejected)` both return 0.

### Exercise 6

Explain what local validation cannot prove.

Range and schema checks do not establish representativeness, causality, freshness or measurement accuracy.

**Approach:** Report the admitted row as passing these rules, and list separately what the rules do not check.

**Why it holds here:** A with amount 2 passes both checks, but nothing here tests the currency, whether A was already loaded yesterday, how recent the batch is, or whether the stores in it represent all stores.

**Tempting mistake:** Labeling the admitted table as correct data. The rules only show that ids are present and amounts are finite and nonnegative.

**Verify:** The rejected table shows a reason for each of its three rows; no column in result shows freshness, duplication across batches or measurement accuracy.

## What the checks establish

The assertions confirm the required columns and types, one admitted row and three rejected rows for this input, rejection flags for a missing id and an invalid amount, that admitted plus rejected rows always equal the input row count, and that an empty input yields two empty tables. They do not test inputs with unexpected extra columns or text in the amount column.

The reference makes 5 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
