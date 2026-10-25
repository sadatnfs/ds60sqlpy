# cuda-073: A kernel is a restricted parallel program

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-066`, `cuda-072`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **separate host and device statements**, **move an allocation out of a kernel**, and **list a prepared toolchain ledger** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

A Python GPU kernel is compiled from a restricted typed subset; the Python interpreter does not run independently on every GPU thread. Host-side allocation, file access, arbitrary objects and unsupported library calls stay outside the device function. Compilation specializes supported argument types and shapes or layouts according to the selected toolchain. The same syntax can therefore have different legality on host and device.

Keep allocation and validation in a host wrapper. The kernel receives fixed buffers and scalar parameters, calculates its index, checks bounds and writes only its assigned output. That separation makes errors easier to locate. The maintained numba-cuda distribution uses the numba.cuda namespace, so the import spelling alone does not identify which package supplied the implementation. Pin and record the distribution in a prepared environment.



## Worked examples

### Worked example 1

A host wrapper allocates an output and checks equal input lengths. A device kernel writes `y[i] = 2*x[i]` only when i is in range.

### Worked example 2

A kernel that tries to open a text file violates the execution model. Move file reading to the host, convert values into a numeric buffer, then copy explicitly.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
def affine_reference(values, scale):
    return [scale * x for x in values]


assert affine_reference([1, -2, 3], 2) == [2, -4, 6]
assert affine_reference([], 2) == []
print("CPU kernel oracle:", affine_reference([1, -2, 3], 2))
```

**Expected observation:** [2, -4, 6], with empty input accepted by the oracle.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Separate host and device statements

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **separate host and device statements** in the examples above.

### Exercise 2: Implement the CPU oracle

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **implement the CPU oracle** in the examples above.

### Exercise 3: Reject mismatched lengths

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **reject mismatched lengths** in the examples above.

### Exercise 4: Move an allocation out of a kernel

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **move an allocation out of a kernel** in the examples above.

### Exercise 5: Explain type specialization

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **explain type specialization** in the examples above.

### Exercise 6: List a prepared toolchain ledger

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **list a prepared toolchain ledger** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Separate host and device statements".
2. Change one assumption in worked example 2 while preserving the declared contract: implement the CPU oracle.
3. Trace the CPU program's variables before adding hardware behavior: reject mismatched lengths.
4. Draw producers, consumers and the exact operation boundary for the task "Move an allocation out of a kernel".
5. Separate what the small fixture establishes from what the real runtime must show: explain type specialization.
6. Write a counterexample to an overbroad claim before you list a prepared toolchain ledger.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Separate host and device statements`. For the final claim use `List a prepared toolchain ledger`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-073` using `courses/cuda/python/guides/cuda-073.md` and `courses/cuda/python/lessons/cuda-073.md`. Help me reason about A kernel is a restricted parallel program. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)
- [Maintained numba-cuda project](https://github.com/NVIDIA/numba-cuda)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
