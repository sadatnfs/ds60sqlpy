# bayes-001: Generative questions, conditioning and repeated evidence

Tutorial mode. Stage: beginner. Direct prerequisites: `statistics-003`.

## Begin with a generative question

Bayesian inference conditions a probability model on observations. The model describes possible unknown states and how observations arise under each state. A prior describes uncertainty before the specified evidence; a likelihood describes the observation mechanism. Their product is normalized to obtain a posterior. These ingredients should be explained in the language of the scientific question before they become library calls.

For a finite set of hypotheses \(H_j\) and evidence \(E\),

\[
P(H_j\mid E)=\frac{P(E\mid H_j)P(H_j)}{\sum_kP(E\mid H_k)P(H_k)}.
\]

The denominator is the model's probability of the evidence. It is not an arbitrary scaling constant when comparing models, although posterior ratios within one fixed model can often avoid calculating it explicitly. A posterior probability is conditional on the supplied model, including its hypothesis set and observation process.

## Key terms

- **Generative model:** A probability description of the possible unknown states and of how observations arise under each state.
- **Prior:** The probability assigned to each hypothesis before the specified evidence is conditioned on.
- **Likelihood ratio:** The probability of the evidence under one hypothesis divided by its probability under another; it multiplies prior odds to give posterior odds.
- **Conditional independence:** Independence of two signals given the hypothesis, which is required before their likelihoods may be multiplied as separate evidence.

## Worked case 1: update a fault-detector hypothesis

The synthetic hypotheses are normal operation and a fault, with prior probabilities .8 and .2. A positive signal has probabilities .1 and .9 under those hypotheses. The posterior fault probability is \(.18/(.08+.18)=9/13\), about .692. A 90% sensitivity-like number alone would not provide this posterior because the baseline prevalence and false-positive behavior also matter.

The program validates matching hypothesis shapes, normalized nonnegative prior mass and finite likelihood values. If the model assigns zero probability to the evidence under every hypothesis, normalization is impossible. Replacing the zero with an epsilon would conceal a model failure rather than provide a principled update.

Posterior odds provide a second independent calculation. Prior odds .25 are multiplied by a likelihood ratio of nine, yielding posterior odds 2.25. Converting those odds to a probability returns the same 9/13. This is a useful check of ordering and of which hypothesis belongs in the numerator.

## Worked case 2: repeated evidence is not automatically new evidence

If two signals are conditionally independent given the hypothesis, their likelihoods multiply. The posterior fault probability becomes 81/85, approximately .953. If the second signal is instead a perfect duplicate of the first recorded signal, it supplies no new information and the posterior remains 9/13.

Both calculations can be implemented without a software error. The difference is the dependence assumption. A duplicated database row, a cached model response or two metrics derived from the same underlying event can be counted as independent evidence accidentally. The posterior may then become much more confident without any corresponding increase in information.

Conditional independence is a modeling statement, not a property that follows from storing records in separate files. Two sensors can share a failure source, and repeated measurements can share a latent state. A richer model may need to represent those dependencies directly. It should not merely divide the likelihood by an unexplained correction factor after noticing an implausibly narrow posterior.

## What the probabilities do and do not mean

The prior is not necessarily a subjective guess without evidence. It may encode previous measurements, physical constraints, population information or a deliberate regularization choice. Its origin and scale should be stated. Reusing the same observations to construct a prior and then including them again in the likelihood can duplicate evidence unless the joint procedure is modeled explicitly.

The likelihood is also an assumption. Misclassification, selection, censoring and dependence belong to the observation process. A carefully chosen prior does not repair an incorrectly specified likelihood automatically. Posterior predictive checks later in the course examine whether the model reproduces relevant features of the observations.

The two-hypothesis fixture makes all alternatives visible. A real system may fail in a way absent from its modeled hypotheses. A high posterior probability for one listed hypothesis does not prove that the list is complete. Keep model adequacy and uncertainty within a model separate.

## Answered scientific discussion

**Why can a positive signal still leave substantial uncertainty?** The signal is combined with the prior frequency and its behavior under both hypotheses. Bayes' rule exposes that accounting instead of equating a classifier characteristic with a case-specific probability.

**What should be recorded before updating?** Record the hypotheses, prior, observation definition, likelihood and dependence assumptions. Then retain the exact evidence used. The program checks finite-probability arithmetic; an external application still needs evidence that the modeled observation mechanism is appropriate.

## Worked example: Two different detectors, odds form and update order

```python
prior = 0.02
detectors = {"A": (0.90, 0.05), "B": (0.80, 0.10)}  # (P(alarm | fault), P(alarm | no fault))


def update(p, name):
    sens, false_alarm = detectors[name]
    return sens * p / (sens * p + false_alarm * (1 - p))


for order in (("A", "B"), ("B", "A")):
    p = prior
    for name in order:
        p = update(p, name)
        print(f"after {name}: P(fault) = {p:.4f}")
    print("order", "".join(order), "final", round(p, 4))

odds = prior / (1 - prior)
lr = [s / f for s, f in detectors.values()]
post_odds = odds * lr[0] * lr[1]
print(
    f"likelihood ratios {lr[0]:.0f} and {lr[1]:.0f}; prior odds {odds:.4f}; posterior odds {post_odds:.4f}"
)
print(f"posterior from odds {post_odds / (1 + post_odds):.4f}")
```

Observed output:

```text
after A: P(fault) = 0.2687
after B: P(fault) = 0.7461
order AB final 0.7461
after B: P(fault) = 0.1404
after A: P(fault) = 0.7461
order BA final 0.7461
likelihood ratios 18 and 8; prior odds 0.0204; posterior odds 2.9388
posterior from odds 0.7461
```

Detector A alone lifts the fault probability from 0.02 to 0.2687, and detector B alone lifts it only to 0.1404, because A's likelihood ratio is \(0.90/0.05=18\) while B's is \(0.80/0.10=8\). Taken together, in either order, the answer is the same 0.7461. Order cannot matter when the two alarms are conditionally independent given the fault state, since the joint likelihood is a product and multiplication commutes. The odds form makes this arithmetic transparent: prior odds \(0.02/0.98=0.0204\) times \(18\times8=144\) gives posterior odds 2.9388, and \(2.9388/3.9388=0.7461\). The product rule is also the assumption to audit. If B merely re-reads A's sensor, its alarm carries no new information once A has fired, and multiplying by 8 a second time would push the probability far above what the evidence supports. Two independent alarms make a fault about three times more likely than not, yet a single strong alarm still leaves roughly a 73 percent chance that the system is healthy.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def posterior(prior, likelihood):
    prior, likelihood = np.asarray(prior, float), np.asarray(likelihood, float)
    if prior.shape != likelihood.shape or np.any(prior < 0) or not np.isclose(prior.sum(), 1):
        raise ValueError("Use matching hypotheses and a normalized prior")
    if (
        not np.all(np.isfinite(likelihood))
        or np.any(likelihood < 0)
        or np.dot(prior, likelihood) <= 0
    ):
        raise ValueError("Evidence needs finite nonnegative likelihood and positive probability")
    mass = prior * likelihood
    return mass / mass.sum()


def run_cases():
    prior = np.array([0.8, 0.2])
    likelihood = np.array([0.1, 0.9])
    one = posterior(prior, likelihood)
    independent_two = posterior(prior, likelihood**2)
    assert np.isclose(one[1], 9 / 13)
    assert np.isclose(independent_two[1], 81 / 85)
    correlated_repeat = one.copy()
    assert correlated_repeat[1] < independent_two[1]
    odds = (prior[1] / prior[0]) * (likelihood[1] / likelihood[0])
    assert np.isclose(odds, one[1] / one[0])
    return dict(
        one_signal=one.tolist(),
        two_independent_signals=independent_two.tolist(),
        perfectly_repeated_signal=correlated_repeat.tolist(),
        posterior_odds=float(odds),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-001 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Stan Bayesian workflow and modeling guide](https://mc-stan.org/docs/stan-users-guide/)
