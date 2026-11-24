# cuda-019: explanatory solutions

## Mechanism review

Tiling loads small regions of A and B into shared memory and reuses each value across several output calculations. For each k-phase, threads cooperatively load both tiles, synchronize, accumulate from the tiles, then synchronize again before overwriting shared storage for the next phase. Partial tiles require zero-filled invalid positions. An early return by tail threads can break the barrier contract. Tile size trades global reuse against shared storage, registers, occupancy and unused tail work. A tiled learning kernel is a correctness and reuse experiment, not an automatic replacement for a mature GEMM library.

The separate [CPU reference](../references/cuda-019_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For a 2-by-2 output tile and \(\mathrm{k}=2\), the four outputs need eight products. Loading four A values and four B values allows reuse across outputs. The naive per-output scheme conceptually reads sixteen scalar operands; the tile loads eight. Cache behavior can change actual transactions.

**Approach:** Count loads per tile: two A values per row times two rows, and the same for B.

**Why it is correct:** Each loaded value serves two outputs, halving reads from sixteen to eight.

**A plausible wrong approach:** Assuming caches already provide that reuse makes the tile seem pointless without evidence.

**How to verify:** Enumerate operands per output and confirm each loaded value appears twice.

## Exercise 2

With \(\mathrm{k}=3\) and tile width two, the second phase contains one valid inner coordinate and one zero coordinate. Neutralizing invalid A and B entries preserves the sum. Synchronize after accumulation before the next cooperative load; otherwise a fast producer can overwrite data a slower thread still reads.

**Approach:** Split k = 3 into phases [0, 2) and [2, 3), padding the missing column with zeros.

**Why it is correct:** Zero products leave the sum unchanged, and the second barrier protects the tile.

**A plausible wrong approach:** Skipping the post-accumulation barrier lets a fast thread overwrite data still being read.

**How to verify:** Compute a 2-by-3 times 3-by-2 product with tiles and compare to the naive result.

## Exercise 3

Three phases. The final phase contributes one valid inner coordinate and one neutral zero coordinate.

**Approach:** Compute ceil(5 / 2) = 3 phases with the last covering index 4 only.

**Why it is correct:** Phases [0, 2), [2, 4) and [4, 5) cover all five inner coordinates.

**A plausible wrong approach:** Using floor(5 / 2) = 2 phases drops the fifth product.

**How to verify:** The reference asserts phases == [(0, 2), (2, 4), (4, 5)].

## Exercise 4

That thread may still be required for cooperative loads and barriers. Keep all participating threads through the tile phases and predicate final stores.

**Approach:** Keep out-of-range threads in the loop for loads and barriers and predicate only the store.

**Why it is correct:** Those threads load tile values others use and must reach every barrier.

**A plausible wrong approach:** Returning early leaves tile slots unloaded and a barrier that some threads never reach.

**How to verify:** Run a matrix with ragged edges and confirm interior outputs still match.

## Exercise 5

\(2\times 16\times 16\times 4=2,048\) bytes, before any padding or other shared objects.

**Approach:** Multiply 2 tiles by 16 by 16 by 4 bytes.

**Why it is correct:** Each float tile holds 256 values at 4 bytes, totaling 1,024 bytes per tile.

**A plausible wrong approach:** Counting one tile gives 1,024 and underestimates the shared budget per block.

**How to verify:** The reference asserts 2 * 16 * 16 * 4 == 2048.

## Exercise 6

Not necessarily. Compare correctness first; setup, synchronization and unused lanes can outweigh reuse for small shapes.

**Approach:** Check correctness first, then compare times on both small and large shapes.

**Why it is correct:** Small matrices leave many lanes idle and pay barrier costs that reuse cannot repay.

**A plausible wrong approach:** Calling it a bug and disabling tiling for all sizes discards gains on large shapes.

**How to verify:** Record measured times on an actual device for several sizes before choosing.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-019_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It also asserts an exercise answer that the guide's model leaves for you to derive: `assert 2 * 16 * 16 * 4 == 2048`. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Not necessarily. Compare correctness first; setup, synchronization and unused lanes can outweigh reuse for small shapes.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
