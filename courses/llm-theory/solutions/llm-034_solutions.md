# llm-034: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Quantization represents approximate values with a limited set of integers and a scale. Symmetric signed int8 quantization here uses values-127..127, reserving a common zero-centered convention. A per-tensor scale shares one maximum magnitude across all weights; per-row scales adapt to different row ranges. Round-to-nearest-even determines ties under NumPy rint, and clipping handles values beyond the representable range. Dequantized weights are approximate, so measure error in the resulting matrix-vector product as well as weight error. Storage estimates must include scale metadata and distinguish raw numeric bytes from file or runtime overhead. One small matrix cannot establish universal model-quality preservation.

**Scale:** The real-valued spacing represented by one integer quantization step.

**Saturation:** A value clipped to the allowed integer boundary.

**Error budget:** A declared tolerance for the effect of approximation.

## Reading the implementation

For a nonzero block, \(\mathrm{scale}=\frac{\max(\left|W\right|)}{127}\). Quantize with rint(W/scale), clip and cast toint8. Dequantize by multiplying the integer array by its scale. Row scales use keepdims=True to preserve broadcasting along columns. A zero block needs an explicit nonzero scale convention. Compare against full precision W@x for x[1,-2].

## Exercise 1: Compute the full-precision reference

The question is: Multiply W[[.1,-.9],[1.7,-.2]] byx[1,-2].

The reference keeps the original floating-point values. It must not be recomputed from dequantized weights, which would erase the approximation being measured.

```python
w = np.array([[0.1, -0.9], [1.7, -0.2]])
x = np.array([1.0, -2.0])
reference = w @ x
np.testing.assert_allclose(reference, [1.9, 2.1], atol=1e-12, rtol=0)
```

**Expected:** output[1.9,2.1].

**Verify:** Compare the computed values or written argument with output[1.9,2.1].

## Exercise 2: Quantize one shared scale

The question is: Use maxabs1.7 divided by127,nearest-even rounding and signed int8.

The smaller first row uses the scale set by the largest value in the second row. Its values therefore receive coarser relative resolution.

```python
scale = np.abs(w).max() / 127
raw = np.rint(w / scale)
q = np.clip(raw, -127, 127).astype(np.int8)
np.testing.assert_array_equal(q, [[7, -67], [127, -15]])
assert scale == 1.7 / 127
```

**Expected:** scale1.7/127;integer array[[7,-67],[127,-15]].

**Verify:** Compare the computed values or written argument with scale1.7/127;integer array[[7,-67],[127,-15]].

## Exercise 3: Measure output error

The question is: Dequantize the shared-scale matrix and compare its output with the reference.

Weight error can be amplified or cancelled by the input vector. Measuring the actual output difference makes the approximation relevant to this computation.

```python
restored = q.astype(float) * scale
output = restored @ x
error = float(np.max(np.abs(output - reference)))
assert np.isfinite(error) and 0 < error < 0.02
```

**Expected:** finite maximum absolute output error below.02.

**Verify:** Compare the computed values or written argument with finite maximum absolute output error below.02.

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

**Expected:** row scales.9/127 and 1.7/127;row0 integers[14,-127].

**Verify:** Compare the computed values or written argument with row scales.9/127 and 1.7/127;row0 integers[14,-127].

## Exercise 5: Account for storage metadata

The question is: Count4 int8 weights plusone float32 scale versus two float32 row scales.

For tiny arrays, scale metadata can dominate. A claimed compression ratio should state whether it counts metadata, alignment and runtime representations.

```python
per_tensor = 4 * 1 + 1 * 4
per_row = 4 * 1 + 2 * 4
assert (per_tensor, per_row) == (8, 12)
```

**Expected:** 8 bytes per-tensor;12 bytes per-row;excluding overhead.

**Verify:** Compare the computed values or written argument with 8 bytes per-tensor;12 bytes per-row;excluding overhead.

## Exercise 6: Expose clipping and tie policy

The question is: Quantize values exceeding a scale1 range and inspect nearest-even rounding of.5,1.5,2.5.

The calibration maximum from one dataset does not guarantee future values remain in range. Counting saturation exposes a distinct source of error beyond ordinary rounding.

```python
values = np.array([127.0, 128.0])
rounded = np.rint(values)
saturated = np.count_nonzero((rounded < -127) | (rounded > 127))
assert saturated == 1
np.testing.assert_array_equal(np.rint([0.5, 1.5, 2.5]), [0, 2, 2])
```

**Expected:** one saturation for128;ties round0,2,2.

**Verify:** Compare the computed values or written argument with one saturation for128;ties round0,2,2.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
