# cuda-105: Distributed training beyond one host

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-103`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute barrier time**, **define checkpoint consistency**, and **design owned-host cleanup** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Across hosts, the network joins GPU compute and storage as a first-class resource. A rendezvous establishes participants; collectives require compatible ordering and membership. Data parallelism replicates parameters, tensor parallelism partitions operations, pipeline parallelism partitions layers, and state sharding distributes selected model or optimizer state. Their communication patterns differ.

Stragglers delay synchronized steps. Worker failure requires a coordinated stop or a deliberately implemented recovery protocol; independently retrying one rank can hang the rest. Checkpoints need a consistent global boundary and data-position contract. This lesson uses diagrams and synthetic timelines by default. Actual multi-host work requires explicitly owned hosts, bounded access, suitable networking and separate PyTorch/TensorFlow qualification. Nothing in the browser creates a cluster.



### Key terms

- **Rendezvous:** The startup step in which processes discover each other and agree on ranks and world size.
- **Tensor parallelism:** Splitting individual layer weights across devices, which requires communication inside each layer.
- **Pipeline parallelism:** Placing consecutive layer groups on different devices and streaming microbatches through them.
- **State sharding:** Partitioning parameters, gradients or optimizer state across ranks to reduce per-device memory.
- **Communication budget:** The time and bandwidth available for collectives relative to compute in each step.

## Worked examples

### Worked example 1

Three ranks taking 10,12 and 30 ms before a barrier yield at least 30 ms compute-phase latency, even though their average is 17.3 ms.

### Worked example 2

A checkpoint assembled from rank 0 at step 10 and rank 1 at step 11 is not a coherent global state unless a protocol explicitly reconciles that difference.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
rank_ms = [10, 12, 30]
assert max(rank_ms) == 30
steps = {"rank0": 10, "rank1": 11}
consistent = len(set(steps.values())) == 1
assert not consistent
print("CPU distributed trace: barrier", max(rank_ms), "ms; checkpoint consistent", consistent)
```

**Expected observation:** Barrier 30 ms; mixed-step checkpoint rejected.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `rank_ms` | `[10, 12, 30]` |
| `steps` | `{'rank0': 10, 'rank1': 11}` |
| `consistent` | `False` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Compute barrier time

**Trap to avoid:** Reporting the average rank time predicts 17.3 ms and hides 13 ms of idle time per step, which makes adding ranks look more efficient than it is.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Compare parallelism types

**Trap to avoid:** Using data parallelism for a model that does not fit on one device fails immediately, because each replica needs all parameters, gradients and optimizer state.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Diagnose a missing rank

**Trap to avoid:** Restarting only the missing rank while the others wait in a collective fails, because the new process does not join the existing communicator state.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Define checkpoint consistency

**Trap to avoid:** Accepting each rank's latest file independently produces mixed-step checkpoints whenever a failure occurs during saving.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Budget communication

**Trap to avoid:** Estimating communication from the parameter count without element size or frequency misses that float32 gradients are four bytes and some collectives run several times per step.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Design owned-host cleanup

**Trap to avoid:** Killing every GPU process on a host stops other users' jobs, while deleting the output directory loses valid checkpoints.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute barrier time".
2. Change one assumption in worked example 2 while preserving the declared contract: compare parallelism types.
3. Trace the CPU program's variables before adding hardware behavior: diagnose a missing rank.
4. Draw producers, consumers and the exact operation boundary for the task "Define checkpoint consistency".
5. Separate what the small fixture establishes from what the real runtime must show: budget communication.
6. Write a counterexample to an overbroad claim before you design owned-host cleanup.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute barrier time`. For the final claim use `Design owned-host cleanup`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

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
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-105: Distributed training beyond one host.
Read courses/cuda/python/guides/cuda-105.md and courses/cuda/python/lessons/cuda-105.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
