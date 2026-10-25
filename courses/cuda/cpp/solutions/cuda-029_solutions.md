# cuda-029: explanatory solutions

## Mechanism review

A mathematically equivalent expression can have different floating-point behavior. Fused multiply-add rounds a product-plus-sum once instead of rounding the product and then the addition. Fast-math modes can change precision and special-value behavior, so they require an explicit error budget. Variance computed as mean of squares minus square of mean subtracts nearby large values and can lose a small real variance. A centered or carefully merged online algorithm reduces that risk. Conditioning describes sensitivity of the problem itself; algorithmic stability describes how well the chosen computation handles it. Neither is fixed merely by changing processors.

The separate [CPU reference](../references/cuda-029_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For \([100000001,100000002,100000003]\), center around the mean 100000002. Squared deviations are \([1,0,1]\), giving population variance \(\frac{2}{3}\). Computing two roughly \(10^{16}\) quantities and subtracting them risks losing that small answer in ordinary floating precision.

## Exercise 2

A dot product with very large and very small terms can differ under different association or FMA choices. Compare to a higher-precision reference and report absolute error, relative error when meaningful, and nonfinite values. Exact equality is appropriate only when the contract and arithmetic justify it.

## Exercise 3

Zero. A normalization later still needs a deliberate epsilon or constant-row policy.

## Exercise 4

A predeclared tolerance derived from the application, input range and reference method, plus finite-output and adversarial checks.

## Exercise 5

Dividing by a tiny reference magnifies small absolute differences; retain an absolute error criterion.

## Exercise 6

State accumulation precision, association/reproducibility expectations and uncertainty. Preserve raw data and avoid silently changing numerical modes between benchmark baselines.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-029_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

State accumulation precision, association/reproducibility expectations and uncertainty. Preserve raw data and avoid silently changing numerical modes between benchmark baselines.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
