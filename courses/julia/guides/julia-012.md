# julia-012: Parametric types and generic numerical code

## Starting point and outcome

Intermediate; approximately 150 minutes. Direct prerequisites: `julia-011`.

Express useful type relationships without confusing subtype relations, storage representation or a method signature.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## A type parameter records a relationship

A parametric type can represent the same structure with different element types. A record containing `Vector{T}` retains a relationship between its parameter and its stored elements. A parametric method can use that relationship to construct compatible accumulators or outputs.

A type bound such as `T<:Real` restricts the domain to real-number types. It should reflect the intended mathematical operation, not be added as decoration. A generic numerical algorithm often needs fewer restrictions than a beginner expects. Excessively narrow signatures can prevent rational, arbitrary-precision or automatic-differentiation values from using otherwise compatible arithmetic.

Julia's parametric containers are invariant in their parameters. A `Vector{Float64}` is not a `Vector{Real}`, even though Float64 is a subtype of Real. The containers have different representation and mutation contracts. A method accepting `AbstractVector{<:Real}` can express the wider family of suitable vectors.

## Worked case A: preserve the element representation

The typed accumulator initializes with `zero(T)` and iterates using `eachindex`. It works for integers, floating-point values and rationals under the small bounded inputs. The tests inspect both the result and a concrete inference result, rather than assuming that generic code must be untyped or slow.

```julia
using Test

struct Batch{T<:Real}
    values::Vector{T}
end

function typed_total(values::AbstractVector{T}) where {T<:Real}
    total = zero(T)
    for index in eachindex(values)
        total += values[index]
    end
    return total
end

accepts_reals(values::AbstractVector{<:Real}) = length(values)

function worked_a()
    @test typed_total([1, 2, 3]) == 6
    @test typed_total([0.5, 1.5]) == 2.0
    @test typed_total([1//3, 2//3]) == 1//1
    @test (@inferred typed_total([1, 2])) == 3
    @test typed_total(Int[]) == 0
    println("Rational total: ", typed_total([1//3, 2//3]))
end

worked_a()
```

## Worked case B: distinguish invariance from a method family

The second case constructs parameterized batches and checks their concrete types. It then demonstrates the difference between the exact `Vector{Real}` type and the family of vectors with real element types. The relevant method accepts that family without forcing every vector into a heterogeneous abstract-element container.

```julia
using Test

struct Batch{T<:Real}
    values::Vector{T}
end

function typed_total(values::AbstractVector{T}) where {T<:Real}
    total = zero(T)
    for index in eachindex(values)
        total += values[index]
    end
    return total
end

accepts_reals(values::AbstractVector{<:Real}) = length(values)

function worked_b()
    integers = Batch([1, 2])
    floats = Batch([1.0, 2.0])
    @test integers isa Batch{Int}
    @test floats isa Batch{Float64}
    @test !(Vector{Float64} <: Vector{Real})
    @test Vector{Float64} <: AbstractVector{<:Real}
    @test accepts_reals(floats.values) == 2
    println("Batch types: ", typeof(integers), "; ", typeof(floats))
end

worked_b()
```

## Allocation and scientific meaning

A result with a stable concrete type can be easier for the compiler to specialize, but type stability alone does not prove numerical accuracy or good overall performance. An integer accumulator can still overflow; a floating-point accumulator can still lose accuracy. Preserve the representation policies established earlier.

Avoid constructing an output as a hardcoded Float64 array when a generic algorithm is supposed to work with another numeric type. Such a conversion can lose precision or prevent dual numbers from carrying derivatives. The automatic-differentiation unit later uses this principle directly.

## Diagnose a signature

When a method rejects an input, inspect the complete container type, not only its displayed elements. A vector declared with an abstract element type differs from a concrete vector, and a missing-value union is not the same as a purely real vector. Decide whether the algorithm should reject missingness, handle it explicitly or operate on a filtered view.

Use `where` parameters to state relationships that matter. Do not introduce a type parameter merely to repeat the name of an unconstrained input. Keep the method readable and test the representations you promise to support, including a relevant boundary such as an empty collection.

The examples establish invariance and generic accumulation in the prepared runtime. They do not guarantee that every arbitrary numeric type is supported or that inference behavior never changes across Julia releases. The declared tests and actual environment provide the evidence for this route.


## Six investigations

### 1. Preserve a rational

Sum 1//3 and 2//3.

**Expected:** The result is exactly 1//1.

**Hint:** Use a compatible zero and arithmetic.

### 2. Handle an empty concrete vector

Sum Int[].

**Expected:** The explicit additive identity is 0.

**Hint:** The element type supplies zero(T).

### 3. Inspect invariance

Test whether Vector{Float64} is a subtype of Vector{Real}.

**Expected:** It is not.

**Hint:** Compare exact container parameters with a family constraint.

### 4. Accept a useful family

Use AbstractVector{<:Real} in a method signature.

**Expected:** Concrete real vectors can be accepted.

**Hint:** Express the intended family without forcing a conversion.

### 5. Reject unrelated elements

Pass a vector of strings to the real-vector method.

**Expected:** A MethodError occurs.

**Hint:** The domain constraint is meaningful here.

### 6. Connect to differentiation

Explain why an output buffer should not always be Float64.

**Expected:** It may discard or reject another numeric representation.

**Hint:** Type relationships can carry derivative information.

## Primary references

- [Julia parametric types](https://docs.julialang.org/en/v1/manual/types/)
- [Julia parametric methods](https://docs.julialang.org/en/v1/manual/methods/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
