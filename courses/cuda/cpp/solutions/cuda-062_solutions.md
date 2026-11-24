# cuda-062: explanatory solutions

## Mechanism review

Portability means defining what is supported and how unsupported situations behave. CUDA execution requires a supported NVIDIA device and host software path; a CPU-only classroom can still teach algorithms and validate CPU references. AMD, Intel and Apple GPU programming use different backends and APIs, not an automatic CUDA compatibility promise. Detect capability for the operation, not simply the operating-system name. Containers package user-space dependencies but share host driver and hardware constraints. MIG, MPS, device sharing and resets are operator-managed topics. A teaching worker must never silently reset a shared device or erase learner state to recover from a fault.

The separate [CPU reference](../references/cuda-062_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A dispatch policy offers CPU reference on every ordinary classroom and CUDA execution only after visibility, allocation and a small numerical probe succeed. It records which path actually ran. The same expected mathematical result does not make CPU output evidence of CUDA execution.

**Approach:** Offer the CPU reference everywhere, and enable CUDA only after device visibility, allocation and a small numerical probe all succeed.

**Why it is correct:** The probe checks that the device actually computes correctly, and logging the chosen path records what really ran.

**A plausible wrong approach:** Reporting the CUDA path because the expected numbers matched hides that the CPU reference produced them.

**How to verify:** The reference asserts selected == 'CPU_reference' when the probe is False and prints CUDA_execution unavailable.

## Exercise 2

A model fits on one 24 GiB GPU but fails on an 8 GiB device. The container tag is identical; the resource contract is not. Reduce the bounded workload or choose a supported alternate path, preserving the original memory error and learner source.

**Approach:** Check the model's memory need against device memory and shrink the workload or choose another path.

**Why it is correct:** A model fitting 24 GiB does not fit 8 GiB regardless of container tag.

**A plausible wrong approach:** Assuming the same image guarantees the same resources hides the memory limit.

**How to verify:** Run on the smaller device and confirm the original memory error is preserved and reported.

## Exercise 3

Reading/CPU references remain available across the Docker classroom. NVIDIA execution needs a separately supported Linux or WSL path and hardware; Mac local CUDA is not promised.

**Approach:** List reading and CPU references as available everywhere, and NVIDIA execution only on supported Linux or WSL with hardware.

**Why it is correct:** Mac machines lack local CUDA support.

**A plausible wrong approach:** Promising Mac CUDA execution sets expectations the platform cannot meet.

**How to verify:** Check each row against the documented support matrix.

## Exercise 4

Device presence, driver compatibility, feature support and memory vary independently of the OS.

**Approach:** Probe device presence, driver, features and memory directly.

**Why it is correct:** These vary independently of the operating system.

**A plausible wrong approach:** Dispatching on OS name alone selects CUDA on Linux machines without GPUs.

**How to verify:** Run dispatch on a GPU-less Linux machine and confirm CPU is chosen.

## Exercise 5

Source, diagnostics, completed prior results and progress. Report unavailable execution without resetting unrelated hardware or volumes.

**Approach:** Keep source, diagnostics, prior results and progress, and report execution unavailable.

**Why it is correct:** Learners should not lose work because of a device fault.

**A plausible wrong approach:** Resetting hardware or volumes destroys unrelated state.

**How to verify:** Simulate a fault and confirm earlier results remain.

## Exercise 6

Keep its own API/runtime/capability labels and numerical oracle, teach conceptual correspondence, and do not present it as executing CUDA kernels.

**Approach:** Label the alternate backend's API, runtime and capabilities separately, with its own numerical oracle.

**Why it is correct:** Conceptual correspondence teaches ideas without claiming equivalence.

**A plausible wrong approach:** Presenting it as running CUDA kernels misleads learners.

**How to verify:** Check labels in output name the actual backend.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-062_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Keep its own API/runtime/capability labels and numerical oracle, teach conceptual correspondence, and do not present it as executing CUDA kernels.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
