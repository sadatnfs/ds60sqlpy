"""Real Arrow/Parquet round-trips and explicit text-format interpretation."""

import csv
import io
import json
import tempfile
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


def fixture():
    return pa.table(
        {
            "delivery_id": pa.array(["001", "002"], type=pa.string()),
            "packages": pa.array([2, 3], type=pa.int16()),
            "distance_km": pa.array([Decimal("1.20"), None], type=pa.decimal128(8, 2)),
            "note": pa.array(["", None], type=pa.string()),
            "observed_at": pa.array(
                [datetime(2024, 1, 1, 8, tzinfo=UTC), datetime(2024, 1, 1, 9, tzinfo=UTC)],
                type=pa.timestamp("ms", tz="UTC"),
            ),
        }
    )


def portable_rows(table):
    return [
        {
            **row,
            "distance_km": str(row["distance_km"]) if row["distance_km"] is not None else None,
            "observed_at": row["observed_at"].isoformat(),
        }
        for row in table.to_pylist()
    ]


def example_one():
    table = fixture()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "deliveries.parquet"
        pq.write_table(table, path, compression="zstd")
        restored = pq.read_table(path)
        assert restored.schema == table.schema and restored.to_pylist() == table.to_pylist()
        assert restored.column("packages").type == pa.int16()
        note = restored.column("note").combine_chunks()
        mask = note.buffers()[0].to_pybytes()[0]
        validity = [bool(mask & (1 << position)) for position in range(2)]
        assert validity == [True, False] and note.to_pylist() == ["", None]
        return {
            "rows": portable_rows(restored),
            "schema": [[field.name, str(field.type)] for field in restored.schema],
            "note_validity": validity,
            "parquet_rows": pq.read_metadata(path).num_rows,
        }


def example_two():
    table = fixture()
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=["delivery_id", "packages", "note"])
    writer.writeheader()
    writer.writerows({name: row[name] for name in writer.fieldnames} for row in table.to_pylist())
    records = list(csv.DictReader(io.StringIO(stream.getvalue(), newline="")))
    assert [row["note"] for row in records] == ["", ""]
    assert [row["packages"] for row in records] == ["2", "3"]
    try:
        json.dumps(table.to_pylist())
    except TypeError:
        default_json_rejected_native_types = True
    else:
        raise AssertionError("Native Decimal/datetime values require an explicit JSON policy")
    document = {
        "schema_version": 1,
        "distance_representation": "decimal text in kilometers",
        "rows": portable_rows(table),
    }
    decoded = json.loads(json.dumps(document, allow_nan=False))
    assert Decimal(decoded["rows"][0]["distance_km"]) == Decimal("1.20")
    assert decoded["rows"][0]["delivery_id"] == "001"
    return {
        "csv_rows": records,
        "csv_lost_empty_vs_null_note": True,
        "default_json_rejected_native_types": default_json_rejected_native_types,
        "explicit_json_contract": decoded,
    }


def main():
    from ds60sqlpy.plot_artifacts import publish_report, publish_table

    first, second = example_one(), example_two()
    columns = ["delivery_id", "packages", "distance_km", "note", "observed_at"]
    publish_table(
        columns,
        [[row[name] for name in columns] for row in first["rows"]],
        description=(
            "Actual Parquet round-trip of two synthetic deliveries; "
            "empty text and missing values remain "
            "distinct."
        ),
    )
    publish_report(
        {
            "arrow_schema": first["schema"],
            "note_validity": first["note_validity"],
            "text_format_comparison": second,
        },
        description=(
            "Observed Arrow schema, validity bits and declared CSV/JSON conversion behavior."
        ),
    )
    print("Parquet rows:", first["parquet_rows"], "note validity:", first["note_validity"])
    print("CSV note values:", [row["note"] for row in second["csv_rows"]])


if __name__ == "__main__":
    main()
