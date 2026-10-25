# cuda-085: Choose a library before owning a kernel

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-068`, `cuda-071`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute complete latency**, **identify a maintenance cost**, and **write a keep-or-replace decision** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Library selection is an engineering decision about contracts, algorithm quality, maintenance and deployment. A tuned reduction or matrix library usually handles more shapes and architectures than a teaching kernel. A custom implementation may be justified by fusion, unusual layout or a domain-specific operation, but the benefit must survive correctness checks and end-to-end measurement.

Make a comparison ledger: supported dtypes and layouts, temporary memory, numerical behavior, warmup, concurrency, packaging and fallback. Include input sizes where launch overhead dominates and sizes where useful work dominates. A slower educational kernel can still be successful learning evidence; it should not be presented as a production improvement. Prefer the simplest implementation that satisfies the real acceptance criteria.



## Worked examples

### Worked example 1

A library pipeline takes 8 ms of kernels and 2 ms of transfer. A custom kernel saves 2 ms but adds 3 ms of packing, so total latency worsens from 10 to 11 ms.

### Worked example 2

A fused transformation reduces three launches to one and removes a large intermediate. It may win at some sizes while losing at tiny sizes where first-call compilation dominates.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
library = {"kernel": 8, "transfer": 2, "packing": 0}
custom = {"kernel": 6, "transfer": 2, "packing": 3}
assert sum(library.values()) == 10
assert sum(custom.values()) == 11
print("CPU decision model: library", sum(library.values()), "custom", sum(custom.values()))
```

**Expected observation:** Library 10 and custom 11 modeled milliseconds.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Practice and transfer

### Exercise 1: Compute complete latency

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute complete latency** in the examples above.

### Exercise 2: List a numerical contract

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **list a numerical contract** in the examples above.

### Exercise 3: Add temporary memory

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **add temporary memory** in the examples above.

### Exercise 4: Identify a maintenance cost

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **identify a maintenance cost** in the examples above.

### Exercise 5: Choose two workload sizes

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **choose two workload sizes** in the examples above.

### Exercise 6: Write a keep-or-replace decision

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **write a keep-or-replace decision** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute complete latency".
2. Change one assumption in worked example 2 while preserving the declared contract: list a numerical contract.
3. Trace the CPU program's variables before adding hardware behavior: add temporary memory.
4. Draw producers, consumers and the exact operation boundary for the task "Identify a maintenance cost".
5. Separate what the small fixture establishes from what the real runtime must show: choose two workload sizes.
6. Write a counterexample to an overbroad claim before you write a keep-or-replace decision.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute complete latency`. For the final claim use `Write a keep-or-replace decision`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-085` using `courses/cuda/python/guides/cuda-085.md` and `courses/cuda/python/lessons/cuda-085.md`. Help me reason about Choose a library before owning a kernel. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [DLPack Python specification](https://dmlc.github.io/dlpack/latest/python_spec.html)
- [CuPy interoperability](https://docs.cupy.dev/en/stable/user_guide/interoperability.html)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
