# cuda-004: explanatory solutions

## Mechanism review

Decomposition assigns parts of a problem to workers while preserving its mathematical meaning. A map transforms each input independently. A reduction combines many values into one. A scan produces every prefix, so its outputs encode more information than a reduction. Gather reads from chosen locations; scatter writes to chosen locations and needs a conflict policy when destinations overlap. Work counts all operations, while dependency depth counts the longest chain that cannot be parallelized. A useful decomposition names each output owner, describes required inputs and states when producers must finish before consumers read.

The separate [CPU reference](../references/cuda-004_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Partition 10 elements into conceptual blocks of four. The ownership ranges are [0,4), [4,8) and [8,10). The half-open notation includes the start and excludes the end. Each element appears once; the final block has a tail. Allocating three full blocks of output without a bounds predicate would incorrectly expose positions 10 and 11.

## Exercise 2

For \([2,1,3,4]\), reduction returns 10. Inclusive scan returns \([2,3,6,10]\), and exclusive scan returns \([0,2,3,6]\). A reduction alone cannot tell element 2 where to write in a stable filtered output. That position comes from a prefix count of earlier selected elements.

## Exercise 3

Four tiles cover it. Predicate both x<7 and y<3; the right and bottom tiles contain invalid lane positions.

## Exercise 4

Unique readers do not imply unique output ownership. Define an atomic combine, collision-free destination calculation or a staged grouping algorithm.

## Exercise 5

The reduction identity is zero; both scans are empty. An implementation should define these cases before launching work.

## Exercise 6

Map produces selection flags, exclusive scan gives each selected element's destination, and the final prefix plus flag gives output count.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-004_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Map produces selection flags, exclusive scan gives each selected element's destination, and the final prefix plus flag gives output count.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
