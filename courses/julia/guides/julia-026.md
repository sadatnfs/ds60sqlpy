# julia-026: Allocation, mutation and alias-safe numerical work

## Starting point and outcome

Advanced; approximately 150 minutes. Direct prerequisites: `julia-007`, `julia-013`, `julia-025`.

Implement a preallocated matrix step, explain ownership and aliasing, and compare semantic results before measuring storage behavior.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## Mutation is a storage contract

An allocating operation returns fresh storage. A mutating operation writes into a destination supplied by its caller. Julia convention marks many mutating names with `!`, but the punctuation is a promise in documentation, not a language-enforced guarantee. The caller needs to know which objects can change, whether partial results survive an exception, and whether inputs may share storage with outputs.

For a dense matrix \(A\in\mathbb{R}^{m\times n}\), a vector \(x\in\mathbb{R}^{n}\), a bias \(b\in\mathbb{R}^{m}\) and output \(y\in\mathbb{R}^{m}\), the operation is \(y\leftarrow Ax+b\). `mul!(y,A,x)` performs the multiplication into existing storage. It generally requires that the destination not alias its inputs. A view can overlap another array even when the two objects are not identical. `Base.mightalias` is deliberately conservative: it can flag a possible overlap rather than prove one exists.

## Validate before writing

The example first checks dimensions, then rejects possible destination overlap, then performs the update. This ordering protects the destination from the known validation failures. It is not a transactional guarantee for every possible element-type error during computation. We restrict the examples to ordinary Float64 arrays with supported operations and explain that boundary.

A safe alternative when aliasing is required is to copy the input into a scratch buffer before writing. That copy costs time and memory, but correctness determines whether it is necessary. Reusing one scratch buffer across calls can reduce allocations while retaining a clear ownership contract. Do not share a mutable scratch buffer among concurrent tasks without synchronization or exclusive ownership.

### Worked case A: reuse an output buffer

The first example applies a two-dimensional linear update and checks the result against direct arithmetic. It confirms that the same destination object is returned and that the input vector remains unchanged.

```julia
using Test
using LinearAlgebra
BLAS.set_num_threads(1)

function affine!(destination, matrix, input, bias)
    size(matrix, 2) == length(input) || throw(DimensionMismatch("Input width"))
    size(matrix, 1) == length(destination) == length(bias) ||
        throw(DimensionMismatch("Output height"))
    any(source -> Base.mightalias(destination, source), (matrix, input, bias)) &&
        throw(ArgumentError("Destination must not overlap inputs"))
    mul!(destination, matrix, input)
    destination .+= bias
    return destination
end

function worked_a()
    matrix = [2.0 1.0; 0.0 3.0]
    input = [3.0, 4.0]
    bias = [1.0, -1.0]
    destination = zeros(2)
    @test affine!(destination, matrix, input, bias) === destination
    @test destination == [11, 11]
    @test input == [3, 4]
    affine!(destination, matrix, [1.0, 2.0], bias)
    @test destination == [5, 5]
    bytes = @allocated affine!(destination, matrix, input, bias)
    @test bytes >= 0
    println("Reused output: ", destination, "; measured allocation bytes: ", bytes)
end

worked_a()
```

For the declared matrix, the two products are \(2\cdot3+1\cdot4=10\) and \(0\cdot3+3\cdot4=12\). Adding the bias produces 11 and 11. This hand-derived result would catch a transposed matrix, an omitted bias or an unintended update to the input.

### Worked case B: views expose ownership

The second example shows that a view writes through to its parent and then verifies that the numerical kernel rejects an overlapping destination. Rejection is a deliberate API choice. It makes a dangerous call visible instead of relying on a particular multiplication implementation to happen to work.

```julia
using Test
using LinearAlgebra
BLAS.set_num_threads(1)

function affine!(destination, matrix, input, bias)
    size(matrix, 2) == length(input) || throw(DimensionMismatch("Input width"))
    size(matrix, 1) == length(destination) == length(bias) ||
        throw(DimensionMismatch("Output height"))
    any(source -> Base.mightalias(destination, source), (matrix, input, bias)) &&
        throw(ArgumentError("Destination must not overlap inputs"))
    mul!(destination, matrix, input)
    destination .+= bias
    return destination
end

function worked_b()
    storage = [1.0, 2.0, 3.0, 4.0]
    middle = view(storage, 2:3)
    middle[1] = 20
    @test storage == [1, 20, 3, 4]
    matrix = Matrix{Float64}(I, 2, 2)
    destination = view(storage, 1:2)
    input = view(storage, 2:3)
    snapshot = copy(storage)
    @test_throws ArgumentError affine!(destination, matrix, input, zeros(2))
    @test storage == snapshot
    println("Overlapping call rejected before mutation")
end

worked_b()
```

## Storage and performance evidence

The `@allocated` observations in the reference are taken after warming the relevant call. They report this prepared runtime's allocation behavior but do not assert an exact byte count. Wrapper specialization, compiler changes and library dispatch can change those counts. The semantic checks remain stable across such changes. A production optimization report would compare repeated realistic workloads, not only one tiny matrix.

Julia's dense arrays use column-major storage. Traversing the first index in the inner loop usually visits neighboring elements, while a row view may be strided. A view avoids a copy but can make downstream access less contiguous. Copying a repeatedly used strided slice can therefore improve performance in some workloads. Measure the complete repeated operation, including the copy, to decide.

## Failure cases and extension

Using `===` alone detects only identity, not overlapping views. Ignoring dimensions can leave a low-level exception whose message misses the intended contract. Reusing a destination without overwriting every entry can retain previous-run values. Always test the second call as well as the first. For larger scientific workflows, document buffer ownership next to shape and dtype, and keep the reference implementation available as an independent readable oracle. Unit 30 applies the same ownership reasoning to parallel tasks; each task should own its partial result before a controlled reduction.


## Six investigations

### 1. Trace a matrix step

Compute the two entries before running the first case.

**Expected:** The final vector is[11,11].

**Hint:** Multiply rows by the input, then add bias.

### 2. Repeat with new inputs

Reuse the destination for input[1,2].

**Expected:** The new vector is[5,5].

**Hint:** Ensure old output is overwritten.

### 3. Debug a width mismatch

Pass a2-by -3 matrix and a length 2 input.

**Expected:** DimensionMismatch occurs before output mutation.

**Hint:** Snapshot the destination first.

### 4. Find view overlap

Explain why two different view objects can be unsafe.

**Expected:** They may address the same parent elements.

**Hint:** Object identity is weaker than storage independence.

### 5. Design scratch ownership

Describe a safe interface for repeated calls that must permit overlapping inputs.

**Expected:** Use a documented private scratch copy before mutation.

**Hint:** Account for allocation and concurrency.

### 6. Evaluate a speed claim

Explain why fewer measured bytes may not mean faster code.

**Expected:** Access patterns, dispatch and workload sizes also matter.

**Hint:** Views may be strided.

## Primary references

- [LinearAlgebra mul!](https://docs.julialang.org/en/v1/stdlib/LinearAlgebra/#LinearAlgebra.mul!)
- [Julia performance tips](https://docs.julialang.org/en/v1/manual/performance-tips/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
