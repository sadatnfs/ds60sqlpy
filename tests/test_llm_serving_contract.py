"""Independent byte, request, persistence and queue checks for the serving workshop."""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import sys
import threading
import time
from collections.abc import Callable
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
        spec = importlib.util.spec_from_file_location(name, PROJECT / (name + ".py"))
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
TOKENIZER: Any = sys.modules["serving_tokenizer"]
CONTRACT: Any = sys.modules["serving_contract"]
STORE: Any = sys.modules["serving_store"]
SCHEDULER: Any = sys.modules["serving_scheduler"]
ENGINE: Any = sys.modules["serving_engine"]


def request(key: str = "request_0001", **changes: Any) -> Any:
    return CONTRACT.RequestSpec.parse(
        {
            "prompt": "ab",
            "max_new_tokens": 4,
            "temperature": 0,
            "top_k": 4,
            "seed": 3,
            "stops": [],
            "idempotency_key": key,
            **changes,
        }
    )


def test_bpe_merge_rank_unicode_and_special_ids() -> None:
    tokenizer = TOKENIZER.Tokenizer(((97, 98), (258, 97)))
    assert tokenizer.encode("aba ab") == [259, 32, 258]
    assert tokenizer.encode("aba", add_bos=True) == [256, 259]
    assert tokenizer.decode([259, 32, *list("é🙂".encode())]) == "aba é🙂"
    assert tokenizer.token_bytes(0) == b"\0"
    with pytest.raises(ValueError, match="Invalid"):
        TOKENIZER.Tokenizer(((258, 97),))
    with pytest.raises(ValueError, match="Invalid"):
        TOKENIZER.Tokenizer(((256, 97),))
    fitted = TOKENIZER.fit_tokenizer("abab abab", 2)
    assert fitted.merges == ((97, 98), (258, 258))


def test_incremental_utf8_and_stop_boundaries() -> None:
    stream = TOKENIZER.TextStream(("<END>",))
    data = "é🙂<END>tail".encode()
    observed = "".join(stream.feed(bytes([value])) for value in data)
    assert observed == "é🙂"
    assert stream.stopped
    assert stream.replacement_characters == 0
    stream = TOKENIZER.TextStream(("abc",))
    assert stream.feed(b"zzab") == "zz"
    assert stream.feed(b"", final=True) == "ab"
    stream = TOKENIZER.TextStream()
    assert stream.feed(b"\xff") == "\ufffd"
    assert stream.replacement_characters == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"prompt": "\ud800"},
        {"prompt": "a\0b"},
        {"prompt": ""},
        {"max_new_tokens": True},
        {"max_new_tokens": 65},
        {"temperature": float("nan")},
        {"temperature": 0.01},
        {"seed": -1},
        {"seed": True},
        {"top_k": 0},
        {"stops": ["x", "x"]},
        {"stops": ["\ud800"]},
        {"idempotency_key": "../../escape"},
    ],
)
def test_request_rejects_invalid_values(changes: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        request(**changes)


def test_context_and_duplicate_json() -> None:
    spec = request(max_new_tokens=64)
    assert spec.admit(TOKENIZER.Tokenizer(), 96) == [256, 97, 98]
    with pytest.raises(ValueError, match="context"):
        spec.admit(TOKENIZER.Tokenizer(), 66)
    with pytest.raises(ValueError, match="Duplicate"):
        CONTRACT.exact_json(b'{"x":1,"x":2}')
    with pytest.raises(ValueError, match="Nonfinite"):
        CONTRACT.exact_json(b'{"x":NaN}')


def original_record(identity: str = "a" * 32) -> dict[str, Any]:
    spec = request()
    return {
        "format": "ds60-inference-record-v1",
        "id": identity,
        "request": spec.record(),
        "request_sha256": spec.digest,
        "model_sha256": "b" * 64,
        "tokenizer_sha256": "c" * 64,
        "created_unix": 100.0,
        "events": [CONTRACT.event(1, "queued", {"prompt_tokens": 3, "reserved_tokens": 7})],
    }


def test_terminal_readback_preserves_bytes_and_interrupted_is_not_replayed(tmp_path: Path) -> None:
    store = STORE.RecordStore(tmp_path)
    record = original_record()
    store.write(record)
    recovered = store.recover()[0]
    assert recovered["events"][-1]["event"] == "error"
    assert recovered["events"][-1]["data"]["reason"] == "interrupted_by_restart"
    raw = store.read_raw(record["id"])
    for _ in range(3):
        assert store.recover()[0] == recovered
        assert store.read_raw(record["id"]) == raw
    changed = json.loads(json.dumps(recovered))
    changed["request"]["prompt"] = "changed"
    with pytest.raises(ValueError):
        store.write(changed)
    store.close()
    reopened = STORE.RecordStore(tmp_path)
    assert reopened.read_raw(record["id"]) == raw
    reopened.close()


def test_state_lock_count_checksum_and_symlinks(tmp_path: Path) -> None:
    store = STORE.RecordStore(tmp_path, maximum_records=1)
    with pytest.raises(RuntimeError, match="Another"):
        STORE.RecordStore(tmp_path)
    record = original_record()
    store.write(record)
    other = original_record("d" * 32)
    with pytest.raises(STORE.StoreFull):
        store.write(other)
    location = tmp_path / (record["id"] + ".json")
    envelope = json.loads(location.read_text())
    envelope["record"]["request"]["prompt"] = "tampered"
    location.write_text(json.dumps(envelope))
    with pytest.raises(ValueError, match="checksum"):
        store.read(record["id"])
    location.unlink()
    target = tmp_path / "outside"
    target.write_text("data")
    location.symlink_to(target)
    with pytest.raises(ValueError):
        store.read(record["id"])
    store.close()


class FakeEngine:
    tokenizer: Any = TOKENIZER.Tokenizer()
    context = 96
    model_hash = "b" * 64
    tokenizer_hash = "c" * 64
    device = "cpu"

    def __init__(self, *, fail: bool = False, delay: float = 0) -> None:
        self.calls: list[str] = []
        self.fail = fail
        self.delay = delay

    def generate(
        self,
        spec: Any,
        tokens: list[int],
        cancelled: threading.Event,
        emit: Callable[[dict[str, Any]], None],
    ) -> dict[str, Any]:
        self.calls.append(spec.idempotency_key)
        if self.fail:
            raise RuntimeError("independent injected compute failure")
        text = ""
        try:
            for index in range(spec.max_new_tokens):
                if cancelled.wait(self.delay):
                    raise ENGINE.GenerationCancelled("cancelled")
                text += "a"
                emit(
                    {
                        "index": index,
                        "token_id": 97,
                        "bytes_hex": "61",
                        "text": "a",
                        "compute_seconds": 0.01,
                    }
                )
            return {
                "status": "completed",
                "reason": "max_new_tokens",
                "text": text,
                "metrics": {"compute_seconds": 0.04},
            }
        except ENGINE.GenerationCancelled as exc:
            return {"status": "cancelled", "reason": str(exc), "text": text, "metrics": {}}


async def collect(scheduler: Any, identity: str) -> list[dict[str, Any]]:
    iterator = await scheduler.subscribe(identity)
    return [item async for item in iterator]


def test_fifo_capacity_cancellation_idempotency_and_replay(tmp_path: Path) -> None:
    async def scenario() -> None:
        engine = FakeEngine(delay=0.001)
        store = STORE.RecordStore(tmp_path)
        scheduler = SCHEDULER.Scheduler(engine, store, attach_seconds=1)
        scheduler.start()
        first, created = await scheduler.submit(request("first_key"))
        second, _ = await scheduler.submit(request("second_key"))
        third, _ = await scheduler.submit(request("third_key"))
        assert created and scheduler.reserved_tokens == 21
        with pytest.raises(SCHEDULER.Busy):
            await scheduler.submit(request("fourth_key"))
        assert (await scheduler.submit(request("first_key")))[1] is False
        with pytest.raises(ValueError, match="different"):
            await scheduler.submit(request("first_key", prompt="changed"))
        await scheduler.cancel(second["id"])
        assert scheduler.reserved_tokens == 14
        one, three = await asyncio.gather(
            collect(scheduler, first["id"]), collect(scheduler, third["id"])
        )
        assert engine.calls == ["first_key", "third_key"]
        assert one[-1]["event"] == three[-1]["event"] == "completed"
        assert [item["id"] for item in one] == list(range(1, 8))
        assert scheduler.reserved_tokens == 0
        raw = store.read_raw(first["id"])
        assert await collect(scheduler, first["id"]) == one
        assert engine.calls == ["first_key", "third_key"]
        assert store.read_raw(first["id"]) == raw
        await scheduler.close()
        fresh_engine = FakeEngine()
        fresh = SCHEDULER.Scheduler(fresh_engine, STORE.RecordStore(tmp_path))
        fresh.start()
        assert await collect(fresh, first["id"]) == one
        assert fresh_engine.calls == []
        assert (await fresh.submit(request("first_key")))[1] is False
        await fresh.close()

    asyncio.run(scenario())


def test_failure_and_attach_timeout_release_capacity(tmp_path: Path) -> None:
    async def scenario() -> None:
        engine = FakeEngine(fail=True)
        scheduler = SCHEDULER.Scheduler(engine, STORE.RecordStore(tmp_path), attach_seconds=0.02)
        scheduler.start()
        one, _ = await scheduler.submit(request())
        events = await collect(scheduler, one["id"])
        assert events[-1]["event"] == "error"
        assert events[-1]["data"]["reason"] == "inference_failed"
        two, _ = await scheduler.submit(request("unattached"))
        deadline = time.monotonic() + 2
        while two["id"] in scheduler.work and time.monotonic() < deadline:
            await asyncio.sleep(0.005)
        assert (
            scheduler.records[two["id"]]["events"][-1]["data"]["reason"]
            == "subscriber_attach_timeout"
        )
        assert scheduler.reserved_tokens == 0
        assert len(engine.calls) == 1
        await scheduler.close()

    asyncio.run(scenario())


def test_bounded_slow_subscriber_and_explicit_disconnect(tmp_path: Path) -> None:
    async def scenario() -> None:
        engine = FakeEngine()
        scheduler = SCHEDULER.Scheduler(
            engine, STORE.RecordStore(tmp_path), backpressure_seconds=0.02
        )
        scheduler.start()
        one, _ = await scheduler.submit(request(max_new_tokens=16))
        iterator = await scheduler.subscribe(one["id"])
        first = await anext(iterator)
        assert first["event"] == "queued"
        deadline = time.monotonic() + 2
        while one["id"] in scheduler.work and time.monotonic() < deadline:
            await asyncio.sleep(0.005)
        events = [item async for item in iterator]
        assert events[-1]["data"]["reason"] == "subscriber_backpressure_timeout"
        assert len([item for item in events if item["event"] == "token"]) <= 5
        assert scheduler.reserved_tokens == 0
        two, _ = await scheduler.submit(request("disconnect_key", max_new_tokens=16))
        stream = await scheduler.subscribe(two["id"])
        await anext(stream)
        await stream.aclose()
        await scheduler.close()
        assert scheduler.records[two["id"]]["events"][-1]["event"] == "cancelled"

    asyncio.run(scenario())


def test_sse_is_event_framing_not_token_or_network_boundary() -> None:
    item = CONTRACT.event(1, "queued", {"prompt_tokens": 3, "reserved_tokens": 7})
    expected = b'id: 1\nevent: queued\ndata: {"prompt_tokens":3,"reserved_tokens":7}\n\n'
    assert CONTRACT.sse_frame(item) == expected
    assert hashlib.sha256(expected).hexdigest() != hashlib.sha256(expected[:-1]).hexdigest()


def test_storage_failure_retains_real_output_without_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def scenario() -> None:
        engine = FakeEngine()
        store = STORE.RecordStore(tmp_path)
        scheduler = SCHEDULER.Scheduler(engine, store)
        scheduler.start()
        accepted, _ = await scheduler.submit(request())
        original = store.read_raw(accepted["id"])

        def failed_write(record: dict[str, Any]) -> None:
            raise OSError("independent disk-full injection")

        monkeypatch.setattr(store, "write", failed_write)
        events = await collect(scheduler, accepted["id"])
        assert events[-1]["event"] == "completed"
        assert events[-1]["data"]["text"] == "aaaa"
        assert events[-1]["data"]["durable"] is False
        assert "could not be saved" in events[-1]["data"]["warning"]
        assert store.read_raw(accepted["id"]) == original
        assert engine.calls == ["request_0001"]
        await scheduler.close()
        fresh_engine = FakeEngine()
        fresh = SCHEDULER.Scheduler(fresh_engine, STORE.RecordStore(tmp_path))
        fresh.start()
        retained = await collect(fresh, accepted["id"])
        assert retained[-1]["data"]["reason"] == "interrupted_by_restart"
        assert fresh_engine.calls == []
        await fresh.close()

    asyncio.run(scenario())


def test_duplicate_live_subscriber_and_invalid_cursor(tmp_path: Path) -> None:
    async def scenario() -> None:
        scheduler = SCHEDULER.Scheduler(FakeEngine(), STORE.RecordStore(tmp_path))
        scheduler.start()
        accepted, _ = await scheduler.submit(request())
        with pytest.raises(ValueError, match="cursor"):
            await scheduler.subscribe(accepted["id"], 20)
        stream = await scheduler.subscribe(accepted["id"])
        with pytest.raises(SCHEDULER.Busy, match="already"):
            await scheduler.subscribe(accepted["id"])
        await anext(stream)
        await stream.aclose()
        await scheduler.close()

    asyncio.run(scenario())


def test_http_boundary_and_record_routes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from starlette.testclient import TestClient

    spec = importlib.util.spec_from_file_location("serving_http_test", PROJECT / "server.py")
    assert spec is not None and spec.loader is not None
    server = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server)

    class LoadedFake(FakeEngine):
        def __init__(self, model: Path, device: str, pacing: float) -> None:
            super().__init__()

        def describe(self) -> dict[str, Any]:
            return {"generation_calls": len(self.calls), "device": "cpu"}

    monkeypatch.setattr(server, "InferenceEngine", LoadedFake)
    token_file = tmp_path / "token"
    token_file.write_text("a" * 64 + "\n")
    monkeypatch.setenv("DS60_TOKEN_FILE", str(token_file))
    monkeypatch.setenv("DS60_MODEL_DIR", str(tmp_path / "model"))
    monkeypatch.setenv("DS60_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("DS60_PUBLIC_ORIGIN", "http://127.0.0.1:8892")
    headers = {"X-Workshop-Token": "a" * 64, "Origin": "http://127.0.0.1:8892"}
    with TestClient(server.create_app(), base_url="http://127.0.0.1:8892") as client:
        assert client.get("/healthz").json() == {"ready": True}
        assert client.get("/api/status").status_code == 403
        assert (
            client.get("/api/status", headers={**headers, "Host": "attacker.example"}).status_code
            == 403
        )
        assert (
            client.get(
                "/api/status", headers={**headers, "Origin": "http://attacker.example"}
            ).status_code
            == 403
        )
        assert (
            client.post(
                "/api/requests", json=request().record(), headers={"X-Workshop-Token": "a" * 64}
            ).status_code
            == 403
        )
        assert (
            client.get(
                "/api/status", headers={**headers, "Sec-Fetch-Site": "cross-site"}
            ).status_code
            == 403
        )
        assert (
            client.post(
                "/api/requests",
                content='{"prompt":1,"prompt":2}',
                headers={**headers, "Content-Type": "application/json"},
            ).status_code
            == 400
        )
        assert (
            client.post(
                "/api/requests",
                content="x" * 8001,
                headers={**headers, "Content-Type": "application/json"},
            ).status_code
            == 413
        )
        created = client.post("/api/requests", json=request().record(), headers=headers)
        assert created.status_code == 202
        identity = created.json()["id"]
        streamed = client.get(f"/api/requests/{identity}/events", headers=headers)
        assert "event: completed" in streamed.text
        assert "unsafe-eval" not in streamed.headers["Content-Security-Policy"]
        before = client.get("/api/status", headers=headers).json()["generation_calls"]
        raw = client.get(f"/api/requests/{identity}", headers=headers).content
        assert STORE.decode_record(raw, identity)["events"][-1]["event"] == "completed"
        assert (
            client.get(
                f"/api/requests/{identity}/events?after=1",
                headers={**headers, "Last-Event-ID": "1"},
            ).status_code
            == 400
        )
        suffix = client.get(f"/api/requests/{identity}/events?after=6", headers=headers)
        assert suffix.text.startswith("id: 7\nevent: completed")
        assert client.get(f"/api/requests/{identity}", headers=headers).content == raw
        assert client.get("/api/status", headers=headers).json()["generation_calls"] == before == 1


def test_unpublished_snapshot_bounds_preserve_evidence(tmp_path: Path) -> None:
    store = STORE.RecordStore(tmp_path)
    snapshot = tmp_path / ("." + "a" * 32 + "." + "b" * 32 + ".tmp")
    snapshot.write_bytes(b"interrupted unpublished snapshot")
    assert store.inventory() == []
    assert snapshot.read_bytes() == b"interrupted unpublished snapshot"
    snapshot.write_bytes(b"x" * (CONTRACT.MAX_RECORD + 1))
    with pytest.raises(ValueError, match="Unpublished"):
        store.inventory()
    assert snapshot.exists()
    store.close()
