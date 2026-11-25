# cuda-106: A modern tile-based kernel DSL

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-074`, `cuda-076`, `cuda-079`, `cuda-085`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Create tile boundaries.
- Mask a final tile.
- Compare thread and tile abstractions.
- State compiler requirements.
- Design a library comparison.
- Explain a resource tradeoff.

## Mechanism and vocabulary

A thread-level model assigns scalar work to individual threads. A tile-level language describes a block of data and lets a compiler choose lower-level distribution and instructions. The abstraction can simplify matrix and reduction kernels, but layout, memory traffic, masks and numerical behavior still matter. Different DSL releases support different devices and operations.

Use a selected prepared Triton or CUDA tile implementation only after recording its compiler and architecture requirements. Compare the same mathematical operation against a library and the earlier thread-level reference. A masked tile must protect every invalid load and store at the boundary. This elective includes a CPU tiling model; the ordinary Python worker does not acquire a DSL compiler or GPU merely by opening the guide.



### Key terms

- **Tile-level language:** A kernel language such as Triton that describes operations on blocks of data and lets the compiler map them to threads.
- **Program instance:** One launched instance of a tile kernel, identified by its program ID, that processes one tile.
- **Boundary mask:** A boolean vector that disables out-of-bounds loads and stores at tile edges.
- **Block size:** The compile-time tile dimensions, trading parallelism against register and shared memory use.

## Worked examples

### Worked example 1

A vector of 10 elements partitioned into tiles of 4 has tiles [0..3],[4..7],[8,9]. The last tile has two valid lanes and two masked lanes.

### Worked example 2

Changing tile size may improve reuse while increasing register pressure. The direction of the performance change must come from device evidence, not tile size alone.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-106_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-106_cpu.py
```

```python
n, tile = 10, 4
blocks = [list(range(start, min(start + tile, n))) for start in range(0, n, tile)]
assert blocks == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
assert [i for block in blocks for i in block] == list(range(n))
print("CPU tile model:", blocks)
```

**Expected observation:** Three tiles cover ten elements exactly once.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `n` | `10` |
| `tile` | `4` |
| `blocks` | `[[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-106.md) before opening hints.

### Exercise 1: Create tile boundaries

**Trap to avoid:** Using closed intervals `[start, start + tile]` makes adjacent tiles share an element, so index 4 is processed twice and a sum reduction double counts it.

### Exercise 2: Mask a final tile

**Trap to avoid:** Masking only the store still issues out-of-bounds loads, which can fault or read unrelated memory, and an unmasked reduction then includes garbage values.

### Exercise 3: Compare thread and tile abstractions

**Trap to avoid:** Assuming a tile kernel behaves like a thread kernel with the same block size misreads the model, since a tile program instance is not a single thread.

### Exercise 4: State compiler requirements

**Trap to avoid:** Writing that the kernel requires a recent version gives no way to reproduce the build.

### Exercise 5: Design a library comparison

**Trap to avoid:** Timing the DSL kernel once against a warmed library call reports the DSL as much slower purely because of compilation.

### Exercise 6: Explain a resource tradeoff

**Trap to avoid:** Concluding that larger tiles are always faster because they reuse more data predicts a direction that only device evidence can establish.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Start each tile at a multiple of the tile size and end it before the next start or at the vector length.
2. In the last tile, compute which lane offsets fall beyond the length and guard both their loads and their stores.
3. Ask which decisions the programmer writes in a thread-level kernel that a tile compiler makes instead.
4. Record the DSL release, the compiler and the device architectures that release supports.
5. Use the same shape, dtype and timing boundary for the library call, the thread reference and the tile kernel.
6. Ask what a larger tile keeps live per program and what that does to how many programs can run together.

## Common mistakes and self-check

A common mistake is masking the final tile's loads but not its stores, or the reverse, so the two invalid lanes of the third tile read or write past the vector. Another is assuming a larger tile is faster because it improves reuse; it can raise register pressure and lower concurrency. Fix both by applying one mask to every boundary load and store, and by letting measurements on a supported device, not tile size alone, decide the direction of a performance change.

**Misconception:** A tile language makes memory layout someone else's problem because the compiler chooses the instructions. **Correction:** The compiler distributes work inside a tile, but the program still decides tile shapes, the order of loads and how data is laid out in memory. A strided or misaligned layout can still waste bandwidth, so compare against a library and the thread-level reference on the same operation.

**Evidence limit:** The reference partitions 10 elements into three tiles, each element covered once. It does not compile Triton or a CUDA tile kernel, so masking in generated code, supported operations and performance need a prepared DSL release on a compatible device.

1. What does a tile-level language change for the programmer?
2. Why use half-open tile intervals?
3. Does opening this lesson give the Python worker a DSL compiler?

Answers: [self-check answers](../solutions/cuda-106_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-106: A modern tile-based kernel DSL.
Read courses/cuda/python/guides/cuda-106.md and courses/cuda/python/lessons/cuda-106.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
