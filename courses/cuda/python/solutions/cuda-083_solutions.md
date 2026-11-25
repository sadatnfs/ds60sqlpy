# cuda-083: explained solutions

Compare with your [worksheet](../lessons/cuda-083.md) attempt.

## Exercise 1: Specify the kernel signature

Name pointer element types and scalar widths.

**Approach.** Write the kernel signature in full: `x` is a pointer to `float32`, `y` is a pointer to `float32`, and `n` is a 32-bit signed integer, then make the Python launcher pass exactly those types, for example `numpy.int32(n)`.

**Why it is correct here.** Arguments cross the boundary as raw bytes laid out by the C ABI. The kernel reads 4 bytes for `n` and 8 bytes for each pointer, so the launcher must supply values of exactly those widths in that order.

**A plausible wrong approach.** Passing a plain Python `int` for `n` and letting the wrapper guess the width may package it as 64 bits. On some interfaces that shifts the following arguments or truncates the value.

**How to verify.** Compare the launcher's argument tuple against the declared signature, type by type. A small launch with `n = 5` must produce five correct outputs.

## Exercise 2: Count allocation bytes

Elements times itemsize.

**Approach.** Compute allocation bytes as elements times itemsize: five `float32` values need `5*4 = 20` bytes, while five `float64` values need 40.

**Why it is correct here.** The `validate_contract` helper in the reference rejects an allocation smaller than `count*itemsize`. The call with itemsize 8 and 20 bytes fails because 40 bytes are needed.

**A plausible wrong approach.** Sizing a buffer by element count alone, as if every element were one byte, under-allocates by the itemsize factor and lets the kernel write past the end.

**How to verify.** Run the reference: `validate_contract(5, 4, 20)` passes and `validate_contract(5, 8, 20)` raises. Add a negative count case and confirm it raises too.

## Exercise 3: Classify compile versus launch errors

Compile checks source while launch tests executable compatibility.

**Approach.** Classify errors by stage: a syntax error or unknown identifier fails at compilation, while a missing device, an unsupported architecture or an invalid launch configuration fails at load or launch time.

**Why it is correct here.** Compilation translates source for a target architecture and can succeed on a machine without that GPU. Launch requires a compatible device, driver and module, which are only checked when the kernel runs.

**A plausible wrong approach.** Reporting compile success as working code treats the first stage as the whole contract. A module built for one architecture may still fail to load on another.

**How to verify.** Record three separate fields: compiled, launched and output matched. Without a device, only the first can be filled in.

## Exercise 4: Design cleanup order

Wait for users then release resources.

**Approach.** Order cleanup so that every kernel and copy using a buffer has completed, for example by synchronizing the stream, before the buffer, the stream and the module are released.

**Why it is correct here.** Freeing memory while queued work still reads it lets the allocator hand those bytes to new work. Destroying a stream or unloading a module with pending work is also undefined.

**A plausible wrong approach.** Releasing resources in reverse creation order without waiting looks tidy, but order of creation says nothing about device completion.

**How to verify.** In a test, enqueue a long kernel, synchronize, then free, and check the output is intact. Code review should find a wait before each release.

## Exercise 5: Explain ABI mismatch

Wrong byte interpretation can corrupt arguments.

**Approach.** Explain ABI mismatch with the example from the lesson: a kernel expecting `float32*` and a 32-bit length receives a `float64` buffer and a pointer where the integer belongs.

**Why it is correct here.** The kernel reinterprets each 8-byte double as two 4-byte floats, producing garbage values, and reads part of a pointer as the length, which can be enormous.

**A plausible wrong approach.** Expecting a type error from the device is the mistake: device code has no runtime type information about its arguments.

**How to verify.** Validate dtype and argument types in Python before launch. A test passing a `float64` array must raise in the launcher, not produce numbers.

## Exercise 6: Define release-pinned evidence

Record component versions target architecture and exact source.

**Approach.** Define release evidence as the exact kernel source or its hash, the compiler and runtime versions, the target architecture flags, the driver version, and the GPU used for the run.

**Why it is correct here.** A kernel's behavior depends on how it was compiled and where it ran. Pinning those components lets someone reproduce or invalidate the result later.

**A plausible wrong approach.** Recording only the Python package version omits the toolkit, driver and architecture, which are the usual causes of cross-machine failures.

**How to verify.** Another engineer should rebuild from the recorded source and versions and get the same compiled-module hash.

## Self-check answers

1. **Why must compile success be recorded separately from launch success?** Code can compile for an architecture that the current device does not have, so it builds cleanly and still fails or misbehaves at launch.

2. **What does a launch need besides the compiled function?** Arguments in the correct binary layout, grid and block geometry and a stream, all matched to the function signature.

3. **Why use release-matched examples for CUDA Python?** Its components are versioned independently, so code copied from a moving development branch may use APIs your installed release does not have.

## Reference observation

Insufficient storage for five float64 values is rejected.

Asserted by `courses/cuda/python/references/cuda-083_cpu.py`.
