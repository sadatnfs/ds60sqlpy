"""python-numpy-08: Sliding Windows, Convolution, and FFT Boundaries.

Run the two worked examples, then implement the six independent contracts.
Complete answers are kept in solutions/.
"""

import numpy as np


def window_view(values: np.ndarray, width: int) -> np.ndarray:
    """
    Return the default read-only sliding_window_view of a nonempty finite real one-
    dimensional array with the given width. Preserve dtype and shared storage. Require
    integer width from 1 through length, excluding bool; reject invalid inputs with
    ValueError. Source mutations remain visible. Read-only does not mean an immutable
    snapshot.
    """
    raise NotImplementedError("Implement window_view")


def weighted_valid(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """
    Return the floating left-to-right weighted sum of every complete window, with no
    normalization or padding. Accept nonempty finite real signal and weight vectors with
    weight length no larger than the signal. Convert operands to float64 before
    multiplication; reject invalid inputs or nonfinite results with ValueError. Return
    independent output and preserve inputs.
    """
    raise NotImplementedError("Implement weighted_valid")


def convolve_same(values: np.ndarray, kernel: np.ndarray, boundary: str) -> np.ndarray:
    """
    Convolve a nonempty finite real signal with a nonempty odd-length finite real kernel.
    Return the signal length by padding half the kernel width on both sides, then applying
    the reversed kernel. boundary must be zero or reflect; reflect excludes the endpoint and
    requires at least two signal samples. Reject invalid inputs or nonfinite results with
    ValueError. Do not normalize the kernel.
    """
    raise NotImplementedError("Implement convolve_same")


def fft_roundtrip(values: np.ndarray) -> np.ndarray:
    """
    Return irfft(rfft(values, norm="backward"), n=len(values), norm="backward") for a
    nonempty finite real vector, converted to float64. Reject invalid inputs or nonfinite
    results with ValueError. Preserve input and original length for both odd and even
    signals. Verify with numerical tolerance, not exact equality.
    """
    raise NotImplementedError("Implement fft_roundtrip")


def one_sided_amplitude(values: np.ndarray, sample_spacing: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Return (frequency, amplitude) for at least two uniformly sampled finite real
    observations and finite positive sample_spacing excluding bool. Use rfftfreq and
    abs(rfft(values))/n; double positive-frequency interior bins only, leaving DC and the
    even-length Nyquist bin undoubled. For odd length, double every non-DC bin. Reject
    invalid inputs or nonfinite outputs with ValueError. Do not detrend or window.
    """
    raise NotImplementedError("Implement one_sided_amplitude")


def fft_convolve_full(values: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Return full linear convolution of two nonempty finite real vectors using rfft products
    and irfft with transform length len(values) + len(kernel) - 1. Convert to float64 before
    arithmetic, preserve inputs and reject invalid or nonfinite results with ValueError.
    Return exactly that full output length; no circular wraparound or unexplained extra
    scale factor.
    """
    raise NotImplementedError("Implement fft_convolve_full")


def worked_examples() -> None:
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


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Implement and check all six exercise contracts.")

# Exercise 1: Inspect overlapping storage
# Contract: window_view
# Prompt: Return the default read-only sliding_window_view of a nonempty finite real one-
# dimensional array with the given width. Preserve dtype and shared storage. Require integer width
# from 1 through length, excluding bool; reject invalid inputs with ValueError. Source mutations
# remain visible. Read-only does not mean an immutable snapshot.
# Expected: arange(6) with width 3 gives shape (4, 3); source index 2 appears in three overlapping
# locations. Assignment through the view fails, but changing the source changes those locations.

# Exercise 2: Keep weight orientation explicit
# Contract: weighted_valid
# Prompt: Return the floating left-to-right weighted sum of every complete window, with no
# normalization or padding. Accept nonempty finite real signal and weight vectors with weight
# length no larger than the signal. Convert operands to float64 before multiplication; reject
# invalid inputs or nonfinite results with ValueError. Return independent output and preserve
# inputs.
# Expected: Signal [1, 2, 4] with weights [1, 3] returns [7, 14]. Using np.convolve with that same
# unreversed vector instead gives [5, 10] in valid mode.

# Exercise 3: Make the boundary model a parameter
# Contract: convolve_same
# Prompt: Convolve a nonempty finite real signal with a nonempty odd-length finite real kernel.
# Return the signal length by padding half the kernel width on both sides, then applying the
# reversed kernel. boundary must be zero or reflect; reflect excludes the endpoint and requires at
# least two signal samples. Reject invalid inputs or nonfinite results with ValueError. Do not
# normalize the kernel.
# Expected: [1, 2, 4] with [1, 2, 0] gives [4, 8, 8] under zero padding and [4, 8, 10] under
# reflection. Even kernel length is rejected to avoid an unstated centering choice.

# Exercise 4: Preserve real-transform length and normalization
# Contract: fft_roundtrip
# Prompt: Return irfft(rfft(values, norm="backward"), n=len(values), norm="backward") for a
# nonempty finite real vector, converted to float64. Reject invalid inputs or nonfinite results
# with ValueError. Preserve input and original length for both odd and even signals. Verify with
# numerical tolerance, not exact equality.
# Expected: Signals of length 5 and 6 each return their own shape and original values within
# tolerance. Omitting n for a length-5 input would ordinarily reconstruct length 4.

# Exercise 5: Scale DC, interior and Nyquist bins correctly
# Contract: one_sided_amplitude
# Prompt: Return (frequency, amplitude) for at least two uniformly sampled finite real
# observations and finite positive sample_spacing excluding bool. Use rfftfreq and
# abs(rfft(values))/n; double positive-frequency interior bins only, leaving DC and the even-
# length Nyquist bin undoubled. For odd length, double every non-DC bin. Reject invalid inputs or
# nonfinite outputs with ValueError. Do not detrend or window.
# Expected: Eight samples of 2 + 3*cos(2*pi*j/8) + 4*(-1)**j with spacing 1/8 give bins [0, 1, 2,
# 3, 4] and amplitudes [2, 3, 0, 0, 4] within tolerance. Frequency uses inverse units of spacing.

# Exercise 6: Separate linear from circular convolution
# Contract: fft_convolve_full
# Prompt: Return full linear convolution of two nonempty finite real vectors using rfft products
# and irfft with transform length len(values) + len(kernel) - 1. Convert to float64 before
# arithmetic, preserve inputs and reject invalid or nonfinite results with ValueError. Return
# exactly that full output length; no circular wraparound or unexplained extra scale factor.
# Expected: [1, 2] convolved with [3, 4] yields [3, 10, 8] within tolerance. A transform length of
# 2 would alias the last value into the first output position.
