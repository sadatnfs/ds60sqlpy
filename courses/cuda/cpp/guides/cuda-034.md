# cuda-034: Coalescing, layouts and useful bandwidth

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-005`, `cuda-016`, `cuda-033`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Draw per-lane address diagrams and compare useful bandwidth for array-of-structures and structure-of-arrays layouts.

**Scope:** Neighboring lane addresses, memory transactions, alignment, strides and useful bytes versus transferred bytes.

**Evidence to produce:** Address diagrams, correctness, and a bandwidth interpretation using the actual input and timing scope.

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

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-034_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-034_cpu.py
```

## Worked example 1: trace the mechanism

Thirty-two lanes read float32 elements at offsets 0 through 31. Their useful data spans 128 bytes. With stride eight elements, offsets run from 0 through 248 and span 996 bytes including gaps. Span is not a transaction count, but it reveals why the access pattern deserves measurement.

**Why:** Contiguous offsets end at 124 plus 4, spanning 128 bytes; strided ones end at 992 plus 4, spanning 996.

```python
contiguous = [lane * 4 for lane in range(32)]
strided = [lane * 8 * 4 for lane in range(32)]
assert contiguous[-1] + 4 == 128
assert strided[-1] + 4 == 996
print({"contiguous_span_bytes": 128, "strided_span_bytes": 996})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'contiguous_span_bytes': 128, 'strided_span_bytes': 996}
```

**Check:** The reference asserts contiguous[-1] + 4 == 128 and strided[-1] + 4 == 996.

## Worked example 2: change a meaningful condition

For records containing x,y,z,w as four floats, reading x for 32 particles advances 16 bytes per lane. A separate x array advances four bytes per lane. If the next stage needs all four fields, compare complete pipeline costs before committing to a representation change.

**Why:** Reading x alone from records drags y, z and w along, while the separate array uses each byte.

**Check:** Measure the whole pipeline in both layouts with identical outputs.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Multiply each lane by 4 bytes for contiguous reads and by 32 bytes for stride eight.

**Trap to avoid:** Treating the 996-byte span as an exact transaction count ignores caching and segment rules.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Compare a 16-byte step per lane in the record layout with a 4-byte step in a separate x array.

**Trap to avoid:** Converting to separate arrays without checking whether later stages need all four fields may cost more overall.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

List the first four byte addresses for float32 stride three from base zero.

**Trap to avoid:** Using stride 3 as a byte offset gives 0, 3, 6, 9 and misaligned reads.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A report calls the address span 'bytes transferred'. Correct it.

**Trap to avoid:** Reporting span as bytes transferred presents a model as a measurement.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What does a single active lane tell you about warp coalescing?

**Trap to avoid:** Profiling only one lane can call a pattern coalesced when it is not.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Choose a layout for a many-step x-only update pipeline.

**Trap to avoid:** Comparing only the inner step ignores the conversion and final consumers.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Sequential-looking source code guarantees coalesced device accesses.** Coalescing depends on the addresses neighboring lanes touch at the same instruction, not on how the source loop reads. A loop over records that reads one field advances 16 bytes per lane in worked example 2. Write each lane's address first, then judge the layout.

## Self-check, retrieval and transfer

1. What span do 32 float32 lanes cover at stride one?
2. Why is address span not the same as bytes transferred?
3. When can array-of-structures be the better layout?

Short answers are in the [separate explanations](../solutions/cuda-034_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
