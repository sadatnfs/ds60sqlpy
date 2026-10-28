"""Actual CSV validation, Polars/DuckDB transformation, Parquet and accepted publication."""

import hashlib
import json
import tempfile
from pathlib import Path

import duckdb
import polars as pl
import pyarrow.parquet as pq


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_version(root, version):
    if len(version) != 64 or any(character not in "0123456789abcdef" for character in version):
        raise ValueError("Invalid accepted version identity")
    directory = root / "versions" / version
    manifest = json.loads((directory / "manifest.json").read_text())
    path = directory / "summary.parquet"
    if digest(path) != manifest["data_sha256"]:
        raise ValueError("Accepted Parquet content changed")
    rows = pq.read_table(path).to_pylist()
    if (
        len(rows) != manifest["output_rows"]
        or sum(row["packages"] for row in rows) != manifest["packages"]
    ):
        raise ValueError("Accepted product reconciliation failed")
    return {"version": version, "rows": rows, "manifest": manifest}


def current(root):
    pointer = json.loads((root / "current.json").read_text())
    return read_version(root, pointer["version"])


def publish(root, source, expected_rows):
    if type(expected_rows) is not int or not 0 <= expected_rows <= 100:
        raise ValueError("Declare a bounded complete source population")
    root.mkdir(exist_ok=True)
    if source.stat().st_size > 10_000:
        raise ValueError("Source fixture exceeds its byte budget")
    frame = pl.read_csv(source, infer_schema=False)
    if set(frame.columns) != {"delivery_id", "route", "packages"} or frame.height != expected_rows:
        raise ValueError("Complete delivery schema or population differs from its declaration")
    checked = frame.with_columns(
        pl.col("route").cast(pl.Int64, strict=False),
        pl.col("packages").cast(pl.Int64, strict=False),
    )
    valid = (
        pl.col("delivery_id").str.contains(r"^[A-Za-z0-9_-]{1,30}$")
        & pl.col("route").is_in([10, 20])
        & (pl.col("packages") > 0)
    ).fill_null(False)
    quarantined = checked.filter(~valid).to_dicts()
    duplicated = checked.select(pl.col("delivery_id").n_unique()).item() != checked.height
    source_sha = digest(source)
    decision = {
        "input_sha256": source_sha,
        "input_rows": frame.height,
        "quarantine_rows": len(quarantined),
        "quarantine": quarantined,
        "duplicated_identity": duplicated,
        "accepted": not quarantined and not duplicated,
    }
    (root / "attempts").mkdir(exist_ok=True)
    (root / "attempts" / (source_sha + ".json")).write_text(json.dumps(decision, sort_keys=True))
    if not decision["accepted"]:
        return decision
    source_code_sha = digest(Path(__file__))
    version = hashlib.sha256((source_sha + source_code_sha).encode()).hexdigest()
    directory = root / "versions" / version
    if directory.exists():
        prior = read_version(root, version)
        if (
            prior["manifest"]["input_sha256"] != source_sha
            or prior["manifest"]["source_sha256"] != source_code_sha
            or prior["manifest"]["input_rows"] != expected_rows
        ):
            raise ValueError("An existing version has inconsistent provenance")
        if current(root)["version"] != version:
            raise ValueError("An older prepared version needs an explicit activation decision")
        return {**decision, "version": version, "rows": prior["rows"], "replayed": True}
    directory.mkdir(parents=True, exist_ok=False)
    with duckdb.connect(":memory:") as connection:
        connection.register("deliveries", checked.to_arrow())
        connection.execute("create table routes(route integer primary key,region varchar)")
        connection.executemany("insert into routes values(?,?)", [(10, "north"), (20, "south")])
        result = connection.sql(
            "select d.route,r.region,sum(d.packages)::BIGINT packages "
            "from deliveries d join routes r using(route) "
            "group by d.route,r.region order by d.route"
        ).to_arrow_table()
    rows = result.to_pylist()
    total = int(checked["packages"].sum())
    if sum(row["packages"] for row in rows) != total:
        raise ValueError("Transformation failed the input-to-output total reconciliation")
    path = directory / "summary.parquet"
    pq.write_table(result, path)
    manifest = {
        "schema_version": 1,
        "input_sha256": source_sha,
        "source_sha256": source_code_sha,
        "data_sha256": digest(path),
        "input_rows": frame.height,
        "output_rows": len(rows),
        "packages": total,
    }
    (directory / "manifest.json").write_text(json.dumps(manifest, sort_keys=True))
    if pq.read_table(path).to_pylist() != rows:
        raise ValueError("Written Parquet differs from the reviewed candidate")
    pending = root / "current.pending"
    pending.write_text(json.dumps({"version": version}))
    pending.replace(root / "current.json")
    accepted = current(root)
    return {**decision, "version": version, "rows": accepted["rows"]}


def fixture(path):
    path.write_text("delivery_id,route,packages\nA,10,2\nB,10,3\nC,20,1\n")


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "input.csv"
        fixture(source)
        result = publish(root / "product", source, 3)
        assert result["rows"] == [
            {"route": 10, "region": "north", "packages": 5},
            {"route": 20, "region": "south", "packages": 1},
        ]
        assert current(root / "product")["manifest"]["input_rows"] == 3
        assert publish(root / "product", source, 3)["replayed"] is True
        return result


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "input.csv"
        fixture(source)
        product = root / "product"
        first = publish(product, source, 3)
        before = (product / "current.json").read_bytes()
        source.write_text(source.read_text() + "D,99,4\n")
        rejected = publish(product, source, 4)
        assert rejected["accepted"] is False and rejected["quarantine_rows"] == 1
        assert (product / "current.json").read_bytes() == before
        assert current(product)["rows"] == first["rows"]
        assert len(list((product / "attempts").glob("*.json"))) == 2
        return {
            "rejected_candidate": rejected,
            "accepted_version_retained": first["version"],
            "prior_total": 6,
            "persistent_http_service_is_a_separate_project": True,
        }


def main():
    from ds60sqlpy.plot_artifacts import publish_report, publish_table

    first, second = example_one(), example_two()
    print("Actual complete data product:", first)
    print("Quality failure preserves the accepted publication:", second)
    publish_table(
        ["route", "region", "packages"],
        [[row["route"], row["region"], row["packages"]] for row in first["rows"]],
        description=(
            "Actual CSV to Polars to DuckDB to Parquet publication reconciles "
            "north five and south one packages."
        ),
    )
    publish_report(
        second,
        description=(
            "A source-bound invalid-route candidate is rejected while the "
            "earlier accepted six-package product remains available."
        ),
    )


if __name__ == "__main__":
    main()
