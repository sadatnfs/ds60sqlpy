# r-036: reference reasoning

Run the [complete reference](r-036_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The two chunks have unequal sizes. Sufficient totals reconstruct the observation mean while averaging the two chunk means changes the weighting.

Each input entry contributes to either observed or missing count. The total uses only observed measurements under the declared policy.

## Explained practice

### Exercise 1

Reconstruct a mean from count 4, total 100.

The mean is 25.

**Approach:** Divide the merged total by the merged count once: 100 over 4.

**Why it holds here:** The chunks hold 10, and 20, 30 and 40. Their counts and sums add to 4 and 100, so the mean is 25, the same as averaging all four values at once.

**Tempting mistake:** Averaging the chunk means 10 and 30 to get 20. The single value chunk counts as much as the three value chunk.

**Verify:** `a$mean` returns 25, while `mean(c(10, 30))` returns 20.

### Exercise 2

Change chunk boundaries without changing observations.

The semantic total/count remain unchanged, subject to floating-point tolerance.

**Approach:** Split the same four values differently, including an empty chunk, and compare the results.

**Why it holds here:** a uses 10 and then 20, 30, 40; b uses 10, 20, then nothing, then 30, 40. The state only adds counts and sums, so both reach count 4, missing 0 and total 100. These values are integers, so the comparison can be exact.

**Tempting mistake:** Using identical on fractional measurements. Grouping 0.1 and 0.2 apart from 0.3 can change the last bit of the total, so a correct implementation would fail; such data need all.equal.

**Verify:** `identical(a, b)` returns TRUE, and both `a$mean` and `b$mean` return 25.

### Exercise 3

Implement an all-missing finalization rule.

Return an explicit missing mean when count is zero.

**Approach:** Check the observed count before dividing, and return NA_real_ when it is 0.

**Why it holds here:** For three missing values, observed is 0, missing is 3 and total is 0. A mean over no observations does not exist, and the missing count shows why.

**Tempting mistake:** Dividing without the check. 0 divided by 0 returns NaN, which passes downstream as a number and hides that every value was missing.

**Verify:** `is.na(missing$mean)` returns TRUE, and `missing$state[["missing"]]` returns 3.

### Exercise 4

Diagnose averaging chunk medians.

Keep sufficient distribution state or recompute the exact combined median.

**Approach:** Keep the values needed for the exact median, or count each distinct value across chunks, or make a second pass over the data.

**Why it holds here:** For a's chunks the medians are 10 and 30, which average to 20. The four values 10, 20, 30 and 40 have median 25. With b's boundaries the chunk medians 15 and 35 happen to average to 25, so the method can look right on one split and be wrong on another.

**Tempting mistake:** Averaging chunk medians. A median depends on where each value sits in the combined order, and one number per chunk loses that.

**Verify:** `median(c(10, 20, 30, 40))` returns 25, while `mean(c(10, 30))` returns 20.

### Exercise 5

Process an empty chunk among nonempty chunks.

It leaves the accumulated state unchanged.

**Approach:** Let the loop add the empty chunk's zero count, zero missing and zero total.

**Why it holds here:** For `numeric(0)`, valid is `logical(0)`, both sums are 0, and the sum of no values is 0. The state is unchanged, which is why b, which contains an empty chunk, still matches a.

**Tempting mistake:** Computing a mean per chunk before merging. `mean(numeric(0))` is NaN, and adding NaN to the state turns the final result into NaN as well.

**Verify:** `identical(a, b)` returns TRUE although b includes an empty chunk.

### Exercise 6

State what a scalability claim still requires.

Measure representative peak memory, elapsed work and equivalent outputs under controlled conditions.

**Approach:** State that the reference checks arithmetic equivalence only, and name what a scalability claim needs: a disk reader, realistic sizes, peak memory and timing.

**Why it holds here:** Here all chunks already sit in one R list, so memory is the same as for a single vector. Only a streamed source shows the benefit of keeping three numbers of state.

**Tempting mistake:** Claiming the function handles data larger than memory because it loops over chunks. The loop proves the merge is correct, not that the data were never fully loaded.

**Verify:** A run on a file many chunks long shows the same mean as an in memory calculation, with peak memory measured by a process monitor.

## What the checks establish

The checks confirm a final mean of 25 that does not depend on chunk order, an NA mean with three missing values when every observation is missing, and a mean of 3 from three observed values in another stream. They show that the combination rule is correct, not that chunking reduced memory use, which would need separate measurement.

The reference makes 3 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
