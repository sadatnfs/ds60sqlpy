## Dots request elementwise application

Broadcasting applies an operation across compatible collection shapes. A dot on a function call or operator requests the broadcasted form. Compatible singleton axes can be expanded without copying the corresponding logical value into a full matrix first.

Shape remains meaningful. A vector can align with one matrix axis, while a reshaped row can align with another. Write the intended formula using row and column indices before relying on broadcasting to infer the desired arrangement. Equal element counts are not sufficient for compatible axes.

Dotted expressions can fuse, and dotted assignment can update existing storage. These properties can reduce intermediate allocations, but they do not prove that a computation is correct or fastest for every workload. Keep a semantic reference and measure allocation behavior later under a controlled setup.

## Worked case A: row and column contributions

The first example adds row-specific offsets and column-specific offsets to a2-by -3 matrix. Reshaping the column offsets to a one-row matrix makes the intended axes explicit. The checked result corresponds to \(B_{ij}=A_{ij}+u_i+v_j\). An incompatible vector length produces a dimension error instead of a plausible but unintended result.

{{WORKED_A}}

## Worked case B: an in-place update and a snapshot

An elementwise affine update can safely read and overwrite the same indexed element. A left-to-right shift implemented as a loop is different: each write changes a value that a later iteration reads. The program contrasts that mutation-order result with an explicit source snapshot. The lesson does not assume that every library broadcast operation handles overlapping storage in the same way as that manual loop.

{{WORKED_B}}

## Generic broadcasting

Broadcasting is an extensible interface. Arrays, scalars and custom objects can define how they participate. For an ordinary numerical array, inspect `size` and `axes` and test a tiny example before scaling up. Use explicit reshaping when a vector's intended axis could be misunderstood.

A dotted assignment does not automatically change an array's element type. Writing an incompatible value into an integer destination can fail or require a conversion according to the element contract. Choose an output representation capable of holding the intended results before performing the update.

## Diagnose allocation and aliasing separately

If a result differs between out-of-place and in-place implementations, inspect dependencies between reads and writes. A snapshot can restore the intended semantics at an allocation cost. If the results agree but timings differ, separate compilation, allocation, memory access and arithmetic costs before interpreting a benchmark.

Do not add lower-level bounds or vectorization annotations merely to force a benchmark result. First establish the indexing and aliasing assumptions. A fast implementation of the wrong recurrence or axis alignment is still wrong.

The examples verify exact small shape and mutation contracts. They do not claim that broadcasting eliminates every allocation, that all loops are slow, or that a copied result is always preferable. Later performance lessons reuse these distinctions when measuring concrete scientific kernels.
