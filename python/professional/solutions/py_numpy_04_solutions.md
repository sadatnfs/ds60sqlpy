# python-numpy-04: Explained reference solutions

These answers implement the contracts in [Stable Numerical Computation and Honest Error Bounds](../companion-guides/py_numpy_04.md). Compare after an attempt. The [executable reference](py_numpy_04_solution.py) contains the complete implementations and assertions. Each answer explains the mechanism, not just the final value.

## Exercises and reasoning

### Exercise 1: Aggregate log weights without overflow

Implement stable log(sum(exp(values))) for a one-dimensional array. Allow finite values and negative infinity; reject NaN or positive infinity. Define the empty input and an all-negative-infinity input as negative infinity.

**Expected:** [1000,1000] yields 1000+log(2) without infinity; [-inf,-inf] and empty return-inf. [NaN] and [inf] raise ValueError.

```python
def logsumexp(values: np.ndarray) -> float:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or np.isnan(x).any() or np.isposinf(x).any():
        raise ValueError("Expected finite or negative-infinite log weights")
    if x.size == 0 or np.isneginf(x).all():
        return -math.inf
    maximum = float(x.max())
    with np.errstate(over="ignore"):
        shifted = x - maximum
    return maximum + math.log(float(np.exp(shifted).sum()))
```

The maximum shift bounds all exponential inputs above by zero. A very negative shifted value can become negative infinity through subtraction overflow, which correctly contributes zero exponential weight; this specific operation is handled explicitly. The all-negative-infinity case is separated before subtracting to avoid an undefined infinity-minus-infinity operation. Empty aggregation has zero total weight, whose logarithm is the declared negative-infinity identity.

```python
assert math.isclose(logsumexp(np.array([1000.0, 1000.0])), 1000 + math.log(2))
assert logsumexp(np.array([-np.inf, -np.inf])) == -np.inf
assert logsumexp(np.array([])) == -np.inf
expect_value_error(lambda: logsumexp(np.array([np.nan])))
expect_value_error(lambda: logsumexp(np.array([np.inf])))
```

### Exercise 2: Normalize large scores

Return softmax probabilities for a nonempty finite vector using a maximum shift. Preserve the source and reject NaN, infinity, empty or nonvector inputs. Test invariance when a constant is added to every score.

**Expected:** [1000,1001] returns finite probabilities summing to one with the second larger. Adding-1000 produces the same probabilities; equal scores give [.5,.5].

```python
def softmax(scores: np.ndarray) -> np.ndarray:
    x = np.asarray(scores, dtype=float)
    if x.ndim != 1 or x.size == 0 or not np.isfinite(x).all():
        raise ValueError("Expected a nonempty finite score vector")
    with np.errstate(over="ignore"):
        weight = np.exp(x - x.max())
    return np.asarray(weight / weight.sum())
```

At least one shifted score is zero, so at least one exponential is one and the denominator cannot vanish. Other sufficiently negative scores can underflow to zero without causing normalization failure. Shift invariance is a mathematical property independent of the exact printed probabilities. The result is a normalized score transformation, not proof that the probabilities are statistically calibrated for any real classification problem.

```python
s = np.array([1000.0, 1001.0])
p = softmax(s)
assert np.isfinite(p).all() and np.isclose(p.sum(), 1) and p[1] > p[0]
assert np.allclose(p, softmax(s - 1000)) and np.allclose(softmax(np.array([7.0, 7.0])), [0.5, 0.5])
expect_value_error(lambda: softmax(np.array([])))
expect_value_error(lambda: softmax(np.array([np.inf])))
```

### Exercise 3: Preserve small contributions

Sum a finite one-dimensional array using math.fsum after conversion to Python floats. Return zero for empty input. Reject nonfinite inputs or a final overflow with ValueError. Demonstrate a cancellation case rather than only positive small integers.

**Expected:** [1e16,1,-1e16] returns 1; empty returns 0; [inf] and [1e308,1e308] raise ValueError.

```python
def accurate_sum(values: np.ndarray) -> float:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or not np.isfinite(x).all():
        raise ValueError("Expected finite summands")
    try:
        return math.fsum(float(value) for value in x)
    except OverflowError as error:
        raise ValueError("The sum exceeds floating-point range") from error
```

Compensated partial-sum logic avoids losing the small contribution in the supplied cancellation example. Converting inputs to Python floats makes the representation boundary explicit. The overflow case distinguishes precision loss that an improved algorithm can reduce from a final result the representation cannot hold. Returning infinity would violate the finite-result interpretation, so overflow is surfaced as a contract error.

```python
assert accurate_sum(np.array([1e16, 1.0, -1e16])) == 1.0
assert accurate_sum(np.array([])) == 0.0
expect_value_error(lambda: accurate_sum(np.array([np.inf])))
expect_value_error(lambda: accurate_sum(np.array([1e308, 1e308])))
```

### Exercise 4: Promote before multiplying

Compute a floating dot product of equal-length finite vectors, converting operands before multiplication. Reject shape mismatch or an unrepresentable nonfinite result. Empty equal vectors return zero. This contract is approximate floating arithmetic, not exact integer accounting.

**Expected:** int64[2**62] dotted with int64[4] yields float(2**64), not integer overflow zero. Length mismatch raises ValueError, and empty vectors return 0.

```python
def floating_dot(left: np.ndarray, right: np.ndarray) -> float:
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    if (
        a.ndim != 1
        or b.ndim != 1
        or a.shape != b.shape
        or not np.isfinite(a).all()
        or not np.isfinite(b).all()
    ):
        raise ValueError("Expected equal finite vectors")
    with np.errstate(over="ignore", invalid="ignore"):
        result = float(np.dot(a, b))
    if not math.isfinite(result):
        raise ValueError("Dot product exceeds finite floating range")
    return result
```

Promotion happens before the multiplication, which avoids wrapping the int64 product. The chosen power-of-two result is exactly representable as a float, making the expected value unambiguous. Other large integers may lose low-order digits on conversion, so this is not an exactness guarantee for arbitrary integer values. A finite-output check catches arithmetic range failures that a successful array shape match cannot detect.

```python
a = np.array([2**62], dtype=np.int64)
b = np.array([4], dtype=np.int64)
assert floating_dot(a, b) == float(2**64)
assert floating_dot(np.array([]), np.array([])) == 0
expect_value_error(lambda: floating_dot(np.array([1]), np.array([1, 2])))
expect_value_error(lambda: floating_dot(np.array([1e308]), np.array([1e308])))
```

### Exercise 5: Separate solver residual from conditioning

Solve a nonempty finite square system with a matching finite target vector. Require a finite condition limit of at least one and reject systems whose condition number exceeds it. Use np.linalg.solve, not an explicit inverse.

**Expected:** diag(2,4) with [6,8] returns [3,2] and a zero residual within tolerance. A duplicate-row system and diag(1,1e-12) at default limit raise ValueError.

```python
def solve_checked(
    matrix: np.ndarray, target: np.ndarray, max_condition: float = 1e10
) -> np.ndarray:
    a = np.asarray(matrix, dtype=float)
    b = np.asarray(target, dtype=float)
    if (
        a.ndim != 2
        or a.shape[0] == 0
        or a.shape[0] != a.shape[1]
        or b.shape != (a.shape[0],)
        or not np.isfinite(a).all()
        or not np.isfinite(b).all()
        or not math.isfinite(max_condition)
        or max_condition < 1
    ):
        raise ValueError("Expected a finite square system and valid condition limit")
    condition = float(np.linalg.cond(a))
    if not math.isfinite(condition) or condition > max_condition:
        raise ValueError("System is singular or exceeds the condition policy")
    return np.asarray(np.linalg.solve(a, b))
```

The condition-number gate is an explicit policy about sensitivity, not a universal scientific cutoff. A matrix can be invertible yet too sensitive for the intended precision. Solving directly avoids forming an unnecessary inverse, while the residual check verifies the answer against the supplied equations. It does not prove that small changes to measured matrix entries would leave the solution stable; that is why conditioning is examined separately.

```python
a = np.diag([2.0, 4.0])
b = np.array([6.0, 8.0])
x = solve_checked(a, b)
assert np.allclose(x, [3, 2]) and np.linalg.norm(a @ x - b) < 1e-12
expect_value_error(lambda: solve_checked(np.ones((2, 2)), np.ones(2)))
expect_value_error(lambda: solve_checked(np.diag([1.0, 1e-12]), np.ones(2)))
```

### Exercise 6: Make numerical comparison semantics explicit

Compare finite arrays with exactly equal shapes using abs(actual-expected)<=atol+rtol*abs(expected) elementwise. Require finite nonnegative tolerances. Reject broadcasting-compatible but unequal shapes and nonfinite values. Empty equal arrays return True.

**Expected:** Actual[1e8+1,1e-9] versus expected[1e8,0] passes with atol 1 e-8, rtol 1 e-7; it fails with zero tolerances. Shapes(2,) and (1,2) raise ValueError.

```python
def within_tolerance(actual: np.ndarray, expected: np.ndarray, atol: float, rtol: float) -> bool:
    a = np.asarray(actual, dtype=float)
    b = np.asarray(expected, dtype=float)
    if (
        a.shape != b.shape
        or not np.isfinite(a).all()
        or not np.isfinite(b).all()
        or not math.isfinite(atol)
        or not math.isfinite(rtol)
        or atol < 0
        or rtol < 0
    ):
        raise ValueError("Expected equal finite shapes and nonnegative tolerances")
    scale = np.maximum(np.abs(a), np.abs(b))
    safe_scale = np.where(scale == 0, 1.0, scale)
    with np.errstate(over="ignore", under="ignore"):
        distance = np.abs(a / safe_scale - b / safe_scale)
        allowance = atol / safe_scale + rtol * (np.abs(b) / safe_scale)
    return bool(np.all(distance <= allowance))
```

Absolute tolerance allows a small error near a zero reference, while relative tolerance scales with the expected magnitude. Scaling both sides by the larger absolute input avoids an infinity-versus-infinity comparison when opposite large finite values are subtracted. The comparison remains reference-oriented rather than symmetric. Exact shape equality prevents broadcasting from turning a structural error into a passing numerical check. Empty matching arrays satisfy the all-elements condition vacuously, but a caller still needs separate evidence that an empty output is scientifically appropriate.

```python
a = np.array([1e8 + 1, 1e-9])
b = np.array([1e8, 0.0])
assert within_tolerance(a, b, 1e-8, 1e-7) and not within_tolerance(a, b, 0, 0)
assert within_tolerance(np.array([]), np.array([]), 0, 0)
assert not within_tolerance(np.array([1.7e308]), np.array([-1.7e308]), 0, 1.9)
assert within_tolerance(np.array([1.7e308]), np.array([-1.7e308]), 0, 2.0)
expect_value_error(lambda: within_tolerance(np.ones(2), np.ones((1, 2)), 0, 0))
expect_value_error(lambda: within_tolerance(a, b, -1, 0))
```

## Verification and interpretation

Run `python python/professional/solutions/py_numpy_04_solution.py` from the repository root with the prepared interpreter. The code checks normal inputs and explicit edge cases before printing its success line. Assertions are the evidence; the printed sentence alone is not. The helper `expect_value_error` requires an actual `ValueError` and fails if a function silently accepts an invalid input. Inspect each function's mutation and ordering behavior as part of its contract.
