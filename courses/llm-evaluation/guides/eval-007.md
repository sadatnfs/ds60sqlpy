# eval-007: Multiplicity and sequential release decisions

## Starting point and outcome

Intermediate; approximately 120 minutes. Direct prerequisites: `eval-006`.

Prespecify a family of comparisons and monitoring times, calculate conservative error control, and separate statistical evidence from release policy.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-007`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## A collection of tests is one decision procedure

An evaluation often compares several models, prompts, datasets and metrics. It may also be inspected repeatedly while labels arrive. A per-test threshold does not describe the error behavior of the whole procedure. The relevant family should follow the claims and decisions being made, not whichever grouping produces the smallest adjustment.

For events \(E_j\) representing false rejections, the union bound gives

\[
P\left(\bigcup_{j=1}^{m}E_j\right)\leq\sum_{j=1}^{m}P(E_j).
\]

If each fixed analysis uses a valid p-value under its null and thresholds \(\alpha_j\) have a prespecified sum at most \(\alpha\), this controls the probability of at least one false rejection in that family. Independence is not required for the bound. Validity of the individual tests is still required: adjustment does not repair data leakage, a wrong sampling unit or a post-hoc hypothesis invented from the final labels.

A threshold-crossing event is also different from a decision to deploy. An improvement too small to matter can be statistically detectable, while an uncertain critical-risk condition may still block a release. Retain effect sizes, practical margins, uncertainty and operational gates separately.

## Worked case A: three opportunities for a false alarm

For three independent continuous uniform p-values under their nulls, testing each at 0.05 gives a family error probability of \(1-0.95^3\), approximately 0.143. Equal Bonferroni allocation uses 0.05 divided by three and has a probability below 0.05 in this independent illustration. Real repeated looks at accumulating data are correlated; the independent calculation is an explanatory contrast, not their exact operating characteristic.

The decision function below uses the declared number of hypotheses even if one p-value is missing. Reducing the family size after excluding an inconvenient result would change the procedure. Missing assessments remain explicit and cannot be interpreted as passed conditions.

```python
import numpy as np


def bonferroni(pvalues, alpha=0.05):
    p = np.asarray(pvalues, float)
    if (
        not len(p)
        or np.any(p < 0)
        or np.any(p > 1)
        or not np.isfinite(p).all()
        or not 0 < alpha < 1
    ):
        raise ValueError("Invalid p-value family")
    return p <= alpha / len(p)


def spent_decisions(pvalues, budgets, alpha=0.05):
    p = np.asarray(pvalues, float)
    a = np.asarray(budgets, float)
    if (
        p.ndim != 1
        or p.shape != a.shape
        or not 0 < alpha < 1
        or not p.size
        or not np.isfinite(p).all()
        or not np.isfinite(a).all()
        or np.any(p < 0)
        or np.any(p > 1)
        or np.any(a < 0)
        or a.sum() > alpha + 1e-12
    ):
        raise ValueError("Invalid declared monitoring plan")
    return p <= a


def worked_a():
    unadjusted = 1 - (1 - 0.05) ** 3
    adjusted = 1 - (1 - 0.05 / 3) ** 3
    assert np.isclose(unadjusted, 0.142625) and adjusted < 0.05
    assert bonferroni([0.01, 0.03, 0.2]).tolist() == [True, False, False]
    print("Independent three-test family error:", unadjusted, "adjusted:", adjusted)


worked_a()
```

## Worked case B: spending across declared looks

The second case allocates 0.01,0.015 and 0.025 to three fixed monitoring times. Their sum is 0.05. A p-value of 0.02 at the first look does not cross its allocated threshold, even though it is below 0.05. The same p-value can cross the third threshold under this declared rule. This is a conservative spending example, not an implementation of an always-valid confidence sequence.

```python
import numpy as np


def bonferroni(pvalues, alpha=0.05):
    p = np.asarray(pvalues, float)
    if (
        not len(p)
        or np.any(p < 0)
        or np.any(p > 1)
        or not np.isfinite(p).all()
        or not 0 < alpha < 1
    ):
        raise ValueError("Invalid p-value family")
    return p <= alpha / len(p)


def spent_decisions(pvalues, budgets, alpha=0.05):
    p = np.asarray(pvalues, float)
    a = np.asarray(budgets, float)
    if (
        p.ndim != 1
        or p.shape != a.shape
        or not 0 < alpha < 1
        or not p.size
        or not np.isfinite(p).all()
        or not np.isfinite(a).all()
        or np.any(p < 0)
        or np.any(p > 1)
        or np.any(a < 0)
        or a.sum() > alpha + 1e-12
    ):
        raise ValueError("Invalid declared monitoring plan")
    return p <= a


def worked_b():
    flags = spent_decisions([0.02, 0.02, 0.02], [0.01, 0.015, 0.025])
    assert flags.tolist() == [False, False, True]
    print("Declared-look crossings:", flags.tolist())


worked_b()
```

## What optional stopping changes

A fixed-sample p-value evaluated only at a prespecified sample size has a different interpretation from the smallest p-value seen across arbitrary stopping times. You may use a valid group-sequential design, a confidence sequence, an e-process or another method whose assumptions match continuous monitoring. The choice must be made and explained before its favorable result is used. Repeatedly applying an ordinary test until it passes is not such a method.

Do not mix a rule calibrated for cumulative data with a sequence of independently selected subsets without reviewing its assumptions. Similarly, observing early outcomes can affect later enrollment, exposure or annotation. That feedback can change the population and invalidate an analysis that assumed a fixed, unaffected sampling process.

## Diagnosis and transfer

Start a release notebook by listing all candidate models, primary and secondary metrics, error-control goals, look times and practical thresholds. Classify exploratory findings honestly and reserve independent data for confirmation. A useful discovery can motivate a later study without being relabeled as a prespecified success.

The programs enforce bounded probabilities and explicit budgets. They demonstrate arithmetic and decision logic on authored p-values; they do not manufacture a valid p-value for an LLM benchmark. The paired and clustered methods from the previous unit still need the appropriate null and dependence assumptions. Preserve the entire monitoring history so a reviewer can reconstruct why the decision was made.


## Six investigations

### 1. One comparison

Test one valid p-value 0.05 at alpha 0.05.

**Expected:** The declared non-strict rule rejects.

**Hint:** State whether equality is included.

### 2. Three equal findings

Use p-values 0.02,0.02,0.02.

**Expected:** None crosses equal Bonferroni thresholds.

**Hint:** Each allocation is approximately 0.0167.

### 3. Overspend the budget

Allocate 0.03 and 0.03 while total alpha is 0.05.

**Expected:** The monitoring plan is rejected.

**Hint:** Validate budgets before observing results.

### 4. Specify dependent looks

Explain whether the union bound requires independent tests.

**Expected:** It does not; individual error bounds still need to hold.

**Hint:** Separate the bound from the illustrative independent calculation.

### 5. Unknown result

Replace a p-value with NaN.

**Expected:** The decision function rejects it.

**Hint:** Do not silently drop the row and reduce the family.

### 6. Separate value from significance

A precise improvement is below the minimum useful effect.

**Expected:** The statistical result alone does not mandate deployment.

**Hint:** Use a declared practical margin and independent safety gates.

## Primary references

- [Existing sequential and multiplicity chapter](../../../courses/statistics-ml/chapters/10-multiple-testing-sequential-inference-and-selective-inference.md)
- [SciPy exact binomial test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
