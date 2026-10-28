"""Restore actual snapshot SSTables into one bounded owned evidence table.

Run inside the node container through run.sh check-backup. Original tables are
never truncated/dropped. At most four successful or partial restore targets are
retained until the project's explicit confirmed data destruction.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

from backup_receipts import save_receipt
from cassandra.cluster import EXEC_PROFILE_DEFAULT, Cluster, ExecutionProfile
from cassandra.query import dict_factory
from client import EXPECTED, ROW_QUERY


def exact_orders(rows: list[dict[str, Any]]) -> None:
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
    expected = sorted(
        (customer, day.isoformat(), event, identity, amount)
        for customer, day, event, identity, amount in EXPECTED
    )
    if actual != expected:
        raise AssertionError("Snapshot/restore rows differ from independent fixture oracle")


def tool(*arguments: str) -> None:
    result = subprocess.run(
        ["/opt/cassandra/bin/nodetool", "-h", "127.0.0.1", *arguments],
        timeout=45,
        capture_output=True,
        text=True,
        env=os.environ | {"MAX_HEAP_SIZE": "128M"},
    )
    if result.returncode:
        raise RuntimeError(
            "Bounded nodetool action failed: " + (result.stderr + result.stdout)[-4000:]
        )


def main() -> int:
    profile = ExecutionProfile(row_factory=dict_factory, request_timeout=10)
    cluster = Cluster(
        ["cassandra"],
        protocol_version=4,
        connect_timeout=5,
        control_connection_timeout=5,
        executor_threads=2,
        idle_heartbeat_interval=0,
        execution_profiles={EXEC_PROFILE_DEFAULT: profile},
    )
    tag = "ds60-restore-" + uuid.uuid4().hex[:16]
    target = "restore_" + uuid.uuid4().hex[:16]
    snapshot_created = False
    result: dict[str, Any] = {}
    failure: BaseException | None = None
    try:
        session = cluster.connect()
        if len(list(cluster.metadata.all_hosts())) != 1:
            raise ValueError(
                "This bounded table-snapshot restore is qualified only for the single-node topology"
            )
        exact_orders(list(session.execute(ROW_QUERY)))
        names = [
            row["table_name"]
            for row in session.execute(
                "SELECT table_name FROM system_schema.tables WHERE keyspace_name='ds60_orders'"
            )
        ]
        if len([name for name in names if name.startswith("restore_")]) >= 4:
            raise ValueError(
                "Four restore targets are already retained. Preserve/export evidence, "
                "then use a fresh owned workshop or its explicit confirmed destruction."
            )
        source = session.execute(
            "SELECT id FROM system_schema.tables "
            "WHERE keyspace_name='ds60_orders' AND table_name='by_customer'"
        ).one()
        if not source:
            raise AssertionError("Source table metadata missing")
        session.execute(
            f"CREATE TABLE ds60_orders.{target} "
            "(customer_id text, day_bucket date, ordered_at timestamp, "
            "order_id int, amount int, "
            "PRIMARY KEY ((customer_id,day_bucket),ordered_at,order_id)) "
            "WITH CLUSTERING ORDER BY (ordered_at DESC,order_id ASC)"
        )
        tool("snapshot", "--table", "by_customer", "--tag", tag, "ds60_orders")
        snapshot_created = True
        snapshot = (
            Path("/state/data/ds60_orders")
            / ("by_customer-" + source["id"].hex)
            / "snapshots"
            / tag
        )
        if not snapshot.is_dir() or snapshot.is_symlink():
            raise AssertionError("Expected actual owned table snapshot directory")
        components = [
            path
            for path in snapshot.iterdir()
            if re.fullmatch(r"[a-z]{2}-[0-9]+-(big|bti)-[A-Za-z0-9_.]+", path.name)
        ]
        if (
            not components
            or len(components) > 64
            or sum(p.stat().st_size for p in components) > 16 * 1024 * 1024
        ):
            raise AssertionError("Snapshot component count/bytes exceed the bounded fixture")
        if any(path.is_symlink() or not path.is_file() for path in components):
            raise AssertionError("Snapshot components must be regular files")
        if not any(path.name.endswith("-Data.db") for path in components):
            raise AssertionError("Snapshot contains no actual SSTable data")
        hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in components}
        with tempfile.TemporaryDirectory(prefix="ds60-cassandra-restore-", dir="/tmp") as temporary:
            stage = Path(temporary) / "ds60_orders" / target
            stage.mkdir(parents=True)
            for component in components:
                shutil.copy2(component, stage / component.name)
                if (
                    hashlib.sha256((stage / component.name).read_bytes()).hexdigest()
                    != hashes[component.name]
                ):
                    raise AssertionError("Snapshot staging bytes changed")
            tool("import", "--copy-data", "--extended-verify", "ds60_orders", target, str(stage))
            restored = list(session.execute(ROW_QUERY.replace("by_customer", target)))
            exact_orders(restored)
            exact_orders(list(session.execute(ROW_QUERY)))
            if any(
                hashlib.sha256(component.read_bytes()).hexdigest() != hashes[component.name]
                for component in components
            ):
                raise AssertionError("Original snapshot component bytes changed during import")
        result = {
            "schema_version": 1,
            "passed": True,
            "actual_sstable_import": True,
            "snapshot_tag": tag,
            "restored_table": target,
            "source_table_id": str(source["id"]),
            "source_schema": cluster.metadata.keyspaces["ds60_orders"]
            .tables["by_customer"]
            .export_as_string(),
            "rows": 3,
            "receipt_saved": True,
            "component_sha256": hashes,
            "original_orders_unchanged": True,
            "remote_backup_or_cluster_disaster_recovery_demonstrated": False,
        }
        try:
            save_receipt(Path("/state/backup-evidence"), target, result)
        except (OSError, ValueError) as error:
            result["receipt_saved"] = False
            result["storage_warning"] = "Restore succeeded; local evidence save failed: " + str(
                error
            )
    except BaseException as error:
        failure = error
        raise
    finally:
        try:
            if snapshot_created:
                try:
                    tool("clearsnapshot", "-t", tag, "ds60_orders")
                except Exception as cleanup_error:
                    if failure is None:
                        result["cleanup_warning"] = str(cleanup_error)
                    else:
                        failure.add_note(
                            "Owned snapshot cleanup also failed: " + str(cleanup_error)
                        )
        finally:
            cluster.shutdown()
    print(json.dumps(result, indent=2))
    return 0 if result.get("receipt_saved") is True and "cleanup_warning" not in result else 1


if __name__ == "__main__":
    raise SystemExit(main())
