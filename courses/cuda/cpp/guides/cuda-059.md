# cuda-059: PTX, SASS, JIT and inspecting generated code

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-011`, `cuda-033`, `cuda-036`, `cuda-056`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Inspect generated PTX and SASS to explain a selected instruction sequence and validate any change with existing tests.

Work through *PTX, SASS, JIT and inspecting generated code* with the concrete cases below. Finish with this evidence:
explain a selected instruction sequence and validate any optimization with the existing tests. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

PTX is a virtual instruction language, while SASS describes machine instructions for a particular GPU architecture. The driver or toolchain can translate PTX differently across targets and versions. A fat binary can contain native device images and PTX fallback according to a deliberate policy. JIT can introduce cold-start cost and compatibility constraints. Inspect compiler resource reports and generated code to test a hypothesis, such as unexpected local-memory traffic, before attempting inline assembly. Counting PTX instructions does not directly count executed hardware operations or predict runtime.

### Key terms

- **PTX:** The virtual instruction set that `nvcc` emits before architecture-specific assembly.
- **SASS:** The native machine instructions that a specific GPU architecture actually executes.
- **cuobjdump:** A tool that extracts embedded PTX and SASS from compiled binaries.
- **Resource usage report:** Compiler output from `-Xptxas -v` that lists registers, shared memory and spill bytes per kernel.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-059_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-059_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A high-level multiply-plus-add may become a fused instruction depending on types, options and target. If generated code changes, retain the numerical test because one rounding differs from two. A shorter instruction sequence is useful evidence only in combination with the workload's actual behavior.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

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

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'source.cu': 'CUDA C++ source', 'kernel.ptx': 'virtual instructions', 'kernel.cubin': 'target machine code', 'main': 'host executable'}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A per-thread array causes reported local-memory traffic. Reducing its live range may remove spills, but it can also add recomputation. Compare the compiler report, output and uninstrumented timing under the same target. Do not edit assembly until the source-level cause is understood.

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

Distinguish native image compatibility from PTX JIT compatibility.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is PTX instruction count not a timing oracle?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should an unsupported target diagnostic change?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a cold-start experiment.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **PTX instruction count equals executed hardware instruction count or fewer instructions always means faster. , .**

For the concrete failure exercise, why is PTX instruction count not a timing oracle?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-059_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
