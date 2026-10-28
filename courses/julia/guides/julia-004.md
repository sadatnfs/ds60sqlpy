# julia-004: Conditions, equality and explicit missing decisions

## Starting point and outcome

Beginner; approximately 90 minutes. Direct prerequisites: `julia-002`.

Write explicit Boolean decisions and select equality semantics appropriate to numeric values and data keys.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## A condition needs a Boolean

Julia conditions use Boolean values. An integer count or an arbitrary object is not automatically treated as true merely because it is nonzero or nonempty. This forces a decision rule to say what it means: compare a count to zero, test whether a collection is empty, or apply a named predicate.

`if`, `elseif`, `else` and `end` organize branches. Short-circuit operators can prevent an unsafe second operation when the first condition already determines the result. Their order matters when an expression has side effects or requires a guard, such as validating a denominator before dividing.

An assignment binds a name; `==` compares values under equality methods. `===` tests a stricter identity-style relation, while `isequal` is designed for consistent data-key equality, including special floating-point values. These operations have different purposes. A later dictionary lesson relies on the same distinction.

## Worked case A: guard a computation

The first helper checks that a denominator is positive before calculating a rate. A zero denominator returns an explicit missing-result sentinel, `nothing`, rather than a misleading zero rate. A counter demonstrates that the second part of a false short-circuit expression is not executed.

```julia
using Test

function rate_or_nothing(numerator, denominator)
    denominator > 0 || return nothing
    return numerator / denominator
end

function worked_a()
    @test rate_or_nothing(2, 4) == 0.5
    @test rate_or_nothing(0, 0) === nothing
    calls = Ref(0)
    bump() = (calls[] += 1; true)
    @test !(false && bump())
    @test calls[] == 0
    @test true && bump()
    @test calls[] == 1
    println("Guarded rate and short-circuit checks passed")
end

worked_a()
```

## Worked case B: NaN and signed zero

Floating-point NaN is not equal to itself under `==`, while `isequal` treats NaN keys consistently. Positive and negative zero compare equal under `==`, but `isequal` distinguishes them. A Boolean condition involving `missing` remains unknown and is not a valid `if` condition. The program checks these behaviors directly.

```julia
using Test

function rate_or_nothing(numerator, denominator)
    denominator > 0 || return nothing
    return numerator / denominator
end

function worked_b()
    @test !(NaN == NaN)
    @test isequal(NaN, NaN)
    @test 0.0 == -0.0
    @test !isequal(0.0, -0.0)
    @test ismissing(missing == 1)
    @test_throws TypeError if missing
        1
    else
        0
    end
    println("Special equality cases checked")
end

worked_b()
```

## Missing information is not a false result

A missing measurement, an absent return value and a numerical NaN can represent different states. This lesson introduces the distinction; a later unit treats missing-value arrays and aggregation. Do not convert every unknown condition to false just to make a branch run. Decide whether the application should reject incomplete input, defer a decision or use an explicitly justified fallback.

A short-circuit guard should state an invariant. For example, check that a collection is nonempty before accessing its first element. Catching an indexing exception afterward may be appropriate at a boundary, but it should not conceal a violated data contract. Keep validation separate from the scientific question answered by the computation.

## Diagnose a decision rule

Trace the predicate, the chosen branch and any side effects. A returned zero can be a real numeric result, whereas `nothing` can mean that no valid result was produced. Tests should distinguish those states. Comparing strings or floating values also requires the appropriate representation and tolerance policy from earlier units.

Avoid relying on an implementation accident such as one container's current ordering or one numeric type's conversion rules. Express the condition needed by the algorithm. A clear predicate makes failures easier to explain and makes later changes to data representations less likely to alter behavior silently.

The programs establish Julia's Boolean and equality behavior on small authored cases. They do not choose a universal policy for missing information. A reliable data-science application records that policy and tests normal, boundary and rejected inputs explicitly.


## Six investigations

### 1. Distinguish zero and absent

Compare rates 0/5 and 0/0 under the helper policy.

**Expected:** The first is 0; the second is nothing.

**Hint:** Inspect both value and meaning.

### 2. Check a predicate

Use an integer directly as an if condition.

**Expected:** Julia raises a type error.

**Hint:** Write an explicit comparison.

### 3. Protect an access

Guard the first element of a possibly empty array.

**Expected:** The access occurs only when the collection is nonempty.

**Hint:** Put the guard first in a short-circuit expression.

### 4. Compare NaN keys

Use isequal for two NaN values.

**Expected:** The data-key equality result is true.

**Hint:** Do not substitute ordinary numerical equality.

### 5. Inspect signed zero

Compare 0.0 and -0.0 using both equality functions.

**Expected:** == agrees; isequal distinguishes them.

**Hint:** The sign bit can matter for key semantics.

### 6. Keep an unknown decision

Evaluate a comparison involving missing.

**Expected:** Its result can remain missing.

**Hint:** Unknown is not automatically false.

## Primary references

- [Julia control flow](https://docs.julialang.org/en/v1/manual/control-flow/)
- [Julia missing values](https://docs.julialang.org/en/v1/manual/missing/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
