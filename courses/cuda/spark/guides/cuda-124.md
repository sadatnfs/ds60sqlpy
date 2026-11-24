# cuda-124: Python UDFs, pandas APIs and GPU-aware ML boundaries

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-116`, `cuda-118`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **classify four APIs**, **define GPU-aware UDF ownership**, and **design quality parity tests** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Spark SQL expressions, Python UDFs, pandas UDFs, pandas API on Spark and GPU dataframe libraries are different execution surfaces. Arrow can improve interchange for vectorized UDFs without making their body GPU code. A GPU-aware UDF must explicitly manage supported packages, device assignment, batch size and transfers under a reviewed contract. Ordinary plugin enablement does not rewrite arbitrary Python algorithms.

GPU-accelerated machine-learning integrations such as Spark RAPIDS ML are separate from SQL operator acceleration. Estimator support, semantics and release compatibility need their own validation. A training job inside each partition can duplicate work or oversubscribe a device if resource ownership is unclear. Keep preprocessing, distributed SQL and training responsibilities explicit, and compare model quality as well as elapsed time.

## Avoid the GPU-UDF shortcut trap

A common mistake is to create a GPU model or dataframe inside every UDF call. That can repeatedly initialize contexts, transfer tiny batches and duplicate model storage. Even when each call is numerically correct, the process and batching design can overwhelm the useful GPU work. A vectorized UDF changes batching, but still needs explicit resource ownership and package compatibility.

A declarative built-in expression gives Catalyst visibility into algebra and types. Prefer it when it expresses the same contract. When a genuinely custom GPU operation is needed, define per-worker initialization, bounded batch sizes, device assignment, input/output schema, null policy and cleanup. Do not let every partition choose device zero independently on a multi-executor host.

Machine-learning training is another boundary. A SQL acceleration plugin does not automatically coordinate gradient collectives across Spark tasks. Separate GPU-aware ML integrations can provide reviewed estimator behavior, but they need their own supported algorithms, versions and quality comparisons. The curriculum therefore links the Spark specialization to the PyTorch/TensorFlow distribution chapters without treating one scheduler as a drop-in replacement for the other.

For the included null-preserving doubling example, the built-in expression and reference function agree on integers and missing values. The next meaningful test adds type boundaries and verifies the output schema. Only after that should a real Spark plan be inspected for supported acceleration. This sequence makes correctness visible before any GPU configuration is introduced.


### Key terms

- **Python UDF:** A row-at-a-time Python function called from Spark, which the GPU plugin does not translate.
- **Pandas UDF:** A vectorized Python function that receives Arrow-backed batches as pandas objects.
- **Pandas API on Spark:** A pandas-like interface that compiles to Spark plans rather than running pandas code directly.
- **GPU-aware UDF:** A UDF that explicitly manages GPU packages, device assignment, batch size and transfers under a reviewed contract.

## Worked examples

### Worked example 1

A built-in multiplication expression is visible in the relational plan. A Python UDF returning x*2 may hide the same algebra behind a process boundary and block equivalent optimization.

### Worked example 2

Calling a GPU library from every partition does not automatically coordinate multi-GPU training. Each task needs a defined device share and bounded memory contract.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
values = [1, None, 3]


def expression(x):
    return None if x is None else x * 2


expected = [2, None, 6]
assert [expression(x) for x in values] == expected
print("CPU expression parity oracle:", expected)
```

**Expected observation:** Null-preserving expression produces [2, None,6].

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `values` | `[1, None, 3]` |
| `expected` | `[2, None, 6]` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Classify four APIs

**Trap to avoid:** Treating a pandas UDF as equivalent to a built-in because it is vectorized ignores the process boundary and serialization that still surround it.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Replace an equivalent simple UDF

**Trap to avoid:** Replacing a UDF that maps null to 0 with the built-in, which keeps null, changes results while appearing to be the same arithmetic.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Explain Arrow limits

**Trap to avoid:** Assuming that enabling Arrow moves UDF work to the GPU confuses data format with execution location.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Define GPU-aware UDF ownership

**Trap to avoid:** Calling a GPU library from every partition with no device assignment risks oversubscription and out-of-memory errors that appear only at higher concurrency.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Distinguish SQL and ML acceleration

**Trap to avoid:** Reporting the whole pipeline as accelerated because the SQL plan shows GPU operators omits the training step.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Design quality parity tests

**Trap to avoid:** Comparing a GPU model trained on a different split with a CPU model attributes data differences to the backend.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Classify four APIs".
2. Change one assumption in worked example 2 while preserving the declared contract: replace an equivalent simple UDF.
3. Trace the CPU program's variables before adding hardware behavior: explain Arrow limits.
4. Draw producers, consumers and the exact operation boundary for the task "Define GPU-aware UDF ownership".
5. Separate what the small fixture establishes from what the real runtime must show: distinguish SQL and ML acceleration.
6. Write a counterexample to an overbroad claim before you design quality parity tests.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Classify four APIs`. For the final claim use `Design quality parity tests`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

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
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-124: Python UDFs, pandas APIs and GPU-aware ML boundaries.
Read courses/cuda/spark/guides/cuda-124.md and courses/cuda/spark/lessons/cuda-124.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
