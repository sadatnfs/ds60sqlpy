# cuda-043: explanatory solutions

## Mechanism review

A CUDA Graph represents a dependency graph that can be instantiated and replayed. It can reduce repeated host submission overhead for suitable workflows, but graph creation and instantiation cost time. Resources referenced by nodes must remain valid across execution, and updates must obey the selected graph API's rules. Stream capture records supported operations in a defined capture context; it is not permission to capture arbitrary host control flow. A CUDA Graph differs from an autograd graph: one schedules execution dependencies, while the other tracks differentiation relationships. Graph replay does not automatically fuse kernels.

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

## Self-check answers

1. **Where is break-even in worked example 1?** Setup 300 microseconds divided by a 15 microsecond saving per replay is 20 replays; more than twenty gives a net gain.
2. **What must stay valid across graph replays?** Every buffer and resource referenced by graph nodes.
3. **Why can a graph lose for a pipeline that runs once?** Capture and instantiation cost more than the submission overhead saved.

## Numerical reference and its limits

The [CPU reference](../references/cuda-043_cpu.py) reproduces worked example 1 and prints `{'synthetic_break_even_replays': 20.0}`.

## Transfer review

Fixed-shape repeated inference may benefit, but validate shapes, memory addresses, dynamic operations and framework support before capture or replay.
