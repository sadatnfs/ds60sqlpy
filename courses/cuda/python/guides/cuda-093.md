# cuda-093: Graphs, compilation and shape behavior

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-087`, `cuda-092`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Count specializations.
- Calculate break-even calls.
- Describe a graph break.
- Specify an accepted shape set.
- Compare gradients.
- Separate compilation and replay.

## Mechanism and vocabulary

Tracing records a representation of operations; compilation transforms that representation; replay reuses prepared work. These are related but different. Python side effects, data-dependent control flow and changing shapes may trigger graph breaks or new specializations. A compiled path can spend substantial time before steady-state execution, which matters for short-lived jobs.

PyTorch torch.compile has guards and graph-break behavior; TensorFlow tf.function uses tracing and signatures, with XLA an additional choice. Explain them through each framework's idioms. Compare eager and compiled outputs and gradients over the accepted shape set. CUDA Graph replay has further restrictions around allocations and stable execution, so a generic graph API is not proof of CUDA Graph use.



### Key terms

- **Tracing:** Recording the operations executed on sample inputs to build a graph for compilation.
- **Graph break:** A point where the compiler cannot capture code, so execution falls back to eager Python.
- **Shape specialization:** Compiling for specific input shapes, so a new shape can trigger recompilation.
- **Break-even call count:** The number of calls after which compile time is repaid by faster steady-state execution.

## Worked examples

### Worked example 1

A specialization cache sees shapes (4,8),(4,8),(8,8) and compiles twice in a simplified model. Repeating the first shape reuses its entry.

### Worked example 2

A compiled model saves 1 ms per call after a 500 ms compile. More than 500 equivalent calls are needed to repay that startup cost under this simple model.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-093_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-093_cpu.py
```

```python
shapes = [(4, 8), (4, 8), (8, 8)]
assert len(set(shapes)) == 2
compile_ms, saving_ms = 500, 1
assert compile_ms / saving_ms == 500
print("CPU compilation model:", len(set(shapes)), "specializations; break-even", 500)
```

**Expected observation:** Two modeled specializations; 500-call break-even.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `shapes` | `[(4, 8), (4, 8), (8, 8)]` |
| `compile_ms` | `500` |
| `saving_ms` | `1` |

## Equal framework lanes

### PyTorch

Compare eager and torch.compile with the same initial state. Record compilation latency, shape guards, graph breaks and accepted shape changes; do not claim every graph uses CUDA Graph replay.

### TensorFlow

Compare eager and tf.function with a stated input signature. Count retraces, then evaluate XLA as a separate configuration and preserve both outputs and gradients.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-093.md) before opening hints.

### Exercise 1: Count specializations

**Trap to avoid:** Counting one compilation per call, three here, ignores the cache and overestimates startup cost. Counting one compilation total assumes the compiler generalizes across shapes, which static specialization does not.

### Exercise 2: Calculate break-even calls

**Trap to avoid:** Assuming compilation pays off immediately because each call is faster ignores the startup cost. A short-lived job of 100 calls loses 400 ms overall.

### Exercise 3: Describe a graph break

**Trap to avoid:** Assuming a program that ran without errors under the compiler was compiled as one graph overlooks silent breaks, which are reported only when logging is enabled.

### Exercise 4: Specify an accepted shape set

**Trap to avoid:** Accepting arbitrary shapes in production lets each new batch size trigger a recompilation, causing latency spikes.

### Exercise 5: Compare gradients

**Trap to avoid:** Checking only that forward outputs match and assuming gradients follow can miss a backward bug that shows up only as slower training.

### Exercise 6: Separate compilation and replay

**Trap to avoid:** Expecting graph replay to speed up compute-bound kernels confuses launch overhead with kernel time.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. List the shape signatures in order and count how many are new when they arrive.
2. Divide the compile time by the per-call saving, then check the calls just below and above that number.
3. Ask what happens when compiled code meets a Python side effect or a data-dependent branch it cannot capture.
4. Write the dimensions and dtypes the compiled path must accept, with explicit bounds.
5. Ask whether matching forward outputs guarantees that the backward pass matches too.
6. Ask which step generates code and which step only reuses a recorded execution schedule.

## Common mistakes and self-check

A common mistake is enabling compilation for a short job and reporting a speedup from warm calls only. With a 500 ms compile and a 1 ms saving per call, the first 500 calls are slower in total. Another mistake is feeding many distinct shapes, which triggers new specializations or graph breaks. Fix both by stating an accepted shape set, measuring compile time separately and comparing eager and compiled outputs and gradients across that set.

**Misconception:** A compiled function always computes exactly the same values as its eager version. **Correction:** Compilation can fuse operations and reorder floating-point arithmetic, and Python side effects in traced code may run once at trace time rather than on every call. Compare compiled and eager outputs and gradients with a stated tolerance over the accepted shape set, and keep side effects outside compiled regions.

**Evidence limit:** The reference counts two specializations and a 500-call break-even with a simplified cache. Real frameworks use guards, graph breaks and recompilation limits of their own, so actual behavior must be observed with the pinned PyTorch or TensorFlow release.

1. How do tracing, compilation and replay differ?
2. Why can changing shapes slow a compiled model?
3. Is using a generic graph API proof that CUDA Graph replay happened?

Answers: [self-check answers](../solutions/cuda-093_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-093: Graphs, compilation and shape behavior.
Read courses/cuda/python/guides/cuda-093.md and courses/cuda/python/lessons/cuda-093.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
