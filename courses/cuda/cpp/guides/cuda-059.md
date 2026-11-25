# cuda-059: PTX, SASS, JIT and inspecting generated code

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-011`, `cuda-033`, `cuda-036`, `cuda-056`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Inspect generated PTX and SASS to explain a selected instruction sequence and validate any change with existing tests.

**Scope:** Virtual versus hardware instruction sets, compiler resource reports, fat binaries, architecture targets, disassembly and JIT startup.

**Evidence to produce:** Explain a selected instruction sequence and validate any optimization with the existing tests.

## Purpose, vocabulary and mental model

PTX is a virtual instruction language, while SASS describes machine instructions for a particular GPU architecture. The driver or toolchain can translate PTX differently across targets and versions. A fat binary can contain native device images and PTX fallback according to a deliberate policy. JIT can introduce cold-start cost and compatibility constraints. Inspect compiler resource reports and generated code to test a hypothesis, such as unexpected local-memory traffic, before attempting inline assembly. Counting PTX instructions does not directly count executed hardware operations or predict runtime.

### Key terms

- **PTX:** The virtual instruction set that `nvcc` emits before architecture-specific assembly.
- **SASS:** The native machine instructions that a specific GPU architecture actually executes.
- **cuobjdump:** A tool that extracts embedded PTX and SASS from compiled binaries.
- **Resource usage report:** Compiler output from `-Xptxas -v` that lists registers, shared memory and spill bytes per kernel.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-059_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-059_cpu.py
```

## Worked example 1: trace the mechanism

A high-level multiply-plus-add may become a fused instruction depending on types, options and target. If generated code changes, retain the numerical test because one rounding differs from two. A shorter instruction sequence is useful evidence only in combination with the workload's actual behavior.

**Why:** A fused multiply-add rounds once instead of twice, so results can differ slightly from separate operations.

```python
artifacts = {
    "source.cu": "CUDA C++ source",
    "kernel.ptx": "virtual instructions",
    "kernel.cubin": "target machine code",
    "main": "host executable",
}
assert artifacts["kernel.ptx"] != artifacts["kernel.cubin"]
print(artifacts)
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'source.cu': 'CUDA C++ source', 'kernel.ptx': 'virtual instructions', 'kernel.cubin': 'target machine code', 'main': 'host executable'}
```

**Check:** Compare outputs from fused and unfused builds against a high-precision reference within a stated tolerance.

## Worked example 2: change a meaningful condition

A per-thread array causes reported local-memory traffic. Reducing its live range may remove spills, but it can also add recomputation. Compare the compiler report, output and uninstrumented timing under the same target. Do not edit assembly until the source-level cause is understood.

**Why:** Fewer live values can remove spills, though recomputation may add instructions.

**Check:** Compare the spill report, outputs and uninstrumented timings before and after.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Inspect generated code to see whether multiply and add became one fused instruction, and keep the numerical test either way.

**Trap to avoid:** Accepting a shorter instruction sequence as automatically better skips checking that its rounding still meets the tolerance.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Read the compiler's local-memory report, shorten the array's live range, and rebuild for the same target.

**Trap to avoid:** Hand-editing SASS to remove spills makes code that cannot be rebuilt or maintained.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Distinguish native image compatibility from PTX JIT compatibility.

**Trap to avoid:** Assuming any PTX runs on any driver ignores version requirements.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is PTX instruction count not a timing oracle?

**Trap to avoid:** Ranking kernels by PTX length can pick a slower kernel with more memory stalls.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should an unsupported target diagnostic change?

**Trap to avoid:** Trying architecture flags until the error disappears can produce code for the wrong device.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a cold-start experiment.

**Trap to avoid:** Averaging the first run with later runs hides the startup cost.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **PTX instruction count equals executed hardware instruction count or fewer instructions always means faster.** PTX is virtual code that the driver or assembler translates, so its instruction count does not equal executed SASS instructions. Fewer instructions can still be slower if they cause stalls, spills or poor memory behavior. Worked example 1 keeps the numerical test because a fused multiply-add rounds once instead of twice. Judge changes by uninstrumented timing plus correctness. Keep the compiler resource report from each build next to its timing so changes in registers and spills can be traced.

## Self-check, retrieval and transfer

1. How do native image and PTX JIT compatibility differ?
2. What should a cold-start experiment measure?
3. Why can removing spills in worked example 2 fail to speed things up?

Short answers are in the [separate explanations](../solutions/cuda-059_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [NVCC reference](https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/index.html)
- [PTX reference](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-059: PTX, SASS, JIT and inspecting generated code.
Read courses/cuda/cpp/guides/cuda-059.md and courses/cuda/cpp/lessons/cuda-059.md.
Direct prerequisites: `cuda-011`, `cuda-033`, `cuda-036`, `cuda-056`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-059_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-059_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
