# cuda-079: Python kernels meet memory performance

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-007`, `cuda-071`, `cuda-075`, `cuda-076`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Count touched segments.
- Shift the base by four bytes.
- Model a stride of two.
- Explain tiled transpose.
- Separate occupancy from throughput.
- Propose a matched profiler experiment.

## Mechanism and vocabulary

Neighboring lanes accessing neighboring elements can be served by fewer memory transactions than widely strided accesses. Count bytes requested by useful data and compare them with the transactions the layout forces. Alignment, transaction granularity and cache behavior depend on architecture, so a simple segment model is educational rather than a complete GPU simulator.

A transpose illustrates the conflict: contiguous reads can lead to strided writes. Shared-memory tiling can reorganize the data before output. Padding may reduce bank conflicts for specific layouts, but it consumes shared capacity. Measure the entire kernel and inspect profiler counters before attributing speed to one mechanism. Increased occupancy is a means to hide latency, not an unconditional goal.



### Key terms

- **Warp:** A group of 32 threads that the scheduler issues together.
- **Coalesced access:** A pattern in which consecutive threads of a warp touch consecutive addresses, so the hardware combines them into few memory transactions.
- **Memory transaction:** The aligned segment of memory the hardware moves to serve a warp's request; scattered addresses need more transactions.
- **Alignment:** Placement of data at an address that is a multiple of the transaction size, so a request does not straddle extra segments.
- **Tiled transpose:** A transpose that stages a tile in shared memory so both the global read and the global write are coalesced.

## Worked examples

### Worked example 1

Eight four-byte lanes reading offsets 0,4,...,28 fit one aligned 32-byte segment in the simplified model. Offsets 0,32,...,224 touch eight segments.

### Worked example 2

A tiled transpose first reads rows cooperatively then writes rows in the transposed coordinate system. This changes traffic organization without changing the mathematical transpose.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-079_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-079_cpu.py
```

```python
def segments(offsets, width=32):
    return len({offset // width for offset in offsets})


contiguous = [4 * i for i in range(8)]
strided = [32 * i for i in range(8)]
assert segments(contiguous) == 1 and segments(strided) == 8
print("CPU segment model:", segments(contiguous), segments(strided))
```

**Expected observation:** Simplified segment counts 1 and 8, not hardware measurements.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `contiguous` | `[0, 4, 8, 12, 16, 20, 24, 28]` |
| `strided` | `[0, 32, 64, 96, 128, 160, 192, 224]` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-079.md) before opening hints.

### Exercise 1: Count touched segments

**Trap to avoid:** Counting one transaction per lane, eight here, treats every load as independent and ignores coalescing. That would make the contiguous and strided patterns look equally expensive.

### Exercise 2: Shift the base by four bytes

**Trap to avoid:** Assuming contiguity alone guarantees one segment ignores the boundary. A misaligned base can double the modeled transactions for the same amount of useful data.

### Exercise 3: Model a stride of two

**Trap to avoid:** Thinking stride only matters when it reaches the segment size misses the intermediate cost. Stride two already doubles the transactions in this model.

### Exercise 4: Explain tiled transpose

**Trap to avoid:** Expecting the shared-memory version to change the output values, or to need a different verification, confuses reorganized traffic with a different algorithm.

### Exercise 5: Separate occupancy from throughput

**Trap to avoid:** Treating the occupancy number as the performance goal leads to changes that raise the percentage while total runtime stays the same or rises.

### Exercise 6: Propose a matched profiler experiment

**Trap to avoid:** Comparing kernels that differ in dtype or element count mixes several causes. A float64 strided kernel against a float32 contiguous one cannot attribute the difference to stride.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. List each lane's byte offset, divide by the 32-byte segment size with floor division and count the distinct results.
2. Add 4 to every offset of the contiguous case and check whether the last lane now lands in a new segment.
3. Double the spacing between lanes and recount the segments eight four-byte loads touch.
4. Ask which side of a naive transpose is contiguous, the reads or the writes, and how a shared tile could swap that.
5. Ask what extra resident warps need from registers and shared memory, and whether they still wait on the same memory traffic.
6. List what to hold fixed between the two kernels and which real profiler counters would confirm a traffic difference.

## Common mistakes and self-check

A common mistake is crediting a speedup to one mechanism, such as higher occupancy or a padded shared tile, without measuring. Occupancy only helps hide latency; more resident warps can still compete for the same bandwidth or shared capacity. Another mistake is treating this chapter's segment counts as hardware facts. Fix both by holding dtype, shape and output fixed, timing the entire kernel, and checking profiler counters for memory transactions before naming a cause.

**Evidence limit:** The segment counts 1 and 8 come from a simplified 32-byte model. Real alignment, transaction granularity, caching and bank conflicts depend on the GPU architecture, so the model teaches the access pattern, not measured traffic.

1. Why can neighboring lanes reading neighboring elements be cheaper?
2. What problem does a tiled transpose address?
3. Why can padding a shared tile have a cost?

Answers: [self-check answers](../solutions/cuda-079_solutions.md#self-check-answers).

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-079: Python kernels meet memory performance.
Read courses/cuda/python/guides/cuda-079.md and courses/cuda/python/lessons/cuda-079.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
