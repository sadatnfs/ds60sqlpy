# eval-019: explained reference

`eval-019_reference.py` asserts each answer below, from *Add a reward constant* to *Test independent utility*, on the authored KL regularization and reference policy fixture only. Before applying a conclusion to other data, recheck the assumption that *Inspect the gradient sum* tests.

## 1. Add a reward constant

Only relative action rewards influence the finite-policy optimum under a fixed reference.

**Approach.** Compute `optimal_policy(q, r, 1)` and `optimal_policy(q, r + 100, 1)` with q = [0.25, 0.75] and r = [1, 0].

**Why it holds for this fixture.** The policy is softmax(log q + r / beta). Adding 100 to every reward adds 100 to every logit, and softmax is unchanged by a common shift. Both calls return the same distribution.

**A tempting wrong approach.** Expecting larger rewards to sharpen the policy is the mistake. Only differences between action rewards matter for which action gains probability.

**How to verify.** The reference asserts `np.testing.assert_allclose(optimal_policy(q, r, 1), optimal_policy(q, r + 100, 1))`.

**Expected observation:** The optimal distribution is unchanged.

## 2. Rescale reward and beta

The objective scale changes but the reward-to-regularization tradeoff does not.

**Approach.** Compare `optimal_policy(q, r, 1)` with `optimal_policy(q, 2 * r, 2)`.

**Why it holds for this fixture.** The policy uses r / beta, and (2r) / 2 = r. The tradeoff between reward and staying near the reference is unchanged, so the optimum is the same. The objective value itself doubles.

**A tempting wrong approach.** Doubling only the reward without adjusting beta would push the policy further from the reference. Reward scale and beta must be reported together.

**How to verify.** The reference asserts `np.testing.assert_allclose(optimal_policy(q, r, 1), optimal_policy(q, 2 * r, 2))`.

**Expected observation:** The optimal distribution is unchanged.

## 3. Inspect the gradient sum

This invariance checks the centered gradient through the probability parameterization.

**Approach.** Call `logit_gradient([0.2, 0.3], q, r, 1)` and sum its components.

**Why it holds for this fixture.** The gradient is p times (direction minus its p-weighted mean). Summing gives the p-weighted mean minus itself, which is 0. Adding the same amount to every logit leaves softmax unchanged, so the objective cannot change in that direction.

**A tempting wrong approach.** A nonzero sum would indicate a bug, most often a missing centering term. Testing only against finite differences at one point could miss it if the step size is large.

**How to verify.** The reference asserts `abs(logit_gradient([0.2, 0.3], q, r, 1).sum()) < 1e-12`. Case A also compares the gradient against central differences.

**Expected observation:** The sum is approximately zero.

## 4. Handle large rewards

The subtraction preserves normalized ratios while avoiding unnecessary overflow.

**Approach.** Call `optimal_policy([0.5, 0.5], [1000, 999], 1)`. The logits are log 0.5 + 1000 and log 0.5 + 999.

**Why it holds for this fixture.** `softmax` subtracts the maximum logit before exponentiating, so it computes exp(0) and exp(-1). The result is about [0.731, 0.269], the same as for rewards [1, 0].

**A tempting wrong approach.** Exponentiating 1000 directly overflows to infinity and the normalized result is `nan`. This is the same numerical concern as the stable loss in eval-017.

**How to verify.** The reference asserts `np.isfinite(optimal_policy([0.5, 0.5], [1000, 999], 1)).all()`.

**Expected observation:** Stable normalization returns finite probabilities.

## 5. Identify missing support

Adding a probability floor creates another reference distribution and must be treated as a modeling change.

**Approach.** Call `optimal_policy([0, 1], [1, 0], 1)`. `probability_vector` requires every reference probability to be strictly positive.

**Why it holds for this fixture.** log 0 is minus infinity, so the KL term is undefined for any policy that gives the action positive probability. The optimum forces it to zero probability no matter how good its reward. The helper rejects the input instead.

**A tempting wrong approach.** Replacing 0 with a small floor such as 1e-6 silently creates a different reference. That changes the objective and should be reported as a modeling choice.

**How to verify.** The reference raises `Unsupported action silently smoothed` if `optimal_policy([0, 1], [1, 0], 1)` returns without error.

**Expected observation:** The bounded helper rejects the unsupported objective.

## 6. Test independent utility

KL regularization can limit distribution change, but it cannot validate the reward model or rule out exploitation of a proxy.

**Approach.** Compute the case B policy with proxy rewards [1, 3], beta 0.2 and q = [0.5, 0.5]. Evaluate both proxy and utility under q and under the optimized policy.

**Why it holds for this fixture.** The logits differ by (3 - 1) / 0.2 = 10, so action 2 gets probability 1 / (1 + exp(-10)), about 0.99995. Proxy reward rises from 2 to nearly 3, while utility [1, -2] falls from -0.5 to nearly -2.

**A tempting wrong approach.** Treating the KL penalty as a safeguard against reward hacking is the mistake. With beta 0.2 it barely restrains the policy, and even a strong penalty cannot tell whether the proxy is right.

**How to verify.** Case B asserts the proxy rose, utility fell and `optimized[1] > 0.999`. An independent utility measure is required to detect this.

**Expected observation:** Proxy reward rises while independent task utility falls.
