"""Complete offline references for python-numpy-08; explicit transform conventions."""

from collections.abc import Callable

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def _vector(values: np.ndarray) -> np.ndarray:
    x = np.asarray(values)
    if x.ndim != 1 or x.size == 0 or x.dtype.kind not in "iuf" or not np.isfinite(x).all():
        raise ValueError("Expected a nonempty finite real numeric vector, excluding bool")
    return x


def _finite_result(values: np.ndarray) -> np.ndarray:
    if not np.isfinite(values).all():
        raise ValueError("Result exceeds finite floating range")
    return values


def window_view(values: np.ndarray, width: int) -> np.ndarray:
    x = _vector(values)
    if (
        isinstance(width, (bool, np.bool_))
        or not isinstance(width, (int, np.integer))
        or not 1 <= width <= x.size
    ):
        raise ValueError("Window width must be an integer from one through signal length")
    return sliding_window_view(x, int(width))


def weighted_valid(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    x, w = _vector(values).astype(np.float64), _vector(weights).astype(np.float64)
    windows = window_view(x, w.size)
    with np.errstate(over="ignore", invalid="ignore"):
        return _finite_result(windows @ w)


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


def fft_roundtrip(values: np.ndarray) -> np.ndarray:
    x = _vector(values).astype(np.float64)
    with np.errstate(over="ignore", invalid="ignore"):
        transformed = np.fft.rfft(x, norm="backward")
        result = np.fft.irfft(transformed, n=x.size, norm="backward")
    return _finite_result(result)


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


def fft_convolve_full(values: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    x, h = _vector(values).astype(np.float64), _vector(kernel).astype(np.float64)
    length = x.size + h.size - 1
    with np.errstate(over="ignore", invalid="ignore"):
        transformed = np.fft.rfft(x, n=length) * np.fft.rfft(h, n=length)
        result = np.fft.irfft(transformed, n=length)
    return _finite_result(result)


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    source = np.arange(6, dtype=float)
    windows = window_view(source, 3)
    assert windows.shape == (4, 3) and np.shares_memory(source, windows)
    assert not windows.flags.writeable
    source[2] = 17
    assert windows[0, 2] == windows[1, 1] == windows[2, 0] == 17
    expect_value_error(lambda: window_view(source, 0))
    np.testing.assert_allclose(weighted_valid(np.array([1, 2, 4]), np.array([1, 3])), [7, 14])
    x, h = np.array([1.0, 2.0, 4.0]), np.array([1.0, 2.0, 0.0])
    np.testing.assert_allclose(convolve_same(x, h, "zero"), [4, 8, 8])
    np.testing.assert_allclose(convolve_same(x, h, "reflect"), [4, 8, 10])
    expect_value_error(lambda: convolve_same(x, np.ones(2), "zero"))
    for length in (5, 6):
        original = np.arange(length, dtype=float)
        np.testing.assert_allclose(fft_roundtrip(original), original, atol=1e-12)
    signal = 2 + 3 * np.cos(2 * np.pi * np.arange(8) / 8) + 4 * (-1.0) ** np.arange(8)
    frequency, amplitude = one_sided_amplitude(signal, 0.125)
    np.testing.assert_allclose(frequency, [0, 1, 2, 3, 4], atol=1e-12)
    np.testing.assert_allclose(amplitude, [2, 3, 0, 0, 4], atol=1e-12)
    expect_value_error(lambda: one_sided_amplitude(signal, 0))
    np.testing.assert_allclose(
        fft_convolve_full(np.array([1, 2]), np.array([3, 4])), [3, 10, 8], atol=1e-12
    )
    expect_value_error(lambda: fft_convolve_full(np.array([]), h))
    print("python-numpy-08: six window, convolution, and spectrum contracts passed")


if __name__ == "__main__":
    main()
