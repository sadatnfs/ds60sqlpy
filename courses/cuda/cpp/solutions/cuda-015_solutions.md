# cuda-015: explanatory solutions

## Mechanism review

A dim3 value holds three dimensions, though an image often uses only x and y. Map x to a column and y to a row, then calculate storage using the row stride. Logical width and stored leading dimension are different quantities. The grid must cover both axes, and each thread predicates both coordinate bounds before accessing storage. This is especially important for rectangular images because square examples can conceal a swapped width and height. If an allocation uses a byte pitch, convert coordinates using that byte quantity deliberately rather than treating it as an element stride.

The separate [CPU reference](../references/cuda-015_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Take a width-3, height-2 image stored as \([1,2,3,99,4,5,6,99]\) with stride four. Add ten to each real pixel. The expected storage is \([11,12,13,99,14,15,16,99]\). Both padding sentinels stay 99. Coordinate (1,2) means row one, column two, stored at index six.

**Approach:** For each row and column add ten at row * 4 + col, leaving column 3 alone.

**Why it is correct:** Stride four skips the padding slot in each row, so indices 3 and 7 are never touched.

**A plausible wrong approach:** Looping over all eight storage slots adds ten to the 99 sentinels too.

**How to verify:** The reference asserts the image equals [11, 12, 13, 99, 14, 15, 16, 99].

## Exercise 2

A 4-by-2 thread block covers a 3-by-2 image with two unused x positions, one in each row. If the image becomes 2-by-3, grid height must also grow. Checking only the flattened offset can accidentally accept a logically invalid column that lands in the next row.

**Approach:** Predicate x < width and y < height separately before forming any flat offset.

**Why it is correct:** Per-axis checks reject column 3 even though offset 3 lies inside the padded allocation.

**A plausible wrong approach:** Checking only offset < stride * height accepts x = 3, which writes the padding slot.

**How to verify:** Swap the image to 2-by-3 and confirm grid height increases and every pixel is covered.

## Exercise 3

Ceiling division gives grid x=3 and y=3. Predicate each coordinate because both axes have tails.

**Approach:** Compute ceil(17 / 8) = 3 and ceil(9 / 4) = 3 for grid x and y.

**Why it is correct:** Three blocks of 8 cover 24 columns and three blocks of 4 cover 12 rows, enough for both axes.

**A plausible wrong approach:** Using floor division gives 2 by 2 and misses column 16 and row 8.

**How to verify:** Count covered pixels with predicates and expect 17 * 9 = 153.

## Exercise 4

An invalid x value may map inside the allocation or into another row. Storage capacity is not the same as logical image validity.

**Approach:** Check coordinates before flattening so invalid x never becomes a storage index.

**Why it is correct:** Flattening x = 3 in a width-3, stride-4 image hits padding, and larger x reaches the next row.

**A plausible wrong approach:** Relying on the allocation size as the bound treats padding as valid pixels.

**How to verify:** Write a test with an extra column of threads and confirm the padding stays 99.

## Exercise 5

Produce an empty logical image and skip launch; retain a clear contract for output shape and storage ownership.

**Approach:** Return an empty image with defined shape and stride and skip the launch.

**Why it is correct:** Width zero means no pixels exist, so nothing should be read or written.

**A plausible wrong approach:** Launching ceil(0 / 8) = 0 blocks in x yields an invalid configuration error.

**How to verify:** Call the transform with width zero and confirm no launch and an empty result.

## Exercise 6

Add a channel dimension or multiply pixel offsets by three, preserving row stride and channel bounds. Document whether stride counts bytes, elements or pixels.

**Approach:** Add a channel index and compute row * stride + col * 3 + channel, bounding channel below 3.

**Why it is correct:** Interleaved pixels store three values per column, so the column step becomes three elements.

**A plausible wrong approach:** Treating stride as pixels when it counts elements misplaces every row after the first.

**How to verify:** Transform a 2-by-2 RGB fixture and confirm each channel changes once and padding stays fixed.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-015_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Add a channel dimension or multiply pixel offsets by three, preserving row stride and channel bounds. Document whether stride counts bytes, elements or pixels.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
