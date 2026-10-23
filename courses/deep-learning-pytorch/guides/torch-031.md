# torch-031: Profiling, torch.compile and honest performance measurement

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-030`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Compilation and profiling answer different questions. The central investigation is concrete: Evaluatef(x)=x*x+1 at float32[1, 2]. The finish condition is output[2, 5]. receipt does not claim universal speedup. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Compilation and profiling answer different questions. torch.compile captures eligible Python/tensor computation and sends graphs to a selected backend. An eager graph backend can demonstrate capture and specialization without compiling optimized native kernels. That is useful in a bounded classroom image but is not an Inductor speedup claim. Input dtype, shape and Python control can affect graph reuse or graph breaks.

Measure correctness before performance. The first call can include capture and setup, while later calls reuse prepared work. A small timing sample is an observation for one environment, not a universal ranking. The CPU profiler can identify which operations ran and where time was attributed, but profiling itself adds overhead. This lesson uses a custom backend that records captured graphs and returns their eager forward function, then separates warmup and steady-state measurements explicitly.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-031](../../deep-learning-tensorflow/guides/tf-031.md) after deriving the shared numerical contract.

TensorFlow tf.function also separates graph construction from repeated execution, but its tracing and execution stack are not identical to torch.compile. This PyTorch lesson explicitly selects an eager graph backend, so it should not be compared with an optimizing TensorFlow runtime as a performance contest.

## Vocabulary and concepts

**Graph capture:** Representing eligible tensor computation as a reusable graph.

**Backend:** The implementation receiving a captured graph for execution or compilation.

**Warmup:** Initial setup calls separated from repeated-work measurement.

**Profiler overhead:** Extra work introduced by measurement instrumentation.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-031/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-031.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-031.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

torch.compile(function, backend=counting_backend, full graph=True, dynamic=False) passes capture dF X graphs to a local backend. The backend records each graph and returns graph.forward. Repeated equal signatures should reuse the capture; changed dtype needs separate treatment. time.perf_counter measures elapsed wall time. torch.profiler.profile with CPU act iv i ties records eager tensor operations without assuming aGPU or native optimizing compiler.

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

1. **Establish an eager oracle.** Evaluatef(x)=x*x+1 at float32[1, 2].
   **Expected:** output[2, 5].
   **Verify:** Save the assertion results for exercise 1, including output[2, 5].

2. **Capture with a transparent backend.** Compile using a counting backend that returns graph.forward and compare output.
   **Expected:** captured graph exists; output matches eager.
   **Verify:** Save the assertion results for exercise 2, including captured graph exists; output matches eager.

3. **Check signature reuse.** Call with float32[3, 4], then with float64[1, 2].
   **Expected:** same signature reuses capture; changed dtype adds a graph.
   **Verify:** Save the assertion results for exercise 3, including same signature reuses capture; changed dtype adds a graph.

4. **Measure warmed calls honestly.** Warm the float32 path, then execute20 calls and record elapsed time.
   **Expected:** 20 correct outputs and nonnegative elapsed time.
   **Verify:** Save the assertion results for exercise 4, including 20 correct outputs and nonnegative elapsed time.

5. **Inspect actual CPU operations.** Profile one eager call and inspect operation names.
   **Expected:** aten::mul and a ten::add appear.
   **Verify:** Save the assertion results for exercise 5, including aten::mul and a ten::add appear.

6. **State the backend limitation.** Record graph capture True, optimizing native backend False and GPU benchmark False.
   **Expected:** receipt does not claim universal speedup.
   **Verify:** Save the assertion results for exercise 6, including receipt does not claim universal speedup.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

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
