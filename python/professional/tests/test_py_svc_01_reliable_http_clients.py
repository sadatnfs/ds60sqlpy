"""Tests for the python-svc-01 reference implementation."""

from __future__ import annotations

import unittest

from python.professional.solutions.py_svc_01_reliable_http_clients_solution import (
    ClientConfig,
    MemoryLog,
    PermanentHttpError,
    ReliableClient,
    Response,
    ResponseProtocolError,
    RetryExhausted,
    RetryPolicy,
    ScriptedTransport,
    TransportTimeout,
    classify_status,
    redact_headers,
    redact_url,
)


def make_client(
    transport: ScriptedTransport,
    *,
    delays: list[float] | None = None,
    log: MemoryLog | None = None,
) -> ReliableClient:
    return ReliableClient(
        config=ClientConfig(
            base_url="https://local.invalid",
            auth_token="credential-used-only-by-fake",
            timeout_seconds=0.25,
        ),
        transport=transport,
        retry_policy=RetryPolicy(
            max_attempts=3,
            base_delay_seconds=0.25,
            maximum_delay_seconds=3.0,
        ),
        sleep=(delays if delays is not None else []).append,
        jitter=lambda: 0.0,
        id_factory=lambda: "correlation-test",
        log=log if log is not None else MemoryLog(),
    )


class RetryPolicyTests(unittest.TestCase):
    def test_safe_get_retries_retryable_status(self) -> None:
        transport = ScriptedTransport([Response(503), Response(200)])
        delays: list[float] = []
        client = make_client(transport, delays=delays)

        response = client.request("GET", "/health")

        self.assertEqual(response.status, 200)
        self.assertEqual(len(transport.requests), 2)
        self.assertEqual(delays, [0.25])
        self.assertEqual(
            transport.requests[0].headers["X-Correlation-ID"],
            transport.requests[1].headers["X-Correlation-ID"],
        )
        self.assertEqual(transport.requests[0].timeout_seconds, 0.25)

    def test_permanent_status_is_not_retried(self) -> None:
        transport = ScriptedTransport([Response(400), Response(200)])
        client = make_client(transport)

        with self.assertRaises(PermanentHttpError) as caught:
            client.request("GET", "/bad")

        self.assertEqual(caught.exception.status, 400)
        self.assertEqual(len(transport.requests), 1)

    def test_post_requires_idempotency_key_before_replay(self) -> None:
        without_key = ScriptedTransport([Response(503), Response(200)])
        with self.assertRaises(PermanentHttpError):
            make_client(without_key).request("POST", "/orders", json_body={"qty": 1})
        self.assertEqual(len(without_key.requests), 1)

        with_key = ScriptedTransport([Response(503), Response(200)])
        response = make_client(with_key).request(
            "POST",
            "/orders",
            json_body={"qty": 1},
            idempotency_key="order-1001",
        )
        self.assertEqual(response.status, 200)
        self.assertTrue(
            all(request.headers["Idempotency-Key"] == "order-1001" for request in with_key.requests)
        )

    def test_429_honors_bounded_retry_after(self) -> None:
        transport = ScriptedTransport([Response(429, headers={"Retry-After": "2"}), Response(200)])
        delays: list[float] = []

        make_client(transport, delays=delays).request("GET", "/limited")

        self.assertEqual(delays, [2.0])

    def test_timeout_reports_context_after_exhaustion(self) -> None:
        transport = ScriptedTransport(
            [TransportTimeout("one"), TransportTimeout("two"), TransportTimeout("three")]
        )
        with self.assertRaises(RetryExhausted) as caught:
            make_client(transport).request("GET", "/slow")

        self.assertEqual(caught.exception.attempts, 3)
        self.assertIn("correlation-test", str(caught.exception))

    def test_status_validation_rejects_impossible_values(self) -> None:
        self.assertEqual(classify_status(200), "success")
        self.assertEqual(classify_status(503), "retryable")
        self.assertEqual(classify_status(404), "permanent")
        with self.assertRaises(ValueError):
            classify_status(700)


class PaginationAndLoggingTests(unittest.TestCase):
    def test_pagination_stops_at_null_cursor(self) -> None:
        transport = ScriptedTransport(
            [
                Response(200, json_body={"items": [{"id": 1}], "next_cursor": "p2"}),
                Response(200, json_body={"items": [{"id": 2}], "next_cursor": None}),
            ]
        )
        items = make_client(transport).get_all_pages("/items")

        self.assertEqual(items, [{"id": 1}, {"id": 2}])
        self.assertEqual(len(transport.requests), 2)
        self.assertTrue(transport.requests[1].url.endswith("cursor=p2"))

    def test_pagination_detects_repeated_cursor(self) -> None:
        transport = ScriptedTransport(
            [
                Response(200, json_body={"items": [], "next_cursor": "same"}),
                Response(200, json_body={"items": [], "next_cursor": "same"}),
            ]
        )
        with self.assertRaises(ResponseProtocolError):
            make_client(transport).get_all_pages("/items")

    def test_logs_redact_credentials_and_sensitive_query_values(self) -> None:
        log = MemoryLog()
        transport = ScriptedTransport([Response(200)])
        client = make_client(transport, log=log)

        client.request("GET", "/profile", query={"access_token": "query-value"})

        rendered = repr(log.events)
        self.assertNotIn("credential-used-only-by-fake", rendered)
        self.assertNotIn("query-value", rendered)
        self.assertIn("<redacted>", rendered)
        self.assertEqual(
            redact_headers({"authorization": "private", "Accept": "json"}),
            {"authorization": "<redacted>", "Accept": "json"},
        )
        self.assertEqual(
            redact_url("https://local.invalid/x?api_key=value"),
            "https://local.invalid/x?api_key=<redacted>",
        )

    def test_configuration_repr_hides_auth_token(self) -> None:
        config = ClientConfig(
            base_url="https://local.invalid",
            auth_token="must-not-appear",
        )
        self.assertNotIn("must-not-appear", repr(config))
        with self.assertRaises(ValueError):
            ClientConfig.from_env({})


if __name__ == "__main__":
    unittest.main()
