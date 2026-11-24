# cuda-001: explanatory solutions

## Mechanism review

A CPU is optimized to make progress on a comparatively small number of complicated instruction streams. A GPU spends more of its resources on throughput across many pieces of work. This is a design distinction, not a rule that the GPU wins. A dependency means that one result must exist before another calculation can start. Pixel brightness updates have independent destinations; a running account balance has a dependency between successive balances. There can still be a parallel prefix algorithm for that balance, but changing the algorithm is real work. Include loading data, launching kernels and returning results when deciding whether acceleration helps a person waiting for an answer.

The separate [CPU reference](../references/cuda-001_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Suppose an application spends 20 seconds parsing and 80 seconds transforming pixels. An imagined GPU makes the transform ten times faster and adds 4 seconds of transfers. The new time is \(20 + 8 + 4 = 32\) seconds, so the application speedup is 3.125. The tenfold kernel improvement is not the application improvement. Even an infinitely fast transform leaves 24 seconds under these assumptions.

**Approach:** Split the 100-second run into its 20-second parse, 80-second transform and the new 4-second transfer, then rescale only the transform by ten.

**Why it is correct:** Amdahl's model divides only the accelerated phase, so parsing stays at 20 seconds and the added copies count against the 32-second total.

**A plausible wrong approach:** Dividing the whole 100 seconds by ten predicts 10 seconds; that silently accelerates the parser and forgets the 4 seconds of copies.

**How to verify:** Run the CPU reference: its assertions require gpu == 32 and cpu / gpu == 3.125, and the printed dictionary shows modeled_GPU_seconds 32.0.

## Exercise 2

For one tiny request, suppose CPU arithmetic costs 2 microseconds, while GPU submission and transfers cost 30 microseconds before arithmetic. A 0.2 microsecond kernel gives 30.2 microseconds end to end. Batching 1,000 independent requests may amortize overhead, but it changes waiting time and memory usage. Neither result follows from a core count.

**Approach:** Add the 30 microseconds of submission and transfer to the 0.2 microsecond kernel and compare that 30.2 sum with 2 microseconds of CPU arithmetic.

**Why it is correct:** A single request waits for every phase in sequence, so fixed launch and copy overhead dominate when the arithmetic itself is only two microseconds.

**A plausible wrong approach:** Comparing 0.2 against 2 and claiming a tenfold win measures the kernel alone; the requester still waits more than fifteen times longer.

**How to verify:** Recompute 30 + 0.2 by hand, then recompute per-request overhead for a batch of 1,000 and note the extra queueing delay it introduces.

## Exercise 3

The 40-second serial part remains. The upper bound is \(\frac{100}{40} = 2.5\), even with an infinitely fast parallel part.

**Approach:** Hold the 40 serial seconds fixed, let the 60 parallel seconds approach zero, and divide the original 100 seconds by what remains.

**Why it is correct:** With zero transfer cost the limit of 40 + 60/s as s grows is 40, so no processor count can push past 2.5.

**A plausible wrong approach:** Answering 60 or 100 times faster from the parallel fraction alone ignores that the serial 40 seconds never shrinks.

**How to verify:** The reference asserts 100 / 40 == 2.5; also try s = 10 to get 46 seconds and a 2.17 speedup below the bound.

## Exercise 4

Record upload, allocation, launch, synchronization and download costs with the same input and output contract before computing application speedup.

**Approach:** List every phase the 2 ms CPU path includes, then demand the GPU path report the same phases: allocation, upload, launch, synchronization and download.

**Why it is correct:** Only matching input and output contracts make a ratio meaningful; 0.1 ms covers device arithmetic, not the request a user experiences.

**A plausible wrong approach:** Timing the kernel with a host clock and no synchronization records only the asynchronous launch call, inflating the claimed speedup further.

**How to verify:** Write a table with one column per phase for both paths and confirm both rows end at the same validated output bytes.

## Exercise 5

The mathematical output is empty. A host guard can return immediately instead of launching an empty grid; fixed overhead otherwise dominates.

**Approach:** Check the pixel count on the host before any allocation and return an empty result when it equals zero.

**Why it is correct:** An empty image has an empty output by definition, so skipping the launch preserves the contract and avoids paying fixed overhead for nothing.

**A plausible wrong approach:** Computing a grid of ceil(0 / 256) blocks and launching anyway yields a zero-sized grid, which the runtime rejects as an invalid configuration.

**How to verify:** Call the transform with a zero-length buffer and assert the output length is zero and that no device allocation was requested.

## Exercise 6

CUDA does not remove network waiting or dependency ordering. First change the request architecture or batch independent work; do not infer a compute bottleneck.

**Approach:** Identify that each HTTP call needs the previous response, then look for independent requests or a redesigned API before considering any kernel.

**Why it is correct:** The dominant cost is network round trips ordered by data dependency; a kernel cannot issue or wait on those requests faster.

**A plausible wrong approach:** Launching 1,000 GPU threads, one per request, ignores that request k cannot start until request k minus one returns.

**How to verify:** Profile wall time per request on the host and confirm network wait, not local arithmetic, accounts for nearly all of it.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-001_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It also asserts an exercise answer that the guide's model leaves for you to derive: `assert 100 / 40 == 2.5`. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

CUDA does not remove network waiting or dependency ordering. First change the request architecture or batch independent work; do not infer a compute bottleneck.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
