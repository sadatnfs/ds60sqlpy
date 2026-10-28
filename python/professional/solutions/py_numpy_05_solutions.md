# python-numpy-05: Explained reference solutions

These answers accompany [NumPy Dtypes, Promotion, and Overflow Contracts](../companion-guides/py_numpy_05.md). Compare after an honest attempt. The [complete standalone executable reference](py_numpy_05_solution.py) includes imports, shared validation helpers and a `main()` that exercises every contract. The snippets below use those helpers; run the complete reference for a fresh-process check. Each named function matches the learner artifact.

## Exercise 1: Inspect storage before arithmetic

**Contract: `numeric_schema`.** Return a dictionary with dtype (dtype.name), shape (tuple), itemsize (int), and bounds (inclusive Python integer min/max tuple for integer dtypes, otherwise None). Accept arrays of any shape with signed integer, unsigned integer, or real floating dtype. Inspection permits nonfinite floats. Reject bool, complex, object and string dtypes with ValueError; do not mutate the input.

**Expected:** uint8 [1] reports uint8, (1,), 1 and (0, 255). An empty float32 vector reports shape (0,), itemsize 4 and bounds None.

```python
def numeric_schema(values: np.ndarray) -> dict:
    x = _real_array(values)
    bounds = None
    if x.dtype.kind in "iu":
        info = np.iinfo(x.dtype)
        bounds = (int(info.min), int(info.max))
    return {"dtype": x.dtype.name, "shape": x.shape, "itemsize": x.itemsize, "bounds": bounds}
```

The dtype is a storage contract shared by every element. np.iinfo describes representable bounds, not the minimum and maximum observed values. Inspecting a floating array does not perform arithmetic, so this function can describe NaN storage without accepting NaN in later operations. Keeping schema inspection distinct from domain validation prevents an accidental claim that every value is suitable for calculation.

## Exercise 2: Make common-dtype conversion visible

**Contract: `promote_pair`.** For equal-shaped finite real integer or floating arrays, return two independent copies converted to np.result_type(left.dtype, right.dtype). Reject unequal shapes, bool/complex/object/string dtypes and nonfinite values with ValueError. Preserve sources. This follows dtype promotion, without promising that every integer value remains exact.

**Expected:** int64 [2**53 + 1] paired with uint64 [0] produces two float64 copies; the first integer is rounded. The same dtype on both sides still produces independent copies.

```python
def promote_pair(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a, b = _real_array(left), _real_array(right)
    if a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Expected equal shapes with finite values")
    destination = np.result_type(a.dtype, b.dtype)
    return a.astype(destination, copy=True), b.astype(destination, copy=True)
```

Use dtype objects rather than Python scalar values when planning the common type. There is no standard signed integer dtype that represents the entire combined int64 and uint64 ranges, so float64 is selected. Its precision is insufficient for every 64-bit integer. This is a deliberate counterexample to interpreting promotion as a lossless cast. copy=True gives the ownership guarantee even when no dtype change is necessary.

## Exercise 3: Reject range loss before casting

**Contract: `checked_integer_cast`.** Accept a one-dimensional signed or unsigned integer array and an integer destination dtype string. Return an independent array only if every mathematical input value fits the destination range. Empty inputs are valid. Reject noninteger source/destination dtypes, nonvector inputs and out-of-range values with ValueError. Do not accept float values merely because they look integral.

**Expected:** [0, 255] casts to uint8; [-1] and [256] cannot. uint64 [2**64 - 1] cannot cast to int64. Empty int64 input becomes shape (0,) with the requested dtype.

```python
def checked_integer_cast(values: np.ndarray, dtype: str) -> np.ndarray:
    x = _integers(values)
    destination = _integer_dtype(dtype)
    bounds = np.iinfo(destination)
    exact = [int(value) for value in x]
    if any(value < int(bounds.min) or value > int(bounds.max) for value in exact):
        raise ValueError("An input is outside the destination integer range")
    return np.array(exact, dtype=destination)
```

A cast is not a range validator. Inspect Python integer values against Python integer bounds before constructing the destination array. This avoids overflow in mixed signed/unsigned comparisons and avoids any float64 conversion. Rejecting float input is an API policy: a separate application could define truncation or rounding, but silently choosing one here would alter the contract.

## Exercise 4: Compute then validate an exact integer sum

**Contract: `checked_integer_add`.** Accept two equal-length one-dimensional integer arrays and an integer destination dtype string. Add each pair using Python integer arithmetic, then reject with ValueError if any result is outside the destination range. Inputs need not themselves fit that destination. Return a new destination-typed array; preserve empty inputs. Reject invalid shape or dtype with ValueError.

**Expected:** [120] + [7] fits int8; [127] + [1] does not. [300] + [-300] fits uint8 as [0], despite the operands not fitting it.

```python
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
```

Convert each operand to Python int before addition. Converting an already wrapped NumPy result cannot reconstruct the lost mathematical sum. Validation concerns the final sum, so cancellation can produce a valid narrow output from wider inputs. This deliberately favors explicit correctness over vectorized throughput for tiny teaching fixtures. Production scale may justify a vectorized checked algorithm after equivalent edge cases are proved.

## Exercise 5: Accumulate beyond fixed-width limits

**Contract: `exact_integer_sum`.** Return the exact Python int sum of a one-dimensional signed or unsigned integer array. Empty input returns the Python integer zero. Reject float, bool, complex, object and nonvector inputs with ValueError. Do not use fixed-width accumulation or convert through floating point.

**Expected:** int64 [2**63 - 1, 1] returns 2**63. Two uint64 maximum values return 2 * (2**64 - 1), without wrapping or rounding.

```python
def exact_integer_sum(values: np.ndarray) -> int:
    return sum(int(value) for value in _integers(values))
```

The empty identity and accumulator must both be Python integers. A NumPy reduction may promote a small dtype, but no fixed-width destination provides unlimited integer capacity. Summing converted scalar values supplies arbitrary precision. This is useful for reference checks and exact bounded accounting; it is not a claim that object-based arithmetic is the fastest numerical representation.

## Exercise 6: Audit representability without an unsafe round trip

**Contract: `float64_exact_mask`.** For a one-dimensional signed or unsigned integer array, return a boolean vector indicating whether each value is exactly representable as float64. Compare through Python int and float, without casting a rounded float back into a fixed-width integer dtype. Empty input returns an empty boolean vector. Reject noninteger or nonvector input with ValueError.

**Expected:** int64 [2**53, 2**53 + 1, 2**53 + 2, 2**63 - 1] yields [True, False, True, False]. uint64 [2**64 - 1] yields [False].

```python
def float64_exact_mask(values: np.ndarray) -> np.ndarray:
    x = _integers(values)
    # Python integers avoid an overflowing float-to-int64 round trip at 2**63.
    return np.array([int(float(int(value))) == int(value) for value in x], dtype=bool)
```

Float64 has 53 significant binary digits. Beyond 2**53, spacing grows, but some larger integers remain representable. Testing only whether magnitude exceeds 2**53 would reject valid even integers. Python int(float(value)) safely returns the rounded mathematical integer even at 2**63 or 2**64, where a fixed-width round trip would itself be unsafe. The mask reports representability, not an acceptable business error.

## Verification and interpretation

The executable reference covers normal and invalid examples for these contracts. Independent tests in `tests/test_python_numpy_modernization.py` use analytical answers, invariants and changed-condition cases rather than treating the reference output as its own oracle. A reference run is evidence that the implementation meets the tested inputs; explain the relevant assumption and construct an additional counterexample before claiming independent understanding.
