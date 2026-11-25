# cuda-127: Capstone: the same analytical pipeline in Scala and PySpark

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-117`, `cuda-121`, `cuda-123`, `cuda-124`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Derive expected revenue.
- Write Scala expressions.
- Write PySpark expressions.
- Test duplicate dimension keys.
- Capture executed GPU evidence.
- Prepare a balanced capstone report.

## Mechanism and vocabulary

Build a bounded ETL pipeline with an explicit schema, null handling, a join, a derived column and a grouped metric. Provide Scala and PySpark implementations using equivalent declarative expressions. Use a CPU oracle for exact expected output, then run both ordinary Spark implementations. Only after semantic agreement should a separately prepared GPU Spark environment be compared.

The GPU report includes exact compatibility matrix, initial and executed plans, unsupported-operation reasons, resource assignment, task concurrency, memory/spill observations and complete timing. Keep query text and input identity unchanged across backends unless a rewrite is separately named and revalidated. A result table alone does not prove the plugin accelerated any operator. A plan alone does not prove the final result is correct.

## An end-to-end acceptance notebook

Begin with the grain of each table. A sales row represents one product quantity observation; the price table has one row per product under the declared input contract. Validate price-key uniqueness before joining. Derive revenue using exact integer cents or the chosen exact decimal schema rather than introducing floating rounding into a simple accounting example.

The Scala and PySpark programs should use the same explicit schemas and sorted output. Both build local finite fixtures, perform a declarative join and aggregate, collect only the tiny final table and stop the owned Spark session in a finally block. Printing the formatted plan teaches physical execution, but the result assertions remain independent literal expectations. Changing input cardinality or null rules requires updating the mathematical derivation, not merely copying observed output into the expected result.

On an optional GPU environment, repeat the same query and input. Add plugin release, jar checksum, Spark/Scala/JDK versions, CUDA variant, driver, GPU model and executor-resource configuration to the notebook. Capture the final executed plan after materialization and record operator fallback reasons, device use, task concurrency, spill and total completion time. Keep GPU evidence separate from the already completed CPU language parity tests.

The capstone is complete when another learner can reproduce the CPU semantics, explain the plan and understand exactly what remains unqualified. Real GPU performance is an additional evidence layer. A useful report can conclude that the tiny fixture is too small for a meaningful speed comparison while still demonstrating correct setup and operator execution on prepared hardware.


### Key terms

- **CPU oracle:** An exact, simple implementation whose output serves as the expected result for both Spark languages.
- **Declarative expression:** A DataFrame or SQL expression that Spark can optimize, unlike opaque procedural code.
- **Explicit schema:** A declared set of column names, types and nullability that avoids inference differences.
- **Duplicate dimension keys:** Repeated keys in a lookup table that multiply joined rows and change aggregates.
- **Executed plan:** The plan Spark actually ran for an action, which is the evidence for GPU operator use.

## Worked examples

### Worked example 1

Sales (A,2),(A,4),(B,3) joined to prices (A,10),(B,20) yield revenue A 60 and B 60. The fixture has deterministic exact integer output.

### Worked example 2

Adding a duplicate A price row intentionally doubles A matches. A defensive uniqueness check should reject that input if the business contract requires one price per product.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-127_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-127_cpu.py
```

```python
sales = [("A", 2), ("A", 4), ("B", 3)]
prices = {"A": 10, "B": 20}
revenue = {}
for product, quantity in sales:
    revenue[product] = revenue.get(product, 0) + quantity * prices[product]
assert sorted(revenue.items()) == [("A", 60), ("B", 60)]
print("CPU ETL oracle:", sorted(revenue.items()))
```

**Expected observation:** Sorted revenue [(A,60),(B,60)].

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `sales` | `[('A', 2), ('A', 4), ('B', 3)]` |
| `prices` | `{'A': 10, 'B': 20}` |
| `revenue` | `{'A': 60, 'B': 60}` |
| `product` | `'B'` |
| `quantity` | `3` |

## Scala and PySpark parity lab

Both CPU variants assert one expected result. Read the [parity rules](../../STUDY-GUIDE.md#spark-parity-and-gpu-spark).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-127.md) before opening hints.

### Exercise 1: Derive expected revenue

**Trap to avoid:** Summing prices per product before multiplying, or multiplying the total quantity by the sum of all prices, mixes products and gives wrong totals such as 180 for A.

### Exercise 2: Write Scala expressions

**Trap to avoid:** Relying on schema inference from text files can type numbers as strings or doubles, changing join behavior or output types between runs.

### Exercise 3: Write PySpark expressions

**Trap to avoid:** Collecting rows into Python and summing in a loop changes where the work runs and stops being a Spark pipeline comparison.

### Exercise 4: Test duplicate dimension keys

**Trap to avoid:** Running the join without checking lets a duplicate price row double A to 120 with no error, which looks like a real sales increase.

### Exercise 5: Capture executed GPU evidence

**Trap to avoid:** Claiming GPU execution from a CPU-only environment, or from a configuration file alone, reports evidence that does not exist.

### Exercise 6: Prepare a balanced capstone report

**Trap to avoid:** Writing the report as if GPU acceleration was demonstrated when only CPU runs happened misleads anyone deciding on deployment.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Multiply each product's quantities by its price, sum per product and check both totals.
2. Read the input with an explicit schema, join on product, derive revenue and group by product in Scala.
3. Apply the same operations in PySpark and sort the output so the two results can be compared row by row.
4. Add a second price for product A and decide whether your contract rejects it or accepts the multiplied rows.
5. List the plans, metrics and equality checks that must come from actual GPU hardware.
6. Report the CPU results and the pending GPU limitations in separate sections.

## Common mistakes and self-check

A common capstone mistake is treating a correct result table as proof of acceleration, or a GPU plan as proof of correctness. Each answers a different question. Another is letting a duplicate dimension key silently double revenue. Fix both by checking exact output against a CPU oracle, enforcing or explicitly accepting key uniqueness and keeping query text and inputs unchanged across backends while collecting plans and metrics separately.

**Evidence limit:** The reference produces sorted revenue `[(A, 60), (B, 60)]` with exact integers. It runs neither Spark implementation, so equivalent Scala and PySpark plans and any GPU evidence must come from executed jobs.

1. Why run both ordinary Spark implementations before any GPU comparison?
2. What does a GPU report need besides timing?
3. When may the query text change across backends?

Answers: [self-check answers](../solutions/cuda-127_solutions.md#self-check-answers).

## Primary references

- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-127: Capstone: the same analytical pipeline in Scala and PySpark.
Read courses/cuda/spark/guides/cuda-127.md and courses/cuda/spark/lessons/cuda-127.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
