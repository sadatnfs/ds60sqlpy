"""Synthetic local minimization and retention rules with actual DuckDB queries."""

import hashlib
import hmac
from datetime import date, timedelta

import duckdb


def database():
    connection = duckdb.connect(":memory:")
    connection.execute(
        "create table observations(person varchar,region varchar,age_band varchar,"
        "packages integer,observed date)"
    )
    connection.executemany(
        "insert into observations values(?,?,?,?,?)",
        [
            ("person-a", "north", "20s", 2, "2024-01-01"),
            ("person-b", "north", "20s", 3, "2024-01-08"),
            ("person-c", "south", "30s", 1, "2024-01-09"),
            ("person-d", "south", "40s", 4, "2024-01-10"),
        ],
    )
    return connection


def aggregate(connection, role, purpose, minimum_count=2):
    if role != "analyst" or purpose != "capacity-planning":
        raise PermissionError("Synthetic purpose and role are not authorized")
    if type(minimum_count) is not int or minimum_count < 2:
        raise ValueError("The reviewed aggregation policy requires at least two people")
    return connection.execute(
        "select region,age_band,count(*),sum(packages) from observations "
        "group by region,age_band having count(*)>=? order by region,age_band",
        [minimum_count],
    ).fetchall()


def example_one():
    with database() as connection:
        result = aggregate(connection, "analyst", "capacity-planning")
        assert result == [("north", "20s", 2, 5)]
        candidates = connection.execute(
            "select region,age_band,count(*) from observations "
            "group by region,age_band order by region,age_band"
        ).fetchall()
        assert candidates == [("north", "20s", 2), ("south", "30s", 1), ("south", "40s", 1)]
        try:
            aggregate(connection, "trainer", "model-training")
        except PermissionError:
            denied = True
        else:
            raise AssertionError("An unapproved purpose was accepted")
        return {
            "released_groups": result,
            "suppressed_small_groups": 2,
            "other_purpose_denied": denied,
            "scope": "synthetic application policy, not a privacy guarantee or legal standard",
        }


def example_two():
    with database() as connection:
        rows = connection.execute(
            "select person,region,age_band from observations order by person"
        ).fetchall()
        public_synthetic_lookup = {("south", "30s"): "person-c", ("south", "40s"): "person-d"}
        key = b"synthetic-classroom-key"
        pseudonyms = [
            (hmac.new(key, person.encode(), hashlib.sha256).hexdigest()[:16], region, age)
            for person, region, age in rows
        ]
        reidentified = [
            public_synthetic_lookup[(region, age)]
            for _, region, age in pseudonyms
            if (region, age) in public_synthetic_lookup
        ]
        assert reidentified == ["person-c", "person-d"]
        cutoff = date(2024, 1, 11) - timedelta(days=7)
        before = connection.execute("select count(*) from observations").fetchone()[0]
        connection.execute("delete from observations where observed < ?", [cutoff])
        after = connection.execute("select count(*) from observations").fetchone()[0]
        retained = [
            row[0]
            for row in connection.execute(
                "select person from observations order by person"
            ).fetchall()
        ]
        assert retained == ["person-b", "person-c", "person-d"] and before - after == 1
        return {
            "pseudonymized_rows_still_linkable": reidentified,
            "retention_audit": {
                "cutoff_inclusive": str(cutoff),
                "before": before,
                "after": after,
                "removed": before - after,
            },
            "external_copies_backups_and_models_were_not_deleted": True,
        }


def main():
    from ds60sqlpy.plot_artifacts import publish_report, publish_table

    first, second = example_one(), example_two()
    print("Minimize output and retain suppressed-population accounting:", first)
    print("Pseudonymization limits and an actual local retention operation:", second)
    publish_table(
        ["region", "age_band", "people", "packages"],
        [list(row) for row in first["released_groups"]],
        description=(
            "Synthetic release policy exposes one group of two people and "
            "suppresses two singleton groups."
        ),
    )
    publish_report(
        second,
        description=(
            "Synthetic linkage risk and local retention counts; external "
            "copies and models are outside this operation."
        ),
    )


if __name__ == "__main__":
    main()
