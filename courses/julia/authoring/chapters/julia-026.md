## Mutation is a storage contract

An allocating operation returns fresh storage. A mutating operation writes into a destination supplied by its caller. Julia convention marks many mutating names with `!`, but the punctuation is a promise in documentation, not a language-enforced guarantee. The caller needs to know which objects can change, whether partial results survive an exception, and whether inputs may share storage with outputs.

For a dense matrix \(A\in\mathbb{R}^{m\times n}\), a vector \(x\in\mathbb{R}^{n}\), a bias \(b\in\mathbb{R}^{m}\) and output \(y\in\mathbb{R}^{m}\), the operation is \(y\leftarrow Ax+b\). `mul!(y,A,x)` performs the multiplication into existing storage. It generally requires that the destination not alias its inputs. A view can overlap another array even when the two objects are not identical. `Base.mightalias` is deliberately conservative: it can flag a possible overlap rather than prove one exists.

## Validate before writing

The example first checks dimensions, then rejects possible destination overlap, then performs the update. This ordering protects the destination from the known validation failures. It is not a transactional guarantee for every possible element-type error during computation. We restrict the examples to ordinary Float64 arrays with supported operations and explain that boundary.

A safe alternative when aliasing is required is to copy the input into a scratch buffer before writing. That copy costs time and memory, but correctness determines whether it is necessary. Reusing one scratch buffer across calls can reduce allocations while retaining a clear ownership contract. Do not share a mutable scratch buffer among concurrent tasks without synchronization or exclusive ownership.

### Worked case A: reuse an output buffer

The first example applies a two-dimensional linear update and checks the result against direct arithmetic. It confirms that the same destination object is returned and that the input vector remains unchanged.

{{WORKED_A}}

For the declared matrix, the two products are \(2\cdot3+1\cdot4=10\) and \(0\cdot3+3\cdot4=12\). Adding the bias produces 11 and 11. This hand-derived result would catch a transposed matrix, an omitted bias or an unintended update to the input.

### Worked case B: views expose ownership

The second example shows that a view writes through to its parent and then verifies that the numerical kernel rejects an overlapping destination. Rejection is a deliberate API choice. It makes a dangerous call visible instead of relying on a particular multiplication implementation to happen to work.

{{WORKED_B}}

## Storage and performance evidence

The `@allocated` observations in the reference are taken after warming the relevant call. They report this prepared runtime's allocation behavior but do not assert an exact byte count. Wrapper specialization, compiler changes and library dispatch can change those counts. The semantic checks remain stable across such changes. A production optimization report would compare repeated realistic workloads, not only one tiny matrix.

Julia's dense arrays use column-major storage. Traversing the first index in the inner loop usually visits neighboring elements, while a row view may be strided. A view avoids a copy but can make downstream access less contiguous. Copying a repeatedly used strided slice can therefore improve performance in some workloads. Measure the complete repeated operation, including the copy, to decide.

## Failure cases and extension

Using `===` alone detects only identity, not overlapping views. Ignoring dimensions can leave a low-level exception whose message misses the intended contract. Reusing a destination without overwriting every entry can retain previous-run values. Always test the second call as well as the first. For larger scientific workflows, document buffer ownership next to shape and dtype, and keep the reference implementation available as an independent readable oracle. Unit 30 applies the same ownership reasoning to parallel tasks; each task should own its partial result before a controlled reduction.
