# eval-004: Agreement, prevalence and adjudication uncertainty

## Starting point and outcome

Beginner; approximately 120 minutes. Direct prerequisites: `eval-003`.

Calculate agreement with the correct marginals, explain prevalence effects, and distinguish reliable labels from valid labels.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-004`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Agreement has several denominators

Two annotators can disagree because an item is ambiguous, because their instructions differ, because one makes mistakes, or because the target concept itself is underspecified. The agreement table organizes those possibilities but cannot decide among them. Begin with a cross-tabulation, not one summary coefficient.

For two categorical annotators, observed agreement \(p_o\) is the fraction of paired labels that match. Cohen's kappa uses the agreement \(p_e\) implied by the two empirical marginal label frequencies:

\[
\kappa=\frac{p_o-p_e}{1-p_e},\qquad
p_e=\sum_c p_{A,c}p_{B,c}.
\]

The correction defines a reference model. It does not mean that people literally guess independently according to their observed marginals. A large kappa is evidence about agreement under that convention, not proof that the labels represent the intended scientific construct.

If both reviewers assign the same category to every item, observed agreement is one and the denominator is zero. Kappa is undefined in that degenerate table. Returning one would conceal the absence of variation; returning zero would invent disagreement. The program raises an explicit error and reports the raw agreement separately.

## Worked case A: calculate the complete table

For labels `[1,1,0,0]` and `[1,0,0,0]`, observed agreement is three quarters. The first annotator's positive frequency is one half and the second's is one quarter, so expected agreement is one half. Kappa is therefore one half. The result follows from the table rather than an arbitrary threshold label such as good or bad.

The second comparison retains a 90% raw agreement while changing marginal prevalence. Kappa changes because its reference agreement changes. When comparing studies, inspect the sample composition, category prevalence and annotation protocol before interpreting a difference in coefficients as better annotator training.

```python
import numpy as np


def agreement(a, b):
    if len(a) != len(b) or not a:
        raise ValueError("Paired nonempty labels required")
    categories = sorted(set(a) | set(b))
    n = len(a)
    table = np.zeros((len(categories), len(categories)), dtype=int)
    positions = {c: i for i, c in enumerate(categories)}
    for x, y in zip(a, b, strict=True):
        table[positions[x], positions[y]] += 1
    observed = float(np.trace(table) / n)
    expected = float((table.sum(0) / n) @ (table.sum(1) / n))
    if np.isclose(expected, 1):
        raise ValueError("Kappa undefined without marginal variation")
    return observed, (observed - expected) / (1 - expected), table


def ordinal_disagreement(a, b, levels=3):
    if levels < 2 or len(a) != len(b) or not a:
        raise ValueError("Invalid ordinal design")
    if any(type(x) is not int or not 0 <= x < levels for x in a + b):
        raise ValueError("Invalid category")
    return float(np.mean([(x - y) ** 2 / (levels - 1) ** 2 for x, y in zip(a, b, strict=True)]))


def worked_a():
    observed, kappa, table = agreement([1, 1, 0, 0], [1, 0, 0, 0])
    assert observed == 0.75 and kappa == 0.5
    assert table.tolist() == [[2, 0], [1, 1]]
    _, balanced, _ = agreement([0] * 5 + [1] * 5, [0] * 4 + [1] * 6)
    _, rare, _ = agreement([0] * 9 + [1], [0] * 10)
    assert np.isclose(balanced, 0.8) and np.isclose(rare, 0)
    print("Observed agreement:", observed, "kappa:", kappa, "table:", table.tolist())


worked_a()
```

## Worked case B: distance matters for ordinal labels

A level 0 versus level 2 disagreement may be more serious than level 1 versus level 2. An ordinal disagreement measure can assign squared distance normalized by the square of the maximum category gap. This example computes the observed weighted disagreement only. It does not silently call that quantity weighted kappa, which would additionally need its own marginal-based expected disagreement.

```python
import numpy as np


def agreement(a, b):
    if len(a) != len(b) or not a:
        raise ValueError("Paired nonempty labels required")
    categories = sorted(set(a) | set(b))
    n = len(a)
    table = np.zeros((len(categories), len(categories)), dtype=int)
    positions = {c: i for i, c in enumerate(categories)}
    for x, y in zip(a, b, strict=True):
        table[positions[x], positions[y]] += 1
    observed = float(np.trace(table) / n)
    expected = float((table.sum(0) / n) @ (table.sum(1) / n))
    if np.isclose(expected, 1):
        raise ValueError("Kappa undefined without marginal variation")
    return observed, (observed - expected) / (1 - expected), table


def ordinal_disagreement(a, b, levels=3):
    if levels < 2 or len(a) != len(b) or not a:
        raise ValueError("Invalid ordinal design")
    if any(type(x) is not int or not 0 <= x < levels for x in a + b):
        raise ValueError("Invalid category")
    return float(np.mean([(x - y) ** 2 / (levels - 1) ** 2 for x, y in zip(a, b, strict=True)]))


def worked_b():
    adjacent = ordinal_disagreement([0, 1, 2], [1, 1, 2])
    distant = ordinal_disagreement([0, 1, 2], [2, 1, 2])
    assert np.isclose(adjacent, 1 / 12) and np.isclose(distant, 1 / 3)
    print("Observed ordinal disagreement:", adjacent, distant)


worked_b()
```

## From coefficients to a useful study

Report the paired count, missing-label policy, confusion matrix, marginal proportions and uncertainty. If prompts share families, bootstrap families when that is the sampling unit. Resampling individual labels as if repeated variants were independent can make the interval too narrow. With very few families, a numerical bootstrap interval is weak evidence regardless of how many resamples are requested.

For more than two reviewers or varying missingness, other reliability coefficients use different coincidence or variance models. Krippendorff's alpha can accommodate incomplete annotation designs with a declared distance function; an intraclass correlation may fit continuous measurements under an appropriate random-effects model. These names are not interchangeable, and this unit does not implement those estimators. Read their assumptions before selecting one.

## Diagnose validity separately

Imagine both reviewers label every answer containing a citation marker as supported. Their agreement could be perfect while both are wrong about actual entailment. Validate the rubric using calibrated evidence and counterexamples. Conversely, adjudication can create one final label while leaving genuine uncertainty about ambiguous items. Retain the original labels and reasons so downstream analyses can examine sensitivity to disputed cases.

When the cost of an error is asymmetric, review the kinds of disagreements rather than only their frequency. A missed unsupported claim and a harmless formatting disagreement may need different follow-up even if they count equally in kappa. The reference programs establish arithmetic, category validation and a degeneracy policy on authored labels, not a universal standard for human reliability.


## Six investigations

### 1. Reconstruct the confusion table

Rebuild the table in case A by counting label pairs.

**Expected:** Rows A and columns B give [[2,0],[1,1]].

**Hint:** Keep the category order 0,1.

### 2. Perfect variation

Use labels 0,1 from both annotators.

**Expected:** Kappa equals 1.

**Hint:** Expected agreement is 0.5.

### 3. Complete disagreement

Pair 0,1 with 1,0.

**Expected:** Kappa equals -1.

**Hint:** Observed agreement is 0 and expected agreement is 0.5.

### 4. Single-category degeneracy

Give both reviewers only label 1.

**Expected:** Kappa is undefined and rejected.

**Hint:** Its denominator is 1 minus expected agreement.

### 5. Distinguish weighted quantities

Compare observed ordinal disagreement to weighted kappa.

**Expected:** The implemented quantity lacks an expected-disagreement correction.

**Hint:** List numerator and denominator for each definition.

### 6. Change the dependence unit

Annotate ten paraphrases from each of two families.

**Expected:** The evaluation still has two sampled families.

**Hint:** Count independent groups, not annotation cells.

## Primary references

- [Cohen kappa API and definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html)
- [Statistical inference foundations](../../../courses/statistics-ml/chapters/08-estimation-and-statistical-inference.md)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
