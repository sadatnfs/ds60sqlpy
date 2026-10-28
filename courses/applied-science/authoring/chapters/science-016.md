## Optimization needs a scientific input contract

An optimizer chooses an action for the objective and constraints supplied. It does not decide whether the coefficients represent the right causal effects, forecast distribution or operational costs. Before interpreting a solution, define units, feasible actions and the origin of every coefficient.

The example maximizes \(3x_1+2x_2\) subject to two resource constraints, \(x_1+x_2\le b\) and \(2x_1+x_2\le8\), with nonnegative activities. The implementation minimizes the negative objective because that is the solver's convention. Confusing maximization signs with minimization marginals is a common source of incorrectly interpreted shadow prices.

For a locally stable optimum, a constraint's dual value describes the derivative of optimal value with respect to its bound. That is a local statement about the specified mathematical problem. It is not a universal price valid for every expansion, and it is not necessarily a market price or causal business benefit.

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
