"""polars-018: complete bounded Polars investigation."""

import hashlib
import json
import tempfile
from pathlib import Path

import polars as pl


def example_one():
    raw = pl.DataFrame(
        {
            "event_id": [1, 2, 2, 3, 4],
            "customer": [10, 10, 10, 20, 20],
            "amount_text": ["5", "7", "7", "bad", "9"],
            "time": [1, 2, 2, 3, 4],
        }
    )
    parsed = raw.with_columns(pl.col("amount_text").cast(pl.Int64, strict=False).alias("amount"))
    quarantine = parsed.filter(pl.col("amount").is_null())
    clean = parsed.filter(pl.col("amount").is_not_null()).unique(subset="event_id").sort("event_id")
    result = (
        clean.group_by("customer")
        .agg(pl.col("amount").sum().alias("total"), pl.len().alias("events"))
        .sort("customer")
    )
    assert quarantine["event_id"].to_list() == [3]
    assert clean.height == 3 and result.to_dicts() == [
        {"customer": 10, "total": 12, "events": 2},
        {"customer": 20, "total": 9, "events": 1},
    ]
    assert raw.height == clean.height + quarantine.height + 1
    return {"result": result.to_dicts(), "rejected": 1, "duplicate_rows": 1}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "features.parquet"
        frame = pl.DataFrame({"customer": [10, 20], "total": [12, 9]})
        frame.write_parquet(path)
        receipt = {
            "grain": "one row per customer",
            "rows": 2,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "schema": {k: str(v) for k, v in frame.schema.items()},
        }
        receipt_path = Path(d) / "receipt.json"
        receipt_path.write_text(json.dumps(receipt, sort_keys=True))
        restored = json.loads(receipt_path.read_text())
        assert restored["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert pl.read_parquet(path).equals(frame)
        assert frame["customer"].n_unique() == frame.height
        return {"receipt": restored, "readback_matches": True}


def main():
    print(example_one())
    print(example_two())
    print("polars-018 reference checks passed")


if __name__ == "__main__":
    main()
