"""Real bounded CQL checks against the copied project's actual Cassandra node."""

from __future__ import annotations

import argparse
import json
import os
import socket
import time
from datetime import date, datetime

from cassandra import ConsistencyLevel, InvalidRequest, ReadFailure, Unavailable
from cassandra.cluster import EXEC_PROFILE_DEFAULT, Cluster, ExecutionProfile, NoHostAvailable
from cassandra.policies import WhiteListRoundRobinPolicy
from cassandra.query import SimpleStatement, dict_factory

PARTITION_KEYS = "WHERE customer_id='alpha' AND day_bucket='2026-01-01'"
ROW_QUERY = (
    "SELECT customer_id,day_bucket,ordered_at,order_id,amount FROM ds60_orders.by_customer LIMIT 4"
)
ID_QUERY = "SELECT order_id FROM ds60_orders.by_customer " + PARTITION_KEYS

EXPECTED = [
    ("alpha", date(2026, 1, 1), datetime(2026, 1, 1, 0, 0), 1, 4),
    ("beta", date(2026, 1, 1), datetime(2026, 1, 1, 0, 30), 2, 9),
    ("alpha", date(2026, 1, 1), datetime(2026, 1, 1, 1, 0), 3, 7),
]


def check(*, health: bool = False, identity: bool = False) -> dict[str, object]:
    contact = os.environ.get("DS60_CASSANDRA_NODE", "cassandra")
    if contact not in {"cassandra", "cassandra-two", "cassandra-three"}:
        raise ValueError("Unapproved fixed workshop node identity")
    primary = socket.gethostbyname(contact)
    profile = ExecutionProfile(
        consistency_level=ConsistencyLevel.ONE,
        request_timeout=5,
        row_factory=dict_factory,
        load_balancing_policy=WhiteListRoundRobinPolicy([primary]),
    )
    cluster = Cluster(
        [primary],
        port=9042,
        protocol_version=4,
        connect_timeout=5,
        control_connection_timeout=5,
        idle_heartbeat_interval=0,
        executor_threads=2,
        max_schema_agreement_wait=5,
        execution_profiles={EXEC_PROFILE_DEFAULT: profile},
    )
    try:
        session = cluster.connect()
        local = session.execute(
            "SELECT release_version,data_center,host_id,cluster_name FROM system.local"
        ).one()
        if not local or local["release_version"] != "5.0.9":
            raise AssertionError("Unexpected Cassandra release")
        if health:
            return {"healthy": True, "release": local["release_version"]}
        if identity:
            orders = [
                {
                    "customer_id": row["customer_id"],
                    "day_bucket": str(row["day_bucket"]),
                    "ordered_at": row["ordered_at"].isoformat(),
                    "order_id": row["order_id"],
                    "amount": row["amount"],
                }
                for row in session.execute(ROW_QUERY)
            ]
            return {
                "host_id": str(local["host_id"]),
                "cluster_name": local["cluster_name"],
                "orders": sorted(orders, key=lambda row: row["order_id"]),
                "read_only_no_initialization": True,
            }
        if local["data_center"] != "datacenter1":
            raise AssertionError("Pinned single-datacenter fixture changed")
        session.execute(
            "CREATE KEYSPACE IF NOT EXISTS ds60_orders WITH replication = "
            "{'class':'NetworkTopologyStrategy','datacenter1':1}"
        )
        session.execute(
            "CREATE TABLE IF NOT EXISTS ds60_orders.by_customer "
            "(customer_id text, day_bucket date, ordered_at timestamp, order_id int, amount int, "
            "PRIMARY KEY ((customer_id, day_bucket), ordered_at, order_id)) "
            "WITH CLUSTERING ORDER BY (ordered_at DESC, order_id ASC)"
        )
        current = list(session.execute(ROW_QUERY))
        if not current:
            insert = session.prepare(
                "INSERT INTO ds60_orders.by_customer "
                "(customer_id,day_bucket,ordered_at,order_id,amount) VALUES (?,?,?,?,?)"
            )
            for row in EXPECTED:
                session.execute(insert, row)
        rows = list(session.execute(ROW_QUERY))
        actual = sorted(
            (
                row["customer_id"],
                str(row["day_bucket"]),
                row["ordered_at"],
                row["order_id"],
                row["amount"],
            )
            for row in rows
        )
        if actual != sorted(
            (customer, day.isoformat(), event, identity, amount)
            for customer, day, event, identity, amount in EXPECTED
        ):
            raise AssertionError("Unexpected retained orders; no reset performed")
        alpha = list(
            session.execute("SELECT order_id,amount FROM ds60_orders.by_customer " + PARTITION_KEYS)
        )
        if alpha != [{"order_id": 3, "amount": 7}, {"order_id": 1, "amount": 4}]:
            raise AssertionError("Partition-local clustering order changed")
        window = list(session.execute(ID_QUERY + " AND ordered_at >= '2026-01-01T00:30:00Z'"))
        if window != [{"order_id": 3}]:
            raise AssertionError("Bounded clustering timestamp range changed")
        try:
            session.execute("SELECT * FROM ds60_orders.by_customer WHERE amount=7")
        except InvalidRequest as error:
            if "filtering" not in str(error).lower():
                raise
        else:
            raise AssertionError("Unapproved unindexed filter unexpectedly accepted")
        for consistency in [ConsistencyLevel.ONE, ConsistencyLevel.QUORUM]:
            statement = SimpleStatement(
                ID_QUERY,
                consistency_level=consistency,
            )
            if len(list(session.execute(statement))) != 2:
                raise AssertionError("RF1 read changed")
        try:
            session.execute(
                SimpleStatement(
                    ID_QUERY,
                    consistency_level=ConsistencyLevel.TWO,
                )
            )
        except (Unavailable, NoHostAvailable) as error:
            causes = list(error.errors.values()) if isinstance(error, NoHostAvailable) else [error]
            if not causes or any(
                not isinstance(cause, Unavailable)
                or cause.required_replicas != 2
                or cause.alive_replicas != 1
                for cause in causes
            ):
                raise
        else:
            raise AssertionError("Two-replica consistency unexpectedly succeeded on RF1")
        session.execute(
            "CREATE TABLE IF NOT EXISTS ds60_orders.inventory (item text PRIMARY KEY,available int)"
        )
        session.execute(
            "INSERT INTO ds60_orders.inventory (item,available) VALUES ('demo',7) IF NOT EXISTS"
        )
        initial = session.execute(
            "SELECT available FROM ds60_orders.inventory WHERE item='demo'"
        ).one()
        if initial != {"available": 7}:
            raise AssertionError("Unexpected retained CAS fixture; no reset performed")
        successful = session.execute(
            "UPDATE ds60_orders.inventory SET available=6 WHERE item='demo' IF available=7"
        ).one()
        rejected = session.execute(
            "UPDATE ds60_orders.inventory SET available=5 WHERE item='demo' IF available=7"
        ).one()
        if not successful["[applied]"] or rejected["[applied]"] or rejected["available"] != 6:
            raise AssertionError("Actual conditional-update results differ")
        restored = session.execute(
            "UPDATE ds60_orders.inventory SET available=7 WHERE item='demo' IF available=6"
        ).one()
        if not restored["[applied]"]:
            raise AssertionError("Could not conditionally restore this probe's known fixture")
        session.execute(
            "CREATE TABLE IF NOT EXISTS ds60_orders.clocked (key text PRIMARY KEY,value text)"
        )
        session.execute(
            "INSERT INTO ds60_orders.clocked (key,value) VALUES ('demo','initial') "
            "USING TIMESTAMP 1700000000000000"
        )
        session.execute(
            "UPDATE ds60_orders.clocked USING TIMESTAMP 1700000000000010 "
            "SET value='newest' WHERE key='demo'"
        )
        session.execute(
            "UPDATE ds60_orders.clocked USING TIMESTAMP 1700000000000005 "
            "SET value='stale' WHERE key='demo'"
        )
        if session.execute("SELECT value FROM ds60_orders.clocked WHERE key='demo'").one() != {
            "value": "newest"
        }:
            raise AssertionError("Explicit last-write timestamp rule changed")
        session.execute(
            "CREATE TABLE IF NOT EXISTS ds60_orders.indexed_orders "
            "(order_id int PRIMARY KEY,amount int)"
        )
        indexed = list(
            session.execute("SELECT order_id,amount FROM ds60_orders.indexed_orders LIMIT 4")
        )
        if not indexed:
            prepared = session.prepare(
                "INSERT INTO ds60_orders.indexed_orders (order_id,amount) VALUES (?,?)"
            )
            for _, _, _, identity, amount in EXPECTED:
                session.execute(prepared, (identity, amount))
        indexed = list(
            session.execute("SELECT order_id,amount FROM ds60_orders.indexed_orders LIMIT 4")
        )
        if sorted((row["order_id"], row["amount"]) for row in indexed) != [(1, 4), (2, 9), (3, 7)]:
            raise AssertionError("Unexpected retained index fixture; no reset performed")
        session.execute(
            "CREATE CUSTOM INDEX IF NOT EXISTS amount_sai ON "
            "ds60_orders.indexed_orders(amount) USING 'StorageAttachedIndex'"
        )
        metadata = session.execute(
            "SELECT kind,options FROM system_schema.indexes WHERE keyspace_name='ds60_orders' "
            "AND table_name='indexed_orders' AND index_name='amount_sai'"
        ).one()
        if (
            not metadata
            or metadata["kind"] != "CUSTOM"
            or not metadata["options"].get("class_name", "").endswith("StorageAttachedIndex")
        ):
            raise AssertionError("Expected real Storage Attached Index metadata")
        index_deadline = time.monotonic() + 15
        while True:
            try:
                selected = list(
                    session.execute(
                        "SELECT order_id FROM ds60_orders.indexed_orders WHERE amount=7"
                    )
                )
            except (InvalidRequest, ReadFailure, NoHostAvailable) as error:
                causes = (
                    list(error.errors.values()) if isinstance(error, NoHostAvailable) else [error]
                )
                if not causes or any(
                    not isinstance(cause, (InvalidRequest, ReadFailure))
                    or not (
                        "index_not_available" in str(cause).lower()
                        or (
                            "index" in str(cause).lower()
                            and any(
                                word in str(cause).lower()
                                for word in ["queryable", "building", "not ready"]
                            )
                        )
                    )
                    for cause in causes
                ):
                    raise
                if time.monotonic() >= index_deadline:
                    raise AssertionError(
                        "Actual SAI did not become queryable before its deadline"
                    ) from error
                time.sleep(0.25)
            else:
                if selected != [{"order_id": 3}]:
                    raise AssertionError(
                        "Actual SAI lookup differs from independent identity oracle"
                    )
                break
        session.execute(
            "CREATE TABLE IF NOT EXISTS ds60_orders.expiring (key text PRIMARY KEY,value text)"
        )
        session.execute("INSERT INTO ds60_orders.expiring (key,value) VALUES ('deleted','demo')")
        if session.execute("SELECT value FROM ds60_orders.expiring WHERE key='deleted'").one() != {
            "value": "demo"
        }:
            raise AssertionError("Deletion fixture was not first observed live")
        session.execute("DELETE FROM ds60_orders.expiring WHERE key='deleted'")
        if (
            session.execute("SELECT value FROM ds60_orders.expiring WHERE key='deleted'").one()
            is not None
        ):
            raise AssertionError("Logical delete still returns the value")
        session.execute(
            "INSERT INTO ds60_orders.expiring (key,value) VALUES ('transient','demo') USING TTL 5"
        )
        ttl = session.execute(
            "SELECT TTL(value) AS remaining FROM ds60_orders.expiring WHERE key='transient'"
        ).one()
        if not ttl or not 0 < ttl["remaining"] <= 5:
            raise AssertionError("No actual positive TTL observed")
        deadline = time.monotonic() + 15
        while (
            session.execute("SELECT value FROM ds60_orders.expiring WHERE key='transient'").one()
            is not None
        ):
            if time.monotonic() >= deadline:
                raise AssertionError("TTL did not expire within its bounded observation")
            time.sleep(0.25)
        return {
            "passed": True,
            "product": "Apache Cassandra",
            "version": "5.0.9",
            "retained_orders": 3,
            "alpha_ids_descending_time": [3, 1],
            "unindexed_filter_rejected": True,
            "rf1_one_and_quorum_passed": True,
            "two_replicas_unavailable": True,
            "cas_success_and_stale_rejection": True,
            "explicit_timestamp_order": True,
            "logical_ttl_expiry": True,
            "logical_delete_observed": True,
            "actual_storage_attached_index": True,
            "replication_or_physical_erasure_demonstrated": False,
        }
    finally:
        cluster.shutdown()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--health", action="store_true")
    parser.add_argument("--identity", action="store_true")
    args = parser.parse_args()
    print(json.dumps(check(health=args.health, identity=args.identity), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
