# cuda-034: Coalescing, layouts and useful bandwidth

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`, `cuda-016`, `cuda-033`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Draw per-lane address diagrams and compare useful bandwidth for array-of-structures and structure-of-arrays layouts.

Work through *Coalescing, layouts and useful bandwidth* with the concrete cases below. Finish with this evidence:
address diagrams, correctness, and a bandwidth interpretation using the actual input and timing scope. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Coalescing concerns how neighboring lanes' memory requests combine into transactions. The source loop may look sequential while lane addresses are far apart. Write the address for each lane first. Structure-of-arrays often helps a kernel that reads one field from many records, while array-of-structures can suit consumers that need complete records. Alignment, transaction size, cache and architecture affect the exact cost. Count useful bytes separately from fetched bytes and include conversion cost if layout changes. A layout beneficial for one kernel can hurt the full pipeline if every boundary requires reshuffling.

### Key terms

- **Coalesced access:** A warp access pattern in which neighboring lanes touch neighboring addresses, so few memory transactions serve the whole warp.
- **Memory sector:** A 32-byte unit of global memory access; touching any byte of a sector moves the whole sector.
- **Structure of arrays (SoA):** A layout that stores each field in its own contiguous array, so lanes reading one field read adjacent values.
- **Array of structures (AoS):** A layout that stores whole records contiguously, so lanes reading one field read strided addresses.
- **Useful bytes:** The bytes the algorithm actually needs, compared with the bytes moved to estimate wasted bandwidth.

## Mathematical contract

\[
a_{\ell}=a_0+\ell s b
\]

Lane ell requests an address at stride s elements, with b bytes per element. Address span is a model input, not a measured transaction count.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-034_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-034_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Thirty-two lanes read float32 elements at offsets 0 through 31. Their useful data spans 128 bytes. With stride eight elements, offsets run from 0 through 248 and span 996 bytes including gaps. Span is not a transaction count, but it reveals why the access pattern deserves measurement.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
contiguous = [lane * 4 for lane in range(32)]
strided = [lane * 8 * 4 for lane in range(32)]
assert contiguous[-1] + 4 == 128
assert strided[-1] + 4 == 996
print({"contiguous_span_bytes": 128, "strided_span_bytes": 996})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'contiguous_span_bytes': 128, 'strided_span_bytes': 996}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

For records containing x,y,z,w as four floats, reading x for 32 particles advances 16 bytes per lane. A separate x array advances four bytes per lane. If the next stage needs all four fields, compare complete pipeline costs before committing to a representation change.

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

List the first four byte addresses for float32 stride three from base zero.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A report calls the address span 'bytes transferred'. Correct it.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What does a single active lane tell you about warp coalescing?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Choose a layout for a many-step x-only update pipeline.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **sequential-looking source code guarantees coalesced device accesses.**

For the concrete failure exercise, a report calls the address span 'bytes transferred'. Correct it.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-034_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-034: Coalescing, layouts and useful bandwidth.
Read courses/cuda/cpp/guides/cuda-034.md and courses/cuda/cpp/lessons/cuda-034.md.
Direct prerequisites: `cuda-005`, `cuda-016`, `cuda-033`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-034_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-034_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
