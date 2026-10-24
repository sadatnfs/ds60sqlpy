"""python-numpy-03: Gather, Scatter, Masks, and Deterministic Selection.

Run the worked examples, then implement the six contracts below.
Official implementations remain in solutions/.
"""

import numpy as np


def gather_positions(values: np.ndarray, positions: np.ndarray) -> np.ndarray:
    """
    Gather a one-dimensional source using a one-dimensional integer index array. Allow
    negative positions in the normal NumPy range and preserve duplicates/order. Reject
    Boolean, floating or out-of-range indices with ValueError. Return an independent result.
    """
    raise NotImplementedError("Implement gather_positions")


def sum_by_code(values: np.ndarray, codes: np.ndarray, bins: int) -> np.ndarray:
    """
    Sum finite one-dimensional values into bins using one nonnegative integer code per
    value. Reject unequal lengths, invalid codes or negative/noninteger bin counts. Zero
    bins are allowed only with empty inputs. Preserve every repeated-code contribution.
    """
    raise NotImplementedError("Implement sum_by_code")


def select_rows(values: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Filter a matrix using an exactly matching one-dimensional Boolean row mask. Preserve
    selected order and return independent storage. Reject integer flags, a cell-shaped mask
    or wrong row count with ValueError.
    """
    raise NotImplementedError("Implement select_rows")


def cartesian_submatrix(values: np.ndarray, rows: np.ndarray, columns: np.ndarray) -> np.ndarray:
    """
    Return a Cartesian submatrix from nonnegative integer row and column arrays. Preserve
    duplicates and index-array order in both axes. Reject out-of-range, Boolean or
    noninteger indices. An empty selection on either axis must preserve the other output
    dimension.
    """
    raise NotImplementedError("Implement cartesian_submatrix")


def stable_top_indices(scores: np.ndarray, k: int) -> np.ndarray:
    """
    Return indices of the k largest finite one-dimensional scores in descending score order,
    breaking ties by original position. Require an integer k between zero and the number of
    scores, rejecting Boolean k. Do not mutate scores.
    """
    raise NotImplementedError("Implement stable_top_indices")


def inverse_permutation(order: np.ndarray) -> np.ndarray:
    """
    Return the inverse of a one-dimensional integer permutation of 0 through n-1. Reject
    duplicates, missing positions, negative values and noninteger dtype. Support the empty
    permutation. Demonstrate recovery of records after reordering.
    """
    raise NotImplementedError("Implement inverse_permutation")


def worked_examples() -> None:
    values = np.array([10, 20, 30, 40])
    selected = values[np.array([3, 1, 1])]
    selected[0] = -1
    assert values.tolist() == [10, 20, 30, 40]
    assert selected.tolist() == [-1, 20, 20]
    print("Gathered copy:", selected.tolist())

    indices = np.array([0, 0, 2])
    updates = np.array([1.0, 2.0, 5.0])
    buffered = np.zeros(3)
    buffered[indices] += updates
    accumulated = np.zeros(3)
    np.add.at(accumulated, indices, updates)
    assert accumulated.tolist() == [3.0, 0.0, 5.0]
    assert buffered[0] != accumulated[0]
    print("Accumulated repeated indices:", accumulated.tolist())


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Complete the six task functions and their boundary checks.")

# Exercise 1: Gather with explicit index rules
# Prompt: Gather a one-dimensional source using a one-dimensional integer index array. Allow
# negative positions in the normal NumPy range and preserve duplicates/order. Reject Boolean,
# floating or out-of-range indices with ValueError. Return an independent result.
# Expected: [10,20,30] with [2,-1,0] yields [30,30,10]. Empty integer positions return shape(0,).
# Position 3, float1.0 or a Boolean index array raises ValueError.

# Exercise 2: Accumulate repeated category codes
# Prompt: Sum finite one-dimensional values into bins using one nonnegative integer code per
# value. Reject unequal lengths, invalid codes or negative/noninteger bin counts. Zero bins are
# allowed only with empty inputs. Preserve every repeated-code contribution.
# Expected: Values[1,2,5] and codes[0,0,2] with 3 bins produce[3,0,5]. Empty inputs and zero bins
# produce shape(0,); code 3 for 3 bins raises ValueError.

# Exercise 3: Validate a row mask
# Prompt: Filter a matrix using an exactly matching one-dimensional Boolean row mask. Preserve
# selected order and return independent storage. Reject integer flags, a cell-shaped mask or wrong
# row count with ValueError.
# Expected: [[1,2],[3,4],[5,6]] with [True, False, True] gives [[1,2],[5,6]]. All false gives
# shape(0,2); an integer[1,0,1] mask is rejected.

# Exercise 4: Select every row-column combination
# Prompt: Return a Cartesian submatrix from nonnegative integer row and column arrays. Preserve
# duplicates and index-array order in both axes. Reject out-of-range, Boolean or noninteger
# indices. An empty selection on either axis must preserve the other output dimension.
# Expected: np.arange(12).reshape(3,4), rows[2,0], columns[3,1] gives [[11,9],[3,1]]. Empty rows
# with two columns returns shape(0,2), not a flat vector.

# Exercise 5: Make top-k ties deterministic
# Prompt: Return indices of the k largest finite one-dimensional scores in descending score order,
# breaking ties by original position. Require an integer k between zero and the number of scores,
# rejecting Boolean k. Do not mutate scores.
# Expected: [5,9,9,1] with k=3 returns [1,2,0]. k=0 returns an empty integer array; k=5 or a NaN
# score raises ValueError.

# Exercise 6: Restore original observation order
# Prompt: Return the inverse of a one-dimensional integer permutation of 0 through n-1. Reject
# duplicates, missing positions, negative values and noninteger dtype. Support the empty
# permutation. Demonstrate recovery of records after reordering.
# Expected: Order[2,0,1] has inverse[1,2,0], and original[order][inverse] equals original.
# Order[0,0] is invalid; an empty integer array returns empty.
