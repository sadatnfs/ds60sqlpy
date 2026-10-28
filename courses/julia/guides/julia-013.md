# julia-013: Broadcasting, axes and mutation order

## Starting point and outcome

Intermediate; approximately 150 minutes. Direct prerequisites: `julia-007`, `julia-012`.

Use broadcasting with explicit axes and distinguish an elementwise formula from a mutation-order-dependent algorithm.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## Dots request elementwise application

Broadcasting applies an operation across compatible collection shapes. A dot on a function call or operator requests the broadcasted form. Compatible singleton axes can be expanded without copying the corresponding logical value into a full matrix first.

Shape remains meaningful. A vector can align with one matrix axis, while a reshaped row can align with another. Write the intended formula using row and column indices before relying on broadcasting to infer the desired arrangement. Equal element counts are not sufficient for compatible axes.

Dotted expressions can fuse, and dotted assignment can update existing storage. These properties can reduce intermediate allocations, but they do not prove that a computation is correct or fastest for every workload. Keep a semantic reference and measure allocation behavior later under a controlled setup.

## Worked case A: row and column contributions

The first example adds row-specific offsets and column-specific offsets to a2-by -3 matrix. Reshaping the column offsets to a one-row matrix makes the intended axes explicit. The checked result corresponds to \(B_{ij}=A_{ij}+u_i+v_j\). An incompatible vector length produces a dimension error instead of a plausible but unintended result.

```julia
using Test

function worked_a()
    matrix = [1 3 5; 2 4 6]
    rows = [10, 20]
    columns = reshape([100, 200, 300], 1, 3)
    result = matrix .+ rows .+ columns
    @test result == [111 213 315; 122 224 326]
    @test_throws DimensionMismatch matrix .+ [1, 2, 3, 4]
    println("Broadcast result: ", result)
end

worked_a()
```

## Worked case B: an in-place update and a snapshot

An elementwise affine update can safely read and overwrite the same indexed element. A left-to-right shift implemented as a loop is different: each write changes a value that a later iteration reads. The program contrasts that mutation-order result with an explicit source snapshot. The lesson does not assume that every library broadcast operation handles overlapping storage in the same way as that manual loop.

```julia
using Test

function worked_b()
    values = [1.0, 2.0, 3.0]
    values .= 2 .* values .+ 1
    @test values == [3, 5, 7]
    sequential = [1, 2, 3, 4]
    for index = 2:length(sequential)
        sequential[index] = sequential[index-1]
    end
    snapshot = [1, 2, 3, 4]
    source = copy(snapshot)
    for index = 2:length(snapshot)
        snapshot[index] = source[index-1]
    end
    @test sequential == [1, 1, 1, 1]
    @test snapshot == [1, 1, 2, 3]
    println("Sequential versus snapshot: ", sequential, "; ", snapshot)
end

worked_b()
```

## Generic broadcasting

Broadcasting is an extensible interface. Arrays, scalars and custom objects can define how they participate. For an ordinary numerical array, inspect `size` and `axes` and test a tiny example before scaling up. Use explicit reshaping when a vector's intended axis could be misunderstood.

A dotted assignment does not automatically change an array's element type. Writing an incompatible value into an integer destination can fail or require a conversion according to the element contract. Choose an output representation capable of holding the intended results before performing the update.

## Diagnose allocation and aliasing separately

If a result differs between out-of-place and in-place implementations, inspect dependencies between reads and writes. A snapshot can restore the intended semantics at an allocation cost. If the results agree but timings differ, separate compilation, allocation, memory access and arithmetic costs before interpreting a benchmark.

Do not add lower-level bounds or vectorization annotations merely to force a benchmark result. First establish the indexing and aliasing assumptions. A fast implementation of the wrong recurrence or axis alignment is still wrong.

The examples verify exact small shape and mutation contracts. They do not claim that broadcasting eliminates every allocation, that all loops are slow, or that a copied result is always preferable. Later performance lessons reuse these distinctions when measuring concrete scientific kernels.


## Six investigations

### 1. Choose the axis

Add one offset per column to a matrix.

**Expected:** Reshape the offsets into a one-row array.

**Hint:** Write the indexed formula first.

### 2. Reject incompatible axes

Broadcast a length 4 vector with the 2-by -3 fixture.

**Expected:** A DimensionMismatch occurs.

**Hint:** Compatible axes are not determined by total element count.

### 3. Update in place

Apply 2x+1 elementwise to a floating vector using dotted assignment.

**Expected:** The destination values change to the expected affine result.

**Hint:** Each output depends only on the corresponding old element.

### 4. Trace a manual recurrence

Shift a vector left-to-right by reading the preceding updated element.

**Expected:** The example becomes[1,1,1,1].

**Hint:** A later read sees an earlier write.

### 5. Preserve a snapshot

Read the shift input from an explicit copy.

**Expected:** The example becomes[1,1,2,3].

**Hint:** Separate source and destination storage.

### 6. Choose a destination type

Write 0.5 into an integer element through dotted assignment.

**Expected:** The incompatible conversion is rejected.

**Hint:** Mutation does not make the destination representation arbitrary.

## Primary references

- [Julia dot syntax](https://docs.julialang.org/en/v1/manual/functions/)
- [Julia array broadcasting](https://docs.julialang.org/en/v1/manual/arrays/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
