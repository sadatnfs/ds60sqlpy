# cuda-082: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Draw the dependency graph

Edges encode actual data dependencies.

**Approach.** Draw the dependency graph for one batch as nodes upload, transform and download with edges upload to transform and transform to download, matching the `edges` list in the reference.

**Why it is correct here.** Edges represent data dependencies: transform reads the uploaded buffer, and download reads the transform output. Any execution order respecting these edges is valid.

**A plausible wrong approach.** Drawing edges from code order instead of data flow invents dependencies between unrelated work and hides real ones crossing library calls.

**How to verify.** Run the reference: the valid order passes the positions check. The order with download first fails, which the second assertion confirms.

## Exercise 2: Locate a missing wait

Reading before the producing event is unsafe.

**Approach.** Locate a missing wait: consumer B on stream 2 reads buffer X without waiting for event E recorded after producer A wrote X on stream 1.

**Why it is correct here.** Streams are independent queues. Without an explicit wait on E, stream 2 may run B before A finishes, so B reads stale or partial data.

**A plausible wrong approach.** Assuming the host Python call to A finishing means A's kernel finished confuses queuing with completion.

**How to verify.** Insert `stream2.wait_event(E)` before B, and show that with a slow producer the consumer output is correct only when the wait exists.

## Exercise 3: Separate host wait and stream wait

One blocks host progress and the other queues device ordering.

**Approach.** Separate `event.synchronize()`, which blocks the host thread until the event completes, from `stream.wait_event(event)`, which queues a device-side dependency and returns immediately.

**Why it is correct here.** A host wait stalls Python and can prevent further work from being enqueued. A stream wait keeps the host free while ordering device work.

**A plausible wrong approach.** Using a host synchronize everywhere fixes correctness but serializes host and device.

**How to verify.** Inspect a profiler timeline for both versions and confirm the outputs are identical.

## Exercise 4: Trace storage reuse

Do not recycle before final consumer completion.

**Approach.** Trace storage reuse: a buffer freed after its last consumer kernel is enqueued must not be handed to a new producer until that consumer completes on the device.

**Why it is correct here.** Caching allocators reuse memory quickly. If the stream order between the old consumer and the new producer is not guaranteed, the new producer can overwrite data still being read.

**A plausible wrong approach.** Freeing a buffer as soon as the host is done with its Python object assumes device work is done too.

**How to verify.** Use `record_stream` or an event so the allocator knows the last user, then test with a slow consumer.

## Exercise 5: Design non-default stream test

Use two streams and known values.

**Approach.** Design a non-default stream test: create two non-default streams, write known values on stream 1, record an event, wait for it on stream 2 and compute on stream 2.

**Why it is correct here.** The default stream may add implicit synchronization that hides missing waits. Using two explicit streams removes that safety net, so the test checks the intended ordering.

**A plausible wrong approach.** Testing only on the default stream passes even with the wait removed.

**How to verify.** Run the test with the wait present and confirm the known result, then remove it and observe possible wrong values.

## Exercise 6: Explain why global synchronization can mask bugs

Global waits accidentally add dependencies absent from the intended program.

**Approach.** Explain that calling `cuda.synchronize()` everywhere can mask a missing dependency, because the global wait orders all prior work.

**Why it is correct here.** The program then works only because of an extra global ordering, not because of explicit data edges. Removing the global wait later for performance exposes the bug.

**A plausible wrong approach.** Treating a correct result with global waits as proof that dependencies are complete hides the missing event.

**How to verify.** Remove global waits one at a time in a test and keep only explicit events. Outputs must stay correct.

## Reference observation

Valid dependency order accepted; premature download rejected.

The reference file is `courses/cuda/python/references/cuda-082_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
