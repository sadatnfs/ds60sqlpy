## Discrete actions require discrete models

Many decisions cannot be divided continuously: a project is selected or not, a facility is opened or closed, and a person is assigned to one shift. A continuous relaxation can be useful for reasoning and bounds, but rounding its solution is not a general mixed-integer optimization algorithm.

The fixture has three projects with values 10,8,6 and costs 6,5,4. A budget of nine permits binary decisions \(x_j\in\{0,1\}\). The objective is \(\max\sum_j v_jx_j\), subject to \(\sum_j c_jx_j\le9\). The implementation again negates the objective because SciPy's `milp` minimizes.

The **linear relaxation** replaces the binary restriction with \(0\le x_j\le1\). Every integer-feasible solution is feasible for that relaxation, so its maximum value is an upper bound on the integer optimum. The bound is useful even when its fractional action cannot be implemented.

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
