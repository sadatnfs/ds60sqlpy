"""python-numpy-02: Axes, Broadcasting, and Batched Linear Algebra.

Run the worked examples, then implement the six contracts below.
Official implementations remain in solutions/.
"""

import numpy as np


def column_center(values: np.ndarray) -> np.ndarray:
    """
    Return a new floating matrix whose columns have zero means. Require a finite
    two-dimensional array with at least one row. Test two rows and three columns so
    row/column mistakes cannot pass accidentally.
    """
    raise NotImplementedError("Implement column_center")


def scale_rows(values: np.ndarray, factors: np.ndarray) -> np.ndarray:
    """
    Multiply each matrix row by its corresponding finite factor without mutating either
    input. Require factors to be a one-dimensional vector whose length equals the number of
    rows. Permit an empty row batch.
    """
    raise NotImplementedError("Implement scale_rows")


def pairwise_squared(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """
    Return squared Euclidean distances between rows of two finite matrices with equal
    feature counts. Support empty row sets. Reject mismatched feature dimensions or
    unrepresentable squared distances with ValueError. Use the tiny broadcasted difference,
    not Python nested loops.
    """
    raise NotImplementedError("Implement pairwise_squared")


def weighted_columns(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """
    Return weighted column means for a finite matrix using one nonnegative finite weight per
    row. Require positive total weight. Reject negative weights, zero total or wrong length,
    rather than dividing and returning NaNs.
    """
    raise NotImplementedError("Implement weighted_columns")


def batched_projection(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """
    Apply a finite two-dimensional weight matrix(d, k) to values with at least two
    dimensions and final dimension d. Return all leading dimensions followed by k. Reject an
    incompatible final dimension.
    """
    raise NotImplementedError("Implement batched_projection")


def unit_rows(values: np.ndarray) -> np.ndarray:
    """
    Return a new finite matrix whose nonzero rows have Euclidean norm one and zero rows
    remain zero. Reject nonfinite or nonmatrix inputs. Avoid evaluating a zero division and
    then hiding its warning.
    """
    raise NotImplementedError("Implement unit_rows")


def worked_examples() -> None:
    x = np.array([[1.0, 3.0, 5.0], [2.0, 4.0, 9.0]])
    centered = x - x.mean(axis=1, keepdims=True)
    assert centered.shape == (2, 3) and np.allclose(centered.mean(axis=1), 0)
    print("Row centered:", centered.tolist())

    a = np.array([[0.0, 0.0], [3.0, 4.0]])
    b = np.array([[0.0, 4.0], [3.0, 0.0], [0.0, 0.0]])
    difference = a[:, None, :] - b[None, :, :]
    distance = np.sqrt(np.sum(difference**2, axis=-1))
    assert distance.shape == (2, 3)
    assert np.allclose(distance, [[4, 3, 0], [3, 4, 5]])
    print("Pairwise distances:", distance.tolist())


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Complete the six task functions and their boundary checks.")

# Exercise 1: Reduce the observation axis
# Prompt: Return a new floating matrix whose columns have zero means. Require a finite
# two-dimensional array with at least one row. Test two rows and three columns so row/column
# mistakes cannot pass accidentally.
# Expected: [[1,10,100],[3,14,108]] becomes[[-1,-2,-4],[1,2,4]]. The source is unchanged;
# shape(0,3) and a vector raise ValueError.

# Exercise 2: Broadcast one factor per row
# Prompt: Multiply each matrix row by its corresponding finite factor without mutating either
# input. Require factors to be a one-dimensional vector whose length equals the number of rows.
# Permit an empty row batch.
# Expected: [[1,2,3],[4,5,6]] with [10,100] gives [[10,20,30],[400,500,600]]. Three factors raise
# ValueError; shape(0,3) with an empty vector returns (0,3).

# Exercise 3: Create all pairs with a declared contraction
# Prompt: Return squared Euclidean distances between rows of two finite matrices with equal
# feature counts. Support empty row sets. Reject mismatched feature dimensions or unrepresentable
# squared distances with ValueError. Use the tiny broadcasted difference, not Python nested loops.
# Expected: [[0,0],[3,4]] against [[0,0]] yields [[0],[25]]. Empty left shape(0,2) returns
# shape(0,1); two versus three features raises ValueError.

# Exercise 4: Contract observations using valid weights
# Prompt: Return weighted column means for a finite matrix using one nonnegative finite weight per
# row. Require positive total weight. Reject negative weights, zero total or wrong length, rather
# than dividing and returning NaNs.
# Expected: [[1,10],[3,30]] with [1,3] gives [2.5,25]. Weights[0,0],[-1,2] and [1] raise
# ValueError; weights scaled by ten give the same means.

# Exercise 5: Preserve leading batch axes
# Prompt: Apply a finite two-dimensional weight matrix(d, k) to values with at least two
# dimensions and final dimension d. Return all leading dimensions followed by k. Reject an
# incompatible final dimension.
# Expected: A(2,3,4) input times a(4,2) weight matrix returns (2,3,2), matching an explicit
# per-batch matrix multiply. A(3,4) input also works; weights(3,2) are rejected.

# Exercise 6: Normalize while preserving zero vectors
# Prompt: Return a new finite matrix whose nonzero rows have Euclidean norm one and zero rows
# remain zero. Reject nonfinite or nonmatrix inputs. Avoid evaluating a zero division and then
# hiding its warning.
# Expected: [[3,4],[0,0],[-2,0]] becomes[[.6,.8],[0,0],[-1,0]]. All results are finite, source
# stays unchanged and infinity raises ValueError.
