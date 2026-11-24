# cuda-060: explanatory solutions

## Mechanism review

Multiple GPUs have distinct allocations, execution contexts and communication paths. Peer access may be available for a pair, but it must be supported and explicitly configured under the platform's rules. Topology affects whether traffic uses PCIe, NVLink or other paths. A collective such as all-reduce combines values and makes the result available to every participant. Participants must agree on communicator, datatype, count and collective order; mismatches can hang or fail. Multi-GPU within one machine does not prove multi-node operation, which adds network, process-launch and failure concerns.

The separate [CPU reference](../references/cuda-060_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Split \([1,2,3,4,5]\) across two devices as \([1,2,3]\) and \([4,5]\). Local sums are six and nine; a combined sum is fifteen. A gather gives the final result to one destination, whereas all-reduce gives fifteen to both participants. A CPU partition model demonstrates semantics only.

**Approach:** Split [1, 2, 3, 4, 5] into [1, 2, 3] and [4, 5], sum each locally, then combine.

**Why it is correct:** Local sums 6 and 9 add to 15, and all-reduce delivers 15 to both devices.

**A plausible wrong approach:** Using a gather when every device needs the total leaves the second device without the result.

**How to verify:** The reference asserts partials == [6, 9] and all_reduce_model == [15, 15], and prints multi_GPU_executed False.

## Exercise 2

For a radius-one stencil split into left and right partitions, each side needs its neighbor's boundary value before updating edge cells. Exchange halos and establish completion before reading them. Copying only the interior or assuming all device pointers share one pool breaks the contract.

**Approach:** Exchange one boundary value each way before updating edge cells, and wait for the exchange to complete.

**Why it is correct:** A radius-one stencil at the partition edge needs the neighbor's adjacent value.

**A plausible wrong approach:** Updating edges before halos arrive uses stale or missing neighbor values.

**How to verify:** Compare the split result against a single-array stencil on the same input.

## Exercise 3

Efficiency is \(\frac{1.6}{2}=0.8\), or 80%, for the same total problem size and timing scope.

**Approach:** Divide speedup 1.6 by device count 2.

**Why it is correct:** Efficiency is 0.8, or 80 percent, for fixed total work.

**A plausible wrong approach:** Comparing runs with different problem sizes makes the ratio meaningless for strong scaling.

**How to verify:** The reference asserts 1.6 / 2 == 0.8.

## Exercise 4

Collective ordering and signatures disagree; correct the shared protocol rather than adding arbitrary sleeps.

**Approach:** Make every rank call the same collectives in the same order with matching arguments.

**Why it is correct:** Collectives pair calls across ranks by order.

**A plausible wrong approach:** Adding sleeps does not fix mismatched collectives and can still hang.

**How to verify:** Log each rank's call sequence and confirm they match.

## Exercise 5

Nothing directly. It can validate local arithmetic and models, while peer execution remains unavailable.

**Approach:** Validate local arithmetic and the collective model, and mark peer execution unavailable.

**Why it is correct:** Peer access requires two devices and a link between them.

**A plausible wrong approach:** Claiming peer behavior from one GPU reports evidence that was never collected.

**How to verify:** Check the output records multi-GPU execution as unavailable.

## Exercise 6

Strong scaling fixes total work while adding devices; weak scaling grows total work with device count while keeping work per device roughly fixed.

**Approach:** Fix total work for strong scaling and fix work per device for weak scaling.

**Why it is correct:** These answer different questions about adding devices.

**A plausible wrong approach:** Reporting weak-scaling results as strong-scaling speedup overstates gains.

**How to verify:** Label each experiment's total and per-device problem sizes.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-060_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It also asserts an exercise answer that the guide's model leaves for you to derive: `assert 1.6 / 2 == 0.8`. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Strong scaling fixes total work while adding devices; weak scaling grows total work with device count while keeping work per device roughly fixed.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
