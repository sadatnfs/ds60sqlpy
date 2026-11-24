# julia-011: explained reference

The executable reference is `julia-011_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Dispatch chooses a method from the types of all positional arguments, while each constructor still checks its own numeric domain. `Circle` and `Rectangle` accept finite nonnegative sizes, `area` has one method per shape, and `classify` has two one-sided integer methods plus an explicit `(Integer, Integer)` method that resolves their overlap.

## 1. Add a zero-size shape

The constructor permits nonnegative dimensions, including zero.

**Expected observation:** Its area is 0.

**Why it holds here:** Radius 0 satisfies `stored >= 0`, so `Circle(0)` is valid and `pi * 0^2` is 0.

**Plausible wrong approach:** Rejecting zero as if it were negative removes a legitimate degenerate case and makes empty shapes impossible to represent.

**How to verify:** The reference asserts `area(Circle(0)) == 0` and `area(Rectangle(0, 5)) == 0`.

## 2. Reject an invalid dimension

A method for the right type can still receive scientifically invalid values unless its contract prevents them.

**Expected observation:** Construction raises ArgumentError.

**Why it holds here:** `Rectangle(1, -1)` fails `h >= 0`, so the constructor throws `ArgumentError` even though the argument types are valid reals.

**Plausible wrong approach:** Relying on the `Real` type annotation to block bad sizes misses that -1 is a perfectly good `Real`.

**How to verify:** The reference asserts `@test_throws ArgumentError Rectangle(1, -1)` and the same for `Circle(-1)`.

## 3. Trace both arguments

There is no requirement that one argument be a special receiver.

**Expected observation:** Different methods handle the two cases.

**Why it holds here:** `classify(1, "x")` matches only `(Integer, Any)` and `classify("x", 1)` matches only `(Any, Integer)`, so they return different symbols.

**Plausible wrong approach:** Reasoning as in single-dispatch languages, where only the first argument selects behavior, predicts the same method for both calls.

**How to verify:** Example B asserts `:first_integer` and `:second_integer` for these two calls.

## 4. Resolve the overlap

An intersection method documents behavior and prevents ambiguity.

**Expected observation:** The explicit intersection method is selected.

**Why it holds here:** Both one-sided methods match `(1, 2)`, and neither is more specific; the `(Integer, Integer)` method is more specific than both and is chosen.

**Plausible wrong approach:** Deleting the intersection method to simplify the code turns `classify(1, 2)` into a `MethodError` reporting ambiguity.

**How to verify:** Example B asserts `classify(1, 2) == :both_integers`; `methods(classify)` lists all three signatures.

## 5. Keep an unsupported case visible

A catch-all fallback should be added only when its semantics are defined.

**Expected observation:** A MethodError is raised.

**Why it holds here:** `(1.0, 2.0)` matches none of the three signatures, so Julia raises `MethodError` rather than guessing a result.

**Plausible wrong approach:** Adding `classify(a, b) = :other` to silence the error claims a meaning for float pairs that the design never defined.

**How to verify:** Example B asserts `@test_throws MethodError classify(1.0, 2.0)`.

## 6. Extend an owned interface

Test the new method and invariants rather than assuming subtype membership proves interface correctness.

**Expected observation:** The generic total can use the operation if its laws hold.

**Why it holds here:** A new `struct Square <: Shape` with an `area` method lets `total_area` include it, because the sum only calls `area` on each element.

**Plausible wrong approach:** Declaring the subtype without an `area` method compiles, but `total_area` then fails with `MethodError` at the first square.

**How to verify:** Test the new `area` on a known side length and include it in a `Shape[]` passed to `total_area`.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-011: all reference checks passed`:

Zero-size shapes are allowed, so `Circle(0)` and `Rectangle(0, 5)` both have area 0, while negative radius or height fails in the inner constructor with `ArgumentError`. The subtype line shows `Circle <: Shape`, and the concreteness check explains why: `Circle` can be instantiated with fields, while `Shape` is an abstract node that only groups methods. A new shape must define its own `area` method to join the dispatch table.

```julia
function exercise_checks()
    @test area(Circle(0)) == 0
    @test area(Rectangle(0, 5)) == 0
    @test_throws ArgumentError Circle(-1)
    @test_throws ArgumentError Rectangle(1, -1)
    @test Circle <: Shape
    @test isconcretetype(Circle) && !isconcretetype(Shape)
end
```
