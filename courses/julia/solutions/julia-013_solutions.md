# julia-013: explained reference

The executable reference is `julia-013_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Write the indexed formula first, then make array axes express it. Broadcasting extends singleton axes and fails when lengths disagree. The worked example adds per-row offsets `[10, 20]` and a one-row array of per-column offsets. For in-place loops, ask whether a read sees earlier writes, since that decides recurrence or snapshot behavior.

## 1. Choose the axis

The explicit singleton axis documents the intended broadcast alignment.

**Expected observation:** Reshape the offsets into a one-row array.

**Why it holds here:** `reshape([100, 200, 300], 1, 3)` has size `(1, 3)`, so it lines up with the three columns of `[1 3 5; 2 4 6]`.

**Plausible wrong approach:** Adding the plain vector `[100, 200, 300]` tries to match it with the two rows and raises `DimensionMismatch`.

**How to verify:** Example A asserts the result `[111 213 315; 122 224 326]`; the reference checks `size(reshape([1, 2, 3], 1, 3)) == (1, 3)`.

## 2. Reject incompatible axes

Shape validation prevents a silent interpretation of an unintended operation.

**Expected observation:** A DimensionMismatch occurs.

**Why it holds here:** A length 4 vector aligns with the first axis of length 2, which is neither equal nor 1, so broadcasting throws.

**Plausible wrong approach:** Arguing that 4 elements fit somewhere in a 6-element matrix treats total size as the rule rather than per-axis compatibility.

**How to verify:** Example A asserts `@test_throws DimensionMismatch matrix .+ [1, 2, 3, 4]`.

## 3. Update in place

This dependence pattern makes the specific self-update straightforward to reason about.

**Expected observation:** The destination values change to the expected affine result.

**Why it holds here:** `values .= 2 .* values .+ 1` fuses into one loop where each output reads only its own old element, so `[1, 2, 3]` becomes `[3, 5, 7]`.

**Plausible wrong approach:** Writing `values = 2 .* values .+ 1` allocates a new array and rebinds the name, so other references to the original see no change.

**How to verify:** Example B asserts `values == [3, 5, 7]`; the reference checks a similar dotted assignment giving `[0.5, 1.0]`.

## 4. Trace a manual recurrence

The loop implements a recurrence, not a simultaneous snapshot assignment.

**Expected observation:** The example becomes `[1, 1, 1, 1]`.

**Why it holds here:** In the loop `sequential[i] = sequential[i-1]`, position 2 receives 1, and position 3 then reads that new 1, so all four entries become 1.

**Plausible wrong approach:** Expecting a shift to `[1, 1, 2, 3]` assumes each read sees the original values, which only holds with separate source storage.

**How to verify:** Example B asserts `sequential == [1, 1, 1, 1]`.

## 5. Preserve a snapshot

The copy changes the read/write dependency and therefore the algorithm.

**Expected observation:** The example becomes `[1, 1, 2, 3]`.

**Why it holds here:** Reading from `source = copy(snapshot)` keeps the old values available, so the shift gives `[1, 1, 2, 3]`.

**Plausible wrong approach:** Taking a `view` of the array instead of a copy shares storage and reproduces the recurrence result.

**How to verify:** Example B asserts `snapshot == [1, 1, 2, 3]`.

## 6. Choose a destination type

Allocate a representation that can express the intended result.

**Expected observation:** The incompatible conversion is rejected.

**Why it holds here:** `Int[0] .= [0.5]` must convert 0.5 into the existing `Int` element, which is inexact, so `InexactError` is raised.

**Plausible wrong approach:** Expecting the destination to widen to `Float64` misunderstands in-place assignment, which never changes the element type of an existing array.

**How to verify:** The reference asserts `@test_throws InexactError Int[0] .= [0.5]`; allocate `zeros(1)` when fractional results are expected.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-013: all reference checks passed`:

Broadcasting rules appear one at a time: `sin.` applies elementwise, a scalar expands across `[1, 2]`, and `.*` multiplies matching positions rather than performing a matrix product. `reshape` turns three values into a one by three row without copying them. The `destination .=` line writes into existing storage, and the final `InexactError` shows that an in-place write into `Int` storage cannot hold 0.5.

```julia
function exercise_checks()
    @test sin.([0.0, pi/2]) ≈ [0, 1]
    @test [1, 2] .+ 3 == [4, 5]
    @test size(reshape([1, 2, 3], 1, 3)) == (1, 3)
    @test [1, 2] .* [3, 4] == [3, 8]
    destination = zeros(2)
    destination .= [1, 2] ./ 2
    @test destination == [0.5, 1.0]
    @test_throws InexactError Int[0] .= [0.5]
end
```
