# julia-022: Forward-mode automatic differentiation

## Starting point and outcome

Advanced; approximately 150 minutes. Direct prerequisites: `julia-012`, `julia-019`.

Differentiate supported numerical functions and validate derivatives while preserving the numeric representation carried by dual numbers.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## Automatic differentiation follows the implemented computation

Forward-mode automatic differentiation propagates derivative information through supported numerical operations. A dual number carries a value and partial information. Arithmetic combines both components according to differentiation rules. This is different from estimating a derivative by subtracting nearby function values or manipulating a symbolic formula.

ForwardDiff supplies derivative, gradient, Jacobian and Hessian operations for suitable Julia functions. Their input/output shapes matter. A gradient belongs to a scalar-valued function of a vector; a Jacobian describes a vector-valued function; a Hessian describes second derivatives of a scalar function. A correct shape does not establish that the chosen function is the right scientific objective.

Type-generic code is essential. Hardcoding an intermediate buffer as Float64 can reject the dual values needed to propagate derivatives. Use an appropriate input-derived representation when the algorithm is intended to support such values, and avoid silently converting away derivative information.

## Worked case A: independent analytic derivatives

The scalar quadratic has a known gradient and Hessian. A second vector function has a known Jacobian. The program compares ForwardDiff's results to those hand-derived arrays, making axes and coefficients explicit. A finite-difference directional check adds a separate numerical perspective without being treated as the definition of the derivative.

```julia
using Test
using LinearAlgebra
using ForwardDiff

quadratic(x) = x[1]^2 + 3x[2]^2
vector_function(x) = [x[1]^2 + x[2], x[1] * x[2]]

function hardcoded_storage(x)
    output = zeros(Float64, length(x))
    output .= x .^ 2
    return sum(output)
end

function generic_storage(x)
    output = similar(x)
    output .= x .^ 2
    return sum(output)
end

function worked_a()
    x = [2.0, 3.0]
    @test ForwardDiff.gradient(quadratic, x) ≈ [4, 18]
    @test ForwardDiff.hessian(quadratic, x) ≈ [2 0; 0 6]
    @test ForwardDiff.jacobian(vector_function, x) ≈ [4 1; 3 2]
    direction = [1.0, -1.0]
    step = 1e-5
    finite_difference = (quadratic(x + step*direction) - quadratic(x - step*direction)) / (2step)
    @test isapprox(finite_difference, dot([4, 18], direction); atol = 1e-8)
    println("Gradient: ", ForwardDiff.gradient(quadratic, x))
end

worked_a()
```

## Worked case B: a storage mistake blocks differentiation

One function writes into a Float64 buffer, while another uses `similar` on its input. Ordinary Float64 evaluation succeeds in both. Differentiation fails in the hardcoded-storage version because it cannot retain the required numeric type, while the generic version produces the expected derivative. The failure is a representation issue, not evidence that the mathematical function lacks a derivative.

```julia
using Test
using LinearAlgebra
using ForwardDiff

quadratic(x) = x[1]^2 + 3x[2]^2
vector_function(x) = [x[1]^2 + x[2], x[1] * x[2]]

function hardcoded_storage(x)
    output = zeros(Float64, length(x))
    output .= x .^ 2
    return sum(output)
end

function generic_storage(x)
    output = similar(x)
    output .= x .^ 2
    return sum(output)
end

function worked_b()
    x = [2.0, 3.0]
    @test hardcoded_storage(x) == 13
    @test generic_storage(x) == 13
    @test_throws MethodError ForwardDiff.gradient(hardcoded_storage, x)
    @test ForwardDiff.gradient(generic_storage, x) ≈ [4, 6]
    println("Generic storage retains derivative information")
end

worked_b()
```

## Boundaries and nonsmooth operations

Automatic differentiation computes derivatives of the executed supported path. At a branch boundary or a nonsmooth point, the mathematical derivative may not exist or the returned convention may need careful interpretation. A value produced by an AD library is not a proof of differentiability. Diagnose the function and its domain independently.

Finite differences have their own tradeoff: a large step introduces approximation error, while a tiny step can amplify floating-point cancellation. Use a range of sensible steps and analytic cases when validating a new differentiable implementation. Do not widen a tolerance to hide an incorrect gradient shape or reduction.

## Transfer to scientific models

Check units and scaling of the objective and parameters. A sum and a mean loss have different gradient scales. Hidden state, randomness and data-dependent transformations can also change what function is being differentiated. Keep these inputs explicit and freeze any information that should not receive derivative updates.

The reference uses small CPU functions with prepared ForwardDiff. It does not qualify GPU differentiation, every external library operation or a large model's optimization behavior. Later optimization uses these derivatives as one component while still checking convergence, objective values and independent scientific assumptions.


## Six investigations

### 1. Differentiate analytically

Compute the gradient of x1 squared plus 3x2 squared at[2,3].

**Expected:** The result is[4,18].

**Hint:** Differentiate each coordinate separately.

### 2. Check Jacobian axes

Differentiate the vector-valued function.

**Expected:** Rows correspond to outputs and columns to inputs.

**Hint:** Inspect the stated function shapes.

### 3. Preserve numeric types

Replace a hardcoded Float64 buffer with similar(x).

**Expected:** The dual-number path can retain derivative information.

**Hint:** Use the input representation when the contract is generic.

### 4. Compare reductions

Differentiate a sum and a mean of two inputs.

**Expected:** Gradients are[1,1] and[0.5,0.5].

**Hint:** The denominator is part of the objective.

### 5. Inspect a branch boundary

Evaluate a nonsmooth function near its kink.

**Expected:** A library result needs a differentiability interpretation.

**Hint:** The executed branch is not a symbolic proof.

### 6. Validate a new gradient

Compare analytic or finite-difference directional behavior at several valid inputs.

**Expected:** Use meaningful tolerances and retain failures.

**Hint:** Separate approximation error from a wrong formula.

## Primary references

- [ForwardDiff differentiation API](https://juliadiff.org/ForwardDiff.jl/stable/user/api/)
- [ForwardDiff limitations](https://juliadiff.org/ForwardDiff.jl/stable/user/limitations/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
