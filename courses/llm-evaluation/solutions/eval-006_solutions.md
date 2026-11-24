# eval-006: explained reference

`eval-006_reference.py` asserts each answer below, from *All differences vanish* to *Bound an exact algorithm*, on the authored paired comparison and permutation test fixture only. Before applying a conclusion to other data, recheck the assumption that *Reverse model labels* tests.

## 1. All differences vanish

There is no observed contrast. All sign assignments are at least as extreme under the non-strict tail convention.

**Approach.** Call `sign_test([0, 0])`. The observed statistic is the absolute mean, 0, and the function enumerates all four sign assignments.

**Why it holds for this fixture.** Every flipped mean is 0, and the tail compares `np.abs(null) >= observed - 1e-12`. Since 0 >= 0 holds for all four, the p-value is 4 / 4 = 1. With no contrast at all, the data give no evidence against the null.

**A tempting wrong approach.** Using a strict `>` comparison would count no assignments and return p = 0, which reads as overwhelming evidence of a difference that does not exist. The tolerance and non-strict inequality are deliberate.

**How to verify.** The reference asserts `sign_test([0, 0])[0] == 1`. Print the null array and confirm it is four zeros.

**Expected observation:** The exact tail probability is 1.

## 2. Four favorable pairs

Even four uniformly favorable pairs cannot attain a two-sided 0.05 threshold under this small sign space.

**Approach.** Call `sign_test([1, 1, 1, 1])`. The function enumerates 2 to the power 4 = 16 sign assignments and compares the absolute mean of each with the observed absolute mean, 1.

**Why it holds for this fixture.** Only all positive and all negative signs give an absolute mean of 1, so the tail count is 2 and p = 2 / 16 = 0.125. With four pairs, this is the smallest two-sided p-value the test can produce.

**A tempting wrong approach.** Concluding that the test is broken because four wins out of four seems decisive is the mistake. The exact reference distribution has only 16 outcomes, so no result with four pairs can reach 0.05. More pairs, not a different threshold, are needed.

**How to verify.** The reference asserts `sign_test([1, 1, 1, 1])[0] == 0.125`. Worked case A, with one negative pair among four, gives 10 / 16 = 0.625 by the same enumeration.

**Expected observation:** The two-sided exact tail is 2/16=0.125.

## 3. Reverse model labels

A two-sided sign-reference test does not favor a naming convention; a one-sided analysis would require a prespecified direction.

**Approach.** Negate every value in case A, giving `[-1, -1, -1, 1]`, and call `sign_test` again. The observed statistic is the absolute mean, which is unchanged at 0.5.

**Why it holds for this fixture.** The null set of sign flips is symmetric: negating every difference just relabels which assignment is which. Both the observed value and the reference distribution are therefore identical, so the two-sided p-value remains 0.625.

**A tempting wrong approach.** Running a one-sided test after looking at which model won and choosing the matching direction would halve the p-value. That direction must be fixed before seeing the data, otherwise the error rate is not the stated one.

**How to verify.** Worked case A asserts `sign_test([-1, -1, -1, 1])[0] == p` where p is 0.625 from the original order.

**Expected observation:** The two-sided p-value is unchanged.

## 4. State the quantile convention

Both calculations use the same four resamples. Different interpolation rules do not constitute additional evidence.

**Approach.** Compute `np.quantile(distribution, [0.025, 0.975])` with the default method and again with `method="inverted_cdf"` on the case B distribution `[-1, 0, 0, 1]`.

**Why it holds for this fixture.** Linear interpolation places the 2.5 percent point between -1 and 0, at -0.925, and symmetrically +0.925. The inverse CDF returns the smallest observed value whose cumulative share reaches the level, so it returns -1 and +1. Both read the same four resamples.

**A tempting wrong approach.** Reporting whichever interval looks tighter as the better result is the mistake. The narrower interval adds no information; it only reflects an interpolation rule, and with four resamples the choice dominates the answer.

**How to verify.** Worked case B checks `np.testing.assert_allclose(..., [-0.925, 0.925])` for the linear rule and `[-1.0, 1.0]` for `inverted_cdf`. Name the method in any reported interval.

**Expected observation:** Linear endpoints are approximately +/-0.925; inverse-CDF endpoints are +/-1.

## 5. Add a third family

The calculation expands to 3 cubed assignments, while the original independent sample still has only three families.

**Approach.** Call `cluster_bootstrap([0, 1, 2])`. The function enumerates every ordered draw with replacement of three family indices using `product(range(3), repeat=3)`.

**Why it holds for this fixture.** Three positions with three choices each give 3 cubed = 27 resamples. The list grows quickly, but the evidence does not: the sample still has three independent families, and every resample is built from those same three means.

**A tempting wrong approach.** Treating 27 resamples as 27 observations and computing a standard error from them as if n were 27 would make uncertainty look much smaller. The bootstrap distribution approximates sampling variation of the three-family mean; it does not create new families.

**How to verify.** The reference asserts `len(cluster_bootstrap([0, 1, 2])) == 27`. Its mean is 1, the original sample mean, as expected for an exhaustive bootstrap.

**Expected observation:** There are 27 ordered draws of three families.

## 6. Bound an exact algorithm

A bounded classroom example should not silently allocate an enormous sign space. A larger analysis needs a declared Monte Carlo or analytical method.

**Approach.** Call `sign_test([1] * 17)`. The guard `1 <= len(d) <= 16` raises `Bounded finite pairs required` before enumeration starts.

**Why it holds for this fixture.** Seventeen pairs would require 2 to the power 17 = 131072 sign assignments, each stored in the null array. The classroom fixture caps the exact method at 16 pairs (65536 assignments) so a learner run stays fast and predictable.

**A tempting wrong approach.** Silently switching to random sampling of signs would change the method from exact to Monte Carlo without telling anyone, and the reported p-value would then carry simulation error that was never stated.

**How to verify.** The reference includes `[1] * 17`, an empty list and `[float("nan")]` in its invalid list and fails if any is accepted. A real analysis with more pairs should declare a Monte Carlo size or a normal approximation.

**Expected observation:** The fixture rejects the request.
