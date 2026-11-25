# cuda-026: Compute Sanitizer as evidence, with its limits

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-017`, `cuda-025`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Run Compute Sanitizer on a broken fixture, confirm the intended diagnostic and verify that the repair passes numerical tests.

**Scope:** Distinguish memory-access, shared-memory hazard, initialization and synchronization checks.

**Evidence to produce:** The broken fixture produces the intended diagnostic, the repair passes that check and numerical tests still pass.

## Purpose, vocabulary and mental model

Compute Sanitizer provides several checks with different scopes. Memcheck investigates invalid and misaligned memory accesses; racecheck investigates shared-memory hazards; initcheck investigates uninitialized global-memory reads; synccheck investigates invalid synchronization use. Their observations complement mathematical tests. Instrumentation can be expensive and can change timing, so sanitizer runs are not performance samples. An automated command should select a nonzero error-exitcode, because a tool diagnostic must make the check fail even if the application itself returns success. Never conclude that one clean run proves race freedom for every input or validates unsupported global protocols.

### Key terms

- **Memcheck:** The Compute Sanitizer tool that reports out-of-bounds and misaligned device memory accesses.
- **Racecheck:** The Compute Sanitizer tool that reports shared-memory data access hazards between threads.
- **Initcheck:** The Compute Sanitizer tool that reports reads of uninitialized device global memory.
- **Synccheck:** The Compute Sanitizer tool that reports invalid uses of synchronization primitives such as divergent barriers.
- **Error exit code:** A sanitizer option that makes the process return nonzero when a diagnostic occurs, so automation fails.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-026_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-026_cpu.py
```

## Worked example 1: trace the mechanism

For an array of four elements, valid indices are 0 through 3. A kernel that accesses index four has an off-by-one defect even if the returned allocation happens to contain readable bytes nearby. Memcheck is an appropriate additional diagnostic, while a CPU bounds model pinpoints the invalid logical access without a GPU.

**Why:** Index 4 is outside the array whether or not nearby bytes happen to be readable.

```python
n = 4
indices = list(range(5))
invalid = [i for i in indices if not 0 <= i < n]
assert invalid == [4]
checker = {
    "out_of_bounds": "memcheck",
    "shared_hazard": "racecheck",
    "uninitialized": "initcheck",
    "invalid_barrier": "synccheck",
}
print({"CPU_bounds_audit": invalid, "tool_selection": checker})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'CPU_bounds_audit': [4], 'tool_selection': {'out_of_bounds': 'memcheck', 'shared_hazard': 'racecheck', 'uninitialized': 'initcheck', 'invalid_barrier': 'synccheck'}}
```

**Check:** The reference asserts invalid == [4]; memcheck should report the access at index 4 on a GPU.

## Worked example 2: change a meaningful condition

A consumer reads shared tile\([2]\) before its producer writes. Racecheck can add evidence about that hazard. Replacing the missing barrier with a host sleep does not establish an ordering relationship between those threads. Repair the dependency and still validate returned numerical values.

**Why:** Only a barrier orders the store to tile[2] before the load by another thread.

**Check:** Run racecheck after the fix and also compare outputs to the CPU reference.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Audit indices 0 through 4 against n = 4 on the CPU and run memcheck on the GPU build.

**Trap to avoid:** Treating a run that did not crash as proof of safety ignores that the slack after the allocation absorbed the bad read.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Restore the barrier between producer and consumer and use racecheck as supporting evidence.

**Trap to avoid:** A host sleep happens outside the kernel and creates no ordering between device threads.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Choose a checker for an uninitialized global output read.

**Trap to avoid:** Memcheck alone accepts reads inside a valid allocation even if they were never written.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why should the command set --error-exitcode 99?

**Trap to avoid:** Searching logs by hand for error text misses reports when log formats change.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Does a passing check at \(\mathrm{n}=32\) establish \(\mathrm{n}=33\) safety?

**Trap to avoid:** Assuming a clean full-warp run covers every size skips exactly the guards most likely to be wrong.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design an acceptance sequence after a shared-memory repair.

**Trap to avoid:** Benchmarking under the sanitizer reports instrumented timings that do not reflect the real kernel.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A sanitizer pass proves speed, all global ordering, or correctness for every input.** A sanitizer reports only problems that occurred in the inputs you ran, and it changes timing, so it says nothing about speed. It also checks access and hazard rules, not whether the arithmetic is correct. Worked example 1 pairs memcheck with a CPU bounds test because each covers what the other misses; worked example 2 still validates values after the race is repaired.

## Self-check, retrieval and transfer

1. Which checker targets shared-memory hazards?
2. Why are sanitizer runs not performance evidence?
3. Why is a host sleep not a repair for a missing barrier?

Short answers are in the [separate explanations](../solutions/cuda-026_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [Compute Sanitizer](https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-026: Compute Sanitizer as evidence, with its limits.
Read courses/cuda/cpp/guides/cuda-026.md and courses/cuda/cpp/lessons/cuda-026.md.
Direct prerequisites: `cuda-017`, `cuda-025`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-026_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-026_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
