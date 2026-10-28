"""polars-016: worked starting point; complete the guide's six changes."""

import polars as pl


def example_one():
    frame = pl.DataFrame({"x": [1, 2, 3]})
    native = frame.select((pl.col("x") * pl.col("x")).alias("square"))
    udf = frame.select(
        pl.col("x").map_elements(lambda value: value * value, return_dtype=pl.Int64).alias("square")
    )
    assert native.equals(udf)
    assert native["square"].to_list() == [1, 4, 9]
    return {"values": native.to_dicts(), "native_and_udf_equal_on_fixture": True}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Write the square operation using column expressions only.
# TODO 2: Explain what a UDF returning integers should declare.
# TODO 3: Center [1,2,3,10] in a different partition.
# TODO 4: Explain why a zero-sum check misses the centering defect.
# TODO 5: Describe the risk of incrementing a global counter inside a UDF.
# TODO 6: Explain how to perform global centering in bounded stages.
