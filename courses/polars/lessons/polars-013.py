"""polars-013: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Create separate counts for an empty list and a null list.
# TODO 2: Write the key for the exploded item table.
# TODO 3: Compute the original number of orders before exploding.
# TODO 4: Add a third named coordinate and round-trip all fields.
# TODO 5: Square each numeric element without a Python row loop.
# TODO 6: Add a list containing a null element and define the policy.
