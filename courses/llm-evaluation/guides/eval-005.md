# eval-005: Stratified sampling and population weighting

## Starting point and outcome

Beginner; approximately 120 minutes. Direct prerequisites: `eval-001`, `eval-002`.

Estimate a declared target mixture from an intentionally balanced evaluation and diagnose overlap and weight concentration.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-005`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Sampling for precision changes the observed mix

Rare but consequential questions deserve enough evaluation cases to reveal failures. A balanced test can therefore oversample a rare stratum relative to future traffic. Its unweighted average describes the balanced sample, not the deployment mixture. This is not a defect in sampling when the estimator and report preserve the distinction.

Let stratum \(h\) have target weight \(W_h\), with nonnegative weights summing to one, and estimated mean correctness \(\bar{C}_h\). The stratified target estimate is

\[
\widehat{\mu}=\sum_h W_h\bar{C}_h.
\]

If the sample draws independently within every stratum, its sampling variance depends on the within-stratum variability and sample sizes. A population weight is not the same as an inverse inclusion-probability weight for an arbitrary sampling design. In particular, overlapping sampling frames or repeated users need more than a two-column weight lookup.

## Worked case A: a balanced sample, an unequal target

The authored test has equal numbers of routine and rare requests. Accuracy is 0.9 in the routine stratum and 0.5 in the rare stratum. Its unweighted mean is 0.7. For a target population that is 90% routine and 10% rare, the target estimate is 0.86. Reporting both numbers is informative: the first describes this test design, and the second applies the specified deployment mixture.

Changing the rare-stratum weight to one half returns 0.7. Neither weight choice should be selected after seeing which produces a favorable model ranking. Fix the target population before comparison, retain stratum-level results, and check whether the intended traffic mix is stable over time.

```python
import numpy as np


def target_mean(means, weights):
    if set(means) != set(weights) or not means:
        raise ValueError("Every target stratum needs data")
    w = np.array(list(weights.values()), float)
    if not np.isfinite(np.asarray(list(means.values()), float)).all():
        raise ValueError("Finite stratum means required")
    if np.any(w < 0) or not np.isfinite(w).all() or not np.isclose(w.sum(), 1):
        raise ValueError("Invalid population weights")
    return sum(weights[h] * means[h] for h in weights)


def inclusion_estimates(y, probability, population_size):
    y = np.asarray(y, float)
    p = np.asarray(probability, float)
    if (
        y.shape != p.shape
        or not y.size
        or np.any(p <= 0)
        or np.any(p > 1)
        or not np.isfinite(p).all()
        or population_size <= 0
    ):
        raise ValueError("Invalid inclusion design")
    weights = 1 / p
    return (
        float(np.sum(weights * y) / population_size),
        float(np.sum(weights * y) / weights.sum()),
        float(weights.sum() ** 2 / np.sum(weights**2)),
    )


def worked_a():
    means = {"routine": 0.9, "rare": 0.5}
    estimate = target_mean(means, {"routine": 0.9, "rare": 0.1})
    assert np.isclose(estimate, 0.86)
    assert np.isclose(target_mean(means, {"routine": 0.5, "rare": 0.5}), 0.7)
    print("Target estimate:", estimate, "balanced sample mean:", 0.7)


worked_a()
```

## Worked case B: inclusion weights and overlap

When units have known inclusion probabilities, a Horvitz-Thompson total sums observed outcomes divided by those probabilities. Dividing by a known population size gives an estimated mean. A self-normalized weighted average instead divides by the sum of sampled weights; it generally has a different finite-sample behavior. The example calculates both using tiny enumerated inputs so the denominators remain visible.

A zero inclusion probability for a relevant target unit is an identification problem. No finite weight recovers outcomes never observable under the sampling design. Very small probabilities can produce extreme weights and high variance. The descriptive effective sample size \((\sum_i w_i)^2/\sum_i w_i^2\) diagnoses concentration, but it is not a universal count of independent observations or a replacement for a design-based variance estimator.

```python
import numpy as np


def target_mean(means, weights):
    if set(means) != set(weights) or not means:
        raise ValueError("Every target stratum needs data")
    w = np.array(list(weights.values()), float)
    if not np.isfinite(np.asarray(list(means.values()), float)).all():
        raise ValueError("Finite stratum means required")
    if np.any(w < 0) or not np.isfinite(w).all() or not np.isclose(w.sum(), 1):
        raise ValueError("Invalid population weights")
    return sum(weights[h] * means[h] for h in weights)


def inclusion_estimates(y, probability, population_size):
    y = np.asarray(y, float)
    p = np.asarray(probability, float)
    if (
        y.shape != p.shape
        or not y.size
        or np.any(p <= 0)
        or np.any(p > 1)
        or not np.isfinite(p).all()
        or population_size <= 0
    ):
        raise ValueError("Invalid inclusion design")
    weights = 1 / p
    return (
        float(np.sum(weights * y) / population_size),
        float(np.sum(weights * y) / weights.sum()),
        float(weights.sum() ** 2 / np.sum(weights**2)),
    )


def worked_b():
    ht, sn, ess = inclusion_estimates([1, 0], [0.5, 0.25], 10)
    assert np.isclose(ht, 0.2) and np.isclose(sn, 1 / 3) and np.isclose(ess, 1.8)
    assert inclusion_estimates([1, 0], [1, 1], 2) == (0.5, 0.5, 2.0)
    print("Known-N mean:", ht, "self-normalized mean:", sn, "weight ESS:", ess)


worked_b()
```

## Assumptions and uncertainty

To generalize a stratified sample, the observed cases within each stratum must represent the relevant target cases under the stated design or model. If difficult rare requests were excluded during labeling, correct top-level weights do not repair that within-stratum selection. If target weights are estimated rather than known, their uncertainty should be reflected in the final analysis.

Use the same target weights when comparing two systems. Pair their outcomes by eligible request, preserve failures, and then aggregate the paired differences. Evaluating A on one traffic mix and B on another conflates model changes with composition changes. A request, a user and a question family can also have different target weights; name which one your estimator represents.

## Practical diagnosis

Inspect support before calculating weighted metrics. Every positive target stratum needs observed data, and every supplied inclusion probability must be in the interval from zero to one with zero excluded. Print the largest weights and sensitivity to a defensible alternative target mixture. Trimming weights can reduce variance but changes the estimator and may introduce bias; it is a policy requiring explanation rather than a cosmetic cleanup step.

The synthetic examples verify arithmetic and invalid-input behavior. They do not estimate live traffic weights. In a real evaluation, document the sampling frame, exclusions, clustering, known population totals and any model used to fill coverage gaps. Keep separate worst-case or critical-risk criteria when average population utility would underweight rare severe failures.


## Six investigations

### 1. Change the mixture

Use 25% routine and 75% rare in case A.

**Expected:** Target accuracy is 0.6.

**Hint:** Multiply each mean by its target weight.

### 2. Expose missing support

Give positive target weight to an unobserved stratum.

**Expected:** The estimator rejects the mismatch.

**Hint:** Missing support cannot be repaired with normalization.

### 3. Compare denominators

Explain why the two weighted means in case B differ.

**Expected:** \(0.2\) uses the known population size \(N=10\); \(1/3\) uses the sampled weight sum \(6\).

**Hint:** Write both fractions explicitly.

### 4. Increase weight concentration

Use inclusion probabilities 0.01 and 1.

**Expected:** The diagnostic ESS is below 1.03.

**Hint:** Compute weights 100 and 1.

### 5. Audit zero probability

Set one inclusion probability to zero.

**Expected:** The calculation must fail.

**Hint:** The inverse weight is undefined.

### 6. Compare systems fairly

Use a common family/stratum ledger to compare A and B.

**Expected:** Both estimates use identical eligible IDs and target weights.

**Hint:** Separate composition from model effects.

## Primary references

- [Horvitz and Thompson: unequal-probability sampling](https://www.tandfonline.com/doi/abs/10.1080/01621459.1952.10483446)
- [Probability and sampling foundations](../../../courses/statistics-ml/chapters/03-probability-fundamentals-and-stochastic-processes.md)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
