# julia-026: explained reference

The executable reference is `julia-026_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

`affine!` validates before it writes: the matrix width must equal the input length, the matrix height must equal the destination and bias lengths, and `Base.mightalias` must find no shared storage between the destination and any input. Only then does `mul!` overwrite the destination and `.+=` add the bias, so a rejected call leaves the output untouched.

## 1. Trace a matrix step

The products `[10, 12]` plus `[1, -1]` give `[11, 11]`.

**Expected observation:** The final vector is `[11, 11]`.

**Why it holds here:** With `[2 1; 0 3]` and input `[3, 4]`, the products are 6 + 4 = 10 and 0 + 12 = 12, and adding `[1, -1]` gives `[11, 11]`.

**Plausible wrong approach:** Multiplying column by column with the input transposed gives different entries and hides the row and column meaning.

**How to verify:** Example A asserts `destination == [11, 11]` and that `affine!` returns the same object with `===`.

## 2. Repeat with new inputs

Multiplication overwrites both entries before adding the bias.

**Expected observation:** The new vector is `[5, 5]`.

**Why it holds here:** For input `[1, 2]` the products are 4 and 6, and adding the bias gives `[5, 5]`, fully replacing the earlier `[11, 11]`.

**Plausible wrong approach:** Accumulating into the destination with `+=` instead of `mul!` would add the new products to the old output.

**How to verify:** Example A asserts `destination == [5, 5]` after the second call.

## 3. Debug a width mismatch

The declared matrix width must equal input length; validation preserves the previous output here.

**Expected observation:** DimensionMismatch occurs before output mutation.

**Why it holds here:** A 2 by 3 matrix needs an input of length 3, so the first check throws `DimensionMismatch` before `mul!` runs.

**Plausible wrong approach:** Validating after the multiplication could leave the destination half written when the error is raised.

**How to verify:** The reference fills the output with 7, makes the bad call and asserts `output == [7, 7]` afterward.

## 4. Find view overlap

The rejection uses mightalias, which conservatively checks possible shared storage.

**Expected observation:** They may address the same parent elements.

**Why it holds here:** `view(storage, 1:2)` and `view(storage, 2:3)` are different objects that both include `storage[2]`, so writing one changes what the other reads.

**Plausible wrong approach:** Checking `destination !== input` passes for two distinct views and misses the shared element.

**How to verify:** Example B asserts `@test_throws ArgumentError` for these views and that `storage == snapshot` after the rejection.

## 5. Design scratch ownership

A scratch buffer can preserve the original input, but its owner and lifetime must be explicit.

**Expected observation:** Use a documented private scratch copy before mutation.

**Why it holds here:** Copying the possibly overlapping input into an owned scratch buffer before writing removes the shared read and write.

**Plausible wrong approach:** Sharing one global scratch buffer among concurrent callers trades an aliasing bug for a race.

**How to verify:** Document who owns the scratch buffer, then test an overlapping call against the result computed on separate copies.

## 6. Evaluate a speed claim

Allocation is one measurement. End-to-end timing and correctness remain necessary.

**Expected observation:** Access patterns, dispatch and workload sizes also matter.

**Why it holds here:** Views can have strided access, and a call with fewer allocated bytes can still run slower on a different access pattern or size.

**Plausible wrong approach:** Treating `@allocated` returning a small number as a speedup claim skips the timing and correctness checks.

**How to verify:** Compare correct results first, then time warmed calls at several sizes and record bytes and seconds together.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-026: all reference checks passed`:

```julia
function exercise_checks()
    output = fill(7.0, 2)
    @test_throws DimensionMismatch affine!(output, ones(2, 3), ones(2), ones(2))
    @test output == [7, 7]
    @test_throws ArgumentError affine!(output, Matrix{Float64}(I, 2, 2), ones(2), output)
    @test affine!(zeros(2), [1.0 2.0; 3.0 4.0], [2.0, 1.0], [0.0, 0.0]) == [4, 10]
    original = [1.0, 2.0]
    separate = copy(original)
    separate[1] = 9
    @test original == [1, 2]
end
```
