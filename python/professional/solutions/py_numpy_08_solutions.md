# python-numpy-08: Explained reference solutions

These answers accompany [Sliding Windows, Convolution, and FFT Boundaries](../companion-guides/py_numpy_08.md). Compare after an honest attempt. The [complete standalone executable reference](py_numpy_08_solution.py) includes imports, shared validation helpers and a `main()` that exercises every contract. The snippets below use those helpers; run the complete reference for a fresh-process check. Each named function matches the learner artifact.

## Exercise 1: Inspect overlapping storage

**Contract: `window_view`.** Return the default read-only sliding_window_view of a nonempty finite real one-dimensional array with the given width. Preserve dtype and shared storage. Require integer width from 1 through length, excluding bool; reject invalid inputs with ValueError. Source mutations remain visible. Read-only does not mean an immutable snapshot.

**Expected:** arange(6) with width 3 gives shape (4, 3); source index 2 appears in three overlapping locations. Assignment through the view fails, but changing the source changes those locations.

```python
def window_view(values: np.ndarray, width: int) -> np.ndarray:
    x = _vector(values)
    if (
        isinstance(width, (bool, np.bool_))
        or not isinstance(width, (int, np.integer))
        or not 1 <= width <= x.size
    ):
        raise ValueError("Window width must be an integer from one through signal length")
    return sliding_window_view(x, int(width))
```

Adjacent rows refer to overlapping regions of the original storage. The view avoids allocating a full window matrix, but applying a width-k reduction still performs work across those logical elements. Preserving the source dtype avoids secretly replacing the array with a floating copy and then claiming shared ownership. Default read-only access reduces accidental conflicting writes; it cannot freeze the source.

## Exercise 2: Keep weight orientation explicit

**Contract: `weighted_valid`.** Return the floating left-to-right weighted sum of every complete window, with no normalization or padding. Accept nonempty finite real signal and weight vectors with weight length no larger than the signal. Convert operands to float64 before multiplication; reject invalid inputs or nonfinite results with ValueError. Return independent output and preserve inputs.

**Expected:** Signal [1, 2, 4] with weights [1, 3] returns [7, 14]. Using np.convolve with that same unreversed vector instead gives [5, 10] in valid mode.

```python
def weighted_valid(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    x, w = _vector(values).astype(np.float64), _vector(weights).astype(np.float64)
    windows = window_view(x, w.size)
    with np.errstate(over="ignore", invalid="ignore"):
        return _finite_result(windows @ w)
```

A row [x_i, x_(i+1)] dotted with [1, 3] is x_i + 3*x_(i+1). Discrete convolution reverses the kernel in a window interpretation, so it is a different operation for asymmetric weights. Symmetric averages conceal that mistake. Float conversion precedes multiplication to prevent integer wrap, but it does not provide exact arithmetic for large integer identifiers.

## Exercise 3: Make the boundary model a parameter

**Contract: `convolve_same`.** Convolve a nonempty finite real signal with a nonempty odd-length finite real kernel. Return the signal length by padding half the kernel width on both sides, then applying the reversed kernel. boundary must be zero or reflect; reflect excludes the endpoint and requires at least two signal samples. Reject invalid inputs or nonfinite results with ValueError. Do not normalize the kernel.

**Expected:** [1, 2, 4] with [1, 2, 0] gives [4, 8, 8] under zero padding and [4, 8, 10] under reflection. Even kernel length is rejected to avoid an unstated centering choice.

```python
def convolve_same(values: np.ndarray, kernel: np.ndarray, boundary: str) -> np.ndarray:
    x, h = _vector(values).astype(np.float64), _vector(kernel).astype(np.float64)
    if h.size % 2 != 1 or boundary not in {"zero", "reflect"}:
        raise ValueError("Expected an odd kernel and a zero or reflect boundary")
    if boundary == "reflect" and x.size < 2:
        raise ValueError("Reflect mode needs at least two samples")
    pad = h.size // 2
    padded = np.pad(x, (pad, pad), mode="constant" if boundary == "zero" else "reflect")
    with np.errstate(over="ignore", invalid="ignore"):
        return _finite_result(sliding_window_view(padded, h.size) @ h[::-1])
```

The interior computation cannot decide which values exist outside the observation interval. Zero padding imposes zero extension; reflection uses nearby interior samples and excludes repeated endpoints under NumPy reflect semantics. Reversal handles convolution orientation separately from padding. Restricting kernels to odd length supplies an unambiguous center, while still permitting kernels wider than the signal.

## Exercise 4: Preserve real-transform length and normalization

**Contract: `fft_roundtrip`.** Return irfft(rfft(values, norm="backward"), n=len(values), norm="backward") for a nonempty finite real vector, converted to float64. Reject invalid inputs or nonfinite results with ValueError. Preserve input and original length for both odd and even signals. Verify with numerical tolerance, not exact equality.

**Expected:** Signals of length 5 and 6 each return their own shape and original values within tolerance. Omitting n for a length-5 input would ordinarily reconstruct length 4.

```python
def fft_roundtrip(values: np.ndarray) -> np.ndarray:
    x = _vector(values).astype(np.float64)
    with np.errstate(over="ignore", invalid="ignore"):
        transformed = np.fft.rfft(x, norm="backward")
        result = np.fft.irfft(transformed, n=x.size, norm="backward")
    return _finite_result(result)
```

The default backward convention leaves the forward transform unscaled and divides the inverse by the transform length. Real-input transforms store only the nonredundant half-spectrum, whose size alone does not distinguish every odd/even original length. Passing n is therefore part of the data contract. Approximate roundtrip identity checks implementation consistency, not the suitability of a spectral model.

## Exercise 5: Scale DC, interior and Nyquist bins correctly

**Contract: `one_sided_amplitude`.** Return (frequency, amplitude) for at least two uniformly sampled finite real observations and finite positive sample_spacing excluding bool. Use rfftfreq and abs(rfft(values))/n; double positive-frequency interior bins only, leaving DC and the even-length Nyquist bin undoubled. For odd length, double every non-DC bin. Reject invalid inputs or nonfinite outputs with ValueError. Do not detrend or window.

**Expected:** Eight samples of 2 + 3*cos(2*pi*j/8) + 4*(-1)**j with spacing 1/8 give bins [0, 1, 2, 3, 4] and amplitudes [2, 3, 0, 0, 4] within tolerance. Frequency uses inverse units of spacing.

```python
def one_sided_amplitude(values: np.ndarray, sample_spacing: float) -> tuple[np.ndarray, np.ndarray]:
    x = _vector(values).astype(np.float64)
    if (
        isinstance(sample_spacing, (bool, np.bool_))
        or not isinstance(sample_spacing, (int, float, np.integer, np.floating))
        or not np.isfinite(sample_spacing)
        or sample_spacing <= 0
        or x.size < 2
    ):
        raise ValueError("Expected at least two samples and finite positive sample spacing")
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        frequency = np.fft.rfftfreq(x.size, d=sample_spacing)
        amplitude = np.abs(np.fft.rfft(x, norm="backward")) / x.size
    stop = -1 if x.size % 2 == 0 else None
    amplitude[1:stop] *= 2
    return _finite_result(frequency), _finite_result(amplitude)
```

Real signals have conjugate frequency pairs. Interior positive bins represent a pair, so doubling their magnitude recovers an isolated bin-centered sinusoid amplitude. DC and an even-length Nyquist bin have no distinct partner. Off-bin tones leak energy; this amplitude convention is neither a general unbiased estimator nor a power spectral density. Uniform sampling and anti-aliasing remain acquisition assumptions.

## Exercise 6: Separate linear from circular convolution

**Contract: `fft_convolve_full`.** Return full linear convolution of two nonempty finite real vectors using rfft products and irfft with transform length len(values) + len(kernel) - 1. Convert to float64 before arithmetic, preserve inputs and reject invalid or nonfinite results with ValueError. Return exactly that full output length; no circular wraparound or unexplained extra scale factor.

**Expected:** [1, 2] convolved with [3, 4] yields [3, 10, 8] within tolerance. A transform length of 2 would alias the last value into the first output position.

```python
def fft_convolve_full(values: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    x, h = _vector(values).astype(np.float64), _vector(kernel).astype(np.float64)
    length = x.size + h.size - 1
    with np.errstate(over="ignore", invalid="ignore"):
        transformed = np.fft.rfft(x, n=length) * np.fft.rfft(h, n=length)
        result = np.fft.irfft(transformed, n=length)
    return _finite_result(result)
```

Multiplication of finite-length DFTs naturally corresponds to circular convolution. Padding to at least the full linear support prevents overlapping tails from wrapping into the beginning. The default inverse already applies the reciprocal length, so dividing again would under-scale the result. FFT methods are not always faster for tiny kernels; this exercise proves the boundary identity rather than making a performance claim.

## Verification and interpretation

The executable reference covers normal and invalid examples for these contracts. Independent tests in `tests/test_python_numpy_modernization.py` use analytical answers, invariants and changed-condition cases rather than treating the reference output as its own oracle. A reference run is evidence that the implementation meets the tested inputs; explain the relevant assumption and construct an additional counterexample before claiming independent understanding.
