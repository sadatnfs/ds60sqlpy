# eval-015: explained reference

`eval-015_reference.py` asserts each answer below, from *Report immature labels* to *Investigate an alert*, on the authored label delay and distribution shift fixture only. Before applying a conclusion to other data, recheck the assumption that *Identical distributions* tests.

## 1. Report immature labels

The missing failure label has not become a success. The report must expose incomplete outcome ascertainment.

**Approach.** Call `observed_cohort(rows, 2)` on case A's two requests. Both events are at day 1, so both are eligible, but only the first label arrives by day 2.

**Why it holds for this fixture.** The labeled row is correct, so accuracy is 1 / 1 = 1. Label coverage is 1 / 2 = 0.5. The second request's label is not yet known; it has not become a success.

**A tempting wrong approach.** Reporting accuracy 1 at day 2 without coverage is the mistake. Delayed labels are often failures (complaints take time to arrive), so early accuracy can be systematically optimistic.

**How to verify.** Case A asserts `early["accuracy"] == 1` and `early["label_coverage"] == 0.5`. The exercise checks also confirm coverage 0 when the only label arrives at day 10 and the cutoff is 5.

**Expected observation:** Accuracy 1 with label coverage 0.5.

## 2. Wait for the cohort

The difference is explained by label arrival, so an unqualified early-versus-late accuracy comparison is misleading.

**Approach.** Call `observed_cohort(rows, 10)` on the same two requests. Both labels have arrived by day 10.

**Why it holds for this fixture.** The second label is a failure, so accuracy becomes (1 + 0) / 2 = 0.5 with coverage 1. Nothing about the model changed between day 2 and day 10; only the set of known labels did.

**A tempting wrong approach.** Comparing the day 2 accuracy of one release with the day 10 accuracy of another and concluding the newer one is better is the mistake. Both releases must be compared on cohorts of the same maturity.

**How to verify.** Case A asserts `mature["accuracy"] == 0.5` and `mature["label_coverage"] == 1`.

**Expected observation:** Accuracy 0.5 and label coverage 1.

## 3. Identical distributions

This is an exact diagnostic invariant, not proof that model quality is unchanged.

**Approach.** Call `js_divergence([0.3, 0.7], [0.3, 0.7])`. The mixture m equals both inputs.

**Why it holds for this fixture.** Each log ratio is log(x / m) = log 1 = 0, so both terms are 0 and the divergence is exactly 0. This is a property of the formula, useful as a code check.

**A tempting wrong approach.** Concluding from a zero drift score that model quality is unchanged is the mistake. The histogram covers inputs only; quality can change because of a model update, a label change or a feature not in the histogram.

**How to verify.** The reference asserts `js_divergence([0.3, 0.7], [0.3, 0.7]) == 0` and that swapping the arguments of the 0.2/0.8 pair gives the same value, since JS divergence is symmetric.

**Expected observation:** JS divergence 0.

## 4. Disjoint support

The finite maximum is a useful boundary test and differs from an unbounded one-direction KL divergence.

**Approach.** Call `js_divergence([1, 0], [0, 1])`. The mixture is m = [0.5, 0.5].

**Why it holds for this fixture.** For p, only the first entry is positive, contributing 1 times log(1 / 0.5) = log 2. The same holds for q on the second entry. The average of the two terms is log 2, about 0.693 in natural logarithms, the maximum possible value.

**A tempting wrong approach.** Using one-direction KL divergence on disjoint supports gives an infinite value, because some q entry is zero where p is positive. JS stays finite because both directions compare against the mixture, which is positive wherever either input is.

**How to verify.** Case B asserts `np.isclose(js_divergence([1, 0], [0, 1]), np.log(2))` and that the 0.8/0.2 pair lies strictly between 0 and log 2.

**Expected observation:** JS divergence is log 2.

## 5. Choose assignment units

The experimental unit should reflect how exposure and outcomes can influence one another; many rows do not create independent users.

**Approach.** Identify the unit through which requests influence one another. Requests from the same user share conversation history, so a user-level assignment keeps all of that user's requests under one system.

**Why it holds for this fixture.** If requests were randomized individually, a user could see system A in one turn and B in the next, and B's answer would depend on A's earlier output. Outcomes would then mix both systems and the comparison would be biased.

**A tempting wrong approach.** Randomizing by request because it gives more units, then computing a standard error over requests, is the mistake. The effective sample is the number of users, so uncertainty must be computed with clustering by user, as in eval-006.

**How to verify.** No reference assertion covers this task. Check that every user ID appears under exactly one arm and that the analysis resamples users, not requests.

**Expected observation:** Consider user-level assignment and cluster-aware analysis.

## 6. Investigate an alert

A changed input mix may be benign or may reveal unsupported future risk; retain outcome and operational evidence alongside drift.

**Approach.** Before concluding degradation, break the drift down: which input categories changed share, whether label coverage changed, and whether mature-cohort quality is stable within each category.

**Why it holds for this fixture.** A rising JS score with stable mature quality often means the input mix shifted toward categories the model already handles well. It can also mean new categories arrived whose labels have not matured yet, which `observed_cohort` would show as low coverage.

**A tempting wrong approach.** Rolling back the model because the drift score crossed a threshold is the mistake. Drift is a property of inputs, not of model quality, and a rollback would not change the input mix.

**How to verify.** No reference assertion covers this task. Report the drift value, per-category shares, mature-cohort accuracy and label coverage together for the same window.

**Expected observation:** Investigate composition and coverage before concluding model degradation.
