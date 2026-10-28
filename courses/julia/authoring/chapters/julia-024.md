## A finite answer is not necessarily an accurate answer

Numerical methods approximate mathematical problems under finite computation and representation. Their errors can come from discretization, roundoff, conditioning or a mismatch between the mathematical model and the real process. These sources should not be collapsed into one vague claim that a solver worked.

For exponential decay \(x'(t)=-\lambda x(t)\) with unit initial value, the exact solution is \(e^{-\lambda t}\). Explicit Euler uses \(x_{k+1}=(1-\lambda\Delta t)x_k\). The dimensionless product \(\lambda\Delta t\) controls important behavior. Stability of the multiplier and preservation of positivity are different conditions.

The unit implements small transparent methods directly. It does not claim to provide the full adaptivity, stiffness handling or diagnostics of a dedicated scientific differential-equation package. Such packages require separate environment preparation and their own problem-specific evidence.

## Worked case A: refine a decay approximation

The first program compares coarse and fine Euler steps with the analytic solution. It also examines a step size that causes an unphysical sign change. A bounded Plotly figure displays the exact and approximate paths with an accessible table. Looking only at the final value could miss an invalid intermediate path.

{{WORKED_A}}

## Worked case B: bracket a root

Bisection narrows a sign-changing interval for a continuous function. Its interval width provides a position-error contract under that continuity and bracketing assumption. A small function residual is a different quantity with different units. The helper rejects a missing bracket and raises an explicit error if its iteration budget cannot satisfy the requested width.

{{WORKED_B}}

## State assumptions separately from software guards

A sign change alone does not prove a root for an arbitrary discontinuous function. The method relies on continuity, which cannot be established by a finite set of evaluations. Similarly, a stable Euler multiplier does not guarantee the model is scientifically correct, and it can permit alternating signs that violate a positive-state interpretation.

Quadrature has its own approximation contract. A trapezoidal rule can be checked against a known integral and refined on the same function. A better result for a smooth polynomial does not certify every discontinuous, singular or noisy integrand.

## Diagnose error sources

Vary a relevant resolution or tolerance while preserving the problem definition. Inspect whether changes are consistent with the method's assumptions. A result that stops improving can reflect roundoff, conditioning or another error source. Do not interpret a smaller reported internal tolerance as an automatic guarantee of better scientific accuracy.

Keep units visible. A root-position tolerance is measured in input units, while a residual has function-value units. A time step is measured in time, while the decay rate has inverse-time units. Confusing those scales can produce a numerically precise answer to an incorrectly specified problem.

The programs use known small problems and deterministic checks. They establish the displayed arithmetic, failure paths and chart output in the prepared Julia runtime. They do not qualify a large simulation, a production solver or an accelerator implementation. Transfer requires a problem-specific numerical and scientific argument.
