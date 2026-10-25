# cuda-061: explanatory solutions

## Mechanism review

A maintainable CUDA project separates interfaces, host orchestration and device implementation without hiding ownership. Host .cpp files compile as ordinary C++; .cu files contain CUDA compilation units; headers declare shared interfaces. Calls across device translation units can require separable compilation and device linking. CMake targets should state languages, dependencies and architecture policy explicitly. A project directory cannot be pasted into a single-source coding pad. Keep external project commands in an owned scratch directory with clear source and build paths, and validate both a clean build and actual execution on supported hardware.

The separate [CPU reference](../references/cuda-061_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A three-file design has include/transform.hpp declaring a host launch function, src/transform.cu defining its kernel and launch wrapper, and src/main.cpp building fixtures and validating output. The caller sees an ordinary host interface, while the implementation owns its CUDA dependencies.

## Exercise 2

An undefined host launch function usually means its object was not linked or its declaration/definition disagree. An unresolved device function in another .cu file concerns device compilation/linking. These failures occur before mathematical validation and require different build fixes.

## Exercise 3

Keep authored files in the project root/src/include and generated files under a separate build directory; never confuse generated binaries with maintained source.

## Exercise 4

Build flags are reviewed execution policy, not arbitrary learner-controlled manifest commands. A prepared project can document its own deliberate external build configuration.

## Exercise 5

Configuration generation only. Compilation, linking and runtime tests remain separate steps.

## Exercise 6

Keep CPU reference/unit tests, CUDA compile checks and actual device numerical/sanitizer tests distinct with explicit unavailable reasons.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-061_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Keep CPU reference/unit tests, CUDA compile checks and actual device numerical/sanitizer tests distinct with explicit unavailable reasons.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
