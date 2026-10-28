"""python-numpy-05: NumPy Dtypes, Promotion, and Overflow Contracts.

Run the two worked examples, then implement the six independent contracts.
Complete answers are kept in solutions/.
"""

import numpy as np


def numeric_schema(values: np.ndarray) -> dict:
    """
    Return a dictionary with dtype (dtype.name), shape (tuple), itemsize (int), and bounds
    (inclusive Python integer min/max tuple for integer dtypes, otherwise None). Accept
    arrays of any shape with signed integer, unsigned integer, or real floating dtype.
    Inspection permits nonfinite floats. Reject bool, complex, object and string dtypes with
    ValueError; do not mutate the input.
    """
    raise NotImplementedError("Implement numeric_schema")


def promote_pair(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    For equal-shaped finite real integer or floating arrays, return two independent copies
    converted to np.result_type(left.dtype, right.dtype). Reject unequal shapes,
    bool/complex/object/string dtypes and nonfinite values with ValueError. Preserve
    sources. This follows dtype promotion, without promising that every integer value
    remains exact.
    """
    raise NotImplementedError("Implement promote_pair")


def checked_integer_cast(values: np.ndarray, dtype: str) -> np.ndarray:
    """
    Accept a one-dimensional signed or unsigned integer array and an integer destination
    dtype string. Return an independent array only if every mathematical input value fits
    the destination range. Empty inputs are valid. Reject noninteger source/destination
    dtypes, nonvector inputs and out-of-range values with ValueError. Do not accept float
    values merely because they look integral.
    """
    raise NotImplementedError("Implement checked_integer_cast")


def checked_integer_add(left: np.ndarray, right: np.ndarray, dtype: str) -> np.ndarray:
    """
    Accept two equal-length one-dimensional integer arrays and an integer destination dtype
    string. Add each pair using Python integer arithmetic, then reject with ValueError if
    any result is outside the destination range. Inputs need not themselves fit that
    destination. Return a new destination-typed array; preserve empty inputs. Reject invalid
    shape or dtype with ValueError.
    """
    raise NotImplementedError("Implement checked_integer_add")


def exact_integer_sum(values: np.ndarray) -> int:
    """
    Return the exact Python int sum of a one-dimensional signed or unsigned integer array.
    Empty input returns the Python integer zero. Reject float, bool, complex, object and
    nonvector inputs with ValueError. Do not use fixed-width accumulation or convert through
    floating point.
    """
    raise NotImplementedError("Implement exact_integer_sum")


def float64_exact_mask(values: np.ndarray) -> np.ndarray:
    """
    For a one-dimensional signed or unsigned integer array, return a boolean vector
    indicating whether each value is exactly representable as float64. Compare through
    Python int and float, without casting a rounded float back into a fixed-width integer
    dtype. Empty input returns an empty boolean vector. Reject noninteger or nonvector input
    with ValueError.
    """
    raise NotImplementedError("Implement float64_exact_mask")


def worked_examples() -> None:
    import numpy as np

    pixels = np.array([250, 10], dtype=np.uint8)
    wrapped = pixels + np.uint8(10)
    widened = pixels.astype(np.uint16) + np.uint16(10)
    assert wrapped.tolist() == [4, 20]
    assert widened.tolist() == [260, 20]
    print("stored:", pixels.dtype, "wrapped:", wrapped.tolist(), "wide:", widened.tolist())

    import numpy as np

    single = np.array([1.0], dtype=np.float32)
    weak = single + 0.5
    strong = single + np.float64(0.5)
    assert weak.dtype == np.dtype("float32")
    assert strong.dtype == np.dtype("float64")
    ids = np.array([2**53, 2**53 + 1], dtype=np.int64)
    rounded = ids.astype(np.float64)
    assert rounded[0] == rounded[1]
    assert int(ids[0]) != int(ids[1])
    print("scalar types:", weak.dtype, strong.dtype, "rounded IDs:", rounded.tolist())


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Implement and check all six exercise contracts.")

# Exercise 1: Inspect storage before arithmetic
# Contract: numeric_schema
# Prompt: Return a dictionary with dtype (dtype.name), shape (tuple), itemsize (int), and bounds
# (inclusive Python integer min/max tuple for integer dtypes, otherwise None). Accept arrays of
# any shape with signed integer, unsigned integer, or real floating dtype. Inspection permits
# nonfinite floats. Reject bool, complex, object and string dtypes with ValueError; do not mutate
# the input.
# Expected: uint8 [1] reports uint8, (1,), 1 and (0, 255). An empty float32 vector reports shape
# (0,), itemsize 4 and bounds None.

# Exercise 2: Make common-dtype conversion visible
# Contract: promote_pair
# Prompt: For equal-shaped finite real integer or floating arrays, return two independent copies
# converted to np.result_type(left.dtype, right.dtype). Reject unequal shapes,
# bool/complex/object/string dtypes and nonfinite values with ValueError. Preserve sources. This
# follows dtype promotion, without promising that every integer value remains exact.
# Expected: int64 [2**53 + 1] paired with uint64 [0] produces two float64 copies; the first
# integer is rounded. The same dtype on both sides still produces independent copies.

# Exercise 3: Reject range loss before casting
# Contract: checked_integer_cast
# Prompt: Accept a one-dimensional signed or unsigned integer array and an integer destination
# dtype string. Return an independent array only if every mathematical input value fits the
# destination range. Empty inputs are valid. Reject noninteger source/destination dtypes,
# nonvector inputs and out-of-range values with ValueError. Do not accept float values merely
# because they look integral.
# Expected: [0, 255] casts to uint8; [-1] and [256] cannot. uint64 [2**64 - 1] cannot cast to
# int64. Empty int64 input becomes shape (0,) with the requested dtype.

# Exercise 4: Compute then validate an exact integer sum
# Contract: checked_integer_add
# Prompt: Accept two equal-length one-dimensional integer arrays and an integer destination dtype
# string. Add each pair using Python integer arithmetic, then reject with ValueError if any result
# is outside the destination range. Inputs need not themselves fit that destination. Return a new
# destination-typed array; preserve empty inputs. Reject invalid shape or dtype with ValueError.
# Expected: [120] + [7] fits int8; [127] + [1] does not. [300] + [-300] fits uint8 as [0], despite
# the operands not fitting it.

# Exercise 5: Accumulate beyond fixed-width limits
# Contract: exact_integer_sum
# Prompt: Return the exact Python int sum of a one-dimensional signed or unsigned integer array.
# Empty input returns the Python integer zero. Reject float, bool, complex, object and nonvector
# inputs with ValueError. Do not use fixed-width accumulation or convert through floating point.
# Expected: int64 [2**63 - 1, 1] returns 2**63. Two uint64 maximum values return 2 * (2**64 - 1),
# without wrapping or rounding.

# Exercise 6: Audit representability without an unsafe round trip
# Contract: float64_exact_mask
# Prompt: For a one-dimensional signed or unsigned integer array, return a boolean vector
# indicating whether each value is exactly representable as float64. Compare through Python int
# and float, without casting a rounded float back into a fixed-width integer dtype. Empty input
# returns an empty boolean vector. Reject noninteger or nonvector input with ValueError.
# Expected: int64 [2**53, 2**53 + 1, 2**53 + 2, 2**63 - 1] yields [True, False, True, False].
# uint64 [2**64 - 1] yields [False].
