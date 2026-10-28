"""Actual loopback HTTP and SQLite tests for raw acceptance and API boundaries."""

from __future__ import annotations

import copy
import http.client
import importlib
import importlib.util
import json
import socket
import struct
import sys
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "courses/data-ml-engineering/projects/data-product/product"
NAME = "_ds60_data_product_http_tests"
OWNER = "0123456789abcdef0123456789abcdef"
TOKEN = "a" * 64


@pytest.fixture(scope="module")
def product_modules() -> SimpleNamespace:
    spec = importlib.util.spec_from_file_location(
        NAME, PACKAGE / "__init__.py", submodule_search_locations=[str(PACKAGE)]
    )
    assert spec is not None and spec.loader is not None
    package = importlib.util.module_from_spec(spec)
    sys.modules[NAME] = package
    spec.loader.exec_module(package)
    return SimpleNamespace(
        server=importlib.import_module(NAME + ".server"),
        contracts=importlib.import_module(NAME + ".contracts"),
        raw=importlib.import_module(NAME + ".raw_store"),
    )


def snapshot(
    modules: SimpleNamespace, *, batch: str = "batch-a", generation: int = 1
) -> dict[str, Any]:
    return {
        "format": modules.contracts.FORMAT,
        "batch_id": batch,
        "generation": generation,
        "expected_rows": 3,
        "records": [
            {"delivery_id": "A", "route_id": 10, "packages": 2},
            {"delivery_id": "B", "route_id": 10, "packages": 3},
            {"delivery_id": "C", "route_id": 20, "packages": 1},
        ],
    }


@pytest.fixture
def api(tmp_path: Path, product_modules: SimpleNamespace) -> Iterator[SimpleNamespace]:
    raw = tmp_path / "raw"
    raw.mkdir()
    published = tmp_path / "published"
    published.mkdir()
    store = product_modules.raw.RawStore(raw, OWNER, writable=True)
    publication: dict[str, Any] = {"mode": "absent", "calls": 0}

    def reader(directory: Path, owner: str) -> dict[str, Any]:
        assert directory == published and owner == OWNER
        publication["calls"] += 1
        if publication["mode"] == "absent":
            raise FileNotFoundError("No active product")
        if publication["mode"] == "corrupt":
            raise product_modules.contracts.StateError("Synthetic corrupt product")
        return {
            "pointer": {"version": "synthetic-accepted-version"},
            "manifest": {"owner": OWNER},
            "rows": [{"route_id": 10, "deliveries": 2, "packages": 5}],
        }

    server = product_modules.server.ProductHTTPServer(
        ("127.0.0.1", 0),
        raw_store=store,
        owner=OWNER,
        token=TOKEN,
        published_directory=published,
        product_reader=reader,
        io_timeout=0.5,
    )
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    try:
        yield SimpleNamespace(
            server=server,
            store=store,
            publication=publication,
            modules=product_modules,
            address=server.server_address,
            origin=server.public_origin,
            host=server.public_host,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def request(
    api: SimpleNamespace,
    method: str,
    path: str,
    value: Any = None,
    *,
    headers: dict[str, str] | None = None,
    auth: bool = True,
) -> tuple[int, Any]:
    fields = {"Host": api.host}
    if auth:
        fields["X-DS60-Product-Token"] = TOKEN
    body = None
    if method == "POST":
        fields.update({"Origin": api.origin, "Content-Type": "application/json"})
    if value is not None:
        body = json.dumps(value).encode()
    fields.update(headers or {})
    address: tuple[str, int] = api.address
    connection = http.client.HTTPConnection(address[0], address[1], timeout=2)
    try:
        connection.request(method, path, body=body, headers=fields)
        response = connection.getresponse()
        assert response.version == 10
        assert response.getheader("Connection") == "close"
        return response.status, json.loads(response.read())
    finally:
        connection.close()


def wire(
    api: SimpleNamespace,
    path: str = "/api/snapshots",
    *,
    body: bytes = b"{}",
    extra: list[bytes] | None = None,
    omit: set[str] | None = None,
) -> tuple[int, Any]:
    omit = omit or set()
    headers = {
        "Host": api.host,
        "Origin": api.origin,
        "X-DS60-Product-Token": TOKEN,
        "Content-Type": "application/json",
        "Content-Length": str(len(body)),
    }
    rows = [f"POST {path} HTTP/1.1".encode()]
    rows += [f"{name}: {value}".encode() for name, value in headers.items() if name not in omit]
    rows += extra or []
    data = b"\r\n".join(rows) + b"\r\n\r\n" + body
    with socket.create_connection(api.address, timeout=2) as connection:
        connection.sendall(data)
        response = http.client.HTTPResponse(connection)
        response.begin()
        return response.status, json.loads(response.read())


def test_raw_accept_replay_conflicts_and_readback_are_real_sqlite(api: SimpleNamespace) -> None:
    value = snapshot(api.modules)
    status, accepted = request(api, "POST", "/api/snapshots", value)
    assert status == 201 and accepted["created"] is True
    receipt = accepted["receipt"]
    assert receipt["raw_accepted"] is True
    assert receipt["analytical_publication"] == "not_attempted"
    assert request(api, "POST", "/api/snapshots", value) == (
        200,
        {"created": False, "receipt": receipt},
    )
    changed = copy.deepcopy(value)
    changed["records"][0]["packages"] = 4
    assert request(api, "POST", "/api/snapshots", changed)[0] == 409
    occupied = snapshot(api.modules, batch="other-batch")
    assert request(api, "POST", "/api/snapshots", occupied)[0] == 409
    assert (
        request(api, "POST", "/api/snapshots", snapshot(api.modules, batch="next", generation=2))[0]
        == 201
    )
    assert request(api, "POST", "/api/snapshots", value)[0] == 200
    status, saved = request(api, "GET", "/api/snapshots/batch-a")
    assert status == 200 and saved == {"snapshot": value, "receipt": receipt}
    status, listed = request(api, "GET", "/api/snapshots")
    assert status == 200 and [row["batch_id"] for row in listed["snapshots"]] == ["batch-a", "next"]
    assert request(api, "GET", "/api/snapshots/absent")[0] == 404
    assert len(api.store.receipts()) == 2 and api.publication["calls"] == 0


@pytest.mark.parametrize(
    "bad", ["count", "bool", "missing", "nonfinite", "duplicate-key", "invalid-utf8"]
)
def test_invalid_http_inputs_leave_no_partial_raw_records(api: SimpleNamespace, bad: str) -> None:
    value = snapshot(api.modules)
    if bad == "count":
        value["expected_rows"] = 2
    elif bad == "bool":
        value["records"][0]["route_id"] = True
    elif bad == "missing":
        del value["records"][0]["delivery_id"]
    body = json.dumps(value).encode()
    if bad == "nonfinite":
        body = b'{"value":NaN}'
    elif bad == "duplicate-key":
        body = b'{"format":"one","format":"two"}'
    elif bad == "invalid-utf8":
        body = b"\xff"
    assert wire(api, body=body)[0] == 400
    assert api.store.receipts() == []


@pytest.mark.parametrize(
    "extra,omit,expected",
    [
        ([b"Content-Length: 2"], set(), 400),
        ([b"Transfer-Encoding: chunked"], set(), 400),
        ([b"Transfer-Encoding:"], set(), 400),
        ([], {"Content-Length"}, 400),
        ([b"Content-Length: 65537"], {"Content-Length"}, 400),
        ([b"Content-Length: 2,2"], {"Content-Length"}, 400),
        ([b"Content-Type: text/plain"], {"Content-Type"}, 400),
        ([b"Content-Type: application/json"], set(), 400),
        ([b"Origin: http://attacker.example"], {"Origin"}, 403),
        ([], {"Origin"}, 403),
        ([b"Host: attacker.example"], {"Host"}, 403),
        ([b"Host: attacker.example"], set(), 403),
        ([b"Expect: 100-continue"], set(), 400),
    ],
)
def test_header_ambiguity_and_origin_fail_before_raw_write(
    api: SimpleNamespace,
    extra: list[bytes],
    omit: set[str],
    expected: int,
) -> None:
    assert wire(api, extra=extra, omit=omit)[0] == expected
    assert api.store.receipts() == []


@pytest.mark.parametrize(
    "path",
    [
        "/api/%73napshots",
        "/api/snapshots?token=synthetic",
        "//api/snapshots",
        "/api/../snapshots",
        "/api/snapshots\\item",
        "http://attacker.example/api/snapshots",
    ],
)
def test_ambiguous_paths_are_rejected_without_store_access(api: SimpleNamespace, path: str) -> None:
    assert wire(api, path)[0] == 400
    assert api.store.receipts() == []


def test_unicode_token_is_rejected_before_constant_time_comparison(
    api: SimpleNamespace,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def forbidden(*args: Any) -> bool:
        nonlocal called
        called = True
        raise AssertionError("Unicode token reached compare_digest")

    monkeypatch.setattr(api.modules.server.hmac, "compare_digest", forbidden)
    status, _ = wire(
        api,
        extra=[b"X-DS60-Product-Token: " + b"\xe9" * 64],
        omit={"X-DS60-Product-Token"},
    )
    assert status == 403 and not called


def test_health_raw_acceptance_and_publication_have_independent_status(
    api: SimpleNamespace,
) -> None:
    assert request(api, "GET", "/healthz", auth=False) == (200, {"status": "ok", "raw_ready": True})
    assert api.publication["calls"] == 0
    assert request(api, "GET", "/api/status", auth=False)[0] == 403
    status, value = request(api, "GET", "/api/status")
    assert status == 200 and value["publication"] == {"status": "absent"}
    assert request(api, "GET", "/api/product")[0] == 404
    api.publication["mode"] = "corrupt"
    assert request(api, "GET", "/healthz", auth=False)[0] == 200
    assert request(api, "GET", "/api/status")[1]["publication"]["status"] == "corrupt"
    assert request(api, "GET", "/api/product")[0] == 503
    api.publication["mode"] = "available"
    assert request(api, "GET", "/api/status")[1]["publication"]["status"] == "available"
    assert request(api, "GET", "/api/product")[1]["rows"] == [
        {"route_id": 10, "deliveries": 2, "packages": 5}
    ]
    assert request(api, "POST", "/api/publish", {})[0] == 404
    assert request(api, "POST", "/api/rollback", {})[0] == 404


def test_typed_raw_acceptance_does_not_pretend_to_perform_business_quality(
    api: SimpleNamespace,
) -> None:
    value = snapshot(api.modules)
    value["records"][0]["packages"] = -1
    value["records"][1]["route_id"] = 999
    value["records"][2]["delivery_id"] = "A"
    status, receipt = request(api, "POST", "/api/snapshots", value)
    assert status == 201 and receipt["receipt"]["analytical_publication"] == "not_attempted"
    assert api.publication["calls"] == 0


def test_disconnected_post_commits_once_and_can_be_reconciled(
    api: SimpleNamespace,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = api.store.accept
    committed = threading.Event()
    calls = 0

    def accept(value: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        nonlocal calls
        calls += 1
        result: tuple[dict[str, Any], bool] = original(value)
        committed.set()
        return result

    monkeypatch.setattr(api.store, "accept", accept)
    body = json.dumps(snapshot(api.modules)).encode()
    data = (
        f"POST /api/snapshots HTTP/1.1\r\nHost: {api.host}\r\n"
        f"Origin: {api.origin}\r\nX-DS60-Product-Token: {TOKEN}\r\n"
        f"Content-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n"
    ).encode() + body
    connection = socket.create_connection(api.address, timeout=2)
    connection.sendall(data)
    assert committed.wait(1)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
    connection.close()
    status, value = request(api, "GET", "/api/snapshots/batch-a")
    assert status == 200 and value["snapshot"]["batch_id"] == "batch-a"
    assert calls == 1 and len(api.store.receipts()) == 1


def test_four_handlers_are_bounded_and_partial_bodies_expire(api: SimpleNamespace) -> None:
    sockets = []
    try:
        for _ in range(4):
            connection = socket.create_connection(api.address, timeout=2)
            connection.sendall(b"GET /healthz HTTP/1.1\r\n")
            sockets.append(connection)
        deadline = time.monotonic() + 0.3
        while time.monotonic() < deadline and api.server.handlers._value != 0:
            time.sleep(0.005)
        assert api.server.handlers._value == 0
        with socket.create_connection(api.address, timeout=2) as rejected:
            rejected.sendall(b"GET /healthz HTTP/1.1\r\n\r\n")
            response = http.client.HTTPResponse(rejected)
            response.begin()
            assert response.status == 503
        time.sleep(0.6)
        assert request(api, "GET", "/healthz", auth=False)[0] == 200
    finally:
        for connection in sockets:
            connection.close()


def test_absolute_body_deadline_prevents_slow_drip_retaining_a_handler(
    api: SimpleNamespace,
) -> None:
    with socket.create_connection(api.address, timeout=2) as connection:
        header = (
            f"POST /api/snapshots HTTP/1.1\r\nHost: {api.host}\r\n"
            f"Origin: {api.origin}\r\nX-DS60-Product-Token: {TOKEN}\r\n"
            "Content-Type: application/json\r\nContent-Length: 10\r\n\r\n"
        ).encode()
        connection.sendall(header + b"{")
        time.sleep(0.3)
        connection.sendall(b" ")
        time.sleep(0.3)
        response = http.client.HTTPResponse(connection)
        response.begin()
        assert response.status == 400
    assert api.store.receipts() == []
    assert request(api, "GET", "/healthz", auth=False)[0] == 200


def test_corrupt_raw_state_is_unavailable_without_automatic_reset(api: SimpleNamespace) -> None:
    api.store.path.write_bytes(b"not a SQLite database")
    original = api.store.path.read_bytes()
    assert request(api, "GET", "/healthz", auth=False)[0] == 503
    assert request(api, "GET", "/api/status")[0] == 503
    assert api.store.path.read_bytes() == original


def test_server_does_not_log_tokens_paths_or_raw_bodies(
    api: SimpleNamespace, capsys: pytest.CaptureFixture[str]
) -> None:
    assert request(api, "POST", "/api/snapshots", snapshot(api.modules))[0] == 201
    assert wire(api, "/api/snapshots?private=synthetic")[0] == 400
    output = capsys.readouterr()
    assert TOKEN not in output.out + output.err
    assert "private=synthetic" not in output.out + output.err
    assert "delivery_id" not in output.out + output.err


def test_environment_factory_validates_private_token_before_raw_initialization(
    tmp_path: Path,
    product_modules: SimpleNamespace,
) -> None:
    raw, published = tmp_path / "raw", tmp_path / "published"
    raw.mkdir()
    published.mkdir()
    token = tmp_path / "token"
    token.write_text("g" * 64)
    environment = {
        "DS60_PRODUCT_OWNER": OWNER,
        "DS60_PRODUCT_PUBLIC_ORIGIN": "http://127.0.0.1:8123",
        "DS60_PRODUCT_TOKEN_FILE": str(token),
        "DS60_PRODUCT_RAW_DIR": str(raw),
        "DS60_PRODUCT_PUBLISHED_DIR": str(published),
    }
    with pytest.raises(product_modules.contracts.StateError, match="token"):
        product_modules.server.create_server(("127.0.0.1", 0), environment=environment)
    assert not (raw / "snapshots.sqlite").exists()
    token.write_text(TOKEN + "\n")
    server = product_modules.server.create_server(("127.0.0.1", 0), environment=environment)
    try:
        assert server.public_origin == "http://127.0.0.1:8123"
        assert server.public_host == "127.0.0.1:8123"
        assert server.io_timeout == 5.0
        assert server.raw_store.receipts() == []
    finally:
        server.server_close()


def test_loopback_server_startup_never_requires_reverse_dns(
    tmp_path: Path,
    product_modules: SimpleNamespace,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw, published = tmp_path / "raw", tmp_path / "published"
    raw.mkdir()
    published.mkdir()
    store = product_modules.raw.RawStore(raw, OWNER, writable=True)

    def forbidden(*args: Any, **kwargs: Any) -> str:
        raise AssertionError("Offline HTTP startup attempted reverse DNS")

    monkeypatch.setattr(product_modules.server.socket, "getfqdn", forbidden)
    server = product_modules.server.ProductHTTPServer(
        ("127.0.0.1", 0),
        raw_store=store,
        owner=OWNER,
        token=TOKEN,
        published_directory=published,
    )
    try:
        assert server.server_name == "127.0.0.1" and server.server_port > 0
    finally:
        server.server_close()
