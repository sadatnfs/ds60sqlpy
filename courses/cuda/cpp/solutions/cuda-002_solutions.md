# cuda-002: explanatory solutions

## Mechanism review

An SM, or streaming multiprocessor, schedules groups of GPU threads and owns finite execution and storage resources. A block is a cooperating group in your program; it is not a physical processor. Blocks can wait for resources and need not run in index order. Within a block, threads are organized into warps, normally 32 threads in CUDA. A warp issues instructions with a set of participating lanes. Registers hold per-thread working values, shared memory supports block cooperation, and device DRAM holds larger arrays. Copy engines may transfer data while computation proceeds, but concurrency depends on hardware and dependencies. Compute capability identifies a hardware feature family; toolkit version identifies software.

The separate [CPU reference](../references/cuda-002_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Draw four SM boxes and a grid of ten blocks. Under the deliberately simplified assumption of one resident block per SM, the grid needs at least three waves: four, four and two blocks. This is an occupancy illustration, not a runtime prediction. Real residency depends on registers, shared memory, threads and architectural limits.

## Exercise 2

A block with 100 threads occupies four warps. The last warp contains four valid program threads and 28 unused lane positions. A kernel with 100 blocks does not require 10,000 physical arithmetic units. Scheduling reuses execution resources over time. Do not build a dependency that assumes block 0 finishes first.

## Exercise 3

Ceiling division by 32 yields one, one and two warps. The second warp in the last case has one program thread.

## Exercise 4

Record device model and compute capability from device properties separately from compiler/toolkit, driver and framework versions.

## Exercise 5

Yes. The drawing ignores resource pressure, uneven duration and scheduling effects; it establishes a simplified lower bound only.

## Exercise 6

Data starts in host storage, is transferred to device allocation, and loads feed SM registers or shared memory. Returned output needs an explicit or framework-managed dependency and transfer.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-002_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Data starts in host storage, is transferred to device allocation, and loads feed SM registers or shared memory. Returned output needs an explicit or framework-managed dependency and transfer.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
