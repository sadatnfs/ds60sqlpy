# eval-006: Paired comparisons and clustered uncertainty

## Starting point and outcome

Intermediate; approximately 120 minutes. Direct prerequisites: `eval-004`, `eval-005`, `statistics-003`.

Compute paired and family-level uncertainty while distinguishing a randomization null, a bootstrap approximation and a deployment claim.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-006`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## Preserve the pairing and the dependence

Two systems should answer the same eligible requests when the goal is a paired comparison. For request \(i\), define \(d_i=C_{B,i}-C_{A,i}\). The average difference answers a paired question and can have lower variance than comparing two independent sample means because request difficulty affects both systems. Dropping a failed response from only one system breaks that pairing and can create selection bias.

Dependence remains after pairing. Ten paraphrases of one question can share nearly all their difficulty and evidence. If families are sampled independently, a family-level mean difference can be the appropriate resampling unit. Decide whether the target weights families equally or requests equally; aggregation and resampling must both match that estimand.

A paired sign-randomization calculation changes the sign of each difference under a null that permits swapping system assignments within the relevant units. For an observed statistic \(T\), an exact two-sided tail probability on a finite randomization space is the fraction of allowed assignments with \(|T^*|\geq |T|\). That null requires a justified exchangeability or randomization argument. An arbitrary observational pair of deployed systems is not automatically a randomized experiment.

## Worked case A: enumerate the small null

With paired differences `[1,1,1,-1]`, the observed mean is 0.5. Enumerating all 16 sign assignments produces the exact finite reference distribution. Ten assignments have an absolute mean at least 0.5, giving 0.625. This deliberately modest result shows why a favorable average is not equivalent to strong evidence against the stated null.

The code enumerates rather than simulates, so there is no Monte Carlo error. Enumeration does not remove sampling uncertainty, selection bias, invalid exchangeability or multiple-comparison problems. It only computes this small reference distribution exactly.

```python
from itertools import product

import numpy as np


def sign_test(differences):
    d = np.asarray(differences, float)
    if d.ndim != 1 or not 1 <= len(d) <= 16 or not np.isfinite(d).all():
        raise ValueError("Bounded finite pairs required")
    observed = abs(d.mean())
    null = np.array([np.mean(d * np.array(signs)) for signs in product((-1, 1), repeat=len(d))])
    p = float(np.mean(np.abs(null) >= observed - 1e-12))
    return p, null


def cluster_bootstrap(means):
    x = np.asarray(means, float)
    if x.ndim != 1 or not 1 <= len(x) <= 6 or not np.isfinite(x).all():
        raise ValueError("Bounded family means required")
    return np.array(
        [np.mean(x[list(indices)]) for indices in product(range(len(x)), repeat=len(x))]
    )


def worked_a():
    p, null = sign_test([1, 1, 1, -1])
    assert len(null) == 16 and p == 0.625
    assert sign_test([-1, -1, -1, 1])[0] == p
    print("Exact paired sign-reference tail:", p)


worked_a()
```

## Worked case B: a cluster bootstrap has limited information

Family means `[-1,1]` give an equal-family mean of zero. Drawing two families with replacement yields only the means-1,0,1, with probabilities one quarter, one half and one quarter. Using the empirical inverse-CDF quantile rule, the central 95% interval spans -1 to 1. Adding repeated rows within a family cannot create new independent families.

The case also contrasts the variance of row differences with the variability of family means. A narrow row-level interval can be misleading when the repeated rows share common causes. Conversely, aggregating to families changes the weighting if families have unequal sizes. Neither method is universally correct; the data-generating and sampling assumptions determine the choice.

```python
from itertools import product

import numpy as np


def sign_test(differences):
    d = np.asarray(differences, float)
    if d.ndim != 1 or not 1 <= len(d) <= 16 or not np.isfinite(d).all():
        raise ValueError("Bounded finite pairs required")
    observed = abs(d.mean())
    null = np.array([np.mean(d * np.array(signs)) for signs in product((-1, 1), repeat=len(d))])
    p = float(np.mean(np.abs(null) >= observed - 1e-12))
    return p, null


def cluster_bootstrap(means):
    x = np.asarray(means, float)
    if x.ndim != 1 or not 1 <= len(x) <= 6 or not np.isfinite(x).all():
        raise ValueError("Bounded family means required")
    return np.array(
        [np.mean(x[list(indices)]) for indices in product(range(len(x)), repeat=len(x))]
    )


def worked_b():
    distribution = cluster_bootstrap([-1, 1])
    assert distribution.tolist() == [-1.0, 0.0, 0.0, 1.0]
    np.testing.assert_allclose(np.quantile(distribution, [0.025, 0.975]), [-0.925, 0.925])
    # Observed support endpoints remain -1 and 1; interpolated percentiles differ.
    assert np.quantile(distribution, [0.025, 0.975], method="inverted_cdf").tolist() == [-1.0, 1.0]
    print("Family resample support:", distribution.tolist())


worked_b()
```

## Interpret uncertainty without changing its target

A bootstrap interval is conditional on the observed sample and the resampling design. With two families it has little ability to describe unseen family heterogeneity. More resamples only estimate the same empirical distribution more accurately. More independently sampled families provide new information. Distinguish these two kinds of additional work when planning an evaluation budget.

Report the number of pairs, family sizes, pairing losses and the complete interval construction. State whether the interval is percentile, basic, BCa or based on another approximation. Automatic software defaults are part of the analysis specification. If some categories have zero eligible observations, a bootstrap cannot manufacture their outcomes.

## Error diagnosis and scientific transfer

Check a few paired differences manually and then reconstruct the aggregate from the stored ledger. A nonzero difference between a row mean and a family mean can be a valid consequence of weights, not a numerical defect. An interval that changes dramatically when a single family is removed is evidence of limited independent support.

For an actual assistant comparison, retain both outputs, label versions, task families and the system-selection protocol. Use a held-out final set after choosing prompts and thresholds. The calculations here are tests of a finite authored case; a deployment conclusion also needs representative sampling, justified labeling and separate critical-risk evidence.


## Six investigations

### 1. All differences vanish

Use paired differences 0,0.

**Expected:** The exact tail probability is 1.

**Hint:** Every allowed statistic equals the observed statistic.

### 2. Four favorable pairs

Use differences 1,1,1,1.

**Expected:** The two-sided exact tail is 2/16=0.125.

**Hint:** Count both all-positive and all-negative assignments.

### 3. Reverse model labels

Negate every difference in case A.

**Expected:** The two-sided p-value is unchanged.

**Hint:** Absolute extremeness is symmetric.

### 4. State the quantile convention

Compare linear interpolation with empirical inverse-CDF percentiles in case B.

**Expected:** Linear endpoints are approximately +/-0.925; inverse-CDF endpoints are +/-1.

**Hint:** A discrete bootstrap distribution needs an explicit quantile rule.

### 5. Add a third family

Enumerate resamples of 0,1,2.

**Expected:** There are 27 ordered draws of three families.

**Hint:** Each of three positions has three choices.

### 6. Bound an exact algorithm

Request 17 paired differences.

**Expected:** The fixture rejects the request.

**Hint:** Enumeration grows exponentially.

## Primary references

- [SciPy paired permutation tests](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html)
- [SciPy bootstrap conventions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
