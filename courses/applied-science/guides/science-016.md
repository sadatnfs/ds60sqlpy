# science-016: Optimization duality and the scope of shadow prices

Tutorial mode. Stage: intermediate. Direct prerequisites: `statistics-036`.

## Optimization needs a scientific input contract

An optimizer chooses an action for the objective and constraints supplied. It does not decide whether the coefficients represent the right causal effects, forecast distribution or operational costs. Before interpreting a solution, define units, feasible actions and the origin of every coefficient.

The example maximizes \(3x_1+2x_2\) subject to two resource constraints, \(x_1+x_2\le b\) and \(2x_1+x_2\le8\), with nonnegative activities. The implementation minimizes the negative objective because that is the solver's convention. Confusing maximization signs with minimization marginals is a common source of incorrectly interpreted shadow prices.

For a locally stable optimum, a constraint's dual value describes the derivative of optimal value with respect to its bound. That is a local statement about the specified mathematical problem. It is not a universal price valid for every expansion, and it is not necessarily a market price or causal business benefit.

## Key terms

- **Shadow price:** A constraint's dual value, the local derivative of optimal objective value with respect to that constraint's bound.
- **Binding constraint:** A constraint that holds with equality at the optimum; changes in the active set end the range where a dual value applies.
- **Strong duality:** For a well-posed linear program, equality between the primal and dual optimal values.
- **KKT conditions:** Feasibility, dual feasibility, stationarity and complementary slackness, which together certify an optimum of a convex program.

## Worked case 1: verify the primal solution and shadow price

At \(b=5\), the solution is \((3,2)\) with value 13. Both resource constraints bind. The code checks the chosen activities, objective and feasibility independently of the solver's success flag.

Increasing the first capacity by .001 changes the optimized value at a rate of one. The negative of the solver's minimization marginal agrees with that finite difference. This independently checks the sign convention and the local sensitivity interpretation. A correct numerical solution without this interpretation can still lead to a wrong managerial recommendation.

The two constraints have different units if their resource coefficients represent different things. A dual value therefore has objective units per unit of its own resource. Comparing two shadow prices without considering those units is meaningless. Rescaling a resource should change its numerical dual value inversely while preserving the underlying tradeoff.

## Worked case 2: leave the local sensitivity region

The first capacity is then increased from five to nine. Extrapolating the earlier shadow price would predict an increase of four in value. The actual solution does not follow that line because the other constraint becomes the limiting resource. The code checks the failure of the long-range linear extrapolation explicitly.

This is why a sensitivity range or scenario analysis matters. The active set can change, another constraint can become binding, or a variable can enter or leave the optimal basis. A local derivative is useful for small changes near the analyzed problem, not as a substitute for resolving materially different scenarios.

Solver tolerances also matter. A tiny residual violation may be numerical rather than operationally acceptable. Translate tolerances into the units of the real constraint, and verify the solution after any rounding or implementation conversion. A fractional allocation that the implementation rounds can become infeasible even when the continuous optimum is valid.

## Distinguish duality from an empirical claim

Strong duality for a well-posed linear program gives an equality between primal and dual optimal values. It does not establish that the input rewards are known, stable or causally affected by the chosen actions. If the coefficients are estimated from noisy data, uncertainty can materially change the selected allocation.

A useful workflow preserves a coefficient ledger, the problem formulation, solver version/status, primal feasibility, objective and relevant dual information. If a constraint represents fairness, safety or a regulatory requirement, its meaning may not be exchangeable for a small increase in objective value. The mathematical form should reflect the intended decision policy.

Test edge cases deliberately. An infeasible set, an unbounded objective, redundant constraints and nearly dependent rows can each reveal different issues. Do not repair them by silently dropping a constraint until a number appears. Explain which assumption or requirement must change to make the problem meaningful.

## Answered scientific discussion

**Should a resource be purchased whenever its shadow price exceeds its cost?** That conclusion requires a small change within the valid sensitivity region, compatible units, correct coefficients and no omitted constraints or transaction effects. A scenario re-solve is usually preferable for a substantial expansion.

**Why retain the simple two-variable example?** Its feasible geometry and optimum can be checked by hand. That makes it an independent oracle for signs, constraints and marginal interpretation before a larger optimizer makes those details harder to inspect.

## Worked example: Re-solving across the second capacity to find its price range

```python
import numpy as np
from scipy.optimize import linprog


def solve(b1, b2):
    res = linprog(c=[-3, -2], A_ub=[[1, 1], [2, 1]], b_ub=[b1, b2], method="highs")
    return -res.fun, res.x, -res.ineqlin.marginals


for b2 in (4, 5, 6, 8, 10, 11, 12):
    value, x, duals = solve(5, b2)
    print(f"b2={b2:>2}: x={x.round(3) + 0.0}, value={value:.2f}, duals={duals.round(3)}")
```

Observed output:

```text
b2= 4: x=[0. 4.], value=8.00, duals=[0. 2.]
b2= 5: x=[0. 5.], value=10.00, duals=[0. 2.]
b2= 6: x=[1. 4.], value=11.00, duals=[1. 1.]
b2= 8: x=[3. 2.], value=13.00, duals=[1. 1.]
b2=10: x=[5. 0.], value=15.00, duals=[1. 1.]
b2=11: x=[5. 0.], value=15.00, duals=[3. 0.]
b2=12: x=[5. 0.], value=15.00, duals=[3. 0.]
```

The program in this unit varies the first capacity; this table varies the second, \(2x_1+x_2\le b_2\), with \(b_1=5\). Below 5, only the second constraint binds and the solution produces only \(x_2\), so each extra unit of \(b_2\) is worth its price of 2, as values 8 and 10 confirm. Between 5 and 10 both constraints bind, the price of \(b_2\) drops to 1 and the value rises from 11 at \(b_2=6\) to 13 at 8 and 15 at 10, one per unit. Above 10 the solution is stuck at \((5,0)\), the second constraint is slack and its price is 0; the first capacity now carries the whole value at price 3. At exactly \(b_2=5\) and \(b_2=10\) the problem is degenerate and the reported dual is one of two valid one-sided slopes. Pricing the second resource from the \(b_2=8\) solution would overstate the gain from expanding to 12 by 2 units, because the price falls to zero after 10.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import optimize


def solve_mix(capacity):
    return optimize.linprog(
        [-3.0, -2.0],
        A_ub=[[1, 1], [2, 1]],
        b_ub=[capacity, 8],
        bounds=[(0, None)] * 2,
        method="highs",
    )


def run_cases():
    fit = solve_mix(5)
    assert fit.success and np.allclose(fit.x, [3, 2]) and np.isclose(-fit.fun, 13)
    epsilon = 0.001
    near = solve_mix(5 + epsilon)
    value_derivative = (-near.fun + fit.fun) / epsilon
    shadow = -float(fit.ineqlin.marginals[0])
    assert np.isclose(value_derivative, shadow) and shadow == 1
    far = solve_mix(9)
    assert not np.isclose(-far.fun, 13 + 4 * shadow)
    assert np.all(np.asarray([[1, 1], [2, 1]]) @ fit.x <= np.array([5, 8]) + 1e-8)
    return dict(
        allocation=fit.x.tolist(),
        value=-fit.fun,
        local_shadow_price=shadow,
        large_change_value=-far.fun,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-016 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [SciPy mixed-integer optimization](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html)
- [SciPy linear programming and marginal values](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html)
