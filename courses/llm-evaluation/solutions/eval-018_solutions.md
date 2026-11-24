# eval-018: explained reference

`eval-018_reference.py` asserts each answer below, from *Verify the initial gradient* to *State the model boundary*, on the authored PyTorch reward model and pairwise training fixture only. Before applying a conclusion to other data, recheck the assumption that *Reverse a comparison* tests.

## 1. Verify the initial gradient

The check tests the implemented likelihood and reduction denominator independently of whether the labels are meaningful.

**Approach.** Set weights to zero, compute `binary_cross_entropy_with_logits(x @ weights, y)` for the two rows, call `backward`, and compare `weights.grad` with `x.T @ (0.5 - y) / n`.

**Why it holds for this fixture.** At zero weights every logit is 0 and every predicted probability is 0.5. With y = 1 for both rows and n = 2, the analytic gradient is [(0.5 - 1) / 2, (0.5 - 1) / 2, 0] = [-0.25, -0.25, 0]. Autograd must produce the same vector.

**A tempting wrong approach.** Forgetting the mean reduction gives [-0.5, -0.5, 0], twice the correct value. The check confirms both the likelihood and the denominator the framework uses.

**How to verify.** The reference uses `torch.testing.assert_close(weights.grad, x.T @ (torch.full_like(y, 0.5) - y) / len(y))` in float64.

**Expected observation:** The two vectors match in float64.

## 2. Inspect the length coefficient

The authored design provides no systematic signal that longer is preferable, so the symmetric initialization and updates preserve the zero length direction.

**Approach.** Train `fit_reward` on case A's design: rows [1, 0, 0] and [0, 1, 0] with label 1, and rows [0, 0, 1] and [0, 0, -1] with label 0.5. Inspect the third weight.

**Why it holds for this fixture.** The length rows appear in both directions with label 0.5, so their gradient contributions cancel at every step. Starting from zero, the length weight stays at 0 throughout training.

**A tempting wrong approach.** Expecting a small positive length weight because longer answers are often preferred is the mistake. The model learns only what this design supports, and this design is balanced on length.

**How to verify.** Case A asserts `abs(float(model.weight[0, 2].detach())) < 1e-12` and a held-out margin above 2 for the probe [1, 1, -3].

**Expected observation:** The length coefficient remains approximately zero.

## 3. Reverse a comparison

This is a useful implementation invariant for a pairwise difference model.

**Approach.** Evaluate the trained model on [1, 1, -3] and on its negation [-1, -1, 3].

**Why it holds for this fixture.** The model is linear with no bias, so f(-x) = -f(x). Reversing which response is first should flip the sign of the margin exactly, which this architecture guarantees.

**A tempting wrong approach.** Adding a bias term would break this invariant: the bias would then favor whichever response appears first. Order effects like that are a known problem in pairwise judges.

**How to verify.** The reference asserts `torch.testing.assert_close(forward, -reverse)` for these two probes.

**Expected observation:** The linear reward margin changes sign.

## 4. Find a training shortcut

An optimizer fits the provided associations. It cannot infer the intended target when the comparison design leaves that target confounded.

**Approach.** Train on case B's rows [1, 0, 3] and [0, 1, 3], both labeled 1, and compare the learned weights.

**Why it holds for this fixture.** Every preferred response is also 3 units longer, so length explains the labels as well as evidence does. Because the length feature has a larger value, gradient descent puts more weight on it, and the held-out probe with a shorter but better answer gets a negative margin.

**A tempting wrong approach.** Concluding the model learned to value evidence because training loss fell is the mistake. Loss fell in both designs; only the held-out probe reveals which feature carries the decision.

**How to verify.** Case B asserts `final < initial`, a negative probe margin, and that the length weight exceeds the first evidence weight.

**Expected observation:** Length receives more weight than either evidence coordinate.

## 5. Recompute the final loss

A reported result should identify the model state that produced it, especially when comparing training and held-out measurements.

**Approach.** Compute the objective once more after the final optimizer step, as `fit_reward` does when it returns `final`.

**Why it holds for this fixture.** The `loss` variable inside the loop was computed before the last `optimizer.step()`, so it describes the second-to-last parameter state. The returned `final` matches the weights the model actually holds.

**A tempting wrong approach.** Reporting the last in-loop loss as the training loss of the returned model is the mistake. The difference is small after many steps but can mislead when comparing to a held-out loss computed on the final weights.

**How to verify.** The reference asserts `final < initial` for the balanced design. Print both the last in-loop loss and `final` to see they differ.

**Expected observation:** The final-state loss is distinct from the last pre-update loss.

## 6. State the model boundary

The exercise uses authored features. It does not train a language encoder, judge real responses or establish the preferences of an external population.

**Approach.** Describe the model as a three-weight linear logistic reward fit on authored feature differences, trained on CPU in float64.

**Why it holds for this fixture.** The three features are hand-written numbers standing for evidence and length. No text is encoded, no real response is judged, and no annotator population supplied the labels.

**A tempting wrong approach.** Calling it a reward model for language responses overstates it. The lesson demonstrates the training mechanics and the shortcut risk, not capability on real text.

**How to verify.** The reference asserts every parameter is on the `cpu` device. A claim in a write-up should mention the feature definitions and the four or two training rows.

**Expected observation:** A real small CPU reward fit, with no natural-language capability claim.
