# cuda-047: explanatory solutions

## Mechanism review

The discrete Fourier transform rewrites samples as frequency components with an explicit sign and normalization convention. An inverse transform must use the matching convention. cuFFT uses plans to prepare a transform shape/layout and may need workspace; plan creation is separate from execution. Multiplication in frequency space corresponds to circular convolution unless padding supplies enough length for the desired linear convolution. Real-to-complex storage has a special output shape and, for some in-place workflows, padding requirements. Define those layouts before moving data rather than treating all transforms as same-size arrays.

The separate [CPU reference](../references/cuda-047_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

The four-sample signal \([0,1,0,-1]\) has energy at the positive and negative one-cycle frequency components. A direct CPU DFT gives approximately [0,-2i,0,2i]. Small real roundoff terms are expected. This is a tiny semantic reference, not a fast FFT implementation.

## Exercise 2

Linear convolution of \([1,2]\) and \([3,4]\) is \([3,10,8]\), requiring length three. A length-two circular convolution wraps the final eight into the first position, giving \([11,10]\). Zero-pad to at least the required linear-convolution length before comparing an FFT workflow.

## Exercise 3

Five plus three minus one equals seven.

## Exercise 4

The normalization convention was omitted or applied on the wrong side; apply the required scaling for the selected transform API.

## Exercise 5

All frequency coefficients are zero within exact or justified numerical behavior; this alone is too weak to validate layout and sign.

## Exercise 6

Separate plan creation from repeated execution, state batch/layout/precision, validate spectrum or convolution semantics and include required transfers.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-047_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Separate plan creation from repeated execution, state batch/layout/precision, validate spectrum or convolution semantics and include required transfers.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
