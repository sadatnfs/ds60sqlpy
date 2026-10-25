# cuda-089: Allocations and out-of-memory reasoning

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-070`, `cuda-087`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **build a parameter ledger**, **diagnose a retained graph**, and **design a safe batch-size experiment** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Training memory contains parameters, gradients, optimizer state, saved activations, temporary workspaces and allocator reserve. These terms respond differently to batch size and precision. Adam commonly maintains two moment tensors, while mixed-precision implementations may retain additional master state. Count the actual implementation instead of applying one universal bytes-per-parameter rule.

PyTorch distinguishes allocated and reserved memory and can retain autograd graphs when losses or outputs remain attached. TensorFlow memory growth changes reservation behavior but does not make an oversized live workload fit. Both require bounded experiments with the same model and controlled batch changes. Host container limits do not generally impose a per-process GPU-memory quota. Avoid intentional OOM on shared devices and use supplied failure traces instead.



## Worked examples

### Worked example 1

For 1000 float32 parameters, parameters, gradients and two moment arrays total 16000 bytes before activations and workspaces. This is an illustrative ledger, not a full framework prediction.

### Worked example 2

Doubling batch size can approximately double saved activation payload while leaving parameter count unchanged. Retaining every step loss tensor can grow a graph independently of batch size.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
params = 1000
state_bytes = params * 4 * 4
activations = 8 * 128 * 4
assert state_bytes == 16000 and activations == 4096
assert state_bytes + 2 * activations == 24192
print("CPU memory ledger:", state_bytes, activations)
```

**Expected observation:** State 16000 bytes and activation 4096 bytes for the example.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Distinguish memory_allocated from memory_reserved. Retained tensors and attached loss histories keep graph storage live; scalar summaries should be detached deliberately.

### TensorFlow

Configure memory growth before device initialization when using it. Inspect current/peak allocator observations where supported and separate reservation policy from the required live tensors.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Executable framework practice

The variant chooser offers **PyTorch on CPU**, **TensorFlow on CPU**, and separate **NVIDIA CUDA** versions. CPU versions force CPU placement. CUDA versions require the named GPU profile and refuse to silently fall back. Each complete program uses the same tiny deterministic objective, bounded tensors and local synthetic data. Read its source before running; a framework pass establishes only that variant and environment.

The checkpoint demonstration is in-memory. It teaches what state must be saved; it does not export a durable model artifact or preserve an in-flight device context. Advanced custom-op, distributed and engine-building projects remain separately prepared external workflows.

## Practice and transfer

### Exercise 1: Build a parameter ledger

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **build a parameter ledger** in the examples above.

### Exercise 2: Add activation bytes

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **add activation bytes** in the examples above.

### Exercise 3: Separate reserve and live usage

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **separate reserve and live usage** in the examples above.

### Exercise 4: Diagnose a retained graph

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **diagnose a retained graph** in the examples above.

### Exercise 5: Explain memory growth

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **explain memory growth** in the examples above.

### Exercise 6: Design a safe batch-size experiment

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **design a safe batch-size experiment** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Build a parameter ledger".
2. Change one assumption in worked example 2 while preserving the declared contract: add activation bytes.
3. Trace the CPU program's variables before adding hardware behavior: separate reserve and live usage.
4. Draw producers, consumers and the exact operation boundary for the task "Diagnose a retained graph".
5. Separate what the small fixture establishes from what the real runtime must show: explain memory growth.
6. Write a counterexample to an overbroad claim before you design a safe batch-size experiment.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Build a parameter ledger`. For the final claim use `Design a safe batch-size experiment`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-089` using `courses/cuda/python/guides/cuda-089.md` and `courses/cuda/python/lessons/cuda-089.md`. Help me reason about Allocations and out-of-memory reasoning. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
