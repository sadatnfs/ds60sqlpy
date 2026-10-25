# cuda-043: explanatory solutions

## Mechanism review

A CUDA Graph represents a dependency graph that can be instantiated and replayed. It can reduce repeated host submission overhead for suitable workflows, but graph creation and instantiation cost time. Resources referenced by nodes must remain valid across execution, and updates must obey the selected graph API's rules. Stream capture records supported operations in a defined capture context; it is not permission to capture arbitrary host control flow. A CUDA Graph differs from an autograd graph: one schedules execution dependencies, while the other tracks differentiation relationships. Graph replay does not automatically fuse kernels.

The separate [CPU reference](../references/cuda-043_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A synthetic pipeline spends 20 microseconds submitting each ordinary iteration. Graph replay reduces this to 5 microseconds, but setup costs 300 microseconds. Ignoring other equal costs, break-even is more than twenty repeats. At exactly twenty, the submission savings merely repay setup.

## Exercise 2

A graph contains fill, affine transform and download nodes with dependencies. Replay uses the same valid storage but new input contents. Changing the input shape beyond allocation capacity is not just a new value; rebuild or perform a supported update after validating all node contracts.

## Exercise 3

Sixty repeats repay setup; more than sixty are needed for a strict improvement under the simplified model.

## Exercise 4

The graph retains an address dependency, not an owning copy of the data. Keep the allocation alive for all executions or update/rebuild safely.

## Exercise 5

Setup may dominate; compare the ordinary launch path under the same end-to-end contract.

## Exercise 6

Fixed-shape repeated inference may benefit, but validate shapes, memory addresses, dynamic operations and framework support before capture or replay.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-043_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Fixed-shape repeated inference may benefit, but validate shapes, memory addresses, dynamic operations and framework support before capture or replay.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
