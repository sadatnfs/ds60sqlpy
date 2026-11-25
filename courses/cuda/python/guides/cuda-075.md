# cuda-075: Two-dimensional indexing and images

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-066`, `cuda-074`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Trace a rectangular tile.
- Calculate flat offsets.
- Change clamp to zero padding.
- Find in-place stencil contamination.
- Test width one.
- Explain row and column tail guards.

## Mechanism and vocabulary

An image has coordinates, channel conventions and storage layout. Map thread x to columns and thread y to rows only after defining that contract. A row-major scalar image uses offset `row * width + column`. A rectangular block launch requires independent checks for row and column, because the input dimensions may have different tails. Multiplying both dimensions by the same bound accidentally accepts invalid coordinates.

Stencil operations read neighbors, so boundary policy is part of correctness: zero padding, clamp, reflect and valid-only output produce different results. Read from an immutable input and write to a separate output unless a proven algorithm allows in-place updates. A CPU loop is useful because its coordinate meanings are visible. Do not infer coalescing or performance from that loop's execution time.



### Key terms

- **Flat pixel offset:** The position `row * width + col` of a pixel in a row-major image buffer.
- **Zero padding:** A boundary rule that treats out-of-range neighbors as zero.
- **Clamp to edge:** A boundary rule that replaces an out-of-range coordinate with the nearest valid one.
- **In-place contamination:** Corruption that occurs when a stencil writes results into the same buffer that neighboring threads are still reading.

## Worked examples

### Worked example 1

For a 2 by 3 image, row 1 column 2 maps to flat offset 5. Swapping row and column changes the address and can escape the allocation.

### Worked example 2

A horizontal three-point average with clamped borders maps [3,6,9] to [4,6,8]. Zero padding would produce [3,6,5], a different documented operation.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-075_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-075_cpu.py
```

```python
values = [3, 6, 9]
clamped = [
    (values[max(0, i - 1)] + values[i] + values[min(len(values) - 1, i + 1)]) / 3
    for i in range(len(values))
]
assert clamped == [4, 6, 8]
assert 1 * 3 + 2 == 5
print("CPU image reference:", clamped)
```

**Expected observation:** Clamped horizontal average [4, 6, 8].

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `values` | `[3, 6, 9]` |
| `clamped` | `[4.0, 6.0, 8.0]` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-075.md) before opening hints.

### Exercise 1: Trace a rectangular tile

**Trap to avoid:** Writing pairs directly from a single flattened thread number tempts the reader to assign `x` to rows, because rows are listed first in mathematics. The tile then covers three rows and two columns, a transposed shape.

### Exercise 2: Calculate flat offsets

**Trap to avoid:** Using `column * width + row` swaps the roles. For row 1 column 2 it gives `2*3 + 1 = 7`, which lies past the six-element allocation, so a kernel would read or write out of bounds.

### Exercise 3: Change clamp to zero padding

**Trap to avoid:** Calling both versions a three-point average and comparing only the interior value 6 hides the change. Tests that skip the edges will pass for either padding and miss a semantic regression.

### Exercise 4: Find in-place stencil contamination

**Trap to avoid:** Assuming each thread writes only its own element and therefore cannot interfere ignores that neighbors read that element. Ownership of writes is not the same as ownership of reads.

### Exercise 5: Test width one

**Trap to avoid:** Assuming width is always at least 3 and reading `values[i-1]` and `values[i+1]` directly fails: `values[-1]` silently returns the last element in Python, and `values[1]` raises IndexError. A device version reads out of bounds.

### Exercise 6: Explain row and column tail guards

**Trap to avoid:** Guarding only the flat offset with `offset < height*width` lets a thread with column 3 and row 0 in a width-3 image pass, because its offset 3 is valid. It then writes into row 1, column 0, corrupting another pixel.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Pick a small rectangular tile and list its row indices and column indices as two separate ranges.
2. Use the row-major formula with the image width, then check the largest offset against the allocation size.
3. Recompute each border element of `[3,6,9]` with a zero outside the image instead of a repeated edge value.
4. Update the output in place from left to right and note which neighbor value the second element reads.
5. With a single column, ask which value clamping supplies for both the left and right neighbors.
6. Choose an image whose height and width have different tails and test each coordinate's guard separately.

## Common mistakes and self-check

A frequent mistake is writing a stencil's output into its own input. After the first pixel is updated, its neighbor reads the new value instead of the original, so the result depends on thread order. A second mistake is guarding only one coordinate, or using one bound for both, which lets threads in a non-square tail write outside the image. Fix both by reading from an immutable input, writing to a separate output and checking row and column against their own limits.

**Evidence limit:** The CPU loop reproduces the clamped average `[4, 6, 8]` with visible coordinates. Its run time says nothing about coalescing, tile shape or GPU throughput, and it cannot show races that only appear when threads run concurrently.

1. Why must the boundary policy be stated as part of correctness?
2. What is the flat offset of row 1, column 2 in a row-major 2 by 3 image?
3. Why does a rectangular launch need two independent guards?

Answers: [self-check answers](../solutions/cuda-075_solutions.md#self-check-answers).

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-075: Two-dimensional indexing and images.
Read courses/cuda/python/guides/cuda-075.md and courses/cuda/python/lessons/cuda-075.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
