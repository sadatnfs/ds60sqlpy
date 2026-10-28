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
