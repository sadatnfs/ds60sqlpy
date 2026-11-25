# cuda-113: RAPIDS, cuDF and the Spark execution boundary

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** intermediate. **Prerequisites:** `cuda-003`, `cuda-005`, `spark-013`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Classify four execution layers.
- Explain cuDF versus plugin.
- Identify an opaque UDF.
- Write equivalent Scala and PySpark expressions.
- Define CPU-only progress.
- List real GPU evidence.

## Mechanism and vocabulary

RAPIDS is an ecosystem of GPU data-science components. cuDF is a columnar dataframe library; the NVIDIA cuDF plugin for Apache Spark, formerly named RAPIDS Accelerator for Apache Spark, integrates with Spark's execution engine. Scala and PySpark SQL/DataFrame expressions can reach the same optimized physical plan. The plugin targets supported SQL/DataFrame operators, not every line of Python or Scala in an application.

A Python loop inside an ordinary UDF does not become a CUDA kernel because the plugin is enabled. Separate GPU-aware UDF and machine-learning integrations have their own package and execution contracts. The first decision is therefore about where the work lives: a single-process dataframe, Spark's distributed SQL engine, a UDF process or a framework training job. This course keeps the existing CPU Spark workers usable and treats GPU Spark as an explicitly prepared external environment.

## Trace one query across language boundaries

A PySpark expression such as `df.groupBy("team").sum("amount")` builds a relational plan. Python is the authoring interface, but supported SQL execution is generally coordinated by Spark's JVM engine. Scala constructs a comparable plan directly through JVM APIs. The key question for GPU acceleration is the resulting supported physical work, not which of those two languages typed the expression.

An ordinary Python UDF is different: Spark must invoke Python code with its declared input/output contract. Vectorized pandas UDFs can reduce interchange overhead, but their body remains whatever Python and libraries actually execute. Arrow improves representation exchange; it does not translate arbitrary Python control flow into GPU instructions. A purpose-built GPU UDF integration needs explicit device allocation and package rules.

cuDF's local dataframe API works within a process and uses GPU columnar algorithms. The Spark plugin connects supported columnar operations to Spark's distributed scheduling, joins, shuffles, retries and SQL semantics. Spark RAPIDS ML adds a separate estimator surface. Keep these names in a diagram with arrows for data movement and process boundaries; treating them as one magic GPU switch leads to misleading performance claims.

The practical beginner sequence is CPU semantic oracle, ordinary Scala and PySpark query, logical/physical plan reading, then optional GPU plugin qualification. The same schema and expected rows carry through all four steps. This lets a learner on any CPU-only machine complete the reasoning and programming foundation without pretending that a container acquired NVIDIA hardware.


### Key terms

- **RAPIDS:** An ecosystem of GPU data-science libraries that includes cuDF.
- **cuDF plugin for Apache Spark:** The plugin, formerly named RAPIDS Accelerator for Apache Spark, that replaces supported Spark SQL operators with GPU implementations.
- **Physical plan:** The concrete operators Spark selects to execute a query, where the plugin substitutes GPU operators.
- **Opaque UDF:** A user-defined function whose body Spark cannot inspect, so the plugin cannot translate it into GPU operators.

## Worked examples

### Worked example 1

A DataFrame filter followed by groupBy sum is visible to Catalyst as declarative relational operations. A Python UDF that performs an opaque operation may require a CPU boundary or a separate supported integration.

### Worked example 2

Grouping values [2,4,6,8] by accompanying labels A,A,B,B is the same relational objective in Scala and PySpark. Equivalent output is necessary, but GPU operator evidence still comes from the executed plan.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-113_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-113_cpu.py
```

```python
rows = [("A", 2), ("A", 4), ("B", 6), ("B", 8)]
totals = {}
for key, value in rows:
    totals[key] = totals.get(key, 0) + value
assert totals == {"A": 6, "B": 14}
print("CPU Spark semantic oracle:", sorted(totals.items()))
```

**Expected observation:** Grouped totals A 6 and B 14; no GPU execution claimed.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `rows` | `[('A', 2), ('A', 4), ('B', 6), ('B', 8)]` |
| `totals` | `{'A': 6, 'B': 14}` |
| `key` | `'B'` |
| `value` | `8` |

## Scala and PySpark parity lab

Both CPU variants assert one expected result. Read the [parity rules](../../STUDY-GUIDE.md#spark-parity-and-gpu-spark).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-113.md) before opening hints.

### Exercise 1: Classify four execution layers

**Trap to avoid:** Calling the whole pipeline GPU-accelerated because one layer uses the GPU hides the layers that still run on CPU and the transfers between them, which often dominate.

### Exercise 2: Explain cuDF versus plugin

**Trap to avoid:** Assuming installing cuDF on executors accelerates Spark SQL confuses the two, since without the plugin configured Spark never routes operators to cuDF.

### Exercise 3: Identify an opaque UDF

**Trap to avoid:** Assuming a UDF runs on the GPU because surrounding operators do ignores the boundary, and the measured time then includes conversions the plan does not advertise.

### Exercise 4: Write equivalent Scala and PySpark expressions

**Trap to avoid:** Writing the PySpark version with a Python loop over collected rows changes where the work happens and loses the equivalence, even if the totals match.

### Exercise 5: Define CPU-only progress

**Trap to avoid:** Reporting a CPU run as evidence that the GPU path works confuses semantic parity with accelerated execution.

### Exercise 6: List real GPU evidence

**Trap to avoid:** Presenting only a configuration file as GPU evidence shows intent but not execution.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. For each piece of work, ask whether it runs in one dataframe process, in Spark SQL operators, in a UDF process or in a training job.
2. Ask which product is the dataframe library and which one hooks into Spark planning and execution.
3. Ask whether Spark's optimizer can see inside the function body, or only its inputs and outputs.
4. Use the same schema, null policy and aggregation in both languages and compare the output rows.
5. List the checks you can complete today on a CPU worker, such as semantic references and plan reading.
6. Write the evidence a GPU run must produce: runtime, executed operator plan, metrics and equal results.

## Common mistakes and self-check

A common mistake is expecting the Spark plugin to accelerate everything in an application. A Python loop inside an ordinary UDF stays opaque to the optimizer and runs as host code even with the plugin enabled. Another is treating equal outputs from Scala and PySpark as proof that GPU operators ran. Fix both by keeping work in declarative DataFrame operations where possible and reading the executed physical plan on a prepared GPU environment before claiming acceleration.

**Evidence limit:** The reference computes grouped totals A 6 and B 14 with no GPU execution claimed. It cannot show which operators the plugin replaces; that requires an executed plan from a compatible Spark and GPU environment.

1. What was the plugin formerly called?
2. Why can Scala and PySpark reach the same physical plan?
3. Do GPU-aware UDF and machine learning integrations come with the plugin?

Answers: [self-check answers](../solutions/cuda-113_solutions.md#self-check-answers).

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-113: RAPIDS, cuDF and the Spark execution boundary.
Read courses/cuda/spark/guides/cuda-113.md and courses/cuda/spark/lessons/cuda-113.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
