"""polars-006: both worked cases; complete the guide's six changes."""

import polars as pl


def example_one():
    facts = pl.DataFrame({"order_id": [1, 2, 3], "customer": [10, 10, 20], "amount": [5, 7, 9]})
    dimension = pl.DataFrame({"customer": [10, 20], "region": ["N", "S"]})
    joined = facts.join(dimension, on="customer", how="left", validate="m:1")
    assert joined.height == 3 and joined["amount"].sum() == 21
    bad = pl.concat([dimension, dimension.head(1)])
    inflated = facts.join(bad, on="customer", how="left")
    assert inflated.height == 5 and inflated["amount"].sum() == 33
    try:
        facts.join(bad, on="customer", how="left", validate="m:1")
    except pl.exceptions.ComputeError:
        rejected = True
    else:
        rejected = False
    assert rejected
    return {"correct_total": 21, "fanout_total": 33, "validation_rejected_duplicate": rejected}


def example_two():
    left = pl.DataFrame({"id": [1, 2, 3], "key": [10, 20, None]})
    right = pl.DataFrame({"key": [10, None]})
    assert left.join(right, on="key", how="semi")["id"].to_list() == [1]
    assert left.join(right, on="key", how="anti").sort("id")["id"].to_list() == [2, 3]
    assert left.join(right, on="key", how="semi", nulls_equal=True).sort("id")["id"].to_list() == [
        1,
        3,
    ]
    return {"known": [1], "unmatched_or_missing": [2, 3], "explicit_null_matching": [1, 3]}


if __name__ == "__main__":
    print(example_one())
    print(example_two())

# TODO 1: Check the dimension key before enrichment.
# TODO 2: Verify that additive order revenue is unchanged by valid enrichment.
# TODO 3: Return orders whose customers occur in the dimension without adding region.
# TODO 4: Add a customer 30 order and inspect it using an anti join.
# TODO 5: Explain why dropping duplicate customer rows can be incorrect.
# TODO 6: Compare default and nulls_equal behavior for two missing keys.
