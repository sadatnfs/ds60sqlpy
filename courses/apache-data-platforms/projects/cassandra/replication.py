"""Actual RF3 ALL/ONE/QUORUM observations with one fixed live coordinator."""

from __future__ import annotations

import argparse
import json
import socket
import time

from cassandra import ConsistencyLevel, ReadTimeout, Unavailable
from cassandra.cluster import EXEC_PROFILE_DEFAULT, Cluster, ExecutionProfile, NoHostAvailable
from cassandra.policies import WhiteListRoundRobinPolicy
from cassandra.query import SimpleStatement, dict_factory

QUERY = "SELECT value FROM ds60_replicated.records WHERE key='fixture'"
EXPECTED = {"value": "three-replica-known-value"}


class ReplicaMembershipPending(RuntimeError):
    """Local listeners are up while the primary's peer view still converges."""


def _execute_once(phase: str) -> dict[str, object]:
    primary = socket.gethostbyname("cassandra")
    profile = ExecutionProfile(
        row_factory=dict_factory,
        request_timeout=10,
        load_balancing_policy=WhiteListRoundRobinPolicy([primary]),
    )
    cluster = Cluster(
        [primary],
        protocol_version=4,
        connect_timeout=5,
        control_connection_timeout=5,
        executor_threads=2,
        idle_heartbeat_interval=0,
        execution_profiles={EXEC_PROFILE_DEFAULT: profile},
    )
    try:
        session = cluster.connect()
        observed_nodes = len(list(cluster.metadata.all_hosts()))
        if observed_nodes != 3:
            if phase in {"inspect", "recovered"}:
                raise ReplicaMembershipPending(
                    "Expected three retained node identities; "
                    f"primary currently reports {observed_nodes}"
                )
            raise AssertionError("Expected exactly three real node identities")
        if phase == "prepare":
            session.execute(
                "CREATE KEYSPACE IF NOT EXISTS ds60_replicated WITH replication="
                "{'class':'NetworkTopologyStrategy','datacenter1':3}"
            )
            session.execute(
                "CREATE TABLE IF NOT EXISTS ds60_replicated.records "
                "(key text PRIMARY KEY,value text)"
            )
            configured = session.execute(
                "SELECT replication FROM system_schema.keyspaces "
                "WHERE keyspace_name='ds60_replicated'"
            ).one()
            mapping = configured["replication"] if configured else {}
            if (
                set(mapping) != {"class", "datacenter1"}
                or mapping.get("datacenter1") != "3"
                or not mapping.get("class", "").endswith("NetworkTopologyStrategy")
            ):
                raise AssertionError(
                    "Unexpected retained replication policy; no alteration performed"
                )
            existing = session.execute(
                SimpleStatement(QUERY, consistency_level=ConsistencyLevel.ALL)
            ).one()
            if existing is None:
                session.execute(
                    SimpleStatement(
                        "INSERT INTO ds60_replicated.records (key,value) "
                        "VALUES ('fixture','three-replica-known-value')",
                        consistency_level=ConsistencyLevel.ALL,
                    )
                )
            elif existing != EXPECTED:
                raise AssertionError("Unexpected retained replica fixture; no overwrite performed")
            if (
                session.execute(
                    SimpleStatement(QUERY, consistency_level=ConsistencyLevel.ALL)
                ).one()
                != EXPECTED
            ):
                raise AssertionError("ALL readback changed")
            return {
                "passed": True,
                "phase": phase,
                "actual_nodes": 3,
                "replication_factor": 3,
                "all_readback": True,
                "write_or_retained_state_confirmed_at_all": True,
            }
        configuration = session.execute(
            "SELECT replication FROM system_schema.keyspaces WHERE keyspace_name='ds60_replicated'"
        ).one()
        mapping = configuration["replication"] if configuration else {}
        if (
            set(mapping) != {"class", "datacenter1"}
            or mapping.get("datacenter1") != "3"
            or not mapping.get("class", "").endswith("NetworkTopologyStrategy")
        ):
            raise AssertionError("The retained keyspace is not the exact RF3/datacenter fixture")
        if phase == "inspect":
            own = session.execute("SELECT host_id FROM system.local").one()["host_id"]
            peers = [
                row["host_id"] for row in session.execute("SELECT host_id FROM system.peers_v2")
            ]
            identities = sorted({str(value) for value in [own, *peers]})
            if len(identities) != 3:
                raise AssertionError("Expected three retained unique database host identities")
            value = session.execute(
                SimpleStatement(QUERY, consistency_level=ConsistencyLevel.QUORUM)
            ).one()
            if value != EXPECTED:
                raise AssertionError("Read-only retained replica value changed")
            return {
                "host_ids": identities,
                "value": value,
                "replication": dict(mapping),
                "read_only_no_initialization": True,
            }
        if phase == "outage":
            if (
                session.execute(
                    SimpleStatement(QUERY, consistency_level=ConsistencyLevel.ONE)
                ).one()
                != EXPECTED
            ):
                raise AssertionError("Surviving replica did not return the original value")
            deadline = time.monotonic() + 45
            while True:
                try:
                    session.execute(
                        SimpleStatement(QUERY, consistency_level=ConsistencyLevel.QUORUM)
                    ).one()
                except (Unavailable, ReadTimeout, NoHostAvailable) as error:
                    causes = (
                        list(error.errors.values())
                        if isinstance(error, NoHostAvailable)
                        else [error]
                    )
                    if causes and all(
                        isinstance(cause, Unavailable)
                        and cause.required_replicas == 2
                        and cause.alive_replicas == 1
                        for cause in causes
                    ):
                        return {
                            "passed": True,
                            "phase": phase,
                            "one_readback": True,
                            "quorum_unavailable": True,
                            "required_replicas": 2,
                            "alive_replicas": 1,
                        }
                    if not causes or not all(
                        isinstance(cause, ReadTimeout)
                        and cause.required_responses == 2
                        and cause.received_responses == 1
                        for cause in causes
                    ):
                        raise
                    if time.monotonic() >= deadline:
                        raise AssertionError(
                            "Expected exact replica-shortage diagnostic after owned outage"
                        ) from error
                    time.sleep(0.5)
                else:
                    raise AssertionError(
                        "QUORUM unexpectedly succeeded with two owned nodes stopped"
                    )
        if phase == "recovered":
            if (
                session.execute(
                    SimpleStatement(QUERY, consistency_level=ConsistencyLevel.QUORUM)
                ).one()
                != EXPECTED
            ):
                raise AssertionError("Recovered quorum changed fixture value")
            return {"passed": True, "phase": phase, "quorum_readback_restored": True}
        raise ValueError("Unknown fixed phase")
    finally:
        cluster.shutdown()


def execute(phase: str) -> dict[str, object]:
    deadline = time.monotonic() + 60
    while True:
        try:
            return _execute_once(phase)
        except ReplicaMembershipPending as error:
            if phase not in {"inspect", "recovered"} or time.monotonic() >= deadline:
                raise RuntimeError(
                    "Read-only replica membership did not converge before its deadline"
                ) from error
            time.sleep(0.5)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["prepare", "outage", "recovered", "inspect"])
    args = parser.parse_args()
    print(json.dumps(execute(args.phase), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
