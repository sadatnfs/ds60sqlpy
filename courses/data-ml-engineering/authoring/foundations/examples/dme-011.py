"""Apply declared synthetic change events to actual local SQLite state."""

import sqlite3


def database():
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "create table state(delivery_id text primary key, "
        "source_version integer not null, deleted integer not "
        "null, packages integer)"
    )
    return connection


def apply_event(connection, delivery_id, version, operation, packages=None):
    if not isinstance(delivery_id, str) or not delivery_id.strip():
        raise ValueError("A delivery identity is required")
    if type(version) is not int or version < 1 or operation not in {"upsert", "delete"}:
        raise ValueError("Invalid source version or operation")
    if operation == "upsert" and (type(packages) is not int or packages < 1):
        raise ValueError("Upserts require a positive integer package count")
    if operation == "delete" and packages is not None:
        raise ValueError("A delete carries a tombstone, not a package measurement")
    incoming = (version, int(operation == "delete"), packages)
    with connection:
        connection.execute("begin immediate")
        prior = connection.execute(
            ("select source_version,deleted,packages from state where delivery_id=?"),
            (delivery_id,),
        ).fetchone()
        if prior is not None:
            if version < prior[0]:
                return "stale"
            if version == prior[0]:
                if incoming != prior:
                    raise ValueError("One source version names conflicting changes")
                return "replayed"
        connection.execute(
            (
                "insert into state values(?,?,?,?) on "
                "conflict(delivery_id) do update set "
                "source_version=excluded.source_version,deleted=excluded"
                ".deleted,packages=excluded.packages"
            ),
            (delivery_id, *incoming),
        )
    return "applied"


def visible(connection):
    return connection.execute(
        "select delivery_id,packages from state where deleted=0 order by delivery_id"
    ).fetchall()


def example_one():
    connection = database()
    try:
        outcomes = [
            apply_event(connection, "A", 1, "upsert", 2),
            apply_event(connection, "A", 2, "upsert", 5),
            apply_event(connection, "A", 2, "upsert", 5),
            apply_event(connection, "B", 1, "upsert", 3),
        ]
        assert outcomes == ["applied", "applied", "replayed", "applied"]
        assert visible(connection) == [("A", 5), ("B", 3)]
        return {"outcomes": outcomes, "current_rows": visible(connection), "package_total": 8}
    finally:
        connection.close()


def example_two():
    connection = database()
    try:
        apply_event(connection, "A", 1, "upsert", 2)
        apply_event(connection, "B", 1, "upsert", 3)
        apply_event(connection, "A", 3, "delete")
        assert apply_event(connection, "A", 2, "upsert", 99) == "stale"
        assert apply_event(connection, "A", 3, "delete") == "replayed"
        try:
            apply_event(connection, "A", 3, "upsert", 7)
        except ValueError:
            conflict_rejected = True
        else:
            raise AssertionError("An equal source version cannot change its meaning")
        assert visible(connection) == [("B", 3)]
        assert connection.execute(
            "select source_version,deleted from state where delivery_id='A'"
        ).fetchone() == (3, 1)
        return {
            "visible_rows": visible(connection),
            "tombstone_version": 3,
            ("stale_resurrection_rejected"): True,
            ("conflict_rejected"): conflict_rejected,
            ("scope"): ("synthetic event application; no WAL capture or broker was run"),
        }
    finally:
        connection.close()


def main():
    print("Ordered identified change application:", example_one())
    print("Deletes still need version memory:", example_two())


if __name__ == "__main__":
    main()
