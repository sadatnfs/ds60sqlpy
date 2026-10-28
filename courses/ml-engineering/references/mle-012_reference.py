"""mle-012: local, bounded ML engineering investigation."""

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


def example_two():
    from fastapi.testclient import TestClient

    frame = dataset()
    model = fit_pipeline(frame[frame.label_available_at <= 180])
    with TestClient(serving_app(model)) as client:
        negative = client.post("/predict", json={"usage": -1, "tickets": 2, "region": "north"})
        extra = client.post(
            "/predict", json={"usage": 1, "tickets": 2, "region": "north", "label": 1}
        )
        assert negative.status_code == 422 and extra.status_code == 422
        return {"negative_value_rejected": 422, "undeclared_target_field_rejected": 422}


def main():
    print(example_one())
    print(example_two())
    print("mle-012 reference checks passed")


if __name__ == "__main__":
    main()
