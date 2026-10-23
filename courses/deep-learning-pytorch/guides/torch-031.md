# torch-031: Profiling, torch.compile and honest performance measurement

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-030`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Compilation and profiling answer different questions. The central investigation is concrete: Evaluatef(x)=\(x\cdot x+1\) at float32[1, 2]. The finish condition is output[2, 5]. receipt does not claim universal speedup. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

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

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-031/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-031.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-031.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

torch.compile(function, backend=counting_backend, fullgraph=True, dynamic=False) passes captured FX graphs to a local backend. The backend records each graph and returns graph.forward. Repeated equal signatures should reuse the capture; changed dtype needs separate treatment. time.perf_counter measures elapsed wall time. torch.profiler.profile with CPU activities records eager tensor operations without assuming aGPU or native optimizing compiler.

## Separate capture, guards, execution and measurement

The eager function computes \(x\cdot x+1\). For[1, 2], the result is[2, 5]; for[3, 4], it is[10, 17]. These literal values establish correctness without relying on the compiled wrapper as its own oracle. The selected backend receives a captured FX graph and example inputs, appends that graph to a diagnostic list, and returns graph.forward. Tensor operations then execute through that eager graph function. No optimized native kernel generation is requested by this backend.

torch.compile is the entry to a larger capture/guard/backend system. fullgraph=True asks this function to be captured as one graph and reports unsupported graph breaks rather than quietly presenting a partly captured program as the intended full graph. dynamic=False specializes the relevant shapes in this example. Those options do not remove Python dispatch and guard workaround every later call. [PyTorch 2.9 torch.compile](https://docs.pytorch.org/docs/2.9/generated/torch.compile.html).

The graph-list length counts backend capture invocations, not tensor executions. The same float32 shape can be called again with different values and reuse its graph. The float64 call changes the operation contract and adds a capture in this fixture. Other relevant guards can involve shape, strides, device, requires_grad, module mode or Python values. A cache hit is useful only when those assumptions still describe the input correctly.

Data-dependent Python control is a different issue from merely changing tensor values. A branch based on a tensor converted to a Python scalar can force a graph break or require a separately supported representation. Do not infer that this pure arithmetic example qualifies arbitrary Python side effects or control flow. Counting captures can help locate recompilation, but it cannot by itself show that all application work was represented in one optimized graph.

The measured interval starts after a warm float32 call and contains twenty repeated calls at the same input. The current reference checks the final observed output after that interval; it does not retain a separate per-call output ledger. CPU tensor operations in this path complete before the observed result is used. The elapsed time includes wrapper dispatch and guard/execution costs, but excludes initial capture, model construction and a realistic input pipeline. It is a small diagnostic sample, not a latency distribution.

Setup amortization can be expressed without inventing a benchmark. If setup cost is C, an eager call costs E, and a prepared alternative costs G, then N calls cost approximately NE versus C+NG under a simple stationary model. A break-even \(N>\frac{C}{E-G}\) exists only if \(E>G\). Hypothetical C=200ms, E=1ms, G=0.5ms would require more than 400 calls. Those are illustrative units, not measurements from this lesson, and the eager graph backend may have no positive speedup to amortize at all.

Real measurements need a fixed mode, dtype, shape distribution, thread setting and input/output boundary. Dynamic request shapes can trigger additional setup that a one-signature loop omits. Memory allocation, caches, JIT warmup and concurrent host load also matter. If a future accelerator path launches asynchronously, a host timer without an appropriate completion boundary can measure enqueue time rather than finished work. This CPU lesson does not qualify that device timing path.

The profiler answers which operations ran and where instrumented time was attributed. aten:: mul and aten:: add are expected for the eager expression, while conversions or wrapper operations can also appear. Their presence is not evidence that an optimizer fused them. Inclusive operator times can contain child work, so summing every inclusive entry can double-count. Self time and total time answer different questions, and aggregate CPU work can differ from elapsed wall time when threads overlap. [PyTorch 2.9 profiler](https://docs.pytorch.org/docs/2.9/profiler.html).

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

def function(value): return value*value+1
x=torch.tensor([1.,2.]); eager=function(x)
assert eager.tolist()==[2.,5.]
```

**Expected:** output[2, 5].

### Example B: Capture with a transparent backend

This executes a captured graph through an eager backend. It deliberately avoids a claim that native optimized kernels were generated.

```python
graphs=[]
def backend(graph,example_inputs): graphs.append(graph); return graph.forward
compiled=torch.compile(function,backend=backend,fullgraph=True,dynamic=False)
torch.testing.assert_close(compiled(x),eager,atol=0,rtol=0); first=len(graphs); assert first>=1
```

**Expected:** captured graph exists; output matches eager.

### Example C: Check signature reuse

Values can vary within a compatible signature. Dtype changes alter the operation contract and should not be hidden inside an average timing result.

```python
assert compiled(torch.tensor([3.,4.])).tolist()==[10.,17.] and len(graphs)==first
assert compiled(torch.tensor([1.,2.],dtype=torch.float64)).tolist()==[2.,5.] and len(graphs)>first
```

**Expected:** same signature reuses capture; changed dtype adds a graph.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: output[2, 5]. receipt does not claim universal speedup. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Establish an eager oracle.** Evaluatef(x)=\(x\cdot x+1\) at float32[1, 2].
   **Expected:** output[2, 5].
   **Verify:** Save the assertion results for exercise 1, including output[2, 5].

2. **Capture with a transparent backend.** Compile using a counting backend that returns graph.forward and compare output.
   **Expected:** captured graph exists; output matches eager.
   **Verify:** Save the assertion results for exercise 2, including captured graph exists; output matches eager.

3. **Check signature reuse.** Call with float32[3, 4], then with float64[1, 2].
   **Expected:** same signature reuses capture; changed dtype adds a graph.
   **Verify:** Save the assertion results for exercise 3, including same signature reuses capture; changed dtype adds a graph.

4. **Measure warmed calls honestly.** Warm the float32 path, then execute 20 calls and record elapsed time.
   **Expected:** 20 correct outputs and nonnegative elapsed time.
   **Verify:** Save the assertion results for exercise 4, including 20 correct outputs and nonnegative elapsed time.

5. **Inspect actual CPU operations.** Profile one eager call and inspect operation names.
   **Expected:** aten:: mul and aten:: add appear.
   **Verify:** Save the assertion results for exercise 5, including aten:: mul and aten:: add appear.

6. **State the backend limitation.** Record graph capture True, optimizing native backend False and GPU benchmark False.
   **Expected:** receipt does not claim universal speedup.
   **Verify:** Save the assertion results for exercise 6, including receipt does not claim universal speedup.

## Common pitfalls and diagnosis

If graph count grows unexpectedly, inspect the wrapper lifetime and changed guards before assuming compilation failed. If fullgraph rejects a function, locate the unsupported Python/tensor boundary instead of disabling the option and retaining the old claim. If outputs agree only at one input, add a changed-value oracle before timing more repetitions.

If a speed result looks implausible, check whether setup, synchronization, materialization or input preparation were included consistently. If profiler time exceeds wall time, inspect nesting and parallel attribution before adding columns together. If the backend only returns graph.forward, report graph capture honestly and leave native optimization or accelerator speed unclaimed.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Graph capture, Backend, Warmup using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-030` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 torch.compile](https://docs.pytorch.org/docs/2.9/generated/torch.compile.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Does calling torch.compile prove a speedup?**

No. The selected backend, graph breaks, warmup, shape diversity and workload determine behavior. Measure a prepared configuration after proving correctness.

**Why use an eager backend in a course?**

It makes graph capture and guard behavior observable without adding a native-compiler dependency. The limitation is explicit rather than presented as optimized deployment.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-031, Profiling, torch.compile and honest performance measurement.
Read courses/deep-learning-pytorch/guides/torch-031.md and courses/deep-learning-pytorch/lessons/torch-031.py. Direct prerequisites: `torch-030`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
