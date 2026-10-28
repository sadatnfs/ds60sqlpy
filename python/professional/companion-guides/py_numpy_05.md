# NumPy Dtypes, Promotion, and Overflow Contracts

## Level and prerequisites

- **Stable ID:** `python-numpy-05`.
- **Level:** Advanced. Allow about 100 minutes for explanations, prediction and practice; the estimate is not a deadline.
- **Direct prerequisite:** `python-16`, [companion guide](../../ds-60day/companion-guides/day16_numpy_fundamentals.md).
- **Direct prerequisite:** `python-numpy-01`, [companion guide](py_numpy_01.md).
- **Artifacts:** [learner script](../lessons/py_numpy_05.py) · [explained reference](../solutions/py_numpy_05_solutions.md) · [executable reference](../solutions/py_numpy_05_solution.py).

## How to run this lesson

Run `./classroom` from the repository root, choose **Python** in the shared
`/classroom` directory, and open `python-numpy-05`. Read the capability notice and
use the saved coding pad with the prepared Python Core environment. Docker
supplies Python and NumPy 2.x; no host package install or notebook kernel is
needed. Windows learners use the same entrypoint in WSL 2. Paste the complete
[learner script](../lessons/py_numpy_05.py), save it, and Run its worked
examples before attempting the six task functions. Those functions remain for
you to implement; a passing demonstration does not complete their contracts.

Each browser Run starts a fresh process. Include imports, fixtures and function
calls in the saved source, and save predictions and evidence in your notes.
Temporary arrays and generator objects do not survive the process, whereas the
browser's saved work lives in its Docker learning volume. Use only the tiny
original offline fixtures here; no download, service or database is required.
The [classroom guide](../../../docs/classroom-experience.md) explains that lifecycle.

A separately prepared contributor environment may run
`uv run --no-sync python python/professional/lessons/py_numpy_05.py`
from its checkout. Follow [contributor setup](../../../CONTRIBUTING.md) first;
that environment has separate files and does not import the browser's saved
learning volume. Keep the separate answers closed until you choose to compare
a genuine attempt.

## Learning objectives

This unit is `python-numpy-05`. Complete `python-16` and `python-numpy-01` first: you should be able to construct arrays, inspect shape, distinguish a view from a copy, and write a validating function. Use the Docker classroom's prepared Python Core environment, select this unit, and run its learner script. The examples use NumPy 2.x and tiny offline inputs. Each classroom Run starts a fresh process; no notebook state or package installation is required.

Your outcome is a small set of explicit representation contracts. You will distinguish a dtype selected by NumPy from a dtype that preserves the values your application needs. Evidence should include a valid result, a rejected boundary, the output dtype, and proof that callers' arrays were preserved. This extends earlier memory and numerical-stability work by making range and exactness decisions observable before arithmetic starts.

By the end of this lesson, you can:

- Predict when a narrow integer operation wraps and move widening before the operation.
- Inspect dtype bounds and distinguish dtype promotion from value-preserving conversion.
- Validate integer casts, elementwise sums and accumulation using an exact Python-integer oracle.
- Identify individual integer values that remain exactly representable as float64 without an unsafe fixed-width round trip.

## Vocabulary and concepts: the model behind a dtype

**Dtype:** Specifies how each element occupies storage. Signed integers reserve a sign bit; unsigned integers use all their bits for nonnegative values. For an unsigned width of \(b\) bits, the range is \(0\) through \(2^b-1\). For a conventional signed width, it is \(-2^{b-1}\) through \(2^{b-1}-1\). `np.iinfo(dtype)` reports those bounds. The observed data maximum and the storage maximum answer different questions.

A floating dtype represents a finite set of numbers with a scale-dependent spacing. Float64 has 53 significant binary digits, including its implicit leading bit. Every integer through \(2^{53}\) is exactly representable, but above that point consecutive integers need not be distinct after conversion. Range and precision are different: a float can represent a number near a large integer while losing its exact identity.

**Promotion:** Chooses a computation dtype when operands differ.

**Casting:** Converts values to a chosen dtype.

**Overflow:** Occurs when a mathematical result exceeds the representation's range. A narrowing integer cast can discard information; array integer arithmetic can wrap. An operation that completes without an exception is therefore not evidence that the mathematical result was retained.

## Syntax anatomy: inspect, plan, then calculate

Read `x.dtype.name` for a human-readable dtype name, `x.dtype.kind` for its category, and `x.itemsize` for bytes per element. The relevant kinds here are `i`, `u`, and `f`. We deliberately reject `b`, `c`, `O`, and text kinds from arithmetic contracts. Boolean values are useful masks but would obscure the meaning of a checked integer API; object arrays carry Python objects and a different computational model.

`np.result_type(a.dtype, b.dtype)` plans a common dtype from two explicit dtype objects. `a.astype(destination, copy=True)` performs a conversion and promises independent array storage. Planning does not inspect every integer for float representability. Similarly, a dtype-level safe-casting decision describes possible values of that dtype, not whether today's particular values happen to fit a narrower destination.

NumPy 2 preserves NumPy scalar precision while treating Python scalars differently in promotion. A Python float added to a float32 array need not widen the array, whereas an explicit NumPy float64 scalar can do so. Do not substitute a memorized rule from NumPy 1.x for an actual dtype observation. These examples make that difference visible.

## Worked example: move widening before addition

Predict the first element of each result before running this complete program. One expression calculates in the original narrow representation; the other changes representation before the potentially overflowing operation.

```python
import numpy as np

pixels = np.array([250, 10], dtype=np.uint8)
wrapped = pixels + np.uint8(10)
widened = pixels.astype(np.uint16) + np.uint16(10)
assert wrapped.tolist() == [4, 20]
assert widened.tolist() == [260, 20]
print("stored:", pixels.dtype, "wrapped:", wrapped.tolist(), "wide:", widened.tolist())
```

The first sum is mathematically 260. Uint8 has only 256 possible values, and the stored array result wraps to 4. The second expression promotes the operands explicitly to a dtype that contains 260, producing the expected value. Casting `wrapped` afterward would only widen the already incorrect 4. Source `pixels` remains unchanged because neither expression performs an in-place assignment.

Change the offset to a number outside uint8's range. Constructing that NumPy scalar may raise an error before addition, which is a different failure from a representable operand whose sum overflows. Record where the failure occurs. An exception policy and a result-validation policy must cover the operation actually performed.

## Worked example: promotion is not an exactness promise

This program contrasts Python scalar promotion with explicit NumPy scalar precision, then shows a collision between distinct integer identities after conversion.

```python
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
```

The first two arrays have equal numerical values for this fixture but different dtypes. The final assertion is more consequential: two distinct IDs collapse to one floating value. Equality of the converted arrays cannot establish equality of the original records. Keep identifiers as integers or strings in joins, caches and exported reports; a floating numerical feature matrix has a different purpose.

Change the integers to \(2^{53}+2\) and \(2^{53}+4\). Both remain exactly representable even though they exceed \(2^{53}\). A threshold-only representability test is too conservative, while a cast-and-forget approach is too permissive. The exactness-mask exercise must identify the actual represented values.

## Designing an honest overflow policy

There are several legitimate responses to an out-of-range result: reject it, widen storage, saturate at a boundary, use modular arithmetic, or switch to arbitrary precision. They serve different applications. Saturation may be intentional in image processing, while modular arithmetic can be intentional in a checksum. Neither is an acceptable accidental replacement for exact counts.

The checked functions in this unit use Python integers as a small, transparent oracle. Convert each NumPy scalar with `int(value)` before addition or accumulation. Python then computes the mathematical integer, and you compare it with exact destination bounds before constructing a fixed-width result. This sequence also handles mixed signed and unsigned arrays without routing their values through float64.

For `checked_integer_add`, inputs need not fit the output dtype individually. Large opposite operands can cancel into a small representable result. Checking operand ranges instead of result ranges would reject a legitimate case. Conversely, checking only the final sum of a whole vector cannot detect an overflowing individual element when the contract returns an elementwise vector.

Exact accumulation has a cost. A Python loop gives up NumPy's fast homogeneous arithmetic, which is acceptable for these bounded validation fixtures. Do not generalize its speed to millions of production records without measurement. Correctness and throughput require separate evidence, and a faster implementation must preserve the same boundaries.

## Six exercises

Implement the named functions in `python/professional/lessons/py_numpy_05.py`. Keep the full answers in the reference area until you have attempted the contracts. For each function, save one hand-predicted case and one changed-condition check alongside your result.

1. **Inspect storage before arithmetic: `numeric_schema`.** Return a dictionary with dtype (dtype.name), shape (tuple), itemsize (int), and bounds (inclusive Python integer min/max tuple for integer dtypes, otherwise None). Accept arrays of any shape with signed integer, unsigned integer, or real floating dtype. Inspection permits nonfinite floats. Reject bool, complex, object and string dtypes with ValueError; do not mutate the input.

   **Expected:** uint8 [1] reports uint8, (1,), 1 and (0, 255). An empty float32 vector reports shape (0,), itemsize 4 and bounds None.

2. **Make common-dtype conversion visible: `promote_pair`.** For equal-shaped finite real integer or floating arrays, return two independent copies converted to np.result_type(left.dtype, right.dtype). Reject unequal shapes, bool/complex/object/string dtypes and nonfinite values with ValueError. Preserve sources. This follows dtype promotion, without promising that every integer value remains exact.

   **Expected:** int64 [2**53 + 1] paired with uint64 [0] produces two float64 copies; the first integer is rounded. The same dtype on both sides still produces independent copies.

3. **Reject range loss before casting: `checked_integer_cast`.** Accept a one-dimensional signed or unsigned integer array and an integer destination dtype string. Return an independent array only if every mathematical input value fits the destination range. Empty inputs are valid. Reject noninteger source/destination dtypes, nonvector inputs and out-of-range values with ValueError. Do not accept float values merely because they look integral.

   **Expected:** [0, 255] casts to uint8; [-1] and [256] cannot. uint64 [2**64 - 1] cannot cast to int64. Empty int64 input becomes shape (0,) with the requested dtype.

4. **Compute then validate an exact integer sum: `checked_integer_add`.** Accept two equal-length one-dimensional integer arrays and an integer destination dtype string. Add each pair using Python integer arithmetic, then reject with ValueError if any result is outside the destination range. Inputs need not themselves fit that destination. Return a new destination-typed array; preserve empty inputs. Reject invalid shape or dtype with ValueError.

   **Expected:** [120] + [7] fits int8; [127] + [1] does not. [300] + [-300] fits uint8 as [0], despite the operands not fitting it.

5. **Accumulate beyond fixed-width limits: `exact_integer_sum`.** Return the exact Python int sum of a one-dimensional signed or unsigned integer array. Empty input returns the Python integer zero. Reject float, bool, complex, object and nonvector inputs with ValueError. Do not use fixed-width accumulation or convert through floating point.

   **Expected:** int64 [2**63 - 1, 1] returns 2**63. Two uint64 maximum values return 2 * (2**64 - 1), without wrapping or rounding.

6. **Audit representability without an unsafe round trip: `float64_exact_mask`.** For a one-dimensional signed or unsigned integer array, return a boolean vector indicating whether each value is exactly representable as float64. Compare through Python int and float, without casting a rounded float back into a fixed-width integer dtype. Empty input returns an empty boolean vector. Reject noninteger or nonvector input with ValueError.

   **Expected:** int64 [2**53, 2**53 + 1, 2**53 + 2, 2**63 - 1] yields [True, False, True, False]. uint64 [2**64 - 1] yields [False].

## Common pitfalls and diagnosis

If a small positive sum turns negative or unexpectedly small, inspect the operand dtype before changing the formula. If an ID comparison suddenly matches distinct records, inspect the conversion path and retain the original integers as evidence. If a range check near the uint64 maximum behaves strangely, determine whether a comparison converted one side to floating point. Print Python integer values for exact diagnosis, not rounded scientific notation.

These contracts apply to sensor counters, image buffers, inventory quantities, binary file fields and data interchange. A scientific measurement can tolerate an explicitly bounded approximation; a unique identifier usually cannot. State which domain you are serving before selecting a dtype.

Without looking at the code, explain why widening after addition is too late, why an integer above \(2^{53}\) can still be exact, and why uint64-to-int64 validation must reject the maximum uint64 value. Then propose a different application policy and name the tests that would change. Continue to the random-stream unit to see how representation and identity interact with simulation state.

## Self-check

Close the examples and answer in your own words before running a confirming case:

- Explain why casting a wrapped uint8 result to uint16 cannot recover the original mathematical sum. Where must the widening occur?
- Without a threshold shortcut, decide why `2**53 + 1` and `2**53 + 2` have different float64 exactness outcomes.
- Describe an exact comparison that rejects the maximum uint64 value as int64 without first converting it to float.
- Give a cancellation case in which operands do not fit the destination dtype but their elementwise sum does.

## Next step

Continue to [reproducible random streams](py_numpy_06.md) when you can defend exact integer identities and input ownership. Keep those contracts when a seed, task identifier or counter is stored in a fixed-width array.

## Official API references

Consult [NumPy's data-type promotion guide](https://numpy.org/doc/2.4/reference/arrays.promotion.html) and [the NumPy 2 migration guidance](https://numpy.org/doc/2.4/numpy_2_0_migration_guide.html) when checking scalar behavior. Use [integer machine limits](https://numpy.org/doc/2.4/reference/generated/numpy.iinfo.html) to inspect a specific destination.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-numpy-05: NumPy Dtypes, Promotion, and Overflow Contracts.
Read python/professional/companion-guides/py_numpy_05.md and python/professional/lessons/py_numpy_05.py. Direct prerequisites: python-16, python-numpy-01. Stay within that boundary and explain new vocabulary at a beginner-friendly pace.
Focus on dtype inspection, NumPy 2 scalar promotion, checked integer arithmetic, exact accumulation, float64 representability. Explain one mechanism, ask me to predict a concrete result, let me attempt it, provide one hint at a time, then review my numerical, shape, ownership or exception evidence. Ask retrieval questions that I answer in my own words. Do not read solutions/ until I ask or have made an honest attempt.
Use the Docker classroom's prepared Python Core environment with tiny offline fixtures. Preserve my saved work. This lesson requires no live SQL, database changes, downloads or external services; do not execute any live SQL as part of it.
Done when all six named contracts have inspected normal and boundary evidence and I can explain a changed-condition failure without copying the reference.
```
