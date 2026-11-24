# cuda-048: explanatory solutions

## Mechanism review

Sparse storage represents selected entries and their coordinates instead of storing every zero. Compressed sparse row, CSR, stores row offsets, column indices and values. Row offsets delimit each row's entries; the final offset equals the stored-entry count. Specify index base, sortedness and duplicate handling. A sparse multiply can save arithmetic and storage but introduces indirect reads and uneven row work. Conversion and preprocessing costs matter, especially for one-shot operations. Arbitrary sparsity is different from structured sparsity supported by certain hardware/library modes.

The separate [CPU reference](../references/cuda-048_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Matrix \([[2,0,1],[0,3,0]]\) has CSR offsets \([0,2,3]\), columns \([0,2,1]\) and values \([2,1,3]\). Multiplying by \([4,5,6]\) gives \([14,15]\). The first row reads two entries; the second reads one. Offsets are boundaries, not per-row counts.

**Approach:** Store [[2, 0, 1], [0, 3, 0]] as offsets [0, 2, 3], columns [0, 2, 1] and values [2, 1, 3], then sum per row.

**Why it is correct:** Row 0 spans entries 0 to 2: 2 times x[0] = 8 plus 1 times x[2] = 6 gives 14; row 1 has 3 times x[1] = 15.

**A plausible wrong approach:** Treating offsets as row lengths makes row 0 read zero entries and row 1 read two, scrambling the products.

**How to verify:** The reference asserts y == [14, 15] and that the final offset equals len(values) and len(columns).

## Exercise 2

An empty middle row repeats an offset. For lengths \([2,0,1]\), row boundaries are \([0,2,2,3]\). Repeated offsets are valid. A descending offset or a column outside the matrix width is invalid and must be rejected before device access.

**Approach:** Exclusive scan the lengths [2, 0, 1] and append the total, giving [0, 2, 2, 3], then validate offsets and columns.

**Why it is correct:** The repeated 2 marks an empty middle row whose span [2, 2) holds nothing.

**A plausible wrong approach:** Rejecting repeated offsets as corrupt refuses a valid matrix with an empty row.

**How to verify:** Check offsets never decrease, every column is below the width, and the last offset equals the entry count.

## Exercise 3

\([0,0,1,4]\), with final offset four stored entries.

**Approach:** Exclusive scan [0, 1, 3] to [0, 0, 1] and append the total 4.

**Why it is correct:** Row 0 is empty, row 1 spans [0, 1), and row 2 spans [1, 4).

**A plausible wrong approach:** Using the inclusive scan [0, 1, 4] as offsets loses the leading zero, so row 1 would appear to start at entry 1.

**How to verify:** Confirm differences of [0, 0, 1, 4] reproduce [0, 1, 3] and the last offset is 4.

## Exercise 4

Conversion, indices, irregular access, launch overhead and small size can dominate. Compare actual reuse and distribution, not only fill ratio.

**Approach:** Weigh conversion, index storage, irregular gathers and launch cost against the zero fraction.

**Why it is correct:** Each nonzero needs a column index read, and gathers from x are irregular.

**A plausible wrong approach:** Assuming 90 percent zeros means ten times faster ignores overhead per stored entry and small sizes.

**How to verify:** Measure dense and sparse runs on the actual matrix including conversion when it is part of the job.

## Exercise 5

Either reject duplicates or combine them with a specified operation before/within the supported library contract; do not leave semantics implicit.

**Approach:** Choose to reject duplicate coordinates or to sum them, and document the choice.

**Why it is correct:** A duplicate (row, col) pair otherwise has library-dependent meaning.

**A plausible wrong approach:** Assuming the library sums duplicates may silently keep one value or fail validation.

**How to verify:** Feed a matrix with a duplicate and assert the documented rejection or combined value.

## Exercise 6

Rows identify destination nodes or the explicitly chosen orientation, columns identify neighbors, and empty/isolated nodes need valid outputs.

**Approach:** Let rows be destination nodes and columns be neighbors, and give isolated nodes valid outputs.

**Why it is correct:** A CSR row then lists the neighbors aggregated into that destination.

**A plausible wrong approach:** Mixing source and destination orientation aggregates along reversed edges.

**How to verify:** Test a graph with an isolated node and a directed edge and check both outputs.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-048_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Rows identify destination nodes or the explicitly chosen orientation, columns identify neighbors, and empty/isolated nodes need valid outputs.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
