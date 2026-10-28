"""A real local DuckDB metadata catalog with a synthetic application policy, not external IAM."""

import json

import duckdb

CONTRACT = {"grain": ["delivery_id"], "units": "packages", "fields": ["delivery_id", "packages"]}


def database():
    connection = duckdb.connect(":memory:")
    connection.execute(
        "create table datasets(name varchar primary key,owner varchar,accepted integer)"
    )
    connection.execute(
        "create table versions(name varchar,version integer,contract varchar,"
        "artifact_sha varchar,primary key(name,version))"
    )
    connection.execute(
        "create table grants(name varchar,role varchar,action varchar,"
        "primary key(name,role,action))"
    )
    connection.execute("insert into datasets values('deliveries','data-team',0)")
    connection.executemany(
        "insert into grants values('deliveries',?,?)",
        [("analyst", "read"), ("curator", "read"), ("curator", "publish")],
    )
    return connection


def authorize(connection, name, role, action):
    if (
        connection.execute(
            "select count(*) from grants where name=? and role=? and action=?", [name, role, action]
        ).fetchone()[0]
        != 1
    ):
        raise PermissionError("Synthetic application policy denies this resource action")


def register(connection, version, contract, digest):
    if type(version) is not int or version < 1 or len(digest) != 64:
        raise ValueError("Use an identified version and declared artifact digest")
    connection.execute(
        "insert into versions values('deliveries',?,?,?)",
        [version, json.dumps(contract, sort_keys=True), digest],
    )


def activate(connection, version, role, expected):
    authorize(connection, "deliveries", role, "publish")
    connection.execute("begin")
    try:
        current = connection.execute(
            "select accepted from datasets where name='deliveries'"
        ).fetchone()[0]
        if current != expected:
            raise ValueError("Accepted catalog version changed")
        candidate = connection.execute(
            "select contract from versions where name='deliveries' and version=?", [version]
        ).fetchone()
        if candidate is None:
            raise ValueError("Candidate version is not registered")
        contract = json.loads(candidate[0])
        if (
            contract["grain"] != CONTRACT["grain"]
            or contract["units"] != CONTRACT["units"]
            or not set(CONTRACT["fields"]) <= set(contract["fields"])
        ):
            raise ValueError("Candidate violates the maintained consumer contract")
        connection.execute("update datasets set accepted=? where name='deliveries'", [version])
        connection.execute("commit")
    except Exception:
        connection.execute("rollback")
        raise


def resolve(connection, role):
    authorize(connection, "deliveries", role, "read")
    value = connection.execute(
        "select d.name,d.owner,v.version,v.contract,v.artifact_sha from datasets d "
        "join versions v on d.name=v.name and d.accepted=v.version "
        "where d.name='deliveries'"
    ).fetchone()
    if value is None:
        raise ValueError("No accepted dataset version is available")
    return {
        "name": value[0],
        "owner": value[1],
        "version": value[2],
        "contract": json.loads(value[3]),
        "artifact_sha": value[4],
    }


def example_one():
    with database() as connection:
        register(connection, 1, CONTRACT, "a" * 64)
        activate(connection, 1, "curator", 0)
        register(connection, 2, {**CONTRACT, "fields": [*CONTRACT["fields"], "region"]}, "b" * 64)
        before = resolve(connection, "analyst")
        assert before["version"] == 1
        activate(connection, 2, "curator", 1)
        after = resolve(connection, "analyst")
        assert after["version"] == 2 and after["owner"] == "data-team"
        return {
            "registered_is_not_accepted": before["version"],
            "accepted_after_review": after,
            "artifact_digest_is_metadata_not_readback": True,
        }


def example_two():
    with database() as connection:
        register(connection, 1, CONTRACT, "a" * 64)
        activate(connection, 1, "curator", 0)
        register(connection, 2, {**CONTRACT, "units": "kilograms"}, "b" * 64)
        rejected = []
        for role, expected in [("analyst", 1), ("curator", 0), ("curator", 1)]:
            try:
                activate(connection, 2, role, expected)
            except (PermissionError, ValueError) as error:
                rejected.append(type(error).__name__)
        try:
            resolve(connection, "unapproved-trainer")
        except PermissionError:
            rejected.append("PermissionError")
        assert rejected == ["PermissionError", "ValueError", "ValueError", "PermissionError"]
        assert resolve(connection, "analyst")["version"] == 1
        return {
            "rejected_unauthorized_stale_incompatible_and_ungranted": rejected,
            "accepted_version_preserved": 1,
            "scope": "application checks, not database-role or cloud IAM enforcement",
        }


def main():
    print("Discover a reviewed dataset version:", example_one())
    print("Policy and compatibility decisions:", example_two())


if __name__ == "__main__":
    main()
