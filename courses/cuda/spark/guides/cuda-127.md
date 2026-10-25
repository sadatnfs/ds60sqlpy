# cuda-127: Capstone: the same analytical pipeline in Scala and PySpark

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-117`, `cuda-121`, `cuda-123`, `cuda-124`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **derive expected revenue**, **test duplicate dimension keys**, and **prepare a balanced capstone report** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Build a bounded ETL pipeline with an explicit schema, null handling, a join, a derived column and a grouped metric. Provide Scala and PySpark implementations using equivalent declarative expressions. Use a CPU oracle for exact expected output, then run both ordinary Spark implementations. Only after semantic agreement should a separately prepared GPU Spark environment be compared.

The GPU report includes exact compatibility matrix, initial and executed plans, unsupported-operation reasons, resource assignment, task concurrency, memory/spill observations and complete timing. Keep query text and input identity unchanged across backends unless a rewrite is separately named and revalidated. A result table alone does not prove the plugin accelerated any operator. A plan alone does not prove the final result is correct.

## An end-to-end acceptance notebook

Begin with the grain of each table. A sales row represents one product quantity observation; the price table has one row per product under the declared input contract. Validate price-key uniqueness before joining. Derive revenue using exact integer cents or the chosen exact decimal schema rather than introducing floating rounding into a simple accounting example.

The Scala and PySpark programs should use the same explicit schemas and sorted output. Both build local finite fixtures, perform a declarative join and aggregate, collect only the tiny final table and stop the owned Spark session in a finally block. Printing the formatted plan teaches physical execution, but the result assertions remain independent literal expectations. Changing input cardinality or null rules requires updating the mathematical derivation, not merely copying observed output into the expected result.

On an optional GPU environment, repeat the same query and input. Add plugin release, jar checksum, Spark/Scala/JDK versions, CUDA variant, driver, GPU model and executor-resource configuration to the notebook. Capture the final executed plan after materialization and record operator fallback reasons, device use, task concurrency, spill and total completion time. Keep GPU evidence separate from the already completed CPU language parity tests.

The capstone is complete when another learner can reproduce the CPU semantics, explain the plan and understand exactly what remains unqualified. Real GPU performance is an additional evidence layer. A useful report can conclude that the tiny fixture is too small for a meaningful speed comparison while still demonstrating correct setup and operator execution on prepared hardware.


## Worked examples

### Worked example 1

Sales (A,2),(A,4),(B,3) joined to prices (A,10),(B,20) yield revenue A 60 and B 60. The fixture has deterministic exact integer output.

### Worked example 2

Adding a duplicate A price row intentionally doubles A matches. A defensive uniqueness check should reject that input if the business contract requires one price per product.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

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

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Scala and PySpark parity lab

Choose **Scala Spark on CPU** or **PySpark on CPU** to run the same bounded query in the ordinary Spark workers. Both use explicit schemas, local fixtures, at most two local threads, a disabled GPU SQL setting and a finally-block session stop. They assert the same expected result. These are CPU Spark observations, not GPU plugin qualification.

For external GPU comparison, retain the same relational expressions and expected result but use a separately reviewed launcher and compatibility matrix. Do not change the classroom source into an arbitrary cluster connection.

## Practice and transfer

### Exercise 1: Derive expected revenue

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **derive expected revenue** in the examples above.

### Exercise 2: Write Scala expressions

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **write Scala expressions** in the examples above.

### Exercise 3: Write PySpark expressions

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **write PySpark expressions** in the examples above.

### Exercise 4: Test duplicate dimension keys

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **test duplicate dimension keys** in the examples above.

### Exercise 5: Capture executed GPU evidence

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **capture executed GPU evidence** in the examples above.

### Exercise 6: Prepare a balanced capstone report

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **prepare a balanced capstone report** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Derive expected revenue".
2. Change one assumption in worked example 2 while preserving the declared contract: write Scala expressions.
3. Trace the CPU program's variables before adding hardware behavior: write PySpark expressions.
4. Draw producers, consumers and the exact operation boundary for the task "Test duplicate dimension keys".
5. Separate what the small fixture establishes from what the real runtime must show: capture executed GPU evidence.
6. Write a counterexample to an overbroad claim before you prepare a balanced capstone report.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Derive expected revenue`. For the final claim use `Prepare a balanced capstone report`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Ask an AI tutor about this lesson

> I am studying `cuda-127` using `courses/cuda/spark/guides/cuda-127.md` and `courses/cuda/spark/lessons/cuda-127.md`. Help me reason about Capstone: the same analytical pipeline in Scala and PySpark. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
