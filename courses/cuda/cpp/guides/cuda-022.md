# cuda-022: Histograms, atomics and contention

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-017`, `cuda-020`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Compute exact histogram counts with atomics and explain two timing regimes through contention.

Work through *Histograms, atomics and contention* with the concrete cases below. Finish with this evidence:
exact counts and a contention-based explanation of two timing regimes. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A histogram counts values into bins. Several threads can increment the same bin, so ordinary read-modify-write operations can lose updates. An atomic addition makes that individual update indivisible at its supported scope. It does not make an entire multi-step algorithm atomic or publish unrelated data automatically. A block-private histogram can reduce global contention by combining local counts before a global merge. It also costs shared memory and initialization work. Distribution matters: uniformly spread samples and one hot bin exercise very different contention patterns even with identical input size.

### Key terms

- **Atomic operation:** A read-modify-write update, such as `atomicAdd`, that is indivisible with respect to competing updates at its scope.
- **Contention:** Many threads updating the same location, which serializes their atomic operations.
- **Privatization:** Giving each block its own shared-memory histogram and merging the partial counts globally afterward.
- **Lost update:** A wrong count that occurs when two threads read the same old value and both write back an increment.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-022_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-022_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

The kernel below is an excerpt from the chapter's complete [GPU reference](../references/cuda-022_gpu.cu). The full program adds device discovery, checked allocation and launch, completion checks and host validation. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

```cpp
__global__ void count_bins(const int *input, unsigned *bins, std::size_t n) {
  const std::size_t i =
      static_cast<std::size_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  if (i < n)
    atomicAdd(&bins[input[i]],
              1U); // Host validates category range before upload.
}
```

## Worked example 1: trace the mechanism

Values \([0,2,2,1,2,0]\) with three bins produce \([2,1,3]\). The sum of bins is six. Two workers both reading an old count of zero and then each writing one lose a count; correct atomic accumulation produces two.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
values = [0, 2, 2, 1, 2, 0]


def histogram(items):
    bins = [0, 0, 0]
    for value in items:
        assert 0 <= value < len(bins)
        bins[value] += 1
    return bins


parts = [histogram(values[:3]), histogram(values[3:])]
merged = [sum(pair) for pair in zip(*parts)]
assert merged == [2, 1, 3] and sum(merged) == len(values)
print({"partials": parts, "merged": merged})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'partials': [[1, 0, 2], [1, 1, 1]], 'merged': [2, 1, 3]}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Split the values into two groups of three. Their private histograms are \([1,0,2]\) and \([1,1,1]\); merging gives \([2,1,3]\). This explains the algorithm without promising the private version is faster. For small inputs, initialization and merging may cost more than direct atomic updates.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Optional CUDA C++ laboratory

A complete [GPU reference](../references/cuda-022_gpu.cu) and separate
[GPU learner source](../lessons/cuda-022_gpu.cu) accompany this chapter.
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

Build a four-bin histogram of \([3,3,0,1,3]\).

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

The input contains category -1. Define a safe contract.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What fixture maximizes simple same-bin contention?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer histograms to quantized floating measurements.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **an atomic operation is either always fast or always slow, independent of access pattern.**

For the concrete failure exercise, the input contains category -1. Define a safe contract.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-022_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-022: Histograms, atomics and contention.
Read courses/cuda/cpp/guides/cuda-022.md and courses/cuda/cpp/lessons/cuda-022.md.
Direct prerequisites: `cuda-017`, `cuda-020`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-022_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-022_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
