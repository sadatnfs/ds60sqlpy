"""polars-012: worked starting point; complete the guide's six changes."""

import polars as pl
import pyarrow as pa


def example_one():
    frame = pl.DataFrame({"id": [1, 2, 3], "value": [2.0, None, 4.0]})
    arrow = frame.to_arrow()
    assert arrow.column("id").to_pylist() == [1, 2, 3]
    assert arrow.column("value").null_count == 1
    restored = pl.from_arrow(arrow)
    assert restored.equals(frame)
    assert isinstance(arrow, pa.Table)
    return {"arrow_schema": str(arrow.schema), "round_trip": True, "nulls": 1}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Explain why a null is separate from a numeric payload value.
# TODO 2: State what the round-trip test actually proves.
# TODO 3: Extend the allowed states with returned.
# TODO 4: Add cancelled without changing the Enum.
# TODO 5: Compare business-order and alphabetical sorting.
# TODO 6: List what a receiver needs beyond an Arrow object.
