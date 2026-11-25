# cuda-022: Histograms, atomics and contention

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-017`, `cuda-020`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Compute exact histogram counts with atomics and explain two timing regimes through contention.

**Scope:** Conflicting writes, atomic updates, collision probability and block privatization.

**Evidence to produce:** Exact counts and a contention-based explanation of two timing regimes.

## Purpose, vocabulary and mental model

A histogram counts values into bins. Several threads can increment the same bin, so ordinary read-modify-write operations can lose updates. An atomic addition makes that individual update indivisible at its supported scope. It does not make an entire multi-step algorithm atomic or publish unrelated data automatically. A block-private histogram can reduce global contention by combining local counts before a global merge. It also costs shared memory and initialization work. Distribution matters: uniformly spread samples and one hot bin exercise very different contention patterns even with identical input size.

### Key terms

- **Atomic operation:** A read-modify-write update, such as `atomicAdd`, that is indivisible with respect to competing updates at its scope.
- **Contention:** Many threads updating the same location, which serializes their atomic operations.
- **Privatization:** Giving each block its own shared-memory histogram and merging the partial counts globally afterward.
- **Lost update:** A wrong count that occurs when two threads read the same old value and both write back an increment.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-022_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-022_cpu.py
```

## CUDA C++ kernel listing

An excerpt from the chapter's complete [GPU reference](../references/cuda-022_gpu.cu); the reading pad does not compile it.

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

**Why:** atomicAdd makes each read-modify-write indivisible, so two threads hitting bin 0 at once produce 2 instead of both writing 1.

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

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'partials': [[1, 0, 2], [1, 1, 1]], 'merged': [2, 1, 3]}
```

**Check:** The reference asserts the merged bins equal [2, 1, 3] and sum to six, the input length, which is the conservation check to keep on a GPU.

## Worked example 2: change a meaningful condition

Split the values into two groups of three. Their private histograms are \([1,0,2]\) and \([1,1,1]\); merging gives \([2,1,3]\). This explains the algorithm without promising the private version is faster. For small inputs, initialization and merging may cost more than direct atomic updates.

**Why:** Addition is associative and commutative on integer counts, so merging private bins yields exactly the global histogram.

**Check:** The reference prints partials [[1, 0, 2], [1, 1, 1]] and merged [2, 1, 3]; time each variant on a GPU before stating which wins.

## Optional CUDA C++ laboratory

- [GPU learner source](../lessons/cuda-022_gpu.cu)
- [GPU reference](../references/cuda-022_gpu.cu)

Read the [laboratory rules](../../STUDY-GUIDE.md#optional-native-cuda-laboratories) before compiling.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Count [0, 2, 2, 1, 2, 0] into three bins with an atomic increment per element, giving [2, 1, 3].

**Trap to avoid:** A plain bins[v]++ looks atomic in source but compiles to separate load, add and store, and two workers reading the old zero both store one.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Give each of two groups a private histogram, [1, 0, 2] for the first three values and [1, 1, 1] for the rest, then add them binwise.

**Trap to avoid:** Claiming the privatized version must be faster ignores the cost of zeroing and merging private copies, which can dominate for six elements.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Build a four-bin histogram of \([3,3,0,1,3]\).

**Trap to avoid:** Allocating max(values) bins from the observed data would still be four here but drops bins silently whenever the top category is absent.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

The input contains category -1. Define a safe contract.

**Trap to avoid:** Casting the value to unsigned makes -1 a huge index that skips the lower check yet still writes far outside the allocation.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What fixture maximizes simple same-bin contention?

**Trap to avoid:** Using random data alone measures an average case and never exposes the worst-case serialization a skewed real dataset can trigger.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer histograms to quantized floating measurements.

**Trap to avoid:** Computing int((x - lo) / width) without a policy sends the maximum value to a bin one past the end.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **An atomic operation is either always fast or always slow, independent of access pattern.** Atomic cost depends on contention. Values spread over many bins rarely collide, while a skewed input that sends most values to one bin serializes updates. Worked example 2 shows block privatization, which reduces global contention but adds initialization and merging, so measure both input shapes before choosing.

## Self-check, retrieval and transfer

1. Why must the bin counts in worked example 1 sum to six?
2. What does an atomic add guarantee and what does it not?
3. When might a private histogram be slower?

Short answers are in the [separate explanations](../solutions/cuda-022_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
