# cuda-090: Mixed precision as a numerical experiment

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-006`, `cuda-087`, `cuda-089`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **calculate scaled and unscaled values**, **compare fp16 and bf16 concepts**, and **record quality and throughput separately** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Lower precision trades representable range and significant digits against memory and arithmetic capability. Mixed precision deliberately assigns different operations or accumulations to different dtypes. It is not the same as converting every tensor to half. Reductions, normalization and small gradients often need special care; bf16 and fp16 have different range/precision tradeoffs even though both use 16 bits.

PyTorch autocast selects operation dtypes, and gradient scaling is appropriate for supported fp16 training workflows. Unscale before clipping so the clipping threshold has its intended meaning. TensorFlow mixed-precision policies and loss-scaling optimizers provide the corresponding framework mechanisms, with APIs tied to the pinned Keras release. Validate finite gradients and held-out behavior before comparing memory or speed.

## Precision policy, scaling and the optimizer boundary

A floating-point format allocates bits to sign, exponent and significand. More exponent range reduces overflow and underflow; more significand precision distinguishes nearby values. fp16 and bfloat16 have the same storage width but different allocations, so they are not interchangeable numerical policies. Hardware support for their fast operations must also be checked independently of a Python dtype existing.

Loss scaling multiplies the scalar loss by a positive scale \(s\), which multiplies its gradients by \(s\). Before the optimizer applies an update, divide by that same scale. In exact arithmetic:

\[
\nabla(sL)/s=\nabla L.
\]

The purpose is to change intermediate representability in finite precision, not change the intended learning rate. Dynamic scaling detects nonfinite gradients and adjusts according to the framework's supported procedure. A skipped optimizer update and a completed batch are different counters; a training report should not hide repeated overflow by reporting only loop iterations.

Gradient clipping belongs after unscaling because its threshold is defined in the original gradient units. Likewise, accumulating multiple microbatches needs a consistent scaling/normalization strategy across the effective batch. Do not update the scale halfway through a set of gradients that will be combined under one scale assumption.

For PyTorch, place forward and loss computation in the selected autocast context and follow the pinned `torch.amp` scaler sequence. For TensorFlow/Keras, select the dtype policy before layer construction, inspect variable dtype versus compute dtype, and follow that release's loss-scaling optimizer API. The supplied CPU scaling model is a mathematical explanation; it does not claim that either framework selected tensor cores. Qualification compares finite gradients, update direction, short loss trajectory, held-out metric, memory and synchronized completed-step timing against full precision.


## Worked examples

### Worked example 1

Multiplying a small gradient by scale 1024 before backpropagation can keep intermediate values away from underflow. Dividing the computed gradient by 1024 before the optimizer restores the intended update.

### Worked example 2

Clipping a scaled gradient of 512 with threshold 1 and then unscaling produces 1/1024, not the intended clipped original gradient 0.5. Operation order changes training.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
gradient = 0.5
scale = 1024
scaled = gradient * scale
correct = min(scaled / scale, 1.0)
wrong = min(scaled, 1.0) / scale
assert correct == 0.5 and wrong == 1 / 1024
print("CPU scaling model:", correct, wrong)
```

**Expected observation:** Correct gradient 0.5; incorrect clipping order yields 0.0009765625.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Use torch.autocast around supported forward/loss operations. The CUDA fp16 workflow can use torch.amp.GradScaler; unscale before gradient clipping, then step and update the scaler.

### TensorFlow

Select a Keras mixed-precision policy before building layers. Use the pinned release's loss-scaling optimizer contract and inspect variable, compute and output dtypes separately.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Practice and transfer

### Exercise 1: Calculate scaled and unscaled values

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **calculate scaled and unscaled values** in the examples above.

### Exercise 2: Explain overflow detection

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **explain overflow detection** in the examples above.

### Exercise 3: Place clipping correctly

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **place clipping correctly** in the examples above.

### Exercise 4: Compare fp16 and bf16 concepts

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **compare fp16 and bf16 concepts** in the examples above.

### Exercise 5: Design a full-precision baseline

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **design a full-precision baseline** in the examples above.

### Exercise 6: Record quality and throughput separately

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **record quality and throughput separately** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Calculate scaled and unscaled values".
2. Change one assumption in worked example 2 while preserving the declared contract: explain overflow detection.
3. Trace the CPU program's variables before adding hardware behavior: place clipping correctly.
4. Draw producers, consumers and the exact operation boundary for the task "Compare fp16 and bf16 concepts".
5. Separate what the small fixture establishes from what the real runtime must show: design a full-precision baseline.
6. Write a counterexample to an overbroad claim before you record quality and throughput separately.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Calculate scaled and unscaled values`. For the final claim use `Record quality and throughput separately`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-090` using `courses/cuda/python/guides/cuda-090.md` and `courses/cuda/python/lessons/cuda-090.md`. Help me reason about Mixed precision as a numerical experiment. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
