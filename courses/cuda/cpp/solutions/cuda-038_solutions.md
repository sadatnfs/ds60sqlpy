# cuda-038: explanatory solutions

## Mechanism review

A defensible benchmark holds the problem contract fixed while changing one implementation decision. Record dtype, layout, supported shapes, numerical tolerance, data residency and required output. Compare against a competent baseline, not a deliberately poor CPU loop. Retain cold and warm measurements separately, avoid reporting only the fastest observation, and disclose device sharing, clocks and thermal conditions when relevant. A performance regression can coexist with improved kernel time if another phase grows. Report uncertainty and supported scope; no universal speed threshold is valid across every GPU and workload.

The separate [CPU reference](../references/cuda-038_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Baseline times are \([10,11,10,9,10]\) ms and candidate times \([8,8,9,8,7]\) ms. Median ratio is \(\frac{10}{8}=1.25\). This suggests an improvement for the measured fixture, but five synthetic samples do not establish stability across hardware, sizes or operating conditions.

## Exercise 2

A candidate uses float16 while the baseline uses float64. It may legitimately target a different accuracy budget, but it is not a like-for-like implementation comparison until both satisfy the same required error contract. Include conversion cost if the application supplies and consumes another dtype.

## Exercise 3

Specify exact input generation, dtype/layout, accumulation, alpha/beta semantics, output tolerance, residency, setup inclusion and sample policy.

## Exercise 4

Apply the same summary policy to both and retain all raw samples; investigate outliers without selectively deleting them.

## Exercise 5

They expose launch overhead and boundary inefficiencies that a single large aligned workload conceals.

## Exercise 6

Ship only if it satisfies a documented application error budget and supported-input policy, with a fallback or rejection outside that contract.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-038_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Ship only if it satisfies a documented application error budget and supported-input policy, with a fallback or rejection outside that contract.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
