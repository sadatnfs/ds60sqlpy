# cuda-040: explanatory solutions

## Mechanism review

Pinned host memory is page-locked storage that can support suitable asynchronous transfers. Pinning has a host resource cost, so use bounded reusable buffers rather than pinning arbitrary datasets. Overlap needs eligible transfers, independent work, compatible copy engines and correct dependencies. In double buffering, one slot can be computing while another is filled, but a producer must not overwrite a slot before its previous consumers finish. Chunk size trades fixed overhead against latency and memory. The word Async in an API name does not prove useful overlap occurred; a timeline supplies that evidence.

The separate [CPU reference](../references/cuda-040_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Three chunks each need 2 ms upload, 3 ms compute and 2 ms download. Fully serial time is 21 ms. An ideal three-stage pipeline takes 7 ms for the first result plus two 3 ms steady-state intervals, totaling 13 ms. This optimistic model assumes independent stages and sufficient engines/resources.

**Approach:** Add 2 + 3 + 2 per chunk for 21 ms serial, then 7 ms for the first chunk plus two 3 ms intervals.

**Why it is correct:** Once the pipeline fills, compute at 3 ms is the longest stage and sets the interval, giving 13 ms.

**A plausible wrong approach:** Dividing 21 by 3 stages for 7 ms assumes perfect overlap including fill and drain.

**How to verify:** The reference asserts serial == 21 and ideal == 13 and marks measured_overlap False.

## Exercise 2

With two reusable slots, chunk 2 reuses chunk 0's slot only after chunk 0's download and host consumption are complete. Checking only compute completion can still overwrite an output that is being transferred or read. Ownership includes every stage, not just the kernel.

**Approach:** Reuse chunk 0's slot for chunk 2 only after chunk 0's download and host use finish.

**Why it is correct:** Two slots alternate, so chunk 2 overwrites memory chunk 0 may still be using.

**A plausible wrong approach:** Waiting only for chunk 0's compute lets the new upload overwrite data being downloaded.

**How to verify:** Add a per-slot done event recorded after host consumption and test with slow consumers.

## Exercise 3

First result seven milliseconds plus four intervals of three gives nineteen milliseconds, versus thirty-five serially.

**Approach:** Compute 7 ms for the first chunk plus four intervals of 3 ms.

**Why it is correct:** Five chunks give 7 + 12 = 19 ms against 5 * 7 = 35 ms serial.

**A plausible wrong approach:** Multiplying 13 by five thirds assumes the fill cost repeats each chunk.

**How to verify:** Plug chunks = 5 into the reference formula and expect 19 and 35.

## Exercise 4

Repeated allocation and registration costs can dominate. Prepare a bounded pool and include setup separately in cold-start reporting.

**Approach:** Allocate a bounded pinned pool once and reuse it.

**Why it is correct:** Pinning pages has fixed setup cost that repeats if done every iteration.

**A plausible wrong approach:** Allocating fresh pinned memory per chunk can erase the transfer gain.

**How to verify:** Time cold setup separately and confirm per-iteration times exclude it.

## Exercise 5

Preserve its actual count, bound transfers and kernel accesses, and validate that no stale elements from the previous slot use appear.

**Approach:** Carry the last chunk's real count into transfers and kernel bounds.

**Why it is correct:** A short chunk reusing a slot leaves stale values past its count.

**A plausible wrong approach:** Copying full slot size for the last chunk returns stale elements.

**How to verify:** Fill slots with a sentinel and confirm none appears in the final output.

## Exercise 6

Measure both per-request latency and throughput under a memory budget; maximum batching may violate response-time requirements.

**Approach:** Measure latency and throughput for several chunk sizes within a memory budget.

**Why it is correct:** Larger chunks raise throughput but delay the first response.

**A plausible wrong approach:** Choosing the largest chunk because throughput peaks violates response-time needs.

**How to verify:** Plot both metrics per size and pick one that meets the latency target.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-040_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Measure both per-request latency and throughput under a memory budget; maximum batching may violate response-time requirements.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
