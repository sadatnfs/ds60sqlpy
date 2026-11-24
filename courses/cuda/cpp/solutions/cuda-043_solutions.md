# cuda-043: explanatory solutions

## Mechanism review

A CUDA Graph represents a dependency graph that can be instantiated and replayed. It can reduce repeated host submission overhead for suitable workflows, but graph creation and instantiation cost time. Resources referenced by nodes must remain valid across execution, and updates must obey the selected graph API's rules. Stream capture records supported operations in a defined capture context; it is not permission to capture arbitrary host control flow. A CUDA Graph differs from an autograd graph: one schedules execution dependencies, while the other tracks differentiation relationships. Graph replay does not automatically fuse kernels.

The separate [CPU reference](../references/cuda-043_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A synthetic pipeline spends 20 microseconds submitting each ordinary iteration. Graph replay reduces this to 5 microseconds, but setup costs 300 microseconds. Ignoring other equal costs, break-even is more than twenty repeats. At exactly twenty, the submission savings merely repay setup.

**Approach:** Divide 300 microseconds of setup by 15 microseconds saved per replay.

**Why it is correct:** Break-even is 20 replays, so 21 replays give 300 + 105 = 405 against 420 ordinary.

**A plausible wrong approach:** Comparing one replay at 5 microseconds with one ordinary iteration at 20 ignores the setup.

**How to verify:** The reference asserts break_even == 20 and that 21 replays cost less than 21 ordinary iterations.

## Exercise 2

A graph contains fill, affine transform and download nodes with dependencies. Replay uses the same valid storage but new input contents. Changing the input shape beyond allocation capacity is not just a new value; rebuild or perform a supported update after validating all node contracts.

**Approach:** Update input contents in place for replay and rebuild the graph when the shape exceeds capacity.

**Why it is correct:** Graph nodes bake in addresses and sizes, so contents can change but capacity cannot grow.

**A plausible wrong approach:** Writing a larger input into the captured buffer overruns the allocation the nodes reference.

**How to verify:** Replay with new values and same shape, then with a larger shape, and confirm a rebuild occurs.

## Exercise 3

Sixty repeats repay setup; more than sixty are needed for a strict improvement under the simplified model.

**Approach:** Divide 600 microseconds by 10 microseconds saved per replay.

**Why it is correct:** Sixty replays repay setup, and the sixty-first makes the graph strictly cheaper.

**A plausible wrong approach:** Halving the earlier answer because savings doubled ignores that setup doubled too.

**How to verify:** Compute 600 / 10 and check 600 + 61 * r < 61 * o for the stated costs.

## Exercise 4

The graph retains an address dependency, not an owning copy of the data. Keep the allocation alive for all executions or update/rebuild safely.

**Approach:** Keep the temporary buffer alive for every replay or rebuild the graph with a new buffer.

**Why it is correct:** The graph stores the buffer's address, not a copy of its data.

**A plausible wrong approach:** Reallocating a new buffer at the same size does not update the address held by the graph.

**How to verify:** Run replays under a sanitizer after freeing and confirm an invalid access appears.

## Exercise 5

Setup may dominate; compare the ordinary launch path under the same end-to-end contract.

**Approach:** Use ordinary launches for a single run and compare end-to-end.

**Why it is correct:** Setup cost is never repaid with one execution.

**A plausible wrong approach:** Capturing anyway because graphs are faster per replay adds pure overhead.

**How to verify:** Time one ordinary run against setup plus one replay.

## Exercise 6

Fixed-shape repeated inference may benefit, but validate shapes, memory addresses, dynamic operations and framework support before capture or replay.

**Approach:** Capture only fixed-shape inference after checking addresses, dynamic operations and framework support.

**Why it is correct:** Graphs replay fixed work, so dynamic shapes or allocations break the captured plan.

**A plausible wrong approach:** Capturing a model with data-dependent control flow freezes one path for all inputs.

**How to verify:** Validate outputs across several inputs of the captured shape against eager runs.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-043_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Fixed-shape repeated inference may benefit, but validate shapes, memory addresses, dynamic operations and framework support before capture or replay.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
