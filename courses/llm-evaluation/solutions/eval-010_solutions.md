# eval-010: explained reference

`eval-010_reference.py` asserts each answer below, from *Answer everything* to *Protect the final set*, on the authored selective prediction and risk coverage fixture only. Before applying a conclusion to other data, recheck the assumption that *Check equality* tests.

## 1. Answer everything

The policy pays 5 twice and averages over all four eligible requests.

**Approach.** Call `policy_metrics([0.9, 0.8, 0.4, 0.2], [1, 0, 1, 0], 0)`. Every score is at least 0, so every request is answered.

**Why it holds for this fixture.** Coverage is 4 / 4 = 1. Two answers are correct, so accuracy is 0.5. The two wrong answers cost 5 each, and correct answers cost 0, so the mean cost is (0 + 5 + 0 + 5) / 4 = 2.5.

**A tempting wrong approach.** Choosing the policy with the highest coverage because it helps the most users ignores the cost structure. A wrong answer costs 12.5 times an abstention here, so answering everything is the most expensive option in the fixture.

**How to verify.** The reference asserts `policy_metrics([1, 0], [1, 0], 0)["coverage"] == 1`. Run the four-row call above and confirm the cost is 2.5.

**Expected observation:** Coverage 1, accuracy 0.5 and cost 2.5.

## 2. Abstain on everything

The operational cost remains defined because every eligible request incurs the abstention cost.

**Approach.** Use a threshold above every development score, such as 0.95. No score is at least 0.95, so every request abstains.

**Why it holds for this fixture.** Coverage is 0, and conditional accuracy has no answered rows, so the function returns `None`. Cost is still defined: every request pays the abstention cost 0.4, so the mean is 0.4.

**A tempting wrong approach.** Dropping abstained requests from the cost would make the always-abstain policy cost 0. The cost is averaged over all eligible requests because declining to answer is a real outcome for the person who asked.

**How to verify.** Call `policy_metrics([0.9, 0.8, 0.4, 0.2], [1, 0, 1, 0], 0.95)` and confirm `coverage == 0`, `accuracy is None` and `cost` equals 0.4. The single-row check `policy_metrics([0.4], [1], 0.5)["cost"] == 0.4` shows the same rule.

**Expected observation:** Coverage 0, missing conditional accuracy and cost 0.4.

## 3. Check equality

Boundary behavior matters for reproducibility and should be written into the policy contract.

**Approach.** Call `policy_metrics([0.5], [1], 0.5)`. The rule is `p >= threshold`, so a score equal to the threshold is answered.

**Why it holds for this fixture.** Coverage is 1 because 0.5 >= 0.5. Scores are often rounded, so many requests can sit exactly at a threshold; the inclusive rule decides all of them the same way every run.

**A tempting wrong approach.** Writing `>` in one implementation and `>=` in another seems trivial, but with rounded scores the two policies can differ on many requests, and their coverage and cost will not reproduce across systems.

**How to verify.** The reference asserts `policy_metrics([0.5], [1], 0.5)["coverage"] == 1`. Write the inclusive rule into the policy description that ships with the threshold.

**Expected observation:** The request is answered.

## 4. Derive the probability cutoff

The derivation assumes calibrated correctness probabilities and zero cost for correct answers. It does not justify using 0.92 on an arbitrary score.

**Approach.** Set expected costs equal. Answering costs `wrong_cost` times the probability of being wrong, 5 times (1 - p); abstaining costs 0.4. Answer when 5 (1 - p) <= 0.4.

**Why it holds for this fixture.** Solving gives 1 - p <= 0.08, so p >= 0.92. Worked case A asserts `np.isclose(1 - 0.4 / 5, 0.92)`. The derivation assumes p is a calibrated probability of correctness and correct answers cost nothing.

**A tempting wrong approach.** Plugging 0.92 into a raw model score that is not calibrated is the mistake. Case A's development search chose 0.85 on these scores, and case B shows scores of 0.99 and 0.97 that were both wrong, so these scores are not calibrated probabilities.

**How to verify.** Check that `1 - 0.4 / 5 == 0.92` and then verify calibration separately (eval-011) before using the formula on any score.

**Expected observation:** The calibrated-probability cutoff is 0.92.

## 5. Inspect subgroup coverage

Differences can reflect calibration, difficulty or selection. Preserve group definitions and uncertainty before attributing them to a model mechanism.

**Approach.** Split the eligible requests by group, run `policy_metrics` once per group with the same frozen threshold, and report eligible count, coverage, conditional accuracy and cost for each.

**Why it holds for this fixture.** The overall coverage is a weighted mix of group coverages. If rare requests get lower scores, they abstain more often, and the overall number hides that rare users receive answers far less often than routine users.

**A tempting wrong approach.** Concluding that the model is biased against rare requests from a coverage gap alone skips other explanations: rare requests may be harder, the scores may be miscalibrated for them, or the groups may have been sampled differently.

**How to verify.** Check that the group eligible counts sum to the total and that the count-weighted group costs reproduce the overall cost. Report intervals because rare groups will usually be small.

**Expected observation:** Report each eligible count, coverage and cost.

## 6. Protect the final set

A test failure can guide development, but the same labels cannot remain untouched evidence for the modified policy.

**Approach.** Treat the held-out failure as diagnostic. Case B applies the frozen 0.85 threshold to new outcomes and gets coverage 0.5, accuracy 0 and cost 2.7, which shows the development threshold does not transfer.

**Why it holds for this fixture.** The two confident answers (scores 0.99 and 0.97) were wrong, costing 5 each, and two abstentions cost 0.4 each, so the mean is (5 + 5 + 0.4 + 0.4) / 4 = 2.7. That is worse than always abstaining at 0.4.

**A tempting wrong approach.** Retuning the threshold on the same held-out rows and reporting the new held-out cost is the mistake. The rows have now shaped the policy, so their cost is a development number and overstates performance.

**How to verify.** Worked case B asserts `coverage == 0.5`, `accuracy == 0` and `np.isclose(cost, 2.7)`. After any change, collect a fresh final set and freeze the policy before scoring it.

**Expected observation:** Use it as a diagnosis and collect a new final assessment after changes.
