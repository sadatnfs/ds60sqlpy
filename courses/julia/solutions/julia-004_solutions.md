# julia-004: explained reference

The executable reference is `julia-004_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Make every decision an explicit `Bool`. `rate_or_nothing` returns `nothing` unless the denominator is positive, so zero and absence stay distinct. Guards come first in short-circuit expressions, and the equality function is chosen by purpose: `==` for numeric comparison, `isequal` for keys, and explicit handling for `missing`.

## 1. Distinguish zero and absent

A real zero rate is different from having no valid denominator.

**Expected observation:** The first is 0; the second is nothing.

**Why it holds here:** `rate_or_nothing(0, 5)` passes the `denominator > 0` guard and returns `0 / 5`, which is 0.0; with denominator 0 the guard returns `nothing`.

**Plausible wrong approach:** Returning 0 for `0 / 0` merges no data with a measured zero rate, so a summary could average in a value that was never observed.

**How to verify:** Assert `rate_or_nothing(0, 5) == 0` and `rate_or_nothing(0, 0) === nothing`, using `===` for the `nothing` comparison.

## 2. Check a predicate

The language requires a Boolean decision rather than an implicit truthiness conversion.

**Expected observation:** Julia raises a type error.

**Why it holds here:** Julia's `if` accepts only a `Bool`; given the integer 1 it raises `TypeError` rather than treating nonzero as true.

**Plausible wrong approach:** Porting a C or Python habit like `if count` assumes truthiness, which Julia rejects at run time with a non-Boolean error.

**How to verify:** The reference wraps `if 1` in `@test_throws TypeError`; rewrite the condition as `count > 0` and confirm it runs.

## 3. Protect an access

This makes the precondition visible and prevents a predictable boundary error.

**Expected observation:** The access occurs only when the collection is nonempty.

**Why it holds here:** In `!isempty(v) && first(v) > 0`, the right side runs only when the left is true, so `first` never sees an empty vector.

**Plausible wrong approach:** Writing the comparison before the emptiness test evaluates `first(Int[])` and throws before the guard can help.

**How to verify:** Evaluate the guarded expression on `Int[]` and on `[0]`; the reference checks `isempty(Int[])` and `!isempty([0])`.

## 4. Compare NaN keys

Dictionary-oriented equality needs consistent treatment of special values.

**Expected observation:** The data-key equality result is true.

**Why it holds here:** `isequal(NaN, NaN)` is true because key equality must be reflexive, while `NaN == NaN` is false by IEEE rules.

**Plausible wrong approach:** Using `==` to look up NaN keys means a stored NaN can never be found, because no comparison with it succeeds.

**How to verify:** Print `NaN == NaN` and `isequal(NaN, NaN)` side by side, expecting `false` and `true`.

## 5. Inspect signed zero

Choose the relation required by the application rather than assuming all equality operations are interchangeable.

**Expected observation:** == agrees; isequal distinguishes them.

**Why it holds here:** `0.0 == -0.0` is true numerically, while `isequal(0.0, -0.0)` is false because the sign bit differs.

**Plausible wrong approach:** Assuming `isequal` is just a slower `==` would merge or split dictionary keys differently than intended for signed zeros.

**How to verify:** Assert `0.0 == -0.0` and `!isequal(0.0, -0.0)`, then build `Dict(0.0 => 1, -0.0 => 2)` and check its length is 2.

## 6. Keep an unknown decision

A data policy must decide whether to reject, defer or explicitly replace the unknown value.

**Expected observation:** Its result can remain missing.

**Why it holds here:** `missing > 1` returns `missing`, since the answer is unknown, and using that result in `if` raises `TypeError`.

**Plausible wrong approach:** Treating missing as false with a silent default drops unknown rows from a filter without recording that a decision was made.

**How to verify:** Print `missing > 1`, then use `coalesce(missing > 1, false)` only where the policy explicitly chooses false.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-004: all reference checks passed`:

The checks pin down truthiness rules that Julia does not share with Python. `isempty(Int[])` and `!isempty([0])` show that emptiness is tested explicitly, since a vector holding zero is not empty. `rate_or_nothing(0, 5) == 0` proves a zero numerator is a valid rate, while the negative denominator returns `nothing` rather than a number. The final `TypeError` confirms that `if 1` is rejected because a condition must be a `Bool`.

```julia
function exercise_checks()
    @test isempty(Int[])
    @test !isempty([0])
    @test rate_or_nothing(0, 5) == 0
    @test rate_or_nothing(2, -1) === nothing
    @test (3 > 2 ? "larger" : "other") == "larger"
    @test_throws TypeError if 1
        true
    else
        false
    end
end
```
