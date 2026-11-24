# cuda-079: Python kernels meet memory performance

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-007`, `cuda-071`, `cuda-075`, `cuda-076`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **count touched segments**, **explain tiled transpose**, and **propose a matched profiler experiment** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

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

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

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

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Count touched segments

**Trap to avoid:** Counting one transaction per lane, eight here, treats every load as independent and ignores coalescing. That would make the contiguous and strided patterns look equally expensive.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Shift the base by four bytes

**Trap to avoid:** Assuming contiguity alone guarantees one segment ignores the boundary. A misaligned base can double the modeled transactions for the same amount of useful data.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Model a stride of two

**Trap to avoid:** Thinking stride only matters when it reaches the segment size misses the intermediate cost. Stride two already doubles the transactions in this model.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Explain tiled transpose

**Trap to avoid:** Expecting the shared-memory version to change the output values, or to need a different verification, confuses reorganized traffic with a different algorithm.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Separate occupancy from throughput

**Trap to avoid:** Treating the occupancy number as the performance goal leads to changes that raise the percentage while total runtime stays the same or rises.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Propose a matched profiler experiment

**Trap to avoid:** Comparing kernels that differ in dtype or element count mixes several causes. A float64 strided kernel against a float32 contiguous one cannot attribute the difference to stride.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Count touched segments".
2. Change one assumption in worked example 2 while preserving the declared contract: shift the base by four bytes.
3. Trace the CPU program's variables before adding hardware behavior: model a stride of two.
4. Draw producers, consumers and the exact operation boundary for the task "Explain tiled transpose".
5. Separate what the small fixture establishes from what the real runtime must show: separate occupancy from throughput.
6. Write a counterexample to an overbroad claim before you propose a matched profiler experiment.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Count touched segments`. For the final claim use `Propose a matched profiler experiment`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)
- [Maintained numba-cuda project](https://github.com/NVIDIA/numba-cuda)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-079: Python kernels meet memory performance.
Read courses/cuda/python/guides/cuda-079.md and courses/cuda/python/lessons/cuda-079.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
