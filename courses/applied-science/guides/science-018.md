# science-018: Scenario decisions, minimax policies and information value

Tutorial mode. Stage: advanced. Direct prerequisites: `science-009`, `science-016`.

## Uncertainty must enter before the decision is chosen

A decision can be optimized for expected cost, worst-case cost, a risk measure or a constrained service requirement. These objectives can recommend different actions even when they use the same scenarios. The appropriate objective comes from the decision context, not from which method produces a favorable number.

This tutorial reuses the inventory loss from the forecasting route. Demand scenarios are 2,3,4,12 with probabilities .4,.3,.2,.1. Underage costs four and overage costs one. The decision is an integer quantity from zero through twelve. The finite scenario table makes every alternative directly inspectable.

Expected loss is \(\sum_s p_sL(q,d_s)\). A minimax decision minimizes \(\max_sL(q,d_s)\). The latter does not use the scenario probabilities; it protects against the worst listed outcome. A scenario omitted from the list is not protected merely because the objective is called robust.

## Worked case 1: expected-cost and minimax decisions

The expected-cost decision is four. The minimax decision is ten, balancing the shortage loss at demand twelve against the surplus loss at demand two. The program evaluates the entire discrete action grid, verifies both choices and compares their worst-case costs.

The minimax decision can have a larger expected cost. That is not a contradiction: it is optimizing a different criterion. Whether the extra protection is worth its expected cost depends on consequences, risk tolerance and the credibility of the scenario set. A report should display the tradeoff instead of calling one quantity universally optimal.

Scenario probabilities may be estimated from sparse history or supplied by experts. Treat them as assumptions with provenance. Sensitivity analysis can vary their values, the cost ratio and the candidate action set. A precise optimizer output does not eliminate uncertainty in any of those inputs.

## Worked case 2: compute the value of perfect information

With perfect information about demand before ordering, the action could be chosen separately for each scenario. The **expected value of perfect information** is the optimized expected cost without that information minus the expected optimized cost with it:

\[
\operatorname{EVPI}=\min_q\sum_s p_sL(q,d_s)
-\sum_s p_s\min_qL(q,d_s).
\]

The code verifies that this difference is nonnegative. In this particular grid, exact demand quantities are available as actions, so a perfectly informed decision can avoid shortage and surplus loss. This makes EVPI a transparent upper bound on the value of an information source that is less than perfect, under the same model and costs.

EVPI is not the expected value of a particular forecast or experiment. That requires modeling what the information will reveal, how decisions will respond and what obtaining it costs. A noisy signal can be valuable, but its value may be far below the perfect-information benchmark.

## Extend carefully to multi-stage decisions

A one-period inventory problem ignores carryover, lead times, action-dependent demand and competition for shared resources. Adding these mechanisms can require dynamic or multi-stage optimization. The information available at each stage must be explicit; a model that lets an early decision depend on a future scenario is using perfect foresight accidentally.

Sample-average approximation uses a finite scenario sample to approximate an expectation. The chosen decision can overfit that sample. Evaluate it on independent scenarios or repeated samples and report stability of both value and action. A small improvement in estimated value can correspond to a large, unstable change in selected action near a decision boundary.

Risk measures also require interpretation. A tail-risk criterion depends on how the tail is represented and on the chosen level. Worst-case optimization over an overly broad uncertainty set can produce impractical conservatism; an overly narrow set can miss the important failure. The phrase robust should be accompanied by the exact set or distributional assumptions.

## Answered scientific discussion

**Does EVPI tell us how much to pay for a model?** It is an upper bound under the supplied decision model. The actual model's information quality, latency, implementation costs and effects on behavior require a separate analysis.

**Why show both policies when only one will be deployed?** Their difference reveals the consequences of the risk objective. A decision maker can then discuss the underlying tradeoff rather than treating the solver's chosen action as a value judgment made by mathematics.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def inventory_loss(quantity, demand, under=4.0, over=1.0):
    d = np.asarray(demand, float)
    return under * np.maximum(d - quantity, 0) + over * np.maximum(quantity - d, 0)


def run_cases():
    demand = np.array([2.0, 3.0, 4.0, 12.0])
    prob = np.array([0.4, 0.3, 0.2, 0.1])
    quantities = np.arange(13.0)
    costs = np.array([inventory_loss(q, demand) for q in quantities])
    mean = costs @ prob
    mean_choice = int(quantities[mean.argmin()])
    worst = costs.max(axis=1)
    robust_choice = int(quantities[worst.argmin()])
    assert mean_choice == 4 and robust_choice == 10
    # Perfect-information value compares optimization before vs after observing demand.
    evpi = float(mean.min() - np.sum(prob * np.min(costs, axis=0)))
    assert evpi >= 0
    assert worst[robust_choice] < worst[mean_choice]
    return dict(
        expected_cost_choice=mean_choice,
        minimax_choice=robust_choice,
        expected_cost=float(mean.min()),
        evpi=evpi,
        worst_cost=float(worst[robust_choice]),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-018 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [SciPy mixed-integer optimization](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html)
- [SciPy linear programming and marginal values](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html)
