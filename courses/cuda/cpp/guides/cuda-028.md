# cuda-028: Memory ordering and atomic scope

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-022`, `cuda-027`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Memory ordering and atomic scope* with the concrete cases below. Finish with this evidence:
the learner can explain what each synchronization operation establishes and what it does not. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Atomicity means one operation is indivisible with respect to competing operations at its scope. Ordering specifies how memory operations relate; visibility concerns which observer can see writes. Publishing a payload through a flag requires a protocol that orders the payload write before a release operation and the consumer's payload read after an appropriate acquire. Both sides must use compatible synchronization and scope. A relaxed atomic counter can correctly count events without publishing unrelated payloads. A fence orders operations but does not force another block to run, so it cannot repair a residency deadlock in an improvised global barrier.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-028_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-028_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A producer writes payload 42, then releases a ready flag. A consumer acquires that publication before reading the payload. The happens-before chain connects payload write to payload read. This is a conceptual protocol; an actual CUDA implementation must use supported atomic types, scope and participating execution conditions.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
events = ["payload_write", "release_flag", "acquire_flag", "payload_read"]
positions = {name: i for i, name in enumerate(events)}
assert (
    positions["payload_write"]
    < positions["release_flag"]
    < positions["acquire_flag"]
    < positions["payload_read"]
)
print({"conceptual_happens_before": events, "GPU_memory_model_test": False})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'conceptual_happens_before': ['payload_write', 'release_flag', 'acquire_flag', 'payload_read'], 'GPU_memory_model_test': False}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Two workers atomically increment a count, giving count two, while writing separate payloads without publication ordering. The count's arithmetic can be correct even though the payload protocol is incomplete. 'Atomic' describes the increment, not every access in the surrounding program.

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

Name the four events in the publication chain.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why does a memory fence not make a sleeping producer execute?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

When might block-scope synchronization be insufficient?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Apply the reasoning to a ring buffer slot.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **incrementing an atomic flag automatically publishes all other writes to every possible observer.**

For the concrete failure exercise, why does a memory fence not make a sleeping producer execute?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-028_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-028: Memory ordering and atomic scope.
Read courses/cuda/cpp/guides/cuda-028.md and courses/cuda/cpp/lessons/cuda-028.md.
Direct prerequisites: `cuda-022`, `cuda-027`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-028_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-028_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
