# cuda-121: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Calculate duplicate join output

Multiply key multiplicities.

**Approach.** Calculate duplicate join output by multiplying key multiplicities: A appears twice on each side, so the inner join produces `2*2 = 4` rows for A.

**Why it is correct here.** Each left row with key A pairs with each right row with key A. Duplicates multiply rather than add.

**A plausible wrong approach.** Expecting the output size to be at most the smaller input underestimates joins with duplicate keys, which can grow much larger than either input.

**How to verify.** The reference asserts four joined rows, all with key A. Compute the per-key product before running large joins.

## Exercise 2: Add unmatched keys

Inner joins exclude unmatched keys while outer joins preserve defined null rows.

**Approach.** Add unmatched keys: B on the left and C on the right have no partners, so an inner join drops them, while a full outer join keeps each with nulls on the other side.

**Why it is correct here.** Join type defines what happens to unmatched rows. The outer join here would return six rows.

**A plausible wrong approach.** Using an inner join where unmatched records must be preserved silently drops them. Downstream totals then shrink without any error, which is harder to detect than a failure.

**How to verify.** Run inner, left and full outer joins on this fixture and count rows: 4, 5 and 6.

## Exercise 3: Identify skew

Compare maximum and distribution not average alone.

**Approach.** Identify skew by comparing the maximum partition with the distribution: one partition of 900 rows beside nine of about 11 has a small average but one task dominates.

**Why it is correct here.** Stage time is set by the slowest task. The maximum matters more than the mean for wall time.

**A plausible wrong approach.** Reporting the average partition size of about 100 rows hides the 900-row partition.

**How to verify.** Report maximum, median and percentiles of task durations or input sizes for the join stage.

## Exercise 4: Compare broadcast and shuffle

Broadcast replicates one side and shuffle redistributes both as needed.

**Approach.** Compare broadcast and shuffle joins: a broadcast join copies the small side to every executor, while a shuffle join redistributes both sides by key.

**Why it is correct here.** Broadcast avoids shuffling the large side but requires the small side to fit in memory on every executor.

**A plausible wrong approach.** Broadcasting a table that is large after a filter misestimate can exhaust executor memory. The driver also collects the broadcast side before sending it, so a too-large table can fail on the driver first.

**How to verify.** Check the size estimate and the chosen strategy in the executed plan. Compare the estimated size with the actual rows read for the small side, to see whether the threshold decision was based on accurate statistics.

## Exercise 5: Design a safe rewrite

Preserve duplicates and null-key semantics.

**Approach.** Design a safe skew rewrite, such as salting a hot key, that preserves duplicates and null-key semantics.

**Why it is correct here.** Salting splits a hot key across partitions and must reunite the rows so the join output is the same. The other side's rows for that key are replicated across every salt value, so each salted left row still meets every matching right row.

**A plausible wrong approach.** Dropping null keys or deduplicating to reduce skew changes results. Salting only one side without replicating the other loses matches, which reduces output silently rather than raising an error.

**How to verify.** Compare the rewritten join output with the original on the fixture, including duplicates and nulls. Then compare the maximum task duration before and after, which is the quantity the rewrite targeted.

## Exercise 6: Inspect final AQE decision

Capture executed plan after action.

**Approach.** Inspect the final AQE decision after the action, since adaptive execution may switch to a broadcast join or split skewed partitions at runtime.

**Why it is correct here.** AQE uses statistics from completed stages, so the executed plan may differ from the initial one.

**A plausible wrong approach.** Citing the pre-execution plan reports a strategy that may not have run. Skew handling in particular appears only in the final plan, so the initial plan cannot show whether a skewed partition was split.

**How to verify.** Compare the initial explain output with the final plan in the SQL tab. Record the AQE settings with the plan, since disabling adaptive execution changes which plan runs.

## Reference observation

Four A matches from two-by-two duplicate keys.

The reference file is `courses/cuda/spark/references/cuda-121_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
