# cuda-035: explanatory solutions

## Mechanism review

Shared memory is organized into banks. Different lanes accessing different words in the same bank can serialize under the relevant hardware rules, while some same-address reads can broadcast. Global coalescing and shared-bank behavior are different layers. A transpose benefits from loading rows coalesced into a tile and storing columns through a coordinated layout. Padding can alter the bank mapping of columns, but it also changes storage usage and is not a universal speed rule. Use a simplified bank model to reason, then check the actual element width and architecture before treating the model as a performance prediction.

The separate [CPU reference](../references/cuda-035_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

In a simplified 32-bank, one-word-per-bank model, a column of a 32-word-wide tile maps every row to bank zero because (row*32) mod 32 is zero. With width 33, row r maps to bank r mod 32. This explains the common padding experiment without promising every architecture uses this exact cost model.

## Exercise 2

Transpose \([[1,2,3],[4,5,6]]\) into \([[1,4],[2,5],[3,6]]\). A tile implementation must preserve this rectangular mapping at edges. Padding is internal storage, so it must not appear as extra output rows or columns.

## Exercise 3

0,1,2,3. The modulo calculation changes because 33 mod 32 is one.

## Exercise 4

Restore correct coordinate predicates, tile ownership and output stride; an incorrect faster result is not an optimization.

## Exercise 5

No. It changes bank mapping and resource use, and some patterns already avoid conflicts or use broadcast.

## Exercise 6

Reassess bank width and multiword accesses on the selected architecture. Do not reuse the float32 one-word model unchanged.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-035_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Reassess bank width and multiword accesses on the selected architecture. Do not reuse the float32 one-word model unchanged.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
