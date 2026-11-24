# llm-034: explanatory solutions

Read these precision and quantization error budgets answers after attempting *Quantize a second matrix* through *Expose clipping and tie policy*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Measure output error* points to one step. `llm-034_solution.py` holds the assertions; this page explains how they test scale. Then try *Expose clipping and tie policy* on a fresh input you chose before looking.

## Mechanism review

Quantization represents approximate values with a limited set of integers and a scale. Symmetric signed int8 quantization here uses values -127..127, reserving a common zero-centered convention. A per-tensor scale shares one maximum magnitude across all weights; per-row scales adapt to different row ranges. Round-to-nearest-even determines ties under NumPy rint, and clipping handles values beyond the representable range. Dequantized weights are approximate, so measure error in the resulting matrix-vector product as well as weight error. Storage estimates must include scale metadata and distinguish raw numeric bytes from file or runtime overhead. One small matrix cannot establish universal model-quality preservation.

**Scale:** The real-valued spacing represented by one integer quantization step.

**Saturation:** A value clipped to the allowed integer boundary.

**Error budget:** A declared tolerance for the effect of approximation.

## Reading the implementation

For a nonzero block, \(\mathrm{scale}=\frac{\max(\left|W\right|)}{127}\). Quantize with rint(W/scale), clip and cast to int8. Dequantize by multiplying the integer array by its scale. Row scales use keepdims=True to preserve broadcasting along columns. A zero block needs an explicit nonzero scale convention. Compare against full precision W@x for x[1, -2].

## Exercise 1: Quantize a second matrix

The question is: Quantize W[[0.5, -1.2], [0.25, 2.0]] with one shared scale, the maximum absolute value divided by 127, and nearest-even rounding.

The largest magnitude maps exactly to 127, and every other entry is rounded on the same grid. Values such as 31.75 and 15.875 round to the nearest integer without a tie.

```python
w2 = np.array([[0.5, -1.2], [0.25, 2.0]])
scale2 = np.abs(w2).max() / 127
q2 = np.clip(np.rint(w2 / scale2), -127, 127).astype(np.int8)
np.testing.assert_array_equal(q2, [[32, -76], [16, 127]])
assert scale2 == 2 / 127
```

**Expected:** scale 2/127; integer array `[[32, -76], [16, 127]]`.

**Verify:** For *Quantize a second matrix*, a fresh-process check confirms `q2` equals `[[32, -76], [16, 127]]` and `scale2 == 2 / 127`.

## Exercise 2: Predict the reconstruction error

The question is: Dequantize the new integers and predict the largest absolute weight error and the bound it must respect.

Rounding moves each value by at most half a quantization step, here \(1/127\). The entry 0.5 maps to 31.75 steps and is rounded by a quarter step, the largest move in this matrix.

```python
err = np.abs(q2 * scale2 - w2).max()
np.testing.assert_allclose(err, 0.5 / 127, atol=1e-12, rtol=0)
assert err <= scale2 / 2
```

**Expected:** largest error 0.5/127, about 0.0039, within the half-step bound 1/127.

**Verify:** For *Predict the reconstruction error*, a fresh-process check confirms `err` matches `0.5 / 127` within 1e-12 and `err <= scale2 / 2`.

## Exercise 3: Measure output error

The question is: Dequantize the shared-scale matrix and compare its output with the reference.

Weight error can be amplified or cancelled by the input vector. Measuring the actual output difference makes the approximation relevant to this computation.

```python
restored = q.astype(float) * scale
output = restored @ x
error = float(np.max(np.abs(output - reference)))
assert np.isfinite(error) and 0 < error < 0.02
```

**Expected:** finite maximum absolute output error below 0.02.

**Verify:** For *Measure output error*, a fresh-process check confirms `np.isfinite(error)` and `0 < error < 0.02`.

## Exercise 4: Use per-row scales

The question is: Quantize each row using its own maximum absolute value.

Per-row scaling allocates resolution separately. It often changes errors, but no universal ordering is asserted from one fixture.

```python
scales = np.max(np.abs(w), axis=1, keepdims=True) / 127
qr = np.clip(np.rint(w / scales), -127, 127).astype(np.int8)
np.testing.assert_array_equal(qr[0], [14, -127])
np.testing.assert_allclose(scales[:, 0], [0.9 / 127, 1.7 / 127], atol=1e-12, rtol=0)
row_error = float(np.max(np.abs((qr.astype(float) * scales) @ x - reference)))
assert np.isfinite(row_error)
```

**Expected:** row scales 0.9/127 and 1.7/127; row 0 integers [14, -127].

**Verify:** For *Use per-row scales*, a fresh-process check confirms `qr[0]` equals `[14, -127]`; `scales[:, 0]` matches `[0.9 / 127, 1.7 / 127]` within 1e-12 and `np.isfinite(row_error)`.

## Exercise 5: Account for storage metadata

The question is: Count 4 int8 weights plus one float32 scale versus two float32 row scales.

For tiny arrays, scale metadata can dominate. A claimed compression ratio should state whether it counts metadata, alignment and runtime representations.

```python
per_tensor = 4 * 1 + 1 * 4
per_row = 4 * 1 + 2 * 4
assert (per_tensor, per_row) == (8, 12)
```

**Expected:** 8 bytes per-tensor; 12 bytes per-row; excluding overhead.

**Verify:** For *Account for storage metadata*, a fresh-process check confirms `(per_tensor, per_row) == (8, 12)`.

## Exercise 6: Expose clipping and tie policy

The question is: Quantize values exceeding a scale 1 range and inspect nearest-even rounding of 0.5, 1.5, 2.5.

The calibration maximum from one dataset does not guarantee future values remain in range. Counting saturation exposes a distinct source of error beyond ordinary rounding.

```python
values = np.array([127.0, 128.0])
rounded = np.rint(values)
saturated = np.count_nonzero((rounded < -127) | (rounded > 127))
assert saturated == 1
np.testing.assert_array_equal(np.rint([0.5, 1.5, 2.5]), [0, 2, 2])
```

**Expected:** one saturation for 128; ties round 0, 2, 2.

**Verify:** For *Expose clipping and tie policy*, a fresh-process check confirms `saturated == 1` and `np.rint([0.5, 1.5, 2.5])` equals `[0, 2, 2]`.

## Review after comparison

Change one input to *Use per-row scales* and predict the result first; keep *Account for storage metadata* failing beside the repair. Log a missing NumPy separately from a wrong scale value in `llm-034`.
