"""Actual DuckDB oracles for Pinot design; the separate workshop runs Pinot."""

import duckdb


def current_rows(connection, rows):
    seen = {}
    for identity, revision, region, packages, status in rows:
        key, value = (identity, revision), (region, packages, status)
        if key in seen and seen[key] != value:
            raise ValueError("Equal entity revision has conflicting content")
        seen[key] = value
    connection.execute(
        "create table events(id varchar,revision integer,region varchar,"
        "packages integer,status varchar)"
    )
    connection.executemany("insert into events values(?,?,?,?,?)", rows)
    connection.execute(
        "create view current as select id,revision,region,packages,status from events "
        "qualify row_number() over(partition by id order by revision desc)=1"
    )
    return connection.execute("select * from current order by id").fetchall()


def example_one():
    rows = [
        ("A", 1, "north", 2, "paid"),
        ("A", 2, "north", 4, "paid"),
        ("B", 1, "north", 3, "paid"),
        ("C", 1, "south", 1, "cancelled"),
        ("A", 1, "north", 2, "paid"),
    ]
    with duckdb.connect(":memory:") as connection:
        current = current_rows(connection, rows)
        append_total = connection.execute(
            "select sum(packages) from events where status='paid'"
        ).fetchone()[0]
        upsert_total = connection.execute(
            "select sum(packages) from current where status='paid'"
        ).fetchone()[0]
        assert append_total == 11 and upsert_total == 7
        assert len(current) == 3
        return {
            "append_interpretation_paid_packages": append_total,
            "latest_entity_interpretation_paid_packages": upsert_total,
            "current_entity_count": len(current),
            "actual_engine": "DuckDB oracle, not Pinot",
        }


def example_two():
    rows = [
        ("A", 1, "north", 2, "paid"),
        ("B", 1, "north", 3, "paid"),
        ("A", 2, "south", 4, "paid"),
    ]
    with duckdb.connect(":memory:") as connection:
        current_rows(connection, rows)
        correct = dict(
            connection.execute(
                "select region,sum(packages) from current group by region"
            ).fetchall()
        )
        append = dict(
            connection.execute("select region,sum(packages) from events group by region").fetchall()
        )
        assert correct == {"north": 3, "south": 4} and append == {"north": 5, "south": 4}
        corrected = {"north": 5 - 2, "south": 0 + 4}
        assert corrected == correct
        return {
            "latest_entity_grouping": correct,
            "append_only_aggregate_error": append,
            "required_old_value_retraction": {"north": -2},
            "lost_entity_identity_prevents_general_correction": True,
        }


def main():
    print("Choose append versus entity replacement explicitly:", example_one())
    print("Changing a grouping key requires a retraction or recomputation:", example_two())


if __name__ == "__main__":
    main()
