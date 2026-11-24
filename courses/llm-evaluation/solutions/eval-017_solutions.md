# eval-017: explained reference

`eval-017_reference.py` asserts each answer below, from *Equal scores* to *Interpret a preference cycle*, on the authored Bradley-Terry and pairwise likelihood fixture only. Before applying a conclusion to other data, recheck the assumption that *Reverse empirical counts* tests.

## 1. Equal scores

Equal scores express no preference under the model; observing a chosen response still incurs positive negative log likelihood.

**Approach.** Call `pair_loss([0, 0])`. The score difference is 0, so the loss is `logaddexp(0, 0)`, which is log(1 + 1) = log 2.

**Why it holds for this fixture.** The sigmoid of 0 is 0.5, so the model assigns equal probability to either response being preferred. Observing that the first response was chosen has probability 0.5, and its negative log is log 2, about 0.693.

**A tempting wrong approach.** Expecting zero loss because the scores are equal is the mistake. Zero loss would require probability 1 for the observed choice; an indifferent model still pays log 2 for every labeled comparison.

**How to verify.** The reference asserts `np.isclose(pair_loss([0, 0]), np.log(2))`. Compute `sigmoid(0)` and confirm 0.5.

**Expected observation:** Preference probability 0.5 and loss log 2.

## 2. Shift both rewards

Pairwise labels cannot determine a common reward offset, including prompt-specific offsets when comparisons stay within prompts.

**Approach.** Add 100 to both scores and recompute `pair_loss` and `pair_gradient`. Case A uses `[1, -1]` and `[101, 99]`.

**Why it holds for this fixture.** The loss depends only on the difference a - b, which is 2 in both cases. The gradient is `[g, -g]` with g = sigmoid(2) - 1, again a function of the difference only. A common offset leaves every quantity unchanged.

**A tempting wrong approach.** Reading a learned reward of 101 as better than a reward of 1 from another run is the mistake. Pairwise data cannot pin down the absolute level, so rewards are only comparable within the same comparison.

**How to verify.** Case A asserts `np.isclose(pair_loss(scores), pair_loss(shifted))`, and the exercise checks assert equal gradients for `[4, 2]` and `[104, 102]`. The gradient components also sum to 0.

**Expected observation:** Loss and score gradient remain unchanged.

## 3. Reverse empirical counts

Reversing labels changes the sign of the fitted log odds, while finite counts still imply uncertainty.

**Approach.** Call `mle_difference(1, 3)`. The maximum-likelihood score difference is log(wins / losses) = log(1 / 3).

**Why it holds for this fixture.** The sigmoid of log(1 / 3) is (1 / 3) / (1 + 1 / 3) = 0.25, which equals the observed win fraction 1 / 4. Reversing case B's 3 to 1 counts flips the sign of the log odds and gives 0.25 instead of 0.75.

**A tempting wrong approach.** Reporting 0.25 as the true preference rate is too strong. With four comparisons, many probabilities near 0.25 fit nearly as well; the estimate needs an interval.

**How to verify.** The reference asserts `np.isclose(sigmoid(mle_difference(1, 3)), 0.25)` and `np.isclose(mle_difference(2, 2), 0)` for balanced counts.

**Expected observation:** The fitted preference probability is 0.25.

## 4. All wins and no losses

Regularization or a prior can produce a finite estimate, but it changes the model and must be stated.

**Approach.** Call `mle_difference(4, 0)`. The function requires both wins and losses to be positive and raises otherwise.

**Why it holds for this fixture.** With four wins and zero losses, the likelihood keeps increasing as the difference grows, approaching 1 without reaching it. There is no finite maximum, so any finite number returned would be arbitrary.

**A tempting wrong approach.** Plugging in a tiny loss count such as 0.001 to get a finite answer is the mistake if left unstated. That is a form of regularization, and it changes the model; the chosen prior must be reported.

**How to verify.** The reference wraps `mle_difference(4, 0)` in a try block and raises `Infinite MLE represented as finite` if no error occurs.

**Expected observation:** No finite maximum-likelihood difference exists.

## 5. Test numerical stability

Stable softplus arithmetic preserves the large finite loss without underflowing a probability to zero first.

**Approach.** Call `pair_loss([-1000, 1000])`. The preferred response has score -1000 and the rejected one 1000, so the difference is -2000.

**Why it holds for this fixture.** The loss is `logaddexp(0, 2000)`, which equals 2000 to machine precision. A naive form, -log(sigmoid(-2000)), would compute a sigmoid that underflows to 0 and then return infinity.

**A tempting wrong approach.** Computing the probability first and taking its log is the common error. The result is `inf` or `nan`, which then corrupts any average or gradient that includes it.

**How to verify.** The reference asserts `np.isfinite(pair_loss([-1000, 1000]))` and that the value equals exactly 2000.

**Expected observation:** Loss remains finite at 2000.

## 6. Interpret a preference cycle

Their sum would need to be positive while algebraically equaling zero. Investigate stochasticity, annotator heterogeneity and multiple criteria.

**Approach.** Write the three preferences as scalar inequalities: a > b, b > c and c > a. Sum the implied differences.

**Why it holds for this fixture.** (a - b) + (b - c) + (c - a) = 0, yet each term would need to be positive, so the sum would be positive. No scalar scores satisfy all three; case B shows a = 2, b = 1, c = 0 satisfies two but not c > a.

**A tempting wrong approach.** Fitting a scalar reward anyway and reporting its order as the true ranking hides the cycle. The cycle may reflect label noise, different annotators or different criteria, and each calls for a different response.

**How to verify.** Case B asserts that `(a > b) and (b > c) and not (c > a)` for the example scores. Check cycle frequency in the raw labels before fitting.

**Expected observation:** A deterministic scalar ordering cannot satisfy all three.
