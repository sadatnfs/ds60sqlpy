# cuda-013: explanatory solutions

## Mechanism review

cudaMalloc requests a number of bytes and returns a device allocation handle through a pointer argument. For n float elements, calculate n*sizeof(float), checking multiplication bounds for externally supplied sizes. cudaMemcpy also takes bytes and an explicit direction in the simple runtime API. The input owner must remain alive until the transfer finishes, and the device output must remain allocated until its final consumer completes. Host-to-device transfer supplies input; device-to-host transfer produces an observable result. A pointer is not a container with a length field, so the surrounding program must preserve size and lifetime metadata.

The separate [CPU reference](../references/cuda-013_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Copy \([2,4,6,8]\) as float32. Four elements require 16 bytes. A request for four bytes copies only one float. Zero-initialized test data can hide that error, so use distinct nonzero entries and validate the entire result after the round trip.

## Exercise 2

Place sentinel values around a three-element target: \([-99,1,2,3,-99]\). Transform only positions 1 through 3 by doubling, expecting \([-99,2,4,6,-99]\). Guards reveal writes beyond the intended subrange, but they do not prove absence of every possible invalid read; sanitizers add a different check.

## Exercise 3

\(33\times 8 = 264\) bytes for ordinary eight-byte double representation; use sizeof(double) in actual C++ rather than a copied literal.

## Exercise 4

Distinct nonzero values across the entire range, plus full host comparison. A one-element or all-zero example may conceal the partial copy.

## Exercise 5

Return a valid empty result without allocation, copy or kernel launch; never dereference a missing data pointer.

## Exercise 6

Release every earlier owned allocation and preserve the original error. Do not read nonexistent output or report a successful numerical comparison.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-013_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Release every earlier owned allocation and preserve the original error. Do not read nonexistent output or report a successful numerical comparison.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
