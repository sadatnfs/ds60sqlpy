"""Explicit disposable-service qualification; readback mode never submits a request."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


class Client:
    def __init__(self, url: str, token_file: Path) -> None:
        parsed = urlsplit(url)
        if (
            parsed.scheme != "http"
            or parsed.hostname != "127.0.0.1"
            or parsed.port is None
            or parsed.path not in {"", "/"}
        ):
            raise ValueError("Use the explicit disposable service's loopback origin")
        self.url = url.rstrip("/")
        self.token = token_file.read_text().strip()

    def open(
        self,
        path: str,
        body: dict[str, Any] | None = None,
        *,
        headers: dict[str, str] | None = None,
    ) -> Any:
        values = {"X-Workshop-Token": self.token, "Origin": self.url, **(headers or {})}
        if body is not None:
            values["Content-Type"] = "application/json"
        request = urllib.request.Request(
            self.url + path,
            headers=values,
            data=None if body is None else json.dumps(body).encode(),
        )
        return urllib.request.urlopen(request, timeout=30)

    def json(self, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        with self.open(path, body) as response:
            result: dict[str, Any] = json.load(response)
            return result

    def raw(self, identity: str) -> bytes:
        with self.open("/api/requests/" + identity) as response:
            return bytes(response.read())

    def stream(
        self, identity: str, after: int = 0, cancel_at: int | None = None
    ) -> tuple[list[dict[str, Any]], list[float]]:
        records: list[dict[str, Any]] = []
        arrivals: list[float] = []
        with self.open(f"/api/requests/{identity}/events?after={after}") as response:
            assert response.headers["Content-Type"].startswith("text/event-stream")
            frame: dict[str, str] = {}
            for raw in response:
                line = raw.decode("utf-8").rstrip("\n")
                if not line:
                    if "data" not in frame:
                        continue
                    item = {
                        "id": int(frame["id"]),
                        "event": frame["event"],
                        "data": json.loads(frame["data"]),
                    }
                    assert item["id"] == after + len(records) + 1
                    records.append(item)
                    arrivals.append(time.perf_counter())
                    if (
                        cancel_at is not None
                        and item["event"] == "token"
                        and item["data"]["index"] == cancel_at
                    ):
                        self.json(f"/api/requests/{identity}/cancel", {})
                        cancel_at = None
                    frame = {}
                elif ": " in line:
                    key, value = line.split(": ", 1)
                    assert key in {"id", "event", "data"} and key not in frame
                    frame[key] = value
            assert not frame
        if records:
            assert records[-1]["event"] in {"completed", "cancelled", "error"}
        return records, arrivals


def parameters(key: str, count: int = 24) -> dict[str, Any]:
    return {
        "prompt": "A model learns",
        "max_new_tokens": count,
        "temperature": 0,
        "top_k": 20,
        "seed": 42,
        "stops": [],
        "idempotency_key": key,
    }


def expect_http(status: int, operation: Any) -> None:
    try:
        response = operation()
        response.close()
    except urllib.error.HTTPError as exc:
        assert exc.code == status, (exc.code, exc.read().decode())
    else:
        raise AssertionError(f"Expected HTTP {status}")


def qualify(client: Client) -> dict[str, Any]:
    baseline = client.json("/api/status")
    assert baseline["device"] == "cpu", "This maintained gate qualifies the default CPU project"
    assert baseline["running"] is None and baseline["waiting"] == 0
    prefix = "check_" + uuid.uuid4().hex
    expect_http(403, lambda: client.open("/api/status", headers={"X-Workshop-Token": "wrong"}))
    expect_http(
        403, lambda: client.open("/api/status", headers={"Origin": "http://invalid.example"})
    )
    expect_http(403, lambda: client.open("/healthz", headers={"Host": "invalid.example"}))
    invalid = parameters(prefix + "_invalid")
    invalid["prompt"] = "x" * 2049
    expect_http(400, lambda: client.open("/api/requests", invalid))
    first = client.json("/api/requests", parameters(prefix + "_one"))
    second = client.json("/api/requests", parameters(prefix + "_two"))
    third = client.json("/api/requests", parameters(prefix + "_three"))
    expect_http(429, lambda: client.open("/api/requests", parameters(prefix + "_full")))
    duplicate = client.json("/api/requests", parameters(prefix + "_one"))
    assert not duplicate["created"] and duplicate["id"] == first["id"]
    conflict = parameters(prefix + "_one")
    conflict["seed"] = 43
    expect_http(409, lambda: client.open("/api/requests", conflict))
    cancelled = client.json(f"/api/requests/{second['id']}/cancel", {})
    assert cancelled["status"] == "cancelled"
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(client.stream, first["id"])
        c = pool.submit(client.stream, third["id"])
        first_events, first_arrivals = a.result()
        third_events, third_arrivals = c.result()
    assert first_events[-1]["event"] == third_events[-1]["event"] == "completed"
    assert first_arrivals[-1] <= third_arrivals[-1]
    first_tokens = [item["data"]["token_id"] for item in first_events if item["event"] == "token"]
    third_tokens = [item["data"]["token_id"] for item in third_events if item["event"] == "token"]
    assert first_tokens == third_tokens and len(first_tokens) >= 2
    terminal = first_events[-1]["data"]
    assert terminal["metrics"]["compute_seconds"] > 0
    assert terminal["metrics"]["generation_wall_seconds"] >= terminal["metrics"]["compute_seconds"]
    active = client.json("/api/requests", parameters(prefix + "_cancel", 64))
    cancellation, _ = client.stream(active["id"], cancel_at=0)
    assert cancellation[-1]["event"] == "cancelled"
    assert cancellation[-1]["data"]["reason"] == "cancelled_by_user"
    final = client.json("/api/status")
    assert final["reserved_tokens"] == 0 and final["running"] is None
    assert final["generation_calls"] == baseline["generation_calls"] + 3
    receipts = []
    for entry in (first, second, third, active):
        identity = entry["id"]
        raw = client.raw(identity)
        envelope = json.loads(raw)
        record = envelope["record"]
        events, _ = client.stream(identity)
        assert events == record["events"]
        suffix, _ = client.stream(identity, after=max(0, len(events) - 2))
        assert suffix == events[-2:]
        assert client.raw(identity) == raw
        receipts.append(
            {
                "id": identity,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "source_sha256": record["request_sha256"],
                "events": len(events),
                "status": events[-1]["event"],
            }
        )
    assert client.json("/api/status")["generation_calls"] == final["generation_calls"]
    return {
        "schema_version": 1,
        "url": client.url,
        "model_sha256": baseline["model_sha256"],
        "device": baseline["device"],
        "pacing_seconds": baseline["pacing_seconds"],
        "receipts": receipts,
        "source": "disposable live CPU workshop",
        "checks": [
            "startup-loaded real weights",
            "auth/origin/Host",
            "bounded validation",
            "three reservation capacity",
            "idempotency/conflict",
            "FIFO completion",
            "seeded output",
            "incremental SSE",
            "running/queued cancellation",
            "explicit cursor suffix",
            "exact completed readback without inference",
        ],
    }


def readback(client: Client, report: dict[str, Any]) -> dict[str, Any]:
    before = client.json("/api/status")
    assert before["model_sha256"] == report["model_sha256"]
    for receipt in report["receipts"]:
        raw = client.raw(receipt["id"])
        assert hashlib.sha256(raw).hexdigest() == receipt["sha256"]
        record = json.loads(raw)["record"]
        events, _ = client.stream(receipt["id"])
        assert events == record["events"]
        assert record["request_sha256"] == receipt["source_sha256"]
    after = client.json("/api/status")
    assert after["generation_calls"] == before["generation_calls"]
    assert after["history_count"] == before["history_count"]
    return {
        "readback": "passed",
        "requests": len(report["receipts"]),
        "generation_calls_unchanged": before["generation_calls"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--verify-persisted", type=Path)
    args = parser.parse_args()
    client = Client(args.url, args.token_file)
    result = (
        readback(client, json.loads(args.verify_persisted.read_text()))
        if args.verify_persisted
        else qualify(client)
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
