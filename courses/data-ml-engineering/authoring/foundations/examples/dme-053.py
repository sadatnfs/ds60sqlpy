"""Actual CSV-to-Parquet migration reconciles identities and minor currency units before cutover."""

import csv
import hashlib
import json
import tempfile
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

SCHEMA = pa.schema(
    [("order_id", pa.string()), ("amount_minor", pa.int64()), ("currency", pa.string())]
)


def old_reader(path):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if (
            reader.fieldnames is None
            or set(reader.fieldnames) != {"order_id", "amount_usd"}
            or len(reader.fieldnames) != 2
        ):
            raise ValueError("Old CSV schema differs from its reviewed contract")
        rows = list(reader)
    canonical = []
    for row in rows:
        if (
            set(row) != {"order_id", "amount_usd"}
            or not row["order_id"]
            or row["order_id"] != row["order_id"].strip()
        ):
            raise ValueError("Old record identity or field population is invalid")
        amount = Decimal(row["amount_usd"]) * 100
        if not amount.is_finite() or amount != amount.to_integral_value() or amount < 0:
            raise ValueError("Old contract requires nonnegative exact USD cents")
        canonical.append(
            {"order_id": row["order_id"], "amount_minor": int(amount), "currency": "USD"}
        )
    if len({row["order_id"] for row in canonical}) != len(canonical):
        raise ValueError("Old table has duplicated order identity")
    return sorted(canonical, key=lambda row: row["order_id"])


def candidate(root, name, rows):
    if not name.isalnum():
        raise ValueError("Candidate name must be a simple owned identifier")
    path = root / (name + ".parquet")
    if path.exists():
        raise ValueError("Candidate files are immutable")
    pq.write_table(pa.Table.from_pylist(rows, schema=SCHEMA), path)
    return path


def new_reader(path):
    table = pq.read_table(path)
    if table.schema != SCHEMA:
        raise ValueError("New physical schema differs from the reviewed contract")
    result = sorted(table.to_pylist(), key=lambda row: row["order_id"])
    if len({row["order_id"] for row in result}) != len(result):
        raise ValueError("New table has duplicated order identity")
    return result


def activate(root, source, candidate_path):
    original, proposed = old_reader(source), new_reader(candidate_path)
    if original != proposed:
        raise ValueError("Candidate differs in row identity, value or currency")
    manifest = {
        "kind": "parquet",
        "file": candidate_path.name,
        "sha256": hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "rows": len(proposed),
    }
    pending = root / "current.pending"
    pending.write_text(json.dumps(manifest, sort_keys=True))
    pending.replace(root / "current.json")
    return proposed


def fixture(root):
    path = root / "orders.csv"
    path.write_text("order_id,amount_usd\n001,1.99\n010,2.50\n")
    (root / "current.json").write_text(
        json.dumps(
            {
                "kind": "csv",
                "file": path.name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    )
    return path


def accepted(root):
    manifest = json.loads((root / "current.json").read_text())
    if Path(manifest["file"]).name != manifest["file"]:
        raise ValueError("Accepted file must be an owned basename")
    path = root / manifest["file"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError("Accepted artifact changed")
    if manifest["kind"] == "csv":
        return old_reader(path)
    if manifest["kind"] == "parquet":
        return new_reader(path)
    raise ValueError("Unknown reader contract")


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = fixture(root)
        original = accepted(root)
        path = candidate(root, "reviewed", original)
        activate(root, source, path)
        assert accepted(root) == old_reader(source) == original
        assert [row["order_id"] for row in original] == ["001", "010"]
        assert sum(row["amount_minor"] for row in original) == 449
        return {
            "old_and_new_canonical_rows": original,
            "exact_total_minor_units": 449,
            "leading_zero_identities_preserved": True,
            "accepted_format": "parquet",
        }


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = fixture(root)
        original = accepted(root)
        before = (root / "current.json").read_bytes()
        wrong = [{**row, "order_id": str(int(row["order_id"]))} for row in original]
        path = candidate(root, "lostidentity", wrong)
        assert sum(row["amount_minor"] for row in new_reader(path)) == 449
        try:
            activate(root, source, path)
        except ValueError:
            pass
        else:
            raise AssertionError("Equal totals hid changed order identities")
        assert (root / "current.json").read_bytes() == before and accepted(root) == original
        return {
            "candidate_total_still_449": True,
            "candidate_ids": [row["order_id"] for row in wrong],
            "accepted_ids": [row["order_id"] for row in original],
            "cutover_rejected": True,
        }


def main():
    print("Compatible dual readers with exact currency units:", example_one())
    print("Aggregate equality does not establish migration correctness:", example_two())


if __name__ == "__main__":
    main()
