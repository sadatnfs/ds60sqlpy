# julia-002: Numbers, promotion, overflow and exactness

## Starting point and outcome

Beginner; approximately 90 minutes. Direct prerequisites: `julia-001`.

Choose and validate numeric representations while distinguishing exact arithmetic, overflow and floating-point approximation.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## Representation is part of the calculation

The written number, its stored representation and the scientific quantity are related but different. Julia's ordinary integer literals use a machine integer type in this environment. Floating-point literals such as `0.1` use a binary approximation. A rational literal such as `1//10` represents an exact ratio of integers when its numerator and denominator remain representable.

Arithmetic can promote inputs to a common representation. That convenience does not make every conversion lossless. Dividing two integers with `/` produces a floating-point result, while `div` performs integer division. A rational uses `//`. Select the operation that matches the intended question instead of inferring meaning from the appearance of the result.

Machine integers have finite ranges. Ordinary integer arithmetic can wrap around on overflow. A checked operation raises an error instead, while `BigInt` provides arbitrary-precision integer arithmetic subject to available memory. These are different contracts. A count or identifier should not silently become negative because its representation overflowed.

## Worked case A: checked and arbitrary-precision integers

The first example adds one to the maximum signed 8-bit integer. Ordinary arithmetic wraps to the minimum value; the checked operation raises `OverflowError`. The arbitrary-precision calculation produces the mathematical answer 128. The small representation makes a failure that also matters for large counters easy to see.

```julia
using Test

function worked_a()
    top = typemax(Int8)
    @test top + Int8(1) == typemin(Int8)
    @test_throws OverflowError Base.Checked.checked_add(top, Int8(1))
    @test BigInt(top) + 1 == 128
    println("Wrapped: ", top + Int8(1), "; exact: ", BigInt(top) + 1)
end

worked_a()
```

## Worked case B: approximate and exact decimal-looking values

Binary floating point does not represent most decimal fractions exactly. The familiar 0.1 plus 0.2 calculation therefore differs slightly from 0.3. An approximate comparison uses an explicit tolerance, while rational arithmetic represents the intended decimal fractions exactly. More bits in `BigFloat` can reduce approximation error, but binary arbitrary precision is not the same as exact decimal arithmetic.

```julia
using Test

function worked_b()
    @test 0.1 + 0.2 != 0.3
    @test isapprox(0.1 + 0.2, 0.3; atol = 1e-15, rtol = 0)
    @test 1//10 + 2//10 == 3//10
    @test 7 / 2 == 3.5
    @test div(7, 2) == 3
    println("Floating sum: ", 0.1 + 0.2, "; rational sum: ", 1//10 + 2//10)
end

worked_b()
```

## Tolerances have units and purpose

An absolute tolerance is measured in the units of the compared quantity. A relative tolerance scales with magnitude. Neither should be widened merely to make a failed test pass. Derive a useful bound from rounding, the numerical algorithm and the precision required by the scientific decision. Near zero, a purely relative comparison may be unsuitable.

A conversion from a previously rounded Float64 to BigFloat cannot recover the decimal value that was lost before conversion. Construct higher-precision values from the intended literal or string under an explicit precision policy. Keep that policy local and avoid changing shared precision during concurrent numerical work.

## Diagnosis and transfer

When a total looks wrong, inspect input types, promotion, overflow and the operation used. Integer division can discard a remainder intentionally; an accidental use of it can bias a later average. Floating-point values can also carry infinities or NaNs, which need explicit handling rather than an assumption that every arithmetic result is finite.

For exact money or identifiers, choose a representation and rounding policy deliberately. A financial-looking decimal is not automatically safe as Float64. For scientific computation, Float64 is often useful but still requires conditioning and error analysis. Later numerical lessons separate representation error from approximation and model error.

The programs verify specific representation boundaries on tiny inputs. They do not establish that arbitrary-precision arithmetic is always faster or preferable, nor that approximate equality proves two scientific procedures equivalent. Preserve the intended units and mathematical operation alongside the stored type.


## Six investigations

### 1. Retain a remainder

Compute quotient and remainder for 7 divided by 2.

**Expected:** The integer quotient is 3 and remainder 1.

**Hint:** Use div and rem explicitly.

### 2. Reject a narrowing conversion

Convert 128 to Int8.

**Expected:** The conversion raises InexactError.

**Hint:** Inspect the target range.

### 3. Keep an exact ratio

Add 1//10 and 2//10.

**Expected:** The result equals 3//10 exactly.

**Hint:** Use rational syntax.

### 4. Choose a precision

Compare 1.0f0 and 1.0.

**Expected:** Their types are Float32 and Float64.

**Hint:** Literal syntax is part of the contract.

### 5. Check a large integer

Compute BigInt(2)^100.

**Expected:** The mathematical integer is retained beyond the machine Int range.

**Hint:** Promote before exponentiation.

### 6. Explain a tolerance

Justify an absolute tolerance for a measured quantity.

**Expected:** The bound uses that quantity units and required accuracy.

**Hint:** Do not substitute a larger bound for a diagnosis.

## Primary references

- [Julia numeric representations](https://docs.julialang.org/en/v1/manual/integers-and-floating-point-numbers/)
- [Complex and rational arithmetic](https://docs.julialang.org/en/v1/manual/complex-and-rational-numbers/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
