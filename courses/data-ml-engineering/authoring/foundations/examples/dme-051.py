"""Actual Feast historical/online features, fitted pipeline, MLflow model and ASGI inference."""

import hashlib
import importlib.metadata
import io
import json
import os
import re
import tempfile
from contextlib import redirect_stdout
from datetime import UTC, datetime, timedelta
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from feast import Entity, FeatureStore, FeatureView, Field, FileSource, ValueType
from feast.types import Float32
from mlflow import MlflowClient
from mlflow.models import infer_signature
from pydantic import BaseModel, ConfigDict
from pydantic import Field as InputField
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

CONTRACT = {"feature": "signal", "unit": "dimensionless", "population": "synthetic-accounts-v1"}
MODEL_NAME = "dme-connected-model"


def contract_digest(contract):
    return hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()


def fixtures():
    records = []
    requests = []
    for account in range(40):
        validation = account >= 20
        value = float(account % 20) + (0.25 if validation else 0)
        day = 3 if validation else 1
        records.append(
            {
                "account_id": account,
                "event_time": datetime(2024, 1, day, tzinfo=UTC),
                "known_at": datetime(2024, 1, day, 1, tzinfo=UTC),
                "signal": value,
            }
        )
        requests.append(
            {
                "request_id": account,
                "account_id": account,
                "event_timestamp": datetime(2024, 1, day + 1, tzinfo=UTC),
                "label": int(value >= 12),
                "validation": validation,
            }
        )
    records.append(
        {
            "account_id": 0,
            "event_time": datetime(2024, 1, 1, tzinfo=UTC),
            "known_at": datetime(2024, 1, 5, tzinfo=UTC),
            "signal": 99.0,
        }
    )
    return pd.DataFrame(records), pd.DataFrame(requests)


def feature_store(root):
    directory = root / "features"
    directory.mkdir()
    (directory / "feature_store.yaml").write_text(
        "project: dme_connected\nprovider: local\nregistry: registry.db\n"
        "online_store:\n  type: sqlite\n  path: online.db\nentity_key_serialization_version: 3\n"
    )
    features, requests = fixtures()
    history_path = directory / "history.parquet"
    features.to_parquet(history_path, index=False)
    cutoff = datetime(2024, 1, 4, tzinfo=UTC)
    accepted = features.loc[features.known_at <= cutoff].copy()
    accepted_path = directory / "accepted.parquet"
    accepted.to_parquet(accepted_path, index=False)
    entity = Entity(name="account", join_keys=["account_id"], value_type=ValueType.INT64)
    views = [
        FeatureView(
            name=name,
            entities=[entity],
            ttl=timedelta(days=7),
            schema=[Field(name="signal", dtype=Float32)],
            source=FileSource(
                path=str(path), timestamp_field="event_time", created_timestamp_column="known_at"
            ),
        )
        for name, path in [("history_signal", history_path), ("serving_signal", accepted_path)]
    ]
    store = FeatureStore(repo_path=str(directory))
    store.apply([entity, *views])
    historical = store.get_historical_features(
        entity_df=requests[["request_id", "account_id", "event_timestamp"]],
        features=["history_signal:signal"],
        filter_by_created_timestamp=True,
    ).to_df()
    joined = requests.merge(
        historical[["request_id", "signal"]], on="request_id", how="left", validate="1:1"
    ).sort_values("request_id")
    expected = [float(account % 20) + (0.25 if account >= 20 else 0) for account in range(40)]
    assert len(joined) == 40 and joined.signal.tolist() == expected and joined.signal.iloc[0] == 0
    progress = io.StringIO()
    with redirect_stdout(progress):
        store.materialize(
            start_date=datetime(2023, 12, 31, tzinfo=UTC),
            end_date=cutoff,
            feature_views=["serving_signal"],
        )
    print(re.sub(r"\x1b\[[0-9;]*m", "", progress.getvalue()), end="")
    return store, joined


def train_register_reload(root, rows):
    os.environ["GIT_PYTHON_REFRESH"] = "quiet"
    uri = "sqlite:///" + str(root / "tracking.db")
    mlflow.set_tracking_uri(uri)
    mlflow.set_registry_uri(uri)
    client = MlflowClient(tracking_uri=uri, registry_uri=uri)
    experiment = client.create_experiment(
        "connected-capstone", artifact_location=(root / "artifacts").as_uri()
    )
    train, validation = rows.loc[~rows.validation], rows.loc[rows.validation]
    model = make_pipeline(StandardScaler(), LogisticRegression(C=1000, random_state=51)).fit(
        train[["signal"]], train.label
    )
    accuracy = float(accuracy_score(validation.label, model.predict(validation[["signal"]])))
    assert accuracy >= 0.9
    requirements = [
        f"{name}=={importlib.metadata.version(name)}"
        for name in ("scikit-learn", "numpy", "pandas", "cloudpickle", "skops")
    ]
    created = client.create_run(experiment)
    with mlflow.start_run(run_id=created.info.run_id) as run:
        mlflow.log_params(
            {
                "feature_contract": contract_digest(CONTRACT),
                "training_rows": len(train),
                "validation_rows": len(validation),
            }
        )
        mlflow.log_metric("validation_accuracy", accuracy)
        mlflow.set_tag("source_sha256", hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        info = mlflow.sklearn.log_model(
            sk_model=model,
            name="candidate",
            input_example=train[["signal"]].iloc[:2],
            signature=infer_signature(train[["signal"]], model.predict(train[["signal"]])),
            pip_requirements=requirements,
        )
        registered = mlflow.register_model(info.model_uri, MODEL_NAME, await_registration_for=10)
        run_id = run.info.run_id
    loaded = mlflow.sklearn.load_model(info.model_uri)
    assert (
        loaded.predict(validation[["signal"]]).tolist()
        == model.predict(validation[["signal"]]).tolist()
    )
    client.set_registered_model_alias(MODEL_NAME, "accepted", str(registered.version))
    selected = client.get_model_version_by_alias(MODEL_NAME, "accepted")
    assert selected.run_id == run_id
    return (
        client,
        loaded,
        {
            "run_id": run_id,
            "model_version": str(registered.version),
            "validation_accuracy": accuracy,
            "training_rows": len(train),
            "validation_rows": len(validation),
            "feature_contract": contract_digest(CONTRACT),
        },
    )


class ScoringRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    account_id: int = InputField(ge=0)
    feature_contract: str
    expected_model: str


def application(store, model, card):
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.post("/predict")
    def predict(request: ScoringRequest):
        if (
            request.feature_contract != card["feature_contract"]
            or request.expected_model != card["model_version"]
        ):
            raise HTTPException(409, "Requested feature/model contract is not accepted")
        result = store.get_online_features(
            features=["serving_signal:signal"], entity_rows=[{"account_id": request.account_id}]
        ).to_dict()
        value = result["signal"][0]
        if value is None:
            raise HTTPException(404, "No accepted online feature exists for this account")
        probability = float(model.predict_proba(pd.DataFrame({"signal": [float(value)]}))[0, 1])
        return {
            "account_id": request.account_id,
            "signal": float(value),
            "probability": probability,
            "model_version": card["model_version"],
        }

    return app


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        store, rows = feature_store(root)
        try:
            _, model, card = train_register_reload(root, rows)
            with TestClient(application(store, model, card)) as client:
                responses = [
                    client.post(
                        "/predict",
                        json={
                            "account_id": identity,
                            "feature_contract": card["feature_contract"],
                            "expected_model": card["model_version"],
                        },
                    )
                    for identity in [0, 20, 39]
                ]
            assert all(response.status_code == 200 for response in responses)
            predictions = [response.json() for response in responses]
            assert [row["signal"] for row in predictions] == [0.0, 0.25, 19.25]
            assert predictions[0]["probability"] < 0.5 < predictions[-1]["probability"]
            return {
                "model_card": card,
                "predictions": predictions,
                "historical_rows_preserved": 40,
                "future_known_correction_excluded": True,
                "actual_online_store": "local SQLite",
            }
        finally:
            store.teardown()


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        store, rows = feature_store(root)
        try:
            registry, model, card = train_register_reload(root, rows)
            baseline = {
                "account_id": 20,
                "feature_contract": card["feature_contract"],
                "expected_model": card["model_version"],
            }
            with TestClient(application(store, model, card)) as client:
                wrong_feature = client.post(
                    "/predict",
                    json={
                        **baseline,
                        "feature_contract": contract_digest({**CONTRACT, "unit": "kilograms"}),
                    },
                )
                wrong_model = client.post(
                    "/predict", json={**baseline, "expected_model": "unavailable"}
                )
                unknown = client.post("/predict", json={**baseline, "account_id": 999})
                valid = client.post("/predict", json=baseline)
            assert [
                wrong_feature.status_code,
                wrong_model.status_code,
                unknown.status_code,
                valid.status_code,
            ] == [409, 409, 404, 200]
            selected = registry.get_model_version_by_alias(MODEL_NAME, "accepted")
            assert str(selected.version) == card["model_version"]
            return {
                "rejected_feature_and_model_statuses": [409, 409],
                "unknown_entity_status": 404,
                "retained_registry_version": str(selected.version),
                "valid_request_status": 200,
                "persistent_network_service_requires_the_owned_project": True,
            }
        finally:
            store.teardown()


def main():
    from ds60sqlpy.plot_artifacts import publish_report, publish_table

    first, second = example_one(), example_two()
    print("Actual local feature/training/registry/inference workflow:", first)
    print("Contract rejection preserves the accepted model:", second)
    publish_table(
        ["account_id", "signal", "probability", "model_version"],
        [
            [row[key] for key in ["account_id", "signal", "probability", "model_version"]]
            for row in first["predictions"]
        ],
        description=(
            "Actual Feast SQLite online features feed the reloaded MLflow "
            "sklearn model through ASGI for three synthetic accounts."
        ),
    )
    publish_report(
        {"model_card": first["model_card"], "rejections": second},
        description=(
            "A real local MLflow model card and observed feature/model "
            "contract failures; no external service was deployed."
        ),
    )


if __name__ == "__main__":
    main()
