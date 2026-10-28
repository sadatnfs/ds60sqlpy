"""polars-013: complete bounded Polars investigation."""

import polars as pl


def example_one():
    frame = pl.DataFrame({"order": [1, 2, 3], "items": [["a", "b"], [], None]})
    normalized = frame.with_columns(pl.col("items").list.len().alias("count"))
    assert normalized["count"].to_list() == [2, 0, None]
    eligible = normalized.filter(pl.col("count") > 0).explode("items")
    assert eligible.to_dicts() == [
        {"order": 1, "items": "a", "count": 2},
        {"order": 1, "items": "b", "count": 2},
    ]
    return {"order_rows": 3, "item_rows": 2, "excluded_empty_or_unknown_orders": [2, 3]}


def example_two():
    frame = pl.DataFrame({"x": [1, 2], "y": [3, 4]})
    packed = frame.select(pl.struct("x", "y").alias("point"))
    extracted = packed.select(pl.col("point").struct.field("x"), pl.col("point").struct.field("y"))
    assert extracted.equals(frame)
    evaluated = pl.DataFrame({"values": [[1, 2], [3]]}).select(
        pl.col("values").list.eval(pl.element() * 2).alias("doubled")
    )
    assert evaluated["doubled"].to_list() == [[2, 4], [6]]
    return {"struct_round_trip": True, "nested_values": evaluated.to_dicts()}


def main():
    print(example_one())
    print(example_two())
    print("polars-013 reference checks passed")


if __name__ == "__main__":
    main()
