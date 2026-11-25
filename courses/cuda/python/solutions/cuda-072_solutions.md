# cuda-072: explained solutions

Compare with your [worksheet](../lessons/cuda-072.md) attempt.

## Exercise 1: Order the evidence levels

Import, visibility, allocation, launch, completion and correctness.

**Approach.** Order the evidence as import, device visibility, allocation, kernel launch, completion and correctness, and record each as passed, failed or not attempted.

**Why it is correct here.** Each stage depends on the previous one: no allocation without a visible device, no launch without an allocation, no correctness check without completion. The reference lists the six stages in this order and finds the first failure with `next(...)`, so a later stage is never credited when an earlier one is missing.

**A plausible wrong approach.** Collapsing all stages into one boolean `gpu_ok` hides where a failure happened and makes a correctness failure look like a missing driver.

**How to verify.** Run the cuda-072 reference: it marks correctness false and asserts the first failed stage is `correctness`.

## Exercise 2: Classify missing device

Inspect explicit runtime exposure and host capability.

**Approach.** Classify a probe that imports CuPy but reports zero devices as a visibility failure, then check whether the runtime exposes devices and whether the host has an NVIDIA GPU.

**Why it is correct here.** Worked example 1 shows that import succeeded, so the Python package and its modules are present. The failure sits at the next stage, visibility, and allocation and launch were never reached, so they must be recorded as not attempted rather than failed.

**A plausible wrong approach.** Reinstalling CuPy treats the problem as a package issue when the package is fine; the missing piece is device exposure or hardware.

**How to verify.** Record import passed, visibility failed, allocation and later stages not attempted. Then check two independent facts: whether the container or process was started with the GPU exposed to it, and whether the host itself lists an NVIDIA device and a loaded driver.

## Exercise 3: Classify wrong output

Correctness failure after execution.

**Approach.** Classify a probe that launched, completed, and returned wrong values as a correctness failure after execution.

**Why it is correct here.** Worked example 2 describes exactly this. Launch and completion evidence are real and worth keeping, because they rule out driver and visibility problems, but readiness requires correct values, so the overall status is not ready and the investigation moves to the kernel or its inputs.

**A plausible wrong approach.** Reporting the probe as ready because the exit code was zero ignores the value check. A probe that prints wrong numbers and exits normally is worse than one that crashes, because nothing downstream notices.

**How to verify.** The reference sets correctness to False and asserts `failed == "correctness"`, while every earlier stage is True. A real probe should compare its output with a known host value, such as doubling `[1, 2, 3]` to `[2, 4, 6]`, and fail with the mismatched values printed.

## Exercise 4: Design fail-closed device selection

Require requested backend and visible device.

**Approach.** Make device selection fail closed: if the requested backend is CUDA and no visible device exists, raise an error instead of continuing on CPU.

**Why it is correct here.** A GPU-labeled result must come from a GPU. When the caller asked for CUDA, the only honest outcomes are a CUDA result or an error; failing closed keeps the label attached to the backend that actually ran.

**A plausible wrong approach.** Defaulting to CPU with a warning lets automated runs record a GPU pass for a CPU result.

**How to verify.** Run the selector on a CPU-only host requesting CUDA; it must raise. Run it requesting CPU explicitly; it must proceed with a CPU label.

## Exercise 5: Explain process restart after fatal device error

Discard unhealthy execution context.

**Approach.** After a fatal device error, end the process and start a fresh one rather than continuing to issue work in the same context.

**Why it is correct here.** Some CUDA errors, such as an illegal memory access inside a kernel, are sticky: the context stays in an error state and later calls in the same process keep failing or cannot be trusted. A new process gets a new context.

**A plausible wrong approach.** Catching the exception and retrying in the same process often fails again, and if it seems to succeed the evidence is suspect.

**How to verify.** Record the error, restart, rerun the probe stages, and require all six stages to pass in the new process.

## Exercise 6: Compare alternative backend labels

Name CUDA, ROCm, MPS or CPU truthfully.

**Approach.** Name the backend that ran: CUDA for NVIDIA, ROCm for AMD, MPS for Apple, or CPU, and never relabel one as another.

**Why it is correct here.** Each backend has its own runtime, operator coverage and numerical behavior. A result on Apple MPS or AMD ROCm can be correct and useful, but it is not evidence that the CUDA path works.

**A plausible wrong approach.** Calling any accelerator run a GPU pass loses which runtime produced it, so a CUDA requirement can be satisfied by an Apple run on paper.

**How to verify.** Check the device object's type string (for example `cuda:0` or `mps`) and record it beside every result.

## Self-check answers

1. **Why can a successful import not prove a device is usable?** Import only resolves the Python package. Device visibility, allocation, launch, completion and correctness are later claims that each need their own test.

2. **How do you classify an unsupported architecture binary versus an allocation failure?** The first is a build issue: the compiled code does not target the device. The second is a workload budget issue: the request exceeds the memory available to the job.

3. **Is MPS or ROCm a way to emulate CUDA?** No. They are separate accelerator backends with their own packages and supported operations, so their results must be labeled by name, not reported as CUDA evidence.

## Reference observation

Fixture fails at correctness, not readiness success.

Asserted by `courses/cuda/python/references/cuda-072_cpu.py`.
