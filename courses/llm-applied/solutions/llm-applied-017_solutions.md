# llm-applied-017: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

QLoRA combines a quantized frozen base with trainable low-rank adapters, allowing gradients to flow through computations involving the dequantized base into adapter parameters. The original method includes specific NormalFloat4 quantization, double quantization and paged optimizer mechanisms. A small CPU example cannot establish those GPU implementation or peak-memory properties.

This chapter deliberately implements a narrower mechanism: symmetric uniform signed4-bit quantization of a2x2 matrix, explicit packing of two nibbles per byte, dequantization tofloat32 for computation, and an actual adapter update while the packed base remains unchanged. The uniform codebook is notNF4, and the temporary float32 dequantized matrix means runtime memory does not equal packed storage. The distinction is part of the lesson. Measure output approximation error before training an adapter, then separate that error from the improvement achieved by the adapter objective.

**Quantized base:** Frozen weights represented by discrete codes and scale metadata.

**Nibble packing:** Storing two4-bit codes in one8-bit byte.

**Dequantization:** Reconstructing approximate floating-point values for computation.

**QLoRA boundary:** The distinction between this CPU mechanism and the full NF4/GPU method.

## Reading the implementation

Use scale=maxabs/7 and integer codes-7..7. Offset each code by 8 to fit a4-bit nibble, then pack low and high nibbles into oneuint8. Unpack with bit masks and shifts, subtract8, and multiply by the stored scale. The model uses the reconstructed frozen tensor plus a low-rank delta. Only adapterParameters enter the optimizer; packed bytes and scale are immutable fixture state.

## Derive the codes, bytes and forward error

The maximum absolute matrix entry is1.7, so the uniform scale is1.7/7=17/70, about0.242857. Dividing the entries by that scale and rounding gives codes[[0, -4], [7, -1]]. The allowed signed range contains15 values from-7 through7. Offsetting by eight produces unsigned nibbles[8, 4, 15, 7]; one of the16 possible nibble values is unused by this chosen symmetric scheme.

The first packed byte is8+(4 shifted left by 4)=8+64=72. The second is15+(7 shifted left by 4)=15+112=127. Unpacking the low four bits and then the high four bits restores those integer codes exactly. This is a lossless representation change of the already quantized integers. The information loss happened earlier when the original floating weights were rounded.

Using ideal decimal arithmetic, the reconstructed matrix is[[0, -34/35], [17/10, -17/70]]. Multiplying by x=[1, -2] gives[68/35, 153/70], about[1.942857, 2.185714]. The original output is[1.9, 2.1], so the errors are[3/70, 6/70], about[0.042857, 0.085714]. Actual float32 operations can differ slightly from these ideal-decimal values, which is why the executable comparison uses explicit tolerances.

Without clipping, nearest-grid rounding has per-weight absolute error at most \(\frac{\mathrm{scale}}{2}\). For a fixed output row, the triangle inequality gives an output error bound of(\(\frac{\mathrm{scale}}{2}\))*sum(abs(x)). Here that is(17/140)*3=51/140, about0.364286. The observed errors are smaller. This is a worst-case arithmetic bound for the declared uniform quantizer and input, not a bound on classification quality or generated-answer support.

The adapter code uses the stored output-by-input matrix convention: \(Y=X(W+AB)^{\mathsf T}\). A has shape[2, 1] and B[1, 2]. At \(B=0\), the A gradient is zero, while B can receive a gradient through nonzero A. With the initial one-row output above and mean squared loss against zero, the upstream output gradient equals Y because there are two output elements. Since A entries are 0.1, the first B gradient is 0.1*sum(Y)*X, approximately[0.412857, -0.825714]. The packed codes stay fixed while that differentiable branch changes.

The adapter's target is zero output on one input, not the original full-precision output. A falling loss therefore demonstrates optimization of the stated task; it does not prove recovery of the original weight matrix or correction of quantization on other inputs. A rank-one update fitting one vector leaves many unconstrained directions.

Two packed bytes plus a chosen float32 scale field would occupy six payload bytes in that logical serialized layout. The fixture's scale variable is a Python float and is not itself a four-byte on-disk record; the counter explicitly excludes object overhead. Computation also materializes a 16-byte float32 matrix. Calling six bytes the process's peak memory would combine incompatible accounting levels.

The original QLoRA method includes NF4, double quantization and paged-optimizer machinery. This lesson implements uniform codes and ordinary CPU adapter gradients instead. Those names identify different mechanisms; the local result does not inherit the paper's GPU measurements. [QLoRA](https://arxiv.org/abs/2305.14314).

### Interview reasoning with explanatory answers

**Is nibble round-trip equality evidence of lossless model quantization?** No. It proves that integer codes survive packing. Compare reconstructed weights and outputs with the original floating model to measure quantization error.

**Can a frozen quantized base still participate in gradient computation?** Yes. Its reconstructed values act as constants while derivatives flow into adapters and potentially earlier trainable operations. Freezing updates is different from disabling the whole graph.

**Why is the byte ratio insufficient for a memory claim?** The runtime also holds metadata, reconstructed or transient weights, activations, adapter parameters and optimizer/gradient state. The backend determines their actual lifetime and representation.

## Exercise 1: Quantize a fixed matrix

The question is: QuantizeW[[.1, -.9], [1.7, -.2]] with scale 1.7/7 andnearest-even rounding.

The shared scale is set by the largest magnitude. This is a simple uniform quantizer, not the distribution-awareNF4 codebook used in the referenced method.

```python
original = np.array([[0.1, -0.9], [1.7, -0.2]], dtype=np.float32)
scale = float(np.abs(original).max() / 7)
codes = np.clip(np.rint(original / scale), -7, 7).astype(np.int8)
np.testing.assert_array_equal(codes, [[0, -4], [7, -1]])
```

**Expected:** codes[[0, -4], [7, -1]].

**Verify:** Compare the computed values or written argument with codes[[0, -4], [7, -1]].

## Exercise 2: Pack and unpack real nibbles

The question is: Offset codes by 8, pack adjacent values into two bytes, then unpack.

The storage calculation is backed by actual byte packing. Keeping fourint8 codes without packing would use eight bits per code despite a nominal4-bit value range.

```python
unsigned = (codes.reshape(-1).astype(np.int16) + 8).astype(np.uint8)
packed = unsigned[::2] | (unsigned[1::2] << 4)
unpacked = np.empty(4, dtype=np.uint8)
unpacked[::2] = packed & 15
unpacked[1::2] = packed >> 4
restored_codes = (unpacked.astype(np.int16) - 8).astype(np.int8).reshape(2, 2)
np.testing.assert_array_equal(packed, [72, 127])
np.testing.assert_array_equal(restored_codes, codes)
```

**Expected:** packed bytes[72, 127]; round-trip codes exact.

**Verify:** Compare the computed values or written argument with packed bytes[72, 127]; round-trip codes exact.

## Exercise 3: Measure dequantization error

The question is: Reconstructfloat32weights and compareW@x forx[1, -2] with full precision.

A compact representation changes numerical behavior before any adaptation. The adapter experiment should not conceal that initial approximation error.

```python
dequantized = restored_codes.astype(np.float32) * scale
x_np = np.array([1.0, -2.0], dtype=np.float32)
reference = original @ x_np
approximate = dequantized @ x_np
np.testing.assert_allclose(reference, [1.9, 2.1], atol=1e-6, rtol=0)
assert np.isfinite(approximate).all() and np.max(np.abs(approximate - reference)) > 0
```

**Expected:** reference[1.9, 2.1]; finite nonzero approximation error.

**Verify:** Compare the computed values or written argument with reference[1.9, 2.1]; finite nonzero approximation error.

## Exercise 4: Train only a small adapter

The question is: Use frozen dequantizedW, rank 1 A/B and10SGD updates toward zero output.

Gradients reach adapter factors through a computation using fixed approximate weights. The base codes are not being optimized in this example.

```python
w = torch.tensor(dequantized)
a = nn.Parameter(torch.ones((2, 1)) * 0.1)
b = nn.Parameter(torch.zeros((1, 2)))
x = torch.tensor(x_np[None, :])
saved = packed.copy()
opt = torch.optim.SGD([a, b], lr=0.05)
initial = (x @ (w + a @ b).T).square().mean().item()
for _ in range(10):
    opt.zero_grad(set_to_none=True)
    loss = (x @ (w + a @ b).T).square().mean()
    loss.backward()
    opt.step()
final = (x @ (w + a @ b).T).square().mean().item()
assert final < initial and w.grad is None
np.testing.assert_array_equal(packed, saved)
```

**Expected:** adapter loss decreases; packed base bytes unchanged.

**Verify:** Compare the computed values or written argument with adapter loss decreases; packed base bytes unchanged.

## Exercise 5: Account for storage honestly

The question is: Count2 packed bytes plusonefloat32scale, and separately count the dequantized2x2float32buffer.

Packed artifact size is not peak training memory. The computation materializes floating-point weights and also uses adapters, gradients and optimizer state.

```python
storage = packed.nbytes + np.dtype("float32").itemsize
compute_buffer = dequantized.nbytes
assert storage == 6 and compute_buffer == 16
```

**Expected:** packed representation6 bytes; dequantizedbuffer16 bytes; overhead excluded.

**Verify:** Compare the computed values or written argument with packed representation6 bytes; dequantizedbuffer16 bytes; overhead excluded.

## Exercise 6: State what was not measured

The question is: Write a receipt distinguishing uniform4-bitCPU packing from NF4, double quantization, paged optimizers and GPU memory.

An accurate partial implementation is more useful than a misleading full-method label. The optional scale recipe must use its actual backend and produce separate measurements before making hardware claims.

```python
receipt = {
    "uniform_4bit_packing": True,
    "actual_adapter_update": True,
    "nf4": False,
    "double_quantization": False,
    "paged_optimizer": False,
    "gpu_peak_memory_measured": False,
}
assert receipt["actual_adapter_update"] and not any(
    receipt[k]
    for k in ["nf4", "double_quantization", "paged_optimizer", "gpu_peak_memory_measured"]
)
```

**Expected:** all four unimplemented claims explicitly False.

**Verify:** Compare the computed values or written argument with all four unimplemented claims explicitly False.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
