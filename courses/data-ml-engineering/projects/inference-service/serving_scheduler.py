"""One compute slot, FIFO admission, bounded subscriber buffers and no job replay."""

from __future__ import annotations

import asyncio
import threading
import time
import uuid
from collections import deque
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Protocol

from serving_contract import TERMINAL, ContractError, RequestSpec, event
from serving_engine import GenerationCancelled
from serving_store import RecordStore
from serving_tokenizer import Tokenizer


class Busy(RuntimeError):
    pass


class Engine(Protocol):
    tokenizer: Tokenizer
    context: int
    model_hash: str
    tokenizer_hash: str
    device: str

    def generate(
        self, spec: RequestSpec, tokens: list[int], cancelled: threading.Event, emit: Any
    ) -> dict[str, Any]: ...


@dataclass
class Work:
    record: dict[str, Any]
    spec: RequestSpec
    tokens: list[int]
    admitted: float
    cancel: threading.Event = field(default_factory=threading.Event)
    attached: asyncio.Event = field(default_factory=asyncio.Event)
    finished: asyncio.Event = field(default_factory=asyncio.Event)
    buffer: asyncio.Queue[dict[str, Any]] = field(default_factory=lambda: asyncio.Queue(maxsize=4))
    subscriber: bool = False
    reason: str = "cancelled_by_user"
    durable: bool = True


class Scheduler:
    def __init__(
        self,
        engine: Engine,
        store: RecordStore,
        *,
        attach_seconds: float = 30,
        backpressure_seconds: float = 5,
    ) -> None:
        if not 0 < attach_seconds <= 120 or not 0 < backpressure_seconds <= 30:
            raise ValueError("Use bounded positive stream timeouts")
        self.engine = engine
        self.store = store
        recovered = store.recover()
        self.records = {record["id"]: record for record in recovered}
        self.keys = {record["request"]["idempotency_key"]: record["id"] for record in recovered}
        self.work: dict[str, Work] = {}
        self.pending: deque[str] = deque()
        self.running: str | None = None
        self.reserved_tokens = 0
        self.lock = asyncio.Lock()
        self.wake = asyncio.Event()
        self.attach_seconds = attach_seconds
        self.backpressure_seconds = backpressure_seconds
        self.closing = False
        self.task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self.task is not None:
            raise RuntimeError("Scheduler already started")
        self.task = asyncio.create_task(self._run())

    async def close(self) -> None:
        self.closing = True
        async with self.lock:
            for work in self.work.values():
                work.reason = "service_shutdown"
                work.cancel.set()
                work.attached.set()
            self.wake.set()
        if self.task is not None:
            await self.task
        self.store.close()

    def state(self, identity: str) -> dict[str, Any]:
        if identity not in self.records:
            raise KeyError(identity)
        record = self.records[identity]
        return {
            "id": identity,
            "status": (
                record["events"][-1]["event"]
                if record["events"][-1]["event"] in TERMINAL
                else "running"
                if any(item["event"] == "started" for item in record["events"])
                else "queued"
            ),
            "events": len(record["events"]),
            "request_sha256": record["request_sha256"],
            "durable": (
                self.work[identity].durable
                if identity in self.work
                else record["events"][-1]["data"]["durable"]
                if record["events"][-1]["event"] in TERMINAL
                else True
            ),
        }

    async def submit(self, spec: RequestSpec) -> tuple[dict[str, Any], bool]:
        tokens = spec.admit(self.engine.tokenizer, self.engine.context)
        async with self.lock:
            if spec.idempotency_key in self.keys:
                identity = self.keys[spec.idempotency_key]
                if self.records[identity]["request_sha256"] != spec.digest:
                    raise ContractError("Idempotency key already belongs to a different request")
                return self.state(identity), False
            if self.closing:
                raise Busy("Service is shutting down")
            reservation = len(tokens) + spec.max_new_tokens
            active = len(self.work)
            if active >= 3 or self.reserved_tokens + reservation > self.engine.context * 3:
                raise Busy("One running request and two waiting requests are already reserved")
            identity = uuid.uuid4().hex
            record = {
                "format": "ds60-inference-record-v1",
                "id": identity,
                "request": spec.record(),
                "request_sha256": spec.digest,
                "model_sha256": self.engine.model_hash,
                "tokenizer_sha256": self.engine.tokenizer_hash,
                "created_unix": time.time(),
                "events": [
                    event(
                        1, "queued", {"prompt_tokens": len(tokens), "reserved_tokens": reservation}
                    )
                ],
            }
            self.store.write(record)
            self.records[identity] = record
            self.keys[spec.idempotency_key] = identity
            self.work[identity] = Work(record, spec, tokens, time.perf_counter())
            self.pending.append(identity)
            self.reserved_tokens += reservation
            self.wake.set()
            return self.state(identity), True

    def _append(self, work: Work, kind: str, data: dict[str, Any]) -> dict[str, Any]:
        item = event(len(work.record["events"]) + 1, kind, data)
        work.record["events"].append(item)
        try:
            self.store.write(work.record)
        except (OSError, ValueError, RuntimeError):
            # Real output remains available in memory. No replay follows a storage failure.
            work.durable = False
        return item

    async def _emit(self, work: Work, data: dict[str, Any]) -> None:
        if work.cancel.is_set():
            raise GenerationCancelled(work.reason)
        async with self.lock:
            item = self._append(work, "token", data)
        try:
            await asyncio.wait_for(work.buffer.put(item), self.backpressure_seconds)
        except TimeoutError as exc:
            work.reason = "subscriber_backpressure_timeout"
            work.cancel.set()
            raise GenerationCancelled(work.reason) from exc

    def _finish(self, identity: str, result: dict[str, Any]) -> None:
        work = self.work[identity]
        try:
            try:
                if work.cancel.is_set():
                    result["status"] = "cancelled"
                    result["reason"] = work.reason
                data = {
                    "reason": result["reason"],
                    "text": result["text"],
                    "metrics": result["metrics"],
                    "durable": work.durable,
                    "warning": ""
                    if work.durable
                    else (
                        "Some records could not be saved. Download this result before leaving; "
                        "no automatic rerun will occur."
                    ),
                }
                item = self._append(work, result["status"], data)
            except (KeyError, TypeError, ValueError, OverflowError, RecursionError):
                emitted = "".join(
                    value["data"]["text"]
                    for value in work.record["events"]
                    if value["event"] == "token"
                )
                item = self._append(
                    work,
                    "error",
                    {
                        "reason": "terminal_result_contract_failed",
                        "text": emitted[:2048],
                        "metrics": {},
                        "durable": work.durable,
                        "warning": (
                            "Terminal result violated its contract; displayed text may be a prefix. "
                            "The full emitted token events are retained."
                        ),
                    },
                )
            if not work.durable:
                item["data"]["durable"] = False
                item["data"]["warning"] = (
                    "Some records could not be saved. Download this result before leaving; "
                    "no automatic rerun will occur."
                    if item["data"]["reason"] != "terminal_result_contract_failed"
                    else "Terminal contract failed; this text may be a prefix. Full token events "
                    "remain in memory. Saving failed; download before leaving."
                )
        finally:
            self.reserved_tokens -= len(work.tokens) + work.spec.max_new_tokens
            work.finished.set()
            del self.work[identity]

    async def cancel(self, identity: str, reason: str = "cancelled_by_user") -> dict[str, Any]:
        async with self.lock:
            if identity not in self.records:
                raise KeyError(identity)
            if identity not in self.work:
                return self.state(identity)
            work = self.work[identity]
            work.reason = reason
            work.cancel.set()
            work.attached.set()
            if identity in self.pending:
                self.pending.remove(identity)
                self._finish(
                    identity, {"status": "cancelled", "reason": reason, "text": "", "metrics": {}}
                )
            return self.state(identity)

    async def _run(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            await self.wake.wait()
            async with self.lock:
                if not self.pending:
                    self.wake.clear()
                    if self.closing:
                        return
                    continue
                identity = self.pending.popleft()
                work = self.work[identity]
                self.running = identity
            result: dict[str, Any]
            try:
                try:
                    await asyncio.wait_for(work.attached.wait(), self.attach_seconds)
                except TimeoutError:
                    work.reason = "subscriber_attach_timeout"
                    work.cancel.set()
                if work.cancel.is_set():
                    result = {
                        "status": "cancelled",
                        "reason": work.reason,
                        "text": "",
                        "metrics": {},
                    }
                else:
                    queued = time.perf_counter() - work.admitted
                    async with self.lock:
                        start_event = self._append(
                            work, "started", {"queue_seconds": queued, "device": self.engine.device}
                        )
                    await work.buffer.put(start_event)

                    def emit(data: dict[str, Any], current: Work = work) -> None:
                        future = asyncio.run_coroutine_threadsafe(self._emit(current, data), loop)
                        future.result()

                    result = await asyncio.to_thread(
                        self.engine.generate, work.spec, work.tokens, work.cancel, emit
                    )
                    result["metrics"]["queue_seconds"] = queued
            except Exception:
                result = {
                    "status": "error",
                    "reason": "inference_failed",
                    "text": "".join(
                        item["data"]["text"]
                        for item in work.record["events"]
                        if item["event"] == "token"
                    ),
                    "metrics": {},
                }
            async with self.lock:
                try:
                    self._finish(identity, result)
                finally:
                    self.running = None

    async def subscribe(self, identity: str, after: int = 0) -> AsyncIterator[dict[str, Any]]:
        async with self.lock:
            if identity not in self.records:
                raise KeyError(identity)
            record = self.records[identity]
            if type(after) is not int or not 0 <= after <= len(record["events"]):
                raise ContractError("Event cursor must name an existing event or zero")
            work = self.work.get(identity)
            if work is not None:
                if work.subscriber:
                    raise Busy("This active request already has a stream subscriber")
                work.subscriber = True
                work.attached.set()
            snapshot = list(record["events"][after:])

        async def iterate() -> AsyncIterator[dict[str, Any]]:
            last = after
            try:
                for item in snapshot:
                    last = item["id"]
                    yield item
                if work is not None:
                    while True:
                        if work.finished.is_set() and work.buffer.empty():
                            for item in record["events"][last:]:
                                last = item["id"]
                                yield item
                            return
                        try:
                            item = await asyncio.wait_for(work.buffer.get(), 0.1)
                        except TimeoutError:
                            continue
                        if item["id"] > last:
                            last = item["id"]
                            yield item
            finally:
                if work is not None:
                    work.subscriber = False
                    if not work.finished.is_set():
                        await self.cancel(identity, "subscriber_disconnected")

        return iterate()
