# cuda-108: Accelerator-aware data science pipelines

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-068`, `cuda-081`, `cuda-085`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute grouped sums.
- Distinguish null and zero.
- Define category mapping.
- Preserve row identity.
- Count conversion bytes.
- Distinguish cuDF from Spark acceleration.

## Mechanism and vocabulary

Tabular acceleration connects schemas, null masks, columnar storage, preprocessing and model inputs. RAPIDS cuDF provides GPU dataframe operations; it is not the Spark scheduling engine. A single-process cuDF pipeline differs from the cuDF plugin that replaces supported Spark physical operators. Both require compatible NVIDIA execution for their GPU paths, and both can spend time moving data across boundaries.

Preserve null semantics, category mappings and row identity when converting a dataframe into dense tensors. A missing value is not always a NaN, and an integer nullable column may require a validity mask. Fit encoders on training data and define unknown-category behavior. Compare with a CPU dataframe or simple Python oracle before measuring. The Spark specialization follows this chapter for distributed plans, resource scheduling and operations.



### Key terms

- **cuDF:** A GPU dataframe library from RAPIDS with a pandas-like API and columnar storage.
- **Validity mask:** A per-column bitmap that marks which entries are null.
- **Columnar storage:** Storing each column contiguously so vectorized operations read only the columns they need.
- **Category mapping:** The table that maps categorical codes to labels, which must match between data sets for codes to mean the same thing.
- **Row identity:** A stable key that tracks each record through joins, filters and sorts.

## Worked examples

### Worked example 1

Rows [(A,2),(A, null),(B,5)] grouped by category have non-null sums A=2 and B=5 under the declared skip-null rule. Counting rows and counting non-null values are different.

### Worked example 2

Encoding categories A->0, B->1 then seeing C requires an explicit unknown policy. Relearning category IDs independently in another partition can corrupt model features.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-108_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-108_cpu.py
```

```python
rows = [("A", 2), ("A", None), ("B", 5)]
totals = {}
counts = {}
for key, value in rows:
    totals.setdefault(key, 0)
    counts[key] = counts.get(key, 0) + 1
    if value is not None:
        totals[key] += value
assert totals == {"A": 2, "B": 5} and counts["A"] == 2
print("CPU dataframe oracle:", totals, counts)
```

**Expected observation:** Grouped sums A 2, B 5 and row count A 2.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `rows` | `[('A', 2), ('A', None), ('B', 5)]` |
| `totals` | `{'A': 2, 'B': 5}` |
| `counts` | `{'A': 2, 'B': 1}` |
| `key` | `'B'` |
| `value` | `5` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-108.md) before opening hints.

### Exercise 1: Compute grouped sums

**Trap to avoid:** Treating the null as an error and dropping group A entirely, or failing the whole aggregation, contradicts the stated skip-null rule.

### Exercise 2: Distinguish null and zero

**Trap to avoid:** Filling nulls with zero before aggregation silently changes averages and counts, which then disagree with reports computed by a SQL engine that skips nulls.

### Exercise 3: Define category mapping

**Trap to avoid:** Fitting category codes independently in each partition assigns code 0 to whatever category appears first there, so the same code means different things to the model.

### Exercise 4: Preserve row identity

**Trap to avoid:** Matching rows by position after a join or a GPU to CPU conversion can attach predictions to the wrong records.

### Exercise 5: Count conversion bytes

**Trap to avoid:** Counting only the numeric values misses null masks, string offsets and temporary converted copies.

### Exercise 6: Distinguish cuDF from Spark acceleration

**Trap to avoid:** Assuming a Spark job uses the GPU because cuDF is installed confuses a library with a plugin that needs its own configuration.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Group rows by category and add only the non-null values under the declared rule.
2. Compare how a zero and a missing value affect a sum and a count.
3. Fit the category-to-integer mapping on training data once, and decide where an unseen category goes.
4. Carry a stable key column through every step, so each output row can be traced to its input.
5. Add the value bytes, the validity masks and every host-device copy made during conversion.
6. Ask which one schedules distributed work and which one runs dataframe operations in one process.

## Common mistakes and self-check

A common mistake is turning a missing value into zero or NaN without stating the rule. Zero changes sums and means, and a nullable integer column cannot hold NaN without a type change. Another is fitting category codes separately per partition, so the same category gets different features. Fix both by keeping validity masks, fitting encoders once on training data with an explicit unknown category and checking results against a CPU dataframe before measuring.

**Misconception:** Using cuDF in a single process is the same as running the Spark plugin, just without a cluster. **Correction:** cuDF is a dataframe library that executes operations directly in one process. The Spark plugin replaces supported physical operators inside Spark's scheduler, with Spark's planning, partitioning, shuffles and fallback rules. Results, supported operations and performance must be checked separately for each path against the same CPU dataframe oracle.

**Evidence limit:** The reference computes sums A 2 and B 5 and a row count of 2 for A in Python. It does not run cuDF or the Spark plugin, so GPU null handling, conversion cost and supported operators need compatible NVIDIA execution.

1. How does cuDF differ from the Spark RAPIDS plugin?
2. Why are counting rows and counting non-null values different?
3. Why carry row identity through conversion to tensors?

Answers: [self-check answers](../solutions/cuda-108_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-108: Accelerator-aware data science pipelines.
Read courses/cuda/python/guides/cuda-108.md and courses/cuda/python/lessons/cuda-108.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
