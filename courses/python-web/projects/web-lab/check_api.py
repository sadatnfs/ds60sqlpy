"""Actual HTTP/WS/SSE acceptance, run in the prepared FastAPI service."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import httpx2
from websockets.sync.client import connect

ROOT = Path(__file__).parent


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def signin(client, username, django=False):
    headers = {}
    if django:
        headers["X-CSRFToken"] = client.get("/api/csrf").json()["csrf"]
    response = client.post(
        "/api/login", json={"username": username, "password": "classroom-demo"}, headers=headers
    )
    require(response.status_code == 200, f"Login failed: {response.status_code}")
    csrf = response.json()["csrf"]
    client.headers.update({"X-CSRF-Token": csrf, "X-CSRFToken": csrf})


def source_hashes():
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(ROOT.rglob("*"))
        if path.is_file()
        and not any(part in {".workshop", "__pycache__", "collected-static"} for part in path.parts)
        and path.suffix in {".py", ".js", ".css", ".html", ".yaml"}
    }


def check(ports):
    checks = []
    retained = {}
    clients = []
    try:
        for framework, port in ports.items():
            origin = f"http://127.0.0.1:{port}"
            options = {
                "base_url": f"http://{framework}:8080",
                "timeout": 8,
                "trust_env": False,
                "headers": {"Host": origin.removeprefix("http://"), "Origin": origin},
            }
            alice, bob = httpx2.Client(**options), httpx2.Client(**options)
            clients.extend([alice, bob])
            require(alice.get("/healthz").status_code == 200, f"{framework} readiness")
            require(alice.get("/api/notes").status_code == 401, "Anonymous notes admitted")
            signin(alice, "alice", framework == "django")
            signin(bob, "bob", framework == "django")
            title = f"Acceptance {framework} {time.time_ns()}"
            response = alice.post("/api/notes", json={"title": title})
            require(response.status_code == 201, f"{framework} creation: {response.text}")
            row = response.json()
            require(alice.get(f"/api/notes/{row['id']}").json()["title"] == title, "Owned read")
            require(bob.get(f"/api/notes/{row['id']}").status_code == 404, "Cross-user disclosure")
            require(
                alice.post("/api/notes", json={"title": "bad", "owner": 2}).status_code == 422,
                "Writable owner admitted",
            )
            denied = alice.post(
                "/api/notes",
                json={"title": "bad"},
                headers={"X-CSRF-Token": "invalid", "X-CSRFToken": "invalid"},
            )
            require(denied.status_code == 403, "Invalid CSRF admitted")
            require(
                alice.post(
                    "/api/notes",
                    json={"title": "bad"},
                    headers={"Origin": "https://untrusted.example"},
                ).status_code
                == 403,
                "Untrusted origin admitted",
            )
            require(
                alice.get("/healthz", headers={"Host": "untrusted.example"}).status_code == 400,
                "Untrusted host admitted",
            )
            page = alice.get("/")
            require(
                page.status_code == 200 and "Content-Security-Policy" in page.headers,
                "Local UI policy",
            )
            for asset in ["site.css", "app.js"]:
                require(alice.get("/static/" + asset).status_code == 200, f"Missing local {asset}")
            if framework == "django":
                require(
                    alice.get("/static/admin/css/base.css").status_code == 200,
                    "Collected admin CSS missing",
                )
            retained[framework] = {"id": row["id"], "title": title}
            checks.append(framework + "-http-auth-csrf-ownership-static")
            if framework != "fastapi":
                continue
            require(alice.get("/docs").status_code == 200, "Local API explorer")
            require(alice.get("/static/docs.js").status_code == 200, "Local explorer JavaScript")
            schema = alice.get("/openapi.json").json()
            require("/api/jobs" in schema["paths"], "OpenAPI jobs contract missing")
            require(alice.get("/redoc").status_code == 404, "Unexpected CDN documentation route")
            checks.append("offline-openapi-http-assets")
            cookie = "; ".join(f"{name}={value}" for name, value in alice.cookies.items())
            with connect(
                "ws://127.0.0.1:8080/socket",
                origin=origin,
                additional_headers={"Cookie": cookie},
                open_timeout=5,
                close_timeout=3,
                proxy=None,
            ) as socket:
                socket.send(json.dumps({"message": "actual network"}))
                require(
                    json.loads(socket.recv(timeout=5))
                    == {"user": "alice", "echo": "actual network"},
                    "WebSocket reply",
                )
            checks.append("real-websocket-echo")
            created = alice.post("/api/jobs", json={"values": [2, 3, 5]})
            require(created.status_code == 202, "Job acceptance")
            identifier = created.json()["id"]
            require(
                bob.get(f"/api/jobs/{identifier}").status_code == 404, "Cross-user job disclosure"
            )
            first_id = None
            with alice.stream("GET", f"/api/jobs/{identifier}/events") as response:
                require(response.status_code == 200, "SSE response")
                for line in response.iter_lines():
                    if line.startswith("id: "):
                        first_id = int(line[4:])
                    if line.startswith("data: "):
                        first = json.loads(line[6:])
                        require(first["state"] in {"queued", "running"}, "Unexpected first state")
                        # This happens only after actual bytes arrive over the socket.
                        require(
                            alice.get(f"/api/jobs/{identifier}").json()["released"] is False,
                            "Producer completed before controlled release",
                        )
                        break
            require(first_id is not None, "Missing event identity")
            checks.append("sse-arrives-before-release-and-disconnect")
            require(
                alice.post(f"/api/jobs/{identifier}/release").status_code == 200, "Release failed"
            )
            seen = []
            with alice.stream(
                "GET", f"/api/jobs/{identifier}/events", headers={"Last-Event-ID": str(first_id)}
            ) as response:
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        event = json.loads(line[6:])
                        require(event["id"] > first_id, "Cursor replayed acknowledged event")
                        seen.append(event)
                        if event["state"] == "finished":
                            break
            require(seen and seen[-1]["result"] == 10, "Durable calculation result")
            require(
                alice.get(
                    f"/api/jobs/{identifier}/events", headers={"Last-Event-ID": "999999999"}
                ).status_code
                == 409,
                "Invalid resume cursor admitted",
            )
            retained["job"] = {"id": identifier, "result": 10}
            checks.append("sse-resume-and-worker-result")
        return {
            "schema_version": 1,
            "status": "passed",
            "checks": checks,
            "retained": retained,
            "source_sha256": source_hashes(),
            "scope": "real local Compose HTTP/WebSocket/SSE/PostgreSQL; no TLS or multi-host claim",
        }
    finally:
        for client in clients:
            client.close()


def verify_saved(ports, record):
    for framework, port in ports.items():
        origin = f"http://127.0.0.1:{port}"
        with httpx2.Client(
            base_url=f"http://{framework}:8080",
            timeout=8,
            trust_env=False,
            headers={"Host": origin.removeprefix("http://"), "Origin": origin},
        ) as client:
            signin(client, "alice", framework == "django")
            expected = record["retained"][framework]
            require(
                client.get(f"/api/notes/{expected['id']}").json()["title"] == expected["title"],
                "Saved note lost",
            )
            if framework == "fastapi":
                expected_job = record["retained"]["job"]
                result = client.get(f"/api/jobs/{expected_job['id']}").json()
                require(
                    result["state"] == "finished" and result["result"] == expected_job["result"],
                    "Saved job lost",
                )
    return {
        "schema_version": 1,
        "status": "passed",
        "checks": ["saved-notes-and-job-readback"],
        "source_sha256": source_hashes(),
    }


def pending_job(ports, operation, saved=None):
    origin = f"http://127.0.0.1:{ports['fastapi']}"
    with httpx2.Client(
        base_url="http://fastapi:8080",
        timeout=8,
        trust_env=False,
        headers={"Host": origin.removeprefix("http://"), "Origin": origin},
    ) as client:
        signin(client, "alice")
        if operation == "create":
            response = client.post("/api/jobs", json={"values": [7, 11, 13]})
            require(response.status_code == 202, "Pending job admission")
            identifier = response.json()["id"]
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                current = client.get(f"/api/jobs/{identifier}").json()
                if current["state"] == "running":
                    require(current["released"] is False, "Held job unexpectedly released")
                    return {
                        "schema_version": 1,
                        "status": "passed",
                        "id": identifier,
                        "expected_result": 31,
                        "state_before_stop": "running",
                    }
                time.sleep(0.1)
            raise AssertionError("Worker did not claim the pending job")
        require(
            isinstance(saved, dict) and saved.get("expected_result") == 31,
            "Invalid pending fixture receipt",
        )
        identifier = saved["id"]
        if operation == "release":
            response = client.post(f"/api/jobs/{identifier}/release")
            require(response.status_code == 200, "Pending release")
            current = response.json()
            require(
                current["state"] == "running"
                and current["released"] is True
                and current["result"] is None,
                "Stopped worker changed the pending result",
            )
            return {"status": "passed", "id": identifier, "released_while_worker_stopped": True}
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            current = client.get(f"/api/jobs/{identifier}").json()
            if current["state"] == "finished":
                require(current["result"] == 31, "Resumed worker result differs")
                response = client.get(f"/api/jobs/{identifier}/events")
                events = [
                    json.loads(line[6:])
                    for line in response.text.splitlines()
                    if line.startswith("data: ")
                ]
                require(
                    [event["state"] for event in events] == ["queued", "running", "finished"],
                    "Worker restart duplicated or lost a committed transition",
                )
                return {
                    "schema_version": 1,
                    "status": "passed",
                    "id": identifier,
                    "result": 31,
                    "transitions": [event["state"] for event in events],
                }
            time.sleep(0.1)
        raise AssertionError("Restarted worker did not reconcile the pending job")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--verify-saved", action="store_true")
    group.add_argument("--pending-create", action="store_true")
    group.add_argument("--pending-release", action="store_true")
    group.add_argument("--pending-verify", action="store_true")
    args = parser.parse_args()
    ports = {
        name: int(os.environ["WORKSHOP_" + name.upper() + "_PORT"])
        for name in ("flask", "fastapi", "django")
    }
    if args.verify_saved or args.pending_release or args.pending_verify:
        import sys

        saved = json.load(sys.stdin)
        result = (
            verify_saved(ports, saved)
            if args.verify_saved
            else pending_job(ports, "release" if args.pending_release else "verify", saved)
        )
    elif args.pending_create:
        result = pending_job(ports, "create")
    else:
        result = check(ports)
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
