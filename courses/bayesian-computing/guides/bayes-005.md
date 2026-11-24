# bayes-005: Posterior decisions, loss and regret

Tutorial mode. Stage: beginner. Direct prerequisites: `bayes-003`, `bayes-004`.

## Posterior uncertainty becomes a decision through loss

Inference describes uncertainty under a model. A decision additionally requires actions and consequences. A Bayes action minimizes posterior expected loss, or equivalently maximizes posterior expected utility. A probability threshold such as 95% is not a universal decision rule; it represents a particular choice of consequences or constraints when it is justified at all.

The example considers an action that costs five units and produces eight units of benefit on success. Its success probability has a Beta(10,4) posterior. Under the stated linear utility, expected net benefit is \(8\mathbb{E}[p\mid y]-5\). The action is preferred when this quantity is positive.

This is a decision model for a named future action. It does not establish that a success probability estimated under an unrelated old policy is the causal success probability after a new intervention. Transport, intervention effects and changing selection require their own scientific assumptions.

## Key terms

- **Utility:** A numerical statement of the consequences of an action, here eight units of benefit on success minus a cost of five.
- **Posterior expected loss:** The loss of an action averaged over the posterior distribution of the unknown parameter, also called posterior risk.
- **Bayes action:** The action that minimizes posterior expected loss, or equivalently maximizes posterior expected utility.
- **Regret:** The loss of the chosen action relative to the action that would have been chosen if the parameter were known.

## Worked case 1: compare expected utility with a posterior probability

The posterior mean probability is 10/14. Expected net benefit is therefore positive. The program also calculates the probability that the unknown net-benefit parameter is positive, using the threshold \(p>5/8\). These are two distinct summaries.

Requiring the latter probability to exceed a chosen level would introduce a different decision rule. It might be appropriate under a justified risk constraint, but it should not be silently substituted for maximizing the stated expected utility. A decision maker should be able to identify which objective produced the recommendation.

The same reasoning generalizes to several actions and a nonlinear loss. In that case, plugging a posterior mean parameter into the utility function can differ from averaging utility over the posterior. Retain the full relevant uncertainty when consequences are nonlinear, asymmetric or constrained.

## Worked case 2: calculate posterior expected regret

Regret compares the chosen action with the action that would have been selected if the uncertain parameter were known. The program integrates the loss from choosing the action when its net benefit is negative and the loss from waiting when its net benefit is positive.

The expected regret of acting is smaller. The difference between the expected regrets equals the expected net benefit, providing an independent identity check for this two-action setup. Both quantities are integrated over the same posterior and use the same cost and benefit definitions.

Expected regret is not the same as the probability of making the wrong action. A rare but very large loss can matter more than a common small loss. Reporting only the probability that one action is better can hide the magnitude of the consequences. The program keeps both probability and utility summaries so that distinction can be inspected.

## Separate parameter uncertainty, future noise and model uncertainty

Uncertainty about p is not the same as the randomness of a future success conditional on p. A predictive calculation integrates both when appropriate. If the benefit itself is uncertain or depends on another outcome, the joint model should represent that dependence rather than multiplying unrelated mean values.

The posterior is conditional on the model. A decision can be highly sensitive to prior assumptions, missing outcome mechanisms or a poorly modeled tail. Sensitivity analysis should vary scientifically plausible alternatives and show whether the action changes. A precise Monte Carlo average cannot remove those uncertainties.

Constraints can change the optimal policy. A budget, safety requirement or fairness condition may exclude an action that otherwise has positive expected utility. Define those constraints explicitly. Do not encode every normative requirement as an unexplained penalty coefficient and then call the selected result objective.

## Answered scientific discussion

**Should the lower bound of a credible interval determine every action?** That is one possible conservative rule, but its relationship to costs and risk must be stated. Expected-utility optimization and chance constraints are different decision frameworks.

**What does the small exact example establish?** It verifies the posterior-risk calculation under a transparent beta model and fixed consequences. A real deployment should also preserve the data boundary, intervention assumptions, operational costs, uncertainty assessment and a plan for updating or reversing the decision when evidence changes.

## Worked example: Three losses, three point estimates from one Beta posterior

```python
import numpy as np
from scipy import stats

post = stats.beta(3, 9)
grid = np.linspace(0, 1, 20001)
dens = post.pdf(grid)
dens /= dens.sum()


def expected(loss, a):
    return dens @ loss(grid, a)


candidates = np.linspace(0.05, 0.45, 401)
losses = {
    "squared": lambda t, a: (t - a) ** 2,
    "absolute": lambda t, a: np.abs(t - a),
    "0-1 within 0.005": lambda t, a: (np.abs(t - a) > 0.005).astype(float),
}
for name, loss in losses.items():
    vals = np.array([expected(loss, a) for a in candidates])
    if name.startswith("0-1"):  # exact window mass avoids grid-edge artifacts
        vals = 1 - (post.cdf(candidates + 0.005) - post.cdf(candidates - 0.005))
    print(
        f"{name:16s}: best action {candidates[vals.argmin()]:.3f}, expected loss {vals.min():.4f}"
    )
print(f"mean {post.mean():.3f}, median {post.median():.3f}, mode {(3 - 1) / (3 + 9 - 2):.3f}")
```

Observed output:

```text
squared         : best action 0.250, expected loss 0.0144
absolute        : best action 0.236, expected loss 0.0961
0-1 within 0.005: best action 0.200, expected loss 0.9668
mean 0.250, median 0.236, mode 0.200
```

One posterior, Beta(3, 9), yields three different best actions because each loss asks a different question. Under squared loss the best report is the posterior mean 0.250, and the minimized expected loss 0.0144 is exactly the posterior variance \(27/(144\times13)\). Under absolute loss the minimizer moves left to the median 0.236, because the right-skewed posterior has a long upper tail that the mean chases and the median ignores. Under a 0-1 loss that pays only for landing within 0.005 of the truth, the best action is the mode 0.200, but its expected loss is 0.9668: even the best single guess is inside that narrow window only about 3 percent of the time. The spread from 0.200 to 0.250 is a fifth of the mean, large enough to change a downstream decision. Reporting "the posterior estimate" without naming the loss hides that choice. A defect-rate threshold set from the mode would trigger action more readily than one set from the mean.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic Bayesian investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import stats


def run_cases():
    alpha, beta = 10, 4
    benefit, cost = 8.0, 5.0
    threshold = cost / benefit
    mean = alpha / (alpha + beta)
    expected_net = benefit * mean - cost
    positive_probability = float(stats.beta.sf(threshold, alpha, beta))
    assert expected_net > 0 and 0.5 < positive_probability < 1
    theta = np.linspace(0.0001, 0.9999, 20001)
    density = stats.beta.pdf(theta, alpha, beta)
    regret_treat = float(np.trapezoid(np.maximum(cost - benefit * theta, 0) * density, theta))
    regret_wait = float(np.trapezoid(np.maximum(benefit * theta - cost, 0) * density, theta))
    assert regret_treat < regret_wait
    assert np.isclose(regret_wait - regret_treat, expected_net, atol=1e-6)
    return dict(
        expected_net_benefit=expected_net,
        probability_benefit_positive=positive_probability,
        regret_treat=regret_treat,
        regret_wait=regret_wait,
        decision="treat under the stated linear utility",
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("bayes-005 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [Stan decision-analysis guide](https://mc-stan.org/docs/stan-users-guide/)
