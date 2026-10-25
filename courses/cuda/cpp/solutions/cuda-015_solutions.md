# cuda-015: explanatory solutions

## Mechanism review

A dim3 value holds three dimensions, though an image often uses only x and y. Map x to a column and y to a row, then calculate storage using the row stride. Logical width and stored leading dimension are different quantities. The grid must cover both axes, and each thread predicates both coordinate bounds before accessing storage. This is especially important for rectangular images because square examples can conceal a swapped width and height. If an allocation uses a byte pitch, convert coordinates using that byte quantity deliberately rather than treating it as an element stride.

The separate [CPU reference](../references/cuda-015_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Take a width-3, height-2 image stored as \([1,2,3,99,4,5,6,99]\) with stride four. Add ten to each real pixel. The expected storage is \([11,12,13,99,14,15,16,99]\). Both padding sentinels stay 99. Coordinate (1,2) means row one, column two, stored at index six.

## Exercise 2

A 4-by-2 thread block covers a 3-by-2 image with two unused x positions, one in each row. If the image becomes 2-by-3, grid height must also grow. Checking only the flattened offset can accidentally accept a logically invalid column that lands in the next row.

## Exercise 3

Ceiling division gives grid x=3 and y=3. Predicate each coordinate because both axes have tails.

## Exercise 4

An invalid x value may map inside the allocation or into another row. Storage capacity is not the same as logical image validity.

## Exercise 5

Produce an empty logical image and skip launch; retain a clear contract for output shape and storage ownership.

## Exercise 6

Add a channel dimension or multiply pixel offsets by three, preserving row stride and channel bounds. Document whether stride counts bytes, elements or pixels.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-015_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Add a channel dimension or multiply pixel offsets by three, preserving row stride and channel bounds. Document whether stride counts bytes, elements or pixels.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
