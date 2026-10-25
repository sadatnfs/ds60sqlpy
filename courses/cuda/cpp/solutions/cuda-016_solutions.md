# cuda-016: explanatory solutions

## Mechanism review

Storage spaces describe accessibility and lifetime as well as likely performance. Global allocations can hold data used by many kernels. Shared memory belongs to a block and lasts for that block's execution. Registers hold thread-local values, but a large local array or register pressure can place values in local memory backed by device memory. Constant storage is useful for certain read-only patterns, especially broadcast-like access, but it is not an automatic speedup for arbitrary divergent addresses. A compiler resource report helps explain implementation choices; source variable scope alone does not prove where every value resides.

The separate [CPU reference](../references/cuda-016_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

In a three-tap filter, the input and output images live in global allocations. A thread's running sum is a scalar candidate for a register. A cooperatively loaded tile belongs in shared memory. Three common coefficients may use read-only or constant storage. These are choices to validate, not declarations that force a faster program.

## Exercise 2

A per-thread temporary array with 1,024 floats needs 4,096 bytes per thread. At 128 threads that is 524,288 bytes of logical temporary data, before other resources. Calling it 'local' does not make it inexpensive. Reduce live working state or choose a different algorithm, then inspect compiler and runtime evidence.

## Exercise 3

Global allocation for the image, shared memory for cooperating block data, and a local scalar that the compiler may keep in a register.

## Exercise 4

The compiler can place local data in device-backed local memory or spill registers. Inspect generated resource information and measured behavior.

## Exercise 5

No. Ordinary block shared memory has block scope. Specialized cluster mechanisms have separate feature and synchronization contracts.

## Exercise 6

Compare whether neighboring lanes read the same entries or divergent entries, access frequency and update needs; measure against a suitable read-only/global alternative.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-016_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Compare whether neighboring lanes read the same entries or divergent entries, access frequency and update needs; measure against a suitable read-only/global alternative.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
