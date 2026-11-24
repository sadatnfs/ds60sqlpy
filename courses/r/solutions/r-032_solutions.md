# r-032: reference reasoning

Use the [complete reference](r-032_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The observation mean counts four measurements equally. The equal-group mean gives A and B equal influence despite their unequal sizes.

The declared C category remains visible with zero rows and no observed mean. A missing measurement within A is separately counted.

## Explained practice

### Exercise 1

Reconstruct an overall mean from sums 10,90 and counts 1,3.

The mean is 25.

**Approach:** Add the sums and the counts separately, then divide: 10 plus 90 is 100, over 1 plus 3 counts, which is 4.

**Why it holds here:** The overall mean weights each observation once. B's three values carry three times the weight of A's single value, and dividing total by total does exactly that, giving 25.

**Tempting mistake:** Averaging the group means 10 and 30 to get 20. That gives A's one value the same weight as B's three and answers a different question about groups, not observations.

**Verify:** `sum(sums) / sum(counts)` returns 25, while `mean(sums / counts)` returns 20.

### Exercise 2

Add another observation 50 to B.

Overall sum 150, count 5, mean 30.

**Approach:** Append 50 to B, then update B's sum to 140 and its count to 4 together.

**Why it holds here:** The overall sum becomes 150 over 5 observations, so the mean is 30. Recomputing from `unlist(groups)` gives the same answer, which confirms the state was updated consistently.

**Tempting mistake:** Updating the sum without the count, giving 150 over 4, which is 37.5. Averaging the old overall mean 25 with the new value 50 gives the same wrong 37.5.

**Verify:** `sum(unlist(groups)) / length(unlist(groups))` returns 30.

### Exercise 3

Return rows, observed, missing, sum and mean per group.

An all-missing group has observed 0 and an explicitly missing mean.

**Approach:** Return rows, observed, missing, sum and mean for each group, with mean NA when nothing is observed.

**Why it holds here:** For `c(NA_real_, NA_real_)` the function reports rows 2, observed 0, missing 2 and sum 0. A sum of 0 over no values is still correct for merging, but a mean is undefined, so the guard returns NA.

**Tempting mistake:** Using `mean(x, na.rm = TRUE)` without a guard. On an all missing group it returns NaN, and dropping the denominators leaves no way to tell that the mean rests on nothing.

**Verify:** `summarize(c(NA_real_, NA_real_))[["observed"]]` returns 0, and `summarize(numeric(0))[["mean"]]` returns NA.

### Exercise 4

Diagnose summing distinct-customer counts across overlapping groups.

Deduplicate the intended union or preserve an exact mergeable set/sketch contract.

**Approach:** Take the distinct count of the union, `length(unique(c(a, b)))`, or keep the id sets so they can be merged later.

**Why it holds here:** Group a holds U1 and U2, and group b holds U2 and U3. U2 is in both, so the union has 3 customers. Distinct counts are not additive when groups overlap.

**Tempting mistake:** Adding the per group distinct counts, 2 plus 2. That reports 4 customers and counts U2 twice; the error grows with the overlap.

**Verify:** `length(unique(c(a, b)))` returns 3, while the sum of the two distinct counts returns 4.

### Exercise 5

Retain a category with no observations.

Report zero rows separately from all-missing measured rows.

**Approach:** Declare the group universe with factor levels, split with `drop = FALSE`, and report rows 0 for a level with no records.

**Why it holds here:** Level C has no data in the example, yet it appears in the result with rows 0, observed 0 and mean NA. That differs from an all missing group, which has rows above 0 and observed 0.

**Tempting mistake:** Splitting a character vector or passing `drop = TRUE`. C vanishes from the output, so a reader cannot tell an empty category from one that does not exist.

**Verify:** `summary$C[["rows"]]` returns 0, and `is.na(summary$C[["mean"]])` returns TRUE.

### Exercise 6

Explain why group medians cannot be averaged into an overall median.

Retain the necessary distribution state or recompute from admitted observations.

**Approach:** Recompute the median from the combined observations, or keep enough state such as the sorted values or a full count table.

**Why it holds here:** Group medians are 0 and 100.5. The pooled values 0, 100 and 101 have median 100, which depends on where each value sits in the combined order, information a single median per group discards.

**Tempting mistake:** Averaging the group medians to get 50.25. The result lies in the gap between groups, where no observation exists.

**Verify:** `median(c(0, 100, 101))` returns 100, while the mean of the group medians returns 50.25.

## What the checks establish

The reference makes 5 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
