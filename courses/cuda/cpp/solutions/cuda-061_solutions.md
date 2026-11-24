# cuda-061: explanatory solutions

## Mechanism review

A maintainable CUDA project separates interfaces, host orchestration and device implementation without hiding ownership. Host .cpp files compile as ordinary C++; .cu files contain CUDA compilation units; headers declare shared interfaces. Calls across device translation units can require separable compilation and device linking. CMake targets should state languages, dependencies and architecture policy explicitly. A project directory cannot be pasted into a single-source coding pad. Keep external project commands in an owned scratch directory with clear source and build paths, and validate both a clean build and actual execution on supported hardware.

The separate [CPU reference](../references/cuda-061_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A three-file design has include/transform.hpp declaring a host launch function, src/transform.cu defining its kernel and launch wrapper, and src/main.cpp building fixtures and validating output. The caller sees an ordinary host interface, while the implementation owns its CUDA dependencies.

**Approach:** Declare the host launch function in include/transform.hpp, define kernel and launcher in src/transform.cu, and validate fixtures in src/main.cpp.

**Why it is correct:** main.cpp sees only an ordinary host function, so it compiles with a host compiler and never touches kernel syntax.

**A plausible wrong approach:** Putting the kernel declaration with triple-angle launch syntax in the header forces every includer to be compiled by nvcc.

**How to verify:** The reference asserts the four-entry project layout; also build and confirm main.cpp compiles as plain C++.

## Exercise 2

An undefined host launch function usually means its object was not linked or its declaration/definition disagree. An unresolved device function in another .cu file concerns device compilation/linking. These failures occur before mathematical validation and require different build fixes.

**Approach:** Check that the object defining the launcher is linked and that declaration and definition signatures match.

**Why it is correct:** An undefined host symbol is a link problem, separate from device-code linking errors.

**A plausible wrong approach:** Rewriting kernel math to fix a link error changes code that was never the cause.

**How to verify:** Run the linker with verbose output and confirm the symbol resolves.

## Exercise 3

Keep authored files in the project root/src/include and generated files under a separate build directory; never confuse generated binaries with maintained source.

**Approach:** Keep sources in src and include, and put generated files in a separate build directory.

**Why it is correct:** Separating them prevents committing or editing generated binaries.

**A plausible wrong approach:** Building in the source tree mixes artifacts with maintained files.

**How to verify:** Delete the build directory and confirm a clean rebuild works.

## Exercise 4

Build flags are reviewed execution policy, not arbitrary learner-controlled manifest commands. A prepared project can document its own deliberate external build configuration.

**Approach:** Set architecture targets in the reviewed build configuration, not from lesson metadata arguments.

**Why it is correct:** Build flags are execution policy that should be reviewed.

**A plausible wrong approach:** Accepting flags from learner-controlled manifests lets arbitrary commands into builds.

**How to verify:** Confirm the build ignores architecture flags supplied in metadata.

## Exercise 5

Configuration generation only. Compilation, linking and runtime tests remain separate steps.

**Approach:** Treat a successful configure as proof that generation worked, then run build and tests.

**Why it is correct:** Configuring does not compile or link anything.

**A plausible wrong approach:** Calling the project working after configure skips compile errors.

**How to verify:** Run the build and tests after configure and check each status.

## Exercise 6

Keep CPU reference/unit tests, CUDA compile checks and actual device numerical/sanitizer tests distinct with explicit unavailable reasons.

**Approach:** Separate CPU reference tests, CUDA compile checks and device numerical and sanitizer tests.

**Why it is correct:** Each runs in different environments with different requirements.

**A plausible wrong approach:** Combining them means a missing GPU fails every test.

**How to verify:** Run on a CPU-only machine and confirm device tests report unavailable.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-061_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Keep CPU reference/unit tests, CUDA compile checks and actual device numerical/sanitizer tests distinct with explicit unavailable reasons.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
