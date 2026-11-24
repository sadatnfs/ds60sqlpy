# julia-006: explained reference

The executable reference is `julia-006_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Read each function's contract from its signature. `affine` uses keywords `scale = 1` and `shift = 0`, `make_scaler` returns a closure over `scale`, `rebind` assigns a new array to its local name, and `change_first!` mutates the caller's array after rejecting empty input. Compare contents with `==` and identity with `===`.

## 1. Use defaults

A default is part of the function contract and should be recorded when it matters scientifically.

**Expected observation:** The result is 5.

**Why it holds here:** With `scale = 1` and `shift = 0`, `affine(5)` computes `1 * 5 + 0`, which is 5.

**Plausible wrong approach:** Assuming unspecified keywords become zero predicts `0 * 5 + 0 = 0`; the defaults in the signature decide.

**How to verify:** The reference asserts `affine(5) == 5`; compare it with `affine(5; scale = 0)`, which is 0.

## 2. Override one choice

Explicit keyword configuration makes a transformation reproducible.

**Expected observation:** The result is 3.

**Why it holds here:** `affine(5; shift = -2)` keeps `scale = 1` and gives `5 - 2 = 3`.

**Plausible wrong approach:** Passing -2 positionally, as `affine(5, -2)`, raises `MethodError` because `affine` has one positional argument.

**How to verify:** Assert `affine(5; shift = -2) == 3` as the reference does, then confirm the positional call fails.

## 3. Build a closure

A closure packages a transformation and context; it does not necessarily copy mutable captured objects.

**Expected observation:** The result is 6.

**Why it holds here:** `make_scaler(3)` returns `x -> 3 * x`, which remembers `scale = 3`, so applying it to 2 gives 6.

**Plausible wrong approach:** Expecting the closure to read a global named `scale` at call time would make its result depend on unrelated script state.

**How to verify:** The reference asserts `make_scaler(3)(2) == 6`; also map it over `[1, 2]` and expect `[3, 6]`.

## 4. Trace a rebound argument

Rebinding the argument name is different from mutating the shared object.

**Expected observation:** The caller array remains unchanged.

**Why it holds here:** In `rebind`, `values = [99]` points the local name at a new array, so the caller's `[1]` is untouched.

**Plausible wrong approach:** Expecting the caller to see `[99]` assumes assignment writes through the argument, which only element mutation such as `values[1] = 99` does.

**How to verify:** The reference checks `replacement == [99]`, `replacement !== original` and `original == [1]`.

## 5. Trace a mutated argument

The naming convention warns callers that the operation changes shared state.

**Expected observation:** Its first element becomes 99 and the returned object aliases it.

**Why it holds here:** `change_first!` writes `values[1] = 99` into the caller's array and returns that same object.

**Plausible wrong approach:** Testing only `returned == [99, 2]` cannot tell a mutated original from a modified copy; identity needs `===`.

**How to verify:** As in worked example B, assert both `values == [99, 2]` and `returned === values`.

## 6. Reject an empty mutation

A clear input contract produces a more useful diagnostic than an accidental indexing failure.

**Expected observation:** An explicit ArgumentError is raised.

**Why it holds here:** The guard `isempty(values) && throw(ArgumentError(...))` runs before indexing, so an empty input gets a named precondition error.

**Plausible wrong approach:** Dropping the guard lets `values[1] = 99` raise `BoundsError`, which describes an index rather than the violated contract.

**How to verify:** Assert `@test_throws ArgumentError change_first!(Int[])` as the reference does.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-006: all reference checks passed`:

The keyword default leaves `affine(5)` unchanged while `shift = -2` moves it to 3, and `make_scaler(3)(2) == 6` shows the closure remembering its factor after the outer call returns. The last group is the important one: `rebind` assigns a new vector to its local name, so the caller's `original` stays `[1]` while the returned `replacement` holds 99 and is a different object. Mutation through `change_first!` is the only way to change the caller's array, and it refuses an empty one.

```julia
function exercise_checks()
    @test affine(5) == 5
    @test affine(5; shift = -2) == 3
    @test make_scaler(3)(2) == 6
    @test map(x -> x + 1, [0, 1]) == [1, 2]
    @test_throws ArgumentError change_first!(Int[])
    original = [1]
    replacement = rebind(original)
    @test replacement == [99]
    @test replacement !== original
    @test original == [1]
end
```
