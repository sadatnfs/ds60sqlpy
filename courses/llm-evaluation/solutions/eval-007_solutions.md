# eval-007: explained reference

`eval-007_reference.py` asserts each answer below, from *One comparison* to *Separate value from significance*, on the authored familywise error and Bonferroni fixture only. Before applying a conclusion to other data, recheck the assumption that *Overspend the budget* tests.

## 1. One comparison

With one prespecified comparison the threshold remains 0.05; this code uses <=.

**Approach.** Call `bonferroni([0.05])` at the default alpha 0.05. With one comparison the threshold is alpha / 1 = 0.05.

**Why it holds for this fixture.** The decision rule is `p <= alpha / len(p)`. Since 0.05 <= 0.05 is true, the comparison rejects. The family has one member, so no multiplicity adjustment changes the threshold.

**A tempting wrong approach.** Using a strict `<` would fail to reject at exactly 0.05. Either convention can be defended, but it must match the written protocol; switching after seeing a boundary p-value changes the rule to fit the result.

**How to verify.** The reference asserts `bonferroni([0.05]).tolist() == [True]`. Change the input to 0.0501 and confirm it returns `[False]`.

**Expected observation:** The declared non-strict rule rejects.

## 2. Three equal findings

Three nominal findings are not three adjusted findings under this family definition.

**Approach.** Call `bonferroni([0.02, 0.02, 0.02])`. The family has three members, so each threshold is 0.05 / 3, about 0.0167.

**Why it holds for this fixture.** Each p-value is 0.02, which is above 0.0167, so none is rejected. Each would pass a single unadjusted 0.05 test, but the family claim (at least one true effect, with family error at most 0.05) is not supported.

**A tempting wrong approach.** Reporting three significant improvements because each p-value is below 0.05 ignores that three tests were run. Worked case A shows the independent three-test family error is about 0.143, nearly three times the nominal rate.

**How to verify.** The reference asserts `bonferroni([0.02, 0.02, 0.02]).tolist() == [False] * 3`. Worked case A's `[0.01, 0.03, 0.2]` rejects only 0.01.

**Expected observation:** None crosses equal Bonferroni thresholds.

## 3. Overspend the budget

The advertised family bound requires the total allocation to remain within its declared budget.

**Approach.** Call `spent_decisions([0.1, 0.2], [0.03, 0.03])` with alpha 0.05. The validation computes `a.sum()` and compares it with alpha plus a small tolerance.

**Why it holds for this fixture.** The budgets add to 0.06, which exceeds 0.05. The plan's promise is that total false rejection probability across looks stays below alpha by the union bound; a 0.06 allocation breaks that bound before any data are examined.

**A tempting wrong approach.** Accepting the plan and just noting it is "slightly over" means the reported family guarantee is false. If more budget is needed for a later look, an earlier allocation must shrink so the total stays at 0.05.

**How to verify.** The reference rejects `([0.1], [0.06])` as an overspent single look and fails with `Invalid monitoring plan accepted` otherwise. Worked case B shows a valid split, 0.01 + 0.015 + 0.025 = 0.05.

**Expected observation:** The monitoring plan is rejected.

## 4. Specify dependent looks

The formula \(1-(1-\alpha)^m\) uses independence; the union-bound inequality does not.

**Approach.** Write the two inequalities side by side. The union bound says the probability that any of m tests falsely rejects is at most the sum of their individual error rates. The formula 1 - (1 - alpha) to the power m gives the exact family error only for independent tests.

**Why it holds for this fixture.** Repeated looks at an accumulating evaluation are strongly dependent, since later data include earlier data. The union bound still holds because it makes no independence assumption; it only requires each look's own error rate to be at most its budget.

**A tempting wrong approach.** Using 1 - (1 - 0.05 / 3) cubed to justify the plan and then noting the looks are dependent is a mismatch. The independence formula is the illustrative calculation in case A, not the guarantee the monitoring plan relies on.

**How to verify.** No assertion covers this task. Check your explanation by naming which inequality the `spent_decisions` budget check enforces (the sum, so the union bound) and noting it would remain valid for dependent looks.

**Expected observation:** It does not; individual error bounds still need to hold.

## 5. Unknown result

Unknown evidence requires an explicit incomplete assessment, not a smaller multiplicity correction.

**Approach.** Pass `[float("nan")]` with budget `[0.01]` to `spent_decisions`. The guard `np.isfinite(p).all()` fails and the function raises.

**Why it holds for this fixture.** A missing p-value, such as from a failed job, is not evidence for or against an effect. Excluding it while keeping its budget elsewhere, or treating it as 1, both change the family the plan was written for.

**A tempting wrong approach.** Dropping the NaN and recomputing Bonferroni with a smaller m makes each remaining threshold larger, which raises the chance of rejection. Missing evidence would then make the test more permissive, the opposite of what is safe.

**How to verify.** The reference includes `([float("nan")], [0.01])` in the invalid list. Record the look as incomplete and rerun it rather than editing the family.

**Expected observation:** The decision function rejects it.

## 6. Separate value from significance

A release decision combines expected utility, uncertainty, constraints and costs; its logic must be recorded separately from a p-value.

**Approach.** Write down the estimated improvement, its interval, and the minimum useful effect, and compare the interval with that minimum. A very precise estimate can lie entirely below it.

**Why it holds for this fixture.** Statistical significance says the effect is probably not zero; it does not say the effect is large enough to justify migration cost, risk or latency. A release decision needs the size of the effect and the costs, not only the p-value.

**A tempting wrong approach.** Shipping because the result is significant is the mistake. With a large evaluation set, an improvement of 0.1 points can be highly significant and still not worth any operational change.

**How to verify.** No assertion covers this task. Verify by recording the decision rule explicitly, for example "ship if the lower interval bound exceeds 0.02 and no constraint fails," and checking the estimate against it separately from the p-value.

**Expected observation:** The statistical result alone does not mandate deployment.
