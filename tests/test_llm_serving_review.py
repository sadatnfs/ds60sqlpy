"""Regressions independently reproduced against the frozen serving contribution."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT = (
    Path(__file__).resolve().parents[1] / "courses/data-ml-engineering/projects/inference-service"
)
for name in (
    "serving_tokenizer",
    "serving_contract",
    "serving_model",
    "serving_checkpoint",
    "serving_engine",
    "serving_store",
    "serving_scheduler",
):
    if name not in sys.modules:
        specification = importlib.util.spec_from_file_location(name, PROJECT / f"{name}.py")
        assert specification is not None and specification.loader is not None
        loaded = importlib.util.module_from_spec(specification)
        sys.modules[name] = loaded
        specification.loader.exec_module(loaded)
CONTRACT: Any = sys.modules["serving_contract"]
STORE: Any = sys.modules["serving_store"]
SCHEDULER: Any = sys.modules["serving_scheduler"]
TOKENIZER: Any = sys.modules["serving_tokenizer"]


def submitted() -> dict[str, Any]:
    return {
        "prompt": "ab",
        "max_new_tokens": 1,
        "temperature": 0,
        "top_k": 1,
        "seed": 1,
        "stops": [],
        "idempotency_key": "independent_review",
    }


class Engine:
    tokenizer: Any = TOKENIZER.Tokenizer()
    context = 96
    model_hash = "b" * 64
    tokenizer_hash = "c" * 64
    device = "cpu"

    def __init__(self, *arguments: Any) -> None:
        self.calls = 0

    def describe(self) -> dict[str, Any]:
        return {"generation_calls": self.calls}

    def generate(self, spec: Any, tokens: Any, cancelled: Any, emit: Any) -> dict[str, Any]:
        self.calls += 1
        emit({"index": 0, "token_id": 97, "bytes_hex": "61", "text": "a", "compute_seconds": 0})
        return {"status": "completed", "reason": "max_new_tokens", "text": "a", "metrics": {}}


@pytest.mark.parametrize("failure", ["every_update", "one_update"])
def test_failed_save_remains_visible_in_state_and_idempotent_reconciliation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    async def scenario() -> None:
        store = STORE.RecordStore(tmp_path)
        engine = Engine()
        scheduler = SCHEDULER.Scheduler(engine, store)
        scheduler.start()
        spec = CONTRACT.RequestSpec.parse(submitted())
        accepted, created = await scheduler.submit(spec)
        assert created
        original_write = store.write
        attempts = 0

        def saving(record: dict[str, Any]) -> None:
            nonlocal attempts
            attempts += 1
            if failure == "every_update" or attempts == 1:
                raise OSError("independent save-failure injection")
            original_write(record)

        monkeypatch.setattr(store, "write", saving)
        try:
            events = [item async for item in await scheduler.subscribe(accepted["id"])]
            terminal = events[-1]
            assert terminal["event"] == "completed"
            assert terminal["data"]["text"] == "a"
            assert terminal["data"]["durable"] is False
            assert scheduler.state(accepted["id"])["durable"] is False
            reconciled, recreated = await scheduler.submit(spec)
            assert not recreated
            assert reconciled["id"] == accepted["id"]
            assert reconciled["durable"] is False
            assert engine.calls == 1
        finally:
            await scheduler.close()
        if failure == "one_update":
            recovered = SCHEDULER.Scheduler(Engine(), STORE.RecordStore(tmp_path))
            try:
                assert recovered.state(accepted["id"])["durable"] is False
            finally:
                await recovered.close()

    asyncio.run(scenario())


@pytest.mark.parametrize("case", ["integer_conversion_limit", "finite_number_overflow"])
def test_bounded_numeric_input_returns_client_error_without_admission(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    from starlette.testclient import TestClient

    specification = importlib.util.spec_from_file_location(
        "serving_review_http", PROJECT / "server.py"
    )
    assert specification is not None and specification.loader is not None
    server = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(server)
    monkeypatch.setattr(server, "InferenceEngine", Engine)
    origin = "http://127.0.0.1:8892"
    token_path = tmp_path / "token"
    token_path.write_text("a" * 64 + "\n")
    for name, value in {
        "DS60_TOKEN_FILE": str(token_path),
        "DS60_MODEL_DIR": str(tmp_path / "model"),
        "DS60_STATE_DIR": str(tmp_path / "state"),
        "DS60_PUBLIC_ORIGIN": origin,
    }.items():
        monkeypatch.setenv(name, value)
    if case == "integer_conversion_limit":
        payload = b'{"temperature":' + b"9" * 5000 + b"}"
    else:
        payload = json.dumps({**submitted(), "temperature": 10**400}).encode()
    assert len(payload) < CONTRACT.MAX_BODY
    headers = {
        "X-Workshop-Token": "a" * 64,
        "Origin": origin,
        "Content-Type": "application/json",
    }
    with TestClient(server.create_app(), base_url=origin, raise_server_exceptions=False) as client:
        response = client.post("/api/requests", content=payload, headers=headers)
        assert response.status_code == 400, response.text
        assert isinstance(response.json()["error"], str)
        status = client.get("/api/status", headers=headers).json()
        assert (
            status["history_count"] == status["reserved_tokens"] == status["generation_calls"] == 0
        )


def test_resume_supports_compose_228_without_build_or_recreation(tmp_path: Path) -> None:
    import os
    import shutil
    import subprocess

    owned = tmp_path / "owned"
    owned.mkdir()
    helper = owned / "workshop"
    shutil.copy2(PROJECT / "workshop", helper)
    (owned / "compose.yaml").write_bytes((PROJECT / "compose.yaml").read_bytes())
    private = owned / ".workshop"
    private.mkdir()
    (private / "state").mkdir()
    (private / "settings.env").write_text(
        "WORKSHOP_PROJECT=review-inference\nWORKSHOP_PORT=18895\n"
        "WORKSHOP_BASE_IMAGE=ds60sqlpy-worker-llm-torch-cpu:1.0.0\n"
        "WORKSHOP_PACING=0\nWORKSHOP_IMAGE=review-inference-image:1.0.0\n"
        "WORKSHOP_UID=1000\nWORKSHOP_GID=1000\n"
    )
    fake_directory = tmp_path / "bin"
    fake_directory.mkdir()
    log = tmp_path / "docker-calls.jsonl"
    fake = fake_directory / "docker"
    fake.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "args = sys.argv[1:]\n"
        "with open(os.environ['REVIEW_DOCKER_LOG'], 'a') as stream:\n"
        "    stream.write(json.dumps(args) + '\\n')\n"
        "if args[0] == 'info': pass\n"
        "elif args[0] == 'ps': print('owned-container|inference-service')\n"
        "elif args[0] == 'inspect': print('running healthy')\n"
        "elif args[0] == 'compose':\n"
        "    if 'version' in args: print('2.28.0')\n"
        "    elif 'ps' in args: print('owned-container')\n"
        "    elif 'start' in args:\n"
        "        if '--wait' in args or '--wait-timeout' in args:\n"
        "            print('unknown flag: --wait', file=sys.stderr); sys.exit(125)\n"
        "    else: sys.exit('unexpected Compose mutation: ' + repr(args))\n"
        "else: sys.exit('unexpected Docker mutation: ' + repr(args))\n"
    )
    fake.chmod(0o755)
    result = subprocess.run(
        ["bash", str(helper), "resume"],
        cwd=owned,
        env={
            **os.environ,
            "PATH": str(fake_directory) + os.pathsep + os.environ.get("PATH", ""),
            "REVIEW_DOCKER_LOG": str(log),
        },
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    assert any(call[0] == "compose" and "start" in call for call in calls)
    assert any(call[0] == "inspect" and "owned-container" in call for call in calls)
    assert not any(set(call) & {"build", "pull", "up", "rm", "prune"} for call in calls)


def test_valid_unicode_generation_finishes_without_stranding_reservations(tmp_path: Path) -> None:
    class UnicodeEngine(Engine):
        tokenizer: Any = TOKENIZER.Tokenizer(
            ((195, 169), (258, 258), (259, 259), (260, 260), (261, 261), (262, 262))
        )

        def generate(self, spec: Any, tokens: Any, cancelled: Any, emit: Any) -> dict[str, Any]:
            self.calls += 1
            raw = self.tokenizer.token_bytes(263)
            assert len(raw) == 64
            delta = raw.decode("utf-8")
            text = ""
            for index in range(spec.max_new_tokens):
                text += delta
                emit(
                    {
                        "index": index,
                        "token_id": 263,
                        "bytes_hex": raw.hex(),
                        "text": delta,
                        "compute_seconds": 0,
                    }
                )
            return {
                "status": "completed",
                "reason": "max_new_tokens",
                "text": text,
                "metrics": {},
            }

    async def scenario() -> None:
        store = STORE.RecordStore(tmp_path)
        scheduler = SCHEDULER.Scheduler(UnicodeEngine(), store)
        scheduler.start()
        accepted, _ = await scheduler.submit(
            CONTRACT.RequestSpec.parse({**submitted(), "max_new_tokens": 64})
        )

        async def collect() -> list[dict[str, Any]]:
            return [item async for item in await scheduler.subscribe(accepted["id"])]

        collector = asyncio.create_task(collect())
        try:
            assert scheduler.task is not None
            completed, _ = await asyncio.wait(
                {collector, scheduler.task}, timeout=2, return_when=asyncio.FIRST_COMPLETED
            )
            assert collector in completed, (
                str(scheduler.task.exception())
                if scheduler.task in completed
                else "Valid Unicode result never reached a terminal event"
            )
            result = collector.result()
            assert result[-1]["event"] == "completed"
            assert result[-1]["data"]["text"] == "é" * 2048
            assert scheduler.reserved_tokens == 0
            assert not scheduler.work
            retained = store.read(accepted["id"])
            assert retained["events"] == result
        finally:
            collector.cancel()
            await asyncio.gather(collector, return_exceptions=True)
            await asyncio.gather(scheduler.close(), return_exceptions=True)
            store.close()

    asyncio.run(scenario())


def test_browser_sse_is_independent_of_network_chunk_coalescing(tmp_path: Path) -> None:
    import shutil
    import subprocess

    node = shutil.which("node")
    if node is None:
        pytest.skip("The serving browser transport regression requires prepared Node.js")
    data = "é" * 32
    events = [
        {"event": "queued", "data": {"prompt_tokens": 3, "reserved_tokens": 67}},
        {"event": "started", "data": {"queue_seconds": 0, "device": "cpu"}},
        *[
            {
                "event": "token",
                "data": {
                    "index": index,
                    "token_id": 263,
                    "bytes_hex": data.encode().hex(),
                    "text": data,
                    "compute_seconds": 0,
                },
            }
            for index in range(64)
        ],
        {
            "event": "completed",
            "data": {
                "reason": "max_new_tokens",
                "text": data * 64,
                "metrics": {},
                "durable": True,
                "warning": "",
            },
        },
    ]
    frames = "".join(
        f"id: {index}\nevent: {item['event']}\ndata: "
        + TOKENIZER.canonical_json(item["data"]).decode().rstrip("\n")
        + "\n\n"
        for index, item in enumerate(events, 1)
    )
    fixture = tmp_path / "stream.txt"
    fixture.write_text(frames)
    script = r"""
const fs = require("fs");
const vm = require("vm");
const source = fs.readFileSync(process.argv[1], "utf8");
const frames = fs.readFileSync(process.argv[2], "utf8");
async function inspect(payload, chunkSize) {
  const nodes = new Map();
  const node = (id) => {
    if (!nodes.has(id)) nodes.set(id, {
      textContent: "", addEventListener() {}, replaceChildren() {},
      append() {}, setAttribute() {}
    });
    return nodes.get(id);
  };
  const context = {
    document: {
      querySelector: () => ({content: "private"}),
      getElementById: node, createElement: () => node(Symbol())
    },
    sessionStorage: {getItem: () => null, setItem() {}, removeItem() {}},
    TextDecoder, TextEncoder,
    fetch: async (path) => {
      if (path.endsWith("/events")) return new Response(new ReadableStream({
        start(controller) {
          const bytes = new TextEncoder().encode(payload);
          for (let index = 0; index < bytes.length; index += chunkSize)
            controller.enqueue(bytes.slice(index, index + chunkSize));
          controller.close();
        }
      }));
      return Response.json(path === "/api/requests" ? {requests: []} : {
        device: "cpu", waiting: 0, reserved_tokens: 0, generation_calls: 0,
        parameters: 1, context: 96, vocabulary: 264, model_sha256: "b".repeat(64),
        load_seconds: 0, warm_seconds: 0, pacing_seconds: 0
      });
    }
  };
  vm.createContext(context);
  vm.runInContext(source, context);
  try {
    await vm.runInContext('streamEvents("a".repeat(32))', context);
    return {output: node("output").textContent, error: null};
  } catch (error) {
    return {output: node("output").textContent, error: error.message};
  }
}
(async () => {
  const oversized = 'id: 1\nevent: token\ndata: ' + JSON.stringify({
    index: 0, token_id: 97, bytes_hex: "61", text: "x".repeat(100000), compute_seconds: 0
  }) + "\n\n";
  process.stdout.write(JSON.stringify({
    chunked: await inspect(frames, 512),
    coalesced: await inspect(frames, 1000000),
    oversizedComplete: await inspect(oversized, 1000000),
    oversizedIncomplete: await inspect("data: " + "x".repeat(100000), 1000000)
  }));
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    completed = subprocess.run(
        [node, "-e", script, str(PROJECT / "app.js"), str(fixture)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert completed.returncode == 0, completed.stderr
    observed = json.loads(completed.stdout)
    assert observed["chunked"] == {"output": "é" * 2048, "error": None}
    assert observed["coalesced"] == observed["chunked"]
    for key in ("oversizedComplete", "oversizedIncomplete"):
        assert "limit" in observed[key]["error"].lower()


def test_failed_container_ownership_inventory_aborts_before_stop(tmp_path: Path) -> None:
    import os
    import shutil
    import subprocess

    owned = tmp_path / "owned"
    owned.mkdir()
    helper = owned / "workshop"
    shutil.copy2(PROJECT / "workshop", helper)
    private = owned / ".workshop"
    private.mkdir()
    (private / "settings.env").write_text(
        "WORKSHOP_PROJECT=review-inference\nWORKSHOP_PORT=18895\n"
        "WORKSHOP_BASE_IMAGE=ds60sqlpy-worker-llm-torch-cpu:1.0.0\n"
        "WORKSHOP_PACING=0\nWORKSHOP_IMAGE=review-inference-image:1.0.0\n"
        "WORKSHOP_UID=1000\nWORKSHOP_GID=1000\n"
    )
    fake_directory = tmp_path / "bin"
    fake_directory.mkdir()
    log = tmp_path / "docker-calls.jsonl"
    fake = fake_directory / "docker"
    fake.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "args = sys.argv[1:]\n"
        "with open(os.environ['REVIEW_DOCKER_LOG'], 'a') as stream:\n"
        "    stream.write(json.dumps(args) + '\\n')\n"
        "if args[0] == 'info': pass\n"
        "elif args[0] == 'ps': sys.exit('independent ownership inventory failure')\n"
        "elif args[0] == 'compose': pass\n"
        "else: sys.exit('unexpected Docker invocation')\n"
    )
    fake.chmod(0o755)
    result = subprocess.run(
        ["bash", str(helper), "stop"],
        cwd=owned,
        env={
            **os.environ,
            "PATH": str(fake_directory) + os.pathsep + os.environ.get("PATH", ""),
            "REVIEW_DOCKER_LOG": str(log),
        },
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode != 0, result.stdout + result.stderr
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    assert not any(call[0] == "compose" for call in calls)


def test_malformed_terminal_keeps_token_events_and_allows_next_fifo_request(tmp_path: Path) -> None:
    class MalformedOnce(Engine):
        def __init__(self) -> None:
            super().__init__()
            self.identities: list[str] = []

        def generate(self, spec: Any, tokens: Any, cancelled: Any, emit: Any) -> dict[str, Any]:
            self.identities.append(spec.idempotency_key)
            result = super().generate(spec, tokens, cancelled, emit)
            if self.calls == 1:
                del result["reason"]
            return result

    async def scenario() -> None:
        engine = MalformedOnce()
        store = STORE.RecordStore(tmp_path)
        scheduler = SCHEDULER.Scheduler(engine, store)
        scheduler.start()
        first_spec = CONTRACT.RequestSpec.parse(submitted())
        first, _ = await scheduler.submit(first_spec)
        second_spec = CONTRACT.RequestSpec.parse(
            {**submitted(), "idempotency_key": "independent_review_next"}
        )
        second, _ = await scheduler.submit(second_spec)
        first_stream = await scheduler.subscribe(first["id"])
        second_stream = await scheduler.subscribe(second["id"])

        async def collect(iterator: Any) -> list[dict[str, Any]]:
            return [item async for item in iterator]

        try:
            first_events, second_events = await asyncio.wait_for(
                asyncio.gather(collect(first_stream), collect(second_stream)), timeout=2
            )
            assert first_events[-1]["event"] == "error"
            assert first_events[-1]["data"]["reason"] == "terminal_result_contract_failed"
            assert first_events[-1]["data"]["text"] == "a"
            assert "token" in first_events[-1]["data"]["warning"].lower()
            emitted = [item for item in first_events if item["event"] == "token"]
            assert len(emitted) == 1
            assert emitted[0]["data"]["text"] == "a"
            assert emitted[0]["data"]["bytes_hex"] == "61"
            assert store.read(first["id"])["events"] == first_events
            assert second_events[-1]["event"] == "completed"
            assert second_events[-1]["data"]["text"] == "a"
            assert scheduler.reserved_tokens == 0
            assert not scheduler.work
            assert scheduler.task is not None and not scheduler.task.done()
            reconciled, created = await scheduler.submit(first_spec)
            assert not created and reconciled["id"] == first["id"]
            assert engine.identities == [first_spec.idempotency_key, second_spec.idempotency_key]
            assert engine.calls == 2
        finally:
            await first_stream.aclose()
            await second_stream.aclose()
            await asyncio.gather(scheduler.close(), return_exceptions=True)
            store.close()

    asyncio.run(scenario())
