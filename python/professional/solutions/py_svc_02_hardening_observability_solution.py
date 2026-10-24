"""Reference implementation for python-svc-02.

This is a local policy model, not an Internet-facing server. All dependencies,
identity, time, work, and artifact files are injected or temporary.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import threading
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import TracebackType
from typing import Literal, Protocol, TypeAlias

Role = Literal["reader", "operator"]
JsonScalar: TypeAlias = str | int | float | bool | None


class Clock(Protocol):
    def now(self) -> float:
        """Return monotonic-style seconds."""


class DependencyProbe(Protocol):
    def ready(self) -> bool:
        """Return whether the dependency can serve new work."""


class Authenticator(Protocol):
    def authenticate(self, token: str) -> Principal | None:
        """Resolve a credential without logging it."""


@dataclass(frozen=True)
class ServiceConfig:
    max_concurrency: int
    rate_capacity: int
    refill_per_second: float

    @classmethod
    def from_mapping(cls, values: Mapping[str, str]) -> ServiceConfig:
        try:
            max_concurrency = int(values.get("MAX_CONCURRENCY", "4"))
            rate_capacity = int(values.get("RATE_CAPACITY", "10"))
            refill_per_second = float(values.get("REFILL_PER_SECOND", "2"))
        except ValueError as exc:
            raise ValueError("service limits must be numeric") from exc
        if max_concurrency < 1 or rate_capacity < 1 or refill_per_second <= 0:
            raise ValueError("service limits must be positive")
        return cls(max_concurrency, rate_capacity, refill_per_second)


@dataclass(frozen=True)
class Principal:
    subject: str
    role: Role


@dataclass
class StaticAuthenticator:
    identities: Mapping[str, Principal] = field(repr=False)

    def authenticate(self, token: str) -> Principal | None:
        return self.identities.get(token)


@dataclass
class FixedProbe:
    value: bool

    def ready(self) -> bool:
        return self.value


@dataclass(frozen=True)
class Status:
    ok: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class LogEvent:
    event: str
    request_id: str
    fields: tuple[tuple[str, str], ...]


@dataclass
class StructuredLog:
    events: list[LogEvent] = field(default_factory=list)

    def emit(
        self,
        event: str,
        request_id: str,
        fields: Mapping[str, str],
    ) -> None:
        self.events.append(
            LogEvent(
                event,
                request_id,
                tuple(sorted(redact_fields(fields).items())),
            )
        )


@dataclass
class Metrics:
    counters: dict[str, int] = field(default_factory=dict)
    durations: dict[str, list[float]] = field(default_factory=dict)

    def increment(self, name: str) -> None:
        self.counters[name] = self.counters.get(name, 0) + 1

    def observe(self, name: str, value: float) -> None:
        if value < 0:
            raise ValueError("duration must be non-negative")
        self.durations.setdefault(name, []).append(value)

    def snapshot(self) -> dict[str, int | tuple[float, ...]]:
        result: dict[str, int | tuple[float, ...]] = dict(self.counters)
        result.update({name: tuple(values) for name, values in self.durations.items()})
        return result


@dataclass
class FixedClock:
    value: float

    def now(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("clock cannot move backward")
        self.value += seconds


@dataclass
class TokenBucket:
    capacity: int
    refill_per_second: float
    clock: Clock
    _state: dict[str, tuple[float, float]] = field(default_factory=dict)

    def allow(self, subject: str) -> bool:
        if not subject:
            raise ValueError("rate-limit subject must not be blank")
        now = self.clock.now()
        tokens, previous = self._state.get(subject, (float(self.capacity), now))
        tokens = min(
            float(self.capacity),
            tokens + max(0.0, now - previous) * self.refill_per_second,
        )
        if tokens < 1.0:
            self._state[subject] = (tokens, now)
            return False
        self._state[subject] = (tokens - 1.0, now)
        return True


class ConcurrencyLease:
    def __init__(self, gate: ConcurrencyGate) -> None:
        self._gate = gate
        self._released = False

    def __enter__(self) -> ConcurrencyLease:
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        if not self._released:
            self._released = True
            self._gate.release()
        return False


class ConcurrencyGate:
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self._semaphore = threading.BoundedSemaphore(capacity)
        self._lock = threading.Lock()
        self._active = 0
        self._peak = 0

    @property
    def active(self) -> int:
        with self._lock:
            return self._active

    @property
    def peak(self) -> int:
        with self._lock:
            return self._peak

    def try_acquire(self) -> ConcurrencyLease | None:
        if not self._semaphore.acquire(blocking=False):
            return None
        with self._lock:
            self._active += 1
            self._peak = max(self._peak, self._active)
        return ConcurrencyLease(self)

    def release(self) -> None:
        with self._lock:
            if self._active < 1:
                raise RuntimeError("concurrency lease released twice")
            self._active -= 1
        self._semaphore.release()


def is_authorized(role: Role, action: str) -> bool:
    permissions: dict[Role, frozenset[str]] = {
        "reader": frozenset({"predict"}),
        "operator": frozenset({"predict", "reload"}),
    }
    return action in permissions[role]


def readiness(
    dependency_checks: Sequence[bool],
    *,
    artifact_verified: bool,
    draining: bool,
) -> bool:
    return bool(dependency_checks) and all(dependency_checks) and artifact_verified and not draining


def redact_fields(fields: Mapping[str, str]) -> dict[str, str]:
    sensitive = {"token", "authorization", "password", "secret", "api_key"}
    return {
        key: "<redacted>" if key.lower() in sensitive else value for key, value in fields.items()
    }


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_trusted_json(path: Path, expected_sha256: str) -> dict[str, JsonScalar]:
    if len(expected_sha256) != 64 or sha256_file(path) != expected_sha256:
        raise ValueError("artifact hash verification failed")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not all(
        isinstance(key, str) and (value is None or isinstance(value, str | int | float | bool))
        for key, value in raw.items()
    ):
        raise ValueError("trusted artifact must be a flat JSON object")
    return raw


@dataclass(frozen=True)
class ServiceResponse:
    status: int
    message: str


@dataclass
class HardenedService:
    dependencies: Mapping[str, DependencyProbe]
    artifact_verified: bool
    authenticator: Authenticator
    rate_limiter: TokenBucket
    gate: ConcurrencyGate
    log: StructuredLog
    metrics: Metrics
    clock: Clock
    draining: bool = False

    def health(self) -> Status:
        return Status(True)

    def ready(self) -> Status:
        reasons = [] if self.dependencies else ["dependency:none_configured"]
        reasons.extend(
            f"dependency:{name}" for name, probe in self.dependencies.items() if not probe.ready()
        )
        if not self.artifact_verified:
            reasons.append("artifact:not_verified")
        if self.draining:
            reasons.append("service:draining")
        return Status(not reasons, tuple(sorted(reasons)))

    def handle(
        self,
        *,
        request_id: str,
        token: str,
        action: str,
        work: Callable[[], str],
    ) -> ServiceResponse:
        if not request_id.strip():
            return ServiceResponse(400, "request ID required")
        ready = self.ready()
        if not ready.ok:
            self.metrics.increment("requests_not_ready")
            self.log.emit(
                "request_rejected",
                request_id,
                {"reason": ",".join(ready.reasons)},
            )
            return ServiceResponse(503, "not ready")
        principal = self.authenticator.authenticate(token)
        if principal is None:
            self.metrics.increment("requests_unauthenticated")
            return ServiceResponse(401, "authentication required")
        if not is_authorized(principal.role, action):
            self.metrics.increment("requests_forbidden")
            return ServiceResponse(403, "forbidden")
        if not self.rate_limiter.allow(principal.subject):
            self.metrics.increment("requests_rate_limited")
            return ServiceResponse(429, "rate limited")
        lease = self.gate.try_acquire()
        if lease is None:
            self.metrics.increment("requests_saturated")
            return ServiceResponse(503, "busy")

        started = self.clock.now()
        with lease:
            self.log.emit(
                "request_started",
                request_id,
                {"action": action, "subject": principal.subject},
            )
            try:
                message = work()
            except Exception as exc:
                self.metrics.increment("requests_failed")
                self.log.emit(
                    "request_failed",
                    request_id,
                    {"error_type": type(exc).__name__},
                )
                return ServiceResponse(500, "internal error")
            finally:
                self.metrics.observe("request_duration_seconds", self.clock.now() - started)
        self.metrics.increment("requests_succeeded")
        self.log.emit("request_completed", request_id, {"action": action})
        return ServiceResponse(200, message)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ds60-service-drill-") as directory:
        artifact = Path(directory) / "model.json"
        artifact.write_text('{"format":"local-json-v1","version":1}', encoding="utf-8")
        load_trusted_json(artifact, sha256_file(artifact))

        clock = FixedClock(10.0)
        dependency = FixedProbe(True)
        service = HardenedService(
            dependencies={"model-store": dependency},
            artifact_verified=True,
            authenticator=StaticAuthenticator({"local-reader": Principal("learner", "reader")}),
            rate_limiter=TokenBucket(2, 1.0, clock),
            gate=ConcurrencyGate(1),
            log=StructuredLog(),
            metrics=Metrics(),
            clock=clock,
        )
        print(
            "normal request:",
            service.handle(
                request_id="request-1",
                token="local-reader",
                action="predict",
                work=lambda: "prediction-local",
            ),
        )
        dependency.value = False
        print("incident readiness:", service.ready())
        print("health stays process-level:", service.health())
        print("metrics:", service.metrics.snapshot())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
