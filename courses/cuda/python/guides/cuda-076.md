# cuda-076: Shared memory and collective responsibility

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-002`, `cuda-075`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **choose a sum identity**, **repair early return**, and **design a nonmultiple test** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Shared memory is a block-local cooperation area. Threads load assigned pieces, synchronize, then consume data another thread may have produced. A barrier is a collective obligation: all threads that participate in a block must reach compatible synchronization points. Returning early for a tail lane before a required barrier can leave other threads waiting or produce undefined behavior.

For a partial tile, valid lanes load input while invalid lanes write the operation's identity, such as zero for a sum. Every lane still reaches the barrier. The identity is algorithm-specific: minimum needs a suitably large sentinel, and a weighted average needs counts as well as sums. Shared storage does not communicate between arbitrary blocks; cross-block cooperation needs a separate algorithm or explicitly supported launch mechanism.



## Worked examples

### Worked example 1

A four-lane tile reads [2,4,6] and stores [2,4,6,0]. All four lanes synchronize, then the block computes sum 12.

### Worked example 2

Replacing the invalid lane with an early return is unsafe when later code has a block barrier. Keeping that lane active with a neutral value preserves collective participation.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
tile = [2, 4, 6]
width = 4
shared = [tile[i] if i < len(tile) else 0 for i in range(width)]
participants = list(range(width))
assert participants == [0, 1, 2, 3]
assert sum(shared) == 12
print("CPU cooperative model:", shared, sum(shared))
```

**Expected observation:** All four modeled lanes participate; padded sum is 12.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Choose a sum identity

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **choose a sum identity** in the examples above.

### Exercise 2: Choose a minimum identity

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **choose a minimum identity** in the examples above.

### Exercise 3: Trace barrier participants

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **trace barrier participants** in the examples above.

### Exercise 4: Repair early return

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **repair early return** in the examples above.

### Exercise 5: Separate block and grid scope

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **separate block and grid scope** in the examples above.

### Exercise 6: Design a nonmultiple test

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **design a nonmultiple test** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Choose a sum identity".
2. Change one assumption in worked example 2 while preserving the declared contract: choose a minimum identity.
3. Trace the CPU program's variables before adding hardware behavior: trace barrier participants.
4. Draw producers, consumers and the exact operation boundary for the task "Repair early return".
5. Separate what the small fixture establishes from what the real runtime must show: separate block and grid scope.
6. Write a counterexample to an overbroad claim before you design a nonmultiple test.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Choose a sum identity`. For the final claim use `Design a nonmultiple test`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-076` using `courses/cuda/python/guides/cuda-076.md` and `courses/cuda/python/lessons/cuda-076.md`. Help me reason about Shared memory and collective responsibility. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)
- [Maintained numba-cuda project](https://github.com/NVIDIA/numba-cuda)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
