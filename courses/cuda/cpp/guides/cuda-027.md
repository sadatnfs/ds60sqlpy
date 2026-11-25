# cuda-027: Race reasoning, masks and warp cooperation

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-017`, `cuda-020`, `cuda-026`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement a warp shuffle reduction that is correct for every tail size and state its participation invariant.

**Scope:** Warp participation, active masks, collective operations, shuffle exchanges and explicit synchronization.

**Evidence to produce:** Correct results across all tail sizes and a written participation invariant.

## Purpose, vocabulary and mental model

Warp collectives require agreement about participating lanes. A mask names lanes expected to take part in a synchronized intrinsic, and source lanes used by a shuffle must actually participate. Independent thread scheduling means a convenient source ordering is not a general synchronization guarantee. Partial warps and divergent predicates need explicit reasoning. One safe educational reduction pattern has all lanes in a full warp participate, assigns zero to invalid data lanes, and then uses a full mask. A genuinely partial group needs a suitable mask and algorithm, not the same mask pasted everywhere.

### Key terms

- **Lane:** A thread's position, from 0 to 31, within its warp.
- **Participation mask:** A 32-bit value naming the lanes that must take part in a synchronized warp intrinsic.
- **Warp shuffle:** An intrinsic such as `__shfl_down_sync` that reads a register value from another lane of the same warp.
- **Independent thread scheduling:** The execution model, from Volta onward, in which lanes of a warp can progress separately, so implicit warp synchrony is not guaranteed.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-027_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-027_cpu.py
```

## CUDA C++ kernel listing

This reduction keeps the chapter's participation invariant: one full warp executes every shuffle with the full mask, and lanes without data contribute 0. With values 1 through 8 in lanes 0-7, lane 0 ends with 36.

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

**Why:** Values 1 through 8 sum to 36 and zeros add nothing, so the full-warp reduction is correct.

```python
mask = sum(1 << lane for lane in (0, 2, 5))
assert mask == 37 and mask.bit_count() == 3
contributions = list(range(1, 9)) + [0] * 24
assert sum(contributions) == 36
print({"ballot_mask": mask, "count": mask.bit_count(), "sum": sum(contributions)})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'ballot_mask': 37, 'count': 3, 'sum': 36}
```

**Check:** The reference asserts the 32-entry contributions sum to 36.

## Worked example 2: change a meaningful condition

A ballot for predicates true at lanes 0,2 and 5 has bit mask 37: binary positions contribute \(1+4+32\). Population count is three. Reading a shuffled value from lane seven is not justified if lane seven is outside the participating group.

**Why:** Bits 1, 4 and 32 add to 37, and three bits are set.

**Check:** The reference asserts mask == 37 and mask.bit_count() == 3.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Keep all 32 lanes in the collective and let the 24 unselected lanes contribute zero to the sum.

**Trap to avoid:** Launching only eight threads and calling a full-mask shuffle names 24 lanes that never execute it.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Set bit lane for lanes 0, 2 and 5 and count set bits.

**Trap to avoid:** Shuffling from lane 7 assumes it participates, but it is outside the predicate set.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Construct a ballot mask for lanes 1,3 and 4.

**Trap to avoid:** Writing the lane numbers as decimal digits 1 + 3 + 4 = 8 confuses indices with bit weights.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A shuffle uses a full mask inside a branch reached by half the warp. Diagnose it.

**Trap to avoid:** Adding __syncwarp before the shuffle in the branch still names absent lanes.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What happens for no selected values in a full participating warp?

**Trap to avoid:** Skipping the collective when no value is selected makes participation depend on data.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Transfer warp cooperation to segmented data.

**Trap to avoid:** Using the full-warp sum for each segment mixes values from neighboring segments.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A full bit mask is automatically correct for a collective executed by only some lanes.** The mask must name exactly the lanes that reach the collective. If a branch admits only half the warp, a full mask promises 16 lanes that never arrive, which is undefined behavior. Worked example 1 avoids this by letting all 32 lanes execute the collective while unselected lanes contribute zero.

## Self-check, retrieval and transfer

1. What ballot mask do predicates true at lanes 0 and 3 produce?
2. Why may a shuffle not read from lane seven in worked example 2?
3. Why is source order not a synchronization guarantee within a warp?

Short answers are in the [separate explanations](../solutions/cuda-027_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
