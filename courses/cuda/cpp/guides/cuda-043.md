# cuda-043: CUDA Graphs for repeated workflows

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-020`, `cuda-031`, `cuda-039`, `cuda-041`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Capture and replay a CUDA Graph correctly and compare its submission cost against ordinary stream launches.

Work through *CUDA Graphs for repeated workflows* with the concrete cases below. Finish with this evidence:
correct replay, safe resource lifetimes, a scoped comparison and explicit unsupported changes. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

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

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-043_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-043_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

The kernel below is an excerpt from the chapter's complete [GPU reference](../references/cuda-043_gpu.cu). The full program adds device discovery, checked allocation and launch, completion checks and host validation. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

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

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
setup_us, ordinary_us, replay_us = 300, 20, 5
break_even = setup_us / (ordinary_us - replay_us)
assert break_even == 20
assert setup_us + 21 * replay_us < 21 * ordinary_us
print({"synthetic_break_even_replays": break_even})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'synthetic_break_even_replays': 20.0}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A graph contains fill, affine transform and download nodes with dependencies. Replay uses the same valid storage but new input contents. Changing the input shape beyond allocation capacity is not just a new value; rebuild or perform a supported update after validating all node contracts.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Optional CUDA C++ laboratory

A complete [GPU reference](../references/cuda-043_gpu.cu) and separate
[GPU learner source](../lessons/cuda-043_gpu.cu) accompany this chapter.
They are standalone files with bounded fixtures, checked runtime calls and host
validation. The learner source intentionally reports incomplete implementation
until you add the chapter's algorithm and assertions. It must never return a
fake GPU success on a CPU machine. Follow the [manual GPU workflow](../README.md)
for exact compilation and execution paths. If the classroom offers the optional
CUDA C++ variant, its capability notice must confirm actual runtime readiness.

The reference contains an explicit no-device failure, launch and completion
checks, and returned-value validation. Source review and CPU reference checks do
not qualify this .cu file on your hardware. Preserve compilation, actual device
execution and sanitizer evidence separately. Exercise 4 is a reasoning diagnosis;
do not deliberately launch a hanging kernel or reset a shared GPU to reproduce it.

## Six progressive exercises

Exercises 1 and 2 are guided reconstructions of the worked examples; exercises
3-6 change an input, diagnose a defect, test a boundary and transfer the idea.
For each one, keep the calculation, output, diagram or failure policy you
produce so another reader can compare it with the worked cases. If the hint is
not enough, reread the mechanism paragraph and the bounded CPU assertion.

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute break-even if setup is 600 microseconds and savings 10 per replay.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A captured graph references a destroyed temporary buffer. Diagnose it.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What if the pipeline runs only once?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer the idea to model inference.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a graph automatically fuses kernels or accepts arbitrary dynamic control flow without further design. .**

For the concrete failure exercise, a captured graph references a destroyed temporary buffer. Diagnose it.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-043_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
