# cuda-099: Memory-saving training techniques

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-089`, `cuda-090`, `cuda-094`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute weighted accumulation**, **explain checkpoint recomputation**, and **design equal-update tests** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Gradient accumulation splits an effective batch across microbatches and delays the optimizer step. To match a full mean-loss gradient, weight each microbatch by its number of examples divided by the total. Equal division by microbatch count works only when sizes are equal. Batch-dependent layers, random state and optimizer timing can still break equivalence.

Activation checkpointing saves selected intermediates and recomputes others during backward. It exchanges compute for memory rather than eliminating arithmetic. PyTorch checkpoint utilities and TensorFlow recomputation mechanisms have framework-specific state and randomness rules. Frozen parameters still occupy storage, and upstream activations may remain necessary for trainable downstream components. Compare updates first, then measured peak memory and time.



## Worked examples

### Worked example 1

Microbatch mean gradients 2 and 8 over sizes 3 and 1 combine to\((3\times2+1\times8)/4=3.5\). Averaging the two means gives 5, which is wrong for the effective batch.

### Worked example 2

Checkpointing reduces retained activations by an illustrative 20 MiB but adds another forward computation. Its benefit depends on memory pressure and the recomputation cost.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
sizes, means = [3, 1], [2.0, 8.0]
weighted = sum(n * g for n, g in zip(sizes, means, strict=True)) / sum(sizes)
wrong = sum(means) / len(means)
assert weighted == 3.5 and wrong == 5
print("CPU accumulation oracle:", weighted, wrong)
```

**Expected observation:** Correct weighted gradient 3.5 versus incorrect 5.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Normalize each microbatch contribution by total effective examples and step once. Evaluate checkpoint recomputation separately, including random-state and nonreentrant/reentrant API choices for the pinned release.

### TensorFlow

Accumulate GradientTape gradients with example-count weighting. Use the prepared recomputation mechanism only after checking variable capture and stateful behavior; evaluate memory and extra forward work separately.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Executable framework practice

The variant chooser offers **PyTorch on CPU**, **TensorFlow on CPU**, and separate **NVIDIA CUDA** versions. CPU versions force CPU placement. CUDA versions require the named GPU profile and refuse to silently fall back. Each complete program uses the same tiny deterministic objective, bounded tensors and local synthetic data. Read its source before running; a framework pass establishes only that variant and environment.

The checkpoint demonstration is in-memory. It teaches what state must be saved; it does not export a durable model artifact or preserve an in-flight device context. Advanced custom-op, distributed and engine-building projects remain separately prepared external workflows.

## Practice and transfer

### Exercise 1: Compute weighted accumulation

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute weighted accumulation** in the examples above.

### Exercise 2: Find unequal-batch normalization error

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **find unequal-batch normalization error** in the examples above.

### Exercise 3: Place optimizer steps

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **place optimizer steps** in the examples above.

### Exercise 4: Explain checkpoint recomputation

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **explain checkpoint recomputation** in the examples above.

### Exercise 5: Account for frozen weights

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **account for frozen weights** in the examples above.

### Exercise 6: Design equal-update tests

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **design equal-update tests** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute weighted accumulation".
2. Change one assumption in worked example 2 while preserving the declared contract: find unequal-batch normalization error.
3. Trace the CPU program's variables before adding hardware behavior: place optimizer steps.
4. Draw producers, consumers and the exact operation boundary for the task "Explain checkpoint recomputation".
5. Separate what the small fixture establishes from what the real runtime must show: account for frozen weights.
6. Write a counterexample to an overbroad claim before you design equal-update tests.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute weighted accumulation`. For the final claim use `Design equal-update tests`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-099` using `courses/cuda/python/guides/cuda-099.md` and `courses/cuda/python/lessons/cuda-099.md`. Help me reason about Memory-saving training techniques. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
