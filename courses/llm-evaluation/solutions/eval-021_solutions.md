# eval-021: explained reference

`eval-021_reference.py` asserts each answer below, from *Remove the trace* to *Freeze rollout quantities*, on the authored GAE and termination fixture only. Before applying a conclusion to other data, recheck the assumption that *Positive advantage outside the interval* tests.

## 1. Remove the trace

This isolates the one-step residual calculation and its terminal mask.

**Approach.** Call `gae([1, 2], [0.5, 0.4, 0.2], [False, True], lam=0)`. With lambda 0 the carried term is multiplied by zero, so each advantage is its one-step residual.

**Why it holds for this fixture.** Step 1 is terminal, so its residual is 2 + 0 - 0.4 = 1.6. Step 0 is not terminal, so its residual is 1 + 0.9 times 0.4 - 0.5 = 0.86. With lambda 0.8, step 0 instead becomes 0.86 + 0.72 times 1.6 = 2.012, as in case A.

**A tempting wrong approach.** Forgetting the terminal mask on step 1 would add 0.9 times 0.2 and give 1.78, the truncated case. The value after a true terminal state must not be bootstrapped.

**How to verify.** The reference asserts `[0.86, 1.6]` for lambda 0. Case A asserts `[2.012, 1.6]` for terminal and `[2.1416, 1.78]` for truncated.

**Expected observation:** Advantages reduce to residuals 0.86 and 1.6.

## 2. Terminate the first step

The array illustrates boundary behavior; separate episodes should otherwise be processed with explicit episode structure.

**Approach.** Call `gae([1, 2], [0.5, 0.4, 0.2], [True, True])`. Both steps are now terminal.

**Why it holds for this fixture.** Step 0's residual drops the bootstrap term, giving 1 - 0.5 = 0.5, and the terminal flag also zeroes the carry from step 1. Step 1 is unchanged at 1.6. The result is `[0.5, 1.6]`.

**A tempting wrong approach.** Treating the array as one continuous rollout and letting step 0 inherit step 1's advantage mixes two episodes. Rewards after an episode ends must not be credited to earlier actions.

**How to verify.** The reference asserts `np.testing.assert_allclose(gae([1, 2], [0.5, 0.4, 0.2], [True, True]), [0.5, 1.6])`.

**Expected observation:** The first result is 0.5 and does not inherit the second residual.

## 3. Positive advantage outside the interval

The surrogate stops rewarding that favorable increase beyond the upper boundary.

**Approach.** Call `clipped_terms([1.5], [1], epsilon=0.2)`. Compare the unclipped term 1.5 times 1 with the clipped term 1.2 times 1 and take the minimum.

**Why it holds for this fixture.** The minimum is 1.2. Once the ratio passes 1 + epsilon, the clipped term is constant, so its gradient with respect to the policy is zero. The objective stops rewarding further increase of an already favored action.

**A tempting wrong approach.** Expecting 1.5 because the ratio was observed is the mistake. Clipping exists to remove the incentive for large steps that the old samples cannot justify.

**How to verify.** Case B asserts the first term of `clipped_terms([1.5, 0.5, 0.5, 1.5], [1, 1, -1, -1])` is 1.2. Also check that ratio 1 with advantages 2 and -2 returns them unchanged.

**Expected observation:** The clipped term is 1.2.

## 4. Negative advantage outside the interval

The bad-direction probability increase still receives its larger penalty.

**Approach.** Call `clipped_terms([1.5], [-1])`. The unclipped term is -1.5 and the clipped term is -1.2.

**Why it holds for this fixture.** The minimum of -1.5 and -1.2 is -1.5, so the unclipped term is used. An action with negative advantage that became more likely keeps its full penalty and full gradient, pushing the policy back.

**A tempting wrong approach.** Assuming clipping is symmetric and always caps the term at the boundary gives -1.2. The minimum is pessimistic: it caps gains but not losses.

**How to verify.** Case B asserts the last term is -1.5. The third term, ratio 0.5 with advantage -1, is -0.8 because the clipped value is the smaller one there.

**Expected observation:** The term is -1.5, not-1.2.

## 5. Check an unobserved action

Clipping a finite sampled objective cannot by itself bound every unobserved action probability or full-distribution divergence.

**Approach.** Compare `p = [0.6, 0.39, 0.01]` and `other = [0.6, 0.01, 0.39]` against `old = [0.5, 0.49, 0.01]`. Only action 0 was sampled.

**Why it holds for this fixture.** Both policies give action 0 ratio 1.2, so the sampled clipped terms match. Their full KL from old differs a lot: about 0.02 for p and about 1.5 for other, because other moved 0.38 probability onto an action old almost never took.

**A tempting wrong approach.** Believing clipping bounds the overall policy change is the mistake. It constrains only the sampled actions' terms; unobserved actions can shift freely.

**How to verify.** Case B asserts the two sampled terms are equal and `kl(other, old) > kl(p, old)`. Monitor full KL separately if it is computable.

**Expected observation:** Their sampled terms agree while global KL differs.

## 6. Freeze rollout quantities

Gradients through old probabilities or an unintended baseline optimize another objective and can destroy the interpretation of the ratio estimator.

**Approach.** Store old log probabilities and advantages as constants when the rollout is collected, and compute the ratio from current log probabilities against those stored values.

**Why it holds for this fixture.** The ratio's denominator represents the policy that generated the data. If gradients flow into it, the update changes the denominator too, and the ratio no longer estimates the change from the sampling policy.

**A tempting wrong approach.** Recomputing old probabilities from the live model each inner step, or leaving advantages attached to the critic graph, is the usual bug. The loss then optimizes a different objective, and the actor can lower loss by moving the baseline.

**How to verify.** No reference assertion covers this task. In PyTorch, assert `old.requires_grad` and `advantage.requires_grad` are both false, as eval-022's `fit_policy` does.

**Expected observation:** Stored old log probabilities and computed advantages are fixed.
