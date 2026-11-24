# cuda-032: explanatory solutions

## Mechanism review

A timeline shows when the CPU submits work, when copies and kernels execute, and where synchronization or idle gaps occur. Begin with the application's critical path before optimizing an individual instruction. NVTX ranges can name phases such as upload, transform and download, but annotations must match real code boundaries. Nsight Systems collection needs an explicitly prepared environment and appropriate permissions. A captured or synthetic trace remains useful for reasoning on a CPU-only machine, provided its provenance is clear. A timeline suggests a hypothesis; a controlled change tests whether that hypothesis improves the desired metric.

The separate [CPU reference](../references/cuda-032_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A synthetic request contains upload 3 ms, kernel 2 ms, download 3 ms and host processing 2 ms, sequentially. Halving the kernel saves only 1 ms, changing total time from 10 to 9 ms. Eliminating an unnecessary round trip could offer a larger opportunity if semantics permit data to stay resident.

**Approach:** Sum upload 3, kernel 2, download 3 and host 2 ms, then halve only the kernel.

**Why it is correct:** The phases are sequential, so the total drops from 10 ms to 9 ms.

**A plausible wrong approach:** Expecting halving the kernel to halve the request ignores the 8 ms outside it.

**How to verify:** The reference asserts total == 10 and optimized == 9.

## Exercise 2

A GPU sits idle for 6 ms between two 1 ms kernels while the host prepares data. Increasing the second kernel's occupancy does not remove that gap. Investigate host preparation, batching and dependencies, then measure the entire request again.

**Approach:** Attack the 6 ms host-preparation gap rather than the 1 ms kernels.

**Why it is correct:** The GPU waits on the host, so kernel speed does not limit this request.

**A plausible wrong approach:** Raising occupancy of the second kernel leaves the idle gap untouched.

**How to verify:** Measure the full request before and after a host-side change.

## Exercise 3

Label upload, kernel, download and host processing with their stated intervals and identify that all are sequential in this synthetic model.

**Approach:** Draw four sequential bars labeled with 3, 2, 3 and 2 ms.

**Why it is correct:** The labels show which phase dominates the 10 ms.

**A plausible wrong approach:** Drawing the kernel as overlapping transfers misstates this synthetic model.

**How to verify:** Confirm the bar lengths add to 10 ms.

## Exercise 4

Yes. Another critical-path dependency may dominate, and collection overhead or different work can mislead. Compare equal end-to-end contracts.

**Approach:** Yes; check the critical path and end-to-end time.

**Why it is correct:** Overlap off the critical path saves nothing if another dependency still waits.

**A plausible wrong approach:** Treating visual overlap as speedup skips measuring the request.

**How to verify:** Compare equal end-to-end runs with and without the overlap.

## Exercise 5

Initialization and JIT may create one-time gaps absent from steady state; both cold and warm behavior need truthful labels.

**Approach:** Label the first iteration as cold and report it separately from steady state.

**Why it is correct:** Initialization and JIT compilation happen once and inflate that iteration.

**A plausible wrong approach:** Averaging cold and warm runs together hides both behaviors.

**How to verify:** Show the first-iteration time next to the steady-state median.

## Exercise 6

Precompute the next bounded input before the dependent launch or batch preparation, preserving results, then compare the same timing scope and retained samples.

**Approach:** Prepare the next input on the host while the current kernel runs, then compare.

**Why it is correct:** Overlapping preparation with device work can shrink the 6 ms gap.

**A plausible wrong approach:** Changing several things at once makes any improvement impossible to attribute.

**How to verify:** Check results match and compare the same timing scope with retained samples.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-032_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Precompute the next bounded input before the dependent launch or batch preparation, preserving results, then compare the same timing scope and retained samples.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
