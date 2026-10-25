# cuda-117: Nulls, decimals, timestamps and equality contracts

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-116`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **calculate both counts**, **name timestamp timezone**, and **design ordered result comparison** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

SQL semantics include null propagation, three-valued predicates, decimal precision/scale, overflow policy, timezone interpretation and string ordering. GPU and CPU results should be compared under the query's declared semantics, not by assuming every numeric column is a floating array. An empty aggregate and an aggregate of only null values can differ from a sum initialized to zero in Python.

Use explicit schemas and deterministic ordering for comparison. Floating aggregates may require a justified tolerance because reduction order can change; decimal and integer outputs often require exact equality under the selected SQL mode. Timestamp tests should name the session timezone and include boundary cases. Never hide a semantic mismatch by relaxing tolerance until the test passes.



## Worked examples

### Worked example 1

COUNT (*) over [2, null,5] is 3 while COUNT (value) is 2. SUM (value) is 7 under skip-null semantics. The two counts answer different questions.

### Worked example 2

Decimal 1.10 plus 2.20 should preserve the chosen decimal contract. A binary floating approximation is not a substitute for testing a decimal expression.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
from decimal import Decimal

values = [2, None, 5]
assert len(values) == 3
assert sum(v is not None for v in values) == 2
assert sum(v for v in values if v is not None) == 7
assert Decimal("1.10") + Decimal("2.20") == Decimal("3.30")
print("CPU SQL-semantics oracle: rows3 nonnull2 sum7 decimal3.30")
```

**Expected observation:** Rows 3, non-null 2, sum 7 and exact decimal 3.30.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Scala and PySpark parity lab

Choose **Scala Spark on CPU** or **PySpark on CPU** to run the same bounded query in the ordinary Spark workers. Both use explicit schemas, local fixtures, at most two local threads, a disabled GPU SQL setting and a finally-block session stop. They assert the same expected result. These are CPU Spark observations, not GPU plugin qualification.

For external GPU comparison, retain the same relational expressions and expected result but use a separately reviewed launcher and compatibility matrix. Do not change the classroom source into an arbitrary cluster connection.

## Practice and transfer

### Exercise 1: Calculate both counts

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **calculate both counts** in the examples above.

### Exercise 2: Handle all-null aggregate

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **handle all-null aggregate** in the examples above.

### Exercise 3: Compare decimal values

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **compare decimal values** in the examples above.

### Exercise 4: Name timestamp timezone

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **name timestamp timezone** in the examples above.

### Exercise 5: Choose float tolerances

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **choose float tolerances** in the examples above.

### Exercise 6: Design ordered result comparison

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **design ordered result comparison** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Calculate both counts".
2. Change one assumption in worked example 2 while preserving the declared contract: handle all-null aggregate.
3. Trace the CPU program's variables before adding hardware behavior: compare decimal values.
4. Draw producers, consumers and the exact operation boundary for the task "Name timestamp timezone".
5. Separate what the small fixture establishes from what the real runtime must show: choose float tolerances.
6. Write a counterexample to an overbroad claim before you design ordered result comparison.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Calculate both counts`. For the final claim use `Design ordered result comparison`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Ask an AI tutor about this lesson

> I am studying `cuda-117` using `courses/cuda/spark/guides/cuda-117.md` and `courses/cuda/spark/lessons/cuda-117.md`. Help me reason about Nulls, decimals, timestamps and equality contracts. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
