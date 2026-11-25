# cuda-057: explanatory solutions

## Mechanism review

Thread-block clusters and tensor memory accelerator mechanisms expand cooperation and data movement on supported newer architectures. Distributed shared memory changes which participating blocks can access certain shared regions, but introduces cluster lifetime and synchronization requirements. TMA transfers use descriptors and completion protocols; they are not ordinary memcpy calls with a new name. Different instructions can require architecture-specific targets beyond a broad compute-capability family. Maintain a feature table for the exact operation, compiler and GPU, and retain a portable fallback. Learning the ownership diagram is useful without executing architecture-specific code.

## Exercise 1

A cluster-assisted histogram can combine partial bins across cooperating blocks before global output. Before a remote shared-memory read, the producing block's storage must be initialized and remain alive through the required cluster synchronization. A block exiting early can invalidate the assumed lifetime.

**Approach:** Each block writes partial histogram bins to its shared memory, the cluster synchronizes, then blocks read remote bins and merge them before one global write.

**Why it is correct:** The cluster barrier guarantees the producer's bins are written and its shared storage still exists when a neighbor reads it.

**A plausible wrong approach:** Reading a neighbor's distributed shared memory before the cluster sync, or after the producer block exits, reads uninitialized or freed storage.

**How to verify:** Compare merged bins against a host histogram of the same input, and run on supported hardware only; otherwise record the check as unavailable.

## Exercise 2

A feature table might mark baseline kernels available, cluster launch unavailable and a TMA experiment unqualified. Dispatch should choose the baseline, not attempt an unsupported instruction and silently label a CPU calculation as the specialized result. Feature detection is per operation, not a marketing-name comparison.

**Approach:** Consult the capability table and dispatch to the baseline kernel when cluster launch and TMA are not qualified.

**Why it is correct:** The baseline computes the same counts on any supported device, so choosing it keeps results correct.

**A plausible wrong approach:** Trying the cluster instruction and catching a failure, then labeling a CPU result as the cluster path, misreports what ran.

**How to verify:** The reference asserts selected == 'baseline' and prints specialized_execution_verified False.

## Exercise 3

Operation, exact target requirement, device properties, compiler/library versions, launch constraints and actual execution evidence.

**Approach:** Record operation, exact target requirement, device properties, compiler and library versions, launch limits and execution evidence.

**Why it is correct:** Each field narrows whether the feature actually applies to this device and build.

**A plausible wrong approach:** Recording only the GPU model name omits the compiler target and launch evidence that decide support.

**How to verify:** Have a second person reproduce dispatch from the record alone.

## Exercise 4

Feature families and architecture-specific variants have distinct contracts; names are not an executable compatibility check.

**Approach:** Check the specific feature and compile target rather than inferring support from the product name.

**Why it is correct:** Architecture-specific instructions belong to particular families and suffixed targets, not to every newer-sounding device.

**A plausible wrong approach:** Assuming a larger model number includes every earlier specialized instruction can produce code the device cannot load.

**How to verify:** Query compute capability and test the compiled target with a small probe kernel.

## Exercise 5

Nothing. The learner can complete the model and worksheet while the optional hardware evidence remains unavailable.

**Approach:** Leave reading progress unaffected and mark only the optional hardware evidence unavailable.

**Why it is correct:** The lesson's model and worksheet do not depend on cluster hardware.

**A plausible wrong approach:** Blocking completion until a cluster-capable GPU appears punishes learners for hardware they cannot control.

**How to verify:** Complete the lesson on a CPU-only machine and confirm progress records it.

## Exercise 6

Preserve input/bin/output semantics and return the same validated counts, while recording which implementation ran and comparing performance only within supported conditions.

**Approach:** Keep the same input, bin edges and output layout for both implementations, and log which one ran.

**Why it is correct:** Callers then get identical validated counts whichever path dispatch chooses.

**A plausible wrong approach:** Letting the fallback use different bin boundaries makes outputs differ silently between devices.

**How to verify:** Run both paths on the same input where supported and compare every bin.

## Self-check answers

1. **Name four fields of a capability record.** Device and compute capability, toolkit and driver versions, the feature probed and the probe result.
2. **What should an unavailable cluster feature do to reading progress?** Nothing; the lesson remains complete, and only the optional lab stays unqualified.
3. **When may a block read another block's distributed shared memory?** After the producer initialized it, within the required cluster synchronization, while that block is still alive.

## Numerical reference and its limits

The [CPU reference](../references/cuda-057_cpu.py) reproduces worked example 1 and prints `{'selected_implementation': 'baseline', 'specialized_execution_verified': False}`.

## Transfer review

Preserve input/bin/output semantics and return the same validated counts, while recording which implementation ran and comparing performance only within supported conditions.
