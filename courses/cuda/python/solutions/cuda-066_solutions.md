# cuda-066: explained solutions

Compare with your [worksheet](../lessons/cuda-066.md) attempt.

## Exercise 1: Calculate offset (1,1)

Offset is 16 bytes in the original matrix.

**Approach.** Use the address formula with the original matrix strides `(12, 4)`: offset equals `1*12 + 1*4`. Row index 1 skips one 12-byte row, column index 1 skips one 4-byte float32.

**Why it is correct here.** The matrix is 2 by 3 float32 and row-major, so each row holds three 4-byte values and the row stride is 12 bytes. Element (1,1) is the fifth element in storage, and 4 elements times 4 bytes is 16.

**A plausible wrong approach.** Computing `1*3 + 1` and calling the answer 4 gives an element index, not a byte offset. Using the sliced view strides `(12, 8)` gives 20, which is the address of a different element in the original storage.

**How to verify.** Plug `(1, 1)` and `(12, 4)` into the reference `offset` function; it returns 16. The reference also checks that `(1, 1)` with the slice strides `(12, 8)` gives 20, showing why the stride tuple, not the shape, decides the answer.

## Exercise 2: Change dtype to float64

Element width and strides double.

**Approach.** Change the itemsize from 4 to 8 and recompute strides: a contiguous 2 by 3 float64 matrix has strides `(24, 8)`, so every byte offset doubles while logical coordinates stay the same.

**Why it is correct here.** Strides are byte displacements, and float64 uses 8 bytes per element. Element (1,2) moves from 20 to 40 bytes, and the allocation grows from 24 to 48 bytes, while the shape `(2, 3)` is unchanged.

**A plausible wrong approach.** Keeping strides `(12, 4)` and only relabeling the dtype reads half of each float64 as a float32. The element count matches, which is why the bug is easy to miss, but every value is garbage.

**How to verify.** Compute `offset((1, 2), (24, 8))` and confirm 40, double the reference 20. With NumPy, `np.zeros((2, 3), np.float64).strides` should print `(24, 8)`.

## Exercise 3: Describe a transposed view

Transpose exchanges shape axes and strides.

**Approach.** Describe the transpose of the 2 by 3 matrix as a view with shape `(3, 2)` and strides `(4, 12)`: the axes and their strides swap and no bytes move.

**Why it is correct here.** Moving one step along the new first axis walks to the next column of the original, which is 4 bytes away; moving along the new second axis walks to the next original row, 12 bytes away. The reference checks that `(2, 1)` with `(4, 12)` lands at byte 20, the same element as original `(1, 2)`.

**A plausible wrong approach.** Assuming the transpose is contiguous and indexing it with `row*2 + col` reads the original storage in the wrong order. A raw kernel given only the data pointer and new shape silently computes on the untransposed matrix.

**How to verify.** Run the reference and check the third assertion, `offset((2, 1), (4, 12)) == 20`. In NumPy, `a.T.strides` on a `(2, 3)` float32 array should print `(4, 12)` and `a.T.flags.c_contiguous` should be `False`.

## Exercise 4: Find the contiguous-only bug

Using row*width+col ignores actual strides.

**Approach.** Find the line that computes an index as `row*width + col` and replace it with `row*stride0 + col*stride1` (in elements or bytes), or reject non-contiguous input before launch.

**Why it is correct here.** That flat formula is only valid when the last stride equals itemsize and the row stride equals width times itemsize. The column slice in worked example 2 has strides `(12, 8)`, so the formula reads columns 0 and 1 instead of 0 and 2.

**A plausible wrong approach.** Fixing it by calling a reshape on the slice can hide the bug: reshape may copy, so the kernel becomes correct but writes go to a temporary and the original view never changes.

**How to verify.** Feed the slice `a[:, ::2]` to both a contiguous-only model and a stride-aware model on the 2 by 3 array `[[0,1,2],[3,4,5]]`. The stride-aware version must return `[[0,2],[3,5]]`; the buggy one returns `[[0,1],[2,3]]`.

## Exercise 5: Specify negative-stride support

Reject or implement negative strides explicitly.

**Approach.** Decide explicitly: either validate that every stride is positive and raise a clear error, or support negative strides by allowing the view base to point at the last element and adding signed offsets.

**Why it is correct here.** A reversed view such as `a[:, ::-1]` has a last stride of -4 for float32. The address formula still works with signed arithmetic, but only if the kernel uses signed index types and the base pointer includes the view offset.

**A plausible wrong approach.** Taking absolute values of strides makes indices non-negative and appears to work, but it reads the columns in the original order, so a reversed view returns unreversed data.

**How to verify.** For the 2 by 3 example, compute addresses for `a[:, ::-1]` with base offset 8 and strides `(12, -4)`; element (0,0) must be at byte 8 (value 2). A rejection policy is verified by a test asserting that a negative-stride input raises before launch.

## Exercise 6: Design layout contract tests

Include contiguous, sliced, transposed, empty and wrong dtype.

**Approach.** Write one test per layout class: contiguous `(2,3)`, the column slice with strides `(12,8)`, the transpose with `(4,12)`, an empty `(0,3)` array, and a float64 input that must be rejected or converted explicitly.

**Why it is correct here.** Each case breaks a different assumption. The slice breaks row times width indexing, the transpose breaks C-contiguity, the empty case tests the launch guard, and the float64 case tests dtype validation instead of byte reinterpretation.

**A plausible wrong approach.** Testing only random contiguous arrays of various sizes gives high coverage numbers but never exercises a non-unit stride, which is the exact contract this chapter is about.

**How to verify.** Each test compares the kernel or model output with a NumPy reference on the same view. The suite passes when all five cases agree, and the float64 case asserts a raised error or an explicit, counted conversion copy.

## Self-check answers

1. **What does a stride tell you that a shape does not?** The byte displacement for a one-step move along an axis. Two arrays with shape `(2, 2)` can address storage differently, as the column slice with strides `(12, 8)` shows.

2. **Why do logical bytes and storage span differ for the column slice?** The slice holds four float32 values, 16 logical bytes, but they are scattered across the original 24-byte allocation because every other column is skipped.

3. **Why is reinterpreting float64 bytes as float32 wrong even when element counts match?** Dtype decides both width and bit interpretation. Reading 8-byte doubles as 4-byte floats splits each value into two meaningless halves; a conversion must be an explicit cast.

## Reference observation

All three views address byte offset 20.

Asserted by `courses/cuda/python/references/cuda-066_cpu.py`.
