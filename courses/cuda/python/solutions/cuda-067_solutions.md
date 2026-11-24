# cuda-067: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Count bytes for ten iterations

The round-trip version moves 20 B.

**Approach.** Count bytes per iteration for the round-trip version: one upload of B and one download of B, so `2B` per iteration and `20B` over ten iterations. With the reference size of 4096 bytes that is 81920.

**Why it is correct here.** The reference sets `size = 4096`, `iterations = 10`, and asserts `round_trip == 81920`. The resident version uploads once and downloads once, giving `2 * 4096 = 8192`, a factor of ten fewer bytes.

**A plausible wrong approach.** Counting only uploads (`10B`) treats the output copy as free. Many real pipelines download a result every step for logging, so omitting it halves the modeled traffic.

**How to verify.** Run `courses/cuda/python/references/cuda-067_cpu.py`: it asserts 81920 and 8192 and prints both. Change `iterations` to 20 and confirm the round-trip figure doubles while the resident figure does not change.

## Exercise 2: Model a batched transfer

Batch submission reduces fixed cost not payload.

**Approach.** Model each transfer as `latency + bytes / bandwidth` and compare 100 copies of 40 bytes with one copy of 4000 bytes using the reference values `latency = 10e-6` and `bandwidth = 1e9`.

**Why it is correct here.** Both cases move 4000 bytes, so the bandwidth term is identical. The batch pays the 10 microsecond latency once instead of 100 times, which is why the reference asserts `many > one`.

**A plausible wrong approach.** Expecting batching to reduce the payload is the mistake. The bytes are the same; if your model shows the bandwidth term shrinking, you have double-counted or dropped rows.

**How to verify.** Compute by hand: 100 times 10 microseconds is 1 millisecond of latency versus 10 microseconds for one batch. The reference assertion `many > one` must pass, and the gap must be about 990 microseconds in the model.

## Exercise 3: Find premature source reuse

Wait on the copy event before overwrite.

**Approach.** Trace the buffer that an asynchronous copy reads from, and find any write to it before the copy's completion event. Insert a wait on that event (or the stream) before the overwrite.

**Why it is correct here.** An asynchronous upload returns control to Python before the DMA engine has read the host buffer. Refilling that buffer for the next batch can change bytes still being copied, so the device sees a mix of two batches.

**A plausible wrong approach.** Adding a sleep after the copy call seems to fix it in testing because the copy usually finishes. It is timing luck: a larger batch or a busy bus makes the race reappear.

**How to verify.** Write the event order for two batches and check that every refill of the host buffer comes after the previous copy's completion event. On a device, a test that fills the buffer with a known pattern per batch and checks the device copy catches the mix.

## Exercise 4: Explain pinned-memory lifetime

Keep owner alive until completion.

**Approach.** Keep the Python object that owns pinned host memory alive until every copy that reads or writes it has completed, and release it only after that wait.

**Why it is correct here.** Pinned memory is page-locked so the copy engine can access it directly. If the owning object is garbage collected while a copy is pending, the pages can be unpinned or reused, and the copy touches memory it no longer owns.

**A plausible wrong approach.** Pinning every array in the program to be safe consumes host memory the OS cannot page out, which can starve other processes. Pinning is a bounded resource, not a free speedup.

**How to verify.** In a code review, find each pinned allocation and the stream event it depends on, and check that the release path waits on that event. The model check is a written ordering: allocate, copy issued, copy completed, release.

## Exercise 5: Design an end-to-end timer

Start before preparation and stop after host output.

**Approach.** Start the timer before input preparation and the host-to-device copy, and stop it only after the result has been copied back and is usable by host code.

**Why it is correct here.** End-to-end latency is what a caller experiences. In this chapter the resident and round-trip versions differ mainly in transfer counts, so a timer that excludes transfers cannot see the difference the lesson is teaching.

**A plausible wrong approach.** Stopping the timer right after the kernel call returns measures submission only, because the call is asynchronous; it reports a tiny number regardless of the 81920 versus 8192 byte difference.

**How to verify.** Write the timer boundaries next to each event of the pipeline and check that both copies and the completion wait are inside. Any timing you record must be labeled with those boundaries; this chapter's numbers are modeled, not measured.

## Exercise 6: Identify an intentionally CPU-friendly workload

Tiny one-off arrays can favor CPU.

**Approach.** Look for work where the fixed costs dominate: a small array used once, such as the 40-byte rows in worked example 1 processed one at a time, with a simple elementwise operation.

**Why it is correct here.** With the reference model, a 40-byte transfer costs about 10 microseconds of latency and 40 nanoseconds of bandwidth time. A CPU can finish a few arithmetic operations on 10 floats far faster than that latency, before any kernel launch cost is added.

**A plausible wrong approach.** Assuming the GPU always wins because it has more cores ignores the fixed costs. A benchmark on one tiny array would show the CPU ahead, and the conclusion that the GPU is slow would also be wrong.

**How to verify.** State the workload size and the transfer count, and compare modeled latency with an estimate of CPU work. The conclusion is valid when you can show that latency terms, not arithmetic, dominate the GPU total.

## Reference observation

81920 versus 8192 modeled bytes; these are not measured timings.

The reference file is `courses/cuda/python/references/cuda-067_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
