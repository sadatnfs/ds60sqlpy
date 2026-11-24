# cuda-009: explanatory solutions

## Mechanism review

A pointer identifies storage; a size defines the range your function may use. Pair them explicitly. A const input pointer prevents writes through that pointer, but it does not establish unique ownership or guarantee that another alias cannot modify storage. A vector owns contiguous elements and can lend its data pointer while it remains alive and does not reallocate. A device function cannot generally use an ordinary host vector object because its implementation, allocator and storage belong to the host environment. Use plain element buffers and explicit shape metadata at the boundary, with deliberate integer-width choices for address arithmetic.

The separate [CPU reference](../references/cuda-009_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

A CPU affine transform accepts input, output, count, scale and bias. For input \([-1,0,2]\), scale 3 and bias 1, the result is \([-2,1,7]\). Reject mismatched ranges before indexing. If input and output overlap, either document in-place safety or reject that case; const alone does not answer it.

**Approach:** Validate that input and output lengths match the count, then compute 3 * x + 1 for each of [-1, 0, 2].

**Why it is correct:** Each output depends only on its own input, so the map is correct for any order of evaluation.

**A plausible wrong approach:** Assuming const on the input makes in-place calls safe ignores aliasing when output points to the same storage.

**How to verify:** The reference asserts the result equals [-2, 1, 7]; add an aliased call and state its documented policy.

## Exercise 2

A function returning `vector<float>{1,2,3}.data()` returns a pointer to storage whose owner is destroyed at the end of the expression. The pointer value may still print, but dereferencing it is invalid. Return the owning vector, or pass caller-owned storage into the function. Keeping a numeric address does not keep an allocation alive.

**Approach:** Return the owning vector by value or accept caller storage, never a pointer into a temporary.

**Why it is correct:** The temporary vector is destroyed at the end of the full expression, so its storage is released.

**A plausible wrong approach:** Printing the pointer to prove it is valid fails because a numeric address says nothing about lifetime.

**How to verify:** Build with address sanitizer on the host; the dangling read is reported as use after free.

## Exercise 3

Input pointer, row count, column count and leading dimension, plus an output buffer and capacity. State element type and accessibility.

**Approach:** List pointer, rows, columns, leading dimension, output pointer, output capacity, element type and memory space.

**Why it is correct:** The padded example stores 3 slots per row for 2 logical columns, so the leading dimension is required.

**A plausible wrong approach:** Passing only rows and columns makes row 1 start at offset 2, reading the padding value 99.

**How to verify:** The reference sums padded[r * 3 : r * 3 + 2] and asserts row sums [3, 7].

## Exercise 4

Growth may reallocate, invalidating borrowed pointers. Reacquire pointers after changes and prevent outstanding consumers from using the old storage.

**Approach:** Reacquire data() after any operation that can grow the vector and ensure no consumer still holds the old pointer.

**Why it is correct:** push_back beyond capacity reallocates and moves elements, invalidating every earlier pointer.

**A plausible wrong approach:** Calling reserve once and then appending past that capacity still reallocates and invalidates the pointer.

**How to verify:** Compare data() before and after growth past capacity and observe that the address changes.

## Exercise 5

Return without dereferencing either pointer. Do not use an empty range as permission to form invalid pointer arithmetic.

**Approach:** Return immediately when count is zero, before any pointer arithmetic or dereference.

**Why it is correct:** An empty range has no elements to transform, and its pointers may legitimately be null.

**A plausible wrong approach:** Computing input + count - 1 as a last element pointer creates an invalid pointer before input.

**How to verify:** Call the function with a null pointer and count zero and confirm it returns without error.

## Exercise 6

A cast changes the C++ type, not allocation location, accessibility or ownership. Use a supported memory allocation and transfer contract.

**Approach:** Allocate device memory through the runtime and copy host data into it with an explicit transfer.

**Why it is correct:** A reinterpret_cast changes only the static type; the bytes still live in host memory.

**A plausible wrong approach:** Casting a host float pointer to a device pointer type and launching causes an illegal address fault.

**How to verify:** Query the pointer's attributes through the runtime and confirm the memory type before launch.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-009_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

A cast changes the C++ type, not allocation location, accessibility or ownership. Use a supported memory allocation and transfer contract.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
