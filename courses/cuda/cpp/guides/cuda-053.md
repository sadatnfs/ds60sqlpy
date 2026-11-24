# cuda-053: Tensor cores and mixed precision from first principles

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-019`, `cuda-029`, `cuda-036`, `cuda-046`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Report the data type, compute mode, numerical error and confirmed execution path of a mixed-precision matrix multiply.

Work through *Tensor cores and mixed precision from first principles* with the concrete cases below. Finish with this evidence:
reported type and compute mode, numerical error and confirmed execution path where available. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Tensor cores accelerate supported matrix multiply-accumulate tile operations. Operand formats, accumulator types, layouts, alignment and instruction availability depend on architecture and library mode. Lower precision can reduce memory and increase throughput while changing range and rounding. FP16 and BF16 are not interchangeable merely because both occupy sixteen bits; they allocate exponent and precision bits differently. TF32 and FP8 families also need explicit hardware/software qualification. Use a supported library path first, then study tile-level APIs. A matrix shape or low-precision tensor alone does not prove tensor-core instructions executed.

### Key terms

- **Tensor core:** A specialized matrix-multiply-accumulate unit that operates on small matrix tiles in reduced-precision formats.
- **Mixed precision:** Using lower-precision inputs with higher-precision accumulation or selected higher-precision operations.
- **BF16:** A 16-bit format with 8 exponent bits that keeps FP32 range but has far fewer significand bits.
- **TF32:** A tensor core mode that uses FP32 range with a 10-bit mantissa for multiplication inputs.
- **Accumulator type:** The precision of the running sum in a matrix multiply, which strongly affects final error.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-053_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-053_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A toy decimal format retaining three significant digits represents 1.001 as 1.00. Summing 1,000 such rounded inputs gives 1,000 rather than 1,001. This is a CPU quantization analogy, not an emulation of FP16 or a measured tensor-core error. Accumulating in a wider type cannot restore information already lost in the inputs.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
exact_input = 1.001
rounded_input = float(format(exact_input, ".3g"))
assert rounded_input == 1.0
exact_sum, quantized_sum = exact_input * 1000, rounded_input * 1000
assert abs(exact_sum - quantized_sum - 1) < 1e-9
print(
    {
        "toy_decimal_exact_sum": exact_sum,
        "toy_quantized_sum": quantized_sum,
        "tensor_core_emulation": False,
    }
)
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'toy_decimal_exact_sum': 1000.9999999999999, 'toy_quantized_sum': 1000.0, 'tensor_core_emulation': False}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A matrix product can use low-precision operands with wider accumulation. Compare this with low-precision accumulation separately because the two introduce different errors. Include well-scaled and badly scaled matrices, and record actual compute mode plus a supported profiling or library-path observation when available.

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

What information belongs in a tensor-core experiment record?

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A float16 GEMM ran successfully. Does that prove tensor-core use?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why test extreme magnitudes?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Choose an accuracy policy for ML.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **every NVIDIA GPU supports every tensor format or lower precision is free accuracy-wise.**

For the concrete failure exercise, a float16 GEMM ran successfully. Does that prove tensor-core use?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-053_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-053: Tensor cores and mixed precision from first principles.
Read courses/cuda/cpp/guides/cuda-053.md and courses/cuda/cpp/lessons/cuda-053.md.
Direct prerequisites: `cuda-019`, `cuda-029`, `cuda-036`, `cuda-046`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-053_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-053_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
