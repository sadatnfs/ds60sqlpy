import math

import pyarrow as pa
import pyarrow.compute as pc

values = pa.chunked_array([[4, None, 8], [2, 6]], type=pa.int64())
assert len(values) == 5 and values.num_chunks == 2
assert pc.sum(values).as_py() == 20 and pc.mean(values).as_py() == 5
assert pc.mean(values.combine_chunks()).as_py() == 5
unequal = pa.chunked_array([[4], [None, 8, 2, 6]], type=pa.int64())
wrong_mean = sum(pc.mean(chunk).as_py() for chunk in unequal.chunks) / 2
assert math.isclose(wrong_mean, 14 / 3) and not math.isclose(wrong_mean, 5)
sums = [pc.sum(chunk).as_py() for chunk in unequal.chunks]
counts = [len(chunk) - chunk.null_count for chunk in unequal.chunks]
assert sum(sums) / sum(counts) == 5
mask = pc.greater(values, 5)
selected = pc.filter(values, mask)
uncertain = pc.filter(values, mask, null_selection_behavior="emit_null")
assert selected.to_pylist() == [8, 6]
assert uncertain.to_pylist() == [None, 8, 6]
assert pc.mean(pc.fill_null(values, 0)).as_py() == 4
print("Observed mean:", 5, "incorrect chunk mean:", wrong_mean)
print("Selected:", selected.to_pylist(), "retaining unknown membership:", uncertain.to_pylist())
print("Zero-filled mean changes the denominator:", 4)
