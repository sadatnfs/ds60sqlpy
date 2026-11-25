# cuda-005: explanatory solutions

## Mechanism review

A shape says how many logical coordinates exist. A stride says how far to move in storage when a coordinate increases by one. A row-major two-dimensional float array with row stride s elements places coordinate (r,c) at element offset r*s+c, then multiplies by the element size to obtain a byte offset. Padded rows use s greater than their logical width. A view can change shape and strides while borrowing the same allocation. Copying an address does not extend the allocation's lifetime or create independent data. Device and host pointers also carry an accessibility contract beyond their printed numeric value.

## Exercise 1

Take a 2-by-3 float32 matrix with five stored elements per row. Coordinate (1,2) has element offset \(1\times 5+2=7\) and byte offset 28. The logical six values occupy a padded allocation of ten floats, or 40 bytes. Multiplying by logical width would read element 5 instead, a different location.

**Approach:** Compute element offset as row times stored stride plus column, 1 * 5 + 2 = 7, then multiply by 4 bytes.

**Why it is correct:** Rows advance by the allocation's stride of 5, not the logical width 3, so padding is skipped correctly.

**A plausible wrong approach:** Using the logical width gives 1 * 3 + 2 = 5, reading a padding slot or the wrong row's element.

**How to verify:** The reference asserts (1 * 5 + 2) * 4 == 28 and prints offset_bytes 28.

## Exercise 2

For contiguous \([[1,2,3],[4,5,6]]\), the row-major strides are (3,1) elements. A transposed view has shape (3,2) and strides (1,3). Coordinate (2,1) still refers to underlying element 5, value 6. There was no mandatory movement of bytes, and writing through the view can change the original owner.

**Approach:** Swap the shape to (3, 2) and the strides to (1, 3), then evaluate coordinate (2, 1) as 2 * 1 + 1 * 3.

**Why it is correct:** The view reuses the same six stored values, so offset 5 still holds value 6 with no copy.

**A plausible wrong approach:** Copying data into a new transposed buffer before every read wastes bandwidth and detaches writes from the owner.

**How to verify:** The reference rebuilds the view with storage[r + c * 3] and asserts [[1, 4], [2, 5], [3, 6]].

## Exercise 3

The element offset is \(2\times 8+3=19\); at eight bytes per element the offset is 152 bytes.

**Approach:** Evaluate 2 * 8 + 3 = 19 elements using the padded row stride 8, then multiply by 8 bytes for float64.

**Why it is correct:** Each float64 occupies 8 bytes, so element 19 begins 152 bytes after the allocation's base.

**A plausible wrong approach:** Using 4 bytes per element, a float32 habit, yields 76 bytes and lands mid-way through a different value.

**How to verify:** Check 19 * 8 == 152 and confirm 19 lies inside the row 2 range of 16 to 23.

## Exercise 4

Shape omits the stride contract. Pass actual strides or make and account for a contiguous copy before dispatch.

**Approach:** Pass the view's actual strides, (1, 3), alongside its shape, or produce a contiguous copy and account for that cost.

**Why it is correct:** Shape (3, 2) fits both a contiguous matrix and a transposed view, so only strides disambiguate addressing.

**A plausible wrong approach:** Assuming row-major from the shape reads element (0, 1) at offset 1, which holds value 2 instead of 4.

**How to verify:** Read a few coordinates through both assumptions and compare with the reference's transpose output.

## Exercise 5

Its column coordinate stays zero, but row steps still use the stored leading dimension. Width one does not imply adjacent row values.

**Approach:** Keep the column index fixed at zero and move between rows by the stored leading dimension.

**Why it is correct:** Padding means row r begins at r times the leading dimension, so values are not adjacent even with width one.

**A plausible wrong approach:** Treating the column as a dense vector and reading offsets 0, 1, 2 mixes values and padding.

**How to verify:** With a leading dimension of 4, confirm rows live at offsets 0, 4 and 8 and the gaps hold padding.

## Exercise 6

An x-only kernel reads separated x fields in records versus neighboring x values in a dedicated array. Include conversion and other consumers before choosing layout.

**Approach:** Compare the bytes read per useful x: a record layout strides over y, z and other fields, an x array is contiguous.

**Why it is correct:** Neighboring threads reading neighboring x values in a dedicated array combine into fewer memory transactions.

**A plausible wrong approach:** Switching layout for this kernel alone ignores other consumers that read whole particles and the conversion cost.

**How to verify:** Count bytes touched for 32 x reads under each layout and list every kernel that would need updated indexing.

## Self-check answers

1. **Give the element offset of (1,1) in a 2-by-3 float32 matrix with row stride 4.** 1 times 4 plus 1, which is element 5, or byte offset 20.
2. **Why must a kernel receive strides, not only a shape, for a view?** Without strides it assumes contiguous rows and reads the wrong storage locations for transposed or padded data.
3. **What risk does aliasing add when one buffer is both input and output?** A write can change a value that another thread still needs to read, so results depend on execution order.

## Numerical reference and its limits

The [CPU reference](../references/cuda-005_cpu.py) reproduces worked example 1 and prints `{'offset_bytes': 28, 'transpose_view_values': [[1, 4], [2, 5], [3, 6]]}`.

## Transfer review

An x-only kernel reads separated x fields in records versus neighboring x values in a dedicated array. Include conversion and other consumers before choosing layout.
