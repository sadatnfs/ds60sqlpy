# cuda-107: Python-accessible CUDA library algorithms

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-082`, `cuda-085`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **trace stable sorting**, **account for temporary storage**, and **choose a release-specific contract** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Library algorithms expose more than an operation name. Sorting needs comparator and stability semantics; reductions need identity and dtype rules; matrix operations need layout and leading dimensions; FFTs need normalization and transform conventions. Some APIs create reusable plans or request temporary storage. Plan lifetime, workspace ownership and stream association affect both correctness and performance.

Choose a small release-pinned library family instead of installing every package. Compare an educational reference and a prepared library result on tiny fixtures, including empty or rejected cases and duplicate keys. Reuse plans only when their shape/dtype contract permits. Report plan creation separately from repeated execution. Python accessibility does not eliminate CUDA resource and compatibility requirements.



## Worked examples

### Worked example 1

A stable sort of [(2, A),(1, B),(2, C)] by key retains A before C among equal keys. An unstable sort may legally change that relative order.

### Worked example 2

A matrix multiply output shape follows contracted dimensions: a 2 by 3 matrix times 3 by 4 gives 2 by 4. A plan prepared for a different dtype or shape cannot be reused blindly.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
records = [(2, "A"), (1, "B"), (2, "C")]
ordered = sorted(records, key=lambda row: row[0])
assert ordered == [(1, "B"), (2, "A"), (2, "C")]
a, b = (2, 3), (3, 4)
assert a[1] == b[0]
print("CPU library contracts:", ordered, "matrix output", (a[0], b[1]))
```

**Expected observation:** Stable duplicate order and matrix output shape (2,4).

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Trace stable sorting

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **trace stable sorting** in the examples above.

### Exercise 2: Specify duplicate semantics

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **specify duplicate semantics** in the examples above.

### Exercise 3: Calculate output shape

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **calculate output shape** in the examples above.

### Exercise 4: Account for temporary storage

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **account for temporary storage** in the examples above.

### Exercise 5: Separate plan creation

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **separate plan creation** in the examples above.

### Exercise 6: Choose a release-specific contract

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **choose a release-specific contract** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Trace stable sorting".
2. Change one assumption in worked example 2 while preserving the declared contract: specify duplicate semantics.
3. Trace the CPU program's variables before adding hardware behavior: calculate output shape.
4. Draw producers, consumers and the exact operation boundary for the task "Account for temporary storage".
5. Separate what the small fixture establishes from what the real runtime must show: separate plan creation.
6. Write a counterexample to an overbroad claim before you choose a release-specific contract.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Trace stable sorting`. For the final claim use `Choose a release-specific contract`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-107` using `courses/cuda/python/guides/cuda-107.md` and `courses/cuda/python/lessons/cuda-107.md`. Help me reason about Python-accessible CUDA library algorithms. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
