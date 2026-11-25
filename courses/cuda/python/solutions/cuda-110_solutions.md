# cuda-110: explained solutions

Compare with your [worksheet](../lessons/cuda-110.md) attempt.

## Exercise 1: List compatibility axes

Python framework compiler toolkit OS architecture and driver.

**Approach.** List compatibility axes for a custom operator: Python version, framework version and ABI, compiler, CUDA toolkit, operating system, host architecture, driver and device targets.

**Why it is correct here.** A compiled extension links against framework internals and CUDA runtime libraries. A mismatch on any axis can prevent loading or cause a failure at the first kernel launch.

**A plausible wrong approach.** Recording only the Python version suggests one wheel works everywhere that Python runs, while a framework ABI change alone can break the import.

**How to verify.** The reference asserts the manifest keys equal the required set and that `driver` is absent from the build ledger, since the driver belongs to the runtime environment.

## Exercise 2: Separate import and execution

Only real kernel work tests the device path.

**Approach.** Separate import from execution: importing proves the host shared library loaded, while only launching a real kernel on the device tests that compatible device code exists.

**Why it is correct here.** Device code is selected at the first launch. A package built without code for the device architecture imports cleanly and then fails with a no-kernel-image error.

**A plausible wrong approach.** Treating a successful import as proof of portability passes packages that cannot run any kernel on the target GPU.

**How to verify.** Add a smoke test that runs the operator on a small tensor on the device and compares with a CPU reference.

## Exercise 3: Explain native code versus intermediate code

Their portability rules differ.

**Approach.** Explain native device code versus intermediate code: native binaries for an architecture run only on compatible devices, while embedded PTX can be compiled by the driver for newer architectures.

**Why it is correct here.** Including PTX for the newest targeted architecture lets future GPUs load the kernel through driver compilation, at the cost of a first-launch delay.

**A plausible wrong approach.** Shipping native code only for the build machine's GPU makes the package fail on any older or newer architecture.

**How to verify.** Inspect the binary's embedded architectures with `cuobjdump --list-elf` and `--list-ptx` and compare with the declared device targets.

## Exercise 4: Design a build ledger

Record inputs versions hashes and flags in a reviewed recipe.

**Approach.** Design a build ledger that records source revision, toolkit and compiler versions, framework version, architecture flags and output hashes in a reviewed build recipe.

**Why it is correct here.** A ledger allows rebuilding the same artifact and explains why two builds differ. Hashes tie a distributed file to the recorded inputs.

**A plausible wrong approach.** Building from a developer machine without recording flags yields an artifact nobody can reproduce or audit.

**How to verify.** Rebuild from the ledger and compare the resulting hash, or explain any difference by a recorded input change.

## Exercise 5: Test unsupported dtype

Reject with a clear contract error.

**Approach.** Test an unsupported dtype, such as float64 for an operator implemented only for float32, and require a clear contract error before any kernel launch.

**Why it is correct here.** Passing unsupported types to a kernel can reinterpret bytes as the wrong type and return plausible but wrong numbers.

**A plausible wrong approach.** Silently casting to float32 hides precision loss and gives callers a different result from what they requested.

**How to verify.** Call the operator with float64 and assert the error message names the supported types.

## Exercise 6: Define a package release gate

Require functional tests in every declared supported environment.

**Approach.** Define a release gate requiring functional tests in every declared supported environment, so each combination of framework, toolkit and device target in the matrix runs the smoke and correctness tests.

**Why it is correct here.** The compatibility matrix is a claim, and only tests in each environment support it. A gate stops a release with untested combinations.

**A plausible wrong approach.** Testing one environment and declaring the whole matrix supported presents untested claims as verified.

**How to verify.** Store test results per environment with the release and reject it if any declared row lacks a passing result.

## Self-check answers

1. **Why does a wheel filename not guarantee GPU support?** It encodes Python and platform tags, not every device architecture the embedded code was compiled for.

2. **When can intermediate device code help portability?** It can be compiled by a driver for a newer device, but only within the documented compatibility rules.

3. **Is publishing a package part of this lesson's workflow?** No. Publishing or using external registries is a separately authorized workflow, kept apart from classroom reading.

## Reference observation

Build ledger completeness does not establish runtime driver or GPU acceptance.

Asserted by `courses/cuda/python/references/cuda-110_cpu.py`.
