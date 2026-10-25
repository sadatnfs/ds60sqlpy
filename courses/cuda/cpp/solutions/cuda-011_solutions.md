# cuda-011: explanatory solutions

## Mechanism review

A .cu translation unit can contain ordinary host functions and CUDA device functions. nvcc coordinates separate compilation paths, invokes a supported host compiler and links the CUDA runtime. PTX is a virtual instruction representation; a cubin holds device machine code for a target architecture. An executable can package several device images in a fat binary. Loading may select a compatible image or invoke supported JIT compilation of PTX. This explains why source compilation, host linking, device loading and kernel execution can fail at different times. Header suffix .cuh is a convention, not an instruction that executes anything.

The separate [CPU reference](../references/cuda-011_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

The manual lab command is `nvcc -std=c++17 -O2 -lineinfo main.cu -o main`. The input is main.cu; `-o main` names the executable. `./main` runs that file from the current directory. The toolkit's default target must support the actual device. A release build later needs deliberately selected architecture targets, not guessed values from a tutorial.

## Exercise 2

A missing semicolon is a source diagnostic. An undefined host function is a host-link diagnostic. 'No kernel image is available for execution on the device' is a loading/target problem. Replacing arithmetic in the kernel is unlikely to solve the latter. Save the complete diagnostic and identify the stage before changing versions.

## Exercise 3

Source is authored C++/CUDA, PTX is virtual device instructions, and the executable contains host code plus packaged device code and link dependencies.

## Exercise 4

Compilation can happen without a visible GPU. Device loading, allocation, launch and returned-value validation remain separate steps.

## Exercise 5

Nothing yet. The host did not start the program; inspect the exact file path and permissions before GPU diagnosis.

## Exercise 6

Record toolkit and host compiler, target architectures/PTX policy, linked library versions, source revision and actual device runtime tests.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-011_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Record toolkit and host compiler, target architectures/PTX policy, linked library versions, source revision and actual device runtime tests.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
