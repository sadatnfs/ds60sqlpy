"""Tests for python-svc-02."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from python.professional.solutions.py_svc_02_hardening_observability_solution import (
    ConcurrencyGate,
    FixedClock,
    FixedProbe,
    HardenedService,
    Metrics,
    Principal,
    ServiceConfig,
    StaticAuthenticator,
    StructuredLog,
    TokenBucket,
    load_trusted_json,
    sha256_file,
)


def build_service() -> tuple[HardenedService, FixedProbe, FixedClock]:
    clock = FixedClock(10.0)
    dependency = FixedProbe(True)
    service = HardenedService(
        dependencies={"artifact-store": dependency},
        artifact_verified=True,
        authenticator=StaticAuthenticator(
            {
                "reader-local": Principal("reader-1", "reader"),
                "operator-local": Principal("operator-1", "operator"),
            }
        ),
        rate_limiter=TokenBucket(2, 1.0, clock),
        gate=ConcurrencyGate(1),
        log=StructuredLog(),
        metrics=Metrics(),
        clock=clock,
    )
    return service, dependency, clock


class ServiceHardeningTests(unittest.TestCase):
    def test_configuration_rejects_unsafe_limits(self) -> None:
        self.assertEqual(
            ServiceConfig.from_mapping({}),
            ServiceConfig(4, 10, 2.0),
        )
        with self.assertRaises(ValueError):
            ServiceConfig.from_mapping({"MAX_CONCURRENCY": "0"})

    def test_health_and_readiness_have_different_semantics(self) -> None:
        service, dependency, _clock = build_service()
        self.assertTrue(service.health().ok)
        self.assertTrue(service.ready().ok)
        dependency.value = False
        self.assertTrue(service.health().ok)
        self.assertFalse(service.ready().ok)
        self.assertIn("dependency:artifact-store", service.ready().reasons)

        service.dependencies = {}
        self.assertIn("dependency:none_configured", service.ready().reasons)

    def test_authentication_authorization_and_success_metrics(self) -> None:
        service, _dependency, _clock = build_service()
        unauthenticated = service.handle(
            request_id="r1",
            token="unknown",
            action="predict",
            work=lambda: "never",
        )
        forbidden = service.handle(
            request_id="r2",
            token="reader-local",
            action="reload",
            work=lambda: "never",
        )
        success = service.handle(
            request_id="r3",
            token="reader-local",
            action="predict",
            work=lambda: "prediction",
        )
        self.assertEqual(
            (unauthenticated.status, forbidden.status, success.status),
            (401, 403, 200),
        )
        self.assertEqual(service.metrics.counters["requests_succeeded"], 1)
        self.assertEqual(service.gate.active, 0)

    def test_rate_limit_refills_with_injected_clock(self) -> None:
        service, _dependency, clock = build_service()
        statuses = [
            service.handle(
                request_id=f"r{number}",
                token="reader-local",
                action="predict",
                work=lambda: "ok",
            ).status
            for number in range(3)
        ]
        self.assertEqual(statuses, [200, 200, 429])
        clock.advance(1.0)
        self.assertEqual(
            service.handle(
                request_id="r4",
                token="reader-local",
                action="predict",
                work=lambda: "ok",
            ).status,
            200,
        )

    def test_concurrency_gate_rejects_saturation_without_waiting(self) -> None:
        gate = ConcurrencyGate(1)
        first = gate.try_acquire()
        self.assertIsNotNone(first)
        assert first is not None
        with first:
            self.assertIsNone(gate.try_acquire())
            self.assertEqual(gate.active, 1)
        self.assertEqual(gate.active, 0)
        self.assertEqual(gate.peak, 1)

    def test_artifact_hash_precedes_json_trust(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ds60-trusted-artifact-") as directory:
            path = Path(directory) / "artifact.json"
            path.write_text('{"format":"local","version":1}', encoding="utf-8")
            expected = sha256_file(path)
            self.assertEqual(load_trusted_json(path, expected)["version"], 1)
            path.write_text('{"format":"local","version":2}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash"):
                load_trusted_json(path, expected)

    def test_logs_keep_request_context_without_credentials(self) -> None:
        service, _dependency, _clock = build_service()
        service.handle(
            request_id="trace-1",
            token="reader-local",
            action="predict",
            work=lambda: "ok",
        )
        rendered = repr(service.log.events)
        self.assertIn("trace-1", rendered)
        self.assertNotIn("reader-local", rendered)

    def test_local_incident_drill_rejects_new_work(self) -> None:
        service, dependency, _clock = build_service()
        dependency.value = False
        response = service.handle(
            request_id="incident-1",
            token="reader-local",
            action="predict",
            work=lambda: "never",
        )
        self.assertEqual(response.status, 503)
        self.assertEqual(service.metrics.counters["requests_not_ready"], 1)
        self.assertEqual(service.log.events[-1].event, "request_rejected")


if __name__ == "__main__":
    unittest.main()
