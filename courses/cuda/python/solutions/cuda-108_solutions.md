# cuda-108: explained solutions

Compare with your [worksheet](../lessons/cuda-108.md) attempt.

## Exercise 1: Compute grouped sums

Ignore null only under the stated aggregate contract.

**Approach.** Group `[(A, 2), (A, null), (B, 5)]` with the skip-null sum rule: A totals 2 and B totals 5, while A has a row count of 2.

**Why it is correct here.** Under the declared contract, nulls do not contribute to the sum but the row still exists. Sum and row count therefore answer different questions about group A.

**A plausible wrong approach.** Treating the null as an error and dropping group A entirely, or failing the whole aggregation, contradicts the stated skip-null rule.

**How to verify.** The reference asserts `totals == {'A': 2, 'B': 5}` and `counts['A'] == 2`. Compare with a cuDF or pandas `groupby` sum and size on the same rows.

## Exercise 2: Distinguish null and zero

Zero contributes a numeric value.

**Approach.** Distinguish null from zero: a null value means unknown and is skipped by the sum, while a zero is a real value that contributes 0 and counts as non-null.

**Why it is correct here.** The difference matters for means and non-null counts. Group A has mean 2 over one non-null value, but filling the null with 0 gives a mean of 1.

**A plausible wrong approach.** Filling nulls with zero before aggregation silently changes averages and counts, which then disagree with reports computed by a SQL engine that skips nulls.

**How to verify.** Compute `count` and `mean` for group A with and without filling, and confirm the skip-null version gives count 1 and mean 2.

## Exercise 3: Define category mapping

Fit once and reserve an unknown category if needed.

**Approach.** Define the category mapping once on training data, such as A to 0 and B to 1, and reserve a code for unknown categories such as C.

**Why it is correct here.** Model features depend on consistent codes. A mapping fitted once and reused gives every partition and later batch the same meaning for each code.

**A plausible wrong approach.** Fitting category codes independently in each partition assigns code 0 to whatever category appears first there, so the same code means different things to the model.

**How to verify.** Encode two partitions with the saved mapping and assert A has the same code in both, and that C maps to the unknown code.

## Exercise 4: Preserve row identity

Carry a stable key through transformations.

**Approach.** Preserve row identity by carrying a stable key column through filtering, joins and conversions, so outputs can be matched back to inputs.

**Why it is correct here.** GPU dataframe operations may reorder rows, for example in hash joins or group operations. A key column allows correct alignment without relying on position.

**A plausible wrong approach.** Matching rows by position after a join or a GPU to CPU conversion can attach predictions to the wrong records.

**How to verify.** Shuffle input rows, run the pipeline and join results on the key, then check each output matches its input.

## Exercise 5: Count conversion bytes

Count masks dtype conversions and host-device copies.

**Approach.** Count conversion bytes: moving a column to the GPU moves its values plus a null mask, and dtype conversions such as int64 to float32 or object strings to device strings create extra buffers.

**Why it is correct here.** Transfer and conversion costs can exceed the computation for small operations, so the ledger shows whether staying on the device is worthwhile.

**A plausible wrong approach.** Counting only the numeric values misses null masks, string offsets and temporary converted copies.

**How to verify.** Compute expected bytes for a column of known length and dtype, then compare with the device memory reported after transfer.

## Exercise 6: Distinguish cuDF from Spark acceleration

One is a dataframe library and the other integrates Spark physical execution.

**Approach.** Distinguish cuDF, a dataframe library with a pandas-like API on the GPU, from the RAPIDS Accelerator for Spark, which replaces Spark physical operators with GPU implementations.

**Why it is correct here.** cuDF code calls GPU operations directly, while Spark acceleration keeps Spark's API and planner and changes how the plan executes, falling back to CPU for unsupported operators.

**A plausible wrong approach.** Assuming a Spark job uses the GPU because cuDF is installed confuses a library with a plugin that needs its own configuration.

**How to verify.** For Spark, inspect the physical plan for GPU operators. For cuDF, check that the objects are cuDF dataframes.

## Self-check answers

1. **How does cuDF differ from the Spark RAPIDS plugin?** cuDF is a single-process GPU dataframe library; the plugin replaces supported Spark physical operators inside Spark's scheduler.

2. **Why are counting rows and counting non-null values different?** Category A has two rows but only one non-null value, so the two counts answer different questions.

3. **Why carry row identity through conversion to tensors?** Without a stable key you cannot join predictions back to inputs or verify that no rows were dropped or reordered.

## Reference observation

Grouped sums A 2, B 5 and row count A 2.

Asserted by `courses/cuda/python/references/cuda-108_cpu.py`.
