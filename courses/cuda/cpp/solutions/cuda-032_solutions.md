# cuda-032: explanatory solutions

## Mechanism review

A timeline shows when the CPU submits work, when copies and kernels execute, and where synchronization or idle gaps occur. Begin with the application's critical path before optimizing an individual instruction. NVTX ranges can name phases such as upload, transform and download, but annotations must match real code boundaries. Nsight Systems collection needs an explicitly prepared environment and appropriate permissions. A captured or synthetic trace remains useful for reasoning on a CPU-only machine, provided its provenance is clear. A timeline suggests a hypothesis; a controlled change tests whether that hypothesis improves the desired metric.

The separate [CPU reference](../references/cuda-032_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A synthetic request contains upload 3 ms, kernel 2 ms, download 3 ms and host processing 2 ms, sequentially. Halving the kernel saves only 1 ms, changing total time from 10 to 9 ms. Eliminating an unnecessary round trip could offer a larger opportunity if semantics permit data to stay resident.

## Exercise 2

A GPU sits idle for 6 ms between two 1 ms kernels while the host prepares data. Increasing the second kernel's occupancy does not remove that gap. Investigate host preparation, batching and dependencies, then measure the entire request again.

## Exercise 3

Label upload, kernel, download and host processing with their stated intervals and identify that all are sequential in this synthetic model.

## Exercise 4

Yes. Another critical-path dependency may dominate, and collection overhead or different work can mislead. Compare equal end-to-end contracts.

## Exercise 5

Initialization and JIT may create one-time gaps absent from steady state; both cold and warm behavior need truthful labels.

## Exercise 6

Precompute the next bounded input before the dependent launch or batch preparation, preserving results, then compare the same timing scope and retained samples.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-032_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Precompute the next bounded input before the dependent launch or batch preparation, preserving results, then compare the same timing scope and retained samples.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
