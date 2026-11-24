# cuda-056: explanatory solutions

## Mechanism review

Within-GPU asynchronous copy mechanisms can move tiles from global to shared storage while other work proceeds, subject to architecture, alignment and API requirements. These are different from host-to-device asynchronous transfers. A producer commits a stage, a consumer waits for its completion, and the stage cannot be overwritten until consumption finishes. Double buffering alternates two storage slots but does not remove these dependencies. Hardware-accelerated paths and fallback behavior must be checked for the exact toolchain and device. Correct tail loading and barrier participation remain essential even when the happy path overlaps efficiently.

The separate [CPU reference](../references/cuda-056_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For three tiles using two slots, tile 0 loads slot A and tile 1 loads slot B. Tile 2 may reuse A only after computation using tile 0 finishes. Copy completion permits reading; consumer completion permits reuse. Those are two different milestones.

**Approach:** Load tiles 0 and 1 into slots A and B, and reuse A for tile 2 only after tile 0's compute finishes.

**Why it is correct:** Copy completion allows reading, while consumer completion allows overwriting.

**A plausible wrong approach:** Reusing A when tile 0's copy completed overwrites data still being computed on.

**How to verify:** The reference asserts ready precedes consuming, which precedes done.

## Exercise 2

A 16-byte transfer requirement does not mean an arbitrary pointer cast creates 16-byte alignment. An address offset by four bytes from an aligned base is still misaligned for that contract. Use valid alignment/layout or a supported fallback, and test the final partial tile separately.

**Approach:** Check the real address alignment before using a 16-byte transfer.

**Why it is correct:** An address 4 bytes past an aligned base is not a multiple of 16.

**A plausible wrong approach:** Casting the pointer to a 16-byte type does not change its address.

**How to verify:** The reference asserts (16 + 4) % 16 != 0 and prints aligned False.

## Exercise 3

Free, copy in progress, copy complete, being consumed, consumption complete, then free for reuse.

**Approach:** List free, copying, ready, consuming, done and back to free.

**Why it is correct:** Each state names what is allowed: reading only after ready, reuse only after done.

**A plausible wrong approach:** Collapsing ready and done into one state allows reuse too early.

**How to verify:** Check the reference's states list in that order.

## Exercise 4

Initiation is not completion. Wait on the correct token/barrier before accessing the destination.

**Approach:** Wait on the barrier or token for the copy before reading.

**Why it is correct:** Starting a copy only queues it.

**A plausible wrong approach:** Reading immediately sees stale or partial data.

**How to verify:** Run racecheck or compare outputs after adding the wait.

## Exercise 5

Use valid bounded loads and neutralization according to the operation; do not copy beyond input merely to fill the tile.

**Approach:** Bound the last tile's copy to valid elements and neutralize the rest.

**Why it is correct:** Copying beyond the input reads memory you do not own.

**A plausible wrong approach:** Filling the tile by over-reading past the end can fault.

**How to verify:** Test a size that leaves a partial tile and compare outputs.

## Exercise 6

First establish a correct synchronous baseline, then verify capability and measure whether hidden latency exceeds added synchronization/resource costs.

**Approach:** Build a correct synchronous baseline and add async staging only if measured faster.

**Why it is correct:** Async copies add synchronization and resource use.

**A plausible wrong approach:** Adding them because they sound faster can slow small kernels.

**How to verify:** Compare correct outputs and measured times for both versions.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-056_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

First establish a correct synchronous baseline, then verify capability and measure whether hidden latency exceeds added synchronization/resource costs.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
