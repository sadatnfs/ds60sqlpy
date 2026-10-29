# pyweb-071: Integration, failure and load testing

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-070`.

## Starting point and result

A useful test suite combines successful boundary cases, invalid inputs, side-effect checks and recovery after failure. This chapter executes a small unittest suite against a real FastAPI application. It deliberately does not call those tests a load benchmark or a deployed-service acceptance test.

## Mechanism: each test states a behavioral claim

The fixture accepts a strict integer quantity between 1 and 5. A successful request appends one effect and returns 201. An unavailable dependency causes 503 before the append. Each test creates a fresh application and effects list, then closes its TestClient during teardown.

Isolation matters because a test that depends on another test's mutation can pass in one order and fail in another. A fresh fixture gives each case its own state and makes parallel execution practical. Shared real databases need separately owned namespaces or reviewed grouping, not accidental cross-test interference.

The suite uses subtests for related input values so a failure reports the particular boundary value. It still checks final side effects, because response status alone cannot establish that invalid requests left state unchanged.

## Worked case: valid boundaries and invalid types

The successful test submits the minimum and maximum allowed quantities and verifies both responses and effects. The invalid test submits values below and above the range, a boolean, a numeric string and null. Each receives 422, and the effects list stays empty.

Strictness is meaningful here. Python booleans behave like integers in some contexts, and permissive parsers can coerce numeric strings. The request model deliberately refuses those forms so the accepted wire contract is narrower than an informal numeric-looking value.

A larger API should also test extra fields, missing fields, malformed JSON, content types and meaningful domain combinations. The purpose is not to maximize a test count with redundant assertions, but to cover different failure mechanisms and invariants.

## Worked case: fail a dependency, then recover

The second behavior disables the controlled dependency flag, sends a valid request and receives 503 without an effect. It then restores availability, repeats a valid request and observes one successful effect.

This checks recovery, which a failure-only test can miss. A resource may remain poisoned after an error, or an exception handler may close shared state accidentally. A successful operation after the failure demonstrates that the finite fixture returned to a usable state.

The dependency flag is an explicit fault-injection seam, not a simulated network outage presented as one. The owned workshop separately stops/restarts actual service components and observes durable state. Both kinds of tests are useful when their claims remain distinct.

## Failure diagnosis and discussion

**Why not measure requests per second here?** In-process client execution, synthetic handlers and shared host scheduling do not represent the deployed workload. Load testing needs an actual server path, controlled concurrency, latency distributions and resource/error observations.

**Why test state after a refusal?** An implementation can return the expected error after already mutating storage. The no-effect assertion catches that ordering defect.

If tests fail only in parallel, inspect shared settings, files, ports and databases rather than adding sleeps. Django examples intentionally run in fresh processes because its settings registry is global. If a recovery test fails, inspect rollback and resource ownership.

Continue with the final review, which connects framework choices to request, data, background-work and deployment contracts and maps each claim to the evidence that actually establishes it.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Finite cross-framework engineering investigation with explicit scope."""

import json
import unittest


def run_cases():
    from fastapi import FastAPI, HTTPException
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, ConfigDict, Field

    class Input(BaseModel):
        model_config = ConfigDict(extra="forbid", strict=True)
        quantity: int = Field(ge=1, le=5)

    class Contract(unittest.TestCase):
        def setUp(self):
            self.effects = []
            self.available = True
            app = FastAPI(docs_url=None, redoc_url=None)

            @app.post("/reserve", status_code=201)
            def reserve(payload: Input):
                if not self.available:
                    raise HTTPException(503, "Dependency unavailable")
                self.effects.append(payload.quantity)
                return {"quantity": payload.quantity}

            self.client = TestClient(app).__enter__()

        def tearDown(self):
            self.client.__exit__(None, None, None)

        def test_valid_boundary_values(self):
            for value in [1, 5]:
                with self.subTest(value=value):
                    response = self.client.post("/reserve", json={"quantity": value})
                    self.assertEqual(response.status_code, 201)
                    self.assertEqual(response.json(), {"quantity": value})
            self.assertEqual(self.effects, [1, 5])

        def test_invalid_values_have_no_effect(self):
            for value in [0, 6, True, "2", None]:
                with self.subTest(value=value):
                    self.assertEqual(
                        self.client.post("/reserve", json={"quantity": value}).status_code, 422
                    )
            self.assertEqual(self.effects, [])

        def test_failure_then_recovery(self):
            self.available = False
            self.assertEqual(self.client.post("/reserve", json={"quantity": 2}).status_code, 503)
            self.assertEqual(self.effects, [])
            self.available = True
            self.assertEqual(self.client.post("/reserve", json={"quantity": 2}).status_code, 201)
            self.assertEqual(self.effects, [2])

    result = unittest.TestResult()
    unittest.defaultTestLoader.loadTestsFromTestCase(Contract).run(result)
    assert result.wasSuccessful(), str(result.errors + result.failures)
    return {
        "contract_tests": result.testsRun,
        "failed": len(result.failures),
        "errors": len(result.errors),
        "load_testing": "not performed by this finite unit suite",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True))
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/)
