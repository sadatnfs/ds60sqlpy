# cuda-003: explanatory solutions

## Mechanism review

An application calls a runtime API or a higher-level library. User-space CUDA libraries then cooperate with the host NVIDIA driver to access a device. A container packages application code and user-space dependencies; it does not package a physical GPU or replace the host kernel driver. The toolkit includes tools such as the nvcc compiler. A framework wheel may bring compatible CUDA user-space components without a general-purpose CUDA compiler. Conversely, nvcc can exist on a machine where no GPU is visible. Each observation answers a different question: compilation, driver management access, framework device discovery, allocation and numerical execution are separate checks.

The separate [CPU reference](../references/cuda-003_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A shell reports `nvcc: command not found`, while an already installed framework executes a tensor operation on a GPU. This is possible because the framework can run precompiled kernels without the developer compiler. Building a new CUDA extension has a different dependency contract from running the existing tensor operator.

**Approach:** Separate two capabilities: running prebuilt framework kernels, which needs a driver and runtime libraries, and compiling new kernels, which needs nvcc.

**Why it is correct:** Framework wheels ship compiled device code and runtime libraries, so a tensor operation can execute on a machine with no compiler installed.

**A plausible wrong approach:** Concluding the GPU is broken because nvcc is missing confuses the compile dependency with the execute dependency.

**How to verify:** Run the existing tensor operation and record its device, then separately attempt an extension build and record the missing compiler.

## Exercise 2

A container contains nvcc and compiles a program, but `cudaGetDeviceCount` reports no available device. Editing the kernel cannot repair absent hardware access. Inspect host support, driver and deliberate container GPU exposure. The compiler result remains valid compilation evidence; record execution as unavailable instead of silently presenting a CPU result as CUDA success.

**Approach:** Record the successful compilation as build evidence, then diagnose device visibility from the zero device count before touching any source.

**Why it is correct:** cudaGetDeviceCount returning no devices depends on host driver and container exposure, which no change to kernel code can alter.

**A plausible wrong approach:** Rewriting the kernel or adding a CPU fallback that prints success hides the missing hardware and produces a false GPU claim.

**How to verify:** Check host driver presence and the container's GPU exposure flags; device count must become nonzero before execution evidence exists.

## Exercise 3

Application calls runtime; runtime uses the kernel driver; the driver controls the GPU. Libraries and framework dispatch can add intermediate layers.

**Approach:** Order calls from the top: application code calls the runtime, the runtime calls into the kernel driver, and the driver controls the device.

**Why it is correct:** Each layer only talks to its neighbor, so a missing driver blocks the runtime regardless of how correct the application is.

**A plausible wrong approach:** Placing the runtime below the driver suggests the runtime can reach hardware directly, which would make driver diagnostics pointless.

**How to verify:** Draw the stack and annotate where a framework dispatch layer inserts itself between the application and the runtime.

## Exercise 4

Preserve the exact allocation status and requested bytes. Check device visibility, compatibility and available memory rather than treating management visibility as a successful compute test.

**Approach:** Capture the allocation's error code and byte request, then check visible devices, driver and runtime compatibility, and free memory.

**Why it is correct:** A management tool can list a device without proving the compute context can allocate, so the failing call holds the evidence.

**A plausible wrong approach:** Retrying the allocation in a loop without reading its status discards the error and can mask an out-of-memory condition.

**How to verify:** Retry with a small, known-safe request; success narrows the cause to size or pressure, failure points to compatibility.

## Exercise 5

The layer diagrams, diagnostic classification and CPU models. A Linux container on that Mac does not create an NVIDIA CUDA device.

**Approach:** Complete layer diagrams, classify the diagnostic scenarios and run the CPU models, labeling all of it as reading or CPU evidence.

**Why it is correct:** Apple hardware has no NVIDIA device, so no container or virtual machine on it can expose a CUDA device.

**A plausible wrong approach:** Assuming Docker on the Mac passes a GPU through treats container packaging as hardware access, which it never provides.

**How to verify:** Run the CPU reference and confirm it prints the compilation-only message rather than any device result.

## Exercise 6

Use 'CUDA compilation available; GPU execution not verified'. Keep hardware, driver access and actual allocation/execution observations separate.

**Approach:** Write a label that states what was observed, compilation, and what was not observed, execution, in separate explicit fields.

**Why it is correct:** A build-only machine can produce binaries yet has never allocated or launched, so execution remains unverified by construction.

**A plausible wrong approach:** Labeling the machine CUDA-ready merges two claims and lets a reader assume kernels have produced validated results there.

**How to verify:** The reference asserts compiler is true and kernel_validated is false; the label must keep those values distinguishable.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-003_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Use 'CUDA compilation available; GPU execution not verified'. Keep hardware, driver access and actual allocation/execution observations separate.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
