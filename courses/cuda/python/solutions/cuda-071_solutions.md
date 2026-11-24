# cuda-071: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Identify the timing boundary

Completion must be inside the interval when timing finished work.

**Approach.** Place the stop point after the completion event, not after the call returns: the operation spans from submission at 2 microseconds to finish at 102 microseconds.

**Why it is correct here.** The launch is asynchronous, so returning at 2 microseconds only means the work was queued. The output exists at 102, so the interval that measures finished work must include it.

**A plausible wrong approach.** Stopping the timer at the return reports 2 microseconds and undercounts by the factor of 51 the reference computes.

**How to verify.** The reference asserts `finish_us / submit_us == 51`. In real code, place a synchronize or event wait before the stop timestamp and confirm the recorded interval includes it.

## Exercise 2: Compute the median

Median is eleven.

**Approach.** Sort the five samples `[10, 10, 11, 12, 100]` and take the middle value, 11.

**Why it is correct here.** With an odd count the median is the third sorted value. The single 100 ms outlier does not move it, which is why the median describes typical completion.

**A plausible wrong approach.** Reporting the mean, 28.6 ms, mixes the tail into the center and overstates the typical case by a factor of about 2.6.

**How to verify.** Run the cuda-071 reference: `statistics.median(samples) == 11` is asserted. Also report the maximum 100 so the tail is not lost.

## Exercise 3: Add transfer cost

Include both transfers for end-to-end latency.

**Approach.** Add both transfer costs to the kernel interval: host-to-device before and device-to-host after, so the end-to-end interval covers every byte the caller needs.

**Why it is correct here.** A caller cannot use a device result until it is on the host. In this chapter's 2 to 102 microsecond trace, any copy time is additional end-to-end time.

**A plausible wrong approach.** Reporting only the kernel interval as latency makes a GPU path look faster than a CPU path that includes its own I/O.

**How to verify.** Draw the timeline with upload, kernel and download, and check the timer brackets all three. Label any number as synthetic unless measured on a device.

## Exercise 4: Separate first-call compile time

Report cold and warm distributions separately.

**Approach.** Report the first call and later calls as separate distributions, because the first call can include JIT compilation, module loading and allocation.

**Why it is correct here.** Numba and CuPy compile on first use. Folding that into a warm median hides it or, with few samples, distorts the median.

**A plausible wrong approach.** Discarding the first call without reporting it hides a cost a real user pays at process start.

**How to verify.** Record cold and warm samples in two lists and check the median of the warm list does not include call one.

## Exercise 5: Design equal-work comparison

Use same data and tolerances.

**Approach.** Use the same input data, dtype, output and tolerance for both backends, and time the same boundary (end-to-end or kernel-only) on each.

**Why it is correct here.** A comparison is meaningful only when both sides do the same work. Different input sizes or a looser tolerance on one side make the ratio meaningless.

**A plausible wrong approach.** Comparing a float32 GPU run with a float64 CPU run reports a speedup that is partly a precision change.

**How to verify.** Check outputs agree within the stated tolerance before timing. Record the shape, dtype, tolerance and boundary next to every number.

## Exercise 6: Explain why CPU trace is not a benchmark

The supplied times are invented teaching observations.

**Approach.** State that the trace numbers in this chapter are invented teaching values used to practice analysis, not measurements of any device.

**Why it is correct here.** The reference script computes a median of a hard-coded list; nothing executes on a GPU. Reporting its output as performance would be fabricated evidence.

**A plausible wrong approach.** Copying the 11 ms median into a report as GPU latency misrepresents a CPU script's constant as a hardware result.

**How to verify.** The reference prints `CPU trace analysis`, which is the correct label. A real benchmark records host, device, versions and raw samples.

## Reference observation

Median 11 ms and maximum 100 ms, from synthetic trace data.

The reference file is `courses/cuda/python/references/cuda-071_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
