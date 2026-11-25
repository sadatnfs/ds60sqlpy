# torch-031: Profiling, torch.compile and honest performance measurement

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-030`.

## Learning objectives

Measure performance honestly by separating an eager oracle, graph capture, warmed timing and profiler evidence.

Central investigation: Compile f(x)=\(x\cdot x+1\) with a counting backend, reuse and change its input signature, time warmed calls and profile one eager call.

Finish condition: The eager oracle returns [2, 5], the captured graph matches it, a float64 call adds a second graph, 20 warmed calls are correct with nonnegative elapsed time, aten::mul and aten::add appear, and the receipt makes no speedup claim.

## Purpose and mental model

Compilation and profiling answer different questions. torch.compile captures eligible Python/tensor computation and sends graphs to a selected backend. An eager graph backend can demonstrate capture and specialization without compiling optimized native kernels. That is useful in a bounded classroom image but is not an Inductor speedup claim. Input dtype, shape and Python control can affect graph reuse or graph breaks.

Measure correctness before performance. The first call can include capture and setup, while later calls reuse prepared work. A small timing sample is an observation for one environment, not a universal ranking. The CPU profiler can identify which operations ran and where time was attributed, but profiling itself adds overhead. This lesson uses a custom backend that records captured graphs and returns their eager forward function, then separates warmup and steady-state measurements explicitly.

## Design decisions and when to use this method

Use compilation to evaluate a specific execution strategy for a repeated, well-defined workload. First establish an independent eager result and the supported input contracts. Select and name the backend deliberately; the counting backend in this lesson is a capture diagnostic, not an optimizing native compiler.

Use profiling to answer a bottleneck question and timing to measure a declared interval. Keep cold setup, steady calls, data preparation and instrumentation overhead separate. Optimize only after the output and state contract is unchanged, and report the workload and variability rather than a universal framework ranking.

## Paired TensorFlow comparison

Compare [tf-031](../../deep-learning-tensorflow/guides/tf-031.md) after deriving the shared numerical contract.

TensorFlow tf.function also separates graph construction from repeated execution, but its tracing and execution stack are not identical to torch.compile. This PyTorch lesson explicitly selects an eager graph backend, so it should not be compared with an optimizing TensorFlow runtime as a performance contest.

## Vocabulary and concepts

**Graph capture:** Representing eligible tensor computation as a reusable graph.

**Backend:** The implementation receiving a captured graph for execution or compilation.

**Warmup:** Initial setup calls separated from repeated-work measurement.

**Profiler overhead:** Extra work introduced by measurement instrumentation.

## How to run this lesson

Run `torch-031` on the `llm-torch-cpu` worker ([launch, save and tolerance rules](../STUDY-GUIDE.md#launch-a-lesson)).

Examples B and C reuse `function`, `eager`, `x`, `first`, `graphs` and `compiled` from earlier blocks; run all three in order.

## Syntax anatomy and reasoning sequence

torch.compile(function, backend=counting_backend, fullgraph=True, dynamic=False) passes captured FX graphs to a local backend. The backend records each graph and returns graph.forward. Repeated equal signatures should reuse the capture; changed dtype needs separate treatment. time.perf_counter measures elapsed wall time. torch.profiler.profile with CPU activities records eager tensor operations without assuming a GPU or native optimizing compiler.

## Separate capture, guards, execution and measurement

The eager function computes \(x\cdot x+1\). For [1, 2], the result is [2, 5]; for [3, 4], it is [10, 17]. These literal values establish correctness without relying on the compiled wrapper as its own oracle. The selected backend receives a captured FX graph and example inputs, appends that graph to a diagnostic list, and returns graph.forward. Tensor operations then execute through that eager graph function. No optimized native kernel generation is requested by this backend.

torch.compile is the entry to a larger capture/guard/backend system. fullgraph=True asks this function to be captured as one graph and reports unsupported graph breaks rather than quietly presenting a partly captured program as the intended full graph. dynamic=False specializes the relevant shapes in this example. Those options do not remove Python dispatch and guard checks before every later call. [PyTorch 2.9 torch.compile](https://docs.pytorch.org/docs/2.9/generated/torch.compile.html).

The graph-list length counts backend capture invocations, not tensor executions. The same float32 shape can be called again with different values and reuse its graph. The float64 call changes the operation contract and adds a capture in this fixture. Other relevant guards can involve shape, strides, device, requires_grad, module mode or Python values. A cache hit is useful only when those assumptions still describe the input correctly.

Data-dependent Python control is a different issue from merely changing tensor values. A branch based on a tensor converted to a Python scalar can force a graph break or require a separately supported representation. Do not infer that this pure arithmetic example qualifies arbitrary Python side effects or control flow. Counting captures can help locate recompilation, but it cannot by itself show that all application work was represented in one optimized graph.

The measured interval starts after a warm float32 call and contains twenty repeated calls at the same input. The current reference checks the final observed output after that interval; it does not retain a separate per-call output ledger. CPU tensor operations in this path complete before the observed result is used. The elapsed time includes wrapper dispatch and guard/execution costs, but excludes initial capture, model construction and a realistic input pipeline. It is a small diagnostic sample, not a latency distribution.

Setup amortization can be expressed without inventing a benchmark. If setup cost is C, an eager call costs E, and a prepared alternative costs G, then N calls cost approximately NE versus C+NG under a simple stationary model. A break-even \(N>\frac{C}{E-G}\) exists only if \(E>G\). Hypothetical C=200ms, E=1ms, G=0.5ms would require more than 400 calls. Those are illustrative units, not measurements from this lesson, and the eager graph backend may have no positive speedup to amortize at all.

Real measurements need a fixed mode, dtype, shape distribution, thread setting and input/output boundary. Dynamic request shapes can trigger additional setup that a one-signature loop omits. Memory allocation, caches, JIT warmup and concurrent host load also matter. If a future accelerator path launches asynchronously, a host timer without an appropriate completion boundary can measure enqueue time rather than finished work. This CPU lesson does not qualify that device timing path.

The profiler answers which operations ran and where instrumented time was attributed. aten::mul and aten::add are expected for the eager expression, while conversions or wrapper operations can also appear. Their presence is not evidence that an optimizer fused them. Inclusive operator times can contain child work, so summing every inclusive entry can double-count. Self time and total time answer different questions, and aggregate CPU work can differ from elapsed wall time when threads overlap. [PyTorch 2.9 profiler](https://docs.pytorch.org/docs/2.9/profiler.html).

Profiling itself adds work. Keep an instrumented diagnosis run separate from the ordinary timing comparison unless the overhead is explicitly part of the measured system. The paired TensorFlow guide similarly distinguishes tf.function tracing from XLA compilation and names its NumPy-materialization boundary. Those are analogous questions, not identical runtimes or a fair performance contest by default.

The useful result is a packet containing correct outputs, capture/reuse observations, actual operation names, the exact timing boundary and a limited conclusion. A nonnegative elapsed interval proves the timer ran; it does not establish that this backend is faster, that throughput scales, or that a deployment meets a latency target.

## Worked example / walkthrough

### Example A: Establish an eager oracle

A simple arithmetic oracle establishes correctness before graph capture or timing is introduced.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def function(value):
    return value * value + 1


x = torch.tensor([1.0, 2.0])
eager = function(x)
assert eager.tolist() == [2.0, 5.0]
```

**Expected:** output [2, 5].

### Example B: Capture with a transparent backend

This executes a captured graph through an eager backend. It deliberately avoids a claim that native optimized kernels were generated.

```python
graphs = []


def backend(graph, example_inputs):
    graphs.append(graph)
    return graph.forward


compiled = torch.compile(function, backend=backend, fullgraph=True, dynamic=False)
torch.testing.assert_close(compiled(x), eager, atol=0, rtol=0)
first = len(graphs)
assert first >= 1
```

**Expected:** captured graph exists; output matches eager.

### Example C: Check signature reuse

Values can vary within a compatible signature. Dtype changes alter the operation contract and should not be hidden inside an average timing result.

```python
assert compiled(torch.tensor([3.0, 4.0])).tolist() == [10.0, 17.0] and len(graphs) == first
assert (
    compiled(torch.tensor([1.0, 2.0], dtype=torch.float64)).tolist() == [2.0, 5.0]
    and len(graphs) > first
)
```

**Expected:** same signature reuses capture; changed dtype adds a graph.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Establish an eager oracle. Predict exercise 6, State the backend limitation, from its prompt alone: Record graph capture True, optimizing native backend False and GPU benchmark False. Then explain why this finish condition holds: The eager oracle returns [2, 5], the captured graph matches it, a float64 call adds a second graph, 20 warmed calls are correct with nonnegative elapsed time, aten::mul and aten::add appear, and the receipt makes no speedup claim. Keep each prediction beside the observed value.

## Exercises

1. **Establish a new eager oracle.** Evaluate g(x)=2x-1 eagerly at the float32 inputs [0, 3].
   **Expected:** output [-1, 5].
   **Verify:** In a fresh process, the exercise checks confirm `affine(points).tolist() == [-1.0, 5.0]`.

2. **Capture the new function.** Compile g with a counting backend that returns graph.forward and compare it with the eager output.
   **Expected:** at least one captured graph; outputs match exactly.
   **Verify:** In a fresh process, the exercise checks confirm `compiled_affine(points)` matches `affine(points)` exactly and `len(captured) >= 1`.

3. **Predict recompilation for a new shape.** Call the compiled function with a three-element input, then with a second three-element input.
   **Expected:** the first three-element call adds a graph; the repeated shape reuses it.
   **Verify:** In a fresh process, the exercise checks confirm `after_three > before_three` and `len(captured) == after_three`.

4. **Measure warmed calls honestly.** Warm the float32 path, then execute 20 calls and record elapsed time.
   **Expected:** 20 correct outputs and nonnegative elapsed time.
   **Verify:** In a fresh process, the exercise checks confirm `observed.tolist() == [2.0, 5.0]` and `elapsed >= 0`.

5. **Inspect actual CPU operations.** Profile one eager call and inspect operation names.
   **Expected:** aten::mul and aten::add appear.
   **Verify:** In a fresh process, the exercise checks confirm `'aten::mul' in operations` and `'aten::add' in operations`.

6. **State the backend limitation.** Record graph capture True, optimizing native backend False and GPU benchmark False.
   **Expected:** receipt does not claim universal speedup.
   **Verify:** In a fresh process, the exercise checks confirm `receipt['graph_capture_checked']`, `not receipt['optimizing_native_backend']` and `not receipt['gpu_benchmark']`.

## Common pitfalls and diagnosis

If graph count grows unexpectedly, inspect the wrapper lifetime and changed guards before assuming compilation failed. If fullgraph rejects a function, locate the unsupported Python/tensor boundary instead of disabling the option and retaining the old claim. If outputs agree only at one input, add a changed-value oracle before timing more repetitions.

If a speed result looks implausible, check whether setup, synchronization, materialization or input preparation were included consistently. If profiler time exceeds wall time, inspect nesting and parallel attribution before adding columns together. If the backend only returns graph.forward, report graph capture honestly and leave native optimization or accelerator speed unclaimed.

## Progressive hints

Hint 1: Example B (Capture with a transparent backend) alters one assumption of Example A (Establish an eager oracle). Hint 2: exercise 4, Measure warmed calls honestly, should end at 20 correct outputs and nonnegative elapsed time. Work backward from it. Hint 3: exercise 5, Inspect actual CPU operations, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Check signature reuse, from its inputs alone. Predict whether exercise 3, Predict recompilation for a new shape, survives one changed input. Then explain Graph capture, Backend, Warmup in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Establish an eager oracle) cannot be rebuilt without help, revisit `torch-030` first. `torch-032` (state_dict, torch.export and inference parity) builds directly on this lesson.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 torch.compile](https://docs.pytorch.org/docs/2.9/generated/torch.compile.html), reviewed 2026-10-22 for the Graph capture, Backend, Warmup behavior these fixtures check ([verification status](../STUDY-GUIDE.md#sources-and-verification-status)).

## Interview reasoning with worked answers

**Does calling torch.compile prove a speedup?**

No. The selected backend, graph breaks, warmup, shape diversity and workload determine behavior. Measure a prepared configuration after proving correctness.

**Why use an eager backend in a course?**

It makes graph capture and guard behavior observable without adding a native-compiler dependency. The limitation is explicit rather than presented as optimized deployment.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-031, Profiling, torch.compile and honest performance measurement.
Read courses/deep-learning-pytorch/guides/torch-031.md and courses/deep-learning-pytorch/lessons/torch-031.py. Direct prerequisites: `torch-030`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
