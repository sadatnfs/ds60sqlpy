# eval-001: explained reference

`eval-001_reference.py` asserts each answer below, from *Reverse the comparison* to *Define an empty population*, on the authored estimand and sampling unit fixture only. Before applying a conclusion to other data, recheck the assumption that *Duplicate an identifier* tests.

## 1. Reverse the comparison

An improvement sign is a convention. Correctness B minus A favors B when positive; swapping systems negates the result.

**Approach.** Write one row such as `("only", "x", 0, 1)` where A fails and B succeeds, call `family_difference` on it, then swap the last two fields and call it again. The function subtracts `r[2]` from `r[3]`, so the column order alone fixes the sign.

**Why it holds for this fixture.** The helper computes B minus A per request. One success gained by B gives 1 - 0 = +1, and swapping the columns gives 0 - 1 = -1. Nothing about the data changed, only which system sits in the subtracted slot.

**A tempting wrong approach.** Reporting the absolute value as "a one point difference" hides which system won. A reader comparing two reports with opposite conventions could then promote the worse system, because +1 under one convention is the same evidence as -1 under the other.

**How to verify.** The reference asserts `family_difference([("only", "x", 0, 1)]) == 1` and the swapped call `== -1`. Also check that swapping columns in the two-row set `[("a", "x", 1, 0), ("b", "y", 0, 1)]` still returns 0, since that set is symmetric.

**Expected observation:** The values are +1 and -1.

## 2. Change the target mix

0.75(1)+0.25(-1)=0.5. The weights describe the target population, not a correction that is always preferable.

**Approach.** Take the per-family differences from case A: metrics rows all move from 0 to 1, so the metrics difference is +1, and the single policy row moves from 1 to 0, so the policy difference is -1. Multiply each family difference by its target share and add.

**Why it holds for this fixture.** With target weights 0.75 and 0.25, the estimand is 0.75 times 1 plus 0.25 times -1, which is 0.5. The case A request mean is also 0.5 only because three of four rows happen to be metrics rows; the family mean of 0 uses equal 0.5 weights.

**A tempting wrong approach.** Passing `weighting="family"` and calling it the target estimate gives 0, which answers a different question: equal importance per family. Neither 0 nor 0.5 is wrong in general; each is correct only for the population the report names.

**How to verify.** Compute `0.75 * 1 + 0.25 * -1` by hand and confirm 0.5. Then add the six extra metrics rows from case A: the request mean moves toward 1 while the 75/25 target estimate stays at 0.5, because target weights do not depend on how many rows were sampled.

**Expected observation:** The weighted improvement is 0.5.

## 3. Duplicate an identifier

Counting an accidental duplicate twice changes both weights and apparent precision; reject it before estimation.

**Approach.** Append a copy of an existing tuple, for example `[rows[0], rows[0]]`, and call `family_difference`. The validator compares `len(ids)` with `len(set(ids))` and raises `ValueError` before any differences are averaged.

**Why it holds for this fixture.** Each request ID names one paired observation of A and B. A repeated ID means the same request would count twice, doubling its weight in the request mean and making the sample look larger than the population of distinct requests actually observed.

**A tempting wrong approach.** Deduplicating silently by keeping the first copy seems harmless, but if the two copies disagree (say one has B correct and one has B wrong) the program would pick a label arbitrarily. Rejection forces someone to find out why the ledger contains two rows for one request.

**How to verify.** The reference wraps `family_difference([rows[0], rows[0]])` in `try` and raises `AssertionError("Duplicate request accepted")` if no `ValueError` appears. Run the reference and confirm it prints the final pass line.

**Expected observation:** The paired-data validator rejects it.

## 4. Require complete gates

An absent result is unknown. Explicit completeness prevents an all([]) or missing-key success.

**Approach.** Build a gate dictionary with only `quality` and `label_coverage`, both `True`, and pass it to `decision`. The function first compares `set(gates)` with the required set `{"quality", "label_coverage", "access_policy"}` and only then checks values.

**Why it holds for this fixture.** The missing key makes the set comparison fail, so the function returns `no-go` even though every supplied value is `True`. Worked case B shows the same rule for a present key holding `None`: `v is True` rejects it because unknown is not a pass.

**A tempting wrong approach.** Writing `all(gates.values())` returns `True` for the two-key dictionary and also returns `True` for an empty dictionary, since `all([])` is `True`. That would let an incomplete or empty packet ship as `go`.

**How to verify.** The reference asserts `decision({"quality": True, "label_coverage": True}) == "no-go"` and the complete three-key version `== "go"`. Adding `"access_policy": None` should also return `no-go`.

**Expected observation:** The result remains no-go.

## 5. Show missing-label coverage

The unchanged accuracy does not imply unchanged evidence. Half the eligible population now lacks labels.

**Approach.** Extend the case B label list from `[1, 1, None]` to `[1, 1, None, None]` and recompute both numbers: accuracy over the observed labels, and coverage as observed count divided by eligible count.

**Why it holds for this fixture.** The observed labels are still `[1, 1]`, so accuracy is 2 / 2 = 1. Coverage drops from 2 / 3 to 2 / 4 = 0.5. The accuracy number is computed only over labeled rows, so it cannot reveal that half the eligible requests now carry no evidence at all.

**A tempting wrong approach.** Treating unlabeled rows as correct (filling `None` with 1) reports accuracy 1 with coverage 1, which invents evidence. Treating them as wrong reports 0.5, which invents failures. Both hide the real state: unknown.

**How to verify.** Run `observed = [x for x in labels if x is not None]`, then check `np.mean(observed) == 1` and `len(observed) / len(labels) == 0.5`. The `label_coverage` gate should be `False` at this coverage under any reasonable threshold, which makes `decision` return `no-go`.

**Expected observation:** Observed accuracy stays 1 while label coverage falls to 0.5.

## 6. Define an empty population

An empty evaluation cannot support a deployment claim; the program rejects it and the report should identify why coverage is empty.

**Approach.** Call `family_difference([])`. The first guard `if not rows` raises `ValueError` with the message that requests must be nonempty and uniquely paired.

**Why it holds for this fixture.** With no eligible requests there is no numerator and no denominator. `np.mean` of an empty array returns `nan` with a warning, and a perfect-accuracy shortcut would return 1. Neither describes evidence about the deployment population.

**A tempting wrong approach.** Returning 0 as "no difference" looks neutral, but 0 is a claim that A and B performed equally on the population. An empty evaluation supports no claim, and a downstream gate that sees 0 might treat it as a tie and ship either system.

**How to verify.** The reference calls `family_difference([])` inside `try` and fails with `Empty population accepted` if no error is raised. In a report, record why the eligible set was empty, such as a filter that excluded every family.

**Expected observation:** Raise an error instead of returning perfect accuracy.
