# julia-002: explained reference

The executable reference is `julia-002_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Pick the numeric type from the question being asked. Integer division and remainder use `div` and `rem`; exact ratios use `Rational`; values past `typemax(Int)` need `BigInt` before the operation; and floating-point checks use tolerances tied to units. Every conversion that cannot hold its value should fail loudly rather than wrap.

## 1. Retain a remainder

Integer division answers another question from floating-point division.

**Expected observation:** The integer quotient is 3 and remainder 1.

**Why it holds here:** Seven equals 2 times 3 plus 1, so `div(7, 2)` returns 3 and `rem(7, 2)` returns 1, both as integers.

**Plausible wrong approach:** Writing `7 / 2` and truncating the float answers a different question; it returns 3.5 and loses the remainder unless it is recomputed separately.

**How to verify:** Assert `div(7, 2) == 3` and `rem(7, 2) == 1`; the reference already checks `rem(7, 2) == 1`.

## 2. Reject a narrowing conversion

A constructor conversion that cannot represent the value must not be confused with wrapping arithmetic.

**Expected observation:** The conversion raises InexactError.

**Why it holds here:** `Int8` covers -128 through 127, so the constructor `Int8(128)` has no exact result and throws `InexactError`.

**Plausible wrong approach:** Expecting -128 confuses conversion with wrapping arithmetic; `typemax(Int8) + Int8(1)` wraps, but a checked constructor refuses an unrepresentable value.

**How to verify:** Use `@test_throws InexactError Int8(128)` as the reference does, then confirm `Int8(127)` succeeds.

## 3. Keep an exact ratio

This preserves the intended ratio instead of first rounding decimal-looking binary floats.

**Expected observation:** The result equals 3//10 exactly.

**Why it holds here:** `1//10 + 2//10` is computed as integer numerators over a common denominator, giving `3//10` with no rounding at any step.

**Plausible wrong approach:** Using `0.1 + 0.2` and comparing with `0.3` fails, because both decimals are rounded binary floats and the sum is `0.30000000000000004`.

**How to verify:** Check `1//10 + 2//10 == 3//10` and, for contrast, `0.1 + 0.2 == 0.3`, which is false.

## 4. Choose a precision

More precision changes representation cost and error; it does not validate the model.

**Expected observation:** Their types are Float32 and Float64.

**Why it holds here:** The suffix `f0` makes `1.0f0` a `Float32`; plain `1.0` is `Float64`, with roughly 7 versus 16 significant decimal digits.

**Plausible wrong approach:** Treating the two literals as the same value with different spelling ignores precision; `eps(1.0f0)` is about 1.2e-7 while `eps(1.0)` is about 2.2e-16.

**How to verify:** Print `typeof(1.0f0)` and `typeof(1.0)`; the reference asserts `typeof(1.0f0) == Float32`.

## 5. Check a large integer

Converting a wrapped machine result afterward cannot reconstruct the lost value.

**Expected observation:** The mathematical integer is retained beyond the machine Int range.

**Why it holds here:** `BigInt(2)^100` promotes before multiplying, so the exact 31-digit value survives; machine `2^100` wraps modulo 2 to the 64 and yields 0.

**Plausible wrong approach:** Computing `2^100` first and calling `BigInt` on the result gives `BigInt(0)`, since the overflow happened before the conversion.

**How to verify:** Assert `BigInt(2)^100 > typemax(Int)` as the reference does, and print `2^100` beside it to see the wrapped 0.

## 6. Explain a tolerance

Representation, conditioning and algorithmic error inform a tolerance; passing an arbitrary bound proves little.

**Expected observation:** The bound uses that quantity units and required accuracy.

**Why it holds here:** A measured length in meters with a stated 1 millimeter requirement justifies an absolute tolerance of 0.001, tied to units rather than to float precision alone.

**Plausible wrong approach:** Raising `atol` until a failing comparison passes hides whether the error came from representation, conditioning or a wrong formula.

**How to verify:** Write the tolerance next to its unit and source, then confirm `isapprox(x, y; atol = 0.001)` fails for a deliberately perturbed value.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-002: all reference checks passed`:

```julia
function exercise_checks()
    @test rem(7, 2) == 1
    @test 2//4 == 1//2
    @test BigInt(2)^100 > typemax(Int)
    @test_throws InexactError Int8(128)
    @test typeof(1.0f0) == Float32
    @test !isfinite(Inf)
end
```
