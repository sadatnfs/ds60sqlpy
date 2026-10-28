# mle-018: explained reference

Deliver a connected local ML product with actual tool execution and a reviewable acceptance decision.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Trace the training features

Compare them with the independent prepared source and verify complete request coverage. A separate successful store demo would not prove this connection.

**Expected:** They came through the registered Feast historical retrieval.

## 2. Review label maturity

Preserve the cutoff and included identities. Do not select training rows merely because their prediction times are earlier.

**Expected:** The training cutoff excludes labels not yet known.

## 3. Inspect the saved report

Verify actual readback and distinguish package execution, numerical assertions, evaluation interpretation and deployment qualification.

**Expected:** Each claim has a defined local scope.

## 4. Run the real local service

The project has explicit training, serving and control roles. Its checker proves declared local lifecycle behavior and cleans only its owned resources.

**Expected:** The loopback HTTP endpoint predicts from durable owned state.

## 5. Exercise rollback and stale inputs

Retain accepted artifacts, preserve true feature age and record the operational decision. Monitoring and publication are part of the product.

**Expected:** Versioned predictions and diagnostics follow the contract.

## 6. Write the final acceptance argument

Cite the data/interface contracts, actual tool results, diagnostics, persistent state and rollback checks. Identify additional scale, security, population and governance qualification required for a real use.

**Expected:** It separates local evidence from broader deployment claims.

## Complete reference

```python
"""mle-018: local, bounded ML engineering investigation."""

import hashlib
import json
import os
import tempfile
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd


def configure_local_tools():
    os.environ.update(
        FEAST_USAGE="False",
        DO_NOT_TRACK="true",
        MLFLOW_ENABLE_TELEMETRY="false",
        MLFLOW_DISABLE_AGENT_HINT="1",
        DBT_SEND_ANONYMOUS_USAGE_STATS="false",
    )


def digest(data):
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


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


def tracker(directory):
    configure_local_tools()
    from mlflow.tracking import MlflowClient

    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    client = MlflowClient(
        tracking_uri="sqlite:///" + str(root / "tracking.db"),
        registry_uri="sqlite:///" + str(root / "tracking.db"),
    )
    experiment = client.create_experiment(
        "local-quality-investigation", artifact_location=(root / "artifacts").as_uri()
    )
    return client, experiment


def example_one():
    configure_local_tools()
    import polars as pl
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from feast import Entity, FeatureStore, FeatureView, Field, FileSource, ValueType
    from feast.types import Float32, Int64, String
    from sklearn.metrics import brier_score_loss

    from ds60sqlpy.plot_artifacts import publish_report

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        raw = dataset()
        data = (
            pl.from_pandas(raw)
            .filter(pl.col("available_at") <= pl.col("cutoff"))
            .sort("id")
            .to_pandas()
        )
        epoch = pd.Timestamp("2024-01-01", tz="UTC")
        feature_rows = data[["customer_id", "usage", "tickets", "region"]].copy()
        feature_rows["feature_time"] = epoch + pd.to_timedelta(data.available_at, unit="h")
        feature_rows["feature_epoch"] = [
            int(value.timestamp()) for value in feature_rows.feature_time
        ]
        repo = root / "feature_store"
        repo.mkdir()
        (repo / "feature_store.yaml").write_text(
            "project: classroom\nprovider: local\nregistry: "
            "registry.db\nonline_store:\n  type: sqlite\n  path: "
            "online.db\nentity_key_serialization_version: "
            "3\n"
        )
        feature_rows.to_parquet(repo / "features.parquet", index=False)
        entity = Entity(name="customer", join_keys=["customer_id"], value_type=ValueType.INT64)
        view = FeatureView(
            name="customer_features",
            entities=[entity],
            ttl=timedelta(days=30),
            schema=[
                Field(name="usage", dtype=Float32),
                Field(name="tickets", dtype=Int64),
                Field(name="region", dtype=String),
                Field(name="feature_epoch", dtype=Int64),
            ],
            source=FileSource(path=str(repo / "features.parquet"), timestamp_field="feature_time"),
        )
        store = FeatureStore(repo_path=str(repo))
        store.apply([entity, view])
        try:
            requests = data[["id", "customer_id", "label", "label_available_at", "cutoff"]].copy()
            requests["event_timestamp"] = epoch + pd.to_timedelta(data.cutoff, unit="h")
            retrieved = (
                store.get_historical_features(
                    entity_df=requests,
                    features=[
                        "customer_features:usage",
                        "customer_features:tickets",
                        "customer_features:region",
                    ],
                )
                .to_df()
                .sort_values("id")
            )
            assert retrieved.id.tolist() == data.id.tolist()
            assert np.allclose(retrieved.usage, data.usage, atol=1e-5)
            train = retrieved[retrieved.label_available_at <= 180]
            test = retrieved[retrieved.cutoff >= 180]
            model = fit_pipeline(train)
            probabilities = model.predict_proba(test[["usage", "tickets", "region"]])[:, 1]
            metric = float(brier_score_loss(test.label, probabilities))
            assert len(train) == 77 and len(test) == 40 and 0 <= metric <= 1
            end = (epoch + pd.Timedelta(hours=220)).to_pydatetime()
            store.materialize(epoch.to_pydatetime(), end)
            online = store.get_online_features(
                features=[
                    "customer_features:usage",
                    "customer_features:tickets",
                    "customer_features:region",
                    "customer_features:feature_epoch",
                ],
                entity_rows=[{"customer_id": 1}],
            ).to_dict()
            age = int(end.timestamp()) - int(online["feature_epoch"][0])
            assert 0 <= age <= 24 * 3600
            request = {name: online[name][0] for name in ("usage", "tickets", "region")}
            client, experiment = tracker(root / "tracking")
            run = client.create_run(experiment, tags={"feature_contract": "customer-v1"})
            client.log_metric(run.info.run_id, "brier", metric)
            client.log_param(run.info.run_id, "data_sha256", digest(data.id.tolist()))
            app = FastAPI()

            @app.post("/predict")
            def predict(payload: dict):
                return {
                    "probability": float(model.predict_proba(pd.DataFrame([payload]))[0, 1]),
                    "version": "v1",
                }

            with TestClient(app) as service:
                response = service.post("/predict", json=request)
                assert response.status_code == 200
                score = response.json()["probability"]
                assert (
                    abs(score - float(model.predict_proba(pd.DataFrame([request]))[0, 1])) < 1e-12
                )
            card = {
                "training_rows": len(train),
                "validation_rows": len(test),
                "historical_retrieval_rows": len(retrieved),
                "label_cutoff": 180,
                "brier": metric,
                "feature_contract": "customer-v1",
                "feature_age_hours": age / 3600,
                "feature_store": "actual local file + SQLite",
                "serving_evidence": "actual in-process ASGI request",
                "probability": score,
                "data_sha256": digest(data.id.tolist()),
                "deployment": "not deployed to an external service",
            }
            path = root / "model-card.json"
            path.write_text(json.dumps(card, sort_keys=True))
            client.log_artifact(run.info.run_id, str(path))
            client.set_terminated(run.info.run_id)
            assert client.get_run(run.info.run_id).data.metrics["brier"] == metric
            publish_report(
                card, description="Connected local data, features, model and serving evidence"
            )
            return card
        finally:
            store.teardown()


def example_two():
    from ds60sqlpy.plot_artifacts import publish_report

    candidate = {
        "schema_ok": True,
        "mature_label_coverage": 0.1,
        "required_coverage": 0.8,
        "artifact_hash_ok": True,
    }
    accepted = bool(
        candidate["schema_ok"]
        and candidate["artifact_hash_ok"]
        and candidate["mature_label_coverage"] >= candidate["required_coverage"]
    )
    assert not accepted
    decision = {
        "accepted": accepted,
        "reason": "insufficient mature-label coverage",
        "active_version_retained": "v1",
        "candidate": candidate,
    }
    publish_report(
        decision, description="Blocked publication decision with retained accepted version"
    )
    return decision


def main():
    print(example_one())
    print(example_two())
    print("mle-018 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Deliver a connected local ML product with actual tool execution and a reviewable acceptance decision. Use the owned service project to test persistent HTTP operation and recovery, then specify the additional evidence needed before adapting the design to a real organization and population.
