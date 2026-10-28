# apache-012: IPC, streams and ownership

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-011`.

## The mechanism

In-memory representation and interchange are related but different tasks. A
running process can retain pointers to its buffers. Another process cannot use
those addresses directly without an agreed sharing and lifetime mechanism.
Arrow IPC serializes schema and record-batch information into a documented
interchange representation so a reader can reconstruct the logical arrays.
IPC means interprocess communication here; it is not a promise of shared-memory
transport or an authentication protocol.

Arrow provides stream and file forms. A stream is naturally consumed in order:
the reader obtains the schema and then a sequence of record batches. A file adds
structure that permits locating batches without replaying every earlier batch.
Choose the form from the access pattern. A streaming consumer often wants to
process a bounded batch and release it. An interactive tool may want batch 2
without first materializing batches 0 and 1.

All batches in one IPC stream share the declared schema. This includes types,
not just names. Changing an integer amount into a string halfway through a
stream is not transparent schema evolution. A system must either normalize the
batch, begin a new compatible stream, or negotiate a different protocol. The
complete example uses in-memory buffers so it needs no external service.

## Worked case A: an ordered stream with explicit metadata

The first case writes two record batches with a schema that includes a synthetic
currency metadata key. It closes the writer before obtaining the completed
buffer, then reads the stream back. The assertions compare schema metadata,
batch count and logical values. These are three separate checks: matching values
alone would miss the loss of metadata, while matching a schema would not prove
that every batch arrived.

The amounts are integer minor units, so 1299 denotes a precisely represented
amount in the fixture's declared unit. Serialization must preserve that integer.
The example avoids floating-point rounding so a discrepancy is easy to locate.
It also avoids interpreting metadata as an enforcement mechanism: the currency
label documents the unit, while application code decides which arithmetic and
cross-currency operations are permitted.

The second write attempt intentionally uses a mismatched schema. The writer is
expected to reject it. Catching that error demonstrates a contract boundary; it
must not be handled by silently dropping the bad batch and declaring the stream
complete. A real ingestion process would record the rejected input and decide
whether to fail the job or route it to an explicit quarantine process.

## Worked case B: random batch access in an IPC file

The second case writes the same batches in file form and opens a file reader.
It inspects the number of batches and retrieves the second batch directly.
That batch contains the expected record. Reading all batches reconstructs the
same logical table as the stream case. The difference is the access capability,
not the meaning of the values.

Now consider memory. A serialized byte count is not the same quantity as the
logical value payload or the process memory footprint. Schemas, offsets and
message framing consume bytes too. With a tiny fixture their relative overhead
can be large. The program prints file and stream sizes as observations without
asserting one must always be smaller. Compression, data types and batch sizes
can change the comparison.

If a reader uses a memory-mapped file, some arrays may reference mapped storage.
Their lifetime and the file's lifetime must remain valid. Converting the final
table to a Python list creates Python objects and is used here only to inspect
small results. A production streaming consumer should avoid collecting an
unbounded result merely because the interchange format is efficient.

## Mistakes and diagnosis

Do not assume that naming a file `.arrow` tells you whether it contains the stream
or file representation. Use the matching reader contract. Do not reuse a writer
schema while inserting a differently typed batch. Do not call a local IPC
round-trip a successful network transfer; this chapter opens no listening port.
A later Flight workshop will test the transport and invalid-ticket behavior
separately.

## Interview discussion

**When would you select stream IPC rather than file IPC?** Select a stream when
ordered batch consumption fits the producer/consumer boundary and random batch
lookup is unnecessary. Select file IPC when the consumer needs file-level batch
indexing. In either case, verify schema, completeness and ownership. The format
alone does not provide transactions, authorization, retry semantics or a catalog.

## Complete worked source

This is a complete editable worked program for the declared prepared runtime. It uses bounded local fixtures and does not install packages or start distributed services.

```python
import pyarrow as pa
import pyarrow.ipc as ipc

schema = pa.schema(
    [("id", pa.int64()), ("amount_minor", pa.int64())], metadata={b"currency": b"fixture-USD"}
)
batches = [
    pa.record_batch([[1, 2], [1299, 2500]], schema=schema),
    pa.record_batch([[3], [700]], schema=schema),
]
stream_sink = pa.BufferOutputStream()
with ipc.new_stream(stream_sink, schema) as writer:
    for batch in batches:
        writer.write_batch(batch)
stream = stream_sink.getvalue()
reader = ipc.open_stream(stream)
assert reader.schema.equals(schema, check_metadata=True)
restored = list(reader)
assert len(restored) == 2
assert pa.Table.from_batches(restored).to_pylist() == [
    {"id": 1, "amount_minor": 1299},
    {"id": 2, "amount_minor": 2500},
    {"id": 3, "amount_minor": 700},
]
bad = pa.record_batch([[4], ["900"]], names=["id", "amount_minor"])
with ipc.new_stream(pa.BufferOutputStream(), schema) as writer:
    try:
        writer.write_batch(bad)
    except (pa.ArrowInvalid, ValueError):
        print("Mismatched batch schema rejected")
    else:
        raise AssertionError("Expected a schema mismatch")
file_sink = pa.BufferOutputStream()
with ipc.new_file(file_sink, schema) as writer:
    for batch in batches:
        writer.write_batch(batch)
file_bytes = file_sink.getvalue()
file_reader = ipc.open_file(file_bytes)
assert file_reader.num_record_batches == 2
assert file_reader.get_batch(1).to_pylist() == [{"id": 3, "amount_minor": 700}]
assert file_reader.read_all().equals(pa.Table.from_batches(restored), check_metadata=True)
print("Stream bytes:", stream.size, "file bytes:", file_bytes.size)
print("Directly read second batch:", file_reader.get_batch(1).to_pylist())
```

## Primary references

- [Arrow IPC documentation](https://arrow.apache.org/docs/python/ipc.html)
- [Arrow IPC format](https://arrow.apache.org/docs/format/Columnar.html#serialization-and-interprocess-communication-ipc)
