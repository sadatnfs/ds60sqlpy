# cuda-103: Multi-GPU training on one host

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-087`, `cuda-088`, `cuda-092`, `cuda-094`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute equal-replica average**, **check complete sample coverage**, and **compare framework distribution contracts** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Data parallelism gives replicas different examples, computes gradients and combines those gradients before consistent updates. Rank identifies a participant; a process often owns one GPU. Correctness depends on sample partition, loss normalization, collective order and optimizer state, not merely launching more processes. Different effective batch sizes change the optimization problem.

PyTorch DistributedDataParallel typically uses one process per device and a suitable collective backend. TensorFlow MirroredStrategy coordinates replicas with its own distribution and loss-scaling conventions. Test against a single-device effective-batch reference. Unequal final batches require deliberate handling; repeated examples from padding must be counted. A CPU weighted-average model teaches semantics but cannot validate NCCL, GPU peer access or communication performance.



## Worked examples

### Worked example 1

Two equal-sized replicas with mean gradients 2 and 4 combine to 3. A single-device batch containing their examples should produce the same mathematical gradient.

### Worked example 2

With replica sample counts 3 and 1 and gradients 2 and 4, the global sample mean is 2.5, not 3. Normalization must match the intended data accounting.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
counts, gradients = [3, 1], [2.0, 4.0]
weighted = sum(n * g for n, g in zip(counts, gradients, strict=True)) / sum(counts)
assert weighted == 2.5
assert sum(gradients) / 2 == 3.0
print("CPU distributed-gradient oracle:", weighted)
```

**Expected observation:** Global example-weighted gradient 2.5.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Use an explicitly owned one-process-per-device DDP job with appropriate collective backend and bounded rendezvous. Validate the effective global batch and every rank's sample coverage.

### TensorFlow

Use MirroredStrategy for an explicitly prepared multi-device host. In custom loops apply the distribution-aware loss normalization and compare the resulting update with a single-device reference.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Practice and transfer

### Exercise 1: Compute equal-replica average

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute equal-replica average** in the examples above.

### Exercise 2: Handle unequal counts

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **handle unequal counts** in the examples above.

### Exercise 3: Assign rank and device

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **assign rank and device** in the examples above.

### Exercise 4: Check complete sample coverage

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **check complete sample coverage** in the examples above.

### Exercise 5: Design collective failure handling

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design collective failure handling** in the examples above.

### Exercise 6: Compare framework distribution contracts

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **compare framework distribution contracts** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute equal-replica average".
2. Change one assumption in worked example 2 while preserving the declared contract: handle unequal counts.
3. Trace the CPU program's variables before adding hardware behavior: assign rank and device.
4. Draw producers, consumers and the exact operation boundary for the task "Check complete sample coverage".
5. Separate what the small fixture establishes from what the real runtime must show: design collective failure handling.
6. Write a counterexample to an overbroad claim before you compare framework distribution contracts.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute equal-replica average`. For the final claim use `Compare framework distribution contracts`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-103` using `courses/cuda/python/guides/cuda-103.md` and `courses/cuda/python/lessons/cuda-103.md`. Help me reason about Multi-GPU training on one host. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
