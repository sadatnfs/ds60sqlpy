# cuda-045: explanatory solutions

## Mechanism review

CUDA Core Compute Libraries bring maintained building blocks such as Thrust algorithms, CUB primitives and CUDA-oriented standard-library facilities. Their abstractions do not remove ownership, stream or temporary-storage obligations. Prefer a tested library primitive when it matches semantics, and keep a handwritten version as a learning baseline or for a demonstrated special requirement. Some primitive interfaces separate workspace-size queries from execution; read the pinned interface rather than guessing. Iterator adapters can avoid materializing intermediate arrays, but they must preserve valid lifetimes and access patterns.

The separate [CPU reference](../references/cuda-045_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Transform \([1,2,3,4]\) by squaring and sum, obtaining 30. A fused transform-reduce can avoid a separate \([1,4,9,16]\) allocation when its interface supports the desired operation. The mathematical result is the same; the memory and scheduling behavior differ.

## Exercise 2

Stable filtering \([5,2,5,1]\) for values at least five returns \([5,5]\). Sorting before filtering also retains the two fives here, but generally changes order. Choose the algorithm according to semantic requirements, not merely the nearest familiar function name.

## Exercise 3

Both can produce thirty for the fixture, but transform-reduce can express transformation without a materialized full intermediate.

## Exercise 4

Work can otherwise occur on a different queue than its producers/consumers, breaking dependencies or introducing unexpected synchronization.

## Exercise 5

Zero under the chosen reduction operator; confirm the library call's initial-value contract.

## Exercise 6

A measured unmet contract or fusion opportunity after correctness and library baseline comparison, not merely a desire to avoid reading library documentation.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-045_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

A measured unmet contract or fusion opportunity after correctness and library baseline comparison, not merely a desire to avoid reading library documentation.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
