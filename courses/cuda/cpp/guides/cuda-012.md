# cuda-012: The first bounded kernel and the truth about completion

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-008`, `cuda-010`, `cuda-011`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Launch a bounded kernel, check launch and completion status separately and validate returned values on the host.

**Scope:** `__global__`, `__device__`, `__host__`, launch configuration and asynchronous launch.

**Evidence to produce:** Host validates the returned values and reports both launch and completion status.

## Purpose, vocabulary and mental model

The `__global__` qualifier declares a kernel callable through CUDA launch syntax. In `fill<<<blocks, threads>>>(out,n)`, the angle-bracket configuration chooses a grid of blocks and threads per block; parentheses carry ordinary function arguments. Each thread reads its own indices to choose work. A launch normally submits work asynchronously. Checking cudaGetLastError after submission detects launch problems, while a checked synchronization or dependent copy exposes execution failures. Only after the dependency is complete should the host validate returned values. Device printf is a debugging tool with ordering and buffering limitations, not a replacement for checking the output buffer.

### Key terms

- **Kernel:** A `__global__` function that the host launches to run across many device threads.
- **Execution configuration:** The `<<<blocks, threads>>>` launch parameters that set the grid size and the threads per block.
- **Asynchronous launch:** Kernel submission that returns control to the host before the device finishes the work.
- **Completion check:** A checked synchronization, such as `cudaDeviceSynchronize`, that waits for device work and reports errors raised during execution.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-012_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-012_cpu.py
```

## CUDA C++ kernel listing

An excerpt from the chapter's complete [GPU reference](../references/cuda-012_gpu.cu); the reading pad does not compile it.

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

**Why:** The predicate rejects threads 5 to 7, so each valid index is written once and nothing beyond.

```python
n, launched = 5, 8
out = [None] * n
for i in range(launched):
    if i < n:
        out[i] = 2 * i + 1
assert out == [1, 3, 5, 7, 9]
print({"CPU_ownership_trace": out, "GPU_execution": "not performed"})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'CPU_ownership_trace': [1, 3, 5, 7, 9], 'GPU_execution': 'not performed'}
```

**Check:** Compare the returned [0, 1, 2, 3, 4] element by element after a checked synchronization.

## Worked example 2: change a meaningful condition

Change the expression to twice the index plus one. Expected output is \([1,3,5,7,9]\). Keeping the same ownership mapping separates the arithmetic change from scheduling. A launch status of success without a completion check does not establish these values arrived in host memory.

**Why:** Ownership is unchanged, so any wrong value isolates an arithmetic error rather than scheduling.

**Check:** The reference asserts out == [1, 3, 5, 7, 9] and prints GPU_execution not performed.

## Optional CUDA C++ laboratory

- [GPU learner source](../lessons/cuda-012_gpu.cu)
- [GPU reference](../references/cuda-012_gpu.cu)

Read the [laboratory rules](../../STUDY-GUIDE.md#optional-native-cuda-laboratories) before compiling.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Launch eight threads for five outputs and guard each write with i < 5.

**Trap to avoid:** Omitting the guard lets threads 5 to 7 write past the five-element allocation.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Keep the same index mapping and change only the stored expression to 2 * i + 1.

**Trap to avoid:** Trusting the launch status as proof of results ignores that launches return before execution finishes.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Identify the configuration and arguments in fill<<<2,32>>>(out,50).

**Trap to avoid:** Reading <<<2, 32>>> as 32 blocks of 2 threads reverses the configuration order.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

The process exits immediately after submission. What evidence is missing?

**Trap to avoid:** Checking only cudaGetLastError after launch catches configuration errors but not execution faults.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should count zero do?

**Trap to avoid:** Launching ceil(0 / 32) = 0 blocks yields an invalid configuration error, not a quiet no-op.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Write a useful success message.

**Trap to avoid:** Printing 'GPU kernel is fast and correct' generalizes from five values and no timing.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Returning from the launch expression means the kernel finished.** Launches are asynchronous: the host regains control after submission. Only a synchronizing call, such as a checked `cudaDeviceSynchronize` or a blocking copy, proves the kernel completed and surfaces execution errors. Worked example 2 notes that a launch status alone does not establish the output values.

## Self-check, retrieval and transfer

1. In `fill<<<2,32>>>(out,50)`, how many threads launch and how many write?
2. Which call reports launch configuration errors and which reports execution errors?
3. Why keep the ownership mapping fixed when changing the formula in worked example 2?

Short answers are in the [separate explanations](../solutions/cuda-012_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
