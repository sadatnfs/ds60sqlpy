# cuda-115: From Catalyst plans to actual GPU operators

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** intermediate. **Prerequisites:** `cuda-113`, `cuda-114`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **draw logical versus physical plan**, **explain lazy evaluation**, and **choose operator metrics** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Catalyst represents a query as logical operations, applies transformations and selects physical implementations. Explain output shows what Spark planned, while an executed SQL plan and metrics show what happened for an action. Adaptive Query Execution can change a physical plan using runtime statistics, so the initial plan may differ from the final executed plan.

The plugin replaces supported physical operators with GPU-capable implementations and inserts transitions where needed. Use the release's explain diagnostics to understand why an operation stayed on CPU. Seeing one GPU node does not establish that the entire job is accelerated. Conversely, a CPU metadata or coordination node can coexist with useful GPU computation. Interpret the plan by operation and stage, then compare measured completed work.

## Read a plan as a sequence of contracts

A scan establishes a schema and row source. A filter applies a predicate, including SQL null logic. A projection chooses or computes columns. An exchange changes partition ownership. A join or aggregate combines records according to key and multiplicity rules. Each node has both a semantic contract and a physical representation. A GPU replacement must preserve the first while changing the second.

Start by drawing the logical intent without backend labels. Then inspect `explain("formatted")` in the exact Spark environment. Highlight CPU/GPU representation transitions and exchanges separately: a device transfer is not the same operation as redistribution across executors, although one stage can involve both. Add operator metrics after an action completes. If AQE is enabled, retain the final executed plan because broadcast and partition decisions may have changed.

The plugin's explain diagnostics can report why a node is not selected for GPU execution. Read the reason at the expression and dtype level. An unsupported child can change the useful acceleration region around it, and a small unsupported expression can force expensive conversions. Do not rewrite the query merely to maximize the count of GPU nodes; preserve semantics and compare complete latency.

A useful review table has columns node, semantic role, input/output representation, supported status, fallback reason, rows/batches, elapsed time and spill. This turns a screenshot into an argument. A GPU node in a planned diagram is weaker evidence than that node in an executed query with metrics, and even the executed node must be accompanied by a correct result comparison.


## Worked examples

### Worked example 1

A synthetic plan Scan -> Filter -> Aggregate can contain a GPU filter and aggregate with a CPU-side source boundary. Count transfers and conversions rather than labeling the whole query GPU-only.

### Worked example 2

A count action triggers execution; constructing a DataFrame alone is lazy. A plan printed before an action does not contain the same runtime evidence as the completed SQL execution view.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
plan = [("scan", "CPU"), ("filter", "GPU"), ("aggregate", "GPU"), ("collect", "CPU")]
transitions = sum(plan[i][1] != plan[i - 1][1] for i in range(1, len(plan)))
assert transitions == 2
assert sum(device == "GPU" for _, device in plan) == 2
print("Synthetic plan worksheet:", transitions, "CPU/GPU transitions")
```

**Expected observation:** Synthetic plan has two GPU nodes and two backend transitions.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Draw logical versus physical plan

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **draw logical versus physical plan** in the examples above.

### Exercise 2: Mark GPU candidate nodes

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **mark GPU candidate nodes** in the examples above.

### Exercise 3: Locate transitions

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **locate transitions** in the examples above.

### Exercise 4: Explain lazy evaluation

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **explain lazy evaluation** in the examples above.

### Exercise 5: Compare initial and final AQE plan

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **compare initial and final AQE plan** in the examples above.

### Exercise 6: Choose operator metrics

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **choose operator metrics** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Draw logical versus physical plan".
2. Change one assumption in worked example 2 while preserving the declared contract: mark GPU candidate nodes.
3. Trace the CPU program's variables before adding hardware behavior: locate transitions.
4. Draw producers, consumers and the exact operation boundary for the task "Explain lazy evaluation".
5. Separate what the small fixture establishes from what the real runtime must show: compare initial and final AQE plan.
6. Write a counterexample to an overbroad claim before you choose operator metrics.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Draw logical versus physical plan`. For the final claim use `Choose operator metrics`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

GPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.

## Ask an AI tutor about this lesson

> I am studying `cuda-115` using `courses/cuda/spark/guides/cuda-115.md` and `courses/cuda/spark/lessons/cuda-115.md`. Help me reason about From Catalyst plans to actual GPU operators. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [cuDF Spark plugin release and compatibility matrix](https://nvidia.github.io/cudf-spark/docs/download.html)
- [Supported Spark operators and expression types](https://nvidia.github.io/cudf-spark/docs/supported_ops.html)
- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)
- [Apache Spark SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
