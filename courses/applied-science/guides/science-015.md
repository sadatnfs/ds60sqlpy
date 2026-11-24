# science-015: Logged-policy evaluation, support and variance control

Tutorial mode. Stage: intermediate. Direct prerequisites: `science-013`, `statistics-017`.

## Logged behavior is selected by a policy

Historical outcomes are observed under the actions chosen by a logging policy. If that policy prefers one item or treatment, its observed mean reward is not generally the value of another policy. Off-policy evaluation uses the logging mechanism and explicit support assumptions to estimate what a proposed policy would do.

Let \(p(a\mid x)\) be the logging probability, \(q(a\mid x)\) the target-policy probability and \(R\) the observed reward. An inverse-propensity estimate is

\[
\widehat V_{\mathrm{IPS}}=\frac{1}{n}\sum_i
\frac{q(A_i\mid X_i)}{p(A_i\mid X_i)}R_i.
\]

Every action used by the target must have positive logging probability in the relevant contexts. Accurate logging probabilities also need to correspond to the actual action-selection process, including eligibility, exploration and overrides. An undocumented business rule can invalidate a nominal propensity stored by a model service.

## Key terms

- **Logging policy:** The mechanism that chose the logged actions, whose probabilities p(a | x) must match actual selection including overrides.
- **Inverse propensity scoring:** Estimating a target policy's value by averaging rewards reweighted by q(a | x)/p(a | x).
- **Support:** The requirement that every action the target policy uses has positive logging probability in the relevant contexts.
- **Doubly robust estimator:** A combination of an outcome model and importance weights that remains consistent if either component is correct.
- **Weight clipping:** Capping importance ratios to reduce variance at the cost of a changed expectation, that is, bias.

## Worked case 1: recover a new policy's value

The logging policy chooses action A 80% of the time and B 20%. Their known rewards are .2 and .8. The observed logging mean is .32. A target policy choosing each action equally has value .5. The program represents the logging population with exact repeated proportions and recovers .5 using the probability ratio.

This calculation distinguishes two values that are often confused: the performance of the policy that generated the log and the performance of the proposed policy. A dataset can accurately describe the former while being inadequate for the latter because of limited support or large importance weights.

The function rejects a target-positive action with zero logging support. Replacing a zero propensity with an epsilon would produce an arbitrary finite number without creating evidence. Support may also be practically weak when probabilities are merely very small; examine weight concentration, effective sizes and behavior by context rather than checking only for exact zeros.

## Worked case 2: clipping and doubly robust correction

Clipping the importance ratio at 1.5 reduces the influence of the rarely logged high-reward action. In this fixture, the resulting estimate is below .5. The code checks that direction explicitly. Clipping can reduce variance in a random sample, but it changes the expectation. It should be presented as a stated bias-variance tradeoff and accompanied by sensitivity analysis.

The program also supplies an imperfect reward model with predictions .3 and .7. It combines the model's target-policy average with an importance-weighted residual correction. The result is again .5 because the logging probabilities are correct. This is a concrete doubly robust calculation, not a claim that an arbitrary model and arbitrary weights are jointly safe.

In observational settings, reward-model fitting and evaluation should be separated, often using cross-fitting or a clearly held-out design. Reusing the evaluation rewards to overfit the nuisance model can undermine finite-sample behavior. A doubly robust formula does not remove the need for identification, support and honest model-selection boundaries.

## Build an evaluation ledger

Store the context, eligible action set, selected action, exact logging probability, reward definition, attribution window and model/policy version. A probability before a deterministic eligibility filter may not be the probability of the action actually delivered. If users receive multiple actions or influence each other, a simple single-action contextual-bandit estimand may be inappropriate.

Report uncertainty at the correct independent unit, such as a user or session. Examine whether delayed rewards are complete and whether missing outcomes depend on action. Self-normalized importance estimates, clipping and alternative nuisance models are distinct estimators with different finite-sample properties. Record them rather than presenting all as the same IPS method.

Offline evidence should lead to a bounded deployment decision, such as a controlled experiment with guardrails, rather than an automatic claim of online benefit. Changes in user behavior, catalog eligibility, feedback loops and serving latency can invalidate the historical environment assumed by an offline calculation.

## Answered scientific discussion

**Can a deterministic historical policy evaluate every new policy?** No. If it never chose an action in a context, that outcome is not identified from the log without additional modeling assumptions or new exploration.

**Does unbiasedness guarantee a useful estimate?** An unbiased estimator can have enormous variance when it relies on rare actions. Diagnose both identification and uncertainty before using its point estimate to make a deployment decision.

## Worked example: IPS, clipped IPS and doubly robust on six logged rounds

```python
import numpy as np

action = np.array([0, 1, 1, 0, 1, 0])
reward = np.array([1.0, 0.0, 1.0, 0.0, 1.0, 1.0])
p_log = np.array([0.9, 0.1, 0.1, 0.9, 0.1, 0.9])  # logging probability of the action taken
p_new = np.where(action == 1, 0.8, 0.2)  # new policy prefers action 1
q_hat = {0: 0.6, 1: 0.5}  # reward model by action

w = p_new / p_log
ips = np.mean(w * reward)
clipped = np.mean(np.minimum(w, 3.0) * reward)
direct = 0.8 * q_hat[1] + 0.2 * q_hat[0]
q_taken = np.array([q_hat[a] for a in action])
dr = direct + np.mean(w * (reward - q_taken))
print("importance weights:", w.round(3))
print(f"IPS {ips:.4f}, clipped IPS (cap 3) {clipped:.4f}, direct {direct:.4f}, DR {dr:.4f}")
print(f"ESS of weights {w.sum() ** 2 / (w**2).sum():.3f} out of {len(w)}")
```

Observed output:

```text
importance weights: [0.222 8.    8.    0.222 8.    0.222]
IPS 2.7407, clipped IPS (cap 3) 1.0741, direct 0.5200, DR 1.1941
ESS of weights 3.167 out of 6
```

The new policy chooses action 1 with probability 0.8, while the logging policy chose it with probability 0.1, so each logged action-1 round gets weight 8. Three such rounds dominate: plain IPS returns 2.7407, an impossible value for rewards bounded by 1, because two of those three rounds had reward 1. Clipping weights at 3 brings the estimate to 1.0741, still above 1, and introduces bias whose size depends on the cap. The direct method uses only the reward model, \(0.8(0.5)+0.2(0.6)=0.52\), and is biased if that model is wrong. The doubly robust estimate 1.1941 adds the weighted residuals to 0.52. Here the residuals on action-1 rounds are \(-0.5, +0.5, +0.5\), each multiplied by 8, so the correction is still dominated by those three rows. The effective sample size of 3.167 out of 6 and the impossible IPS value say the same thing: the log contains too little support for action 1 to evaluate this policy reliably.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def ips_value(reward, logged_probability, target_probability):
    r, p, q = map(lambda v: np.asarray(v, float), (reward, logged_probability, target_probability))
    if r.shape != p.shape or r.shape != q.shape or r.ndim != 1 or not len(r):
        raise ValueError("Use matching nonempty vectors")
    if not all(np.all(np.isfinite(v)) for v in (r, p, q)) or np.any((p > 1) | (q < 0) | (q > 1)):
        raise ValueError("Use finite rewards and valid probabilities")
    if np.any(p <= 0):
        raise ValueError("Target action lacks logging-policy support")
    return float(np.mean(r * q / p))


def run_cases():
    # Exact repeated logging population: A occurs80%, B20%; reward(.2,.8).
    p = np.r_[np.full(80, 0.8), np.full(20, 0.2)]
    reward = np.r_[np.full(80, 0.2), np.full(20, 0.8)]
    q = np.full(100, 0.5)
    value = ips_value(reward, p, q)
    observed = float(reward.mean())
    assert np.isclose(value, 0.5) and np.isclose(observed, 0.32)
    clipped = float(np.mean(reward * np.minimum(q / p, 1.5)))
    assert clipped < value
    model = np.r_[np.full(80, 0.3), np.full(20, 0.7)]
    dr = 0.5 * 0.3 + 0.5 * 0.7 + float(np.mean(q / p * (reward - model)))
    assert np.isclose(dr, 0.5)
    return dict(ips=value, logging_average=observed, clipped_estimate=clipped, doubly_robust=dr)


if __name__ == "__main__":
    evidence = run_cases()
    print("science-015 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Rendle and colleagues, Bayesian Personalized Ranking](https://arxiv.org/abs/1205.2618)
- [Dudik and colleagues, doubly robust policy evaluation](https://arxiv.org/abs/1103.4601)
