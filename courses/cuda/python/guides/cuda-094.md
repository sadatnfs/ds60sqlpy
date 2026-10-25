# cuda-094: Reproducible, restartable GPU training

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-069`, `cuda-087`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **list checkpoint fields**, **record sampler position**, and **define cross-hardware tolerance** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A training checkpoint is a state contract, not simply model weights. It may include optimizer moments, learning-rate schedule, gradient scaler, RNG states, sample position and preprocessing metadata. Saving at an update boundary avoids ambiguous partially accumulated gradients unless the format explicitly handles them. The storage must outlive the disposable execution process.

PyTorch state dictionaries and TensorFlow checkpoints track state differently; both need restore tests. Compare a short uninterrupted run with an interrupted/restored run under a declared tolerance and deterministic configuration. GPU algorithm choices and hardware changes can limit bitwise equality. A model checkpoint restores numerical training state, not an arbitrary live GPU context or in-flight stream.



## Worked examples

### Worked example 1

Momentum update \(v=0.9v+g\) stores v as well as weight w. Restoring w but resetting v changes the next update even with the same gradient.

### Worked example 2

A checkpoint after batch 2 should resume with batch 3. Replaying batch 2 or skipping batch 3 changes data exposure and invalidates a claimed exact continuation.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
w, v = 1.0, 0.5
checkpoint = {"w": w, "v": v, "next_batch": 3}
grad = 0.2
continued = checkpoint["w"] - 0.1 * (0.9 * checkpoint["v"] + grad)
weights_only = w - 0.1 * grad
assert abs(continued - 0.935) < 1e-12
assert continued != weights_only
print("CPU restart model:", continued, weights_only)
```

**Expected observation:** Correct restored update 0.935 differs from weights-only 0.98.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Checkpoint model and optimizer state, scaler and RNG state as applicable. The included in-memory momentum restore proves the numerical state contract; it is not durable storage or a process snapshot.

### TensorFlow

Use tracked variables and tf.train.Checkpoint for a durable prepared project. The included in-memory weight/velocity restore isolates the mathematical contract before file and optimizer-trackable integration.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Executable framework practice

The variant chooser offers **PyTorch on CPU**, **TensorFlow on CPU**, and separate **NVIDIA CUDA** versions. CPU versions force CPU placement. CUDA versions require the named GPU profile and refuse to silently fall back. Each complete program uses the same tiny deterministic objective, bounded tensors and local synthetic data. Read its source before running; a framework pass establishes only that variant and environment.

The checkpoint demonstration is in-memory. It teaches what state must be saved; it does not export a durable model artifact or preserve an in-flight device context. Advanced custom-op, distributed and engine-building projects remain separately prepared external workflows.

## Practice and transfer

### Exercise 1: List checkpoint fields

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **list checkpoint fields** in the examples above.

### Exercise 2: Compute momentum continuation

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **compute momentum continuation** in the examples above.

### Exercise 3: Diagnose weights-only restart

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **diagnose weights-only restart** in the examples above.

### Exercise 4: Record sampler position

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **record sampler position** in the examples above.

### Exercise 5: Choose a safe save boundary

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **choose a safe save boundary** in the examples above.

### Exercise 6: Define cross-hardware tolerance

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **define cross-hardware tolerance** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "List checkpoint fields".
2. Change one assumption in worked example 2 while preserving the declared contract: compute momentum continuation.
3. Trace the CPU program's variables before adding hardware behavior: diagnose weights-only restart.
4. Draw producers, consumers and the exact operation boundary for the task "Record sampler position".
5. Separate what the small fixture establishes from what the real runtime must show: choose a safe save boundary.
6. Write a counterexample to an overbroad claim before you define cross-hardware tolerance.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `List checkpoint fields`. For the final claim use `Define cross-hardware tolerance`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-094` using `courses/cuda/python/guides/cuda-094.md` and `courses/cuda/python/lessons/cuda-094.md`. Help me reason about Reproducible, restartable GPU training. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
