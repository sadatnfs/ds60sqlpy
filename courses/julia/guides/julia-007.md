# julia-007: Arrays, shapes, copies and views

## Starting point and outcome

Beginner; approximately 90 minutes. Direct prerequisites: `julia-006`.

Trace array storage and indexing while choosing deliberately between copies and shared views.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## Shape and storage are separate descriptions

An array has element values, an element type and an index shape. A matrix can contain six values arranged as two rows and three columns. Julia's ordinary dense arrays use column-major storage, so a linear traversal visits a column before moving to the next. A scientific formula should state its intended axes rather than relying on storage order to supply meaning.

`size` reports axis lengths, `length` reports the number of elements and `eltype` describes their stored type. Generic code can inspect `axes` and use `eachindex`. Standard arrays are one-based, but not every possible custom array type has identical indexing conventions.

Indexing a slice with an ordinary range often produces a copy, while `view` or `@view` creates a window into the original storage. Both can display the same values initially. Their difference becomes visible when one is mutated or when allocation costs matter.

## Worked case A: inspect a column-major matrix

Reshaping the values 1 through 6 into a2-by -3 matrix fills its first column before the second. The example checks selected coordinates, the complete shape and the sum. `reshape` can share the underlying data, so a shape transformation should not automatically be treated as a deep copy.

```julia
using Test

function worked_a()
    values = collect(1:6)
    matrix = reshape(values, 2, 3)
    @test size(matrix) == (2, 3)
    @test matrix[:, 1] == [1, 2]
    @test matrix[1, 3] == 5
    @test length(matrix) == 6
    @test sum(matrix) == 21
    println("Matrix: ", matrix)
end

worked_a()
```

## Worked case B: mutate a view and a copy

The second example takes the same first two vector elements as an ordinary slice and as a view. Changing the copy leaves the source untouched. Changing the view updates the source. A second binding to the original array also shares that same mutable object, while `copy` creates another array storage object for these scalar elements.

```julia
using Test

function worked_b()
    values = [1, 2, 3]
    snapshot = values[1:2]
    window = @view values[1:2]
    snapshot[1] = 90
    @test values[1] == 1
    window[2] = 80
    @test values == [1, 80, 3]
    alias = values
    @test alias === values
    @test copy(values) !== values
    println("Source after view mutation: ", values)
end

worked_b()
```

## Aliasing can change an algorithm

An in-place transformation can be correct only under assumptions about which inputs share storage. Updating a view while reading overlapping source positions may change later reads. Do not assume that a mathematically elementwise formula remains equivalent under every mutation order. Use an explicit copy when a snapshot is required, and test overlapping as well as disjoint cases.

`copy` is shallow for nested mutable objects. Copying an outer vector of inner vectors does not automatically duplicate every inner vector. `deepcopy` has a different contract and cost. Choose the level of independence required by the data structure rather than treating every copy operation as interchangeable.

## Diagnose shape mistakes

Print small shapes and selected elements before running a large numerical routine. A transposed matrix may have the same element count while representing a different computation. A vector and a one-column matrix also have different shapes. Later broadcasting and linear-algebra units use these distinctions explicitly.

Keep array bounds checks while learning and testing a contract. Removing them can turn a clear indexing exception into incorrect or unsafe behavior. If performance later motivates a lower-level implementation, establish its indexing invariants independently first.

The examples verify concrete storage-sharing and shape properties. They do not claim that views are always faster than copies. Access patterns, specialization and repeated reuse can affect performance, so compare semantically equivalent implementations under a measured workload.


## Six investigations

### 1. Read a shape

Compare a length 2 vector with a2-by -1 matrix.

**Expected:** Their sizes are(2,) and(2,1).

**Hint:** Element count does not determine the number of axes.

### 2. Trace column order

Locate value 5 in the reshaped matrix.

**Expected:** It is at row 1,column 3.

**Hint:** Follow columns through the input vector.

### 3. Take a snapshot

Mutate an ordinary slice from a vector.

**Expected:** The original scalar-element vector is unchanged.

**Hint:** The slice has copied storage.

### 4. Use a shared window

Mutate a view of the same range.

**Expected:** The original array changes.

**Hint:** A view refers to existing storage.

### 5. Copy nested state

Compare copy and deepcopy on a vector of vectors.

**Expected:** A shallow copy shares inner vectors; a deep copy does not in this fixture.

**Hint:** Inspect both outer and inner identities.

### 6. Retain a bound check

Read index 0 from a standard two-element vector.

**Expected:** A BoundsError is raised.

**Hint:** The valid standard indices start at 1.

## Primary references

- [Julia arrays](https://docs.julialang.org/en/v1/manual/arrays/)
- [Array interfaces](https://docs.julialang.org/en/v1/manual/interfaces/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
