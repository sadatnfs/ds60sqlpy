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
