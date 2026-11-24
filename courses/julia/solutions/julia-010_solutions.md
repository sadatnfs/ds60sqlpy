# julia-010: explained reference

The executable reference is `julia-010_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

`Measurement` has an inner constructor that converts the value with `Float64`, requires it to be finite and requires the unit to be `:m` or `:cm` before calling `new`. The struct is immutable, but `VectorRecord` stores a mutable `Vector{Int}`, so a fixed field binding can still expose changing contents.

## 1. Validate a unit

Field types alone cannot distinguish supported and unsupported physical units.

**Expected observation:** Construction fails explicitly.

**Why it holds here:** `unit in (:m, :cm)` fails for anything else, so construction throws `ArgumentError` and no invalid object ever exists.

**Plausible wrong approach:** Validating units later in each analysis function lets an object with `:unknown` circulate and depends on every caller remembering the check.

**How to verify:** Example A asserts `@test_throws ArgumentError Measurement(1, :unknown)`; try `:km` as well and expect the same error.

## 2. Inspect conversion

The conversion is deliberate and can have precision consequences for other numeric inputs.

**Expected observation:** Its stored value is Float64.

**Why it holds here:** The constructor calls `Float64(value)` before storing, so `Measurement(1, :cm).value` is the float 1.0.

**Plausible wrong approach:** Assuming the integer type is kept would predict `Int` storage, but `fieldtypes(Measurement)` fixes the field as `Float64`.

**How to verify:** The reference asserts `fieldtypes(Measurement) == (Float64, Symbol)`; print `typeof(Measurement(1, :cm).value)`.

## 3. Try field reassignment

This says nothing about whether the original measurement was scientifically valid.

**Expected observation:** The operation is rejected.

**Why it holds here:** Fields of an immutable struct cannot be reassigned after construction, so `measurement.value = 3.0` throws `ErrorException`.

**Plausible wrong approach:** Concluding that the failed assignment proves the measurement is valid confuses a language rule about mutation with domain validation.

**How to verify:** Example A asserts `@test_throws ErrorException measurement.value = 3.0`.

## 4. Mutate nested storage

Deep immutability requires more than an immutable wrapper.

**Expected observation:** Its contents can change despite the immutable outer struct.

**Why it holds here:** `VectorRecord(a)` stores the same vector object `a`, so `a[1] = 3` is visible as `record.values[1] == 3`.

**Plausible wrong approach:** Calling the outer struct immutable and therefore frozen predicts the old value, ignoring that the vector inside is shared and mutable.

**How to verify:** The reference performs exactly this mutation and asserts `record.values[1] == 3`.

## 5. Create a snapshot

A snapshot policy must account for every nested mutable layer.

**Expected observation:** Later source-vector mutation does not affect that copied vector.

**Why it holds here:** `VectorRecord(copy(a))` stores a fresh vector, so later writes to `a` do not reach the stored copy.

**Plausible wrong approach:** Copying the record wrapper instead of the vector still shares the inner storage, so the supposed snapshot keeps changing.

**How to verify:** The reference sets `a[1] = 4` after the copy and asserts `separate.values[1] == 3`.

## 6. Review a convenience constructor

An API becomes inconsistent if one creation path bypasses its stated invariant.

**Expected observation:** It preserves the same validation contract.

**Why it holds here:** A convenience method such as `Measurement(value) = Measurement(value, :m)` routes through the inner constructor and keeps both checks.

**Plausible wrong approach:** Writing it with `new` directly or with a different field order can create objects that skip the unit and finiteness guards.

**How to verify:** Call the convenience method with NaN and expect `ArgumentError`, proving the same contract applies.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-010: all reference checks passed`:

Construction checks confirm that `Measurement` stores a `Float64` and a `Symbol`, converting the integer 1 but refusing the string "1" with `MethodError`. The vector lines show what immutability does not protect: `VectorRecord(a)` keeps a reference to `a`, so setting `a[1] = 3` is visible through `record.values`. Passing `copy(a)` breaks that link, and the later write of 4 leaves `separate.values[1]` at 3.

```julia
function exercise_checks()
    @test typeof(Measurement(1, :cm)) == Measurement
    @test fieldtypes(Measurement) == (Float64, Symbol)
    @test_throws MethodError Measurement("1", :m)
    a = [1]
    record = VectorRecord(a)
    a[1] = 3
    @test record.values[1] == 3
    separate = VectorRecord(copy(a))
    a[1] = 4
    @test separate.values[1] == 3
end
```
