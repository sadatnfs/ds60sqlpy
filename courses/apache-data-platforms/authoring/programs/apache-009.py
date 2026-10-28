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
