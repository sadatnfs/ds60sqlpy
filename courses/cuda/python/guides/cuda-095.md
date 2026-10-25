# cuda-095: Inference has a different performance contract

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-087`, `cuda-090`, `cuda-092`. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **compute throughput**, **specify TensorFlow training behavior**, and **test an exported signature boundary** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

Inference evaluates a trained model without performing optimizer updates, but framework mode still matters. Dropout and normalization can change behavior between training and evaluation. PyTorch eval and inference_mode address different concerns: module behavior versus autograd bookkeeping. TensorFlow calls need explicit inference behavior where the layer contract uses training, and exported signatures need shape and dtype definitions.

Latency per request, batch throughput, tail latency, cold start and memory are separate metrics. A large batch can improve items per second while making an interactive request wait longer. Measure output materialization when a response must be sent to a CPU client. Include model loading and compilation in a separate cold-start result instead of hiding them in warmup.



## Worked examples

### Worked example 1

A batch of 32 completes in 8 ms, giving 4000 items per second. That does not imply a single request has 0.25 ms latency when queueing and execution require the whole 8 ms.

### Worked example 2

Dropout randomly removes activations during training but should follow the framework's inference contract at evaluation. Disabling gradients alone does not necessarily switch module training behavior.

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
batch, seconds = 32, 0.008
throughput = batch / seconds
amortized = seconds / batch
assert throughput == 4000
assert amortized == 0.00025
print("CPU serving model:", throughput, "items/s; batch latency", seconds, "s")
```

**Expected observation:** 4000 items/s with 8 ms batch latency, not 0.25 ms request latency.

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.

## Equal framework lanes

### PyTorch

Use model.eval to select evaluation behavior and torch.inference_mode to avoid autograd work. They solve different problems. Materialize the final output inside response-latency timing.

### TensorFlow

Call relevant layers with training=False and define a SavedModel serving signature for the external deployment route. Check output dtypes/shapes and first-call versus warm behavior.

Choose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.

## Executable framework practice

The variant chooser offers **PyTorch on CPU**, **TensorFlow on CPU**, and separate **NVIDIA CUDA** versions. CPU versions force CPU placement. CUDA versions require the named GPU profile and refuse to silently fall back. Each complete program uses the same tiny deterministic objective, bounded tensors and local synthetic data. Read its source before running; a framework pass establishes only that variant and environment.

The checkpoint demonstration is in-memory. It teaches what state must be saved; it does not export a durable model artifact or preserve an in-flight device context. Advanced custom-op, distributed and engine-building projects remain separately prepared external workflows.

## Practice and transfer

### Exercise 1: Compute throughput

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 1 targets **compute throughput** in the examples above.

### Exercise 2: Separate per-item cost and request latency

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 2 targets **separate per-item cost and request latency** in the examples above.

### Exercise 3: Set both PyTorch inference controls

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 3 targets **set both PyTorch inference controls** in the examples above.

### Exercise 4: Specify TensorFlow training behavior

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 4 targets **specify TensorFlow training behavior** in the examples above.

### Exercise 5: Measure cold start

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 5 targets **measure cold start** in the examples above.

### Exercise 6: Test an exported signature boundary

Write your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise 6 targets **test an exported signature boundary** in the examples above.

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

1. Start from worked example 1 and mark the quantities needed for the task "Compute throughput".
2. Change one assumption in worked example 2 while preserving the declared contract: separate per-item cost and request latency.
3. Trace the CPU program's variables before adding hardware behavior: set both PyTorch inference controls.
4. Draw producers, consumers and the exact operation boundary for the task "Specify TensorFlow training behavior".
5. Separate what the small fixture establishes from what the real runtime must show: measure cold start.
6. Write a counterexample to an overbroad claim before you test an exported signature boundary.

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `Compute throughput`. For the final claim use `Test an exported signature boundary`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.

## Ask an AI tutor about this lesson

> I am studying `cuda-095` using `courses/cuda/python/guides/cuda-095.md` and `courses/cuda/python/lessons/cuda-095.md`. Help me reason about Inference has a different performance contract. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
