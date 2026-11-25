# cuda-117: Nulls, decimals, timestamps and equality contracts

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-116`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Calculate both counts.
- Handle all-null aggregate.
- Compare decimal values.
- Name timestamp timezone.
- Choose float tolerances.
- Design ordered result comparison.

## Mechanism and vocabulary

SQL semantics include null propagation, three-valued predicates, decimal precision/scale, overflow policy, timezone interpretation and string ordering. GPU and CPU results should be compared under the query's declared semantics, not by assuming every numeric column is a floating array. An empty aggregate and an aggregate of only null values can differ from a sum initialized to zero in Python.

Use explicit schemas and deterministic ordering for comparison. Floating aggregates may require a justified tolerance because reduction order can change; decimal and integer outputs often require exact equality under the selected SQL mode. Timestamp tests should name the session timezone and include boundary cases. Never hide a semantic mismatch by relaxing tolerance until the test passes.



### Key terms

- **Three-valued logic:** SQL predicate logic in which a comparison can be true, false or unknown when a null is involved.
- **Null propagation:** The rule that most expressions with a null input return null.
- **Decimal precision and scale:** The total digits and the digits after the decimal point that a decimal type can hold, which govern rounding and overflow.
- **Session time zone:** The time zone Spark uses to interpret and display timestamps, which must match for results to compare.

## Worked examples

### Worked example 1

COUNT(*) over [2, null, 5] is 3 while COUNT(value) is 2. SUM(value) is 7 under skip-null semantics. The two counts answer different questions.

### Worked example 2

Decimal 1.10 plus 2.20 should preserve the chosen decimal contract. A binary floating approximation is not a substitute for testing a decimal expression.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-117_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-117_cpu.py
```

```python
from decimal import Decimal

values = [2, None, 5]
assert len(values) == 3
assert sum(v is not None for v in values) == 2
assert sum(v for v in values if v is not None) == 7
assert Decimal("1.10") + Decimal("2.20") == Decimal("3.30")
print("CPU SQL-semantics oracle: rows 3, nonnull 2, sum 7, decimal 3.30")
```

**Expected observation:** Rows 3, non-null 2, sum 7 and exact decimal 3.30.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `values` | `[2, None, 5]` |

## Scala and PySpark parity lab

Both CPU variants assert one expected result. Read the [parity rules](../../STUDY-GUIDE.md#spark-parity-and-gpu-spark).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-117.md) before opening hints.

### Exercise 1: Calculate both counts

**Trap to avoid:** Treating null as zero gives the same sum but makes `COUNT(value)` 3 and the average 7/3 instead of 3.5, which disagrees with Spark.

### Exercise 2: Handle all-null aggregate

**Trap to avoid:** Returning 0 for the sum of an all-null group makes a group with no data look like a group whose values cancel out.

### Exercise 3: Compare decimal values

**Trap to avoid:** Using float64 for the same values gives `3.3000000000000003`, which fails an exact comparison and suggests a bug that exists only in the test.

### Exercise 4: Name timestamp timezone

**Trap to avoid:** Relying on the machine's default timezone gives results that depend on where the job runs. Executors and the driver may also disagree, producing values that differ between stages of one job.

### Exercise 5: Choose float tolerances

**Trap to avoid:** Using exact equality for float sums fails on correct results, while using a very loose tolerance passes wrong ones.

### Exercise 6: Design ordered result comparison

**Trap to avoid:** Converting results to sets before comparing removes duplicates and hides a missing or extra row.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Count all rows for one answer and only the rows where the value is present for the other.
2. Look up what Spark SQL returns for a sum over values that are all null, then compare it with a Python sum starting at zero.
3. Represent both operands as decimals with the declared scale and compare the result exactly.
4. Set the session timezone explicitly and include values near a day or offset boundary.
5. Base the tolerance on the dtype, the reduction algorithm and the magnitude of the values.
6. Sort both result sets by stable keys before comparing, and keep duplicate rows instead of removing them.

## Common mistakes and self-check

A common mistake is comparing CPU and GPU results as if every column were a float array. Decimal and integer results usually need exact equality, an all-null sum is null rather than zero, and timestamps depend on the session timezone. Another is widening a tolerance until a semantic mismatch passes. Fix both by using explicit schemas, deterministic ordering and exact comparison for decimals, reserving justified tolerances for floating aggregates whose reduction order can change.

**Misconception:** Results from CPU Spark and the GPU plugin can always be compared exactly. **Correction:** The plugin documents operations whose GPU results can differ from CPU Spark, such as floating aggregations whose order varies, and some of them are disabled by default for that reason. Read the compatibility notes for each operation in the query, compare decimals and integers exactly and compare floats with a justified tolerance.

**Evidence limit:** The reference computes row count 3, non-null count 2, sum 7 and the exact decimal 3.30 in Python. It does not run Spark SQL, so null, overflow and timezone behavior must be confirmed against the selected Spark mode and plugin release.

1. How do COUNT(*) and COUNT(value) differ?
2. Why can a binary float not stand in for a decimal test?
3. Why name the timezone in a timestamp test?

Answers: [self-check answers](../solutions/cuda-117_solutions.md#self-check-answers).

## Primary references

- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-117: Nulls, decimals, timestamps and equality contracts.
Read courses/cuda/spark/guides/cuda-117.md and courses/cuda/spark/lessons/cuda-117.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
