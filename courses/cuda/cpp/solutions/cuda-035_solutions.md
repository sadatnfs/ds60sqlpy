# cuda-035: explanatory solutions

## Mechanism review

Shared memory is organized into banks. Different lanes accessing different words in the same bank can serialize under the relevant hardware rules, while some same-address reads can broadcast. Global coalescing and shared-bank behavior are different layers. A transpose benefits from loading rows coalesced into a tile and storing columns through a coordinated layout. Padding can alter the bank mapping of columns, but it also changes storage usage and is not a universal speed rule. Use a simplified bank model to reason, then check the actual element width and architecture before treating the model as a performance prediction.

## Exercise 1

In a simplified 32-bank, one-word-per-bank model, a column of a 32-word-wide tile maps every row to bank zero because (row*32) mod 32 is zero. With width 33, row r maps to bank r mod 32. This explains the common padding experiment without promising every architecture uses this exact cost model.

**Approach:** Compute bank = (row * width) mod 32 for column reads of a tile with width 32, then repeat with width 33.

**Why it is correct:** With width 32 every row lands in bank 0, while width 33 shifts each row by one bank, so 32 rows hit 32 distinct banks.

**A plausible wrong approach:** Padding by 32 extra words instead of one leaves (row * 64) mod 32 at zero, keeping every access in bank 0.

**How to verify:** The reference asserts one unique bank for the plain layout and 32 unique banks for the padded layout.

## Exercise 2

Transpose \([[1,2,3],[4,5,6]]\) into \([[1,4],[2,5],[3,6]]\). A tile implementation must preserve this rectangular mapping at edges. Padding is internal storage, so it must not appear as extra output rows or columns.

**Approach:** Map input (r, c) to output (c, r) for the 2-by-3 matrix and guard each axis of the tile separately.

**Why it is correct:** Output row c collects column c of the input, giving [[1, 4], [2, 5], [3, 6]] with three rows of two.

**A plausible wrong approach:** Copying the padded 33-wide tile row straight to output writes the padding column as an extra value.

**How to verify:** The reference asserts list(map(list, zip(*matrix))) == [[1, 4], [2, 5], [3, 6]]; compare shapes as well as values.

## Exercise 3

0,1,2,3. The modulo calculation changes because 33 mod 32 is one.

**Approach:** Evaluate (row * 33) mod 32 for rows 0, 1, 2 and 3.

**Why it is correct:** 33 mod 32 is 1, so the bank equals the row number for the first 32 rows.

**A plausible wrong approach:** Reusing the width-32 result of bank 0 for every row ignores the extra padding word.

**How to verify:** Compute [(r * 33) % 32 for r in range(4)] and expect [0, 1, 2, 3].

## Exercise 4

Restore correct coordinate predicates, tile ownership and output stride; an incorrect faster result is not an optimization.

**Approach:** Fix the width-17 output first by restoring per-axis predicates, ownership and output stride.

**Why it is correct:** 17 leaves a partial tile in each direction, which is where swapped predicates appear.

**A plausible wrong approach:** Keeping the padded kernel because it is faster on aligned sizes ships wrong results for width 17.

**How to verify:** Compare every element of a 17-by-17 and a 17-by-5 transpose with the host reference.

## Exercise 5

No. It changes bank mapping and resource use, and some patterns already avoid conflicts or use broadcast.

**Approach:** Check whether the access already avoids conflicts or broadcasts before adding padding.

**Why it is correct:** Row-wise reads with consecutive lanes already map to distinct banks without help.

**A plausible wrong approach:** Padding every shared array by default wastes shared capacity and can reduce resident blocks.

**How to verify:** Compute bank indices for the actual pattern and measure both versions.

## Exercise 6

Reassess bank width and multiword accesses on the selected architecture. Do not reuse the float32 one-word model unchanged.

**Approach:** Recheck bank width and multiword access rules for doubles on the target architecture.

**Why it is correct:** An eight-byte element covers two four-byte words, so the mapping per lane changes.

**A plausible wrong approach:** Copying the float formula with stride 33 assumes one word per element and may mispredict conflicts.

**How to verify:** Model eight-byte addresses for 32 lanes and confirm with a profiler where available.

## Self-check answers

1. **In the 32-bank model, which bank does row 5 of a column use at width 33?** Bank 5, since 5 times 33 mod 32 is 5.
2. **Why can a same-address read avoid a conflict?** Lanes reading the identical word can receive it by broadcast.
3. **What must a padded transpose never output?** The padding column; it is internal storage, not data.

## Numerical reference and its limits

The [CPU reference](../references/cuda-035_cpu.py) reproduces worked example 1 and prints `{'model_unique_banks': [1, 32]}`.

## Transfer review

Reassess bank width and multiword accesses on the selected architecture. Do not reuse the float32 one-word model unchanged.
