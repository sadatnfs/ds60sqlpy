# eval-020: explained reference

`eval-020_reference.py` asserts each answer below, from *Evaluate the reference* to *Bound the claim*, on the authored DPO and reference log probability fixture only. Before applying a conclusion to other data, recheck the assumption that *Compare beta optima* tests.

## 1. Evaluate the reference

The initial classifier is indifferent under the pairwise parameterization.

**Approach.** Call `dpo_loss(3, 3, 0.1)`. The policy and reference log-odds shifts are equal, so z = beta times (3 - 3) = 0.

**Why it holds for this fixture.** With z = 0 the loss is `logaddexp(0, 0)` = log 2. At initialization, when the policy equals the reference, every preference pair costs log 2 regardless of beta.

**A tempting wrong approach.** Expecting the initial loss to depend on beta is the mistake. Beta scales the margin, and a zero margin scaled by anything is still zero.

**How to verify.** The reference asserts `np.isclose(dpo_loss(3, 3, 0.1), np.log(2))`, and case A asserts the same for beta 2.

**Expected observation:** The loss for a positive preference is log 2.

## 2. Differentiate the two-action loss

The result includes the beta scale and the logistic residual; it should agree with finite differences.

**Approach.** Call `dpo_gradient(0, 0, 2)`. The formula is beta times (sigmoid(z) - win_fraction).

**Why it holds for this fixture.** With z = 0 the sigmoid is 0.5 and the win fraction is 1, so the derivative is 2 times (0.5 - 1) = -1. Case A confirms this at delta 0.4 against a central finite difference.

**A tempting wrong approach.** Dropping the beta factor gives -0.5. That is the gradient with respect to z, not delta, and it would understate the step size by a factor of beta.

**How to verify.** Case A asserts `dpo_gradient(0, 0, 2) == -1` and `np.isclose(numeric, dpo_gradient(delta, 0, 2), atol=1e-10)`.

**Expected observation:** The derivative is -1.

## 3. Compare beta optima

Initial gradient magnitude and final optimum displacement are different properties of the objective.

**Approach.** Call `fitted_delta(3, 1, beta)` for beta 0.5, 1 and 2, then take the sigmoid of each.

**Why it holds for this fixture.** The optimum is delta = log(3) / beta. For beta 0.5, delta = log 9 and the sigmoid is 9 / 10 = 0.9. For beta 1, it is 0.75. For beta 2, delta = log of the square root of 3 and the probability is about 0.634. At each optimum, beta times delta equals log 3, so the gradient is zero.

**A tempting wrong approach.** Assuming a larger beta moves the policy further because its initial gradient is larger is the mistake. Larger beta gives larger first steps but a smaller final change from the reference.

**How to verify.** Case B asserts probabilities `[0.9, 0.75, np.sqrt(3) / (1 + np.sqrt(3))]` and gradients below 1e-12 at each optimum.

**Expected observation:** Preferred-action probabilities are 0.9,0.75 and approximately 0.634.

## 4. Change length normalization

Normalizing each sequence by its own length changes its relative contribution and therefore the objective.

**Approach.** Compute per-token log-ratios: chosen is [0.3, 0.3] (two tokens) and rejected is [0.2, 0.2, 0.2, 0.2] (four tokens). Compare sums and means.

**Why it holds for this fixture.** The chosen sum is 0.6 and the rejected sum is 0.8, a margin of -0.2. The chosen mean is 0.3 and the rejected mean is 0.2, a margin of +0.1. The longer rejected response wins on sums because it has more tokens.

**A tempting wrong approach.** Assuming normalization is a minor detail is the mistake. Summing favors longer sequences, averaging removes that effect, and each defines a different objective.

**How to verify.** The reference asserts `chosen.sum() - rejected.sum() < 0` and `chosen.mean() - rejected.mean() > 0`.

**Expected observation:** The sequence-sum margin is negative while the mean-token margin is positive.

## 5. Protect the reference

Reference refresh can be a deliberate algorithmic choice, but it is not the same fixed-reference DPO problem.

**Approach.** Keep the reference model frozen for the whole run. If it is updated, record that as a different algorithm.

**Why it holds for this fixture.** The DPO loss measures the policy relative to the reference. If the reference moves, the same loss value refers to a different comparison point, and the fixed-reference optimum from exercise 3 no longer applies.

**A tempting wrong approach.** Letting the reference share parameters with the policy, for example by not copying it, is a common bug. The loss then goes to log 2 every step and training appears stuck.

**How to verify.** No reference assertion covers this task. Hash the reference parameters before and after training and confirm they are identical.

**Expected observation:** The objective has changed.

## 6. Bound the claim

Task utility, robustness, calibration and critical constraints still need their own held-out evaluation.

**Approach.** State that a lower training DPO loss shows the policy fits the training preference pairs better under the declared beta and reference.

**Why it holds for this fixture.** The loss rewards matching the labeled preferences. It does not measure whether answers are correct, robust to new prompts, calibrated or free of critical errors.

**A tempting wrong approach.** Reporting the lower loss as an improved model is the mistake. Eval-019 shows a policy can raise a proxy while lowering true utility.

**How to verify.** Pair the training loss with held-out preference accuracy and an independent task metric, as in the decision gates of eval-016.

**Expected observation:** Conclude improved fit to the declared preference objective only.
