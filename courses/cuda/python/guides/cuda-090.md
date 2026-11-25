# cuda-090: Mixed precision as a numerical experiment

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-006`, `cuda-087`, `cuda-089`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Calculate scaled and unscaled values.
- Explain overflow detection.
- Place clipping correctly.
- Compare fp16 and bf16 concepts.
- Design a full-precision baseline.
- Record quality and throughput separately.

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


### Key terms

- **Float16 (fp16):** A 16-bit float with 5 exponent bits and a narrow range, so small gradients can underflow.
- **Bfloat16 (bf16):** A 16-bit float with the same 8 exponent bits as float32 but fewer mantissa bits, trading precision for range.
- **Loss scaling:** Multiplying the loss before backward so fp16 gradients stay representable, then unscaling gradients before clipping and the update.
- **Overflow detection:** Checking unscaled gradients for infinity or NaN, skipping that step and lowering the scale.
- **Master weights:** A float32 copy of parameters that receives updates so small increments are not lost to low precision.

## Worked examples

### Worked example 1

Multiplying a small gradient by scale 1024 before backpropagation can keep intermediate values away from underflow. Dividing the computed gradient by 1024 before the optimizer restores the intended update.

### Worked example 2

Clipping a scaled gradient of 512 with threshold 1 and then unscaling produces 1/1024, not the intended clipped original gradient 0.5. Operation order changes training.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-090_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-090_cpu.py
```

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

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `gradient` | `0.5` |
| `scale` | `1024` |
| `scaled` | `512.0` |
| `correct` | `0.5` |
| `wrong` | `0.0009765625` |

## Equal framework lanes

### PyTorch

Use torch.autocast around supported forward/loss operations. The CUDA fp16 workflow can use torch.amp.GradScaler; unscale before gradient clipping, then step and update the scaler.

### TensorFlow

Select a Keras mixed-precision policy before building layers. Use the pinned release's loss-scaling optimizer contract and inspect variable, compute and output dtypes separately.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-090.md) before opening hints.

### Exercise 1: Calculate scaled and unscaled values

**Trap to avoid:** Unscaling twice, once manually and once by the scaler, produces `0.5/1024`, an update so small that training appears to stall without any error.

### Exercise 2: Explain overflow detection

**Trap to avoid:** Replacing infinities with zero, or clipping them, so the step can proceed corrupts the update with values unrelated to the true gradient.

### Exercise 3: Place clipping correctly

**Trap to avoid:** Clipping the scaled 512 to 1 and then unscaling gives `1/1024 = 0.0009765625`, the wrong value the reference asserts for the reversed order. Training then barely moves.

### Exercise 4: Compare fp16 and bf16 concepts

**Trap to avoid:** Assuming both 16-bit formats behave the same leads to dropping loss scaling for float16, where small gradients flush to zero.

### Exercise 5: Design a full-precision baseline

**Trap to avoid:** Comparing the mixed-precision run with an older float32 run using a different seed attributes noise to precision.

### Exercise 6: Record quality and throughput separately

**Trap to avoid:** Reporting the speedup without the quality comparison can justify a configuration that fails to train properly.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Multiply the gradient by the scale before the backward pass, then divide by the same scale once.
2. Ask what a supported scaler does when the scaled gradient becomes infinite or not a number.
3. Decide which representation the clipping threshold refers to, scaled or original.
4. Compare how many bits fp16 and bf16 spend on the exponent and on the fraction.
5. Run the same initialization, batch and loss at full precision as your reference.
6. Report accuracy and gradient checks separately from memory and speed.

## Common mistakes and self-check

A common mistake is clipping gradients while they are still scaled. In worked example 2 a scaled gradient of 512 clipped at threshold 1 and then unscaled becomes 0.0009765625 instead of the intended 0.5. Another mistake is converting every tensor to half precision and calling it mixed precision, which can break reductions and normalization. Fix both by unscaling before clipping and by letting the framework's autocast or policy choose operation dtypes.

**Evidence limit:** The reference reproduces 0.5 for the correct order and 0.0009765625 for the wrong one with ordinary Python floats. It does not run autocast, a gradient scaler or a Keras policy, so dtype choices and overflow handling need the pinned framework.

1. Why scale the loss in fp16 training?
2. How do fp16 and bf16 differ although both use 16 bits?
3. Can a speedup excuse a numerical failure?

Answers: [self-check answers](../solutions/cuda-090_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-090: Mixed precision as a numerical experiment.
Read courses/cuda/python/guides/cuda-090.md and courses/cuda/python/lessons/cuda-090.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
