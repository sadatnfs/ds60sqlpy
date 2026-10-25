# cuda-003: explanatory solutions

## Mechanism review

An application calls a runtime API or a higher-level library. User-space CUDA libraries then cooperate with the host NVIDIA driver to access a device. A container packages application code and user-space dependencies; it does not package a physical GPU or replace the host kernel driver. The toolkit includes tools such as the nvcc compiler. A framework wheel may bring compatible CUDA user-space components without a general-purpose CUDA compiler. Conversely, nvcc can exist on a machine where no GPU is visible. Each observation answers a different question: compilation, driver management access, framework device discovery, allocation and numerical execution are separate checks.

The separate [CPU reference](../references/cuda-003_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A shell reports `nvcc: command not found`, while an already installed framework executes a tensor operation on a GPU. This is possible because the framework can run precompiled kernels without the developer compiler. Building a new CUDA extension has a different dependency contract from running the existing tensor operator.

## Exercise 2

A container contains nvcc and compiles a program, but `cudaGetDeviceCount` reports no available device. Editing the kernel cannot repair absent hardware access. Inspect host support, driver and deliberate container GPU exposure. The compiler result remains valid compilation evidence; record execution as unavailable instead of silently presenting a CPU result as CUDA success.

## Exercise 3

Application calls runtime; runtime uses the kernel driver; the driver controls the GPU. Libraries and framework dispatch can add intermediate layers.

## Exercise 4

Preserve the exact allocation status and requested bytes. Check device visibility, compatibility and available memory rather than treating management visibility as a successful compute test.

## Exercise 5

The layer diagrams, diagnostic classification and CPU models. A Linux container on that Mac does not create an NVIDIA CUDA device.

## Exercise 6

Use 'CUDA compilation available; GPU execution not verified'. Keep hardware, driver access and actual allocation/execution observations separate.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-003_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Use 'CUDA compilation available; GPU execution not verified'. Keep hardware, driver access and actual allocation/execution observations separate.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
