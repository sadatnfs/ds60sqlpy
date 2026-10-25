# cuda-058: explanatory solutions

## Mechanism review

CUTLASS supplies composable matrix-operation building blocks, while CuTe provides abstractions for shapes, strides and layout composition used in tiled algorithms. An operation atom describes a small supported operation; larger tiles organize repeated work and data movement. Epilogues transform accumulated results, often adding scale, bias or activation. Templates encode choices at compile time, but they do not absolve the programmer from understanding coordinates, alignment, resource costs and architecture support. Pin dependencies and begin with a prepared supported example. A novel tile DSL is an elective comparison, not a universal prerequisite for basic CUDA.

The separate [CPU reference](../references/cuda-058_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A 2-by-3 logical tile with strides (3,1) maps coordinate (1,2) to offset five. A transposed view uses shape (3,2) and strides (1,3), mapping (2,1) to the same offset. Trace tiny layouts before interpreting a large template type.

## Exercise 2

An epilogue applies bias then ReLU to accumulated values \([-2,1,4]\) with bias one, producing \([0,2,5]\). Moving the bias after ReLU would produce \([1,2,5]\), changing semantics. A fused epilogue must match the reference order, type conversion and scaling contract.

## Exercise 3

Four. Shape controls valid coordinates; strides control physical mapping.

## Exercise 4

Runtime architecture and operation qualification, plus correct layout/alignment and library support. Compilation alone is not dispatch evidence.

## Exercise 5

Use a supported tail strategy or reject unsupported shapes explicitly; do not assume padded storage contains valid zeros.

## Exercise 6

When it expresses the required semantics and passes accuracy/performance tests while reducing maintenance; compare against the relevant library baseline first.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-058_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

When it expresses the required semantics and passes accuracy/performance tests while reducing maintenance; compare against the relevant library baseline first.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
