# cuda-012: The first bounded kernel and the truth about completion

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-008`, `cuda-010`, `cuda-011`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Launch a bounded kernel, check launch and completion status separately and validate returned values on the host.

Work through *The first bounded kernel and the truth about completion* with the concrete cases below. Finish with this evidence:
host validates the returned values and reports both launch and completion status. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

The `__global__` qualifier declares a kernel callable through CUDA launch syntax. In `fill<<<blocks, threads>>>(out,n)`, the angle-bracket configuration chooses a grid of blocks and threads per block; parentheses carry ordinary function arguments. Each thread reads its own indices to choose work. A launch normally submits work asynchronously. Checking cudaGetLastError after submission detects launch problems, while a checked synchronization or dependent copy exposes execution failures. Only after the dependency is complete should the host validate returned values. Device printf is a debugging tool with ordering and buffering limitations, not a replacement for checking the output buffer.

### Key terms

- **Kernel:** A `__global__` function that the host launches to run across many device threads.
- **Execution configuration:** The `<<<blocks, threads>>>` launch parameters that set the grid size and the threads per block.
- **Asynchronous launch:** Kernel submission that returns control to the host before the device finishes the work.
- **Completion check:** A checked synchronization, such as `cudaDeviceSynchronize`, that waits for device work and reports errors raised during execution.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-012_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-012_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

The kernel below is an excerpt from the chapter's complete [GPU reference](../references/cuda-012_gpu.cu). The full program adds device discovery, checked allocation and launch, completion checks and host validation. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

```cpp
__global__ void affine_indices(int *out, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    out[i] = 2 * static_cast<int>(i) + 1;
}
```

## Worked example 1: trace the mechanism

Let one kernel write its global index into a five-element output using eight launched threads. Threads 0 through 4 write \([0,1,2,3,4]\); threads 5 through 7 perform no write because the bounds predicate is false. The host compares every returned value with its expected index.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
n, launched = 5, 8
out = [None] * n
for i in range(launched):
    if i < n:
        out[i] = 2 * i + 1
assert out == [1, 3, 5, 7, 9]
print({"CPU_ownership_trace": out, "GPU_execution": "not performed"})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'CPU_ownership_trace': [1, 3, 5, 7, 9], 'GPU_execution': 'not performed'}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Change the expression to twice the index plus one. Expected output is \([1,3,5,7,9]\). Keeping the same ownership mapping separates the arithmetic change from scheduling. A launch status of success without a completion check does not establish these values arrived in host memory.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Optional CUDA C++ laboratory

A complete [GPU reference](../references/cuda-012_gpu.cu) and separate
[GPU learner source](../lessons/cuda-012_gpu.cu) accompany this chapter.
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

Identify the configuration and arguments in fill<<<2,32>>>(out,50).

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

The process exits immediately after submission. What evidence is missing?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should count zero do?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Write a useful success message.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **returning from the launch expression means the kernel finished. .**

For the concrete failure exercise, the process exits immediately after submission. What evidence is missing?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-012_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA C++ introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-cpp.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-012: The first bounded kernel and the truth about completion.
Read courses/cuda/cpp/guides/cuda-012.md and courses/cuda/cpp/lessons/cuda-012.md.
Direct prerequisites: `cuda-008`, `cuda-010`, `cuda-011`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-012_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-012_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
