"""Exercise HTTP sandbox isolation and preview-channel lifetime boundaries."""

from __future__ import annotations

import json
import shutil
import subprocess
import threading
from collections.abc import Iterator
from http.client import HTTPConnection
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.lab import LabServer
from ds60sqlpy.modules import ModuleCatalog

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def browser_module_catalog() -> ModuleCatalog:
    # Reuse real immutable curriculum metadata, not learner state. Catalog admission
    # has its own tests; rebuilding every subject inside an HTTP auth request makes
    # this boundary test depend on catalog size and parallel disk/CPU contention.
    return ModuleCatalog(ROOT)


@pytest.fixture
def sandbox_server(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, browser_module_catalog: ModuleCatalog
) -> Iterator[LabServer]:
    monkeypatch.setattr("ds60sqlpy.lab.rendered_targets", lambda _: {})
    monkeypatch.setattr("ds60sqlpy.module_service.rendered_targets", lambda _: {})
    monkeypatch.setattr(
        "ds60sqlpy.module_service.ModuleCatalog", lambda _root: browser_module_catalog
    )
    server = LabServer(Catalog.load(), progress_path=tmp_path / "progress.json")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive()


def request(
    server: LabServer,
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, str], bytes]:
    # Bound HTTP processing independently of the fixture's curriculum preparation.
    # ModuleService and each learner-state directory are still initialized lazily.
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=15)
    try:
        connection.request(
            method,
            path,
            body=None if payload is None else json.dumps(payload).encode(),
            headers={"Host": server.expected_host, **(headers or {})},
        )
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


def policy(header: str) -> dict[str, set[str]]:
    return {
        parts[0]: set(parts[1:]) for directive in header.split(";") if (parts := directive.split())
    }


def test_only_the_token_free_sandbox_can_be_framed_and_evaluate_source(
    sandbox_server: LabServer,
) -> None:
    server = sandbox_server
    status, headers, body = request(server, "/browser-sandbox")
    assert status == 200
    assert server.token.encode() not in body
    assert b"SERVER_TOKEN" not in body
    assert b"__DS60_D3_BUNDLE__" not in body
    assert b"__DS60_BROWSER_ORIGIN__" not in body
    assert json.dumps("http://" + server.expected_host).encode() in body
    assert b"d3" in body and b"7.9.0" in body
    assert headers["X-Frame-Options"] == "SAMEORIGIN"
    assert headers["Cache-Control"] == "no-store"
    assert headers["Referrer-Policy"] == "no-referrer"
    assert headers["X-Content-Type-Options"] == "nosniff"
    iframe_policy = policy(headers["Content-Security-Policy"])
    assert iframe_policy["sandbox"] == {"allow-scripts"}
    assert iframe_policy["script-src"] == {"'unsafe-inline'", "'unsafe-eval'"}
    assert iframe_policy["frame-ancestors"] == {"'self'"}
    for surface in ("default-src", "connect-src", "frame-src", "worker-src", "object-src"):
        assert iframe_policy[surface] == {"'none'"}
    assert iframe_policy["img-src"] == {"data:"}
    assert iframe_policy["font-src"] == {"data:"}

    for route in ("/classroom", "/assets/classroom.js", "/assets/browser-preview.js"):
        status, headers, body = request(server, route)
        assert status == 200
        assert headers["X-Frame-Options"] == "DENY"
        parent_policy = policy(headers["Content-Security-Policy"])
        assert "sandbox" not in parent_policy
        assert "'unsafe-eval'" not in parent_policy["script-src"]
        assert parent_policy["frame-src"] == {"'self'"}
        assert parent_policy["frame-ancestors"] == {"'none'"}
        if route == "/classroom":
            assert server.token.encode() in body
        else:
            assert server.token.encode() not in body


@pytest.mark.parametrize(
    "host",
    ["localhost", "example.invalid", "127.0.0.1", "127.0.0.1:1", "127.0.0.1.evil.invalid"],
)
def test_sandbox_rejects_every_nonexact_host(sandbox_server: LabServer, host: str) -> None:
    status, _, body = request(sandbox_server, "/browser-sandbox", headers={"Host": host})
    assert status == 400
    assert b"Unexpected Host" in body
    assert sandbox_server.token.encode() not in body
    assert b"AsyncFunction" not in body


@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ({"X-DS60-Token": ""}, 403),
        ({"X-DS60-Token": "wrong"}, 403),
        ({"Origin": ""}, 403),
        ({"Origin": "null"}, 403),
        ({"Origin": "https://example.invalid"}, 403),
        ({"Host": "localhost"}, 400),
    ],
)
def test_browser_observation_writes_require_exact_host_token_and_origin(
    sandbox_server: LabServer, change: dict[str, str], expected: int
) -> None:
    server = sandbox_server
    payload: dict[str, Any] = {
        "action": "module-browser-record",
        "lesson_id": "js-043",
        "fields": {
            "source": "console.log(42)",
            "output": "42",
            "status": "succeeded",
            "elapsed_seconds": 0,
        },
    }
    headers = {
        "Content-Type": "application/json",
        "Origin": server.url.rstrip("/"),
        "X-DS60-Token": server.token,
    }
    status, _, body = request(
        server, "/api/modules", method="POST", payload=payload, headers={**headers, **change}
    )
    assert status == expected
    assert server.token.encode() not in body
    assert server._module_state_directory is not None
    assert not server._module_state_directory.exists()
    assert server._modules is None

    status, result_headers, body = request(
        server, "/api/modules", method="POST", payload=payload, headers=headers
    )
    assert status == 200
    receipt = json.loads(body)["receipt"]
    assert receipt["source"] == payload["fields"]["source"]
    assert receipt["verified"] is False and receipt["checks"] == []
    assert result_headers["X-Frame-Options"] == "DENY"


def test_query_parameters_never_inject_a_token_or_source_into_sandbox_html(
    sandbox_server: LabServer,
) -> None:
    status, _, original = request(sandbox_server, "/browser-sandbox")
    changed_status, _, changed = request(
        sandbox_server, "/browser-sandbox?source=UNTRUSTED_SOURCE_SENTINEL&token=NOT_A_TOKEN"
    )
    assert status == changed_status == 200
    assert original == changed
    assert b"UNTRUSTED_SOURCE_SENTINEL" not in changed
    assert b"NOT_A_TOKEN" not in changed


def test_preview_ignores_stale_ports_and_preserves_submitted_source(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is needed for the isolated preview-controller regression")
    source = ROOT / "src/ds60sqlpy/assets/browser-preview.js"
    script = r"""
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const channels = [], timers = new Map();
let nextTimer = 0, now = 10;
class Port {
  start() {}
  close() { this.closed = true; }
}
class Channel {
  constructor() { this.port1 = new Port(); this.port2 = new Port(); channels.push(this); }
}
const document = {
  createElement(name) {
    assert.equal(name, "iframe");
    return {
      attributes: {}, handlers: {}, removed: false,
      setAttribute(key, value) { this.attributes[key] = value; },
      addEventListener(key, fn) { this.handlers[key] = fn; },
      remove() { this.removed = true; },
      contentWindow: {
        postMessage(message, origin, ports) { this.sent = {message, origin, ports}; }
      },
    };
  },
};
const context = { document, MessageChannel:Channel, TextEncoder, performance:{now:()=>now},
  setTimeout(fn) { const id=++nextTimer; timers.set(id,fn); return id; },
  clearTimeout(id) { timers.delete(id); } };
vm.runInNewContext(fs.readFileSync(process.argv[2], "utf8"), context);
const container = { replaceChildren(...children) { this.children = children; } };
const preview = new context.DS60BrowserPreview(container);
(async () => {
  const first = preview.start("const first = true;");
  const oldFrame = preview.frame, oldPort = channels[0].port1;
  assert.equal(oldFrame.attributes.sandbox, "allow-scripts");
  assert.equal(oldFrame.attributes.referrerpolicy, "no-referrer");
  assert.equal(oldFrame.src, "/browser-sandbox");
  assert.equal(oldFrame.contentWindow.sent, undefined); // Loading alone cannot execute source.
  oldFrame.handlers.load();
  assert.equal(oldFrame.contentWindow.sent.message.source, "const first = true;");
  assert.equal(oldFrame.contentWindow.sent.ports.length, 1);
  const second = preview.start("const current = true;");
  const cancelled = await first;
  assert.equal(cancelled.status, "cancelled");
  assert.equal(cancelled.source, "const first = true;");
  assert.equal(oldPort.closed, true);
  assert.equal(oldFrame.removed, true);
  oldPort.onmessage({data:{type:"complete",status:"succeeded",output:"STALE"}});
  assert.equal(preview.snapshot().source, "const current = true;");
  assert.equal(preview.snapshot().output, "");
  const currentPort = channels[1].port1;
  currentPort.onmessage({data:{type:"output",output:"é".repeat(16001)}});
  assert.equal(preview.snapshot().output, "");
  now = 1010;
  currentPort.onmessage({data:{type:"complete",status:"succeeded",output:"current",
    source:"FORGED",verified:true,checks:[{passed:true}],returncode:0}});
  const done = await second;
  assert.equal(done.source, "const current = true;");
  assert.equal(done.output, "current");
  assert.equal(done.status, "succeeded");
  assert.equal("verified" in done, false);
  assert.equal("checks" in done, false);
  assert.equal("returncode" in done, false);
  assert.equal(timers.size, 0);
  const copy = preview.snapshot(); copy.source = "mutated copy";
  assert.equal(preview.snapshot().source, "const current = true;");
  assert.equal(done.elapsed_seconds, 1);
  now = 5010;
  preview.stop();
  assert.equal(preview.active, false);
  assert.equal(container.children.length, 0);
  assert.equal(preview.snapshot().elapsed_seconds, 1); // Completed timing stays fixed.
  assert.equal(preview.snapshot().status, "succeeded");
  assert.equal(done.elapsed_seconds, 1); // The previously returned observation is unchanged.

  now = 6000;
  const pending = preview.start("await learnerWork;");
  channels[2].port1.onmessage({data:{type:"started",output:""}});
  now = 11000;
  preview.stop("Stopped by the learner.");
  const stopped = await pending;
  assert.equal(stopped.status, "cancelled");
  // Cancellation time advances even without another output event.
  assert.equal(stopped.elapsed_seconds, 5);
  assert.equal(stopped.source, "await learnerWork;");

  now = 12000;
  const timed = preview.start("await initialization;");
  const timeout = [...timers.values()][0];
  now = 132000;
  timeout();
  const expired = await timed;
  assert.equal(expired.status, "cancelled");
  assert.equal(expired.elapsed_seconds, 120);
  assert.match(expired.output, /UI wait budget/);
  assert.equal(timers.size, 0);
  process.stdout.write("preview lifecycle and source binding passed\n");
})().catch(error => { process.stderr.write(error.stack); process.exitCode = 1; });
"""
    harness = tmp_path / "preview-regression.cjs"
    harness.write_text(script, encoding="utf-8")
    result = subprocess.run(
        [node, str(harness), str(source)], capture_output=True, text=True, timeout=15, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "preview lifecycle and source binding passed" in result.stdout
