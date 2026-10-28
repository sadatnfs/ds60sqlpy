"""polars-008: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Add a followup column to the wide fixture and unpivot it.
# TODO 2: Count rows by id and period before pivoting.
# TODO 3: Aggregate the duplicated values 4 and 6 using both policies.
# TODO 4: Replace one measurement with null and repeat the round trip.
# TODO 5: Calculate after minus before in wide form and verify from long records.
# TODO 6: Write the row grain for both forms.
