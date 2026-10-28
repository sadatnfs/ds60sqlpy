## Specify the optimization problem first

An optimizer searches for a point that improves a stated objective under a stated feasible set. The algorithm name does not determine whether the objective represents the scientific question. A mistaken sign, reduction or parameterization can be optimized successfully while solving the wrong problem.

The prepared Optim package supports several methods. This unit uses a gradient-based method for a small smooth vector problem and a bounded method for a scalar problem. ForwardDiff supplies an explicit gradient callback. The code records the final point and objective, then checks them against known mathematical solutions.

A convergence flag is a diagnostic under an algorithm's stopping criteria. It is not a universal proof of a global optimum, especially for nonconvex objectives. Inspect residual gradients, objective values, feasibility and sensitivity to starting points where those checks are relevant.

## Worked case A: minimize a convex quadratic

The first objective has a unique known minimum at[1,-2]. Its gradient is supplied through ForwardDiff using an in-place callback. The program checks the returned point, objective value and gradient norm independently of the optimizer's status flag. The small convex construction makes a global conclusion possible because of its mathematical structure, not because the method is named BFGS.

{{WORKED_A}}

## Worked case B: a feasible boundary changes the answer

The scalar objective has an unconstrained minimum at 3, but the feasible interval is 0 through 2. The constrained answer is at the upper boundary. Optimizing without the constraint and then describing the result as a feasible solution would answer another problem. The bounded solver's approximate location is tested with an explicit position tolerance.

{{WORKED_B}}

## Scaling and derivatives

Parameters with different units or scales can create an ill-conditioned search. A parameter transformation or objective scaling can help numerically, but its effect on constraints, penalties and interpretation must be retained. An optimizer cannot infer those scientific meanings from a vector of numbers.

Validate derivatives before using them to explain optimization behavior. A supplied gradient with the wrong sign or shape can cause failure or an apparently stable but incorrect result. The preceding unit's independent derivative checks remain useful. Finite-difference and AD gradients also have different implementation assumptions.

## Diagnose a stopped run

Inspect why a method stopped: convergence, iteration budget, invalid values or another condition. Report the starting point, algorithm, limits and final diagnostics. A finite final objective alone is weak evidence. Conversely, a failed convergence flag may require investigation rather than an automatic replacement of the result with a fabricated default.

For a nonconvex problem, compare meaningful starting points and retain local-optimum uncertainty. For a constrained problem, inspect the actual feasible-set definition. For a statistical fit, assess held-out behavior separately from training objective improvement.

The examples execute real CPU optimization in the prepared environment without downloading packages. They qualify the specific problems and API paths shown. Larger or specialized optimization ecosystems, distributed solvers and accelerator behavior require separate preparation and evidence.
