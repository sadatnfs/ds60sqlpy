# cuda-040: explanatory solutions

## Mechanism review

Pinned host memory is page-locked storage that can support suitable asynchronous transfers. Pinning has a host resource cost, so use bounded reusable buffers rather than pinning arbitrary datasets. Overlap needs eligible transfers, independent work, compatible copy engines and correct dependencies. In double buffering, one slot can be computing while another is filled, but a producer must not overwrite a slot before its previous consumers finish. Chunk size trades fixed overhead against latency and memory. The word Async in an API name does not prove useful overlap occurred; a timeline supplies that evidence.

The separate [CPU reference](../references/cuda-040_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Three chunks each need 2 ms upload, 3 ms compute and 2 ms download. Fully serial time is 21 ms. An ideal three-stage pipeline takes 7 ms for the first result plus two 3 ms steady-state intervals, totaling 13 ms. This optimistic model assumes independent stages and sufficient engines/resources.

## Exercise 2

With two reusable slots, chunk 2 reuses chunk 0's slot only after chunk 0's download and host consumption are complete. Checking only compute completion can still overwrite an output that is being transferred or read. Ownership includes every stage, not just the kernel.

## Exercise 3

First result seven milliseconds plus four intervals of three gives nineteen milliseconds, versus thirty-five serially.

## Exercise 4

Repeated allocation and registration costs can dominate. Prepare a bounded pool and include setup separately in cold-start reporting.

## Exercise 5

Preserve its actual count, bound transfers and kernel accesses, and validate that no stale elements from the previous slot use appear.

## Exercise 6

Measure both per-request latency and throughput under a memory budget; maximum batching may violate response-time requirements.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-040_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Measure both per-request latency and throughput under a memory budget; maximum batching may violate response-time requirements.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
