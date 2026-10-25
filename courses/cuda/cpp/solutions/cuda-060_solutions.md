# cuda-060: explanatory solutions

## Mechanism review

Multiple GPUs have distinct allocations, execution contexts and communication paths. Peer access may be available for a pair, but it must be supported and explicitly configured under the platform's rules. Topology affects whether traffic uses PCIe, NVLink or other paths. A collective such as all-reduce combines values and makes the result available to every participant. Participants must agree on communicator, datatype, count and collective order; mismatches can hang or fail. Multi-GPU within one machine does not prove multi-node operation, which adds network, process-launch and failure concerns.

The separate [CPU reference](../references/cuda-060_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Split \([1,2,3,4,5]\) across two devices as \([1,2,3]\) and \([4,5]\). Local sums are six and nine; a combined sum is fifteen. A gather gives the final result to one destination, whereas all-reduce gives fifteen to both participants. A CPU partition model demonstrates semantics only.

## Exercise 2

For a radius-one stencil split into left and right partitions, each side needs its neighbor's boundary value before updating edge cells. Exchange halos and establish completion before reading them. Copying only the interior or assuming all device pointers share one pool breaks the contract.

## Exercise 3

Efficiency is \(\frac{1.6}{2}=0.8\), or 80%, for the same total problem size and timing scope.

## Exercise 4

Collective ordering and signatures disagree; correct the shared protocol rather than adding arbitrary sleeps.

## Exercise 5

Nothing directly. It can validate local arithmetic and models, while peer execution remains unavailable.

## Exercise 6

Strong scaling fixes total work while adding devices; weak scaling grows total work with device count while keeping work per device roughly fixed.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-060_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Strong scaling fixes total work while adding devices; weak scaling grows total work with device count while keeping work per device roughly fixed.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
