"""Bounded actual Pinot REST/SQL observations; initialization is explicit."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
EXPECTED = [[1, "east", 4], [2, "west", 9], [3, "east", 7]]


def request(host: str, path: str, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        host + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=12) as response:
        raw = response.read(200001)
        if len(raw) > 200000:
            raise ValueError("Oversized Pinot response")
        return json.loads(raw)


def query(sql: str, *, multistage: bool = False):
    result = request(
        "http://broker:8099",
        "/query/sql",
        {
            "sql": sql,
            "queryOptions": "timeoutMs=5000;useMultistageEngine=" + str(multistage).lower(),
        },
    )
    if result.get("exceptions"):
        raise ValueError("Pinot query returned explicit exceptions")
    return result


def check():
    deadline = time.monotonic() + 90
    while True:
        try:
            result = query("SELECT id, region, amount FROM ds60_orders ORDER BY id LIMIT 10")
            rows = result["resultTable"]["rows"]
            if rows != EXPECTED:
                raise ValueError("Retained order identities or values differ; no reset occurred")
            break
        except (OSError, KeyError, ValueError):
            if time.monotonic() >= deadline:
                raise
            time.sleep(1)
    grouped = query(
        "SELECT region, SUM(amount) FROM ds60_orders GROUP BY region ORDER BY region LIMIT 10"
    )
    if grouped["resultTable"]["rows"] != [["east", 11.0], ["west", 9.0]]:
        raise ValueError("Independent regional oracle differs")
    selective = query(
        "SELECT id FROM ds60_orders WHERE region = 'east' AND amount >= 5 ORDER BY id LIMIT 10"
    )
    if selective["resultTable"]["rows"] != [[3]]:
        raise ValueError("Selective index-query result differs")
    bad = request(
        "http://broker:8099", "/query/sql", {"sql": "SELECT absent_field FROM ds60_orders LIMIT 1"}
    )
    if not any(
        isinstance(error, dict) and "absent_field" in str(error.get("message", "")).lower()
        for error in bad.get("exceptions", [])
    ):
        raise ValueError("Unknown-column negative case did not return its actual field diagnostic")
    segments = request("http://controller:9000", "/segments/ds60_orders")
    instances = request("http://controller:9000", "/instances")
    instance_names = instances.get("instances")
    if not isinstance(instance_names, list) or not all(
        isinstance(name, str) for name in instance_names
    ):
        raise ValueError("Controller instance response violates the pinned metadata contract")
    brokers = sorted(name for name in instance_names if name.startswith("Broker_"))
    servers = sorted(name for name in instance_names if name.startswith("Server_"))
    offline_segments = (
        [name for group in segments for name in group.get("OFFLINE", [])]
        if isinstance(segments, list)
        else []
    )
    if (
        not brokers
        or not servers
        or len(offline_segments) != 1
        or not isinstance(offline_segments[0], str)
    ):
        raise ValueError("Expected live broker/server metadata and one owned offline segment")
    return {
        "passed": True,
        "product": "Apache Pinot",
        "rows": rows,
        "regional_totals": grouped["resultTable"]["rows"],
        "selective_ids": [3],
        "unknown_column_rejected": True,
        "segments": segments,
        "instances": instances,
        "offline_segment_names": offline_segments,
        "broker_instances": brokers,
        "server_instances": servers,
        "controller_metadata_observed": True,
        "read_only_no_initialization": True,
        "streaming_hybrid_upsert_multistage_qualified": False,
    }


def plan():
    tables = request("http://controller:9000", "/tables")["tables"]
    if "ds60_orders" not in tables and "ds60_orders_OFFLINE" not in tables:
        return "absent"
    check()
    return "ready"


def create():
    if plan() != "absent":
        raise ValueError("Initialization requires an absent owned table; no mutation occurred")
    request("http://controller:9000", "/schemas", json.loads((BASE / "schema.json").read_text()))
    request("http://controller:9000", "/tables", json.loads((BASE / "table.json").read_text()))
    return {"created": True, "ingestion_required": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["check", "plan", "create"])
    args = parser.parse_args()
    result = {"check": check, "plan": plan, "create": create}[args.action]()
    print(result if isinstance(result, str) else json.dumps(result, sort_keys=True))
