# cuda-019: explanatory solutions

## Mechanism review

Tiling loads small regions of A and B into shared memory and reuses each value across several output calculations. For each k-phase, threads cooperatively load both tiles, synchronize, accumulate from the tiles, then synchronize again before overwriting shared storage for the next phase. Partial tiles require zero-filled invalid positions. An early return by tail threads can break the barrier contract. Tile size trades global reuse against shared storage, registers, occupancy and unused tail work. A tiled learning kernel is a correctness and reuse experiment, not an automatic replacement for a mature GEMM library.

The separate [CPU reference](../references/cuda-019_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For a 2-by-2 output tile and \(\mathrm{k}=2\), the four outputs need eight products. Loading four A values and four B values allows reuse across outputs. The naive per-output scheme conceptually reads sixteen scalar operands; the tile loads eight. Cache behavior can change actual transactions.

## Exercise 2

With \(\mathrm{k}=3\) and tile width two, the second phase contains one valid inner coordinate and one zero coordinate. Neutralizing invalid A and B entries preserves the sum. Synchronize after accumulation before the next cooperative load; otherwise a fast producer can overwrite data a slower thread still reads.

## Exercise 3

Three phases. The final phase contributes one valid inner coordinate and one neutral zero coordinate.

## Exercise 4

That thread may still be required for cooperative loads and barriers. Keep all participating threads through the tile phases and predicate final stores.

## Exercise 5

\(2\times 16\times 16\times 4=2,048\) bytes, before any padding or other shared objects.

## Exercise 6

Not necessarily. Compare correctness first; setup, synchronization and unused lanes can outweigh reuse for small shapes.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-019_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Not necessarily. Compare correctness first; setup, synchronization and unused lanes can outweigh reuse for small shapes.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
