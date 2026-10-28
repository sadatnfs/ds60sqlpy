"""Complete offline references for python-numpy-05; requires NumPy 2.x."""

from collections.abc import Callable

import numpy as np


def _real_array(values: np.ndarray) -> np.ndarray:
    x = np.asarray(values)
    if x.dtype.kind not in "iuf":
        raise ValueError("Expected a real integer or floating dtype, excluding bool")
    return x


def _integers(values: np.ndarray) -> np.ndarray:
    x = _real_array(values)
    if x.ndim != 1 or x.dtype.kind not in "iu":
        raise ValueError("Expected a one-dimensional integer array")
    return x


def _integer_dtype(dtype: str) -> np.dtype:
    try:
        destination = np.dtype(dtype)
    except (TypeError, ValueError) as error:
        raise ValueError("Invalid destination dtype") from error
    if destination.kind not in "iu":
        raise ValueError("Destination must be a signed or unsigned integer dtype")
    return destination


def numeric_schema(values: np.ndarray) -> dict[str, object]:
    x = _real_array(values)
    bounds = None
    if x.dtype.kind in "iu":
        info = np.iinfo(x.dtype)
        bounds = (int(info.min), int(info.max))
    return {"dtype": x.dtype.name, "shape": x.shape, "itemsize": x.itemsize, "bounds": bounds}


def promote_pair(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a, b = _real_array(left), _real_array(right)
    if a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Expected equal shapes with finite values")
    destination = np.result_type(a.dtype, b.dtype)
    return a.astype(destination, copy=True), b.astype(destination, copy=True)


def checked_integer_cast(values: np.ndarray, dtype: str) -> np.ndarray:
    x = _integers(values)
    destination = _integer_dtype(dtype)
    bounds = np.iinfo(destination)
    exact = [int(value) for value in x]
    if any(value < int(bounds.min) or value > int(bounds.max) for value in exact):
        raise ValueError("An input is outside the destination integer range")
    return np.array(exact, dtype=destination)


def checked_integer_add(left: np.ndarray, right: np.ndarray, dtype: str) -> np.ndarray:
    a, b = _integers(left), _integers(right)
    destination = _integer_dtype(dtype)
    if a.shape != b.shape:
        raise ValueError("Expected equal one-dimensional shapes")
    bounds = np.iinfo(destination)
    exact = [int(x) + int(y) for x, y in zip(a, b, strict=True)]
    if any(value < int(bounds.min) or value > int(bounds.max) for value in exact):
        raise ValueError("A mathematical sum is outside the destination range")
    return np.array(exact, dtype=destination)


def exact_integer_sum(values: np.ndarray) -> int:
    return sum(int(value) for value in _integers(values))


def float64_exact_mask(values: np.ndarray) -> np.ndarray:
    x = _integers(values)
    # Python integers avoid an overflowing float-to-int64 round trip at 2**63.
    return np.array([int(float(int(value))) == int(value) for value in x], dtype=bool)


def expect_value_error(call: Callable[[], object]) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main() -> None:
    schema = numeric_schema(np.array([1], dtype=np.uint8))
    assert schema == {"dtype": "uint8", "shape": (1,), "itemsize": 1, "bounds": (0, 255)}
    assert numeric_schema(np.array([np.nan]))["bounds"] is None
    expect_value_error(lambda: numeric_schema(np.array([True])))
    a = np.array([2**53 + 1], dtype=np.int64)
    b = np.array([0], dtype=np.uint64)
    left, right = promote_pair(a, b)
    assert left.dtype == right.dtype == np.dtype("float64")
    assert not np.shares_memory(left, a) and int(left[0]) != int(a[0])
    expect_value_error(lambda: promote_pair(a, np.array([[1]])))
    assert checked_integer_cast(np.array([0, 255]), "uint8").tolist() == [0, 255]
    expect_value_error(lambda: checked_integer_cast(np.array([-1]), "uint8"))
    expect_value_error(lambda: checked_integer_cast(np.array([1.0]), "int8"))
    assert checked_integer_add(np.array([120]), np.array([7]), "int8").tolist() == [127]
    expect_value_error(lambda: checked_integer_add(np.array([127]), np.array([1]), "int8"))
    assert checked_integer_add(np.array([300]), np.array([-300]), "uint8").tolist() == [0]
    assert exact_integer_sum(np.array([2**63 - 1, 1], dtype=np.int64)) == 2**63
    assert exact_integer_sum(np.array([], dtype=np.uint64)) == 0
    values = np.array([2**53, 2**53 + 1, 2**53 + 2, 2**63 - 1], dtype=np.int64)
    assert float64_exact_mask(values).tolist() == [True, False, True, False]
    assert float64_exact_mask(np.array([2**64 - 1], dtype=np.uint64)).tolist() == [False]
    print("python-numpy-05: six dtype, range, and exactness contracts passed")


if __name__ == "__main__":
    main()
