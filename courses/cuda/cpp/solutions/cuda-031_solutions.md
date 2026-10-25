# cuda-031: explanatory solutions

## Mechanism review

A host clock around an asynchronous launch measures submission unless a completion dependency is included. Device events record positions in a stream and can measure elapsed device work between those positions after completion. End-to-end host timing includes the transfers and synchronization the application actually requires. Warm-up separates one-time initialization or JIT work from repeated work, but cold start remains a real user concern and deserves its own measurement. Retain repeated samples and summarize a distribution. Profiling or sanitizer instrumentation changes execution, so do not mix instrumented and ordinary samples in one performance claim.

The separate [CPU reference](../references/cuda-031_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Suppose host submission takes 5 microseconds and the queued kernel completes 80 microseconds later. Reporting five as kernel duration measures the wrong interval. A correctly ordered event interval measures relevant device work; a completed host interval can measure the full request, including additional overhead.

## Exercise 2

Samples \([1.0,1.1,1.0,1.2,9.0]\) milliseconds have median 1.1, but the 9.0 sample still matters. Retain it and investigate interference or cold behavior instead of deleting it merely because it weakens a speedup. Report the warm-up rule before collecting data.

## Exercise 3

Three times. Do not substitute an isolated kernel time into one side of that comparison.

## Exercise 4

A defined ordering/dependency and timing scope. Unordered stream positions do not establish the intended interval.

## Exercise 5

Report fixed overhead separately and avoid interpreting division by near-zero work as meaningful throughput.

## Exercise 6

Resident data can exclude repeated uploads by contract; request-response timing must include transfers needed to deliver the requested result.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-031_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Resident data can exclude repeated uploads by contract; request-response timing must include transfers needed to deliver the requested result.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
