# cuda-034: explanatory solutions

## Mechanism review

Coalescing concerns how neighboring lanes' memory requests combine into transactions. The source loop may look sequential while lane addresses are far apart. Write the address for each lane first. Structure-of-arrays often helps a kernel that reads one field from many records, while array-of-structures can suit consumers that need complete records. Alignment, transaction size, cache and architecture affect the exact cost. Count useful bytes separately from fetched bytes and include conversion cost if layout changes. A layout beneficial for one kernel can hurt the full pipeline if every boundary requires reshuffling.

The separate [CPU reference](../references/cuda-034_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Thirty-two lanes read float32 elements at offsets 0 through 31. Their useful data spans 128 bytes. With stride eight elements, offsets run from 0 through 248 and span 996 bytes including gaps. Span is not a transaction count, but it reveals why the access pattern deserves measurement.

## Exercise 2

For records containing x,y,z,w as four floats, reading x for 32 particles advances 16 bytes per lane. A separate x array advances four bytes per lane. If the next stage needs all four fields, compare complete pipeline costs before committing to a representation change.

## Exercise 3

0,12,24,36. Element stride must be multiplied by element size.

## Exercise 4

Span is a reasoning aid. Actual transactions depend on alignment, caching and hardware; measure or clearly model those separately.

## Exercise 5

Little about the full-warp case. Include realistic active masks and tail behavior in the workload.

## Exercise 6

A dedicated x array may reduce repeated unused-field traffic; account for initial conversion, ownership and final consumers in the comparison.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-034_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

A dedicated x array may reduce repeated unused-field traffic; account for initial conversion, ownership and final consumers in the comparison.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
