# cuda-028: explanatory solutions

## Mechanism review

Atomicity means one operation is indivisible with respect to competing operations at its scope. Ordering specifies how memory operations relate; visibility concerns which observer can see writes. Publishing a payload through a flag requires a protocol that orders the payload write before a release operation and the consumer's payload read after an appropriate acquire. Both sides must use compatible synchronization and scope. A relaxed atomic counter can correctly count events without publishing unrelated payloads. A fence orders operations but does not force another block to run, so it cannot repair a residency deadlock in an improvised global barrier.

The separate [CPU reference](../references/cuda-028_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A producer writes payload 42, then releases a ready flag. A consumer acquires that publication before reading the payload. The happens-before chain connects payload write to payload read. This is a conceptual protocol; an actual CUDA implementation must use supported atomic types, scope and participating execution conditions.

**Approach:** Order four events: write payload 42, release the ready flag, acquire the flag in the consumer, then read the payload.

**Why it is correct:** A release store orders earlier writes before the flag, and an acquire load that sees it orders later reads after it.

**A plausible wrong approach:** Using a plain volatile flag with no release or acquire semantics lets the consumer see ready before 42 is visible.

**How to verify:** The reference asserts the four positions are strictly increasing and prints GPU_memory_model_test False, so a device litmus test is still needed.

## Exercise 2

Two workers atomically increment a count, giving count two, while writing separate payloads without publication ordering. The count's arithmetic can be correct even though the payload protocol is incomplete. 'Atomic' describes the increment, not every access in the surrounding program.

**Approach:** Separate the atomic counter from the payload protocol and add release and acquire to the publication.

**Why it is correct:** atomicAdd gives a correct count of two, but says nothing about when each worker's payload becomes visible.

**A plausible wrong approach:** Reasoning that the atomic increment also publishes the payload confuses arithmetic atomicity with ordering.

**How to verify:** Check that a consumer reading the count before the payloads would be guarded by an acquire on a published flag.

## Exercise 3

Payload write, release publication, matching acquire observation and payload read, with the required ordering relationship between them.

**Approach:** List payload write, release publication, matching acquire and payload read.

**Why it is correct:** Removing any link breaks the chain that makes the write visible before the read.

**A plausible wrong approach:** Listing only write and read assumes program order on one thread carries to another.

**How to verify:** Trace the chain on a diagram and mark which thread executes each event.

## Exercise 4

Ordering does not schedule or release resources for another block. Progress and memory visibility are separate obligations.

**Approach:** Separate progress from visibility: the producer must be scheduled to write at all.

**Why it is correct:** A fence orders memory operations of the calling thread and cannot start another block.

**A plausible wrong approach:** Adding more fences in the waiting consumer still never schedules a non-resident producer.

**How to verify:** Replace the wait with a kernel boundary and confirm the consumer sees 42.

## Exercise 5

When the observer is in another block or on the host/device boundary. Use a primitive with scope matching actual observers and supported memory.

**Approach:** Match fence or atomic scope to the farthest observer: block, device or system.

**Why it is correct:** A block-scope operation only promises ordering to threads in the same block.

**A plausible wrong approach:** Using block scope for a host observer leaves the host free to see a stale payload.

**How to verify:** List each observer and confirm the chosen scope covers it.

## Exercise 6

Publish data and ownership only after writing completes; consumers acknowledge completion before producers reuse the slot. Account for wraparound and capacity.

**Approach:** Write a slot, release its full state, let the consumer acquire, read, and release it empty.

**Why it is correct:** Both directions need publication, and the producer must not reuse a slot until it sees empty.

**A plausible wrong approach:** Indexing slots with head mod capacity but not tracking fullness overwrites unread data on wraparound.

**How to verify:** Test a capacity-2 ring with three items and confirm the third waits for the first.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-028_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Publish data and ownership only after writing completes; consumers acknowledge completion before producers reuse the slot. Account for wraparound and capacity.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
