# cuda-043: CUDA Graphs for repeated workflows

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-020`, `cuda-031`, `cuda-039`, `cuda-041`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Capture and replay a CUDA Graph correctly and compare its submission cost against ordinary stream launches.

**Scope:** Define, instantiate and replay a dependency graph; stream capture, lifetime of referenced resources, launch overhead and update constraints.

**Evidence to produce:** Correct replay, safe resource lifetimes, a scoped comparison and explicit unsupported changes.

## Purpose, vocabulary and mental model

A CUDA Graph represents a dependency graph that can be instantiated and replayed. It can reduce repeated host submission overhead for suitable workflows, but graph creation and instantiation cost time. Resources referenced by nodes must remain valid across execution, and updates must obey the selected graph API's rules. Stream capture records supported operations in a defined capture context; it is not permission to capture arbitrary host control flow. A CUDA Graph differs from an autograd graph: one schedules execution dependencies, while the other tracks differentiation relationships. Graph replay does not automatically fuse kernels.

### Key terms

- **CUDA Graph:** A recorded set of kernels, copies and dependencies that can be launched as one unit.
- **Stream capture:** Recording work submitted to a stream into a graph instead of executing it.
- **Graph instantiation:** Turning a graph into an executable form once so later launches avoid most per-operation overhead.
- **Graph update:** Changing parameters of an executable graph without rebuilding it, when the topology stays the same.

## Mathematical contract

\[
N_{\mathrm{break-even}}=\frac{T_{\mathrm{setup}}}{T_{\mathrm{ordinary}}-T_{\mathrm{replay}}}
\]

The denominator must be positive and the compared iteration work must be equivalent. Strict improvement needs more repetitions than equality at break-even.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-043_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-043_cpu.py
```

## CUDA C++ kernel listing

An excerpt from the chapter's complete [GPU reference](../references/cuda-043_gpu.cu); the reading pad does not compile it.

```cpp
__global__ void write_indices(int *values, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    values[i] = static_cast<int>(i);
}

__global__ void increment(int *values, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    values[i] += 1;
}
```

## Worked example 1: trace the mechanism

A synthetic pipeline spends 20 microseconds submitting each ordinary iteration. Graph replay reduces this to 5 microseconds, but setup costs 300 microseconds. Ignoring other equal costs, break-even is more than twenty repeats. At exactly twenty, the submission savings merely repay setup.

**Why:** Break-even is 20 replays, so 21 replays give 300 + 105 = 405 against 420 ordinary.

```python
setup_us, ordinary_us, replay_us = 300, 20, 5
break_even = setup_us / (ordinary_us - replay_us)
assert break_even == 20
assert setup_us + 21 * replay_us < 21 * ordinary_us
print({"synthetic_break_even_replays": break_even})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'synthetic_break_even_replays': 20.0}
```

**Check:** The reference asserts break_even == 20 and that 21 replays cost less than 21 ordinary iterations.

## Worked example 2: change a meaningful condition

A graph contains fill, affine transform and download nodes with dependencies. Replay uses the same valid storage but new input contents. Changing the input shape beyond allocation capacity is not just a new value; rebuild or perform a supported update after validating all node contracts.

**Why:** Graph nodes bake in addresses and sizes, so contents can change but capacity cannot grow.

**Check:** Replay with new values and same shape, then with a larger shape, and confirm a rebuild occurs.

## Optional CUDA C++ laboratory

- [GPU learner source](../lessons/cuda-043_gpu.cu)
- [GPU reference](../references/cuda-043_gpu.cu)

Read the [laboratory rules](../../STUDY-GUIDE.md#optional-native-cuda-laboratories) before compiling.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Divide 300 microseconds of setup by 15 microseconds saved per replay.

**Trap to avoid:** Comparing one replay at 5 microseconds with one ordinary iteration at 20 ignores the setup.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Update input contents in place for replay and rebuild the graph when the shape exceeds capacity.

**Trap to avoid:** Writing a larger input into the captured buffer overruns the allocation the nodes reference.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute break-even if setup is 600 microseconds and savings 10 per replay.

**Trap to avoid:** Halving the earlier answer because savings doubled ignores that setup doubled too.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A captured graph references a destroyed temporary buffer. Diagnose it.

**Trap to avoid:** Reallocating a new buffer at the same size does not update the address held by the graph.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What if the pipeline runs only once?

**Trap to avoid:** Capturing anyway because graphs are faster per replay adds pure overhead.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer the idea to model inference.

**Trap to avoid:** Capturing a model with data-dependent control flow freezes one path for all inputs.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A graph automatically fuses kernels or accepts arbitrary dynamic control flow without further design.** A graph replays the nodes you captured or defined, kernel by kernel; it does not merge them into one kernel. Its structure is fixed at instantiation, so data-dependent control flow or a shape beyond the allocation needs a supported update or a rebuild, as worked example 2 explains.

## Self-check, retrieval and transfer

1. Where is break-even in worked example 1?
2. What must stay valid across graph replays?
3. Why can a graph lose for a pipeline that runs once?

Short answers are in the [separate explanations](../solutions/cuda-043_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Graphs](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cuda-graphs.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-043: CUDA Graphs for repeated workflows.
Read courses/cuda/cpp/guides/cuda-043.md and courses/cuda/cpp/lessons/cuda-043.md.
Direct prerequisites: `cuda-020`, `cuda-031`, `cuda-039`, `cuda-041`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-043_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-043_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
