# science-014: Pairwise learned ranking and defensible negative sampling

Tutorial mode. Stage: intermediate. Direct prerequisites: `science-013`, `statistics-learning-003`.

## A pairwise objective encodes a comparison

Pairwise ranking learns that one item should score above another for a given context. A pair should therefore have a defensible interpretation. A positive historical interaction and an unobserved item do not automatically form a known preference pair. Exposure, observation windows and sampling policy determine what the training comparison means.

For a linear score \(s(x)=\mathbf w^{\mathsf T}x\), let \(d=x^+-x^-\) be a positive-minus-negative feature difference. A regularized pairwise logistic objective is

\[
\mathcal L(\mathbf w)=\frac{1}{n}\sum_i\log\{1+\exp(-d_i^{\mathsf T}\mathbf w)\}
+\frac{\lambda}{2}\|\mathbf w\|^2.
\]

The implementation uses `logaddexp` for the loss and the logistic function for its gradient. Computing a naive exponential at a very large margin can overflow even when the mathematical loss is finite. Numerical stability is part of a correct implementation, but it does not validate the sampled comparisons.

## Worked case 1: learn and independently check the gradient

Three synthetic pair differences have known positive directions. Starting from zero weights gives equal scores and a loss near the logarithm of two. Gradient descent lowers the objective and makes every training margin positive. The code verifies both properties.

An independent central finite-difference calculation checks each gradient component at the fitted weight vector. This compares the analytic derivative with the actual implemented scalar objective. It would catch a reversed pair sign, omitted regularization term or incorrect averaging factor. The step size is small enough for this smooth, moderate-scale fixture; a finite-difference check itself can fail numerically at unsuitable scales or nondifferentiable points.

The learned weights are not probabilities of user preference unless a suitable probabilistic interpretation and calibration procedure are established. They produce scores under a particular training objective. A lower training loss also does not establish better ranking on new users, items or time periods.

## Worked case 2: a future positive is not a known negative

The second fixture contains four exposures and two positive events, each with an availability time. At cutoff five, only the first positive is known. The sampler requires a three-unit attribution window plus a declared two-unit maximum reporting delay before treating an exposed item as a candidate negative. It therefore admits only i3. At cutoff nine, i3 and i4 are eligible, while the delayed positive for i2 has arrived and excludes that item. Merely subtracting currently known positives from the catalog would incorrectly label immature exposures as negatives.

This example separates two uncertainties: whether an item was exposed and whether its response window has matured. A defensible negative-sampling scheme might sample from displayed-but-unclicked items after an explicit attribution window, or it might treat unobserved items as noisy negatives under a stated learning objective. Those are different assumptions, not interchangeable labels.

Changing the negative-sampling distribution changes which comparisons dominate learning. Popular-item negatives, hard negatives and uniformly sampled items can lead to different objectives and different evaluation behavior. A harder training task is not automatically a more valid one. Keep the sampling mechanism reproducible and evaluate against the intended serving candidate set.

## Design evaluation around queries and time

Ranking metrics are usually defined per query or user context. Resampling individual item rows can break those groups and produce overly optimistic uncertainty. Preserve the query unit when comparing models, and account for repeated users or correlated sessions when those structures matter.

Split before feature construction, candidate mining and hyperparameter choice. A model can leak test information through vocabulary, item statistics, hard-negative mining or an index built from future interactions, even when its final fitting function sees only training labels. Record the entire procedure being evaluated.

A system may need constraints on diversity, eligibility, repetition or provider exposure. Adding those constraints after optimizing a pairwise model changes the delivered ranking. Evaluate the resulting combined policy, not only the unconstrained scorer. Business utility, safety and calibration should be reviewed alongside relevance metrics.

## Answered scientific discussion

**Does a positive margin for every training pair prove the recommendation is good?** It proves that the supplied comparisons are ordered in-sample. Those comparisons may be biased, sparse or unrepresentative, and their features may not be available at serving time.

**Why compare a gradient with finite differences when an autodiff library is available?** A finite-difference check can validate the intended objective and reduction against an independent calculation. Autodiff faithfully differentiates the program supplied to it, including an incorrectly signed or incorrectly weighted objective.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import special


def bpr_loss_gradient(weights, differences, penalty=0.01):
    w = np.asarray(weights, float)
    d = np.asarray(differences, float)
    margin = d @ w
    loss = float(np.logaddexp(0, -margin).mean() + penalty * (w @ w) / 2)
    grad = -(d * special.expit(-margin)[:, None]).mean(axis=0) + penalty * w
    return loss, grad


def negative_candidates(exposures, positives, cutoff, window, max_reporting_lag):
    if window < 0 or max_reporting_lag < 0:
        raise ValueError("Attribution and reporting bounds must be nonnegative")
    result = []
    for item, exposed in exposures:
        if exposed + window + max_reporting_lag > cutoff:
            continue
        positive = any(
            observed_item == item
            and exposed <= event_time <= exposed + window
            and available <= cutoff
            for observed_item, event_time, available in positives
        )
        if not positive:
            result.append(item)
    return result


def run_cases():
    d = np.array([[1.0, 0.0], [2.0, 1.0], [1.0, -1.0]])
    w = np.zeros(2)
    initial = bpr_loss_gradient(w, d)[0]
    for _ in range(200):
        w -= 0.1 * bpr_loss_gradient(w, d)[1]
    loss, gradient = bpr_loss_gradient(w, d)
    assert loss < initial and np.all(d @ w > 0)
    h = 1e-5
    numeric = []
    for j in range(2):
        shift = np.eye(2)[j] * h
        numeric.append(
            (bpr_loss_gradient(w + shift, d)[0] - bpr_loss_gradient(w - shift, d)[0]) / (2 * h)
        )
    assert np.allclose(gradient, numeric, atol=1e-8)
    # A future click is not a verified negative at the earlier ranking time.
    exposures = [("i1", 0), ("i2", 4), ("i3", 0), ("i4", 1)]
    positives = [("i1", 1, 2), ("i2", 6, 8)]
    known_positive = {item for item, event_time, available in positives if available <= 5}
    negatives = negative_candidates(exposures, positives, 5, 3, 2)
    assert "i2" not in known_positive and negatives == ["i3"]
    assert negative_candidates(exposures, positives, 9, 3, 2) == ["i3", "i4"]
    return dict(
        initial_loss=initial, trained_loss=loss, weights=w.tolist(), margins=(d @ w).tolist()
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-014 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Rendle and colleagues, Bayesian Personalized Ranking](https://arxiv.org/abs/1205.2618)
- [Dudik and colleagues, doubly robust policy evaluation](https://arxiv.org/abs/1103.4601)
