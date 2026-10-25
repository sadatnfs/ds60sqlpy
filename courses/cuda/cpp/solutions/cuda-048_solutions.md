# cuda-048: explanatory solutions

## Mechanism review

Sparse storage represents selected entries and their coordinates instead of storing every zero. Compressed sparse row, CSR, stores row offsets, column indices and values. Row offsets delimit each row's entries; the final offset equals the stored-entry count. Specify index base, sortedness and duplicate handling. A sparse multiply can save arithmetic and storage but introduces indirect reads and uneven row work. Conversion and preprocessing costs matter, especially for one-shot operations. Arbitrary sparsity is different from structured sparsity supported by certain hardware/library modes.

The separate [CPU reference](../references/cuda-048_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Matrix \([[2,0,1],[0,3,0]]\) has CSR offsets \([0,2,3]\), columns \([0,2,1]\) and values \([2,1,3]\). Multiplying by \([4,5,6]\) gives \([14,15]\). The first row reads two entries; the second reads one. Offsets are boundaries, not per-row counts.

## Exercise 2

An empty middle row repeats an offset. For lengths \([2,0,1]\), row boundaries are \([0,2,2,3]\). Repeated offsets are valid. A descending offset or a column outside the matrix width is invalid and must be rejected before device access.

## Exercise 3

\([0,0,1,4]\), with final offset four stored entries.

## Exercise 4

Conversion, indices, irregular access, launch overhead and small size can dominate. Compare actual reuse and distribution, not only fill ratio.

## Exercise 5

Either reject duplicates or combine them with a specified operation before/within the supported library contract; do not leave semantics implicit.

## Exercise 6

Rows identify destination nodes or the explicitly chosen orientation, columns identify neighbors, and empty/isolated nodes need valid outputs.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-048_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Rows identify destination nodes or the explicitly chosen orientation, columns identify neighbors, and empty/isolated nodes need valid outputs.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
