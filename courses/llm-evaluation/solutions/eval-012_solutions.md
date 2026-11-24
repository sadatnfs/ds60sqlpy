# eval-012: explained reference

`eval-012_reference.py` asserts each answer below, from *Inspect each prompt* to *Validate axes*, on the authored crossed design and interaction fixture only. Before applying a conclusion to other data, recheck the assumption that *Change the prompt target* tests.

## 1. Inspect each prompt

An overall favorable result does not imply improvement under every configuration.

**Approach.** Compute the cell means with `decomposition(fixture())`, then subtract the baseline row from the candidate row: `cells[1] - cells[0]`.

**Why it holds for this fixture.** The cells are `[[0.9, 0.6], [0.8, 0.9]]` with models as rows and prompts as columns. Candidate minus baseline is 0.8 - 0.9 = -0.1 under prompt 1 and 0.9 - 0.6 = +0.3 under prompt 2. The average is +0.1.

**A tempting wrong approach.** Reporting +0.1 as "the candidate is better" is the mistake when the deployment uses prompt 1. The candidate is worse there, and the average hides that because prompt 2 contributes a large gain.

**How to verify.** Worked case A asserts `np.testing.assert_allclose(cells[1] - cells[0], [-0.1, 0.3])`, and the exercise checks assert the mean difference is 0.1.

**Expected observation:** The differences are -0.1 and +0.3.

## 2. Check reconstruction

This algebraic identity is a useful implementation check, independent of any inferential assumptions.

**Approach.** Add `grand + model[:, None] + prompt[None, :] + interaction` and compare with `cells`.

**Why it holds for this fixture.** The grand mean is 0.8. Model effects are -0.05 and +0.05; prompt effects are +0.05 and -0.05. The interaction is `[[0.1, -0.1], [-0.1, 0.1]]`. For the baseline under prompt 1: 0.8 - 0.05 + 0.05 + 0.1 = 0.9, which is the observed cell.

**A tempting wrong approach.** Computing interaction with a sign error, for example adding the main effects instead of subtracting, will still produce numbers that look plausible. The reconstruction check is the fastest way to catch it.

**How to verify.** Worked case A uses `np.testing.assert_allclose(cells, grand + model[:, None] + prompt[None, :] + interaction)`. The exercise checks also confirm each effect vector and each interaction row and column sum to zero.

**Expected observation:** Every observed cell is recovered within floating tolerance.

## 3. Change the prompt target

A fixed-prompt deployment needs evidence for that prompt, not an attractive average over unused alternatives.

**Approach.** Use weights 1 and 0 over the two prompts and compute the weighted candidate minus baseline difference.

**Why it holds for this fixture.** With all weight on prompt 1 the difference is simply that column's value, -0.1. The equal-weight +0.1 described a deployment that uses both prompts equally, which this one does not.

**A tempting wrong approach.** Using the average over prompts because it is the main effect is the mistake. Main effects average over prompts that will not be used, so they do not describe a fixed-prompt deployment when the interaction is nonzero.

**How to verify.** Compute `(cells[1] - cells[0]) @ [1, 0]` and confirm -0.1. Repeat with `[0, 1]` for +0.3.

**Expected observation:** The candidate difference becomes-0.1.

## 4. Equalize selection budgets

A comparison of selection procedures differs from a comparison of one selected system with an untuned mean; final assessment must still be independent.

**Approach.** Give each model the same selection procedure: choose the best prompt per model on development data with `cells.max(axis=1)`.

**Why it holds for this fixture.** Both models reach 0.9 on development: the baseline with prompt 1 and the candidate with prompt 2. Under equal selection budgets the development difference is 0.

**A tempting wrong approach.** Case B shows the unequal version: tuning the candidate (0.9) and comparing with the baseline's untuned mean (0.75) gives 0.15. That difference measures extra tuning effort, not a better model.

**How to verify.** Worked case B asserts `fair_development` equals `[0.9, 0.9]` and the mixed-budget difference equals 0.15. Final claims still need an independent test set because both maxima are selected values.

**Expected observation:** Both selected development scores are 0.9.

## 5. Count seed replication

This describes the three constructed seed scores. It does not quantify variation across an unseen population of task families.

**Approach.** Take the three baseline seeds under prompt 1, `fixture()[0, 0]` = `[0.8, 0.9, 1.0]`, and compute the sample variance with `ddof=1`.

**Why it holds for this fixture.** The mean is 0.9 and the squared deviations are 0.01, 0 and 0.01, which sum to 0.02. Dividing by n - 1 = 2 gives 0.01. That is the spread across three seeds in one constructed cell.

**A tempting wrong approach.** Using 0.01 as the uncertainty of the model comparison is the mistake. Seed variation is one source; variation across task families is usually larger and needs its own replication, as in eval-006.

**How to verify.** The reference asserts `np.isclose(fixture()[0, 0].var(ddof=1), 0.01)`. With `ddof=0` the result would be 0.02 / 3, about 0.0067.

**Expected observation:** The sample variance is 0.01.

## 6. Validate axes

Silently averaging an unidentified axis can mix model, prompt and replication factors and invalidate the comparison.

**Approach.** Call `decomposition([[1, 2]])`. The array has two dimensions, and the guard `values.ndim != 3` raises.

**Why it holds for this fixture.** The helper needs model, prompt and seed axes in that order. A two-dimensional input could mean model by prompt with one seed, or model by seed with one prompt, and averaging axis 2 would be impossible or meaningless.

**A tempting wrong approach.** Reshaping automatically, such as adding a trailing axis, would accept the input but would require guessing what each axis means. A wrong guess silently swaps prompt and seed variation.

**How to verify.** The reference wraps `decomposition([[1, 2]])` in `try` and fails with `Missing tensor axis accepted` if no error is raised. Pass `[[[1, 2]]]` explicitly when you mean one model, one prompt and two seeds.

**Expected observation:** The tensor contract rejects it.
