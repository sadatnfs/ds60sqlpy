# cuda-026: Compute Sanitizer as evidence, with its limits

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-017`, `cuda-025`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Run Compute Sanitizer on a broken fixture, confirm the intended diagnostic and verify that the repair passes numerical tests.

Work through *Compute Sanitizer as evidence, with its limits* with the concrete cases below. Finish with this evidence:
the broken fixture produces the intended diagnostic, the repair passes that check and numerical tests still pass. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Compute Sanitizer provides several checks with different scopes. Memcheck investigates invalid and misaligned memory accesses; racecheck investigates shared-memory hazards; initcheck investigates uninitialized global-memory reads; synccheck investigates invalid synchronization use. Their observations complement mathematical tests. Instrumentation can be expensive and can change timing, so sanitizer runs are not performance samples. An automated command should select a nonzero error-exitcode, because a tool diagnostic must make the check fail even if the application itself returns success. Never conclude that one clean run proves race freedom for every input or validates unsupported global protocols.

### Key terms

- **Memcheck:** The Compute Sanitizer tool that reports out-of-bounds and misaligned device memory accesses.
- **Racecheck:** The Compute Sanitizer tool that reports shared-memory data access hazards between threads.
- **Initcheck:** The Compute Sanitizer tool that reports reads of uninitialized device global memory.
- **Synccheck:** The Compute Sanitizer tool that reports invalid uses of synchronization primitives such as divergent barriers.
- **Error exit code:** A sanitizer option that makes the process return nonzero when a diagnostic occurs, so automation fails.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-026_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-026_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

For an array of four elements, valid indices are 0 through 3. A kernel that accesses index four has an off-by-one defect even if the returned allocation happens to contain readable bytes nearby. Memcheck is an appropriate additional diagnostic, while a CPU bounds model pinpoints the invalid logical access without a GPU.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

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

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'CPU_bounds_audit': [4], 'tool_selection': {'out_of_bounds': 'memcheck', 'shared_hazard': 'racecheck', 'uninitialized': 'initcheck', 'invalid_barrier': 'synccheck'}}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A consumer reads shared tile\([2]\) before its producer writes. Racecheck can add evidence about that hazard. Replacing the missing barrier with a host sleep does not establish an ordering relationship between those threads. Repair the dependency and still validate returned numerical values.

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

Choose a checker for an uninitialized global output read.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why should the command set --error-exitcode 99?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Does a passing check at \(\mathrm{n}=32\) establish \(\mathrm{n}=33\) safety?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design an acceptance sequence after a shared-memory repair.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a sanitizer pass proves speed, all global ordering, or correctness for every input. .**

For the concrete failure exercise, why should the command set --error-exitcode 99?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-026_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
