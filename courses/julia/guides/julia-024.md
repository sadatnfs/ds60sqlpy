# julia-024: Numerical methods, stability and error contracts

## Starting point and outcome

Advanced; approximately 150 minutes. Direct prerequisites: `julia-019`, `julia-020`, `julia-023`.

Compare explicit numerical approximations with known solutions and distinguish stability, positivity, residuals and position error.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## A finite answer is not necessarily an accurate answer

Numerical methods approximate mathematical problems under finite computation and representation. Their errors can come from discretization, roundoff, conditioning or a mismatch between the mathematical model and the real process. These sources should not be collapsed into one vague claim that a solver worked.

For exponential decay \(x'(t)=-\lambda x(t)\) with unit initial value, the exact solution is \(e^{-\lambda t}\). Explicit Euler uses \(x_{k+1}=(1-\lambda\Delta t)x_k\). The dimensionless product \(\lambda\Delta t\) controls important behavior. Stability of the multiplier and preservation of positivity are different conditions.

The unit implements small transparent methods directly. It does not claim to provide the full adaptivity, stiffness handling or diagnostics of a dedicated scientific differential-equation package. Such packages require separate environment preparation and their own problem-specific evidence.

## Worked case A: refine a decay approximation

The first program compares coarse and fine Euler steps with the analytic solution. It also examines a step size that causes an unphysical sign change. A bounded Plotly figure displays the exact and approximate paths with an accessible table. Looking only at the final value could miss an invalid intermediate path.

```julia
using Test
using .DS60Plots

function euler_decay(rate, steps)
    steps isa Integer && !(steps isa Bool) && steps > 0 && isfinite(rate) && rate >= 0 ||
        throw(ArgumentError("Positive steps and finite nonnegative rate required"))
    values = ones(steps+1)
    step = 1/steps
    for index = 1:steps
        values[index+1] = (1-rate*step)*values[index]
    end
    return collect(range(0.0, 1.0; length = steps+1)), values
end

function bisect(function_value, left, right; tolerance = 1e-10, maxiter = 100)
    isfinite(left) &&
    isfinite(right) &&
    left < right &&
    isfinite(tolerance) &&
    tolerance > 0 &&
    maxiter isa Integer &&
    !(maxiter isa Bool) &&
    maxiter > 0 || throw(ArgumentError("Valid bracket and budget required"))
    a, b = function_value(left), function_value(right)
    isfinite(a) && isfinite(b) || throw(ArgumentError("Finite endpoint values required"))
    a == 0 && return left
    b == 0 && return right
    signbit(a) != signbit(b) || throw(ArgumentError("A sign-changing bracket is required"))
    for _ = 1:maxiter
        middle = left/2 + right/2
        value = function_value(middle)
        isfinite(value) || throw(ArgumentError("Finite interior value required"))
        (right-left)/2 <= tolerance && return middle
        value == 0 && return middle
        if signbit(value) == signbit(a)
            left, a = middle, value
        else
            right, b = middle, value
        end
    end
    error("Iteration budget exhausted")
end

function worked_a()
    coarse_time, coarse = euler_decay(1.0, 4)
    fine_time, fine = euler_decay(1.0, 20)
    @test coarse[end] == (3/4)^4
    @test fine[end] ≈ (19/20)^20
    @test abs(fine[end]-exp(-1)) < abs(coarse[end]-exp(-1))
    _, unstable = euler_decay(3.0, 1)
    _, alternating = euler_decay(3.0, 2)
    @test unstable == [1, -2]
    @test alternating == [1, -0.5, 0.25]
    exact = exp.(-fine_time)
    data = [
        Dict("type"=>"scatter", "x"=>fine_time, "y"=>exact, "mode"=>"lines", "name"=>"Exact"),
        Dict(
            "type"=>"scatter",
            "x"=>coarse_time,
            "y"=>coarse,
            "mode"=>"lines+markers",
            "name"=>"Euler 4",
        ),
        Dict("type"=>"scatter", "x"=>fine_time, "y"=>fine, "mode"=>"lines", "name"=>"Euler 20"),
    ]
    layout = Dict(
        "title"=>"Explicit Euler error under a known decay model",
        "meta"=>Dict(
            "description"=>"For rate 1 over unit time, 20 Euler steps are closer to the analytic path than 4. Stability and positivity are separate conditions.",
            "table"=>Dict(
                "columns"=>["Time", "Exact state", "Euler 20 state"],
                "rows"=>[[fine_time[i], exact[i], fine[i]] for i in eachindex(fine)],
            ),
        ),
    )
    show_plotly(
        data;
        layout = layout,
        description = "Known decay solution and Euler approximations",
    )
    println("Final Euler errors: ", coarse[end]-exp(-1), "; ", fine[end]-exp(-1))
end

worked_a()
```

## Worked case B: bracket a root

Bisection narrows a sign-changing interval for a continuous function. Its interval width provides a position-error contract under that continuity and bracketing assumption. A small function residual is a different quantity with different units. The helper rejects a missing bracket and raises an explicit error if its iteration budget cannot satisfy the requested width.

```julia
using Test
using .DS60Plots

function euler_decay(rate, steps)
    steps isa Integer && !(steps isa Bool) && steps > 0 && isfinite(rate) && rate >= 0 ||
        throw(ArgumentError("Positive steps and finite nonnegative rate required"))
    values = ones(steps+1)
    step = 1/steps
    for index = 1:steps
        values[index+1] = (1-rate*step)*values[index]
    end
    return collect(range(0.0, 1.0; length = steps+1)), values
end

function bisect(function_value, left, right; tolerance = 1e-10, maxiter = 100)
    isfinite(left) &&
    isfinite(right) &&
    left < right &&
    isfinite(tolerance) &&
    tolerance > 0 &&
    maxiter isa Integer &&
    !(maxiter isa Bool) &&
    maxiter > 0 || throw(ArgumentError("Valid bracket and budget required"))
    a, b = function_value(left), function_value(right)
    isfinite(a) && isfinite(b) || throw(ArgumentError("Finite endpoint values required"))
    a == 0 && return left
    b == 0 && return right
    signbit(a) != signbit(b) || throw(ArgumentError("A sign-changing bracket is required"))
    for _ = 1:maxiter
        middle = left/2 + right/2
        value = function_value(middle)
        isfinite(value) || throw(ArgumentError("Finite interior value required"))
        (right-left)/2 <= tolerance && return middle
        value == 0 && return middle
        if signbit(value) == signbit(a)
            left, a = middle, value
        else
            right, b = middle, value
        end
    end
    error("Iteration budget exhausted")
end

function worked_b()
    root = bisect(x -> x^2-2, 0.0, 2.0)
    @test abs(root-sqrt(2)) <= 1e-10
    @test abs(root^2-2) < 1e-8
    @test_throws ArgumentError bisect(x -> x^2+1, -1.0, 1.0)
    @test_throws ErrorException bisect(x -> x^2-2, 0.0, 2.0; maxiter = 1)
    println("Bracketed root: ", root)
end

worked_b()
```

## State assumptions separately from software guards

A sign change alone does not prove a root for an arbitrary discontinuous function. The method relies on continuity, which cannot be established by a finite set of evaluations. Similarly, a stable Euler multiplier does not guarantee the model is scientifically correct, and it can permit alternating signs that violate a positive-state interpretation.

Quadrature has its own approximation contract. A trapezoidal rule can be checked against a known integral and refined on the same function. A better result for a smooth polynomial does not certify every discontinuous, singular or noisy integrand.

## Diagnose error sources

Vary a relevant resolution or tolerance while preserving the problem definition. Inspect whether changes are consistent with the method's assumptions. A result that stops improving can reflect roundoff, conditioning or another error source. Do not interpret a smaller reported internal tolerance as an automatic guarantee of better scientific accuracy.

Keep units visible. A root-position tolerance is measured in input units, while a residual has function-value units. A time step is measured in time, while the decay rate has inverse-time units. Confusing those scales can produce a numerically precise answer to an incorrectly specified problem.

The programs use known small problems and deterministic checks. They establish the displayed arithmetic, failure paths and chart output in the prepared Julia runtime. They do not qualify a large simulation, a production solver or an accelerator implementation. Transfer requires a problem-specific numerical and scientific argument.


## Six investigations

### 1. Refine the time step

Compare Euler with 4 and 20 steps for rate 1.

**Expected:** The fine final value is closer to exp(-1).

**Hint:** Use the analytic solution as an independent reference.

### 2. Inspect the complete path

Use rate 3 with 2 Euler steps.

**Expected:** The path includes a negative intermediate value.

**Hint:** Stability and positivity have different requirements.

### 3. Require a root bracket

Try x squared plus 1 on[-1,1].

**Expected:** The helper rejects the absent sign change.

**Hint:** The bracketing invariant must hold before iteration.

### 4. Bound the iteration budget

Allow only one bisection iteration for square-root 2.

**Expected:** The helper reports budget exhaustion.

**Hint:** Do not label the last iterate converged automatically.

### 5. Compare quadrature resolution

Integrate x squared using the two trapezoidal grids.

**Expected:** The refined approximation is closer to 1/3.

**Hint:** Keep the function and interval unchanged.

### 6. Name tolerance units

Compare a root-position tolerance with a function residual.

**Expected:** They have different units and meanings.

**Hint:** The derivative scale connects them only under additional conditions.

## Primary references

- [Julia numerical operations](https://docs.julialang.org/en/v1/stdlib/LinearAlgebra/)
- [Existing scientific numerical foundations](../../../courses/jax/README.md)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
