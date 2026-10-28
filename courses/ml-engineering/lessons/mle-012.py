"""mle-012: worked starting point; complete the guide's six changes."""

import numpy as np
import pandas as pd


def dataset():
    rng = np.random.default_rng(17)
    n = 120
    usage = rng.uniform(1, 100, n)
    tickets = rng.poisson(2, n)
    region = np.where(np.arange(n) % 2 == 0, "north", "south")
    logit = 0.9 * tickets - 0.035 * usage + (region == "north") * 0.3
    probability = 1 / (1 + np.exp(-logit))
    label = (rng.random(n) < probability).astype(int)
    cutoff = np.arange(n) + 100
    return pd.DataFrame(
        {
            "id": np.arange(n),
            "customer_id": np.arange(n) % 12,
            "cutoff": cutoff,
            "available_at": cutoff - 2,
            "label_available_at": cutoff + 4,
            "usage": usage,
            "tickets": tickets,
            "region": region,
            "label": label,
        }
    )


def fit_pipeline(frame):
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    transform = ColumnTransformer(
        [
            ("numeric", numeric, ["usage", "tickets"]),
            ("region", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["region"]),
        ]
    )
    model = Pipeline(
        [("features", transform), ("classifier", LogisticRegression(max_iter=200, random_state=17))]
    )
    model.fit(frame[["usage", "tickets", "region"]], frame["label"])
    return model


def serving_app(model):
    from typing import Literal

    from fastapi import FastAPI
    from pydantic import BaseModel, ConfigDict, Field

    class Request(BaseModel):
        model_config = ConfigDict(extra="forbid")
        usage: float = Field(ge=0, le=10000)
        tickets: int = Field(ge=0, le=100)
        region: Literal["north", "south"]

    app = FastAPI()

    @app.post("/predict")
    def predict(request: Request):
        frame = pd.DataFrame([request.model_dump()])
        return {
            "probability": float(model.predict_proba(frame)[0, 1]),
            "model_version": "fixture-v1",
        }

    return app


def example_one():
    from fastapi.testclient import TestClient

    frame = dataset()
    model = fit_pipeline(frame[frame.label_available_at <= 180])
    payload = {"usage": 20.0, "tickets": 2, "region": "north"}
    with TestClient(serving_app(model)) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        expected = float(model.predict_proba(pd.DataFrame([payload]))[0, 1])
        assert abs(response.json()["probability"] - expected) < 1e-12
        assert response.json()["model_version"] == "fixture-v1"
        return {
            "in_process_asgi_status": 200,
            "model_parity": True,
            "no_network_server_started": True,
        }


if __name__ == "__main__":
    print(example_one())

# TODO 1: Submit usage 0 and the declared maximum.
# TODO 2: Add label to an otherwise valid request.
# TODO 3: Keep the returned version with a prediction record.
# TODO 4: Submit an unknown region.
# TODO 5: List what the in-process client has not tested.
# TODO 6: Describe a diagnostic that avoids exposing credentials or internals.
