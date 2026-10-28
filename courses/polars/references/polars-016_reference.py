"""polars-016: complete bounded Polars investigation."""

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


def example_two():
    values = [1.0, 2.0, 3.0, 10.0]
    global_centered = [x - sum(values) / len(values) for x in values]
    batches = [values[:2], values[2:]]
    incorrectly_batched = [x - sum(batch) / len(batch) for batch in batches for x in batch]
    assert global_centered == [-3.0, -2.0, -1.0, 6.0]
    assert incorrectly_batched == [-0.5, 0.5, -3.5, 3.5]
    assert global_centered != incorrectly_batched
    return {
        "whole_dataset_centering": global_centered,
        "invalid_batchwise_centering": incorrectly_batched,
    }


def main():
    print(example_one())
    print(example_two())
    print("polars-016 reference checks passed")


if __name__ == "__main__":
    main()
