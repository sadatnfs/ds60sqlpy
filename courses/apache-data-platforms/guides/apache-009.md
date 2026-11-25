# apache-009: Arrays, buffers and null bitmaps

Tutorial mode. Stage: beginner. Direct prerequisites: `apache-008`.

## Key terms

- **Buffer:** A contiguous memory region holding one part of an Arrow array, such as its fixed-width values or its validity bits.
- **Validity bitmap:** A buffer with one bit per slot in which a set bit marks a present value, so nulls need no sentinel. Its logical size is n divided by 8, rounded up, bytes for n slots.
- **Array offset:** The starting slot of an array within its buffers. With offset o and value width w, logical element i starts at byte (o + i) times w.
- **Zero-copy slice:** A new array view that reuses its parent's buffers with a different offset and length instead of copying values.

## The mechanism

An Arrow array is a typed view over buffers. That sentence is more precise than
calling it a fast Python list. A Python list stores references to separately
represented objects. An Arrow integer array stores fixed-width values together,
plus optional validity information and view metadata. Its type tells a consumer
how to interpret each slot. The array also carries a logical length and an offset.
Those three quantities, type, length and offset, are necessary to interpret the
buffers correctly across a language boundary.

For an integer width of \(w\) bytes, the value associated with logical element
\(i\) starts at byte \((o+i)w\), where \(o\) is the array offset. A validity
bitmap uses one bit per slot; a set bit identifies a present value. Its required
logical storage is \(\lceil n/8\rceil\) bytes for \(n\) unsliced elements,
although allocation and alignment can occupy more memory. A missing integer is
not represented by a special integer sentinel. Every integer bit pattern remains
available for a present value, including zero and negative numbers.

This design helps an execution engine scan one column without loading unrelated
columns. It also permits a slice to share buffers rather than copying every value.
Neither fact guarantees that every operation is zero-copy. Filtering constructs a
new selection, Python object conversion allocates objects, and changing physical
types can require new buffers. Ask which specific operation shares which allocation.

## Worked case A: a missing measurement is not zero

The first case creates `[10, None, 30, 40]` with explicit signed 64-bit type. The
validity bits for these four slots are present, absent, present, present. The
program checks those bits directly and separately verifies the logical values.
The value-buffer bytes under the absent slot must not be interpreted as a real
measurement. Their contents are irrelevant to the logical array contract.

Summing valid measurements gives 80. The mean over observed measurements is
\(80/3\), whereas replacing the missing observation with zero gives 20. The
second number answers a different question. A pipeline that conflates missing
with zero has changed its denominator even if its integer representation looks
plausible. The example prints both values so the data-model decision is visible.

The explicit type also controls range. An 8-bit signed array cannot represent 200.
The program expects the library to reject that construction, rather than treating
a wrapped negative number as a valid observation. A parser that silently narrows
an identifier could join unrelated records later, making type validation a data
correctness property rather than a cosmetic choice.

## Worked case B: a slice is a view with an offset

The second case selects two elements beginning at logical position 1. Its values
are `[None, 30]`, its length is 2, and its offset is 1. The test compares the value
buffer addresses to establish sharing within this process. It never prints or
persists those addresses as portable identifiers. The parent and slice point to
the same allocation, but they describe different logical arrays.

Now delete the parent Python reference and force collection. The slice still
returns its values because Arrow retains ownership of the buffers it needs.
That is a lifetime guarantee of this managed object relationship, not permission
to retain a raw pointer after its owner is released. Native integrations must
respect their own release callbacks and ownership rules.

A tiny slice can therefore keep a large parent allocation alive. Copying a small
result can sometimes reduce long-lived memory, despite adding an immediate copy.
The right choice depends on retention time and allocation size, not a universal
rule that zero-copy is always preferable.

## Mistakes and diagnosis

Do not read bitmap bit 0 when a sliced logical element begins at a nonzero offset.
Do not treat `nbytes` as a process resident-memory measurement. Allocator overhead,
shared allocations and other objects are outside that simple measure. Do not
infer a memory leak merely because deleting a Python variable fails to release
buffers still referenced by another view. Inspect ownership before changing the
representation.

## Interview discussion

**How would you explain Arrow's benefit without promising zero-copy everywhere?**
A column has an explicit interoperable layout that supports vectorized scans and
buffer sharing for compatible views. Serialization, network transport, type
conversion and Python materialization can still allocate or copy. The evidence
in this chapter proves sharing for one slice and correct null handling, not an
end-to-end performance claim. Next, nested arrays extend the same idea with child
arrays and offsets whose meaning must also survive a language boundary.

## Worked examples

### Read the validity bitmap behind a null

```python
import pyarrow as pa
import pyarrow.compute as pc

values = pa.array([10, None, 30, 40], type=pa.int64())
validity = values.buffers()[0].to_pybytes()[0]
print([(validity >> i) & 1 for i in range(4)])
print(pc.mean(values).as_py(), pc.mean(pc.fill_null(values, 0)).as_py())
```

```text
[1, 0, 1, 1]
26.666666666666668 20.0
```

Bit 1 is zero, so the second slot is missing even though the payload buffer still holds some integer there. The observed mean divides 80 by three known values, while the zero-filled mean divides by four and reports 20. Neither is wrong in general; the question is whether a missing reading means no measurement or a real zero, and that decision belongs in the contract rather than in a default fill.

### Confirm a slice shares memory with its parent

```python
import pyarrow as pa

values = pa.array([10, None, 30, 40], type=pa.int64())
sliced = values.slice(1, 2)
print(sliced.offset, len(sliced), sliced.to_pylist())
print(sliced.buffers()[1].address == values.buffers()[1].address)
```

```text
1 2 [None, 30]
True
```

The slice reports offset 1 and length 2 and points at the same payload address as the parent, so slicing copied nothing. That is efficient, but it also means a tiny slice can keep a large parent buffer alive in memory. When memory use stays high after filtering a big batch down to a few rows, check for retained slices and copy them with take or concat if the parent should be released.

## Complete worked source

Run it as the [worked program rules](../STUDY-GUIDE.md#worked-programs) describe.

```python
import gc

import pyarrow as pa
import pyarrow.compute as pc

values = pa.array([10, None, 30, 40], type=pa.int64())
validity, payload = values.buffers()
assert validity is not None and payload is not None
bits = validity.to_pybytes()[0]
assert [(bits >> i) & 1 for i in range(4)] == [1, 0, 1, 1]
assert pc.sum(values).as_py() == 80
assert abs(pc.mean(values).as_py() - 80 / 3) < 1e-12
assert pc.mean(pc.fill_null(values, 0)).as_py() == 20
try:
    pa.array([200], type=pa.int8())
except pa.ArrowInvalid:
    print("Narrowing rejected: 200 cannot fit in signed int8")
else:
    raise AssertionError("Expected an invalid narrowing conversion")
sliced = values.slice(1, 2)
assert sliced.offset == 1 and len(sliced) == 2
assert sliced.buffers()[1].address == payload.address
assert sliced.to_pylist() == [None, 30]
del values, payload
gc.collect()
assert sliced.to_pylist() == [None, 30]
print("Observed mean:", 80 / 3, "zero-filled mean:", 20)
print("Retained slice:", sliced.to_pylist(), "offset:", sliced.offset)
```

## Primary references

- [Arrow columnar format](https://arrow.apache.org/docs/format/Columnar.html)
- [PyArrow array API](https://arrow.apache.org/docs/python/generated/pyarrow.Array.html)
