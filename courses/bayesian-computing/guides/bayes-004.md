# bayes-004: Probability transformations and Jacobian accounting

Tutorial mode. Stage: beginner. Direct prerequisites: `bayes-002`.

## A density depends on its coordinate system

A change of variables preserves probability mass, not density height. If a constrained parameter \(\theta\) is represented through an unconstrained coordinate \(z\), the transformed density includes the absolute determinant of the transformation's derivative. Omitting it generally changes the distribution being sampled.

For \(\theta=\operatorname{logit}^{-1}(z)\), the derivative is \(d\theta/dz=\theta(1-\theta)\). Thus

\[
\log p_Z(z)=\log p_\Theta(\theta(z))
+\log\theta(z)+\log\{1-\theta(z)\}.
\]

The extra term is the log Jacobian. It is not a regularizer or an optional numerical adjustment. It is the probability-accounting term required when a density originally defined with respect to one coordinate is expressed with respect to another.

## Worked case 1: verify a transformed beta density

The target is Beta(2,2). The program evaluates a fine grid in log-odds coordinates, maps it to probabilities and includes the Jacobian. Numerical integration over the z grid gives total mass close to one. The implied second moment of theta is .3, agreeing with the analytic beta moment.

The logarithms of theta and one minus theta are computed with stable log-add-exp expressions. Directly evaluating a sigmoid near an extreme and then subtracting it from one can lose precision. The finite integration interval still truncates the tails, so the test uses a range and tolerance appropriate to this particular target.

A check of the transformed normalizer and a check of a parameter moment serve different purposes. A wrong density can always be renormalized. Matching an independently derived moment helps reveal that the transformed calculation represents the intended distribution rather than merely some normalized distribution.

## Worked case 2: omit the Jacobian deliberately

The second calculation uses the beta density evaluated at theta(z) but integrates it with respect to z without the derivative adjustment. After normalization, its implied theta distribution is uniform in this example, giving a second moment near one third instead of .3.

This is an exact conceptual failure despite apparently sensible code and finite values. For Beta(2,2), the original density contains a factor proportional to theta times one minus theta. Changing coordinates without the matching derivative cancels that shape when interpreted back on the probability scale. The example makes the error visible through an analytic moment rather than relying on the appearance of a histogram.

The error can be harder to detect in a complex model where no simple marginal moment is known. That is why a small transformed reference target is useful when testing a new parameterization or interface. A sampler can explore the wrong target efficiently and still produce attractive trace plots.

## Distinguish declared constraints from manual transformations

Probabilistic programming systems often transform declared constrained parameters internally and account for the corresponding Jacobians automatically. A user-defined transformation inside a model may require different treatment. Adding a Jacobian that the system already includes can be as incorrect as omitting one that is needed.

The later Stan tutorial contrasts a declared positive rate with a manually introduced unconstrained log rate. It keeps two independent copies of the same posterior to compare their implied parameter distributions. That computational comparison should not be confused with counting the same observed likelihood twice for one parameter.

Changing variables can also improve or worsen geometry. A mathematically correct Jacobian does not guarantee efficient sampling. A hierarchy can have strongly varying scales even after every density term is correct. Reparameterization and diagnostic review therefore complement probability accounting rather than replacing it.

## Answered scientific discussion

**Does a transformed deterministic prediction need a Jacobian in generated output?** Merely calculating a function of sampled parameters does not redefine the sampled density. A Jacobian is needed when changing the variables with respect to which the target density is represented.

**What should be written before implementing a transformation?** State the original density, the transformation, its domain, the reference measure and which transformations the inference system already handles. Then check a tractable case. The code here demonstrates that procedure for one one-dimensional transform.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import special, stats


def run_cases():
    z = np.linspace(-12, 12, 40001)
    theta = special.expit(z)
    log_beta = stats.beta.logpdf(theta, 2, 2)
    log_jacobian = -np.logaddexp(0, -z) - np.logaddexp(0, z)
    correct = np.exp(log_beta + log_jacobian)
    wrong = np.exp(log_beta)
    normalizer = float(np.trapezoid(correct, z))
    second_correct = float(np.trapezoid(theta**2 * correct, z) / normalizer)
    second_wrong = float(np.trapezoid(theta**2 * wrong, z) / np.trapezoid(wrong, z))
    assert np.isclose(normalizer, 1, atol=1e-8)
    assert np.isclose(second_correct, 0.3, atol=1e-6) and np.isclose(second_wrong, 1 / 3, atol=3e-5)
    assert second_wrong > second_correct
    return dict(
        transformed_normalizer=normalizer,
        correct_theta_second_moment=second_correct,
        omitted_jacobian_second_moment=second_wrong,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-004 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Stan reference manual, transforms and constraints](https://mc-stan.org/docs/reference-manual/)
