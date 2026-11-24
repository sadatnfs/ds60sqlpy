# cuda-017: Shared memory and block synchronization

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-014`, `cuda-016`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Trace producer and consumer threads through each block barrier and verify correct tail behavior.

Work through *Shared memory and block synchronization* with the concrete cases below. Finish with this evidence:
correct boundary behavior and a synchronization explanation naming producer and consumer threads. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Shared memory lets threads in one block communicate through a common scratch array. Communication requires ordering: a consumer must not read a location until its producer has written it. `__syncthreads()` is a block barrier with memory-ordering effects for participating threads. Put bounds predicates around loads and stores while keeping the required barrier participation uniform. Invalid tail lanes can load a neutral value and still reach the barrier. A barrier does not coordinate ordinary independent blocks, and a memory fence does not force other threads to arrive at the same program point.

### Key terms

- **Block barrier:** A `__syncthreads()` call that every thread in the block must reach before any continues, which also orders shared-memory accesses.
- **Producer and consumer:** A thread that writes a shared value and a thread that later reads it, which need an ordering between them.
- **Neutral value:** An identity element, such as zero for addition, that invalid tail lanes load so they can still reach the barrier.
- **Divergent barrier:** A barrier reached by only some threads of a block, which is undefined behavior and can hang the kernel.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-017_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-017_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

The kernel applies this chapter's reversal pattern to block-sized tiles. Each block loads its tile into shared memory, every thread reaches one barrier, and only then does any thread read a value another thread wrote. Tail threads load 0 instead of returning, so barrier participation stays uniform; with four values one block returns [12, 9, 6, 3]. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

```cpp
constexpr int BLOCK = 256;

// Reverse each block-sized tile of in into out. Launch with BLOCK threads per
// block. Tail threads load a neutral value and still reach the barrier.
__global__ void reverse_tiles(const int *in, int *out, int n) {
  __shared__ int tile[BLOCK];
  const int base = blockIdx.x * BLOCK;
  const int t = threadIdx.x;
  const int valid = min(BLOCK, n - base); // elements owned by this block
  tile[t] = t < valid ? in[base + t] : 0;
  __syncthreads(); // every load is visible before any thread reads the tile
  if (t < valid)
    out[base + t] = tile[valid - 1 - t];
}
// Launch: reverse_tiles<<<(n + BLOCK - 1) / BLOCK, BLOCK>>>(in, out, n);
```

## Worked example 1: trace the mechanism

Four threads load \([3,6,9,12]\) into a shared tile, synchronize, then thread t reads tile[3-t]. The reversed output is \([12,9,6,3]\). Without the barrier, a consumer could read before another thread loads its value. An apparent success on one execution is not a synchronization proof.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
tile = [3, 6, 9, 12]
# A CPU phase boundary models the dependency, not GPU scheduling.
output = [tile[3 - lane] for lane in range(4)]
assert output == [12, 9, 6, 3]
partial = [3, 6, 9, 0]
assert sum(partial) == 18
print({"reversal": output, "neutralized_tail_sum": sum(partial)})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'reversal': [12, 9, 6, 3], 'neutralized_tail_sum': 18}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For a three-element tail in a four-thread block, lane three loads a neutral zero and still participates in the barrier. Only valid lanes store output. A conditional `if (i<n) { load; barrier; }` can violate the barrier contract when some block threads skip it.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

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

Draw the producer and consumer for reversed output index zero.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A conditional barrier hangs only on ragged input. What is the smallest repair?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why does a block barrier not make a global reduction complete?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a neighbor-average tile with a halo.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a memory fence and a barrier are interchangeable.**

For the concrete failure exercise, a conditional barrier hangs only on ragged input. What is the smallest repair?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-017_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-017: Shared memory and block synchronization.
Read courses/cuda/cpp/guides/cuda-017.md and courses/cuda/cpp/lessons/cuda-017.md.
Direct prerequisites: `cuda-014`, `cuda-016`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-017_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-017_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
