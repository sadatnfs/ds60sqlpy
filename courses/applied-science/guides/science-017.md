# science-017: Integer decisions, relaxation bounds and solver certificates

Tutorial mode. Stage: advanced. Direct prerequisites: `science-016`.

## Discrete actions require discrete models

Many decisions cannot be divided continuously: a project is selected or not, a facility is opened or closed, and a person is assigned to one shift. A continuous relaxation can be useful for reasoning and bounds, but rounding its solution is not a general mixed-integer optimization algorithm.

The fixture has three projects with values 10,8,6 and costs 6,5,4. A budget of nine permits binary decisions \(x_j\in\{0,1\}\). The objective is \(\max\sum_j v_jx_j\), subject to \(\sum_j c_jx_j\le9\). The implementation again negates the objective because SciPy's `milp` minimizes.

The **linear relaxation** replaces the binary restriction with \(0\le x_j\le1\). Every integer-feasible solution is feasible for that relaxation, so its maximum value is an upper bound on the integer optimum. The bound is useful even when its fractional action cannot be implemented.

## Key terms

- **Mixed-integer linear program:** An optimization with a linear objective and constraints in which some variables must take integer values.
- **Integrality:** The restriction that a decision such as selecting a project is 0 or 1 rather than fractional.
- **Linear relaxation:** The problem with each binary restriction replaced by bounds from 0 to 1, whose optimum is an upper bound on the integer maximum.
- **Optimality gap:** The distance between the best feasible incumbent and the best bound, which limits any claim of exact optimality.

## Worked case 1: solve and validate the binary allocation

The mixed-integer solver selects projects two and three, using the full budget and producing value 14. The program verifies the exact decision, value, integrality and resource feasibility. Those checks are distinct: an integral result can violate the budget, and a feasible fractional result is not an implementable binary allocation.

For this tiny problem, every subset can also be enumerated. That makes it suitable for an independent test oracle. A larger problem usually needs a solver's incumbent, bound and termination information, but the small enumerated case helps verify that the formulation means what the author intended.

A success flag should be interpreted with the solver's documented status and tolerances. If a solver stops early, the best feasible incumbent and the bound on the optimum may still support a useful decision. They do not establish exact optimality unless the stated gap and assumptions justify that claim.

## Worked case 2: rounding violates the resource constraint

The relaxation prioritizes the first project's value-per-cost ratio and then selects part of the second. Rounding both selected fractions to one exceeds the budget. The program asserts this violation rather than presenting the rounded vector as a near-optimal solution.

Rounding down avoids this particular violation but can leave value unused, and it is not generally optimal either. Feasibility-preserving heuristics may be useful when exact optimization is too expensive, but they need a declared algorithm and evaluation. A comparison with an optimistic relaxation bound can indicate how much improvement remains possible without claiming that the bound itself is an attainable policy.

The apparent simplicity of a binary variable can conceal modeling choices. A project may require setup costs, dependencies, minimum allocations or mutually exclusive alternatives. These belong in explicit constraints and variables. Trying to represent them through a score adjustment can change the feasible set in ways that are difficult to audit.

## Numerical and operational review

Large penalty constants can weaken relaxations and create poor numerical conditioning. Use the smallest justified bound when constructing a big-M formulation, and consider indicator or alternative formulations supported by the selected solver. A coefficient named penalty is not evidence that an invalid action has truly been ruled out.

After solving, validate the decisions in the same units and precision used by the consuming system. Currency rounding, integer conversions and stale capacity values can invalidate a mathematically feasible solution. Keep a record of the exact input snapshot and revalidate when material inputs change.

Uncertainty in project values is also important. Optimizing noisy estimates tends to favor unusually optimistic errors. Compare decisions across plausible parameter scenarios, use appropriate uncertainty or robust formulations, and evaluate the complete estimated-value-to-decision procedure. Optimization is not a substitute for statistical evaluation.

## Answered scientific discussion

**Is a continuous relaxation useless because it cannot be deployed?** No. It supplies bounds and structural information and is central to many exact algorithms. The error is treating a fractional optimum as an already feasible discrete decision.

**When should a time-limited result be reported?** Report the feasible incumbent, the best bound, the gap, the time limit and any violated assumptions. A transparent bounded result can be more useful than an unsupported claim that a solver found the global answer.

## Worked example: Enumeration, relaxation bound and rounding up

```python
from itertools import product
import numpy as np
from scipy.optimize import linprog

value = np.array([10, 13, 7, 8])
weight = np.array([4, 6, 3, 5])
cap = 10

best = max(
    ((value @ np.array(z), z) for z in product((0, 1), repeat=4) if weight @ np.array(z) <= cap)
)
print("exact integer optimum:", best[0], "choice", best[1])

lp = linprog(-value, A_ub=[weight], b_ub=[cap], bounds=[(0, 1)] * 4, method="highs")
print("LP relaxation bound:", round(-lp.fun, 4), "x =", lp.x.round(4))
up = np.ceil(lp.x - 1e-9) + 0.0
print("rounded up:", up, "weight", weight @ up, "value", value @ up)
down = np.floor(lp.x + 1e-9)
print("rounded down:", down, "weight", weight @ down, "value", value @ down)
print("optimality gap of rounding down:", best[0] - value @ down)
```

Observed output:

```text
exact integer optimum: 23 choice (1, 1, 0, 0)
LP relaxation bound: 23.5 x = [1.  0.5 1.  0. ]
rounded up: [1. 1. 1. 0.] weight 13.0 value 30.0
rounded down: [1. 0. 1. 0.] weight 7.0 value 17.0
optimality gap of rounding down: 6.0
```

Enumerating all 16 subsets finds the best feasible choice: items 1 and 2, weight 10 and value 23. The linear relaxation reaches 23.5 by taking half of item 2, and because every integer solution is also feasible for the relaxation, 23.5 is a certified upper bound. The integer optimum is within 0.5 of it, so a branch-and-bound solver holding the incumbent 23 can prove it is within 0.5, about 2.1 percent, of optimal without enumerating anything else. Rounding the relaxation is not a solution method. Rounding up yields weight 13, three units over capacity, with an attractive but meaningless value of 30. Rounding down is feasible at weight 7 but leaves value 17, six below the optimum, because it discards the high-value item 2 instead of swapping out item 3. The relaxation ranks items by value per unit weight (item 1 at 2.5, item 3 at 2.33, item 2 at 2.17), which is why it fills item 3 before item 2 even though item 2 belongs in the integer answer.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import optimize


def run_cases():
    value = np.array([10.0, 8.0, 6.0])
    cost = np.array([6.0, 5.0, 4.0])
    fit = optimize.milp(
        -value,
        integrality=np.ones(3),
        bounds=optimize.Bounds(0, 1),
        constraints=optimize.LinearConstraint(cost, -np.inf, 9),
    )
    assert fit.success and np.allclose(fit.x, [0, 1, 1]) and np.isclose(-fit.fun, 14)
    relaxed = optimize.linprog(-value, A_ub=[cost], b_ub=[9], bounds=[(0, 1)] * 3, method="highs")
    rounded = np.rint(relaxed.x)
    assert relaxed.success and -relaxed.fun > -fit.fun
    assert cost @ rounded > 9
    # Integrality and feasibility are checked separately from a solver status.
    integral = np.allclose(fit.x, np.round(fit.x), atol=1e-7)
    feasible = cost @ fit.x <= 9 + 1e-7
    return dict(
        binary=fit.x.tolist(),
        integer_value=-fit.fun,
        relaxation_bound=-relaxed.fun,
        rounded_cost=float(cost @ rounded),
        integral=bool(integral),
        feasible=bool(feasible),
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-017 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [SciPy mixed-integer optimization](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html)
- [SciPy linear programming and marginal values](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html)
