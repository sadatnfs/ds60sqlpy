"""Produce an ephemeral local Cassandra config from the pinned distribution."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path


def configure(
    source: Path = Path("/opt/cassandra/conf"),
    destination: Path = Path("/tmp/cassandra-conf"),
) -> None:
    if destination.is_symlink() or destination.resolve() == source.resolve():
        raise ValueError("Refusing an unsafe generated-config destination")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    config = destination / "cassandra.yaml"
    text = config.read_text()
    node = os.environ.get("DS60_CASSANDRA_NODE", "cassandra")
    if node not in {"cassandra", "cassandra-two", "cassandra-three"}:
        raise ValueError("Unapproved fixed workshop node identity")
    settings = {
        "cluster_name": "'DS60 local Cassandra'",
        "listen_address": node,
        "rpc_address": "0.0.0.0",
        "broadcast_rpc_address": node,
        "hints_directory": "/state/hints",
        "commitlog_directory": "/state/commitlog",
        "saved_caches_directory": "/state/saved_caches",
        "cdc_raw_directory": "/state/cdc_raw",
        "memtable_heap_space": "64MiB",
        "memtable_offheap_space": "64MiB",
        "commitlog_total_space": "128MiB",
        "concurrent_reads": "2",
        "concurrent_writes": "2",
        "concurrent_counter_writes": "2",
        "concurrent_materialized_view_writes": "2",
        "concurrent_compactors": "1",
    }
    for key, value in settings.items():
        pattern = rf"(?m)^#? ?{key}:.*$"
        text, count = re.subn(pattern, f"{key}: {value}", text)
        if count != 1:
            raise ValueError(f"Pinned configuration key changed: {key}")
    text, count = re.subn(
        r"(?m)^# data_file_directories:$", "data_file_directories:\n  - /state/data", text
    )
    if count != 1:
        raise ValueError("Pinned data-directory configuration changed")
    text, count = re.subn(r"(?m)^(\s+- seeds:) .+$", r'\1 "cassandra:7000"', text)
    if count != 1:
        raise ValueError("Pinned seed configuration changed")
    config.write_text(text)
    (destination.parent / "home").mkdir(exist_ok=True)


if __name__ == "__main__":
    configure()
