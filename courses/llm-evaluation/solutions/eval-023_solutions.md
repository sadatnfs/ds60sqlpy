# eval-023: explained reference

`eval-023_reference.py` asserts each answer below, from *Shift all rewards* to *Declare algorithm variants*, on the authored GRPO and group baseline fixture only. Before applying a conclusion to other data, recheck the assumption that *Change length weighting* tests.

## 1. Shift all rewards

Relative normalization removes a common level; it does not preserve information about absolute task success.

**Approach.** Call `group_advantages` on `[0, 1, 2, 3]` and `[10, 11, 12, 13]`.

**Why it holds for this fixture.** The mean is 1.5 and the centered rewards are [-1.5, -0.5, 0.5, 1.5]. Their root mean square is the square root of 1.25, about 1.118, giving advantages about [-1.342, -0.447, 0.447, 1.342]. Adding 10 shifts the mean by 10 and leaves the centered values unchanged.

**A tempting wrong approach.** Reading normalized advantages as task success is the mistake. A group scoring 10 to 13 and one scoring 0 to 3 look identical after normalization.

**How to verify.** Case A asserts mean 0, mean square 1 and equality with both the shifted and the doubled group. The exercise checks assert that reversing the group negates the advantages.

**Expected observation:** The normalized advantages stay unchanged.

## 2. Inspect a constant group

These groups represent different absolute outcomes despite the same lack of within-group ranking signal.

**Approach.** Call `group_advantages([0, 0, 0])` and `group_advantages([1, 1])`.

**Why it holds for this fixture.** Centering gives all zeros and the scale is 0, so the helper returns zeros instead of dividing by zero. Both groups produce no learning signal even though one failed every attempt and the other succeeded every time.

**A tempting wrong approach.** Dividing by a small epsilon instead of handling zero scale returns zeros too, but adding epsilon to every scale changes the advantages of other groups slightly. Also, treating all-success and all-failure groups as equivalent in a report hides absolute performance.

**How to verify.** Case A asserts `group_advantages([0, 0, 0]).tolist() == [0.0, 0.0, 0.0]` and prints the constant group `[1, 1]`. Track the share of constant groups separately.

**Expected observation:** Both produce zero relative advantages under the declared rule.

## 3. Change length weighting

A token average weights longer responses more heavily and defines a different objective from equal-response weighting.

**Approach.** Take advantages -1 and +1 for responses of 2 and 4 tokens. Average per response and per token.

**Why it holds for this fixture.** The response average is (-1 + 1) / 2 = 0. The token average is (-1 times 2 + 1 times 4) / 6 = 2 / 6 = 1 / 3. The longer response has twice the influence under token averaging.

**A tempting wrong approach.** Treating the reduction as an implementation detail is the mistake. A token average rewards length when long responses carry positive advantage, so the two choices optimize different objectives.

**How to verify.** The reference asserts `response_mean == 0` and `np.isclose(token_mean, 1 / 3)`.

**Expected observation:** Response average 0; token average 1/3.

## 4. Check the sampling law

Importance correction can recover the value expectation with adequate support, but has variance costs and does not by itself prove a gradient estimator is correct.

**Approach.** With p = [0.8, 0.2] and q = [0.5, 0.5], compute `kl_terms(p, q)` and average it under p, under old = [0.5, 0.5], and under old with weights p / old.

**Why it holds for this fixture.** The ratios q / p are 0.625 and 2.5, giving terms about 0.095 and 0.584. Under p the average is about 0.193, the exact KL 0.8 log 1.6 + 0.2 log 0.4. Under old it is about 0.339, which is wrong. Reweighting by p / old recovers 0.193.

**A tempting wrong approach.** Averaging over samples drawn from the old policy without correction is the mistake. The estimator assumes samples from the current policy.

**How to verify.** Case B asserts all terms are nonnegative, `p @ terms` equals the exact KL, `old @ terms` does not, and the importance-weighted average does.

**Expected observation:** The value differs from current-policy KL.

## 5. Separate value from derivative

A zero average advantage or initial objective value does not imply absence of a learning signal.

**Approach.** Define the two-action surrogate 2 times sigmoid(delta) - 1 and evaluate its value and its central difference at delta 0.

**Why it holds for this fixture.** The value is 2 times 0.5 - 1 = 0. The derivative is 2 times sigmoid'(0) = 2 times 0.25 = 0.5. A zero value at the start does not mean a zero gradient.

**A tempting wrong approach.** Concluding that training is stuck because the initial objective or mean advantage is zero is the mistake. Normalized advantages always average zero, yet they still produce gradients.

**How to verify.** The reference asserts `surrogate(0) == 0` and that the central difference with h = 1e-5 is 0.5 within 1e-10.

**Expected observation:** Its value is 0 while its derivative is 0.5.

## 6. Declare algorithm variants

A shared acronym is insufficient to establish that two implementations optimize the same objective.

**Approach.** Record each implementation choice as part of the algorithm name or config: standard deviation correction, clip epsilon, KL estimator and token or response reduction.

**Why it holds for this fixture.** Exercises 1 to 4 show that these choices change the advantages, the weights and the KL estimate. Two runs called by the same acronym can optimize measurably different objectives.

**A tempting wrong approach.** Comparing results across papers or codebases because they share an algorithm name is the mistake. Differences may come from these unreported choices, not from the claimed contribution.

**How to verify.** No reference assertion covers this task. Diff the configuration of two runs before comparing results, and list every differing field in the comparison.

**Expected observation:** Record the change as part of the training algorithm.
