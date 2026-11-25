# cuda-011: explanatory solutions

## Mechanism review

A .cu translation unit can contain ordinary host functions and CUDA device functions. nvcc coordinates separate compilation paths, invokes a supported host compiler and links the CUDA runtime. PTX is a virtual instruction representation; a cubin holds device machine code for a target architecture. An executable can package several device images in a fat binary. Loading may select a compatible image or invoke supported JIT compilation of PTX. This explains why source compilation, host linking, device loading and kernel execution can fail at different times. Header suffix .cuh is a convention, not an instruction that executes anything.

## Exercise 1

The manual lab command is `nvcc -std=c++17 -O2 -lineinfo main.cu -o main`. The input is main.cu; `-o main` names the executable. `./main` runs that file from the current directory. The toolkit's default target must support the actual device. A release build later needs deliberately selected architecture targets, not guessed values from a tutorial.

**Approach:** Read each part of the command: language standard, optimization, line info, input file and output name.

**Why it is correct:** Each flag maps to a stage; -lineinfo keeps source mapping for later profiling without debug slowdown.

**A plausible wrong approach:** Copying an -arch value from a tutorial can build code for a different architecture than the installed device.

**How to verify:** Run nvcc --version and the device query, then confirm the chosen target covers that compute capability.

## Exercise 2

A missing semicolon is a source diagnostic. An undefined host function is a host-link diagnostic. 'No kernel image is available for execution on the device' is a loading/target problem. Replacing arithmetic in the kernel is unlikely to solve the latter. Save the complete diagnostic and identify the stage before changing versions.

**Approach:** Classify each message by stage: compile, link or load, before changing anything.

**Why it is correct:** Each stage has different causes, so the stage determines whether to edit source, link inputs or targets.

**A plausible wrong approach:** Editing kernel arithmetic to fix 'no kernel image' changes code that never ran on the device.

**How to verify:** Save the full diagnostic text and confirm the fix targets the stage it names.

## Exercise 3

Source is authored C++/CUDA, PTX is virtual device instructions, and the executable contains host code plus packaged device code and link dependencies.

**Approach:** Describe each artifact by who produces it and what consumes it.

**Why it is correct:** Authors write .cu, the compiler emits PTX for a virtual architecture, the linker packages the executable.

**A plausible wrong approach:** Calling PTX machine code ignores that the driver may still translate it for the real device.

**How to verify:** Inspect a build's intermediate files and confirm where PTX and the final binary appear.

## Exercise 4

Compilation can happen without a visible GPU. Device loading, allocation, launch and returned-value validation remain separate steps.

**Approach:** List the runtime steps that compilation never exercises: loading, allocation, launch and validation.

**Why it is correct:** nvcc runs on hosts without GPUs, so a zero exit proves only translation and linking.

**A plausible wrong approach:** Reporting a GPU pass from a CI build job without a device claims execution that never occurred.

**How to verify:** Check the build log for a device query; if absent, record execution as not tested.

## Exercise 5

Nothing yet. The host did not start the program; inspect the exact file path and permissions before GPU diagnosis.

**Approach:** Inspect the file path and permission bits before considering the kernel.

**Why it is correct:** The operating system refused to start the process, so no host or device code ran.

**A plausible wrong approach:** Rebuilding with a different -arch cannot fix a missing execute permission.

**How to verify:** Run ls -l on the binary and confirm the execute bit after chmod.

## Exercise 6

Record toolkit and host compiler, target architectures/PTX policy, linked library versions, source revision and actual device runtime tests.

**Approach:** Record toolkit, host compiler, targets, PTX policy, libraries, revision and device test results.

**Why it is correct:** These fields determine which devices can load the binary and which source produced it.

**A plausible wrong approach:** Recording only the toolkit version leaves the supported architectures unknown.

**How to verify:** Compare the recorded targets with a fresh device's compute capability before deploying.

## Self-check answers

1. **What is the difference between PTX and a cubin?** PTX is a virtual instruction form that can be JIT compiled; a cubin is machine code for one target architecture.
2. **Which diagnostic class is an undefined host function?** A host link error, not a device or loading problem.
3. **What should a release record include for a CUDA binary?** Toolkit version, target architectures, host compiler, build flags and the commit, plus later runtime receipts per device.

## Numerical reference and its limits

The [CPU reference](../references/cuda-011_cpu.py) reproduces worked example 1 and prints `source -> host/device compilation -> link -> load -> execute -> validate`.

## Transfer review

Record toolkit and host compiler, target architectures/PTX policy, linked library versions, source revision and actual device runtime tests.
