# cuda-080: A simulator is a debugging tool

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-073`, `cuda-074`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **classify a CPU result**, **design the validation ladder**, and **write an honest evidence label** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A simulator reproduces selected semantics to help inspect indexing and values without requiring the actual device. It usually does not reproduce warp scheduling, memory transactions, concurrent timing, occupancy or all synchronization defects. A serialized execution can hide a race that real concurrent threads expose. Passing a simulator therefore belongs to a different evidence category from passing hardware execution.

Keep a validation ladder: mathematical reference, CPU mapping model, compiler acceptance, real-device output, diagnostic tooling and repeated stress cases. The simulator is useful early in that ladder, especially for small inputs you can inspect by hand. Do not generate invented GPU names, bandwidth or throughput from simulator output. If a feature is unsupported by the chosen simulator, state that instead of changing the algorithm silently.



### Key terms

- **CUDA simulator:** An interpreter that runs kernel code on the CPU for debugging, without real GPU timing or memory behavior.
- **Data race:** Unsynchronized accesses to the same address by several threads where at least one access is a write.
- **Serialized execution:** Running threads one at a time, which can hide races that would appear under true parallel execution.
- **Validation ladder:** A sequence of checks from simulator to CPU oracle to real hardware, where each step catches a different class of error.

## Worked examples

### Worked example 1

A CPU loop visiting all valid indices proves the intended index formula covers the array. It does not prove the GPU compiler generated a correct program for the target architecture.

### Worked example 2

A shared counter incremented serially yields the expected count even when the corresponding parallel code lacks an atomic operation. The serial result hides the race.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
serial_counter = 0
for _ in range(2):
    serial_counter += 1
parallel_reads = [0, 0]
lost_update = max(value + 1 for value in parallel_reads)
assert serial_counter == 2 and lost_update == 1
print("CPU race illustration:", serial_counter, lost_update)
```

**Expected observation:** Serial count 2 versus a possible lost-update count 1.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `serial_counter` | `2` |
| `parallel_reads` | `[0, 0]` |
| `lost_update` | `1` |

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Classify a CPU result

**Trap to avoid:** Calling the result GPU verified because the same Python source was used assumes the compiled device code behaves like the interpreter.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 2: Construct a race hidden by serialization

**Trap to avoid:** Concluding the kernel needs no atomics because the simulator printed the right count treats a serial schedule as representative of every parallel schedule.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 3: Name an unsupported feature

**Trap to avoid:** Assuming anything that runs in the simulator runs identically on hardware ignores that the simulator interprets kernels in Python.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 4: Design the validation ladder

**Trap to avoid:** Collapsing the ladder into a single pass/fail end-to-end test hides where a failure came from.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 5: Choose a tiny debugging input

**Trap to avoid:** Debugging with a million random elements makes a single wrong index hard to find. A size that is a multiple of the block hides tail bugs.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

### Exercise 6: Write an honest evidence label

**Trap to avoid:** Writing only verified or tests pass gives no executor and invites the reader to assume GPU coverage.

Show the intermediate values or the boundary that rules this route out, then record your answer in the worksheet.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Classify a CPU result".
2. Change one assumption in worked example 2 while preserving the declared contract: construct a race hidden by serialization.
3. Trace the CPU program's variables before adding hardware behavior: name an unsupported feature.
4. Draw producers, consumers and the exact operation boundary for the task "Design the validation ladder".
5. Separate what the small fixture establishes from what the real runtime must show: choose a tiny debugging input.
6. Write a counterexample to an overbroad claim before you write an honest evidence label.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Classify a CPU result`. For the final claim use `Write an honest evidence label`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

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
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-080: A simulator is a debugging tool.
Read courses/cuda/python/guides/cuda-080.md and courses/cuda/python/lessons/cuda-080.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
