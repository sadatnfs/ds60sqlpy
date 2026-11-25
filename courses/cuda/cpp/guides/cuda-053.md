# cuda-053: Tensor cores and mixed precision from first principles

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-019`, `cuda-029`, `cuda-036`, `cuda-046`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Report the data type, compute mode, numerical error and confirmed execution path of a mixed-precision matrix multiply.

**Scope:** Matrix multiply-accumulate tiles, supported operand and accumulator types, alignment/layout constraints, range versus precision, and the difference between a tensor core operation and an ordinary scalar instruction.

**Evidence to produce:** Reported type and compute mode, numerical error and confirmed execution path where available.

## Purpose, vocabulary and mental model

Tensor cores accelerate supported matrix multiply-accumulate tile operations. Operand formats, accumulator types, layouts, alignment and instruction availability depend on architecture and library mode. Lower precision can reduce memory and increase throughput while changing range and rounding. FP16 and BF16 are not interchangeable merely because both occupy sixteen bits; they allocate exponent and precision bits differently. TF32 and FP8 families also need explicit hardware/software qualification. Use a supported library path first, then study tile-level APIs. A matrix shape or low-precision tensor alone does not prove tensor-core instructions executed.

### Key terms

- **Tensor core:** A specialized matrix-multiply-accumulate unit that operates on small matrix tiles in reduced-precision formats.
- **Mixed precision:** Using lower-precision inputs with higher-precision accumulation or selected higher-precision operations.
- **BF16:** A 16-bit format with 8 exponent bits that keeps FP32 range but has far fewer significand bits.
- **TF32:** A tensor core mode that uses FP32 range with a 10-bit mantissa for multiplication inputs.
- **Accumulator type:** The precision of the running sum in a matrix multiply, which strongly affects final error.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-053_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-053_cpu.py
```

## Worked example 1: trace the mechanism

A toy decimal format retaining three significant digits represents 1.001 as 1.00. Summing 1,000 such rounded inputs gives 1,000 rather than 1,001. This is a CPU quantization analogy, not an emulation of FP16 or a measured tensor-core error. Accumulating in a wider type cannot restore information already lost in the inputs.

**Why:** Rounding gives 1.00, so the sum is 1,000 against an exact 1,001.

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

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'toy_decimal_exact_sum': 1000.9999999999999, 'toy_quantized_sum': 1000.0, 'tensor_core_emulation': False}
```

**Check:** The reference asserts the difference is 1 within 1e-9 and prints tensor_core_emulation False.

## Worked example 2: change a meaningful condition

A matrix product can use low-precision operands with wider accumulation. Compare this with low-precision accumulation separately because the two introduce different errors. Include well-scaled and badly scaled matrices, and record actual compute mode plus a supported profiling or library-path observation when available.

**Why:** Input rounding and accumulation rounding produce different error growth.

**Check:** Compare both modes on well-scaled and badly scaled matrices against a wide reference.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Round 1.001 to three significant digits, then sum 1,000 rounded copies and compare with the exact sum.

**Trap to avoid:** Presenting this decimal toy as the measured error of FP16 tensor cores overstates what it shows.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Test low-precision inputs with wide accumulation separately from low-precision accumulation.

**Trap to avoid:** Reporting one combined error figure hides which choice causes it.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

What information belongs in a tensor-core experiment record?

**Trap to avoid:** Recording only the speedup makes the result unreproducible.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A float16 GEMM ran successfully. Does that prove tensor-core use?

**Trap to avoid:** Inferring tensor core use from a successful call confuses outcome with mechanism.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Why test extreme magnitudes?

**Trap to avoid:** Testing only values near one passes while real data overflows.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Choose an accuracy policy for ML.

**Trap to avoid:** Assuming lower precision is harmless because one layer looks fine skips the model check.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Every NVIDIA GPU supports every tensor format or lower precision is free accuracy-wise.** Tensor core formats depend on the architecture and library mode, and lower precision changes range and rounding. FP16 has 5 exponent and 10 fraction bits, while BF16 has 8 exponent and 7 fraction bits, so BF16 covers a far wider range with less precision. Worked example 1 shows rounding error accumulating, so record operand and accumulator types and set an accuracy policy before trusting speed.

## Self-check, retrieval and transfer

1. In worked example 1, how far is the rounded sum from the exact sum?
2. A float16 GEMM ran successfully. Does that prove tensor core use?
3. Why test extreme magnitudes?

Short answers are in the [separate explanations](../solutions/cuda-053_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
