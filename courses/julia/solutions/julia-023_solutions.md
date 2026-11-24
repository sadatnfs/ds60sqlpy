# julia-023: explained reference

The executable reference is `julia-023_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Check the problem before the solver. `objective(x) = (x[1]-1)^2 + 4(x[2]+2)^2` is a convex quadratic with minimum 0 at `[1, -2]`. Worked example A runs BFGS with a ForwardDiff gradient, and worked example B minimizes `(x-3)^2` over the interval from 0 to 2. Convergence evidence combines the point, objective value and gradient norm.

## 1. Check the objective sign

Successful numerical progress cannot validate a mistaken objective definition.

**Expected observation:** The mathematical problem changes.

**Why it holds here:** Negating the quadratic makes it unbounded below, so a minimizer moves away from `[1, -2]` without end.

**Plausible wrong approach:** Flipping the sign to turn a maximization into minimization and forgetting to flip it back optimizes the opposite goal.

**How to verify:** Evaluate `-objective` at points farther from `[1, -2]` and confirm it keeps decreasing.

## 2. Verify the known optimum

The test supports this convex fixture rather than a blanket global-convergence claim.

**Expected observation:** Objective and gradient are zero.

**Why it holds here:** At `[1, -2]` both squared terms are zero, so the objective is 0 and its gradient `[2(x1-1), 8(x2+2)]` is zero.

**Plausible wrong approach:** Trusting only the solver's returned point skips an independent check that this point is actually optimal.

**How to verify:** The reference asserts `objective([1.0, -2.0]) == 0`, a zero gradient there, and values 1 and 4 at nearby points.

## 3. Inspect the feasible set

Constraints are part of the problem, not an optional display filter.

**Expected observation:** The best feasible point is near 2.

**Why it holds here:** `(x-3)^2` decreases on the interval from 0 to 2, so the bounded minimizer is the endpoint 2, with value 1.

**Plausible wrong approach:** Solving without bounds and then clamping 3 to 2 happens to work here but fails for objectives whose clamped point is not optimal.

**How to verify:** Example B asserts `abs(point-2) < 1e-5` and a minimum near 1; the reference checks `(x-0.5)^2` gives 0.5 inside the interval.

## 4. Read convergence evidence

Independent mathematical checks make the optimization result more interpretable.

**Expected observation:** They agree with the known quadratic solution.

**Why it holds here:** Example A checks `point ≈ [1, -2]`, `Optim.minimum(result) < 1e-12`, a gradient norm below 1e-6 and `Optim.converged(result)`.

**Plausible wrong approach:** Reading only the converged flag accepts a run that stopped by a tolerance on a wrong objective or a poor starting point.

**How to verify:** Print the point, objective and `norm(ForwardDiff.gradient(objective, point))` together.

## 5. Scale a parameter

Conditioning improvements should retain the original interpretation and feasible decisions.

**Expected observation:** Update penalties and constraints consistently.

**Why it holds here:** If `x[2]` is changed from meters to centimeters, the weight 4 and the offset 2 must change with it to describe the same problem.

**Plausible wrong approach:** Rescaling a parameter for faster convergence but leaving the penalty and bounds in the old units solves a different problem.

**How to verify:** Map the rescaled optimum back to original units and confirm it equals `[1, -2]`.

## 6. Assess a fitted model

A better fit can still reflect overfitting, leakage or a poor target.

**Expected observation:** Evaluate the frozen procedure on independent data.

**Why it holds here:** A lower training objective only shows that the optimizer fit these data better, not that predictions improve elsewhere.

**Plausible wrong approach:** Reporting the drop in training loss as evidence of model quality ignores overfitting and leakage.

**How to verify:** Freeze the fitted procedure and evaluate it on held-out data, as lesson julia-021 does with its final rows.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-023: all reference checks passed`:

```julia
function exercise_checks()
    @test objective([1.0, -2.0]) == 0
    @test ForwardDiff.gradient(objective, [1.0, -2.0]) == [0, 0]
    @test objective([2.0, -2.0]) == 1
    @test objective([1.0, -1.0]) == 4
    scalar = Optim.optimize(x -> (x-0.5)^2, 0.0, 2.0)
    @test abs(Optim.minimizer(scalar)-0.5) < 1e-5
    @test Optim.minimum(scalar) < 1e-8
end
```
