# cuda-007: explanatory solutions

## Mechanism review

Arithmetic intensity measures operations per byte of data movement under an explicitly stated memory model. A roofline estimate limits performance by the smaller of arithmetic capacity and bandwidth times intensity. It is an upper bound, not a timer. Vector addition reads two float32 values and writes one for one addition, giving roughly one operation per twelve useful bytes before cache and transaction effects. Matrix multiplication can reuse each loaded value many times; tiling increases reuse but consumes working storage. Launch cost, transfer cost, dependency stalls and imperfect access patterns can keep measured work far below either bound.

## Exercise 1

Assume hypothetical bandwidth of 600 GB/s, using decimal billions, and a 12-byte-per-element vector addition. The ideal useful-element throughput is 50 billion elements/s. One million elements require at least 20 microseconds at that bandwidth, excluding launch and host transfer. This is a thought experiment, not a claim about the learner's GPU.

**Approach:** Multiply one million elements by 12 bytes, giving 12 MB, and divide by 600e9 bytes per second.

**Why it is correct:** Vector add reads two float32 values and writes one, so 12 bytes per element is the useful traffic floor.

**A plausible wrong approach:** Dividing by 600 GiB/s instead of decimal GB/s shifts the answer by about 7 percent and mixes unit systems.

**How to verify:** The reference asserts the time is within 1e-15 of 20e-6 seconds and prints ideal_memory_seconds 2e-05.

## Exercise 2

A hypothetical device has 10 TFLOP/s arithmetic capacity and 500 GB/s bandwidth. At intensity 2 FLOP/byte the roofline is 1 TFLOP/s; at intensity 40 it is capped at 10 TFLOP/s. Increasing reuse can change the limiting resource, but a kernel must still expose sufficient independent work.

**Approach:** Compute min(10 TFLOP/s, intensity times 500 GB/s) separately for intensity 2 and intensity 40.

**Why it is correct:** At 2 FLOP/byte bandwidth allows 1 TFLOP/s, below the compute ceiling; at 40 the product 20 TFLOP/s is capped at 10.

**A plausible wrong approach:** Quoting 10 TFLOP/s for both kernels ignores that the low-intensity kernel starves for bytes long before arithmetic saturates.

**How to verify:** The reference asserts limits == [1e12, 10e12]; the ridge point 10e12 / 500e9 = 20 FLOP/byte separates the regimes.

## Exercise 3

Two eight-byte reads and one eight-byte write per element gives 24,000 useful bytes. Measured transactions and cache traffic can differ.

**Approach:** Count per element two 8-byte float64 reads and one 8-byte write, then multiply 24 bytes by 1,000.

**Why it is correct:** Only bytes the algorithm must move count as useful, so 24,000 bytes is a floor on any implementation's traffic.

**A plausible wrong approach:** Using 4-byte elements from the float32 example gives 12,000 bytes, half the real payload for float64.

**How to verify:** Recompute 3 * 8 * 1000 == 24000 and note that profiler transaction counts may exceed it.

## Exercise 4

The units do not cancel. Divide bytes by bytes/s for memory time, or floating operations by operations/s for arithmetic time.

**Approach:** Write the units of each operand, bytes and FLOP per second, and show they do not cancel to seconds.

**Why it is correct:** Time equals a quantity divided by its rate in matching units, so bytes need bytes per second.

**A plausible wrong approach:** Converting TFLOP/s to bytes by assuming one byte per FLOP invents an intensity that the kernel does not have.

**How to verify:** Redo the example: 12e6 bytes / 600e9 bytes/s gives 2e-5 s, and the units check reads seconds.

## Exercise 5

Fixed launch and synchronization overhead dominate; the asymptotic bandwidth model omits that term.

**Approach:** Add a fixed overhead term for launch and synchronization to the bandwidth model and compare magnitudes for one element.

**Why it is correct:** Moving 12 bytes at 600 GB/s takes 20 picoseconds, far below microsecond-scale launch overhead.

**A plausible wrong approach:** Plotting the single-element kernel on a roofline predicts near-zero time and makes any measurement look like a defect.

**How to verify:** Compare 12 / 600e9 with a stated overhead assumption and confirm overhead is many orders larger.

## Exercise 6

Correctness first, then measured time, compiler resource usage and selected memory/occupancy metrics on the same workload. Reduced estimated bytes alone is insufficient.

**Approach:** Validate the tiled kernel's output first, then compare measured time, register counts and occupancy on identical inputs.

**Why it is correct:** Fewer global reads help only if doubled registers do not reduce resident warps so much that latency stays exposed.

**A plausible wrong approach:** Accepting the tiled version because estimated bytes fell skips both correctness and the occupancy trade.

**How to verify:** Record compiler resource usage and timed samples for both variants on the same device and workload.

## Self-check answers

1. **What useful byte count does vector addition of n float32 elements move?** 12n bytes: two 4-byte reads and one 4-byte write per element.
2. **At what intensity does the worked example 2 device switch from bandwidth bound to compute bound?** At 20 FLOP/byte, where 500 GB/s times intensity reaches 10 TFLOP/s.
3. **Why must kernel time and end-to-end time be reported separately?** Transfers, launch overhead and host work can dominate the end-to-end figure even when the kernel is fast.

## Numerical reference and its limits

The [CPU reference](../references/cuda-007_cpu.py) reproduces worked example 1 and prints `{'ideal_memory_seconds': 2e-05, 'roofline_flops_per_second': [1000000000000.0, 10000000000000.0]}`.

## Transfer review

Correctness first, then measured time, compiler resource usage and selected memory/occupancy metrics on the same workload. Reduced estimated bytes alone is insufficient.
