from decimal import Decimal

import pyarrow as pa
import pyarrow.compute as pc

money = pa.array([Decimal("12.50"), None, Decimal("7.25")], type=pa.decimal128(10, 2))
assert pc.sum(money).as_py() == Decimal("19.75")
minor = [1250, None, 725]
assert sum(x for x in minor if x is not None) == 1975
valid_count = len(money) - money.null_count
assert valid_count == 2 and len(money) == 3
observed_mean = pc.sum(money).as_py() / valid_count
zero_filled_mean = pc.sum(money).as_py() / len(money)
assert observed_mean == Decimal("9.875") and zero_filled_mean != observed_mean
try:
    pa.array([Decimal("1234.56")], type=pa.decimal128(5, 2))
except pa.ArrowInvalid:
    print("Precision overflow rejected")
else:
    raise AssertionError("Expected a precision failure")
identifiers = pa.array(["001", "1"], type=pa.string())
assert len(set(identifiers.to_pylist())) == 2
assert len({int(value) for value in identifiers.to_pylist()}) == 1
left = pa.table({"amount": money})
right = pa.table({"amount": pa.array(["12.50", None, "7.25"])})
assert not left.schema.equals(right.schema)
try:
    pa.concat_tables([left, right])
except pa.ArrowInvalid:
    print("Same column name with incompatible types rejected")
else:
    raise AssertionError("Expected a schema mismatch")
print("Observed total:", pc.sum(money).as_py(), "valid count:", valid_count)
print("Observed mean:", observed_mean, "zero-filled mean:", zero_filled_mean)
print("String identifiers retain their distinction:", identifiers.to_pylist())
