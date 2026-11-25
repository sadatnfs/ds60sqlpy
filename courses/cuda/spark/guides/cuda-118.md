# cuda-118: Columnar batches, Arrow and data movement

**Route:** CUDA Python and machine learning / GPU Spark specialization. **Stage:** advanced. **Prerequisites:** `cuda-113`, `cuda-117`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Count fixed-width payload.
- Count validity bytes.
- Explain string offsets.
- Locate row-column transitions.
- Budget transfer payload.
- Design a conversion parity test.

## Mechanism and vocabulary

Columnar execution groups values by column with accompanying validity and offset structures. Arrow defines interoperable columnar formats; it is not itself a guarantee of GPU residency or zero-copy across every process and device boundary. Variable-width strings need offsets and character storage, while nullable columns need validity information. A batch's byte size can vary greatly with its schema.

Spark's row-to-columnar and columnar-to-row transitions can add work around unsupported operators. Host-to-device and device-to-host transfers are further boundaries. Plan batches by bytes as well as row counts and include temporary decoded representations. Increasing batch size can improve amortization while raising peak memory and spill risk. Preserve schema and null behavior through every conversion.



### Key terms

- **Columnar batch:** A group of rows stored column by column with the validity and offset structures each column needs.
- **Apache Arrow:** An interoperable columnar memory format that does not by itself guarantee GPU residency or zero copy.
- **Validity bitmap:** A bit per row marking whether a value in a nullable column is present.
- **String offsets:** An integer array giving where each variable-width string starts in the character buffer.

## Worked examples

### Worked example 1

One thousand float64 values occupy 8000 payload bytes, plus any null mask and metadata. One thousand strings can occupy widely different storage depending on lengths.

### Worked example 2

A validity mask for nine rows needs at least two bytes at one bit per row. Treating null as numeric zero would erase information rather than merely change representation.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-118_cpu.py) adds assertions.

```sh
python courses/cuda/spark/lessons/cuda-118_cpu.py
```

```python
rows, itemsize = 1000, 8
payload = rows * itemsize
mask = (9 + 7) // 8
assert payload == 8000 and mask == 2
strings = ["a", "longer", ""]
assert sum(len(s.encode("utf-8")) for s in strings) == 7
print("CPU columnar ledger:", payload, mask, 7)
```

**Expected observation:** Fixed payload 8000 bytes, nine-row mask 2 bytes, string characters 7 bytes.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `rows` | `1000` |
| `itemsize` | `8` |
| `payload` | `8000` |
| `mask` | `2` |
| `strings` | `['a', 'longer', '']` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-118.md) before opening hints.

### Exercise 1: Count fixed-width payload

**Trap to avoid:** Counting 1000 values as 4000 bytes by assuming float32 underestimates the transfer by half when the schema says double. Schema inference from CSV or pandas commonly produces double even when the data looks like small decimals.

### Exercise 2: Count validity bytes

**Trap to avoid:** Using `9//8 = 1` floors the division and leaves the ninth row without a bit. The ninth row's null state would then be read from whatever byte follows the mask.

### Exercise 3: Explain string offsets

**Trap to avoid:** Estimating string columns as rows times an average length ignores the offset array and the UTF-8 encoding of multibyte characters.

### Exercise 4: Locate row-column transitions

**Trap to avoid:** Assuming the whole query is columnar because the source is a Parquet file ignores row-based operators later in the plan. A Python UDF or an unsupported expression in a later stage forces a conversion back to rows at that point.

### Exercise 5: Budget transfer payload

**Trap to avoid:** Budgeting only values underestimates both transfer time and peak memory. For string-heavy tables, offsets and variable character data can exceed the numeric payload by a wide margin.

### Exercise 6: Design a conversion parity test

**Trap to avoid:** Comparing only values with nulls replaced by zero erases the distinction the mask exists to keep. A conversion bug that turns nulls into zeros would then pass the test unnoticed.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Multiply the number of rows by the width of one value.
2. Divide the row count by eight and round up.
3. Ask how a reader finds where the second string starts and ends in one shared character buffer.
4. Read the physical plan and mark each row to columnar and columnar to row node.
5. Add values, masks, offsets and any temporary decoded copies made for the transfer.
6. Convert a batch with nulls and strings and back, then compare schema, row identity, nulls and values.

## Common mistakes and self-check

A common mistake is sizing batches by row count alone. A thousand float64 values occupy 8000 payload bytes, but a thousand strings can occupy far more depending on their lengths. Another is treating null as zero during conversion, which erases information. Fix both by planning batches by bytes, including masks, offsets and temporary copies, and by testing that every conversion preserves schema, nulls and row identity.

**Misconception:** Arrow conversion between Spark and Python is free because both sides are columnar. **Correction:** Spark's internal CPU rows and the plugin's GPU columns are not Arrow buffers by default, so each boundary can serialize, copy or rebuild validity masks and offsets. A pandas UDF, for example, converts batches to Arrow, sends them to a Python worker and converts the result back. Measure that conversion separately and count every row to columnar transition in the plan.

**Evidence limit:** The reference counts 8000 payload bytes, a 2-byte mask for nine rows and 7 string bytes. It moves no data, so Arrow conversion, device transfers and spill behavior need measurement in the actual pipeline.

1. Does using Arrow guarantee zero-copy GPU residency?
2. Why can a larger batch raise spill risk?
3. What structures does a nullable string column need?

Answers: [self-check answers](../solutions/cuda-118_solutions.md#self-check-answers).

## Primary references

- [GPU Spark tuning guide](https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-118: Columnar batches, Arrow and data movement.
Read courses/cuda/spark/guides/cuda-118.md and courses/cuda/spark/lessons/cuda-118.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
