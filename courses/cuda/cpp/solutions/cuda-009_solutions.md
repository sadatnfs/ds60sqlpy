# cuda-009: explanatory solutions

## Mechanism review

A pointer identifies storage; a size defines the range your function may use. Pair them explicitly. A const input pointer prevents writes through that pointer, but it does not establish unique ownership or guarantee that another alias cannot modify storage. A vector owns contiguous elements and can lend its data pointer while it remains alive and does not reallocate. A device function cannot generally use an ordinary host vector object because its implementation, allocator and storage belong to the host environment. Use plain element buffers and explicit shape metadata at the boundary, with deliberate integer-width choices for address arithmetic.

The separate [CPU reference](../references/cuda-009_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A CPU affine transform accepts input, output, count, scale and bias. For input \([-1,0,2]\), scale 3 and bias 1, the result is \([-2,1,7]\). Reject mismatched ranges before indexing. If input and output overlap, either document in-place safety or reject that case; const alone does not answer it.

## Exercise 2

A function returning `vector<float>{1,2,3}.data()` returns a pointer to storage whose owner is destroyed at the end of the expression. The pointer value may still print, but dereferencing it is invalid. Return the owning vector, or pass caller-owned storage into the function. Keeping a numeric address does not keep an allocation alive.

## Exercise 3

Input pointer, row count, column count and leading dimension, plus an output buffer and capacity. State element type and accessibility.

## Exercise 4

Growth may reallocate, invalidating borrowed pointers. Reacquire pointers after changes and prevent outstanding consumers from using the old storage.

## Exercise 5

Return without dereferencing either pointer. Do not use an empty range as permission to form invalid pointer arithmetic.

## Exercise 6

A cast changes the C++ type, not allocation location, accessibility or ownership. Use a supported memory allocation and transfer contract.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-009_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

A cast changes the C++ type, not allocation location, accessibility or ownership. Use a supported memory allocation and transfer contract.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
