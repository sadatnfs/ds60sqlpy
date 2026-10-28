# julia-023: Optimization objectives, constraints and convergence

## Starting point and outcome

Advanced; approximately 150 minutes. Direct prerequisites: `julia-021`, `julia-022`.

Use a prepared optimization library while checking the objective, feasible set and independent convergence evidence.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## Specify the optimization problem first

An optimizer searches for a point that improves a stated objective under a stated feasible set. The algorithm name does not determine whether the objective represents the scientific question. A mistaken sign, reduction or parameterization can be optimized successfully while solving the wrong problem.

The prepared Optim package supports several methods. This unit uses a gradient-based method for a small smooth vector problem and a bounded method for a scalar problem. ForwardDiff supplies an explicit gradient callback. The code records the final point and objective, then checks them against known mathematical solutions.

A convergence flag is a diagnostic under an algorithm's stopping criteria. It is not a universal proof of a global optimum, especially for nonconvex objectives. Inspect residual gradients, objective values, feasibility and sensitivity to starting points where those checks are relevant.

## Worked case A: minimize a convex quadratic

The first objective has a unique known minimum at[1,-2]. Its gradient is supplied through ForwardDiff using an in-place callback. The program checks the returned point, objective value and gradient norm independently of the optimizer's status flag. The small convex construction makes a global conclusion possible because of its mathematical structure, not because the method is named BFGS.

```julia
using Test
using LinearAlgebra
using ForwardDiff
using Optim

objective(x) = (x[1]-1)^2 + 4(x[2]+2)^2
function objective_gradient!(storage, x)
    ForwardDiff.gradient!(storage, objective, x)
    return nothing
end

function worked_a()
    result = Optim.optimize(
        objective,
        objective_gradient!,
        [5.0, 5.0],
        Optim.BFGS(),
        Optim.Options(iterations = 200, show_trace = false),
    )
    point = Optim.minimizer(result)
    @test point ≈ [1, -2]
    @test Optim.minimum(result) < 1e-12
    @test norm(ForwardDiff.gradient(objective, point)) < 1e-6
    @test Optim.converged(result)
    println("Quadratic optimizer: ", point, "; objective: ", Optim.minimum(result))
end

worked_a()
```

## Worked case B: a feasible boundary changes the answer

The scalar objective has an unconstrained minimum at 3, but the feasible interval is 0 through 2. The constrained answer is at the upper boundary. Optimizing without the constraint and then describing the result as a feasible solution would answer another problem. The bounded solver's approximate location is tested with an explicit position tolerance.

```julia
using Test
using LinearAlgebra
using ForwardDiff
using Optim

objective(x) = (x[1]-1)^2 + 4(x[2]+2)^2
function objective_gradient!(storage, x)
    ForwardDiff.gradient!(storage, objective, x)
    return nothing
end

function worked_b()
    result = Optim.optimize(x -> (x-3)^2, 0.0, 2.0)
    point = Optim.minimizer(result)
    @test 0 <= point <= 2
    @test abs(point-2) < 1e-5
    @test isapprox(Optim.minimum(result), 1; atol = 1e-4)
    println("Bounded optimizer: ", point)
end

worked_b()
```

## Scaling and derivatives

Parameters with different units or scales can create an ill-conditioned search. A parameter transformation or objective scaling can help numerically, but its effect on constraints, penalties and interpretation must be retained. An optimizer cannot infer those scientific meanings from a vector of numbers.

Validate derivatives before using them to explain optimization behavior. A supplied gradient with the wrong sign or shape can cause failure or an apparently stable but incorrect result. The preceding unit's independent derivative checks remain useful. Finite-difference and AD gradients also have different implementation assumptions.

## Diagnose a stopped run

Inspect why a method stopped: convergence, iteration budget, invalid values or another condition. Report the starting point, algorithm, limits and final diagnostics. A finite final objective alone is weak evidence. Conversely, a failed convergence flag may require investigation rather than an automatic replacement of the result with a fabricated default.

For a nonconvex problem, compare meaningful starting points and retain local-optimum uncertainty. For a constrained problem, inspect the actual feasible-set definition. For a statistical fit, assess held-out behavior separately from training objective improvement.

The examples execute real CPU optimization in the prepared environment without downloading packages. They qualify the specific problems and API paths shown. Larger or specialized optimization ecosystems, distributed solvers and accelerator behavior require separate preparation and evidence.


## Six investigations

### 1. Check the objective sign

Replace a minimization objective with its negative.

**Expected:** The mathematical problem changes.

**Hint:** State whether the goal is minimization or maximization.

### 2. Verify the known optimum

Evaluate the quadratic at[1,-2].

**Expected:** Objective and gradient are zero.

**Hint:** Use the analytic structure independently.

### 3. Inspect the feasible set

Minimize the scalar case only on[0,2].

**Expected:** The best feasible point is near 2.

**Hint:** The unconstrained minimizer 3 is unavailable.

### 4. Read convergence evidence

Inspect the returned point, objective and gradient norm.

**Expected:** They agree with the known quadratic solution.

**Hint:** A status flag is only one diagnostic.

### 5. Scale a parameter

Change a parameter unit in a real objective.

**Expected:** Update penalties and constraints consistently.

**Hint:** A numeric rescaling can change the scientific specification.

### 6. Assess a fitted model

Observe a lower training objective after optimization.

**Expected:** Evaluate the frozen procedure on independent data.

**Hint:** Optimization and generalization are different questions.

## Primary references

- [Optim minimization guide](https://julianlsolvers.github.io/Optim.jl/stable/user/minimization/)
- [Optim convergence options](https://julianlsolvers.github.io/Optim.jl/stable/user/config/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
