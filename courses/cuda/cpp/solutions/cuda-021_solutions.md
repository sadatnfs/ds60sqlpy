# cuda-021: explanatory solutions

## Mechanism review

An exclusive scan gives each item the reduction of preceding items; an inclusive scan includes the item itself. For stable compaction, map the selection predicate to zeros and ones, scan those flags, then let selected input i write to its exclusive prefix position. Stability means selected elements keep their relative order. Multiple blocks require scanning block totals and adding offsets in another stage. A total count says how much output is needed but does not assign every destination. Separate input and output or prove that aliasing cannot overwrite unread values.

The separate [CPU reference](../references/cuda-021_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For values \([8,3,6,1,4]\), select even values. Flags are \([1,0,1,0,1]\), exclusive positions are \([0,1,1,2,2]\), and selected writes produce \([8,6,4]\). Nonselected elements have positions too, but they do not write.

## Exercise 2

For flags \([0,0,0]\), the exclusive scan is \([0,0,0]\) and count is zero. For \([1,1,1]\), positions are \([0,1,2]\) and count is three. These cases catch allocating from the final exclusive prefix alone without adding the final flag.

## Exercise 3

Flags \([1,0,1,1]\), positions \([0,1,1,2]\), output \([5,7,8]\). The preserved order is part of the contract.

## Exercise 4

It excludes the last element. Count equals final prefix plus final flag for nonempty input.

## Exercise 5

Both are empty and count is zero; no last-element access is valid.

## Exercise 6

Exclusive offsets are \([0,2,2]\); append total five to obtain \([0,2,2,5]\), the row-boundary representation.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-021_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Exclusive offsets are \([0,2,2]\); append total five to obtain \([0,2,2,5]\), the row-boundary representation.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
