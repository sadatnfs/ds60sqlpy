# eval-004: explained reference

`eval-004_reference.py` asserts each answer below, from *Reconstruct the confusion table* to *Change the dependence unit*, on the authored Cohen kappa and weighted agreement fixture only. Before applying a conclusion to other data, recheck the assumption that *Complete disagreement* tests.

## 1. Reconstruct the confusion table

Two negative-negative pairs, one positive-negative pair and one positive-positive pair determine both marginals and agreement.

**Approach.** Order categories as `[0, 1]`, put annotator A on rows and B on columns, and count each pair from case A: A = `[1, 1, 0, 0]` and B = `[1, 0, 0, 0]`. The function builds the same table with `table[positions[x], positions[y]] += 1`.

**Why it holds for this fixture.** The pairs are (1,1), (1,0), (0,0), (0,0). Two (0,0) pairs fill cell [0][0], the (1,0) pair fills [1][0] and the (1,1) pair fills [1][1], giving `[[2, 0], [1, 1]]`. The trace is 3, so observed agreement is 3 / 4 = 0.75.

**A tempting wrong approach.** Swapping rows and columns gives `[[2, 1], [0, 1]]`. The agreement and kappa are unchanged, but reading a cell like "A said positive, B said negative" from the transposed table reverses which annotator was more lenient.

**How to verify.** Worked case A asserts `table.tolist() == [[2, 0], [1, 1]]`, `observed == 0.75` and `kappa == 0.5`. Row sums give A's marginals (2, 2) and column sums give B's (3, 1).

**Expected observation:** Rows A and columns B give [[2,0],[1,1]].

## 2. Perfect variation

There is perfect observed agreement with nondegenerate marginals, so the corrected coefficient is defined and equals 1.

**Approach.** Call `agreement([0, 1], [0, 1])`. Both annotators give one 0 and one 1, and they match on both items.

**Why it holds for this fixture.** Observed agreement is 1. The marginals are 0.5 and 0.5 for each annotator, so expected agreement is 0.5 times 0.5 plus 0.5 times 0.5 = 0.5. Kappa is (1 - 0.5) / (1 - 0.5) = 1, and it is defined because the expected value is not 1.

**A tempting wrong approach.** Expecting perfect agreement to always produce kappa 1 is the trap: it does so only when both annotators use more than one category. Exercise 4 shows that perfect agreement on a single category leaves kappa undefined.

**How to verify.** The reference asserts `agreement([0, 1], [0, 1])[1] == 1`. Print the returned table and confirm it is the identity matrix `[[1, 0], [0, 1]]`.

**Expected observation:** Kappa equals 1.

## 3. Complete disagreement

A negative coefficient means less agreement than the marginal reference, not a negative count of labels.

**Approach.** Call `agreement([0, 1], [1, 0])`. Each item gets opposite labels from the two annotators.

**Why it holds for this fixture.** Observed agreement is 0 because the table's diagonal is empty. Each annotator still uses 0 and 1 once, so expected agreement is again 0.5. Kappa is (0 - 0.5) / (1 - 0.5) = -1, the minimum possible for these marginals.

**A tempting wrong approach.** Reading -1 as an error or clamping it to 0 throws away information. A negative kappa signals systematic disagreement, such as one annotator reversing the scale, which is a fixable labeling problem that a clamped 0 would hide.

**How to verify.** The reference asserts `agreement([0, 1], [1, 0])[1] == -1`. The table should be `[[0, 1], [1, 0]]`, with all mass off the diagonal.

**Expected observation:** Kappa equals -1.

## 4. Single-category degeneracy

Both raw and reference agreement are 1. The coefficient becomes 0/0, so preserve the degeneracy instead of replacing it with an attractive score.

**Approach.** Call `agreement([1, 1], [1, 1])`. Both annotators use only category 1, so the table is the single cell `[[2]]`.

**Why it holds for this fixture.** Observed agreement is 1 and expected agreement is also 1, since each annotator puts all mass on one category. Kappa would be (1 - 1) / (1 - 1) = 0 / 0. The code detects `np.isclose(expected, 1)` and raises instead of returning a number.

**A tempting wrong approach.** Reporting kappa as 1 because the annotators matched perfectly is attractive but unsupported. With no variation in labels, the data cannot show whether annotators would agree on a case that differs, so no chance-corrected reliability can be estimated.

**How to verify.** The reference includes `([1, 1], [1, 1])` in its degenerate list together with empty and unequal-length inputs, and fails with `Degenerate labels accepted` if any returns. Report raw agreement 1 and state that kappa is undefined.

**Expected observation:** Kappa is undefined and rejected.

## 5. Distinguish weighted quantities

Observed squared-distance disagreement is useful descriptively, but weighted kappa would normalize it by expected disagreement under marginals.

**Approach.** Compute `ordinal_disagreement([0, 1, 2], [1, 1, 2])` and `ordinal_disagreement([0, 1, 2], [2, 1, 2])`. Each pair contributes the squared level gap divided by `(levels - 1) ** 2`, which is 4 for three levels.

**Why it holds for this fixture.** The adjacent case has one gap of 1, so the mean is (1 / 4) / 3 = 1 / 12. The distant case has one gap of 2, so the mean is (4 / 4) / 3 = 1 / 3. Larger gaps cost more, which is the point of a quadratic weight on an ordinal scale.

**A tempting wrong approach.** Calling 1 / 12 a weighted kappa is the mistake. Weighted kappa divides observed weighted disagreement by the disagreement expected under the marginals and subtracts from 1. The helper reports only the observed part, so it cannot be compared with published kappa thresholds.

**How to verify.** Worked case B asserts `np.isclose(adjacent, 1 / 12)` and `np.isclose(distant, 1 / 3)`. The exercise checks also assert identical labels give 0 and that label 3 on a three-level scale raises `ValueError`.

**Expected observation:** The implemented quantity lacks an expected-disagreement correction.

## 6. Change the dependence unit

Additional paraphrases may reveal within-family variation, but family-level uncertainty cannot treat twenty rows as twenty independent sampled families.

**Approach.** Count sampled units at the level of the dependence. Ten paraphrases from each of two families give twenty rows but only two independently sampled families.

**Why it holds for this fixture.** Paraphrases within one family share the underlying question, so annotator agreement on them is correlated. The uncertainty of a family-level agreement claim must be computed over families, and two families give a very wide interval no matter how many paraphrases they contain.

**A tempting wrong approach.** Computing a confidence interval for kappa with n = 20 treats every paraphrase as an independent draw. That makes the interval far too narrow and suggests the reliability estimate transfers to new families when only two have been seen.

**How to verify.** No reference assertion covers this task. Verify by stating the sampling unit in your report, counting distinct `family` values (two), and resampling families rather than rows if you compute an interval, following the grouping rule from eval-002.

**Expected observation:** The evaluation still has two sampled families.
