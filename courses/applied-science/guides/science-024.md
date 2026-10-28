# science-024: A scientific decision dossier with explicit rollback conditions

Tutorial mode. Stage: advanced. Direct prerequisites: `science-006`, `science-009`, `science-015`, `science-018`, `science-020`.

## Assemble an inspectable scientific decision dossier

A scientific workflow should preserve the chain from data semantics to an action. A notebook containing a successful model fit is only one piece. The final dossier should identify the question, observation unit, information cutoff, estimation assumptions, uncertainty, decision rule and conditions that would invalidate the recommendation.

This capstone uses three synthetic regions and a small two-arm dataset in each. Each arm contains four independent-unit outcomes under the illustrative analysis model. The constructed mean differences are three, one and minus one. The program calculates those differences and their conventional two-sample standard errors from the supplied arrays instead of accepting effect numbers as unexplained constants.

For region \(j\), the illustrative lower score is \(b_j=\widehat\tau_j-1.96\widehat{\operatorname{SE}}_j\). Binary actions maximize the sum of selected scores subject to a resource budget. This is a deliberately stated utility score. A sum of marginal lower bounds is not automatically a simultaneous 95% lower confidence bound, and four observations per arm do not justify a strong normal-approximation coverage claim.

## Worked case 1: estimate, check and decide

The code first verifies the expected treatment differences and independently derived standard errors. The three activity costs are three, two and one, with total budget four. Under the stated conservative score, only the first region has a positive contribution. The optimizer selects north and leaves the unused resource unspent.

That unused budget is meaningful. The constraint is an upper limit, not an instruction to spend everything. Forcing full budget use would define a different decision problem and could select a region with a negative score. A solver should implement the intended policy rather than infer that every available resource must be consumed.

The ledger records the estimand, information cutoff, budget, objective and selected region. An operational extension should also include stable data/model versions, eligibility rules, variance method and the exact input snapshot. The small arrays are complete synthetic inputs, so there is no claim that the regions represent an external population or a valid observational causal study.

## Worked case 2: revise the evidence and trigger rollback

A later scenario changes the first region's estimated effect from three to .1 while keeping the uncertainty calculation explicit. All lower scores become negative, and the revised optimizer chooses no action. The program verifies that outcome rather than keeping the earlier recommendation because it was once approved.

This scenario illustrates a rollback condition, not a claim that an observed real intervention deteriorated. A production policy should state which evidence updates trigger reassessment, who owns the decision and what fallback is available. A delayed outcome, changed measurement definition or broken data contract can invalidate the analysis without changing the model's numerical code.

Retain the previous result as historical evidence. Replacing a recommendation should not rewrite the source, inputs or uncertainty that supported it at the earlier cutoff. A reproducible record permits review of both whether the original decision was defensible and whether the update was handled correctly.

## Connect the specialist branches

The causal tutorials establish that a prediction difference is not automatically an intervention effect and that time alignment and support matter. The forecasting tutorials establish that historical information must be reconstructed and that the loss should match the decision. Survival examples establish that incomplete outcomes contribute specific likelihood information. Ranking and policy evaluation expose selection by a logging policy. Synthesis and survey lessons show how evidence units and dependence affect uncertainty.

A real dossier may need only a subset of those methods. The purpose is to choose a coherent analysis for the question, not to include every technique. Applying several sophisticated methods with incompatible populations, time horizons or effect definitions can make a report less defensible rather than more comprehensive.

The optimizer treats its scores as given inputs. If those scores are noisy or selected from many candidates, the chosen action can exploit favorable estimation error. Evaluate that selection process, consider joint uncertainty where needed, and use appropriate controlled validation before broad deployment. Constraints on safety, fairness or feasibility should be represented explicitly and reviewed in their own units.

## Answered scientific discussion

**What would an interview-quality explanation emphasize?** Start with the target and data contract, explain how the estimate and uncertainty were obtained, derive how they enter the action rule, identify a failure mode, and state what evidence would change the recommendation. Listing model names is not a substitute for that chain of reasoning.

**What makes this capstone complete?** Every input, calculation, assertion and decision is visible and reproducible within the declared synthetic problem. It also names the assumptions and external evidence that the example cannot supply. Completion of the program is evidence about this bounded computation, not a certificate of scientific validity in a new domain.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import optimize


def run_cases():
    # Reproducible capstone ledger: effects, uncertainty and finite resource decisions.
    regions = ["north", "south", "east"]
    control = np.array([[-1.0, 0.0, 0.0, 1.0], [-2.0, 0.0, 0.0, 2.0], [-0.5, 0.0, 0.0, 0.5]])
    treated = control + np.array([3.0, 1.0, -1.0])[:, None]
    effects = treated.mean(axis=1) - control.mean(axis=1)
    se = np.sqrt(treated.var(axis=1, ddof=1) / 4 + control.var(axis=1, ddof=1) / 4)
    assert np.allclose(effects, [3, 1, -1])
    assert np.allclose(se, np.sqrt([1 / 3, 4 / 3, 1 / 12]))
    cost = np.array([3.0, 2.0, 1.0])
    lower = effects - 1.96 * se
    fit = optimize.milp(
        -lower,
        integrality=np.ones(3),
        bounds=optimize.Bounds(0, 1),
        constraints=optimize.LinearConstraint(cost, -np.inf, 4),
    )
    assert fit.success and np.allclose(fit.x, [1, 0, 0])
    selected = [name for name, chosen in zip(regions, fit.x, strict=True) if chosen > 0.5]
    assert selected == ["north"]
    revised = np.array([0.1, 1.0, -1.0])
    new_lower = revised - 1.96 * se
    updated = optimize.milp(
        -new_lower,
        integrality=np.ones(3),
        bounds=optimize.Bounds(0, 1),
        constraints=optimize.LinearConstraint(cost, -np.inf, 4),
    )
    assert updated.success and updated.x.sum() == 0
    ledger = dict(
        estimand="region-specific additive effect under stated assignment",
        cutoff=10,
        budget=4,
        objective="sum of marginal lower bounds",
        selected=selected,
        rollback_after_revision=True,
    )
    # A sum of marginal lower bounds is a conservative utility score, not a joint95% bound.
    return dict(
        ledger=ledger,
        lower_bounds=lower.tolist(),
        estimated_effects=effects.tolist(),
        standard_errors=se.tolist(),
        selected_cost=float(cost @ fit.x),
        updated_selection_count=int(updated.x.sum()),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-024 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [SciPy mixed-integer optimization](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html)
- [SciPy linear programming and marginal values](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html)
