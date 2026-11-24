# cuda-053: explanatory solutions

## Mechanism review

Tensor cores accelerate supported matrix multiply-accumulate tile operations. Operand formats, accumulator types, layouts, alignment and instruction availability depend on architecture and library mode. Lower precision can reduce memory and increase throughput while changing range and rounding. FP16 and BF16 are not interchangeable merely because both occupy sixteen bits; they allocate exponent and precision bits differently. TF32 and FP8 families also need explicit hardware/software qualification. Use a supported library path first, then study tile-level APIs. A matrix shape or low-precision tensor alone does not prove tensor-core instructions executed.

The separate [CPU reference](../references/cuda-053_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A toy decimal format retaining three significant digits represents 1.001 as 1.00. Summing 1,000 such rounded inputs gives 1,000 rather than 1,001. This is a CPU quantization analogy, not an emulation of FP16 or a measured tensor-core error. Accumulating in a wider type cannot restore information already lost in the inputs.

**Approach:** Round 1.001 to three significant digits, then sum 1,000 rounded copies and compare with the exact sum.

**Why it is correct:** Rounding gives 1.00, so the sum is 1,000 against an exact 1,001.

**A plausible wrong approach:** Presenting this decimal toy as the measured error of FP16 tensor cores overstates what it shows.

**How to verify:** The reference asserts the difference is 1 within 1e-9 and prints tensor_core_emulation False.

## Exercise 2

A matrix product can use low-precision operands with wider accumulation. Compare this with low-precision accumulation separately because the two introduce different errors. Include well-scaled and badly scaled matrices, and record actual compute mode plus a supported profiling or library-path observation when available.

**Approach:** Test low-precision inputs with wide accumulation separately from low-precision accumulation.

**Why it is correct:** Input rounding and accumulation rounding produce different error growth.

**A plausible wrong approach:** Reporting one combined error figure hides which choice causes it.

**How to verify:** Compare both modes on well-scaled and badly scaled matrices against a wide reference.

## Exercise 3

Device capability, toolkit/library, operand/output/accumulator types, shape/layout/alignment, chosen compute mode, error and observed execution path.

**Approach:** Record device capability, library versions, types, shape, layout, alignment, compute mode, error and execution path.

**Why it is correct:** Tensor core use depends on all of these.

**A plausible wrong approach:** Recording only the speedup makes the result unreproducible.

**How to verify:** Rerun from the record on the same device and confirm the result.

## Exercise 4

No. Successful arithmetic and actual instruction/path selection are separate evidence.

**Approach:** Look for profiler evidence of the instruction path rather than the result alone.

**Why it is correct:** Correct float16 results can come from non-tensor-core paths.

**A plausible wrong approach:** Inferring tensor core use from a successful call confuses outcome with mechanism.

**How to verify:** Check the kernel names or instruction counters in a profiler run.

## Exercise 5

Exponent range can overflow or underflow even when ordinary small values pass; precision and range are different limitations.

**Approach:** Include very large and very small values in tests.

**Why it is correct:** float16 overflows above about 65,504 and loses small values to underflow.

**A plausible wrong approach:** Testing only values near one passes while real data overflows.

**How to verify:** Feed 70,000 and 1e-8 and check for infinity or zero.

## Exercise 6

Compare operator error and the model-level metric, including gradients/training stability where applicable, instead of assuming lower precision is harmless.

**Approach:** Compare both operator error and model-level metrics such as accuracy or loss.

**Why it is correct:** Small per-operator errors can grow through training.

**A plausible wrong approach:** Assuming lower precision is harmless because one layer looks fine skips the model check.

**How to verify:** Train or evaluate with both precisions and compare the metric.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-053_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Compare operator error and the model-level metric, including gradients/training stability where applicable, instead of assuming lower precision is harmless.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
