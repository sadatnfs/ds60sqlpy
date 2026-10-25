# cuda-028: explanatory solutions

## Mechanism review

Atomicity means one operation is indivisible with respect to competing operations at its scope. Ordering specifies how memory operations relate; visibility concerns which observer can see writes. Publishing a payload through a flag requires a protocol that orders the payload write before a release operation and the consumer's payload read after an appropriate acquire. Both sides must use compatible synchronization and scope. A relaxed atomic counter can correctly count events without publishing unrelated payloads. A fence orders operations but does not force another block to run, so it cannot repair a residency deadlock in an improvised global barrier.

The separate [CPU reference](../references/cuda-028_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A producer writes payload 42, then releases a ready flag. A consumer acquires that publication before reading the payload. The happens-before chain connects payload write to payload read. This is a conceptual protocol; an actual CUDA implementation must use supported atomic types, scope and participating execution conditions.

## Exercise 2

Two workers atomically increment a count, giving count two, while writing separate payloads without publication ordering. The count's arithmetic can be correct even though the payload protocol is incomplete. 'Atomic' describes the increment, not every access in the surrounding program.

## Exercise 3

Payload write, release publication, matching acquire observation and payload read, with the required ordering relationship between them.

## Exercise 4

Ordering does not schedule or release resources for another block. Progress and memory visibility are separate obligations.

## Exercise 5

When the observer is in another block or on the host/device boundary. Use a primitive with scope matching actual observers and supported memory.

## Exercise 6

Publish data and ownership only after writing completes; consumers acknowledge completion before producers reuse the slot. Account for wraparound and capacity.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-028_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Publish data and ownership only after writing completes; consumers acknowledge completion before producers reuse the slot. Account for wraparound and capacity.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
