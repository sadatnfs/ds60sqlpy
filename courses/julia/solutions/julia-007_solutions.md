# julia-007: explained reference

The executable reference is `julia-007_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Separate shape from contents and storage from interpretation. `size` reports axes, column-major order explains where `reshape(1:6, 2, 3)` puts each value, ordinary slicing copies, `view` shares storage, `copy` is shallow and `deepcopy` duplicates nested arrays. Bounds checks stay on so a bad index fails visibly.

## 1. Read a shape

Operations can dispatch or broadcast differently for these shapes.

**Expected observation:** Their sizes are `(2,)` and `(2, 1)`.

**Why it holds here:** `zeros(2)` has one axis with size `(2,)`, while `zeros(2, 1)` has two axes with size `(2, 1)`, even though both hold two numbers.

**Plausible wrong approach:** Treating both as the same column of two values can make matrix multiplication or broadcasting produce a different shape than intended.

**How to verify:** The reference asserts `size(zeros(2)) == (2,)` and `size(zeros(2, 1)) == (2, 1)`.

## 2. Trace column order

The storage order is explicit and should not be confused with the scientific interpretation of axes.

**Expected observation:** It is at row 1, column 3.

**Why it holds here:** Column-major filling puts 1 and 2 in column 1, 3 and 4 in column 2, and 5 and 6 in column 3, so 5 sits at row 1, column 3.

**Plausible wrong approach:** Reading the vector row by row places 5 at row 2, column 2, which is the row-major layout used by NumPy defaults.

**How to verify:** Print `findfirst(==(5), matrix)` and expect `CartesianIndex(1, 3)`.

## 3. Take a snapshot

A snapshot protects later reads from this mutation, with an allocation cost.

**Expected observation:** The original scalar-element vector is unchanged.

**Why it holds here:** `v[1:2]` allocates a new vector, so setting its first element changes only the copy and `v` keeps its values.

**Plausible wrong approach:** Expecting slices to share memory, as NumPy basic slices do, predicts that the original changes when it does not.

**How to verify:** Mutate the slice and assert the original still equals its starting contents.

## 4. Use a shared window

A view is useful when shared mutation or avoided copying is intended.

**Expected observation:** The original array changes.

**Why it holds here:** `view(v, 1:2)` refers to the same storage, so writing to the view writes into `v`.

**Plausible wrong approach:** Using `@view` as a speed trick and then mutating the result silently alters data that other code still reads.

**How to verify:** Write 99 through the view and assert `v[1] == 99`.

## 5. Copy nested state

The required independence level depends on the data structure and algorithm.

**Expected observation:** A shallow copy shares inner vectors; a deep copy does not in this fixture.

**Why it holds here:** `copy(nested)` makes a new outer vector holding the same inner vectors, so `shallow[1][1] = 9` changes `nested[1][1]` as well.

**Plausible wrong approach:** Assuming `copy` is enough for independence leaves inner arrays shared, so updates leak back into the original.

**How to verify:** The reference checks `nested[1][1] == 9` after the shallow edit and that it stays 9 after editing the `deepcopy`.

## 6. Retain a bound check

Bounds checking makes a violated indexing contract observable before considering lower-level optimizations.

**Expected observation:** A BoundsError is raised.

**Why it holds here:** Standard vectors start at index 1, so `[1, 2][0]` is outside `1:2` and raises `BoundsError`.

**Plausible wrong approach:** Disabling bounds checking with `@inbounds` before the indices are proven valid turns this clear error into reading arbitrary memory.

**How to verify:** Assert `@test_throws BoundsError [1, 2][0]` as the reference does.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-007: all reference checks passed`:

Shape checks show that `zeros(2, 1)` is a two by one matrix while `zeros(2)` is a vector of size `(2,)`, two different types despite holding the same count. Indexing at 0 throws because arrays start at 1. The nested copy lines prove that `copy` duplicates only the outer vector: writing 9 through `shallow` reaches `nested`, while the later write through `deepcopy` leaves `nested[1][1]` at 9.

```julia
function exercise_checks()
    @test size(zeros(2, 1)) == (2, 1)
    @test size(zeros(2)) == (2,)
    @test eltype([1.0, 2.0]) == Float64
    @test_throws BoundsError [1, 2][0]
    nested = [[1], [2]]
    shallow = copy(nested)
    shallow[1][1] = 9
    @test nested[1][1] == 9
    deep = deepcopy(nested)
    deep[1][1] = 4
    @test nested[1][1] == 9
end
```
