# Sliding Windows, Convolution, and FFT Boundaries

## Level and prerequisites

- **Stable ID:** `python-numpy-08`.
- **Level:** Advanced. Allow about 100 minutes for explanations, prediction and practice; the estimate is not a deadline.
- **Direct prerequisite:** `python-numpy-01`, [companion guide](py_numpy_01.md).
- **Direct prerequisite:** `python-21`, [companion guide](../../ds-60day/companion-guides/day21_time_series_pandas.md).
- **Direct prerequisite:** `python-33`, [companion guide](../../ds-60day/companion-guides/day33_linear_algebra_matrices.md).
- **Artifacts:** [learner script](../lessons/py_numpy_08.py) · [explained reference](../solutions/py_numpy_08_solutions.md) · [executable reference](../solutions/py_numpy_08_solution.py).

## How to run this lesson

Run `./classroom` from the repository root, choose **Python** in the shared
`/classroom` directory, and open `python-numpy-08`. Read the capability notice and
use the saved coding pad with the prepared Python Core environment. Docker
supplies Python and NumPy 2.x; no host package install or notebook kernel is
needed. Windows learners use the same entrypoint in WSL 2. Paste the complete
[learner script](../lessons/py_numpy_08.py), save it, and Run its worked
examples before attempting the six task functions. Those functions remain for
you to implement; a passing demonstration does not complete their contracts.

Each browser Run starts a fresh process. Include imports, fixtures and function
calls in the saved source, and save predictions and evidence in your notes.
Temporary arrays and generator objects do not survive the process, whereas the
browser's saved work lives in its Docker learning volume. Use only the tiny
original offline fixtures here; no download, service or database is required.
The [classroom guide](../../../docs/classroom-experience.md) explains that lifecycle.

A separately prepared contributor environment may run
`uv run --no-sync python python/professional/lessons/py_numpy_08.py`
from its checkout. Follow [contributor setup](../../../CONTRIBUTING.md) first;
that environment has separate files and does not import the browser's saved
learning volume. Keep the separate answers closed until you choose to compare
a genuine attempt.

## Learning objectives

This lesson is `python-numpy-08`. Complete `python-numpy-01`, `python-21` and `python-33` first. Bring knowledge of array ownership, vector operations and the idea that sampled signals have a frequency interpretation. Use the Docker classroom's prepared Python Core environment. The examples are complete, offline scripts with tiny arrays, printed numerical evidence and no plotting dependency.

You will distinguish four choices that are often mixed together: which samples form a window, which direction its weights face, what is assumed outside the observed interval, and how a Fourier transform is normalized. Your final evidence should expose mistakes that a symmetric moving average or an even-length roundtrip could hide.

By the end of this lesson, you can:

- Trace overlapping read-only window storage and distinguish a view from an independent result.
- Predict how kernel reversal and zero versus reflected padding change local outputs.
- Preserve odd and even signal lengths and the declared forward/inverse FFT normalization.
- Scale one-sided amplitudes correctly and choose transform support that separates full linear convolution from circular wraparound.

## Vocabulary and concepts: view, correlation, convolution and boundary

**Sliding window:** Groups successive samples into overlapping rows. For a length-\(n\) vector and width \(k\), the valid window matrix has shape \((n-k+1,k)\). A view can describe this matrix without copying every repeated sample. Its logical element count is larger than the original buffer, and several entries can refer to the same storage location.

A left-to-right weighted window computes

\[
z_i=\sum_{j=0}^{k-1}w_jx_{i+j}.
\]

For real inputs, this is a correlation-style operation.

**Convolution:** In a window representation, uses the reversed kernel. Symmetric weights produce the same result after reversal, so they are a poor diagnostic fixture. An asymmetric derivative-like kernel reveals the difference immediately.

**Boundary condition:** Specifies unobserved values outside the signal. Zero extension assumes zeros; reflection borrows nearby interior values; periodic extension wraps to the other end. These are modeling decisions, not cosmetic choices. **Valid** output uses only complete observed windows. **Same** output preserves the signal length under an explicit centering policy. **Full** convolution includes the entire finite support, including partial overlap at both ends.

## Syntax anatomy and memory ownership

Import `sliding_window_view` from `numpy.lib.stride_tricks`, then use `sliding_window_view(x, width)`. The default result is read-only. `np.shares_memory(x, windows)` checks the storage relationship; it does not mean `windows.base is x` must hold through every internal view wrapper.

Read-only access prevents assignment through that view, but the original array can still change. This distinction matters when a window matrix is passed to another function while the source remains mutable. Copy it if an independent snapshot is required. Do not force overlapping windows writable merely to silence an assignment error, because one write can affect several visible positions.

The view saves storage allocation, but a naive reduction across all windows still examines roughly \(nk\) logical elements. Specialized convolution or cumulative-sum methods may reduce work for particular operations. This unit teaches correctness and semantics before performance selection; it does not claim that every stride trick is a faster algorithm.

## Worked example: asymmetric weights expose reversal

Predict the signs of both result arrays. This complete program compares the same two numbers interpreted as left-to-right weights and as a convolution kernel.

```python
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

source = np.array([2.0, 5.0, 9.0, 14.0])
windows = sliding_window_view(source, 2)
weights = np.array([1.0, -1.0])
left_to_right = windows @ weights
convolution = np.convolve(source, weights, mode="valid")
assert np.allclose(left_to_right, [-3, -4, -5])
assert np.allclose(convolution, [3, 4, 5])
assert np.shares_memory(source, windows) and not windows.flags.writeable
print("weighted windows:", left_to_right.tolist(), "convolution:", convolution.tolist())
```

The left-to-right difference subtracts the later sample, producing negative differences for this increasing signal. Convolution reverses the weights in the local window, producing the opposite sign. With weights `[0.5, 0.5]`, both operations would agree, concealing an orientation bug.

Change `source[1]` after constructing the windows and inspect both windows that include that sample. The view updates in both positions. Previously calculated dot-product outputs do not update, because they are new result arrays. Keeping this ownership distinction explicit prevents a misleading expectation that every downstream calculation remains linked to the source.

## Boundary models change edge values

For an odd kernel of width \(k\), use \((k-1)/2\) padding values on each side to define a centered same-length result. This lesson rejects even kernels because choosing left or right alignment would otherwise remain unstated. The `reflect` mode excludes the endpoint itself, unlike a symmetric mode that repeats it.

For `[1, 2, 4]`, one reflected sample on each side produces `[2, 1, 2, 4, 2]`, whereas zero extension gives `[0, 1, 2, 4, 0]`. Compute a boundary result by hand before calling any convenience function. The center result can be correct under both modes while the edge result answers a different physical question.

Reflection can be reasonable for a locally smooth image edge, while zero padding may represent a finite impulse surrounded by silence. Neither is universally correct. For a streaming sensor, reflecting future observations at the right edge would also violate causality if those observations were not actually available. A numerical padding choice is not permission to invent unavailable data.

## Worked example: an FFT product has a circular boundary

Predict where the final value goes when the transform is too short. This complete program compares full linear support with a length-three circular calculation.

```python
import numpy as np

signal = np.array([1.0, 3.0, 2.0])
kernel = np.array([1.0, 2.0])
length = signal.size + kernel.size - 1
linear = np.fft.irfft(np.fft.rfft(signal, n=length) * np.fft.rfft(kernel, n=length), n=length)
circular = np.fft.irfft(np.fft.rfft(signal, n=3) * np.fft.rfft(kernel, n=3), n=3)
assert np.allclose(linear, [1, 5, 8, 4])
assert np.allclose(circular, [5, 5, 8])
assert np.allclose(np.fft.irfft(np.fft.rfft(signal), n=3), signal)
print("linear:", linear.tolist(), "circular:", circular.tolist())
```

The full result has length four. The shorter transform folds its final contribution of 4 into the first position, changing 1 to 5. Zero-padding to at least \(n+m-1\) prevents that overlap for vectors of lengths \(n\) and \(m\). Padding beyond that length is also possible, but the requested full output still needs to be cropped deliberately.

The inverse transform already applies its normalization under the default backward convention. Dividing `linear` again by the transform length would introduce an extra scale error. Change one operand to an impulse and verify that the other is reproduced in the expected position; this is a useful independent test of orientation, support and amplitude.

## Real transforms, length and normalization

For length \(N\), the forward discrete Fourier transform uses

\[
X_k=\sum_{j=0}^{N-1}x_j e^{-2\pi i jk/N}.
\]

With `norm="backward"`, the inverse includes the factor \(1/N\), so forward followed by inverse reconstructs the input within numerical tolerance. Real input has conjugate-symmetric frequency coefficients. `rfft` stores only \(\lfloor N/2\rfloor+1\) bins, and `irfft` reconstructs real observations.

The stored bin count does not uniquely encode whether every original length was odd or even. Always preserve the original `N` and pass it to `irfft`. An odd-length signal can otherwise return a different output shape. This is a metadata failure as much as a numerical one: a spectrum without its sampling interval and original length is incomplete evidence.

## Amplitude scaling and the acquisition assumptions

`rfftfreq(N, d=sample_spacing)` returns frequencies in inverse units of the spacing. If spacing is seconds, frequencies are cycles per second. For a bin-centered real sinusoid away from DC and the even-length Nyquist frequency, its one-sided amplitude is twice the FFT magnitude divided by \(N\). DC represents the mean and has no separate negative-frequency partner. The even-length Nyquist bin also has no separate partner, so neither is doubled.

For odd lengths, the final stored bin is still an interior positive frequency and must be doubled. This is why testing only even lengths is insufficient. The contract reports magnitude, losing phase and the sign of a DC value. It is not a power spectral density and does not automatically provide physical energy units.

Uniform sampling is required for these frequency labels. Frequencies above half the sampling rate can alias into lower bins; post-processing cannot generally recover what the acquisition failed to distinguish. A real system needs an appropriate sampling rate and anti-alias filtering before downsampling. A frequency between FFT bins also leaks across bins because a finite rectangular observation window need not join smoothly under periodic extension. The lesson does not detrend or apply a taper, so do not interpret its largest bin as an unbiased amplitude estimate for arbitrary signals.

## Six exercises

Implement these functions in `python/professional/lessons/py_numpy_08.py`. Keep an asymmetric kernel, an odd-length signal and a direct small convolution among your checks. Numerical equality requires tolerances; output length and source ownership require exact assertions.

1. **Inspect overlapping storage: `window_view`.** Return the default read-only sliding_window_view of a nonempty finite real one-dimensional array with the given width. Preserve dtype and shared storage. Require integer width from 1 through length, excluding bool; reject invalid inputs with ValueError. Source mutations remain visible. Read-only does not mean an immutable snapshot.

   **Expected:** arange(6) with width 3 gives shape (4, 3); source index 2 appears in three overlapping locations. Assignment through the view fails, but changing the source changes those locations.

2. **Keep weight orientation explicit: `weighted_valid`.** Return the floating left-to-right weighted sum of every complete window, with no normalization or padding. Accept nonempty finite real signal and weight vectors with weight length no larger than the signal. Convert operands to float64 before multiplication; reject invalid inputs or nonfinite results with ValueError. Return independent output and preserve inputs.

   **Expected:** Signal [1, 2, 4] with weights [1, 3] returns [7, 14]. Using np.convolve with that same unreversed vector instead gives [5, 10] in valid mode.

3. **Make the boundary model a parameter: `convolve_same`.** Convolve a nonempty finite real signal with a nonempty odd-length finite real kernel. Return the signal length by padding half the kernel width on both sides, then applying the reversed kernel. boundary must be zero or reflect; reflect excludes the endpoint and requires at least two signal samples. Reject invalid inputs or nonfinite results with ValueError. Do not normalize the kernel.

   **Expected:** [1, 2, 4] with [1, 2, 0] gives [4, 8, 8] under zero padding and [4, 8, 10] under reflection. Even kernel length is rejected to avoid an unstated centering choice.

4. **Preserve real-transform length and normalization: `fft_roundtrip`.** Return irfft(rfft(values, norm="backward"), n=len(values), norm="backward") for a nonempty finite real vector, converted to float64. Reject invalid inputs or nonfinite results with ValueError. Preserve input and original length for both odd and even signals. Verify with numerical tolerance, not exact equality.

   **Expected:** Signals of length 5 and 6 each return their own shape and original values within tolerance. Omitting n for a length-5 input would ordinarily reconstruct length 4.

5. **Scale DC, interior and Nyquist bins correctly: `one_sided_amplitude`.** Return (frequency, amplitude) for at least two uniformly sampled finite real observations and finite positive sample_spacing excluding bool. Use rfftfreq and abs(rfft(values))/n; double positive-frequency interior bins only, leaving DC and the even-length Nyquist bin undoubled. For odd length, double every non-DC bin. Reject invalid inputs or nonfinite outputs with ValueError. Do not detrend or window.

   **Expected:** Eight samples of 2 + 3*cos(2*pi*j/8) + 4*(-1)**j with spacing 1/8 give bins [0, 1, 2, 3, 4] and amplitudes [2, 3, 0, 0, 4] within tolerance. Frequency uses inverse units of spacing.

6. **Separate linear from circular convolution: `fft_convolve_full`.** Return full linear convolution of two nonempty finite real vectors using rfft products and irfft with transform length len(values) + len(kernel) - 1. Convert to float64 before arithmetic, preserve inputs and reject invalid or nonfinite results with ValueError. Return exactly that full output length; no circular wraparound or unexplained extra scale factor.

   **Expected:** [1, 2] convolved with [3, 4] yields [3, 10, 8] within tolerance. A transform length of 2 would alias the last value into the first output position.

## Common pitfalls and diagnosis

If a derivative changes sign, inspect kernel orientation. If only the edges differ, inspect padding and alignment. If an FFT result wraps into the beginning, inspect transform length. If every value has an extra scale factor, inspect the normalization pair before changing the data. If a real inverse produces one fewer sample, restore the original odd length explicitly.

These mechanisms appear in time-series smoothing, finite impulse-response filters, image neighborhoods and spectral monitoring. Explain which assumptions are appropriate before selecting an API. Reproduce one boundary calculation by hand, explain why a read-only view can change, and identify a signal that would violate the amplitude interpretation. A correct transform implementation and a scientifically meaningful signal analysis are separate achievements.

## Self-check

Close the examples and answer in your own words before running a confirming case:

- Predict both outputs for an asymmetric two-weight kernel, then explain why symmetric moving averages hide an orientation mistake.
- Explain how a read-only window can change when its source changes, while an already calculated dot product remains fixed.
- State why inverse real FFT needs the original odd length and which one-sided bins must remain undoubled.
- For vectors of lengths three and two, justify a transform length of at least four and describe where a shorter circular calculation sends the last contribution.

## Next step

Use [dtype contracts](py_numpy_05.md) before applying these operations to fixed-width integer signals, and [random-stream contracts](py_numpy_06.md) when constructing reproducible noisy fixtures. Revisit the learner and separate references below only after you have explained orientation, boundary, normalization and storage evidence.

## Official API references

Use [sliding-window view documentation](https://numpy.org/doc/2.4/reference/generated/numpy.lib.stride_tricks.sliding_window_view.html), [real inverse FFT documentation](https://numpy.org/doc/2.4/reference/generated/numpy.fft.irfft.html), and [NumPy's Fourier-transform conventions](https://numpy.org/doc/2.4/reference/routines.fft.html) to check API details.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-numpy-08: Sliding Windows, Convolution, and FFT Boundaries.
Read python/professional/companion-guides/py_numpy_08.md and python/professional/lessons/py_numpy_08.py. Direct prerequisites: python-numpy-01, python-21, python-33. Stay within that boundary and explain new vocabulary at a beginner-friendly pace.
Focus on sliding_window_view, weight orientation, padding boundaries, real FFT normalization, one-sided amplitude, linear versus circular convolution. Explain one mechanism, ask me to predict a concrete result, let me attempt it, provide one hint at a time, then review my numerical, shape, ownership or exception evidence. Ask retrieval questions that I answer in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use the Docker classroom's prepared Python Core environment with tiny offline fixtures. Preserve my saved work. This lesson requires no live SQL, database changes, downloads or external services; do not execute any live SQL as part of it.
Done when all six named contracts have inspected normal and boundary evidence and I can explain a changed-condition failure without copying the reference.
```
