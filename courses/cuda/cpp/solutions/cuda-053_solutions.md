# cuda-053: explanatory solutions

## Mechanism review

Tensor cores accelerate supported matrix multiply-accumulate tile operations. Operand formats, accumulator types, layouts, alignment and instruction availability depend on architecture and library mode. Lower precision can reduce memory and increase throughput while changing range and rounding. FP16 and BF16 are not interchangeable merely because both occupy sixteen bits; they allocate exponent and precision bits differently. TF32 and FP8 families also need explicit hardware/software qualification. Use a supported library path first, then study tile-level APIs. A matrix shape or low-precision tensor alone does not prove tensor-core instructions executed.

The separate [CPU reference](../references/cuda-053_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A toy decimal format retaining three significant digits represents 1.001 as 1.00. Summing 1,000 such rounded inputs gives 1,000 rather than 1,001. This is a CPU quantization analogy, not an emulation of FP16 or a measured tensor-core error. Accumulating in a wider type cannot restore information already lost in the inputs.

## Exercise 2

A matrix product can use low-precision operands with wider accumulation. Compare this with low-precision accumulation separately because the two introduce different errors. Include well-scaled and badly scaled matrices, and record actual compute mode plus a supported profiling or library-path observation when available.

## Exercise 3

Device capability, toolkit/library, operand/output/accumulator types, shape/layout/alignment, chosen compute mode, error and observed execution path.

## Exercise 4

No. Successful arithmetic and actual instruction/path selection are separate evidence.

## Exercise 5

Exponent range can overflow or underflow even when ordinary small values pass; precision and range are different limitations.

## Exercise 6

Compare operator error and the model-level metric, including gradients/training stability where applicable, instead of assuming lower precision is harmless.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-053_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Compare operator error and the model-level metric, including gradients/training stability where applicable, instead of assuming lower precision is harmless.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
