"""python-numpy-04: Stable Numerical Computation and Honest Error Bounds.

Run the worked examples, then implement the six contracts below.
Official implementations remain in solutions/.
"""

import math

import numpy as np


def logsumexp(values: np.ndarray) -> float:
    """
    Implement stable log(sum(exp(values))) for a one-dimensional array. Allow finite values
    and negative infinity; reject NaN or positive infinity. Define the empty input and an
    all-negative-infinity input as negative infinity.
    """
    raise NotImplementedError("Implement logsumexp")


def softmax(scores: np.ndarray) -> np.ndarray:
    """
    Return softmax probabilities for a nonempty finite vector using a maximum shift.
    Preserve the source and reject NaN, infinity, empty or nonvector inputs. Test invariance
    when a constant is added to every score.
    """
    raise NotImplementedError("Implement softmax")


def accurate_sum(values: np.ndarray) -> float:
    """
    Sum a finite one-dimensional array using math.fsum after conversion to Python floats.
    Return zero for empty input. Reject nonfinite inputs or a final overflow with
    ValueError. Demonstrate a cancellation case rather than only positive small integers.
    """
    raise NotImplementedError("Implement accurate_sum")


def floating_dot(left: np.ndarray, right: np.ndarray) -> float:
    """
    Compute a floating dot product of equal-length finite vectors, converting operands
    before multiplication. Reject shape mismatch or an unrepresentable nonfinite result.
    Empty equal vectors return zero. This contract is approximate floating arithmetic, not
    exact integer accounting.
    """
    raise NotImplementedError("Implement floating_dot")


def solve_checked(
    matrix: np.ndarray, target: np.ndarray, max_condition: float = 1e10
) -> np.ndarray:
    """
    Solve a nonempty finite square system with a matching finite target vector. Require a
    finite condition limit of at least one and reject systems whose condition number exceeds
    it. Use np.linalg.solve, not an explicit inverse.
    """
    raise NotImplementedError("Implement solve_checked")


def within_tolerance(actual: np.ndarray, expected: np.ndarray, atol: float, rtol: float) -> bool:
    """
    Compare finite arrays with exactly equal shapes using
    abs(actual-expected)<=atol+rtol*abs(expected) elementwise. Require finite nonnegative
    tolerances. Reject broadcasting-compatible but unequal shapes and nonfinite values.
    Empty equal arrays return True.
    """
    raise NotImplementedError("Implement within_tolerance")


def worked_examples() -> None:
    scores = np.array([1000.0, 1001.0, 999.0])
    shifted = scores - scores.max()
    probability = np.exp(shifted) / np.exp(shifted).sum()
    assert np.isfinite(probability).all() and np.isclose(probability.sum(), 1)
    assert probability.argmax() == 1
    print("Stable probabilities:", probability.tolist())

    values = [1e16, 1.0, -1e16]
    ordinary = float(np.sum(values))
    accurate = math.fsum(values)
    assert accurate == 1.0 and ordinary == 0.0
    a = np.array([[2.0, 0.0], [0.0, 4.0]])
    b = np.array([6.0, 8.0])
    x = np.linalg.solve(a, b)
    assert np.allclose(x, [3.0, 2.0]) and np.allclose(a @ x, b)
    print("Summation:", ordinary, accurate, "linear solution:", x.tolist())


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Complete the six task functions and their boundary checks.")

# Exercise 1: Aggregate log weights without overflow
# Prompt: Implement stable log(sum(exp(values))) for a one-dimensional array. Allow finite values
# and negative infinity; reject NaN or positive infinity. Define the empty input and an
# all-negative-infinity input as negative infinity.
# Expected: [1000,1000] yields 1000+log(2) without infinity; [-inf,-inf] and empty return-inf.
# [NaN] and [inf] raise ValueError.

# Exercise 2: Normalize large scores
# Prompt: Return softmax probabilities for a nonempty finite vector using a maximum shift.
# Preserve the source and reject NaN, infinity, empty or nonvector inputs. Test invariance when a
# constant is added to every score.
# Expected: [1000,1001] returns finite probabilities summing to one with the second larger.
# Adding-1000 produces the same probabilities; equal scores give [.5,.5].

# Exercise 3: Preserve small contributions
# Prompt: Sum a finite one-dimensional array using math.fsum after conversion to Python floats.
# Return zero for empty input. Reject nonfinite inputs or a final overflow with ValueError.
# Demonstrate a cancellation case rather than only positive small integers.
# Expected: [1e16,1,-1e16] returns 1; empty returns 0; [inf] and [1e308,1e308] raise ValueError.

# Exercise 4: Promote before multiplying
# Prompt: Compute a floating dot product of equal-length finite vectors, converting operands
# before multiplication. Reject shape mismatch or an unrepresentable nonfinite result. Empty equal
# vectors return zero. This contract is approximate floating arithmetic, not exact integer
# accounting.
# Expected: int64[2**62] dotted with int64[4] yields float(2**64), not integer overflow zero.
# Length mismatch raises ValueError, and empty vectors return 0.

# Exercise 5: Separate solver residual from conditioning
# Prompt: Solve a nonempty finite square system with a matching finite target vector. Require a
# finite condition limit of at least one and reject systems whose condition number exceeds it. Use
# np.linalg.solve, not an explicit inverse.
# Expected: diag(2,4) with [6,8] returns [3,2] and a zero residual within tolerance. A
# duplicate-row system and diag(1,1e-12) at default limit raise ValueError.

# Exercise 6: Make numerical comparison semantics explicit
# Prompt: Compare finite arrays with exactly equal shapes using
# abs(actual-expected)<=atol+rtol*abs(expected) elementwise. Require finite nonnegative
# tolerances. Reject broadcasting-compatible but unequal shapes and nonfinite values. Empty equal
# arrays return True.
# Expected: Actual[1e8+1,1e-9] versus expected[1e8,0] passes with atol 1 e-8, rtol 1 e-7; it fails
# with zero tolerances. Shapes(2,) and (1,2) raise ValueError.
