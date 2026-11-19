"""polars-008: both worked cases; complete the guide's six changes."""

import polars as pl


def example_one():
    wide = pl.DataFrame({"id": [1, 2], "before": [10, 20], "after": [12, 18]})
    long = wide.unpivot(
        index="id", on=["before", "after"], variable_name="period", value_name="value"
    )
    assert long.height == 4
    rebuilt = (
        long.pivot(on="period", index="id", values="value")
        .select("id", "before", "after")
        .sort("id")
    )
    assert rebuilt.equals(wide)
    return {"long_rows": long.sort("id", "period").to_dicts(), "round_trip": True}


def example_two():
    duplicate = pl.DataFrame({"id": [1, 1], "period": ["after", "after"], "value": [4, 6]})
    result = duplicate.pivot(on="period", index="id", values="value", aggregate_function="sum")
    assert result["after"].item() == 10
    frequencies = duplicate.group_by("id", "period").len()
    assert frequencies["len"].item() == 2
    try:
        duplicate.pivot(on="period", index="id", values="value")
    except pl.exceptions.ComputeError:
        rejected = True
    else:
        rejected = False
    assert rejected
    return {"duplicate_cell_count": 2, "explicit_aggregation_total": 10}


if __name__ == "__main__":
    print(example_one())
    print(example_two())

# TODO 1: Add a followup column to the wide fixture and unpivot it.
# TODO 2: Count rows by id and period before pivoting.
# TODO 3: Aggregate the duplicated values 4 and 6 using both policies.
# TODO 4: Replace one measurement with null and repeat the round trip.
# TODO 5: Calculate after minus before in wide form and verify from long records.
# TODO 6: Write the row grain for both forms.
