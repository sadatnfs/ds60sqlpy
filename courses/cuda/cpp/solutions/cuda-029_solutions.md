# cuda-029: explanatory solutions

## Mechanism review

A mathematically equivalent expression can have different floating-point behavior. Fused multiply-add rounds a product-plus-sum once instead of rounding the product and then the addition. Fast-math modes can change precision and special-value behavior, so they require an explicit error budget. Variance computed as mean of squares minus square of mean subtracts nearby large values and can lose a small real variance. A centered or carefully merged online algorithm reduces that risk. Conditioning describes sensitivity of the problem itself; algorithmic stability describes how well the chosen computation handles it. Neither is fixed merely by changing processors.

## Exercise 1

For \([100000001,100000002,100000003]\), center around the mean 100000002. Squared deviations are \([1,0,1]\), giving population variance \(\frac{2}{3}\). Computing two roughly \(10^{16}\) quantities and subtracting them risks losing that small answer in ordinary floating precision.

**Approach:** Subtract the mean 100000002 from each value before squaring, giving deviations -1, 0 and 1.

**Why it is correct:** Centered squares are [1, 0, 1], small numbers whose average 2 / 3 is computed exactly enough.

**A plausible wrong approach:** Using E[x^2] minus E[x]^2 subtracts two numbers near 1e16 and loses the small difference in rounding.

**How to verify:** The reference asserts variance == 2 / 3 using math.fsum with the centered formula.

## Exercise 2

A dot product with very large and very small terms can differ under different association or FMA choices. Compare to a higher-precision reference and report absolute error, relative error when meaningful, and nonfinite values. Exact equality is appropriate only when the contract and arithmetic justify it.

**Approach:** Compare the dot product with a higher-precision reference and report absolute and relative error.

**Why it is correct:** FMA and reassociation change rounding, so two valid results can differ in low bits.

**A plausible wrong approach:** Demanding bitwise equality with a CPU loop rejects valid optimized results and passes nothing new.

**How to verify:** Check every output is finite and the error is within a declared tolerance.

## Exercise 3

Zero. A normalization later still needs a deliberate epsilon or constant-row policy.

**Approach:** Center each value of [2, 2, 2] at mean 2 and average the squares.

**Why it is correct:** Every deviation is zero, so the variance is zero.

**A plausible wrong approach:** Dividing by the standard deviation next without a policy gives division by zero.

**How to verify:** The reference asserts math.fsum of squared deviations from 2 equals 0.

## Exercise 4

A predeclared tolerance derived from the application, input range and reference method, plus finite-output and adversarial checks.

**Approach:** Decide with a tolerance set in advance from the application and input range.

**Why it is correct:** Fast-math changes rounding and may flush subnormals, which matters most near zero.

**A plausible wrong approach:** Accepting any new value because the mode is faster leaves the error unbounded.

**How to verify:** Run adversarial inputs and confirm results stay finite and within tolerance.

## Exercise 5

Dividing by a tiny reference magnifies small absolute differences; retain an absolute error criterion.

**Approach:** Keep an absolute error bound alongside relative error.

**Why it is correct:** Relative error divides by the reference, and a tiny reference magnifies any small difference.

**A plausible wrong approach:** Reporting only relative error marks near-zero outputs as wildly wrong.

**How to verify:** Compute both errors for a reference of 1e-12 and see which is meaningful.

## Exercise 6

State accumulation precision, association/reproducibility expectations and uncertainty. Preserve raw data and avoid silently changing numerical modes between benchmark baselines.

**Approach:** State accumulation precision, association policy, reproducibility expectation and uncertainty.

**Why it is correct:** Readers can only trust a reported sum if they know how it was formed.

**A plausible wrong approach:** Switching to fast-math between baseline and candidate benchmarks mixes numerical and speed changes.

**How to verify:** Rerun with the stated policy and confirm the result matches within the uncertainty.

## Self-check answers

1. **Why does centering around the mean help in worked example 1?** It subtracts close values first, keeping deviations small, so no huge nearly equal quantities are subtracted.
2. **What does FMA change compared with a separate multiply and add?** It rounds once instead of twice, which usually improves accuracy but changes bit patterns.
3. **When is exact equality an appropriate test for floating point?** Only when the algorithm and order are fixed and the result is known to be exactly representable.

## Numerical reference and its limits

The [CPU reference](../references/cuda-029_cpu.py) reproduces worked example 1 and prints `{'mean': 100000002.0, 'centered_population_variance': 0.6666666666666666}`.

## Transfer review

State accumulation precision, association/reproducibility expectations and uncertainty. Preserve raw data and avoid silently changing numerical modes between benchmark baselines.
