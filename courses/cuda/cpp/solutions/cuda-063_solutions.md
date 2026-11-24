# cuda-063: explanatory solutions

## Mechanism review

An independent numerical project begins with a bounded question, not a performance claim. Specify accepted input, output semantics, precision, resource budget and failure behavior. Build an independent CPU reference and adversarial fixtures before optimizing. Choose algorithms or libraries that fit the contract, then profile the complete pipeline. Retain evidence that another learner can reproduce: source, generation parameters, correctness comparisons, tool diagnostics where available and timing samples. A CPU-only project remains a valid algorithm/design portfolio piece when it clearly leaves GPU performance unmeasured.

The separate [CPU reference](../references/cuda-063_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Project A filters a synthetic signal with a fixed-zero stencil, computes an energy sum and returns both transformed values and the scalar. For \([2,4,8]\), the stencil reference is \([2,\frac{14}{3},4]\). The energy is the sum of squares, \(\frac{376}{9}\). Explicitly define whether energy is computed before or after filtering.

**Approach:** Apply the fixed-zero stencil to [2, 4, 8], then square and sum the filtered values with exact fractions.

**Why it is correct:** The middle value averages 2, 4 and 8 to 14/3, and edges average with zero, giving energy 376/9.

**A plausible wrong approach:** Computing energy on the unfiltered signal returns 84, a different quantity than the contract asks for.

**How to verify:** The reference asserts energy == Fraction(376, 9) and prints the exact filtered values.

## Exercise 2

Project B aggregates graph neighbors using CSR then normalizes nonempty rows. It includes isolated nodes, duplicate-edge policy and skewed row lengths. The project can choose a library sparse multiply or a custom kernel, but must compare identical semantics and include conversion costs when the graph arrives in another format.

**Approach:** Build CSR from edges, aggregate neighbors, then normalize only rows with nonzero degree.

**Why it is correct:** Isolated nodes have no neighbors, so skipping their normalization avoids dividing by zero.

**A plausible wrong approach:** Normalizing every row divides isolated rows by zero and spreads NaN.

**How to verify:** Include isolated nodes, duplicates and skewed rows, and compare against a host reference.

## Exercise 3

Fixed boundary policy, input dtype/length range, full filtered output, post-filter energy, error budget, memory bound and empty-input behavior.

**Approach:** State boundary policy, dtype and length range, full output, energy, error budget, memory bound and empty behavior.

**Why it is correct:** Each item defines what passing means.

**A plausible wrong approach:** Checking only the energy scalar lets filter errors cancel and pass.

**How to verify:** Write a test for each contract item.

## Exercise 4

If conversion is required per request, include it. If reused, state and measure the reuse contract explicitly.

**Approach:** Include graph conversion in timing if each request needs it.

**Why it is correct:** Conversion cost is part of end-to-end work when repeated.

**A plausible wrong approach:** Timing only the kernel overstates speedup.

**How to verify:** Time conversion plus kernel and report both.

## Exercise 5

Empty input, a singleton/boundary case and a ragged or skewed case; add extreme numeric values when the operation permits them.

**Approach:** Use empty input, a singleton or boundary case, and a skewed case.

**Why it is correct:** These expose edge and load-balance bugs.

**A plausible wrong approach:** Testing only typical sizes misses failures at edges.

**How to verify:** Add extreme values when the operation allows them.

## Exercise 6

Compare end-to-end benefit, accuracy, setup/maintenance cost and supported hardware. Keeping a CPU implementation can be the evidence-based result.

**Approach:** Compare end-to-end benefit, accuracy, setup and maintenance cost, and supported hardware.

**Why it is correct:** These decide whether the GPU path is worth it.

**A plausible wrong approach:** Deploying because the kernel is faster ignores total cost.

**How to verify:** Document the decision, including keeping the CPU path.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-063_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Compare end-to-end benefit, accuracy, setup/maintenance cost and supported hardware. Keeping a CPU implementation can be the evidence-based result.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
