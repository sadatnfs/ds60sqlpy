"""Inspect real partitioned Parquet selection without inventing IO measurements."""

import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.dataset as ds


def write_layout(root, rows_per_file):
    table = pa.table(
        {
            "delivery_id": [1, 2, 3, 4],
            "day": ["2024-01-01", "2024-01-01", "2024-01-02", ("2024-01-02")],
            ("packages"): [2, 3, 4, 1],
        }
    )
    partitioning = ds.partitioning(pa.schema([("day", pa.string())]), flavor="hive")
    ds.write_dataset(
        table,
        root,
        format="parquet",
        partitioning=partitioning,
        max_rows_per_file=rows_per_file,
        max_rows_per_group=rows_per_file,
        use_threads=False,
        existing_data_behavior="error",
    )
    return ds.dataset(root, format="parquet", partitioning=partitioning)


def selected(dataset, day):
    predicate = ds.field("day") == day
    fragments = list(dataset.get_fragments(filter=predicate))
    table = dataset.to_table(
        columns=["delivery_id", "packages"], filter=predicate, use_threads=False
    )
    rows = sorted(table.to_pylist(), key=lambda row: row["delivery_id"])
    return {
        "selected_fragments": len(fragments),
        "all_fragments": len(list(dataset.get_fragments())),
        ("columns"): table.column_names,
        ("rows"): rows,
    }


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        dataset = write_layout(Path(directory) / "by-day", 2)
        result = selected(dataset, "2024-01-01")
        assert result["selected_fragments"] == 1 and result["all_fragments"] == 2
        assert result["columns"] == ["delivery_id", "packages"]
        assert result["rows"] == [
            {"delivery_id": 1, "packages": 2},
            {"delivery_id": 2, "packages": 3},
        ]
        absent = selected(dataset, "2024-01-03")
        assert absent["selected_fragments"] == 0 and absent["rows"] == []
        return {
            "observed_selection": result,
            "absent_partition_rows": absent["rows"],
            ("bytes_read_were_not_measured"): True,
        }


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        compact = selected(write_layout(root / "compact", 2), "2024-01-01")
        fragmented = selected(write_layout(root / "small-files", 1), "2024-01-01")
        assert compact["rows"] == fragmented["rows"]
        assert (compact["all_fragments"], fragmented["all_fragments"]) == (2, 4)
        assert (compact["selected_fragments"], fragmented["selected_fragments"]) == (1, 2)
        assert sum(row["packages"] for row in fragmented["rows"]) == 2 + 3
        return {
            "compact_selected_files": compact["selected_fragments"],
            "small_file_selected_files": fragmented[("selected_fragments")],
            ("same_identified_result"): compact[("rows")],
            ("timing_claim_requires_a_separate_measurement"): True,
        }


def main():
    print("Actual partition selection and projection:", example_one())
    print("Same result, different file topology:", example_two())


if __name__ == "__main__":
    main()
