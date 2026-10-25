# cuda-059: explanatory solutions

## Mechanism review

PTX is a virtual instruction language, while SASS describes machine instructions for a particular GPU architecture. The driver or toolchain can translate PTX differently across targets and versions. A fat binary can contain native device images and PTX fallback according to a deliberate policy. JIT can introduce cold-start cost and compatibility constraints. Inspect compiler resource reports and generated code to test a hypothesis, such as unexpected local-memory traffic, before attempting inline assembly. Counting PTX instructions does not directly count executed hardware operations or predict runtime.

The separate [CPU reference](../references/cuda-059_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A high-level multiply-plus-add may become a fused instruction depending on types, options and target. If generated code changes, retain the numerical test because one rounding differs from two. A shorter instruction sequence is useful evidence only in combination with the workload's actual behavior.

## Exercise 2

A per-thread array causes reported local-memory traffic. Reducing its live range may remove spills, but it can also add recomputation. Compare the compiler report, output and uninstrumented timing under the same target. Do not edit assembly until the source-level cause is understood.

## Exercise 3

A native image targets a hardware family; PTX requires a driver/toolchain path able to understand and compile that virtual version for the device.

## Exercise 4

Translation, instruction latency, memory behavior, parallel scheduling and repeated execution all intervene.

## Exercise 5

Revisit the supported architecture policy and toolchain, preserving a valid fallback; do not guess an architecture flag until the error disappears.

## Exercise 6

Measure first load/JIT separately from warmed execution with source/target/driver identities and unchanged correctness fixtures.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-059_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Measure first load/JIT separately from warmed execution with source/target/driver identities and unchanged correctness fixtures.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
