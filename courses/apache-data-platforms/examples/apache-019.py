import pyarrow as pa
import pyarrow.compute as pc
from datafusion import SessionContext, udf

ctx = SessionContext()
ctx.register_record_batches(
    "distances",
    [pa.table({"id": [1, 2, 3], "meters": pa.array([1, 25, None], type=pa.int64())}).to_batches()],
)
ctx.register_udf(
    udf(
        lambda values: pc.multiply(values, 100),
        [pa.int64()],
        pa.int64(),
        "immutable",
        "centimeters",
    )
)
ctx.register_udf(
    udf(
        lambda values: pc.multiply(pc.fill_null(values, 0), 100),
        [pa.int64()],
        pa.int64(),
        "immutable",
        "missing_as_zero",
    )
)


def row_loop(values):
    return pa.array([None if x is None else x * 100 for x in values.to_pylist()], type=pa.int64())


ctx.register_udf(udf(row_loop, [pa.int64()], pa.int64(), "immutable", "centimeters_loop"))
rows = (
    ctx.sql(
        "SELECT centimeters(meters) AS via_udf, meters*100 AS native, "
        "missing_as_zero(meters) AS filled, centimeters_loop(meters) AS via_loop "
        "FROM distances ORDER BY id"
    )
    .to_arrow_table()
    .to_pylist()
)
assert [r["via_udf"] for r in rows] == [100, 2500, None]
assert all(r["via_udf"] == r["native"] == r["via_loop"] for r in rows)
assert [r["filled"] for r in rows] == [100, 2500, 0]
try:
    ctx.sql("SELECT centimeters('not a distance')").collect()
except Exception as error:
    print("Incompatible signature rejected:", type(error).__name__)
else:
    raise AssertionError("String argument was accepted")
print(rows)
