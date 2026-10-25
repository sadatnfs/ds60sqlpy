# cuda-056: explanatory solutions

## Mechanism review

Within-GPU asynchronous copy mechanisms can move tiles from global to shared storage while other work proceeds, subject to architecture, alignment and API requirements. These are different from host-to-device asynchronous transfers. A producer commits a stage, a consumer waits for its completion, and the stage cannot be overwritten until consumption finishes. Double buffering alternates two storage slots but does not remove these dependencies. Hardware-accelerated paths and fallback behavior must be checked for the exact toolchain and device. Correct tail loading and barrier participation remain essential even when the happy path overlaps efficiently.

The separate [CPU reference](../references/cuda-056_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For three tiles using two slots, tile 0 loads slot A and tile 1 loads slot B. Tile 2 may reuse A only after computation using tile 0 finishes. Copy completion permits reading; consumer completion permits reuse. Those are two different milestones.

## Exercise 2

A 16-byte transfer requirement does not mean an arbitrary pointer cast creates 16-byte alignment. An address offset by four bytes from an aligned base is still misaligned for that contract. Use valid alignment/layout or a supported fallback, and test the final partial tile separately.

## Exercise 3

Free, copy in progress, copy complete, being consumed, consumption complete, then free for reuse.

## Exercise 4

Initiation is not completion. Wait on the correct token/barrier before accessing the destination.

## Exercise 5

Use valid bounded loads and neutralization according to the operation; do not copy beyond input merely to fill the tile.

## Exercise 6

First establish a correct synchronous baseline, then verify capability and measure whether hidden latency exceeds added synchronization/resource costs.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-056_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

First establish a correct synchronous baseline, then verify capability and measure whether hidden latency exceeds added synchronization/resource costs.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
