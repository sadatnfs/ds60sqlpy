# cuda-113: RAPIDS, cuDF and the Spark execution boundary

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** intermediate. **Prerequisites:** `cuda-003`, `cuda-005`, `spark-013`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **classify four execution layers**, **write equivalent Scala and PySpark expressions**, and **list real GPU evidence** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

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

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

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

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Scala and PySpark parity lab

Choose **Scala Spark on CPU** or **PySpark on CPU** to run the same bounded query in the ordinary Spark workers. Both use explicit schemas, local fixtures, at most two local threads, a disabled GPU SQL setting and a finally-block session stop. They assert the same expected result. These are CPU Spark observations, not GPU plugin qualification.

For external GPU comparison, retain the same relational expressions and expected result but use a separately reviewed launcher and compatibility matrix. Do not change the classroom source into an arbitrary cluster connection.

## Practice and transfer

### Exercise 1: Classify four execution layers

**Trap to avoid:** Calling the whole pipeline GPU-accelerated because one layer uses the GPU hides the layers that still run on CPU and the transfers between them, which often dominate.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Explain cuDF versus plugin

**Trap to avoid:** Assuming installing cuDF on executors accelerates Spark SQL confuses the two, since without the plugin configured Spark never routes operators to cuDF.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Identify an opaque UDF

**Trap to avoid:** Assuming a UDF runs on the GPU because surrounding operators do ignores the boundary, and the measured time then includes conversions the plan does not advertise.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Write equivalent Scala and PySpark expressions

**Trap to avoid:** Writing the PySpark version with a Python loop over collected rows changes where the work happens and loses the equivalence, even if the totals match.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Define CPU-only progress

**Trap to avoid:** Reporting a CPU run as evidence that the GPU path works confuses semantic parity with accelerated execution.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: List real GPU evidence

**Trap to avoid:** Presenting only a configuration file as GPU evidence shows intent but not execution.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Classify four execution layers".
2. Change one assumption in worked example 2 while preserving the declared contract: explain cuDF versus plugin.
3. Trace the CPU program's variables before adding hardware behavior: identify an opaque UDF.
4. Draw producers, consumers and the exact operation boundary for the task "Write equivalent Scala and PySpark expressions".
5. Separate what the small fixture establishes from what the real runtime must show: define CPU-only progress.
6. Write a counterexample to an overbroad claim before you list real GPU evidence.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Classify four execution layers`. For the final claim use `List real GPU evidence`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-113: RAPIDS, cuDF and the Spark execution boundary.
Read courses/cuda/spark/guides/cuda-113.md and courses/cuda/spark/lessons/cuda-113.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
