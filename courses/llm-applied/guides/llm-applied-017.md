# llm-applied-017: Quantized frozen bases, adapter gradients and QLoRA limits

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-016`, `llm-034`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Quantized adaptation changes both the stored representation of the base and the learning problem faced by an adapter. This chapter separates rounding, packing, computation and task fitting, then explains how to compare quality and resources without turning a byte count into a hardware claim.

## Purpose and mental model

QLoRA combines a quantized frozen base with trainable low-rank adapters, allowing gradients to flow through computations involving the dequantized base into adapter parameters. The original method includes specific NormalFloat4 quantization, double quantization and paged optimizer mechanisms. A small CPU example cannot establish those GPU implementation or peak-memory properties.

This chapter deliberately implements a narrower mechanism: symmetric uniform signed 4-bit quantization of a 2-by-2 matrix, explicit packing of two nibbles per byte, dequantization to float32 for computation, and an actual adapter update while the packed base remains unchanged. The uniform codebook is not NF4, and the temporary float32 dequantized matrix means runtime memory does not equal packed storage. The distinction is part of the lesson. Measure output approximation error before training an adapter, then separate that error from the improvement achieved by the adapter objective.

## Quantization introduces an approximation before adaptation begins

The Methods Desk team wants to reduce the resources required by a larger base model. Quantization replaces floating weights with a smaller set of representable values, usually together with scale or codebook metadata. That substitution changes the function before any adapter is trained. A later improvement must therefore be interpreted relative to both the original base and the quantized base.

The literal example uses a uniform grid with a scale derived from the largest absolute value. It rounds a2-by-2 matrix into signed codes, packs them into bytes and reconstructs approximate float32 values for computation. Each step has a different property: rounding loses numerical information, packing preserves the chosen codes, and dequantization reconstructs the approximation encoded by those codes.

The exact arithmetic below shows that a successful code round trip does not imply unchanged model output. The packed bytes can be perfectly correct while the reconstructed matrix produces a different result. That difference is the expected approximation error to measure before attributing a later task change to adaptation.

## Outliers explain a basic quantization tradeoff

Consider an illustrative uniform quantizer for weights[0.01,0.02,0.03,10] using the range-7 through 7. A single scale based on the maximum is \(\frac{10}{7}\), about 1.4286. The three small weights round to zero because the grid is too coarse to distinguish them, while the large value uses the extreme code.

If the first three weights were represented in a separate group, their maximum-based scale would be \(\frac{0.03}{7}\), about 0.004286. They could then be represented much more accurately, at the cost of additional group metadata and a different computation layout. This explains why granularity and scale policy matter. It is an example of uniform quantization reasoning, not an implementation of NF4 or a claim that a particular block size is optimal.

A nonuniform codebook makes another tradeoff by placing representable values more densely in some regions than others. The original QLoRA method uses specific mechanisms including NF4, double quantization and paged optimizers. The CPU fixture implements none of those particular backend features. Its value is that the simpler codes, packing and adapter gradients can be derived directly before reading a larger implementation.

## Weight reconstruction and task behavior are different objectives

Let W be the original matrix and W_q its reconstruction. An adapter gives W_q+AB under the chosen orientation and scale. If the training target were exact original-model parity on all inputs, the desired correction would relate to W-W_q. That difference need not be low rank. A constrained adapter may approximate it well on some input directions and poorly on others.

Task adaptation can have a different target entirely. The runnable example trains toward zero output on one input. Its falling loss establishes progress on that objective, not recovery of the original matrix. Many matrices agree on one input vector while behaving differently elsewhere. A tiny fit should therefore be accompanied by an explicit statement of which directions or tasks were evaluated.

Input magnitude also affects output error. Small weight errors can be amplified when multiplied by large or aligned input values. The layer-level bound derived later uses the input's absolute values to make that relationship visible. In a full network, nonlinearities and later layers add further dependencies, so a local reconstruction bound is not automatically a bound on generated-answer quality.

A useful comparison separates four conditions: original base, quantized base, adapted original base and adapted quantized base. Keeping the same held-out task contract across them helps identify the degradation introduced by quantization and the behavior learned by the adapter. Without the unadapted quantized control, an adapter's improvement may conceal how much quality was lost earlier.

## Gradients use the reconstructed computation

The frozen codes do not need to be differentiable for this adapter experiment. Their reconstruction acts as a constant in a computation that also contains trainable factors. Gradients can flow into those factors and, when required by the architecture, through the constant base computation to earlier trainable stages.

That is different from optimizing quantization decisions themselves. The fixture does not learn the integer codes, use a straight-through estimator for rounding or update the scale. Those would define additional algorithms with their own assumptions and tests. Keeping the base representation fixed makes it possible to verify that the observed changes come from the intended adapter parameters.

The first factor-gradient asymmetry remains the same as in the unquantized LoRA example: a zero B can give A a connected zero gradient while nonzero A allows B to learn. Quantizing W changes the forward values and therefore the loss gradient, but it does not remove the need to reason about factor orientation, denominator and optimizer membership.

## Account for what is stored and what is live

Packed payload size describes a serialization or storage representation. Peak training memory describes the largest simultaneous set of live allocations. The latter can include packed weights, scales, reconstructed blocks or matrices, adapter parameters, gradients, optimizer state, activations and temporary kernel buffers. Their lifetimes depend on the backend.

The tiny example explicitly materializes a float32 reconstruction. Its six-byte logical packed representation therefore cannot be reported as the total memory used by the calculation. A backend that dequantizes blocks transiently may behave differently, but that behavior must be observed rather than inferred from the word 4-bit.

For a domain-assistant decision, report numerical error, held-out task quality and measured resources separately. Include unsupported answers, exact identifiers and relevant retention tasks, because a small average loss change can conceal a costly domain failure. The next chapter applies the same discipline to comparing full and adapter fine-tuning under fixed evaluation conditions.

## Design decisions and when to use this method

Use quantized-base adaptation when a real backend supports the required dtype, kernels and optimizer behavior and when quality/resource comparisons justify it. The quantizer, compute dtype and adapter dtype are separate choices. Check whether the base is dequantized transiently or persistently, whether activations dominate memory, and whether optimizer states remain full precision.

Do not infer GPU memory savings from this CPU packing exercise. Do not call uniform signed 4-bit quantization NF4. Compare quantized and full-precision baselines on the same held-out tasks before adaptation, then compare adapted variants afterward. A trained adapter may compensate for some approximation error while overfitting the small training set. Record saturation, reconstruction error, task metrics, actual peak memory and the precise library/hardware versions independently.

Compare four states separately when studying quantized adaptation: original weights, reconstructed frozen weights, an untrained adapter on that reconstruction and the trained adapter. A useful task result should identify which transition changed the output and which objective the adapter optimized.

Treat storage format, compute dtype and trainable state as distinct budgets. The tiny packed array is real, but Python objects, scale metadata, dequantized tensors, activations and gradients remain separate allocations. Use the actual backend's measurements before claiming memory savings for a larger training job.

## Vocabulary and concepts

**Quantized base:** Frozen weights represented by discrete codes and scale metadata.

**Nibble packing:** Storing two 4-bit codes in one 8-bit byte.

**Dequantization:** Reconstructing approximate floating-point values for computation.

**QLoRA boundary:** The distinction between this CPU mechanism and the full NF4/GPU method.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-017/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `llm-torch-cpu` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-017.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use scale=maxabs/7 and integer codes-7..7. Offset each code by 8 to fit a 4-bit nibble, then pack low and high nibbles into one uint8. Unpack with bit masks and shifts, subtract 8, and multiply by the stored scale. The model uses the reconstructed frozen tensor plus a low-rank delta. Only adapterParameters enter the optimizer; packed bytes and scale are immutable fixture state.

## Derive the codes, bytes and forward error

The maximum absolute matrix entry is 1.7, so the uniform scale is \(\frac{1.7}{7}=\frac{17}{70}\), about 0.242857. Dividing the entries by that scale and rounding gives codes[[0, -4], [7, -1]]. The allowed signed range contains 15 values from-7 through 7. Offsetting by eight produces unsigned nibbles[8, 4, 15, 7]; one of the 16 possible nibble values is unused by this chosen symmetric scheme.

The first packed byte is 8+(4 shifted left by 4)=8+64=72. The second is 15+(7 shifted left by 4)=15+112=127. Unpacking the low four bits and then the high four bits restores those integer codes exactly. This is a lossless representation change of the already quantized integers. The information loss happened earlier when the original floating weights were rounded.

Using ideal decimal arithmetic, the reconstructed matrix is[[0, -34/35], [17/10, -17/70]]. Multiplying by x=[1, -2] gives[68/35, 153/70], about[1.942857, 2.185714]. The original output is[1.9, 2.1], so the errors are[3/70, 6/70], about[0.042857, 0.085714]. Actual float32 operations can differ slightly from these ideal-decimal values, which is why the executable comparison uses explicit tolerances.

Without clipping, nearest-grid rounding has per-weight absolute error at most \(\frac{\mathrm{scale}}{2}\). For a fixed output row, the triangle inequality gives an output error bound of(\(\frac{\mathrm{scale}}{2}\))*sum(abs(x)). Here that is(17/140)*3=51/140, about 0.364286. The observed errors are smaller. This is a worst-case arithmetic bound for the declared uniform quantizer and input, not a bound on classification quality or generated-answer support.

The adapter code uses the stored output-by-input matrix convention: \(Y=X(W+AB)^{\mathsf T}\). A has shape[2, 1] and B[1, 2]. At \(B=0\), the A gradient is zero, while B can receive a gradient through nonzero A. With the initial one-row output above and mean squared loss against zero, the upstream output gradient equals Y because there are two output elements. Since A entries are 0.1, the first B gradient is \(0.1\cdot \operatorname{sum}(Y)\cdot X\), approximately[0.412857, -0.825714]. The packed codes stay fixed while that differentiable branch changes.

The adapter's target is zero output on one input, not the original full-precision output. A falling loss therefore demonstrates optimization of the stated task; it does not prove recovery of the original weight matrix or correction of quantization on other inputs. A rank-one update fitting one vector leaves many unconstrained directions.

Two packed bytes plus a chosen float32 scale field would occupy six payload bytes in that logical serialized layout. The fixture's scale variable is a Python float and is not itself a four-byte on-disk record; the counter explicitly excludes object overhead. Computation also materializes a 16-byte float32 matrix. Calling six bytes the process's peak memory would combine incompatible accounting levels.

The original QLoRA method includes NF4, double quantization and paged-optimizer machinery. This lesson implements uniform codes and ordinary CPU adapter gradients instead. Those names identify different mechanisms; the local result does not inherit the paper's GPU measurements. [QLoRA](https://arxiv.org/abs/2305.14314).

### Interview reasoning with explanatory answers

**Is nibble round-trip equality evidence of lossless model quantization?** No. It proves that integer codes survive packing. Compare reconstructed weights and outputs with the original floating model to measure quantization error.

**Can a frozen quantized base still participate in gradient computation?** Yes. Its reconstructed values act as constants while derivatives flow into adapters and potentially earlier trainable operations. Freezing updates is different from disabling the whole graph.

**Why is the byte ratio insufficient for a memory claim?** The runtime also holds metadata, reconstructed or transient weights, activations, adapter parameters and optimizer/gradient state. The backend determines their actual lifetime and representation.

## Worked example / walkthrough

### Example A: Quantize a fixed matrix

The shared scale is set by the largest magnitude. This is a simple uniform quantizer, not the distribution-aware NF4 codebook used in the referenced method.

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

The storage calculation is backed by actual byte packing. Keeping four int8 codes without packing would use eight bits per code despite a nominal 4-bit value range.

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

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: codes[[0, -4], [7, -1]]. all four unimplemented claims explicitly False. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Quantize a fixed matrix.** QuantizeW[[.1, -.9], [1.7, -.2]] withscale \(\frac{1.7}{7}\) andnearest-even rounding.
   **Expected:** codes[[0, -4], [7, -1]].
   **Verify:** Save the assertion results for exercise 1, including codes[[0, -4], [7, -1]].

2. **Pack and unpack real nibbles.** Offset codes by 8, pack adjacent values into two bytes, then unpack.
   **Expected:** packed bytes[72, 127]; round-trip codes exact.
   **Verify:** Save the assertion results for exercise 2, including packed bytes[72, 127]; round-trip codes exact.

3. **Measure dequantization error.** Reconstruct float32 weights and compareW@x forx[1, -2] with full precision.
   **Expected:** reference[1.9, 2.1]; finite nonzero approximation error.
   **Verify:** Save the assertion results for exercise 3, including reference[1.9, 2.1]; finite nonzero approximation error.

4. **Train only a small adapter.** Use frozen dequantizedW, rank 1 A/B and 10SGD updates towardzero output.
   **Expected:** adapter loss decreases; packed base bytes unchanged.
   **Verify:** Save the assertion results for exercise 4, including adapter loss decreases; packed base bytes unchanged.

5. **Account for storage honestly.** Count 2 packed bytes plus one float32 scale, and separately count the dequantized 2x2float32buffer.
   **Expected:** packed representation 6 bytes; dequantized buffer 16 bytes; overheadexcluded.
   **Verify:** Save the assertion results for exercise 5, including packed representation 6 bytes; dequantized buffer 16 bytes; overheadexcluded.

6. **State what was not measured.** Write a receipt distinguishing uniform 4-bitCPU packing from NF4, double quantization, paged optimizers and GPU memory.
   **Expected:** all four unimplemented claims explicitly False.
   **Verify:** Save the assertion results for exercise 6, including all four unimplemented claims explicitly False.

## Common pitfalls and diagnosis

If reconstructed outputs are wrong, inspect scale, signed offset, nibble order and matrix orientation before training an adapter. If packing round trips but model output changes, that may be the expected rounding error rather than a packing failure.

If adapter loss falls, identify whether the target was original-model parity or another task. If a report claims NF4 or GPU savings, locate the actual codebook, backend and memory measurement. If a six-byte payload is presented as total memory, separate the serialization calculation from the live Python and Torch allocations.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Quantized base, Nibble packing, Dequantization using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

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
