# cuda-057: explanatory solutions

## Mechanism review

Thread-block clusters and tensor memory accelerator mechanisms expand cooperation and data movement on supported newer architectures. Distributed shared memory changes which participating blocks can access certain shared regions, but introduces cluster lifetime and synchronization requirements. TMA transfers use descriptors and completion protocols; they are not ordinary memcpy calls with a new name. Different instructions can require architecture-specific targets beyond a broad compute-capability family. Maintain a feature table for the exact operation, compiler and GPU, and retain a portable fallback. Learning the ownership diagram is useful without executing architecture-specific code.

The separate [CPU reference](../references/cuda-057_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A cluster-assisted histogram can combine partial bins across cooperating blocks before global output. Before a remote shared-memory read, the producing block's storage must be initialized and remain alive through the required cluster synchronization. A block exiting early can invalidate the assumed lifetime.

## Exercise 2

A feature table might mark baseline kernels available, cluster launch unavailable and a TMA experiment unqualified. Dispatch should choose the baseline, not attempt an unsupported instruction and silently label a CPU calculation as the specialized result. Feature detection is per operation, not a marketing-name comparison.

## Exercise 3

Operation, exact target requirement, device properties, compiler/library versions, launch constraints and actual execution evidence.

## Exercise 4

Feature families and architecture-specific variants have distinct contracts; names are not an executable compatibility check.

## Exercise 5

Nothing. The learner can complete the model and worksheet while the optional hardware evidence remains unavailable.

## Exercise 6

Preserve input/bin/output semantics and return the same validated counts, while recording which implementation ran and comparing performance only within supported conditions.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-057_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Preserve input/bin/output semantics and return the same validated counts, while recording which implementation ran and comparing performance only within supported conditions.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
