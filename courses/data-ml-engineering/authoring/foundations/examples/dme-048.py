"""Actual SQLite expand/backfill/activate/rollback with versioned consumer contracts."""

import sqlite3


def database():
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "create table deliveries(id text primary key not null,packages integer not null)"
    )
    connection.executemany("insert into deliveries values(?,?)", [("A", 2), ("B", 3), ("C", 1)])
    connection.execute("create table deployment(id integer primary key,reader integer not null)")
    connection.execute("insert into deployment values(1,1)")
    connection.commit()
    return connection


def read(connection, version):
    if version == 1:
        return connection.execute("select id,packages from deliveries order by id").fetchall()
    if version == 2:
        result = connection.execute(
            "select id,packages,region from deliveries order by id"
        ).fetchall()
        if any(region is None or not region for _, _, region in result):
            raise ValueError("New reader requires a complete region backfill")
        return result
    raise ValueError("Unsupported consumer contract version")


def expand(connection):
    fields = {row[1] for row in connection.execute("pragma table_info(deliveries)")}
    if "region" not in fields:
        with connection:
            connection.execute("alter table deliveries add column region text")


def activate(connection, version, expected):
    with connection:
        connection.execute("begin immediate")
        current = connection.execute("select reader from deployment where id=1").fetchone()[0]
        if current != expected:
            raise ValueError("Accepted reader version changed")
        result = read(connection, version)
        connection.execute("update deployment set reader=? where id=1", (version,))
    return result


def fill_regions(connection):
    with connection:
        connection.executemany(
            "update deliveries set region=? where id=?",
            [("north", "A"), ("north", "B"), ("south", "C")],
        )


def example_one():
    connection = database()
    try:
        baseline = read(connection, 1)
        expand(connection)
        assert read(connection, 1) == baseline
        try:
            activate(connection, 2, 1)
        except ValueError:
            pass
        else:
            raise AssertionError("Incomplete migration was activated")
        assert connection.execute("select reader from deployment").fetchone() == (1,)
        fill_regions(connection)
        new = activate(connection, 2, 1)
        assert new == [("A", 2, "north"), ("B", 3, "north"), ("C", 1, "south")]
        assert read(connection, 1) == baseline
        return {
            "old_reader_while_schema_expands": baseline,
            "new_reader_after_backfill": new,
            "early_activation_rejected": True,
        }
    finally:
        connection.close()


def example_two():
    connection = database()
    try:
        expand(connection)
        fill_regions(connection)
        activate(connection, 2, 1)
        try:
            activate(connection, 3, 2)
        except ValueError:
            pass
        else:
            raise AssertionError("Unimplemented consumer version was activated")
        assert connection.execute("select reader from deployment").fetchone() == (2,)
        rolled_back = activate(connection, 1, 2)
        assert rolled_back == [("A", 2), ("B", 3), ("C", 1)]
        assert "region" in {row[1] for row in connection.execute("pragma table_info(deliveries)")}
        assert read(connection, 2) == [("A", 2, "north"), ("B", 3, "north"), ("C", 1, "south")]
        return {
            "accepted_reader_after_rollback": 1,
            "retained_additive_schema": True,
            "new_field_values_preserved": True,
            "rollback_did_not_drop_columns_or_reverse_external_effects": True,
        }
    finally:
        connection.close()


def main():
    print("Separate schema expansion, backfill and consumer activation:", example_one())
    print("Compatible rollback preserves useful new data:", example_two())


if __name__ == "__main__":
    main()
