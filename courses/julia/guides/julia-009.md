# julia-009: Errors, tests and explicit input contracts

## Starting point and outcome

Beginner; approximately 90 minutes. Direct prerequisites: `julia-006`, `julia-008`.

Validate scientific inputs, test expected failures and preserve unexpected errors instead of turning them into successful results.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## An error policy is part of an API

A calculation can fail because its input is outside the intended domain, because information is absent, or because the implementation has a defect. These situations deserve different handling. Returning an ordinary numeric value for every failure can make an invalid result look scientifically meaningful.

`throw` raises an exception. `try` and `catch` can handle an expected failure at a boundary. `rethrow` preserves an unexpected exception rather than replacing it with a misleading success. The standard `Test` library provides checks for values and expected exceptions. Tests should state the contract using inputs that expose normal and boundary behavior.

An assertion in a reference program is evidence about that declared fixture. It is not a substitute for validating external data at runtime. Conversely, a validator should check a meaningful invariant rather than merely catch every possible error and continue with a fabricated default.

## Worked case A: a finite nonempty mean

The helper requires a nonempty collection of finite numerical values. It rejects an empty input with `ArgumentError` and nonfinite measurements with `DomainError`. This policy differs deliberately from a function that returns an absent-value sentinel. The caller can distinguish a valid zero mean from a rejected calculation.

```julia
using Test
using Statistics

function finite_mean(values)
    isempty(values) && throw(ArgumentError("At least one observation is required"))
    all(isfinite, values) || throw(DomainError(values, "Observations must be finite"))
    return mean(values)
end

function outcome(values)
    try
        return (status = :ok, value = finite_mean(values))
    catch error
        if error isa ArgumentError || error isa DomainError
            return (status = :rejected, reason = sprint(showerror, error))
        end
        rethrow()
    end
end

function worked_a()
    @test finite_mean([1, 2, 3]) == 2
    @test finite_mean([-1, 1]) == 0
    @test_throws ArgumentError finite_mean(Float64[])
    @test_throws DomainError finite_mean([1.0, Inf])
    println("Finite mean: ", finite_mean([1, 2, 3]))
end

worked_a()
```

## Worked case B: a bounded outcome record

A boundary function converts only the two declared validation failures into a rejected outcome record. An unexpected method error is rethrown. The record retains a readable diagnostic and does not insert a numeric result for rejected input. This makes it possible to count rejected records without silently adding them to a valid-result denominator.

```julia
using Test
using Statistics

function finite_mean(values)
    isempty(values) && throw(ArgumentError("At least one observation is required"))
    all(isfinite, values) || throw(DomainError(values, "Observations must be finite"))
    return mean(values)
end

function outcome(values)
    try
        return (status = :ok, value = finite_mean(values))
    catch error
        if error isa ArgumentError || error isa DomainError
            return (status = :rejected, reason = sprint(showerror, error))
        end
        rethrow()
    end
end

function worked_b()
    valid = outcome([2, 4])
    invalid = outcome(Float64[])
    @test valid == (status = :ok, value = 3.0)
    @test invalid.status == :rejected
    @test occursin("observation", invalid.reason)
    @test_throws MethodError outcome(nothing)
    println("Rejected outcome: ", invalid)
end

worked_b()
```

## Build useful tests

Include a normal case, a boundary case and an input that must fail. Test exact integer or identity properties exactly. Use numerical tolerances only when a representation or algorithm justifies approximation. A tolerance should have a reason related to the quantity and its units, not simply be large enough to hide a mismatch.

When a test fails, inspect the expected value independently. Copying an implementation's formula into the assertion can reproduce the same mistake twice. Hand calculations, algebraic invariants, alternative formulations and known limiting cases provide stronger checks. Tests also need to verify that an expected error actually occurred rather than swallowing an arbitrary exception.

## Diagnosis and transfer

A stack trace identifies the sequence of calls leading to failure. Begin with the first relevant location in your own source and trace its inputs. A broad catch that replaces every exception with zero removes that evidence and can contaminate downstream statistics. Handle expected input failures deliberately and allow unexpected defects to remain visible.

For a real data pipeline, retain rejected-row counts, reasons and the input contract version. Do not reveal sensitive raw data unnecessarily in production diagnostics. The authored fixture here contains no personal data and uses very small values so the failure mechanism is inspectable.

The examples establish a specific error contract and test strategy. They do not provide a universal policy for missing or nonfinite measurements. A scientific workflow must decide how those cases relate to its estimand, then keep the decision visible in both code and reported denominators.


## Six investigations

### 1. Keep valid zero

Calculate the mean of -1 and 1.

**Expected:** The result is the valid number 0.

**Hint:** Do not confuse a zero result with rejection.

### 2. Reject empty input

Call the helper on an empty vector.

**Expected:** ArgumentError identifies the missing observation requirement.

**Hint:** The denominator cannot be zero.

### 3. Reject nonfinite values

Include NaN or Inf in the input.

**Expected:** DomainError is raised.

**Hint:** Check the numeric domain before aggregation.

### 4. Preserve an unexpected error

Pass a value for which the required methods do not exist.

**Expected:** The unexpected method error is rethrown.

**Hint:** Catch only the failures that the boundary promises to handle.

### 5. Test independently

Validate a result using a hand calculation and a limiting case.

**Expected:** The assertion has an independent basis.

**Hint:** Avoid copying the same implementation expression.

### 6. Report rejected rows

Aggregate valid outcomes from a mixed input stream.

**Expected:** Retain counts and reasons for rejected rows.

**Hint:** The valid-result denominator needs provenance.

## Primary references

- [Julia exceptions](https://docs.julialang.org/en/v1/manual/control-flow/)
- [Julia Test standard library](https://docs.julialang.org/en/v1/stdlib/Test/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
