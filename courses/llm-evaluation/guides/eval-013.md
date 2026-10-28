# eval-013: Selection procedures and protected holdouts

## Starting point and outcome

Intermediate; approximately 120 minutes. Direct prerequisites: `eval-012`, `eval-007`.

Evaluate a complete model/prompt selection procedure without using final outcomes to choose the winner.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-013`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Selection is part of the system

A candidate can include a model, prompt, retrieval depth, judge, parser and abstention threshold. Choosing each component after inspecting validation outcomes creates a procedure with more opportunities to fit noise. The final score should assess the selected procedure, not only the final parameter vector or checkpoint name.

Suppose several candidates have the same underlying quality but their development estimates contain zero-mean noise. Selecting the maximum does not preserve zero-mean noise in the selected score. For observed estimates \(\widehat{q}_j=q+\varepsilon_j\), the reported development maximum is \(q+\max_j\varepsilon_j\). Even when each \(\varepsilon_j\) has mean zero, its maximum usually has positive expectation. More search opportunities can therefore improve the reported development score without improving true quality.

The issue is not that tuning is forbidden. Tuning is a useful part of development. The requirement is to distinguish the data that select the system from the data that assess the selected procedure, and to include the relevant search budget when comparing two approaches.

## Worked case A: exact selection optimism

The first program enumerates equally likely development noise values of plus or minus 0.1. With one candidate, mean selected noise is zero. With two candidates it becomes 0.05, and with four it becomes 0.0875. This is an exact constructed distribution, so its optimism is visible without simulation error. It is not a universal formula for arbitrary model searches, whose estimates can be correlated and have unequal variances.

```python
from itertools import product

import numpy as np


def selection_optimism(candidates):
    if type(candidates) is not int or not 1 <= candidates <= 12:
        raise ValueError("Bounded candidate count required")
    return float(np.mean([max(noise) for noise in product((-0.1, 0.1), repeat=candidates)]))


def assess_procedure(development, assessment):
    dev = np.asarray(development, float)
    test = np.asarray(assessment, float)
    if (
        dev.ndim != 2
        or dev.shape != test.shape
        or not dev.size
        or not np.isfinite(dev).all()
        or not np.isfinite(test).all()
    ):
        raise ValueError("Aligned finite fold/candidate tables required")
    choices = np.argmax(dev, axis=1)
    selected = test[np.arange(len(choices)), choices]
    return choices, selected


def worked_a():
    values = [selection_optimism(n) for n in (1, 2, 4)]
    np.testing.assert_allclose(values, [0, 0.05, 0.0875], atol=1e-12)
    print("Mean selected development noise:", values)


worked_a()
```

## Worked case B: inner selection, outer assessment

Two outer folds each contain an inner development comparison. The procedure chooses the development winner inside each fold and then evaluates that selected candidate using its corresponding outer outcomes. The resulting average is 0.45. Choosing the winner using those outer outcomes instead yields 0.85 on the same table, but consumes the assessment data for selection.

This small table demonstrates the information flow, not a complete fitted cross-validation implementation. In an actual workflow, preprocessing, feature construction, prompt selection and calibration must all remain inside the relevant training/development boundary. A transform learned once from the full dataset can leak information even if the final model fit is nested correctly.

```python
from itertools import product

import numpy as np


def selection_optimism(candidates):
    if type(candidates) is not int or not 1 <= candidates <= 12:
        raise ValueError("Bounded candidate count required")
    return float(np.mean([max(noise) for noise in product((-0.1, 0.1), repeat=candidates)]))


def assess_procedure(development, assessment):
    dev = np.asarray(development, float)
    test = np.asarray(assessment, float)
    if (
        dev.ndim != 2
        or dev.shape != test.shape
        or not dev.size
        or not np.isfinite(dev).all()
        or not np.isfinite(test).all()
    ):
        raise ValueError("Aligned finite fold/candidate tables required")
    choices = np.argmax(dev, axis=1)
    selected = test[np.arange(len(choices)), choices]
    return choices, selected


def worked_b():
    dev = [[0.9, 0.8], [0.7, 0.9]]
    test = [[0.4, 0.8], [0.9, 0.5]]
    choices, selected = assess_procedure(dev, test)
    assert choices.tolist() == [0, 1]
    assert np.isclose(selected.mean(), 0.45)
    assert np.isclose(np.max(test, axis=1).mean(), 0.85)
    print("Selected by development:", choices.tolist(), "outer assessment:", selected.tolist())


worked_b()
```

## Protect and version the evaluation protocol

Record candidate eligibility, tuning resources, selection metric, tie policy, stopping rule and final assessment plan before examining the final labels. Preserve a digest of the selected configuration and dataset version. Digests make later changes detectable; they do not prove that the author had no prior knowledge of the labels.

A final test can be reused as a regression suite after publication, but its role changes. If a failure motivates a new model or prompt, use development data for that iteration and acquire another independent final assessment. A succession of improvements on one repeatedly inspected benchmark does not retain the same untouched-test guarantee.

## Scientific interpretation

Nested evaluation estimates a selection procedure under its fold construction. It does not automatically certify the one final model retrained on all available development data. Temporal deployment may also require forward-chaining partitions rather than random folds, and dependent users or question families require group separation. The estimand and data-generating process determine the suitable split.

When a reported improvement disappears on a new benchmark, inspect selection history before attributing the change to a model regression. Compare candidate counts, prompt-search budgets, access to benchmark labels and shared source documents. Keep unsuccessful candidates in an experiment ledger so the selection mechanism can be reconstructed.

The reference programs provide exact counterexamples and invalid-shape guards. They show why the maximum of noisy estimates is optimistic and why outer outcomes must not choose a candidate. They do not imply that four candidates are too many, that cross-validation eliminates every bias, or that a single held-out score establishes broad generalization.


## Six investigations

### 1. Two noisy candidates

Enumerate the four two-candidate noise combinations.

**Expected:** The mean maximum is 0.05.

**Hint:** Only the all-negative combination has a negative maximum.

### 2. Change only final outcomes

Alter the outer outcomes while retaining development scores.

**Expected:** The selected candidate IDs do not change.

**Hint:** Selection must be a function of development information only.

### 3. Specify a tie rule

Give equal development scores to two candidates.

**Expected:** The reference chooses the first candidate deterministically.

**Hint:** NumPy argmax returns the first maximum.

### 4. Find the optimistic procedure

Select using the outer table in case B.

**Expected:** Its same-table average is 0.85, but it is no longer protected assessment.

**Hint:** Trace which labels selected each candidate.

### 5. Place preprocessing

Decide where a learned normalization or calibration fit belongs.

**Expected:** Inside the corresponding training/development partition.

**Hint:** Data-dependent transforms are part of model fitting.

### 6. Reclassify a reused holdout

Use final-set errors to revise a prompt.

**Expected:** The set becomes development or regression evidence for that revision.

**Hint:** A file name does not preserve independence.

## Primary references

- [Selection bias in cross-validation](https://jmlr.org/papers/v11/cawley10a.html)
- [Existing complete-procedure validation](../../../courses/statistics-ml/tutorials/learning/07-validation-as-a-procedure.md)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
