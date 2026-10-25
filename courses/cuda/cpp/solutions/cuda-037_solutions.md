# cuda-037: explanatory solutions

## Mechanism review

Divergence occurs when lanes in a warp follow different control-flow paths. It can reduce useful parallel execution, but branches that are uniform across a warp or skip substantial work can be beneficial. Irregular workloads also suffer from imbalance when some lanes have much longer loops. Reordering or compacting work can improve grouping at the cost of an extra pass and changed order. Preserve semantic ordering where required and include preprocessing in end-to-end measurement. Branch elimination that evaluates both expensive sides can make the program slower even when it reduces control flow.

The separate [CPU reference](../references/cuda-037_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Four conceptual lanes process workloads \([1,1,1,9]\). A simplified lockstep cost is nine rounds, with 12 useful lane-rounds out of 36 available positions, or one third utilization. This is a pedagogical model, not an actual CUDA timing prediction.

## Exercise 2

A threshold operation has cheap and expensive categories. Grouping expensive items can make work more uniform, but a 2 ms compaction pass is not worthwhile if it saves only 1 ms of kernel time for a one-shot request. Reuse across many iterations can change that decision.

## Exercise 3

Twelve useful lane-rounds over twelve positions gives one, while total work equals the first example's twelve.

## Exercise 4

It can perform unnecessary arithmetic or invalid operations and increase resource use. Preserve conditional semantics and measure.

## Exercise 5

A correct branch may skip the expensive work entirely. A branch-free implementation must still avoid unnecessary side effects or invalid accesses.

## Exercise 6

Group similar lengths, preserve a mapping back to original rows, include grouping cost and validate every output and empty row.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-037_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Group similar lengths, preserve a mapping back to original rows, include grouping cost and validate every output and empty row.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
