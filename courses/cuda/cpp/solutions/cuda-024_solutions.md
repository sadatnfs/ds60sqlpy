# cuda-024: explanatory solutions

## Mechanism review

A pipeline is more than a list of correct kernels. Each stage has a shape, ownership and validity contract that must match its consumer. Filtering changes count; normalization changes numeric range; histogramming assumes valid bins. Keep the count with the output buffer, and do not pass allocation capacity as the number of valid elements. First build a tiny CPU oracle, then introduce one GPU stage at a time. A useful capstone report includes cases where a CPU is preferable, because proving that a GPU exists is different from proving it helps the application.

The separate [CPU reference](../references/cuda-024_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A synthetic event pipeline keeps nonnegative values from \([-2,1,3,-1,2]\), producing \([1,3,2]\). It computes count three, sum six and mean two. A histogram over bins 0 through 3 gives \([0,1,1,1]\). This ties compaction output count to every downstream stage.

## Exercise 2

An empty selection from \([-4,-1]\) has count zero and sum zero, but no defined ordinary arithmetic mean. Return a named empty-result status or optional mean rather than dividing by zero. The histogram remains four zeros under this contract.

## Exercise 3

Count three, sum three, mean one and histogram \([2,0,0,1]\) under four bins.

## Exercise 4

Capacity is storage extent, not valid count. Carry the selected count explicitly and bound downstream reads by it.

## Exercise 5

Reject or explicitly extend the declared bin policy. Do not silently clamp unless clamping is part of the specification.

## Exercise 6

Use identical selection, aggregation and result semantics; include required transfers and allocation or document reused state, retain samples and compare numerical outputs first.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-024_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Use identical selection, aggregation and result semantics; include required transfers and allocation or document reused state, retain samples and compare numerical outputs first.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
