# cuda-022: explanatory solutions

## Mechanism review

A histogram counts values into bins. Several threads can increment the same bin, so ordinary read-modify-write operations can lose updates. An atomic addition makes that individual update indivisible at its supported scope. It does not make an entire multi-step algorithm atomic or publish unrelated data automatically. A block-private histogram can reduce global contention by combining local counts before a global merge. It also costs shared memory and initialization work. Distribution matters: uniformly spread samples and one hot bin exercise very different contention patterns even with identical input size.

The separate [CPU reference](../references/cuda-022_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Values \([0,2,2,1,2,0]\) with three bins produce \([2,1,3]\). The sum of bins is six. Two workers both reading an old count of zero and then each writing one lose a count; correct atomic accumulation produces two.

## Exercise 2

Split the values into two groups of three. Their private histograms are \([1,0,2]\) and \([1,1,1]\); merging gives \([2,1,3]\). This explains the algorithm without promising the private version is faster. For small inputs, initialization and merging may cost more than direct atomic updates.

## Exercise 3

\([1,1,0,3]\), with total five. Include the empty bin in validation.

## Exercise 4

Reject it before indexing or explicitly count it in an overflow category. Never let it address memory before the bins.

## Exercise 5

Repeating one category for every element; compare with a spread distribution under the same count and bin size.

## Exercise 6

Specify bin edges, inclusivity, out-of-range and NaN policies before mapping values to integer bins.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-022_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Specify bin edges, inclusivity, out-of-range and NaN policies before mapping values to integer bins.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
