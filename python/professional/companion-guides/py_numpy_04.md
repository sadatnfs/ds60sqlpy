# Stable Numerical Computation and Honest Error Bounds

**Stable ID:** `python-numpy-04`

**Estimated time:** 150 minutes; split the reading and implementation across sessions when useful.

## Level and prerequisites

Intermediate. Direct catalog prerequisites: `python-numpy-03`. This lesson deepens the named mechanism after the introductory track; it does not require a cloud account or download data.

## Learning objectives

By the end, explain the mechanism in your own words, implement each bounded contract, and use a counterexample to distinguish a correct result from a plausible mistake. The six exercises progress from inspection to transformation, edge handling and transfer.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional contributor route:** use the prepared environment in
[CONTRIBUTING](../../../CONTRIBUTING.md) on Linux, macOS or Windows through
WSL 2. The commands below assume its packages are already installed. They are
not prerequisites for opening this lesson in the Docker classroom. Local
`.learning/` files and CLI progress belong to this checkout; they do not read or
update the Docker classroom's named learning volume.

Open the [learner script](../lessons/py_numpy_04.py) in the prepared repository environment. In the Docker classroom, edit the saved learner pad; drafts, notes and results persist in the classroom learning volume. An ignored `.learning/` copy is a separate optional contributor workspace. Run from the repository root. The provided worked examples execute immediately; task functions intentionally raise `NotImplementedError` until you implement them. A successful example is not evidence that the six tasks are finished.

Prepared POSIX/WSL contributor terminal:

```sh
uv run --no-sync python python/professional/lessons/py_numpy_04.py
```

Dependencies: NumPy. All fixtures are tiny and local. The terminal prints the worked results and stops without editing your files. Keep [explanatory solutions](../solutions/py_numpy_04_solutions.md) and [runnable reference](../solutions/py_numpy_04_solution.py) closed until an attempt or an explicit worked comparison.

## Vocabulary and mental model

- **Floating-point precision:** The finite number of significant binary digits retained in a numerical representation, distinct from the magnitude range it can express.

- **Cancellation:** Loss of relative accuracy when subtracting nearly equal approximate quantities.

- **Conditioning:** Sensitivity of the exact problem solution to small changes in its inputs, distinct from errors introduced by the algorithm.

- **Tolerance:** An explicit absolute or relative error allowance chosen for a comparison, not proof of mathematical equality.

Scientific programs represent most real values approximately. An algorithm can be mathematically correct and still lose useful digits through cancellation, overflow or an inappropriate data type. Numerical stability asks whether the computation adds avoidable error. Conditioning asks whether the underlying problem itself is sensitive. A stable solver cannot recover a well-determined answer from nearly indistinguishable input columns without additional assumptions.

Exponentials illustrate avoidable overflow. A softmax divides \(e^{x_i}\) by the sum of all exponentials. Adding the same constant to every score leaves the probabilities unchanged, so subtract the maximum before exponentiating. The largest exponent becomes zero and all others are nonpositive. The log-sum-exp identity similarly writes \(\log\sum_i e^{x_i}\) as \(m+\log\sum_i e^{x_i-m}\). The transformation preserves the mathematical result while avoiding huge intermediate exponentials.

Summation order matters because floating addition is not associative. For values 1e16, one and -1e16, an ordinary sequential or array sum can lose the one. math.fsum tracks partial sums to recover more accurate results for this example. It is not arbitrary-precision arithmetic and cannot represent a final result outside the floating range. Explicitly distinguish a recoverable rounding problem from a genuinely unrepresentable answer.

Integer arrays have their own range limits. Multiplying int64 values before converting to float can overflow in integer arithmetic. Converting operands first avoids that specific failure, but float conversion may lose exact low bits for very large integers. Exact accounting and identity calculations should retain exact integer or decimal contracts instead of assuming scientific floating operations are interchangeable.

Solving A*x=b should use a solver rather than explicitly forming inverse(A). Inspect the condition number and the residual norm. A tiny residual shows that the computed result approximately solves the supplied system; it does not prove the solution is insensitive to measurement error. A nearly singular system can have a tiny residual and wildly unstable coefficients.

Finally, choose comparison tolerances from units and scale. Absolute tolerance controls behavior near zero, while relative tolerance scales with a reference magnitude. Comparing arrays with mismatched shapes through broadcasting can accidentally validate unrelated outputs, so the exercise's comparison contract requires identical shapes. A tolerance should explain which differences are operationally negligible, not be enlarged until a failing computation passes.

## Worked examples and syntax anatomy

### Example 1

```python
scores = np.array([1000.0, 1001.0, 999.0])
shifted = scores - scores.max()
probability = np.exp(shifted) / np.exp(shifted).sum()
assert np.isfinite(probability).all() and np.isclose(probability.sum(), 1)
assert probability.argmax() == 1
print("Stable probabilities:", probability.tolist())
```

The raw exponentials would overflow at these scores, while subtracting 1001 changes neither their relative ratios nor the resulting probabilities. The maximum-score class remains the most probable. Checking finite values, normalization and ordering gives three independent observations about the transformation.

### Example 2

```python
values = [1e16, 1.0, -1e16]
ordinary = float(np.sum(values))
accurate = math.fsum(values)
assert accurate == 1.0 and ordinary == 0.0
a = np.array([[2.0, 0.0], [0.0, 4.0]])
b = np.array([6.0, 8.0])
x = np.linalg.solve(a, b)
assert np.allclose(x, [3.0, 2.0]) and np.allclose(a @ x, b)
print("Summation:", ordinary, accurate, "linear solution:", x.tolist())
```

The summation counterexample exposes lost low-order information. The diagonal system then makes a solver result independently inspectable: two times three is six and four times two is eight. A library success flag is weaker evidence than both the expected solution and a checked residual on a known fixture.

## Exercises

1. **Aggregate log weights without overflow.** Implement stable \(\log\sum_i e^{\mathrm{values}_i}\) for a one-dimensional array. Allow finite values and negative infinity; reject NaN or positive infinity. Define the empty input and an all-negative-infinity input as negative infinity.

**Expected:** [1000,1000] yields \(1000+\log2\) without infinity; [-inf,-inf] and empty return-inf. [NaN] and [inf] raise ValueError.

2. **Normalize large scores.** Return softmax probabilities for a nonempty finite vector using a maximum shift. Preserve the source and reject NaN, infinity, empty or nonvector inputs. Test invariance when a constant is added to every score.

**Expected:** [1000,1001] returns finite probabilities summing to one with the second larger. Adding-1000 produces the same probabilities; equal scores give [.5,.5].

3. **Preserve small contributions.** Sum a finite one-dimensional array using math.fsum after conversion to Python floats. Return zero for empty input. Reject nonfinite inputs or a final overflow with ValueError. Demonstrate a cancellation case rather than only positive small integers.

**Expected:** [1e16,1,-1e16] returns 1; empty returns 0; [inf] and [1e308,1e308] raise ValueError.

4. **Promote before multiplying.** Compute a floating dot product of equal-length finite vectors, converting operands before multiplication. Reject shape mismatch or an unrepresentable nonfinite result. Empty equal vectors return zero. This contract is approximate floating arithmetic, not exact integer accounting.

**Expected:** int64[2**62] dotted with int64[4] yields float(2**64), not integer overflow zero. Length mismatch raises ValueError, and empty vectors return 0.

5. **Separate solver residual from conditioning.** Solve a nonempty finite square system with a matching finite target vector. Require a finite condition limit of at least one and reject systems whose condition number exceeds it. Use np.linalg.solve, not an explicit inverse.

**Expected:** diag(2,4) with [6,8] returns [3,2] and a zero residual within tolerance. A duplicate-row system and diag(1,1e-12) at default limit raise ValueError.

6. **Make numerical comparison semantics explicit.** Compare finite arrays with exactly equal shapes using abs(actual-expected)<=atol+rtol*abs(expected) elementwise. Require finite nonnegative tolerances. Reject broadcasting-compatible but unequal shapes and nonfinite values. Empty equal arrays return True.

**Expected:** Actual[1e8+1,1e-9] versus expected[1e8,0] passes with atol 1 e-8, rtol 1 e-7; it fails with zero tolerances. Shapes(2,) and (1,2) raise ValueError.

## Common mistakes and diagnosis

If exp produces infinity, inspect the largest score and reformulate with a maximum shift instead of clipping arbitrarily. If a sum changes when values are reordered, use a cancellation fixture and compare with math.fsum before selecting a tolerance. If an integer product wraps, inspect dtype before multiplication, not after the incorrect result exists. If a solver returns huge coefficients with a tiny residual, inspect the condition number and input uncertainty. If an allclose assertion passes for the wrong output shape, add a shape assertion rather than merely tightening tolerances.

## Self-check and retrieval

Without copying code, explain which input property each function assumes, which observable result proves the normal case, and which counterexample would expose an incorrect implementation. Trace one boundary input by hand before running it. Keep the input and expected output beside your saved result so a reviewer can reproduce the evidence.

## Next steps

Use these mechanisms in the next deepening lesson or return to the original prerequisite examples and explain precisely which new failure cases you can now diagnose. Review the [professional track](../README.md) for related modules.

## Primary sources and official APIs

- [NumPy numerical data types and overflow](https://numpy.org/doc/stable/user/basics.types.html).

- [Python math.fsum](https://docs.python.org/3/library/math.html#math.fsum).

- [NumPy linear solve](https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-numpy-04: Stable Numerical Computation and Honest Error Bounds.
Read python/professional/companion-guides/py_numpy_04.md and python/professional/lessons/py_numpy_04.py. Direct prerequisites: python-numpy-03.
Explain the vocabulary and mechanism at a beginner-friendly pace, then ask me to predict a concrete result before my attempt. Give one hint at a time, review my numerical or exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt. Use only the prepared local Python environment and tiny offline inputs; preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why a tempting incorrect implementation fails.
```
