# cuda-093: Graphs, compilation and shape behavior

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-087`, `cuda-092`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **count specializations**, **specify an accepted shape set**, and **separate compilation and replay** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Tracing records a representation of operations; compilation transforms that representation; replay reuses prepared work. These are related but different. Python side effects, data-dependent control flow and changing shapes may trigger graph breaks or new specializations. A compiled path can spend substantial time before steady-state execution, which matters for short-lived jobs.

PyTorch torch.compile has guards and graph-break behavior; TensorFlow tf.function uses tracing and signatures, with XLA an additional choice. Explain them through each framework's idioms. Compare eager and compiled outputs and gradients over the accepted shape set. CUDA Graph replay has further restrictions around allocations and stable execution, so a generic graph API is not proof of CUDA Graph use.



## Worked examples

### Worked example 1

A specialization cache sees shapes (4,8),(4,8),(8,8) and compiles twice in a simplified model. Repeating the first shape reuses its entry.

### Worked example 2

A compiled model saves 1 ms per call after a 500 ms compile. More than 500 equivalent calls are needed to repay that startup cost under this simple model.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
shapes = [(4, 8), (4, 8), (8, 8)]
assert len(set(shapes)) == 2
compile_ms, saving_ms = 500, 1
assert compile_ms / saving_ms == 500
print("CPU compilation model:", len(set(shapes)), "specializations; break-even", 500)
```

**Expected observation:** Two modeled specializations;500-call break-even.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Compare eager and torch.compile with the same initial state. Record compilation latency, shape guards, graph breaks and accepted shape changes; do not claim every graph uses CUDA Graph replay.

### TensorFlow

Compare eager and tf.function with a stated input signature. Count retraces, then evaluate XLA as a separate configuration and preserve both outputs and gradients.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Practice and transfer

### Exercise 1: Count specializations

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **count specializations** in the examples above.

### Exercise 2: Calculate break-even calls

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **calculate break-even calls** in the examples above.

### Exercise 3: Describe a graph break

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **describe a graph break** in the examples above.

### Exercise 4: Specify an accepted shape set

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **specify an accepted shape set** in the examples above.

### Exercise 5: Compare gradients

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **compare gradients** in the examples above.

### Exercise 6: Separate compilation and replay

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **separate compilation and replay** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Count specializations".
2. Change one assumption in worked example 2 while preserving the declared contract: calculate break-even calls.
3. Trace the CPU program's variables before adding hardware behavior: describe a graph break.
4. Draw producers, consumers and the exact operation boundary for the task "Specify an accepted shape set".
5. Separate what the small fixture establishes from what the real runtime must show: compare gradients.
6. Write a counterexample to an overbroad claim before you separate compilation and replay.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Count specializations`. For the final claim use `Separate compilation and replay`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-093` using `courses/cuda/python/guides/cuda-093.md` and `courses/cuda/python/lessons/cuda-093.md`. Help me reason about Graphs, compilation and shape behavior. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
