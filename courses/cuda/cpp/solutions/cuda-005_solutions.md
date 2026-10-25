# cuda-005: explanatory solutions

## Mechanism review

A shape says how many logical coordinates exist. A stride says how far to move in storage when a coordinate increases by one. A row-major two-dimensional float array with row stride s elements places coordinate (r,c) at element offset r*s+c, then multiplies by the element size to obtain a byte offset. Padded rows use s greater than their logical width. A view can change shape and strides while borrowing the same allocation. Copying an address does not extend the allocation's lifetime or create independent data. Device and host pointers also carry an accessibility contract beyond their printed numeric value.

The separate [CPU reference](../references/cuda-005_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Take a 2-by-3 float32 matrix with five stored elements per row. Coordinate (1,2) has element offset \(1\times 5+2=7\) and byte offset 28. The logical six values occupy a padded allocation of ten floats, or 40 bytes. Multiplying by logical width would read element 5 instead, a different location.

## Exercise 2

For contiguous \([[1,2,3],[4,5,6]]\), the row-major strides are (3,1) elements. A transposed view has shape (3,2) and strides (1,3). Coordinate (2,1) still refers to underlying element 5, value 6. There was no mandatory movement of bytes, and writing through the view can change the original owner.

## Exercise 3

The element offset is \(2\times 8+3=19\); at eight bytes per element the offset is 152 bytes.

## Exercise 4

Shape omits the stride contract. Pass actual strides or make and account for a contiguous copy before dispatch.

## Exercise 5

Its column coordinate stays zero, but row steps still use the stored leading dimension. Width one does not imply adjacent row values.

## Exercise 6

An x-only kernel reads separated x fields in records versus neighboring x values in a dedicated array. Include conversion and other consumers before choosing layout.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-005_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

An x-only kernel reads separated x fields in records versus neighboring x values in a dedicated array. Include conversion and other consumers before choosing layout.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
