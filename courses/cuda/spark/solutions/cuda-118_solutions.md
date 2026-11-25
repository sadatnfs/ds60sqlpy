# cuda-118: explained solutions

Compare with your [worksheet](../lessons/cuda-118.md) attempt.

## Exercise 1: Count fixed-width payload

Rows times element width.

**Approach.** Count fixed-width payload as rows times element width: 1000 float64 values occupy `1000*8 = 8000` bytes before masks and metadata.

**Why it is correct here.** Fixed-width columns store values contiguously, so payload is exactly rows times width.

**A plausible wrong approach.** Counting 1000 values as 4000 bytes by assuming float32 underestimates the transfer by half when the schema says double. Schema inference from CSV or pandas commonly produces double even when the data looks like small decimals.

**How to verify.** The reference asserts `payload == 8000`. Read the schema to confirm the type, then compare with Arrow buffer sizes.

## Exercise 2: Count validity bytes

Ceiling rows divided by eight.

**Approach.** Count validity bytes as the ceiling of rows over eight: nine rows need `(9 + 7)//8 = 2` bytes of mask at one bit per row.

**Why it is correct here.** Arrow-style formats store one validity bit per row, padded to whole bytes, separate from the values.

**A plausible wrong approach.** Using `9//8 = 1` floors the division and leaves the ninth row without a bit. The ninth row's null state would then be read from whatever byte follows the mask.

**How to verify.** The reference asserts `mask == 2`. Check 8 rows gives 1 and 16 gives 2. Some implementations pad buffers to 8 or 64 bytes, so measured sizes can exceed this minimum, which the ledger should note.

## Exercise 3: Explain string offsets

Offsets identify boundaries in character data.

**Approach.** Explain string offsets: a string column stores all characters in one buffer and an offsets array marking where each string begins and ends; `['a', 'longer', '']` has 7 bytes of characters.

**Why it is correct here.** Variable-length data needs boundaries. Offsets allow empty strings and long strings in the same column without padding.

**A plausible wrong approach.** Estimating string columns as rows times an average length ignores the offset array and the UTF-8 encoding of multibyte characters.

**How to verify.** The reference sums UTF-8 lengths to 7. Add offsets of four entries for three strings to the ledger. With 32-bit offsets that adds 16 bytes, more than the 7 bytes of characters in this tiny column.

## Exercise 4: Locate row-column transitions

Inspect the physical plan.

**Approach.** Locate row to column transitions in the physical plan, which appear where a row-based operator meets a columnar one.

**Why it is correct here.** Each transition converts representation, which costs time and memory proportional to the data size. Columnar to row conversion must also rebuild each row object, which is expensive for wide schemas.

**A plausible wrong approach.** Assuming the whole query is columnar because the source is a Parquet file ignores row-based operators later in the plan. A Python UDF or an unsupported expression in a later stage forces a conversion back to rows at that point.

**How to verify.** Count the transition nodes in the executed plan and read their metrics. Rows and time per transition node show which conversion costs most.

## Exercise 5: Budget transfer payload

Include values masks offsets and temporary copies.

**Approach.** Budget transfer payload as values plus validity masks plus string offsets plus temporary copies created during conversion.

**Why it is correct here.** Each buffer moves across the bus, and conversions may hold two copies at once, raising peak memory.

**A plausible wrong approach.** Budgeting only values underestimates both transfer time and peak memory. For string-heavy tables, offsets and variable character data can exceed the numeric payload by a wide margin.

**How to verify.** Compute the ledger for a test table and compare with measured buffer sizes in Arrow or device memory reports. A table with nulls, empty strings and multibyte text exercises every term in the ledger.

## Exercise 6: Design a conversion parity test

Compare schema row identity nulls and values.

**Approach.** Design a conversion parity test comparing schema, row identity, nulls and values before and after converting between Spark rows, Arrow and back.

**Why it is correct here.** A conversion can drop null information, change types or reorder rows. Checking each property catches each failure.

**A plausible wrong approach.** Comparing only values with nulls replaced by zero erases the distinction the mask exists to keep. A conversion bug that turns nulls into zeros would then pass the test unnoticed.

**How to verify.** Use a key column, compare schemas exactly, and compare null positions as well as values.

## Self-check answers

1. **Does using Arrow guarantee zero-copy GPU residency?** No. Arrow defines interoperable columnar formats; residency and copying depend on each process and device boundary.

2. **Why can a larger batch raise spill risk?** It improves amortization but increases peak memory, which can push data to a slower tier.

3. **What structures does a nullable string column need?** Offsets to mark string boundaries, character storage and a validity mask for nulls.

## Reference observation

Fixed payload 8000 bytes, nine-row mask 2 bytes, string characters 7 bytes.

Asserted by `courses/cuda/spark/references/cuda-118_cpu.py`.
