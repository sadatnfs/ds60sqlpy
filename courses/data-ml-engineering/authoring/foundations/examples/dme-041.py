"""Actual fitted-model batch/ASGI parity with explicit feature freshness and version checks."""

import math

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field
from sklearn.linear_model import LogisticRegression

MODEL_VERSION = "route-risk-v1"
OBSERVATION_HOUR = 48


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    request_id: str = Field(min_length=1, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    load: float = Field(ge=0, le=20, allow_inf_nan=False)
    backlog: float = Field(ge=0, le=20, allow_inf_nan=False)
    event_hour: int = Field(ge=0)
    known_hour: int = Field(ge=0)


class Request(Observation):
    expected_model: str


def trained_model():
    features = np.array(
        [[0, 0], [1, 1], [2, 1], [3, 2], [6, 5], [7, 6], [8, 7], [9, 8]], dtype=float
    )
    labels = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    return LogisticRegression(C=10, random_state=7).fit(features, labels)


def score(model, records):
    observations = [Observation.model_validate(record) for record in records]
    if not 1 <= len(observations) <= 10 or len({row.request_id for row in observations}) != len(
        observations
    ):
        raise ValueError("Use one to ten uniquely identified observations")
    if any(
        not row.event_hour <= row.known_hour <= OBSERVATION_HOUR
        or not 0 <= OBSERVATION_HOUR - row.event_hour <= 24
        for row in observations
    ):
        raise ValueError("Features must be known by decision time and observed within 24 hours")
    matrix = np.array([[row.load, row.backlog] for row in observations])
    probabilities = model.predict_proba(matrix)[:, 1]
    return [
        {
            "request_id": row.request_id,
            "probability": float(value),
            "model_version": MODEL_VERSION,
            "decision_hour": OBSERVATION_HOUR,
        }
        for row, value in zip(observations, probabilities, strict=True)
    ]


def application(model):
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.post("/predict")
    def predict(request: Request):
        if request.expected_model != MODEL_VERSION:
            raise HTTPException(409, "The requested model version is not active")
        try:
            return score(model, [request.model_dump(exclude={"expected_model"})])[0]
        except ValueError as error:
            raise HTTPException(422, str(error)) from error

    return app


def fixture():
    return [
        {"request_id": "A", "load": 1.0, "backlog": 1.0, "event_hour": 46, "known_hour": 48},
        {"request_id": "B", "load": 8.0, "backlog": 6.0, "event_hour": 24, "known_hour": 25},
    ]


def example_one():
    model = trained_model()
    batch = score(model, fixture())
    with TestClient(application(model)) as client:
        online = [
            client.post("/predict", json={**row, "expected_model": MODEL_VERSION}).json()
            for row in fixture()
        ]
    assert batch == online
    independent = [
        1
        / (
            1
            + math.exp(
                -(
                    float(model.intercept_[0])
                    + sum(
                        float(weight) * row[name]
                        for weight, name in zip(model.coef_[0], ["load", "backlog"], strict=True)
                    )
                )
            )
        )
        for row in fixture()
    ]
    assert all(
        math.isclose(row["probability"], expected, abs_tol=1e-12)
        for row, expected in zip(batch, independent, strict=True)
    )
    assert batch[0]["probability"] < 0.5 < batch[1]["probability"]
    return {
        "batch": batch,
        "actual_asgi": online,
        "independent_logistic_formula": independent,
        "network_server_was_not_started": True,
    }


def example_two():
    model = trained_model()
    with TestClient(application(model)) as client:
        baseline = {**fixture()[0], "expected_model": MODEL_VERSION}
        changed = [
            ({**baseline, "event_hour": 23, "known_hour": 48}, 422),
            ({**baseline, "known_hour": 49}, 422),
            ({**baseline, "expected_model": "unavailable-v2"}, 409),
            ({**baseline, "unreviewed_feature": 10}, 422),
        ]
        observed = [client.post("/predict", json=payload).status_code for payload, _ in changed]
        assert observed == [expected for _, expected in changed]
        assert client.post("/predict", json=baseline).status_code == 200
    return {
        "stale_future_version_and_extra_field_statuses": observed,
        "valid_request_still_accepted": True,
    }


def main():
    from ds60sqlpy.plot_artifacts import publish_report, publish_table

    first, second = example_one(), example_two()
    print("Same accepted model through batch and request contracts:", first)
    print("Rejected conditions do not silently change the model:", second)
    publish_table(
        ["request_id", "probability", "model_version"],
        [[row["request_id"], row["probability"], row["model_version"]] for row in first["batch"]],
        description=(
            "Synthetic fitted logistic model: batch and ASGI predictions match by request identity."
        ),
    )
    publish_report(
        second,
        description=(
            "Observed HTTP contract failures for stale/future features, "
            "unavailable versions and extra fields."
        ),
    )


if __name__ == "__main__":
    main()
