# cuda-062: explanatory solutions

## Mechanism review

Portability means defining what is supported and how unsupported situations behave. CUDA execution requires a supported NVIDIA device and host software path; a CPU-only classroom can still teach algorithms and validate CPU references. AMD, Intel and Apple GPU programming use different backends and APIs, not an automatic CUDA compatibility promise. Detect capability for the operation, not simply the operating-system name. Containers package user-space dependencies but share host driver and hardware constraints. MIG, MPS, device sharing and resets are operator-managed topics. A teaching worker must never silently reset a shared device or erase learner state to recover from a fault.

The separate [CPU reference](../references/cuda-062_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A dispatch policy offers CPU reference on every ordinary classroom and CUDA execution only after visibility, allocation and a small numerical probe succeed. It records which path actually ran. The same expected mathematical result does not make CPU output evidence of CUDA execution.

## Exercise 2

A model fits on one 24 GiB GPU but fails on an 8 GiB device. The container tag is identical; the resource contract is not. Reduce the bounded workload or choose a supported alternate path, preserving the original memory error and learner source.

## Exercise 3

Reading/CPU references remain available across the Docker classroom. NVIDIA execution needs a separately supported Linux or WSL path and hardware; Mac local CUDA is not promised.

## Exercise 4

Device presence, driver compatibility, feature support and memory vary independently of the OS.

## Exercise 5

Source, diagnostics, completed prior results and progress. Report unavailable execution without resetting unrelated hardware or volumes.

## Exercise 6

Keep its own API/runtime/capability labels and numerical oracle, teach conceptual correspondence, and do not present it as executing CUDA kernels.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-062_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Keep its own API/runtime/capability labels and numerical oracle, teach conceptual correspondence, and do not present it as executing CUDA kernels.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
