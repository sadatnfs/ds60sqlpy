# julia-024: explained reference

The executable reference is `julia-024_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Compare each approximation with something known exactly. `euler_decay` applies the update `(1 - rate*step) * value` and returns the time grid and path; `bisect` requires a finite sign-changing bracket and a positive iteration budget, then halves the interval until the half-width is within `tolerance`. The trapezoidal rule integrates `x^2` on the interval from 0 to 1, whose exact value is 1/3.

## 1. Refine the time step

This checks the stated smooth problem and does not imply that every refinement improves every numerical task.

**Expected observation:** The fine final value is closer to `exp(-1)`.

**Why it holds here:** With rate 1, 4 steps give (3/4)^4 = 0.31640625 and 20 steps give (19/20)^20, which is closer to exp(-1).

**Plausible wrong approach:** Assuming any refinement must help without measuring the error against exp(-1) misses cases where rounding or instability dominates.

**How to verify:** Example A asserts `coarse[end] == (3/4)^4` and that the fine error is smaller than the coarse error.

## 2. Inspect the complete path

A positive final value alone can hide an unphysical intermediate state.

**Expected observation:** The path includes a negative intermediate value.

**Why it holds here:** Rate 3 with step 1/2 gives the factor 1 - 1.5 = -0.5, so the path is `[1, -0.5, 0.25]` and passes through a negative value.

**Plausible wrong approach:** Inspecting only the final 0.25 suggests a sensible decay and hides the negative concentration in the middle.

**How to verify:** Example A asserts `alternating == [1, -0.5, 0.25]` and `unstable == [1, -2]` for one step.

## 3. Require a root bracket

A numerical routine cannot create a real root where the stated evidence does not support one.

**Expected observation:** The helper rejects the absent sign change.

**Why it holds here:** `x^2 + 1` equals 2 at both -1 and 1, so the signs match and `bisect` throws `ArgumentError` before iterating.

**Plausible wrong approach:** Iterating anyway on the midpoint returns some number in the interval that is not a root of a function with no real root.

**How to verify:** Example B asserts `@test_throws ArgumentError bisect(x -> x^2+1, -1.0, 1.0)`.

## 4. Bound the iteration budget

A stopped computation needs a clear termination reason and evidence about its remaining error.

**Expected observation:** The helper reports budget exhaustion.

**Why it holds here:** With `maxiter = 1`, the half-width of 1 after one step is far above the tolerance, so the loop ends and `error` raises.

**Plausible wrong approach:** Returning the last midpoint as if it were converged hides that the accuracy target was never reached.

**How to verify:** Example B asserts `@test_throws ErrorException bisect(x -> x^2-2, 0.0, 2.0; maxiter = 1)`.

## 5. Compare quadrature resolution

A known integral helps separate discretization error from implementation errors.

**Expected observation:** The refined approximation is closer to 1/3.

**Why it holds here:** The coarse grid with step 0.5 gives 0.375, and the step 0.1 grid gives a value closer to 1/3.

**Plausible wrong approach:** Changing the interval or function between the two runs makes the comparison meaningless as a test of grid size.

**How to verify:** The reference asserts `coarse == 0.375` and `abs(fine-1/3) < abs(coarse-1/3)`.

## 6. Name tolerance units

A small residual alone does not always imply a small position error in an ill-conditioned problem.

**Expected observation:** They have different units and meanings.

**Why it holds here:** A position tolerance is measured in x, while a residual is measured in f; near sqrt(2) they are linked by the slope f'(x) = 2x.

**Plausible wrong approach:** Using a tiny residual as proof of a tiny position error fails for flat functions, where small residuals allow large position errors.

**How to verify:** Example B checks both `abs(root-sqrt(2)) <= 1e-10` and `abs(root^2-2) < 1e-8`; report each with its unit.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-024: all reference checks passed`:

```julia
function exercise_checks()
    @test_throws ArgumentError euler_decay(1, 0)
    @test euler_decay(0, 3)[2] == ones(4)
    @test bisect(x -> x, 0.0, 2.0) == 0
    x = collect(0.0:0.5:1.0)
    y = x .^ 2
    coarse = sum(diff(x) .* (y[1:(end-1)] .+ y[2:end]))/2
    xf = collect(0.0:0.1:1.0)
    yf = xf .^ 2
    fine = sum(diff(xf) .* (yf[1:(end-1)] .+ yf[2:end]))/2
    @test coarse == 0.375
    @test abs(fine-1/3) < abs(coarse-1/3)
end
```
