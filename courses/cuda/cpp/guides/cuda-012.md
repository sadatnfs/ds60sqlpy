# cuda-012: The first bounded kernel and the truth about completion

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-008`, `cuda-010`, `cuda-011`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain the first bounded kernel and the truth about completion using the concrete cases below. Produce host validates the returned values and reports both launch and completion status.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

The `__global__` qualifier declares a kernel callable through CUDA launch syntax. In `fill<<<blocks, threads>>>(out,n)`, the angle-bracket configuration chooses a grid of blocks and threads per block; parentheses carry ordinary function arguments. Each thread reads its own indices to choose work. A launch normally submits work asynchronously. Checking cudaGetLastError after submission detects launch problems, while a checked synchronization or dependent copy exposes execution failures. Only after the dependency is complete should the host validate returned values. Device printf is a debugging tool with ordering and buffering limitations, not a replacement for checking the output buffer.

## How to run and study this lesson

Open this chapter in `/classroom` and use its saved reading worksheet. The primary
reading pad does not execute CUDA. The two examples, six tasks and separate
explanations are usable offline on macOS, Linux and Windows through WSL 2 with
the ordinary classroom. An AMD, Intel or Apple GPU does not make this CUDA C++
source executable through Docker.

For the bounded CPU calculation, select **CPU model (Python)** in this lesson.
That variant keeps its own source and result history under the same chapter. Its
answer-free starter supplies literal fixtures and the task contract; implement
the model and assertions before replacing its deliberate incomplete-work error.
The separate [CPU reference](../references/cuda-012_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-012_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

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

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

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

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Start with the literal input and intermediate quantities in worked example 1.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Identify exactly which condition changes in worked example 2.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 3

Identify the configuration and arguments in fill<<<2,32>>>(out,50).

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

The process exits immediately after submission. What evidence is missing?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

What should count zero do?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Write a useful success message.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **returning from the launch expression means the kernel finished. .**

For the concrete failure exercise, the process exits immediately after submission. What evidence is missing?
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-012_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

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
