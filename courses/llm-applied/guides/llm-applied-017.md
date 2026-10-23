# llm-applied-017: Quantized frozen bases, adapter gradients and QLoRA limits

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-016`, `llm-034`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

QLoRA combines a quantized frozen base with trainable low-rank adapters, allowing gradients to flow through computations involving the dequantized base into adapter parameters. The central investigation is concrete: QuantizeW[[.1, -.9], [1.7, -.2]] withscale1.7/7 andnearest-even rounding. The finish condition is codes[[0, -4], [7, -1]]. all four unimplemented claims explicitlyFalse. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

QLoRA combines a quantized frozen base with trainable low-rank adapters, allowing gradients to flow through computations involving the dequantized base into adapter parameters. The original method includes specific NormalFloat4 quantization, double quantization and paged optimizer mechanisms. A small CPU example cannot establish those GPU implementation or peak-memory properties.

This chapter deliberately implements a narrower mechanism: symmetric uniform signed4-bit quantization of a2x2 matrix, explicit packing of two nibbles per byte, dequantization tofloat32 for computation, and an actual adapter update while the packed base remains unchanged. The uniform codebook is notNF4, and the temporary float32 dequantized matrix means runtime memory does not equal packed storage. The distinction is part of the lesson. Measure output approximation error before training an adapter, then separate that error from the improvement achieved by the adapter objective.

## Design decisions and when to use this method

Use quantized-base adaptation when a real backend supports the required dtype, kernels and optimizer behavior and when quality/resource comparisons justify it. The quantizer, compute dtype and adapter dtype are separate choices. Check whether the base is dequantized transiently or persistently, whether activations dominate memory, and whether optimizer states remain full precision.

Do not infer GPU memory savings from this CPU packing exercise. Do not call uniform signed4-bit quantizationNF4. Compare quantized and full-precision baselines on the same held-out tasks before adaptation, then compare adapted variants afterward. A trained adapter may compensate for some approximation error while overfitting the small training set. Record saturation, reconstruction error, task metrics, actual peak memory and the precise library/hardware versions independently.

## Vocabulary and concepts

**Quantized base:** Frozen weights represented by discrete codes and scale metadata.

**Nibble packing:** Storing two4-bit codes in one8-bit byte.

**Dequantization:** Reconstructing approximate floating-point values for computation.

**QLoRA boundary:** The distinction between this CPU mechanism and the full NF4/GPU method.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-017/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-017.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-017.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use scale=maxabs/7 and integer codes-7..7. Offset each code by 8 to fit a4-bit nibble, then pack low and high nibbles into oneuint8. Unpack with bit masks and shifts, subtract8, and multiply by the stored scale. The model uses the reconstructed frozen tensor plus a low-rank delta. Only adapterParameters enter the optimizer; packed bytes and scale are immutable fixture state.

## Worked example / walkthrough

### Example A: Quantize a fixed matrix

The shared scale is set by the largest magnitude. This is a simple uniform quantizer, not the distribution-awareNF4 codebook used in the referenced method.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

original=np.array([[.1,-.9],[1.7,-.2]],dtype=np.float32); scale=float(np.abs(original).max()/7)
codes=np.clip(np.rint(original/scale),-7,7).astype(np.int8)
np.testing.assert_array_equal(codes,[[0,-4],[7,-1]])
```

**Expected:** codes[[0, -4], [7, -1]].

### Example B: Pack and unpack real nibbles

The storage calculation is backed by actual byte packing. Keeping fourint8 codes without packing would use eight bits per code despite a nominal4-bit value range.

```python
unsigned=(codes.reshape(-1).astype(np.int16)+8).astype(np.uint8)
packed=unsigned[::2] | (unsigned[1::2]<<4)
unpacked=np.empty(4,dtype=np.uint8); unpacked[::2]=packed&15; unpacked[1::2]=packed>>4
restored_codes=(unpacked.astype(np.int16)-8).astype(np.int8).reshape(2,2)
np.testing.assert_array_equal(packed,[72,127]); np.testing.assert_array_equal(restored_codes,codes)
```

**Expected:** packed bytes[72, 127]; round-trip codes exact.

### Example C: Measure dequantization error

A compact representation changes numerical behavior before any adaptation. The adapter experiment should not conceal that initial approximation error.

```python
dequantized=restored_codes.astype(np.float32)*scale; x_np=np.array([1.,-2.],dtype=np.float32)
reference=original@x_np; approximate=dequantized@x_np
np.testing.assert_allclose(reference,[1.9,2.1],atol=1e-6,rtol=0)
assert np.isfinite(approximate).all() and np.max(np.abs(approximate-reference))>0
```

**Expected:** reference[1.9, 2.1]; finite nonzero approximation error.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: codes[[0, -4], [7, -1]]. all four unimplemented claims explicitlyFalse. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Quantize a fixed matrix.** QuantizeW[[.1, -.9], [1.7, -.2]] withscale1.7/7 andnearest-even rounding.
   **Expected:** codes[[0, -4], [7, -1]].
   **Verify:** Save the assertion results for exercise 1, including codes[[0, -4], [7, -1]].

2. **Pack and unpack real nibbles.** Offset codes by 8, pack adjacent values into two bytes, then unpack.
   **Expected:** packed bytes[72, 127]; round-trip codes exact.
   **Verify:** Save the assertion results for exercise 2, including packed bytes[72, 127]; round-trip codes exact.

3. **Measure dequantization error.** Reconstructfloat32weights and compareW@x forx[1, -2] with full precision.
   **Expected:** reference[1.9, 2.1]; finite nonzero approximation error.
   **Verify:** Save the assertion results for exercise 3, including reference[1.9, 2.1]; finite nonzero approximation error.

4. **Train only a small adapter.** Use frozen dequantizedW, rank 1 A/B and10SGD updates towardzero output.
   **Expected:** adapter loss decreases; packed base bytes unchanged.
   **Verify:** Save the assertion results for exercise 4, including adapter loss decreases; packed base bytes unchanged.

5. **Account for storage honestly.** Count2 packed bytes plusonefloat32scale, and separately count the dequantized2x2float32buffer.
   **Expected:** packed representation6 bytes; dequantizedbuffer16 bytes; overheadexcluded.
   **Verify:** Save the assertion results for exercise 5, including packed representation6 bytes; dequantizedbuffer16 bytes; overheadexcluded.

6. **State what was not measured.** Write a receipt distinguishing uniform4-bitCPU packing fromNF4, double quantization, paged optimizers andGPU memory.
   **Expected:** all four unimplemented claims explicitlyFalse.
   **Verify:** Save the assertion results for exercise 6, including all four unimplemented claims explicitlyFalse.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Quantized base, Nibble packing, Dequantization using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-016`, `llm-034` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [QLoRA](https://arxiv.org/abs/2305.14314), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-017, Quantized frozen bases, adapter gradients and QLoRA limits.
Read courses/llm-applied/guides/llm-applied-017.md and courses/llm-applied/lessons/llm-applied-017.py. Direct prerequisites: `llm-applied-016`, `llm-034`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
