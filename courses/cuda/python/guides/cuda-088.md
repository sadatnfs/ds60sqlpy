# cuda-088: Input pipelines and a hungry GPU

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-071`, `cuda-087`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute serial time**, **explain pinned versus ordinary host storage**, and **choose bounded worker experiments** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Training is a producer-consumer pipeline: obtain examples, decode, transform, batch, transfer and compute. GPU idleness can arise because the next batch is not ready, not because the model kernel is poor. Increasing workers helps only while the bottleneck can parallelize and memory/I/O remain within budget. Prefetch queues hide latency by retaining future batches, so queue depth also consumes resources.

PyTorch's DataLoader and pinned-memory options express one host pipeline; TensorFlow's tf.data map, batch and prefetch express another. Use synthetic resident tensors as a diagnostic comparison, not as a replacement for measuring real preprocessing. Time complete steps and inspect overlap. Bound worker counts and terminate workers cleanly so a tiny lesson cannot leave a large background process tree.



### Key terms

- **Producer-consumer pipeline:** An arrangement where loader workers prepare batches while the device trains on earlier ones.
- **DataLoader worker:** A separate process that reads and transforms samples in parallel with training.
- **Prefetch queue:** A bounded buffer of ready batches that hides loading latency while it stays nonempty.
- **Pipeline bottleneck:** The slowest stage, which bounds overall throughput regardless of how fast the other stages are.

## Worked examples

### Worked example 1

A serial pipeline spends 6 ms preparing and 4 ms computing each batch, totaling 10 ms. Ideal steady-state overlap approaches 6 ms per batch after startup, not 4 ms.

### Worked example 2

Prefetching three batches of 8 MiB requires at least 24 MiB for queued payloads, excluding decoder state, copies and framework overhead.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
prepare, compute = 6, 4
serial = prepare + compute
ideal = max(prepare, compute)
queued = 3 * 8 * 1024 * 1024
assert serial == 10 and ideal == 6 and queued == 25165824
print("CPU pipeline model:", serial, ideal, queued)
```

**Expected observation:** Serial 10 ms, ideal steady-state 6 ms, queued payload 25165824 bytes.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `prepare` | `6` |
| `compute` | `4` |
| `serial` | `10` |
| `ideal` | `6` |
| `queued` | `25165824` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Use a bounded DataLoader with num_workers=0 for the tiny baseline. Compare deliberately prepared pinned batches and non_blocking transfers only on the CUDA lane.

### TensorFlow

Build a finite tf.data pipeline with explicit batch and bounded prefetch. Limit the private thread pool in the teaching program and inspect preprocessing versus device work.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Executable framework practice

The variant chooser offers **PyTorch on CPU**, **TensorFlow on CPU**, and separate **NVIDIA CUDA** versions. CPU versions force CPU placement. CUDA versions require the named GPU profile and refuse to silently fall back. Each complete program uses the same tiny deterministic objective, bounded tensors and local synthetic data. Read its source before running; a framework pass establishes only that variant and environment.

The checkpoint demonstration is in-memory. It teaches what state must be saved; it does not export a durable model artifact or preserve an in-flight device context. Advanced custom-op, distributed and engine-building projects remain separately prepared external workflows.

## Practice and transfer

### Exercise 1: Compute serial time

**Trap to avoid:** Reporting the 4 ms GPU compute time as the step time ignores the 6 ms the GPU spends idle waiting for input.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Compute an ideal bottleneck bound

**Trap to avoid:** Claiming overlap reduces the step to 4 ms assumes the input stage becomes free. Only a faster or more parallel preparation stage can move the bound below 6 ms.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Budget the queue

**Trap to avoid:** Budgeting one batch because only one is used at a time ignores that all queued batches are resident at once.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Explain pinned versus ordinary host storage

**Trap to avoid:** Pinning every buffer by default can starve the host and slow the whole machine.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Compare resident-data diagnostic

**Trap to avoid:** Reporting the resident-data speed as production throughput ignores that real training must load new data every step.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Choose bounded worker experiments

**Trap to avoid:** Raising all settings to their maximum at once may exhaust host memory or CPU cores and still hide which change helped.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute serial time".
2. Change one assumption in worked example 2 while preserving the declared contract: compute an ideal bottleneck bound.
3. Trace the CPU program's variables before adding hardware behavior: budget the queue.
4. Draw producers, consumers and the exact operation boundary for the task "Explain pinned versus ordinary host storage".
5. Separate what the small fixture establishes from what the real runtime must show: compare resident-data diagnostic.
6. Write a counterexample to an overbroad claim before you choose bounded worker experiments.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute serial time`. For the final claim use `Choose bounded worker experiments`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-088: Input pipelines and a hungry GPU.
Read courses/cuda/python/guides/cuda-088.md and courses/cuda/python/lessons/cuda-088.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
