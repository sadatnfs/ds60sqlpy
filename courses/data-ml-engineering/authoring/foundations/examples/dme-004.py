"""Execute actual SQL and reconcile each result with identified input rows."""

import duckdb


def database():
    connection = duckdb.connect(":memory:")
    connection.execute(
        "create table deliveries(id integer primary key, route_id integer, packages integer)"
    )
    connection.execute("insert into deliveries values (1,10,2),(2,10,3),(3,20,1)")
    connection.execute("create table routes(route_id integer primary key, name varchar)")
    connection.execute("insert into routes values (10,'north'),(20,'south')")
    return connection


def example_one():
    with database() as connection:
        result = connection.execute(
            "select r.route_id, r.name, sum(d.packages) as packages from deliveries d "
            "join routes r using(route_id) group by r.route_id, r.name order by r.route_id"
        ).fetchall()
        assert result == [(10, "north", 5), (20, "south", 1)]
        assert sum(packages for _, _, packages in result) == 2 + 3 + 1
        return {"packages_by_route": result, "input_delivery_rows": 3, "output_route_rows": 2}


def example_two():
    with database() as connection:
        connection.execute(
            "create table unvalidated_routes as select * from routes "
            "union all select 10,'duplicate'"
        )
        wrong = connection.execute(
            "select sum(d.packages) from deliveries d join unvalidated_routes r using(route_id)"
        ).fetchone()[0]
        duplicate_keys = connection.execute(
            "select route_id from unvalidated_routes group by route_id having count(*) <> 1"
        ).fetchall()
        assert wrong == 11 and duplicate_keys == [(10,)]
        connection.execute("create table observations(delay_minutes integer)")
        connection.execute("insert into observations values (0),(10),(NULL)")
        counts = connection.execute(
            "select count(*), count(delay_minutes), avg(delay_minutes) from observations"
        ).fetchone()
        assert counts == (3, 2, 5.0)
        return {
            "fanout_total": wrong,
            "correct_packages": 6,
            "violating_route_keys": duplicate_keys,
            "all_rows_known_values_mean": counts,
        }


def main():
    print("Identified relational aggregation:", example_one())
    print("Changed key and missing-value assumptions:", example_two())


if __name__ == "__main__":
    main()
