# cuda-034: explanatory solutions

## Mechanism review

Coalescing concerns how neighboring lanes' memory requests combine into transactions. The source loop may look sequential while lane addresses are far apart. Write the address for each lane first. Structure-of-arrays often helps a kernel that reads one field from many records, while array-of-structures can suit consumers that need complete records. Alignment, transaction size, cache and architecture affect the exact cost. Count useful bytes separately from fetched bytes and include conversion cost if layout changes. A layout beneficial for one kernel can hurt the full pipeline if every boundary requires reshuffling.

## Exercise 1

Thirty-two lanes read float32 elements at offsets 0 through 31. Their useful data spans 128 bytes. With stride eight elements, offsets run from 0 through 248 and span 996 bytes including gaps. Span is not a transaction count, but it reveals why the access pattern deserves measurement.

**Approach:** Multiply each lane by 4 bytes for contiguous reads and by 32 bytes for stride eight.

**Why it is correct:** Contiguous offsets end at 124 plus 4, spanning 128 bytes; strided ones end at 992 plus 4, spanning 996.

**A plausible wrong approach:** Treating the 996-byte span as an exact transaction count ignores caching and segment rules.

**How to verify:** The reference asserts contiguous[-1] + 4 == 128 and strided[-1] + 4 == 996.

## Exercise 2

For records containing x,y,z,w as four floats, reading x for 32 particles advances 16 bytes per lane. A separate x array advances four bytes per lane. If the next stage needs all four fields, compare complete pipeline costs before committing to a representation change.

**Approach:** Compare a 16-byte step per lane in the record layout with a 4-byte step in a separate x array.

**Why it is correct:** Reading x alone from records drags y, z and w along, while the separate array uses each byte.

**A plausible wrong approach:** Converting to separate arrays without checking whether later stages need all four fields may cost more overall.

**How to verify:** Measure the whole pipeline in both layouts with identical outputs.

## Exercise 3

0,12,24,36. Element stride must be multiplied by element size.

**Approach:** Multiply element stride 3 by 4 bytes.

**Why it is correct:** Lanes 0 to 3 start at 0, 12, 24 and 36 bytes.

**A plausible wrong approach:** Using stride 3 as a byte offset gives 0, 3, 6, 9 and misaligned reads.

**How to verify:** Compute lane * 3 * 4 for lanes 0 to 3.

## Exercise 4

Span is a reasoning aid. Actual transactions depend on alignment, caching and hardware; measure or clearly model those separately.

**Approach:** Call the span an address range and measure transfers separately.

**Why it is correct:** Transactions depend on alignment, caching and hardware, not span alone.

**A plausible wrong approach:** Reporting span as bytes transferred presents a model as a measurement.

**How to verify:** Label span values as modeled in the report.

## Exercise 5

Little about the full-warp case. Include realistic active masks and tail behavior in the workload.

**Approach:** Test full-warp and realistic partial masks, including tails.

**Why it is correct:** One active lane says little about how 32 lanes share segments.

**A plausible wrong approach:** Profiling only one lane can call a pattern coalesced when it is not.

**How to verify:** Run masks of 1, 16 and 32 lanes and compare.

## Exercise 6

A dedicated x array may reduce repeated unused-field traffic; account for initial conversion, ownership and final consumers in the comparison.

**Approach:** Keep a separate x array and count conversion costs at start and end.

**Why it is correct:** Many x-only steps reuse the cheap layout, repaying a one-time conversion.

**A plausible wrong approach:** Comparing only the inner step ignores the conversion and final consumers.

**How to verify:** Time the full pipeline including conversion for both layouts.

## Self-check answers

1. **What span do 32 float32 lanes cover at stride one?** 128 bytes: byte offsets 0 through 124, each element 4 bytes wide.
2. **Why is address span not the same as bytes transferred?** Transfers happen in fixed-size sectors, so gaps may or may not be fetched depending on alignment and caching.
3. **When can array-of-structures be the better layout?** When the consumer needs every field of each record together.

## Numerical reference and its limits

The [CPU reference](../references/cuda-034_cpu.py) reproduces worked example 1 and prints `{'contiguous_span_bytes': 128, 'strided_span_bytes': 996}`.

## Transfer review

A dedicated x array may reduce repeated unused-field traffic; account for initial conversion, ownership and final consumers in the comparison.
