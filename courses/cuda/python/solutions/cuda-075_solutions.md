# cuda-075: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Trace a rectangular tile

List rows and columns independently.

**Approach.** Pick a small tile, for example two rows by three columns starting at row 0 column 0, and write the row list `[0, 1]` and the column list `[0, 1, 2]` separately before forming the six coordinate pairs.

**Why it is correct here.** In a 2D launch, `threadIdx.y` and `blockIdx.y` produce the row while the `.x` components produce the column. Listing them independently mirrors how the hardware generates them and makes it obvious which pair each thread owns.

**A plausible wrong approach.** Writing pairs directly from a single flattened thread number tempts the reader to assign `x` to rows, because rows are listed first in mathematics. The tile then covers three rows and two columns, a transposed shape.

**How to verify.** Count the pairs: there must be rows times columns of them, six here, with no duplicates. Each pair should satisfy `row < 2` and `column < 3`, and the set should match a nested loop over rows then columns.

## Exercise 2: Calculate flat offsets

Use `row * width + column`.

**Approach.** For row-major storage compute `offset = row * width + column`. With width 3, row 1 column 2 gives `1*3 + 2 = 5`, the last slot of a 2 by 3 image.

**Why it is correct here.** Row-major layout stores each complete row contiguously, so moving down one row skips `width` elements and moving right one column skips one. The reference asserts `1*3+2 == 5`, the same arithmetic.

**A plausible wrong approach.** Using `column * width + row` swaps the roles. For row 1 column 2 it gives `2*3 + 1 = 7`, which lies past the six-element allocation, so a kernel would read or write out of bounds.

**How to verify.** Enumerate all six coordinates with the formula and confirm the offsets are exactly 0 to 5 with no gaps or repeats. Also check that the largest offset is `height*width - 1`.

## Exercise 3: Change clamp to zero padding

State the changed edge semantics.

**Approach.** Replace the clamped neighbor reads with a zero-padded version: a neighbor outside the row contributes 0, so the average for `[3, 6, 9]` becomes `[(0+3+6)/3, 6, (6+9+0)/3] = [3, 6, 5]`.

**Why it is correct here.** Changing padding changes the mathematical operation, not just an implementation detail. Clamping repeats the edge pixel, while zero padding assumes black outside the image, so border values differ and the documentation must say which is computed.

**A plausible wrong approach.** Calling both versions a three-point average and comparing only the interior value 6 hides the change. Tests that skip the edges will pass for either padding and miss a semantic regression.

**How to verify.** Compute both lists and assert the clamped version equals `[4, 6, 8]` from the reference while the zero-padded one equals `[3, 6, 5]`. The difference must appear only in positions 0 and 2.

## Exercise 4: Find in-place stencil contamination

Earlier writes alter later reads.

**Approach.** Trace an in-place stencil on `[3, 6, 9]`: if index 0 is updated to 4 before index 1 reads its left neighbor, index 1 computes `(4+6+9)/3` instead of `(3+6+9)/3`.

**Why it is correct here.** A stencil needs every output computed from the original input. When the output overwrites the input, earlier writes become later reads, and on a GPU the order of those writes between threads is not defined, so results can also vary between runs.

**A plausible wrong approach.** Assuming each thread writes only its own element and therefore cannot interfere ignores that neighbors read that element. Ownership of writes is not the same as ownership of reads.

**How to verify.** Run the in-place version sequentially and show index 1 becomes about 6.33 instead of 6. Then use separate input and output buffers and confirm the result returns to `[4, 6, 8]`.

## Exercise 5: Test width one

Clamping repeats the only element.

**Approach.** Apply the clamped average to a single-column image, for example `[7]`. Both neighbor indices clamp to 0, so the output is `(7+7+7)/3 = 7`.

**Why it is correct here.** With width 1 the left index `max(0, -1)` and right index `min(0, 1)` both collapse to 0. Clamping therefore repeats the only element, and the average equals the input, which is the expected degenerate behavior.

**A plausible wrong approach.** Assuming width is always at least 3 and reading `values[i-1]` and `values[i+1]` directly fails: `values[-1]` silently returns the last element in Python, and `values[1]` raises IndexError. A device version reads out of bounds.

**How to verify.** Call the reference expression with `values = [7]` and assert the result is `[7.0]`. Add the same test for height 1 in a 2D stencil to exercise the vertical clamp.

## Exercise 6: Explain row and column tail guards

Both coordinates need their own upper bound.

**Approach.** In the 2D kernel guard with `if row < height and column < width:` before any load or store, since the grid is rounded up separately in each dimension.

**Why it is correct here.** A 2D launch rounds the number of blocks up in both x and y. Threads past the last column exist in every block row, and threads past the last row exist in every block column, so each coordinate needs its own bound.

**A plausible wrong approach.** Guarding only the flat offset with `offset < height*width` lets a thread with column 3 and row 0 in a width-3 image pass, because its offset 3 is valid. It then writes into row 1, column 0, corrupting another pixel.

**How to verify.** Use a 5 by 5 image with 4 by 4 blocks so both tails exist. Count the threads that pass the guard: it must be exactly 25, and the set of offsets must be 0 to 24 with no duplicates.

## Reference observation

Clamped horizontal average [4, 6, 8].

The reference file is `courses/cuda/python/references/cuda-075_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
