# cuda-080: A simulator is a debugging tool

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-073`, `cuda-074`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **classify a CPU result**, **design the validation ladder**, and **write an honest evidence label** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A simulator reproduces selected semantics to help inspect indexing and values without requiring the actual device. It usually does not reproduce warp scheduling, memory transactions, concurrent timing, occupancy or all synchronization defects. A serialized execution can hide a race that real concurrent threads expose. Passing a simulator therefore belongs to a different evidence category from passing hardware execution.

Keep a validation ladder: mathematical reference, CPU mapping model, compiler acceptance, real-device output, diagnostic tooling and repeated stress cases. The simulator is useful early in that ladder, especially for small inputs you can inspect by hand. Do not generate invented GPU names, bandwidth or throughput from simulator output. If a feature is unsupported by the chosen simulator, state that instead of changing the algorithm silently.



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

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Classify a CPU result

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **classify a CPU result** in the examples above.

### Exercise 2: Construct a race hidden by serialization

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **construct a race hidden by serialization** in the examples above.

### Exercise 3: Name an unsupported feature

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **name an unsupported feature** in the examples above.

### Exercise 4: Design the validation ladder

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **design the validation ladder** in the examples above.

### Exercise 5: Choose a tiny debugging input

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **choose a tiny debugging input** in the examples above.

### Exercise 6: Write an honest evidence label

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **write an honest evidence label** in the examples above.

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

## Ask an AI tutor about this lesson

> I am studying `cuda-080` using `courses/cuda/python/guides/cuda-080.md` and `courses/cuda/python/lessons/cuda-080.md`. Help me reason about A simulator is a debugging tool. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)
- [Maintained numba-cuda project](https://github.com/NVIDIA/numba-cuda)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
