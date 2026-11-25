# cuda-121: Joins, skew and broadcast decisions

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-117`, `cuda-120`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Calculate duplicate join output.
- Add unmatched keys.
- Identify skew.
- Compare broadcast and shuffle.
- Design a safe rewrite.
- Inspect final AQE decision.

## Mechanism and vocabulary

A join matches keys across relations; duplicate keys multiply output rows. GPU acceleration cannot remove that semantic expansion. A broadcast join replicates a small side to workers, while a shuffle join redistributes records by key. Choice depends on estimated sizes, runtime statistics, supported operators and memory. Broadcasting a relation that only appears small in stale statistics can cause pressure.

Skew concentrates rows on a few keys, creating large partitions and long tasks. Salting or repartitioning is not automatically correct: a transformation must preserve intended join multiplicity and outer-join behavior. Inspect partition sizes, output cardinality and the final adaptive plan. Keep one simple CPU oracle with duplicate and missing keys to prevent a fast but incorrect rewrite.

## Derive join cardinality before tuning it

For an inner equijoin, let \(l_k\) be the number of left records for key \(k\) and \(r_k\) the number on the right. Output cardinality is:

\[
\sum_k l_k r_k.
\]

This explains why duplicate dimension keys can unexpectedly multiply a fact table. A GPU cannot optimize away required output rows. If the application assumes a unique dimension key, validate uniqueness as an input contract. Applying `distinct` after the join is not a general repair because it can erase legitimate duplicate facts.

Broadcast avoids redistributing the large side by replicating a suitably small side, but each executor must accommodate that replicated structure and the join's live state. A shuffle join moves records to key owners. Skew can make one key dominate both memory and runtime. Inspect maximum and percentile partition sizes, not only average rows per partition.

AQE may change the chosen join using observed statistics. Record the final executed plan and compare output multiplicity before and after any rewrite. Salting a hot key requires careful duplication or redistribution of the matching side and a proof that every intended pair appears once. Outer joins add unmatched-row/null behavior, making an informal salting recipe particularly risky. Start with the tiny duplicate-key oracle, then expand only after exact semantic parity.


### Key terms

- **Broadcast join:** A join that replicates the small side to every worker so the large side is not redistributed.
- **Shuffle join:** A join that redistributes both sides by key so matching keys meet in the same task.
- **Key skew:** Concentration of rows on a few keys, creating oversized partitions and long tasks.
- **Duplicate key expansion:** Output growth when duplicate keys on both sides multiply into many matched rows.

## Worked examples

### Worked example 1

Left keys [A, A, B] and right keys [A, A, C] produce four matches for A in an inner join. Expected cardinality is not the minimum of input lengths.

### Worked example 2

If one partition holds 900 rows and nine others hold roughly 11, the maximum task dominates the barrier despite a small average partition size.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-121_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-121_cpu.py
```

```python
left = [("A", 1), ("A", 2), ("B", 3)]
right = [("A", 10), ("A", 20), ("C", 30)]
joined = [(k, a, b) for k, a in left for r, b in right if k == r]
assert len(joined) == 4
assert {k for k, _, _ in joined} == {"A"}
print("CPU join oracle:", joined)
```

**Expected observation:** Four A matches from two-by-two duplicate keys.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `left` | `[('A', 1), ('A', 2), ('B', 3)]` |
| `right` | `[('A', 10), ('A', 20), ('C', 30)]` |
| `joined` | `[('A', 1, 10), ('A', 1, 20), ('A', 2, 10), ('A', 2, 20)]` |

## Scala and PySpark parity lab

Both CPU variants assert one expected result. Read the [parity rules](../../STUDY-GUIDE.md#spark-parity-and-gpu-spark).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-121.md) before opening hints.

### Exercise 1: Calculate duplicate join output

**Trap to avoid:** Expecting the output size to be at most the smaller input underestimates joins with duplicate keys, which can grow much larger than either input.

### Exercise 2: Add unmatched keys

**Trap to avoid:** Using an inner join where unmatched records must be preserved silently drops them. Downstream totals then shrink without any error, which is harder to detect than a failure.

### Exercise 3: Identify skew

**Trap to avoid:** Reporting the average partition size of about 100 rows hides the 900-row partition.

### Exercise 4: Compare broadcast and shuffle

**Trap to avoid:** Broadcasting a table that is large after a filter misestimate can exhaust executor memory. The driver also collects the broadcast side before sending it, so a too-large table can fail on the driver first.

### Exercise 5: Design a safe rewrite

**Trap to avoid:** Dropping null keys or deduplicating to reduce skew changes results. Salting only one side without replicating the other loses matches, which reduces output silently rather than raising an error.

### Exercise 6: Inspect final AQE decision

**Trap to avoid:** Citing the pre-execution plan reports a strategy that may not have run. Skew handling in particular appears only in the final plan, so the initial plan cannot show whether a skewed partition was split.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Multiply how many times a key appears on the left by how many times it appears on the right.
2. Decide what each join type does with a key that appears on only one side.
3. Compare the largest partition with the typical ones, not only the average size.
4. Ask which strategy copies one side to every worker and which redistributes records by key.
5. Check that a salted or repartitioned version returns the same duplicates and null-key rows as the CPU oracle.
6. Run an action and read the final adaptive plan to see which join strategy actually ran.

## Common mistakes and self-check

A common mistake is expecting a join's output to be at most as large as its inputs. Duplicate keys multiply: two A rows on each side produce four matches. Another is broadcasting a side that looks small only because statistics are stale, or salting skewed keys in a way that changes multiplicity or outer-join rows. Fix both by checking cardinality against a CPU oracle with duplicate and missing keys, and by inspecting partition sizes and the final executed plan.

**Evidence limit:** The reference counts four A matches from two-by-two duplicate keys. It does not execute Spark joins, so broadcast choices, skew handling and memory pressure need the final adaptive plan from a real run.

1. Can GPU acceleration reduce a join's output rows?
2. Why does skew lengthen a stage?
3. Why keep a simple CPU oracle for joins?

Answers: [self-check answers](../solutions/cuda-121_solutions.md#self-check-answers).

## Primary references

- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-121: Joins, skew and broadcast decisions.
Read courses/cuda/spark/guides/cuda-121.md and courses/cuda/spark/lessons/cuda-121.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
