# cuda-086: explained solutions

Compare with your [worksheet](../lessons/cuda-086.md) attempt.

## Exercise 1: Derive fitted means

Means are [2,3].

**Approach.** Compute the column means of `[[1, 2], [3, 4]]`: column 0 averages `(1+3)/2 = 2` and column 1 averages `(2+4)/2 = 3`, so the means are `[2, 3]`.

**Why it is correct here.** Fitting is a reduction along rows for each column. The reference computes `sum(row[c] for row in rows)/len(rows)` per column, giving exactly `[2, 3]`.

**A plausible wrong approach.** Averaging along columns, the per-row means, gives `[1.5, 3.5]` and centers the wrong axis.

**How to verify.** Assert `means == [2, 3]`. On a GPU, `cupy.mean(X, axis=0)` should match after transfer.

## Exercise 2: Score the centered rows

Scores are [-1,1].

**Approach.** Center each row by subtracting the means, giving `[[-1, -1], [1, 1]]`, then score with weights `[2, -1]`: `2*(-1) + (-1)*(-1) = -1` and `2*1 + (-1)*1 = 1`.

**Why it is correct here.** Scoring is a dot product of each centered row with the weights. The reference zips each centered row with the weights and asserts `scores == [-1, 1]`.

**A plausible wrong approach.** Scoring the raw rows gives `[0, 2]`, which skips the fitted transformation.

**How to verify.** Assert the scores in the reference, and check that the GPU version uses the same means array as the training fit.

## Exercise 3: Add a constant column

Center to zero and define scale policy.

**Approach.** Add a constant column such as `[5, 5]`: its mean is 5 and centering produces zeros. State a scale policy, for example leave the column unscaled or drop it, because its standard deviation is 0.

**Why it is correct here.** Centering is well defined for a constant, but dividing by a zero standard deviation produces NaN or infinity.

**A plausible wrong approach.** Dividing by the standard deviation without a check fills the column with NaN, which spreads into the scores.

**How to verify.** Run the pipeline with a constant column and assert the output has no NaN and the column handling matches the stated policy.

## Exercise 4: Draw owners and waits

Include producer and final-consumer lifetimes.

**Approach.** Draw owners and waits: the training array owns the fitted means, the scoring step reads those means and the input batch, and the output buffer must stay alive until the final copy to host completes.

**Why it is correct here.** Each buffer has a producer and a final consumer. Without an explicit wait, the host might read scores before the scoring kernel finishes.

**A plausible wrong approach.** Drawing only the computation steps without owners loses track of when buffers can be freed.

**How to verify.** Annotate each edge with the event or synchronization that orders it, and check that every buffer's release comes after its last consumer.

## Exercise 5: Design train-validation separation

Fit only on the training subset.

**Approach.** Fit the means only on the training subset and reuse those means for validation rows, never recomputing them on the validation data.

**Why it is correct here.** Recomputing means on validation data changes the transformation and leaks information about the evaluation set into preprocessing.

**A plausible wrong approach.** Fitting on the concatenated train and validation data is a subtler leak with the same effect: validation scores look better than they would on truly unseen rows.

**How to verify.** Store the fitted means as an explicit object, then confirm validation centering uses them by testing a validation row with a known expected value.

## Exercise 6: Write the capstone acceptance report

Report values tolerances timing boundaries and unsupported cases.

**Approach.** Write the acceptance report with the computed values, tolerances, the timing method and boundaries such as whether transfers are included, plus unsupported cases like constant columns.

**Why it is correct here.** A capstone result is useful only if a reader can see what was checked and what was not.

**A plausible wrong approach.** Reporting a single speedup number leaves out correctness and the scope of the claim, so readers cannot tell whether transfers were timed or whether the means were reused.

**How to verify.** Check each report field against the pipeline tests. Mark device timings not attempted if no GPU ran.

## Self-check answers

1. **Why establish a CPU oracle before optimizing the pipeline?** It fixes the expected values, so every later backend or optimization can be checked against the same answers and tolerances.

2. **How should a constant feature be handled?** Center it to zero and follow a declared scale policy instead of dividing by a zero standard deviation.

3. **Why report preparation, transfer and computation separately?** Complete latency hides where time goes. Separate stages show whether an optimization helped the computation or merely moved cost elsewhere.

## Reference observation

Fitted means [2,3] and scores [-1,1].

Asserted by `courses/cuda/python/references/cuda-086_cpu.py`.
