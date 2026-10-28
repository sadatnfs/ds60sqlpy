"""Actual dimensional joins and historical-interval validation in DuckDB."""

import duckdb


def database():
    connection = duckdb.connect(":memory:")
    connection.execute(
        "create table deliveries(id integer primary key, "
        "route_id integer, packages integer, event_day "
        "date)"
    )
    connection.execute(
        "insert into deliveries values "
        "(1,10,2,'2024-01-15'),(2,10,3,'2024-02-01'),(3,20,1,'20"
        "24-02-02')"
    )
    connection.execute(
        "create table history(route_id integer,region "
        "varchar,valid_from date,valid_to date,primary "
        "key(route_id,valid_from),check(valid_to is null or "
        "valid_to>valid_from))"
    )
    connection.execute(
        "insert into history values "
        "(10,'north','2024-01-01','2024-02-01'),(10,'west','2024"
        "-02-01',NULL),(20,'south','2024-01-01',NULL)"
    )
    return connection


def matches(connection):
    return connection.execute(
        "select d.id,count(h.route_id) as matches from "
        "deliveries d left join history h on "
        "d.route_id=h.route_id and d.event_day>=h.valid_from "
        "and (h.valid_to is null or d.event_day<h.valid_to) "
        "group by d.id order by "
        "d.id"
    ).fetchall()


def example_one():
    with database() as connection:
        assert matches(connection) == [(1, 1), (2, 1), (3, 1)]
        historical = connection.execute(
            "select d.id,h.region,d.packages from deliveries d join "
            "history h on d.route_id=h.route_id and "
            "d.event_day>=h.valid_from and (h.valid_to is null or "
            "d.event_day<h.valid_to) order by "
            "d.id"
        ).fetchall()
        current = connection.execute(
            "select d.id,h.region,d.packages from deliveries d join "
            "history h using(route_id) where h.valid_to is null "
            "order by d.id"
        ).fetchall()
        assert historical == [(1, "north", 2), (2, "west", 3), (3, "south", 1)]
        assert current == [(1, "west", 2), (2, "west", 3), (3, "south", 1)]
        return {
            "historical_business_classification": historical,
            "current_classification": current,
            ("boundary_day_uses_new_interval"): True,
        }


def example_two():
    with database() as connection:
        connection.execute("insert into history values (10,'east','2024-01-10','2024-02-10')")
        connection.execute("insert into deliveries values (4,99,4,'2024-01-15')")
        cardinality = matches(connection)
        assert cardinality == [(1, 2), (2, 2), (3, 1), (4, 0)]
        overlaps = connection.execute(
            "select a.route_id,a.region,b.region from history a "
            "join history b on a.route_id=b.route_id and "
            "a.valid_from<b.valid_from and (a.valid_to is null or "
            "b.valid_from<a.valid_to) order by "
            "a.valid_from"
        ).fetchall()
        assert len(overlaps) == 2 and all(row[0] == 10 for row in overlaps)
        accepted = all(count == 1 for _, count in cardinality) and not overlaps
        assert accepted is False
        return {
            "matches_per_delivery": cardinality,
            "overlapping_interval_pairs": overlaps,
            ("publishable"): accepted,
            ("primary_key_did_not_prevent_interval_overlap"): True,
        }


def main():
    print("A declared historical interpretation:", example_one())
    print("Overlap and missing relationships are observable failures:", example_two())


if __name__ == "__main__":
    main()
