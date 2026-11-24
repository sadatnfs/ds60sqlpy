# eval-005: explained reference

`eval-005_reference.py` asserts each answer below, from *Change the mixture* to *Compare systems fairly*, on the authored stratification and inclusion probability fixture only. Before applying a conclusion to other data, recheck the assumption that *Compare denominators* tests.

## 1. Change the mixture

0.25(0.9)+0.75(0.5)=0.6. The model outcomes are unchanged; only the target population differs.

**Approach.** Keep the stratum accuracies from case A, routine 0.9 and rare 0.5, and pass new target weights `{"routine": 0.25, "rare": 0.75}` to `target_mean`. The function multiplies each stratum mean by its target weight and sums.

**Why it holds for this fixture.** The result is 0.25 times 0.9 plus 0.75 times 0.5, which is 0.225 + 0.375 = 0.6. Case A gave 0.86 under a 90/10 mix and 0.7 under a 50/50 mix. The model's per-stratum behavior is identical in all three; only the population the claim describes moves.

**A tempting wrong approach.** Quoting 0.86 for a deployment where rare requests dominate is the error. The routine stratum carries the high score, so a mix that shifts weight toward rare requests lowers the target accuracy without any change in the model.

**How to verify.** Compute `target_mean({"routine": 0.9, "rare": 0.5}, {"routine": 0.25, "rare": 0.75})` and check it with `np.isclose(..., 0.6)`. The reference checks the same arithmetic on another pair: means 0.2 and 0.8 with weights 0.25 and 0.75 give 0.65.

**Expected observation:** Target accuracy is 0.6.

## 2. Expose missing support

The outcome mean for that stratum is unidentified without additional data or explicit modeling assumptions.

**Approach.** Pass means for stratum `a` only and target weights for both `a` and `b`, such as `target_mean({"a": 1}, {"a": 0.5, "b": 0.5})`. The first guard compares the two key sets and raises `Every target stratum needs data`.

**Why it holds for this fixture.** Half the target population lies in stratum `b`, and the sample contains no observed outcome there. Any number for the `b` mean would be an assumption, so the weighted sum is not identified from the data.

**A tempting wrong approach.** Dropping `b` and renormalizing `a` to weight 1 returns 1.0 and reads like a valid estimate. It actually describes a population with no `b` requests, which is not the target the report names.

**How to verify.** The reference wraps exactly this call in `try` and raises `Absent target stratum accepted` if no error occurs. Fixing it requires either sampling from `b` or stating an explicit model for its mean.

**Expected observation:** The estimator rejects the mismatch.

## 3. Compare denominators

Horvitz-Thompson estimates the population total before dividing by N. Self-normalization divides by an estimated total weight and need not equal it.

**Approach.** Rerun case B by hand: outcomes `[1, 0]`, inclusion probabilities `[0.5, 0.25]`, population size 10. The weights are 1 / p, which gives 2 and 4, and the weighted outcome sum is 2 times 1 plus 4 times 0 = 2.

**Why it holds for this fixture.** The Horvitz-Thompson style mean divides that sum by the known N = 10, giving 0.2. The self-normalized mean divides by the sampled weight sum 2 + 4 = 6, giving 1 / 3. The weight sum estimates N, but here it is 6, not 10, so the two means differ.

**A tempting wrong approach.** Assuming the two estimators must agree and hunting for a bug is the mistake. They target the same quantity but use different denominators; disagreement is expected in small samples and shrinks only if the weight sum tends toward N.

**How to verify.** Worked case B asserts `np.isclose(ht, 0.2)` and `np.isclose(sn, 1 / 3)`. With probabilities `[1, 1]` and N = 2, the weights sum to N exactly and both estimators return 0.5.

**Expected observation:** \(0.2\) uses the known population size \(N=10\); \(1/3\) uses the sampled weight sum \(6\).

## 4. Increase weight concentration

A nominal sample of two is dominated by one weighted observation. ESS describes concentration but does not replace a clustering analysis.

**Approach.** Call `inclusion_estimates([1, 0], [0.01, 1], 101)` and read the third returned value. The ESS formula is the squared sum of weights divided by the sum of squared weights.

**Why it holds for this fixture.** The weights are 100 and 1. The squared sum is 101 squared, 10201, and the sum of squares is 10000 + 1 = 10001, so ESS is about 1.02. Two rows were sampled, yet one row carries almost all the weight and the estimate behaves like a sample of one.

**A tempting wrong approach.** Quoting n = 2 as the sample size for uncertainty is the mistake. It understates variance because the low-probability row dominates both estimators. ESS flags this, but it does not account for clustering, which needs a separate grouped analysis.

**How to verify.** The reference asserts `inclusion_estimates([1, 0], [0.01, 1], 101)[2] < 1.03`. Case B's weights 2 and 4 give ESS 36 / 20 = 1.8, a milder concentration for comparison.

**Expected observation:** The diagnostic ESS is below 1.03.

## 5. Audit zero probability

An event that cannot enter the sample cannot provide an observed outcome for this estimator.

**Approach.** Set one probability to 0, for example `inclusion_estimates([1, 0], [0, 0.5], 2)`. The guard `np.any(p <= 0)` raises before any weight is computed.

**Why it holds for this fixture.** A zero inclusion probability means that unit could never be sampled, and its weight 1 / 0 is undefined. The estimator relies on every population unit having positive probability; without it, part of the population has no representation.

**A tempting wrong approach.** Clipping zero to a tiny value like 1e-9 avoids the division error and creates a weight of one billion. A single row would then dominate every estimate, and the code would appear to work while the design assumption has been broken.

**How to verify.** The reference loops over `[0, 0.5]` and `[1.1, 0.5]` and fails with `Unsupported inclusion probability accepted` if either passes. Probabilities above 1 are rejected for the same reason: they are not probabilities.

**Expected observation:** The calculation must fail.

## 6. Compare systems fairly

Paired, consistently weighted differences prevent a traffic-mixture change from masquerading as a model improvement.

**Approach.** Fix one eligible ID list and one set of target weights, compute each system's per-stratum means on those IDs, then pass both through `target_mean` with the same weights and subtract.

**Why it holds for this fixture.** If A is scored on last month's traffic and B on this month's, a mix shift toward routine requests would raise B's number even with identical per-stratum behavior. Sharing the ledger and weights means the difference reflects only the systems.

**A tempting wrong approach.** Comparing a 0.86 estimate for one system against a 0.7 estimate for another looks like a 0.16 gap. In case A those two numbers are the same per-stratum means under two different weightings, so the gap is entirely a population artifact.

**How to verify.** Check that both estimates use identical ID sets (compare them as sets) and identical weight dictionaries. Then recompute with A's and B's means swapped and confirm the difference changes sign, as in eval-001.

**Expected observation:** Both estimates use identical eligible IDs and target weights.
