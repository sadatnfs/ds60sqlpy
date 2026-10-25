# cuda-018: explanatory solutions

## Mechanism review

Matrix multiplication contracts a shared dimension: an m-by-k matrix A times a k-by-n matrix B produces an m-by-n matrix C. One simple CUDA thread owns one output coordinate and loops across k. Row-major A uses row*k+inner; row-major B uses inner*n+column. The output uses row*n+column. This deliberately simple kernel rereads data and serves as an understandable correctness baseline. Accumulation type and tolerance are part of its specification. Distinct entries and rectangular shapes reveal layout errors better than square all-ones inputs.

The separate [CPU reference](../references/cuda-018_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Multiply \([[1,2,3],[4,5,6]]\) by \([[1,2],[0,1],[2,0]]\). The output is \([[7,4],[16,13]]\). Entry (1,0) is \(4\times 1+5\times 0+6\times 2=16\). Explicitly name every dimension before translating the three scalar indices into flat offsets.

## Exercise 2

Multiplying by an identity matrix preserves input, but that test alone can miss some errors. A 3-by-5 times 5-by-2 case exercises tails and asymmetric dimensions. If \(\mathrm{k}=0\), define the sum of zero products as zero and decide how the host handles the empty inputs without invalid launches.

## Exercise 3

\(1\times 2+2\times 1+3\times 0=4\). The summation axis is k, not the output column axis.

## Exercise 4

Use unequal m and n with unique values, such as the 2-by-3 times 3-by-2 worked case plus a 3-by-5 times 5-by-2 fixture.

## Exercise 5

The output has no elements and the host can return without launching a grid.

## Exercise 6

There are 12 products and associated accumulation operations, conventionally about 24 FLOPs. State whether initialization additions are counted.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-018_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

There are 12 products and associated accumulation operations, conventionally about 24 FLOPs. State whether initialization additions are counted.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
