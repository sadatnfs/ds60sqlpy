# cuda-027: Race reasoning, masks and warp cooperation

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-017`, `cuda-020`, `cuda-026`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Implement a warp shuffle reduction that is correct for every tail size and state its participation invariant.

Work through *Race reasoning, masks and warp cooperation* with the concrete cases below. Finish with this evidence:
correct results across all tail sizes and a written participation invariant. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Warp collectives require agreement about participating lanes. A mask names lanes expected to take part in a synchronized intrinsic, and source lanes used by a shuffle must actually participate. Independent thread scheduling means a convenient source ordering is not a general synchronization guarantee. Partial warps and divergent predicates need explicit reasoning. One safe educational reduction pattern has all lanes in a full warp participate, assigns zero to invalid data lanes, and then uses a full mask. A genuinely partial group needs a suitable mask and algorithm, not the same mask pasted everywhere.

### Key terms

- **Lane:** A thread's position, from 0 to 31, within its warp.
- **Participation mask:** A 32-bit value naming the lanes that must take part in a synchronized warp intrinsic.
- **Warp shuffle:** An intrinsic such as `__shfl_down_sync` that reads a register value from another lane of the same warp.
- **Independent thread scheduling:** The execution model, from Volta onward, in which lanes of a warp can progress separately, so implicit warp synchrony is not guaranteed.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-027_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-027_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## CUDA C++ kernel listing

This reduction keeps the chapter's participation invariant: one full warp executes every shuffle with the full mask, and lanes without data contribute 0. With values 1 through 8 in lanes 0-7, lane 0 ends with 36. Read it as CUDA C++ source; the classroom reading pad does not compile or run it.

```cpp
// Sum up to 32 values with exactly one full warp: warp_sum<<<1, 32>>>.
// Every lane executes every shuffle; lanes without data contribute 0.
__global__ void warp_sum(const int *values, int count, int *result) {
  const int lane = threadIdx.x;
  int v = lane < count ? values[lane] : 0;
  const unsigned full = 0xffffffffu; // all 32 lanes participate
  for (int offset = 16; offset > 0; offset /= 2)
    v += __shfl_down_sync(full, v, offset);
  if (lane == 0)
    *result = v; // lane 0 holds the warp total
}
```

## Worked example 1: trace the mechanism

Eight selected lanes among a full 32-thread warp contribute values 1 through 8; other lanes contribute zero. All 32 lanes execute the collective, giving sum 36. This is different from launching only eight threads and pretending the absent 24 lanes participate.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
mask = sum(1 << lane for lane in (0, 2, 5))
assert mask == 37 and mask.bit_count() == 3
contributions = list(range(1, 9)) + [0] * 24
assert sum(contributions) == 36
print({"ballot_mask": mask, "count": mask.bit_count(), "sum": sum(contributions)})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'ballot_mask': 37, 'count': 3, 'sum': 36}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A ballot for predicates true at lanes 0,2 and 5 has bit mask 37: binary positions contribute \(1+4+32\). Population count is three. Reading a shuffled value from lane seven is not justified if lane seven is outside the participating group.

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

Construct a ballot mask for lanes 1,3 and 4.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A shuffle uses a full mask inside a branch reached by half the warp. Diagnose it.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What happens for no selected values in a full participating warp?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer warp cooperation to segmented data.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a full bit mask is automatically correct for a collective executed by only some lanes.**

For the concrete failure exercise, a shuffle uses a full mask inside a branch reached by half the warp. Diagnose it.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-027_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-027: Race reasoning, masks and warp cooperation.
Read courses/cuda/cpp/guides/cuda-027.md and courses/cuda/cpp/lessons/cuda-027.md.
Direct prerequisites: `cuda-017`, `cuda-020`, `cuda-026`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-027_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-027_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
