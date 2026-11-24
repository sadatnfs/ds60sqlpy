# cuda-128: When GPU Spark is the wrong tool

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-123`, `cuda-126`, `cuda-127`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute end-to-end tradeoff**, **include operational cost**, and **write an evidence-based recommendation** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A good acceleration decision includes a credible no-change outcome. Tiny data, unsupported expressions, expensive transfers, external I/O, severe skew or a memory-constrained device can make CPU Spark or a single-process dataframe the better choice. Distributed scheduling overhead can dominate a workload that fits comfortably in one local process. GPU capability is one input to architecture, not a requirement to use it.

Compare total completion time, resource cost, operational complexity and output quality under actual constraints. Maintain a CPU fallback installation separately from plugin operator fallback. Revisit the decision when data size, workload mix or hardware changes. The final review should identify the smallest supported system that solves the problem and the evidence that would justify expanding it.



### Key terms

- **No-change outcome:** A credible decision to keep the existing CPU approach when acceleration does not pay off.
- **Steady-state cost:** Recurring time per run after setup, compared separately from one-time startup cost.
- **Operational complexity:** The ongoing effort to deploy, monitor and support a system, which counts toward total cost.
- **Reevaluation trigger:** A recorded condition, such as data growth or a new release, that justifies revisiting the decision.

## Worked examples

### Worked example 1

A local CPU dataframe finishes a tiny analysis in 0.1 seconds while Spark startup takes several seconds. No kernel speedup can erase startup for a one-off job without changing the execution model.

### Worked example 2

A GPU query saves 30 seconds of compute but adds 40 seconds of transfers and conversions. The complete application loses 10 seconds despite faster arithmetic.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
saved_compute, added_transfer = 30, 40
net = added_transfer - saved_compute
assert net == 10
candidates = {"local_cpu": 0.1, "spark_startup_only": 3.0}
assert candidates["local_cpu"] < candidates["spark_startup_only"]
print("CPU architecture decision: GPU candidate adds", net, "seconds")
```

**Expected observation:** GPU candidate adds 10 modeled seconds end to end.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `saved_compute` | `30` |
| `added_transfer` | `40` |
| `net` | `10` |
| `candidates` | `{'local_cpu': 0.1, 'spark_startup_only': 3.0}` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Compute end-to-end tradeoff

**Trap to avoid:** Reporting the 30-second compute saving alone recommends a change that makes the application slower overall.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Choose a tiny-data tool

**Trap to avoid:** Using GPU Spark for every analysis because it is available adds startup and operational overhead to jobs that never needed distribution.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Separate setup and steady state

**Trap to avoid:** Reporting only steady-state throughput favors GPU Spark for interactive one-off use, where setup actually dominates.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Include operational cost

**Trap to avoid:** Comparing only query time ignores the work of keeping a GPU Spark stack compatible across upgrades. A Spark upgrade can be blocked until a matching plugin release exists, which delays security patches.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Define a reevaluation trigger

**Trap to avoid:** Rejecting GPU Spark permanently ignores that the tradeoff can change, while revisiting constantly wastes effort. A trigger such as transfer time falling below compute savings ties the revisit to the exact term that decided the current outcome.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Write an evidence-based recommendation

**Trap to avoid:** Recommending the most powerful technology by default ignores the measured tradeoff and the operational cost. It also skips stating missing evidence, so the decision cannot be corrected when new data arrives.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute end-to-end tradeoff".
2. Change one assumption in worked example 2 while preserving the declared contract: choose a tiny-data tool.
3. Trace the CPU program's variables before adding hardware behavior: separate setup and steady state.
4. Draw producers, consumers and the exact operation boundary for the task "Include operational cost".
5. Separate what the small fixture establishes from what the real runtime must show: define a reevaluation trigger.
6. Write a counterexample to an overbroad claim before you write an evidence-based recommendation.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute end-to-end tradeoff`. For the final claim use `Write an evidence-based recommendation`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

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
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-128: When GPU Spark is the wrong tool.
Read courses/cuda/spark/guides/cuda-128.md and courses/cuda/spark/lessons/cuda-128.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
