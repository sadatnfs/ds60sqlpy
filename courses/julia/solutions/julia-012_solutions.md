# julia-012: explained reference

The executable reference is `julia-012_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

`typed_total` is parametric in `T<:Real` and starts from `zero(T)`, so integers, rationals, `Float32` and `BigInt` keep their own representation. Parametric containers are invariant, so `Vector{Float64}` is not a `Vector{Real}`; the signature `AbstractVector{<:Real}` expresses the intended family instead.

## 1. Preserve a rational

A hardcoded floating accumulator would change the representation contract.

**Expected observation:** The result is exactly 1//1.

**Why it holds here:** With `T = Rational{Int}`, the accumulator starts at `0//1` and adds 1//3 and 2//3 exactly to get `1//1`.

**Plausible wrong approach:** Initializing `total = 0.0` converts the sum to `Float64`, so the result is approximately 1.0 and no longer rational.

**How to verify:** Example A asserts `typed_total([1//3, 2//3]) == 1//1`; also check `typeof` of the result is `Rational{Int}`.

## 2. Handle an empty concrete vector

This empty-input policy is valid for this additive operation, not every statistic.

**Expected observation:** The explicit additive identity is 0.

**Why it holds here:** `Int[]` still has element type `Int`, so `zero(Int)` is returned without the loop running, giving 0.

**Plausible wrong approach:** Using `values[1]` as the initial total fails on an empty vector, and applying the same identity idea to a mean would be wrong.

**How to verify:** Example A asserts `typed_total(Int[]) == 0`.

## 3. Inspect invariance

The two vector types have different representation and mutation contracts.

**Expected observation:** It is not.

**Why it holds here:** Invariance means `Vector{Float64} <: Vector{Real}` is false, since a `Vector{Real}` could store any real and a `Float64` vector cannot.

**Plausible wrong approach:** Assuming covariance, as with Python type hints for read-only sequences, predicts true and leads to signatures that reject float vectors.

**How to verify:** Example B asserts `!(Vector{Float64} <: Vector{Real})` and `Vector{Float64} <: AbstractVector{<:Real}`.

## 4. Accept a useful family

A suitable signature can preserve generic behavior and avoid unnecessary restrictions.

**Expected observation:** Concrete real vectors can be accepted.

**Why it holds here:** `accepts_reals(values::AbstractVector{<:Real})` accepts `[1//2]` because `Rational{Int}` is a subtype of `Real`, returning its length 1.

**Plausible wrong approach:** Annotating the parameter as `Vector{Real}` rejects nearly all concrete vectors, forcing callers to convert data first.

**How to verify:** The reference asserts `accepts_reals([1//2]) == 1`.

## 5. Reject unrelated elements

Broadening a signature requires defining the corresponding arithmetic or behavior.

**Expected observation:** A MethodError occurs.

**Why it holds here:** `String` is not a subtype of `Real`, so no method matches a string vector and Julia raises `MethodError`.

**Plausible wrong approach:** Widening the signature to `AbstractVector` makes the call succeed until `+` or `zero` fails deeper inside.

**How to verify:** The reference asserts `@test_throws MethodError accepts_reals(["text"])`.

## 6. Connect to differentiation

Generic arithmetic is needed for methods such as forward-mode differentiation, subject to their own supported-operation contract.

**Expected observation:** It may discard or reject another numeric representation.

**Why it holds here:** Forward-mode automatic differentiation passes dual numbers through the same arithmetic, and a `zeros(Float64, n)` buffer cannot hold them.

**Plausible wrong approach:** Hardcoding `Float64` output storage either throws on dual inputs or strips their derivative part, making the gradient wrong or absent.

**How to verify:** Show `typed_total(Float32[1, 2]) isa Float32` and `typed_total(BigInt[1, 2]) == 3` from the reference as evidence that generic code preserves type.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-012: all reference checks passed`:

`typed_total(Float32[1, 2]) isa Float32` shows that starting from `zero(eltype(values))` keeps the element type, and the `BigInt` case shows the same code serving arbitrary precision. `accepts_reals` takes a rational and rejects text by dispatch, because `String` is not a `Real`. The two concreteness lines separate an abstract container type, `AbstractVector{Float64}`, which suits signatures, from `Vector{Float64}`, which suits stored fields. Together these lines cover the three questions the lesson asks of every signature: what result type comes back, which argument types are accepted, and which are refused before any work starts. A version that started the total at the integer literal 0 would return `Float64` for `Float32` input after promotion, or keep `Int` where a `BigInt` sum was needed.

```julia
function exercise_checks()
    @test typed_total(Float32[1, 2]) isa Float32
    @test typed_total(BigInt[1, 2]) == 3
    @test accepts_reals([1//2]) == 1
    @test_throws MethodError accepts_reals(["text"])
    @test !isconcretetype(AbstractVector{Float64})
    @test isconcretetype(Vector{Float64})
end
```
