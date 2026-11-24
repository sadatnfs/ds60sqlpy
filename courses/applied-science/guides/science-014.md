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

## Key terms

- **Pairwise logistic objective:** The BPR-style loss log(1 + exp(-d^T w)) on positive-minus-negative feature differences, plus an L2 penalty.
- **Preference pair:** A positive and a negative item for one context; an unobserved item is not automatically a known negative.
- **Negative sampling:** The rule that chooses which unobserved items become negatives, which defines what the training comparison means.
- **Temporal leakage:** Use of information from after the training cutoff, for example through item statistics or an index built from future interactions.

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

## Worked example: BPR gradient check and leakage-free negatives

```python
import numpy as np

u = np.array([0.5, -0.2])
items = {"p": np.array([0.4, 0.1]), "n": np.array([-0.3, 0.6])}


def loss(u):
    s = u @ (items["p"] - items["n"])
    return np.log1p(np.exp(-s))


s = u @ (items["p"] - items["n"])
analytic = -(1 / (1 + np.exp(s))) * (items["p"] - items["n"])
h = 1e-6
numeric = np.array([(loss(u + h * e) - loss(u - h * e)) / (2 * h) for e in np.eye(2)])
print("score difference:", round(float(s), 4), " loss:", round(float(loss(u)), 6))
print("analytic grad:", analytic.round(6), " numeric grad:", numeric.round(6))

events = [("u1", "p", 1), ("u1", "q", 3), ("u1", "r", 6)]  # (user, item, day)
catalog = {"p", "q", "r", "s", "t"}
cutoff = 2
ever = {i for _, i, _ in events}
seen_by_cutoff = {i for _, i, day in events if day <= cutoff}
print("negatives if future is excluded:", sorted(catalog - ever))
print("negatives using only past positives:", sorted(catalog - seen_by_cutoff))
```

Observed output:

```text
score difference: 0.45  loss: 0.493249
analytic grad: [-0.272553  0.19468 ]  numeric grad: [-0.272553  0.19468 ]
negatives if future is excluded: ['s', 't']
negatives using only past positives: ['q', 'r', 's', 't']
```

The BPR loss for one triple is \(\log(1+e^{-s})\) where \(s\) is the score of the positive item minus the negative item, here 0.45, giving 0.493249. The analytic gradient with respect to the user vector is \(-\sigma(-s)(v_p-v_n)\). With \(v_p-v_n=(0.7,-0.5)\) and \(\sigma(-0.45)=0.3894\) that is \((-0.2726, 0.1947)\), and the central finite difference agrees to six decimals. Agreement at this one point justifies trusting the analytic gradient in a training loop; a sign error would show up immediately as opposite signs. The sampling lines show leakage. With a training cutoff at day 2, the user has only interacted with p. Excluding every item the user ever touched removes q and r, which leaks the future: the training set now knows those items will become positives. Sampling from the catalog minus past positives keeps q and r as legitimate negatives, which is what an online system would have seen on day 2.

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
