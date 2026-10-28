"Train actual local models from Feast historical features and record MLflow evidence."

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd
import polars as pl
from common import FEATURES, STATE, activate, probability
from feast import Entity, FeatureStore, FeatureView, Field, FileSource, ValueType
from feast.types import Float32, Int64, String
from mlflow.tracking import MlflowClient
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss
from sklearn.preprocessing import StandardScaler

os.environ.update(
    FEAST_USAGE="False",
    DO_NOT_TRACK="true",
    MLFLOW_DISABLE_AGENT_HINT="1",
    MLFLOW_ENABLE_TELEMETRY="false",
)


def main() -> None:
    owner = os.environ.get("DS60_WORKSHOP_OWNER", "")
    if not owner or len(owner) > 100:
        raise ValueError("Supply a bounded workshop ownership identifier")
    STATE.mkdir(parents=True, exist_ok=True)
    if any(STATE.iterdir()):
        raise ValueError(
            "Training requires a fresh owned state directory; existing state is retained"
        )
    (STATE / "owner.json").write_text(
        json.dumps({"owner": owner, "kind": "synthetic-local-ml-workshop"})
    )
    clock = datetime.now(UTC).replace(microsecond=0)
    base = pd.Timestamp(clock - timedelta(hours=240))
    rng = np.random.default_rng(17)
    n = 120
    usage = rng.uniform(1, 100, n)
    tickets = rng.poisson(2, n)
    region = np.where(np.arange(n) % 2 == 0, "north", "south")
    logits = 0.9 * tickets - 0.035 * usage + (region == "north") * 0.3
    labels = (rng.random(n) < 1 / (1 + np.exp(-logits))).astype(int)
    raw = pl.DataFrame(
        {
            "id": np.arange(n),
            "customer_id": np.arange(n) % 12,
            "usage": usage,
            "tickets": tickets,
            "region": region,
            "cutoff": np.arange(n) + 100,
            "label": labels,
        }
    )
    assert raw["id"].n_unique() == n
    data = raw.with_columns(
        (pl.col("cutoff") - 2).alias("available_at"),
        (pl.col("cutoff") + 4).alias("label_available_at"),
    ).to_pandas()
    repo = STATE / "feature_repo"
    repo.mkdir()
    source = data[["customer_id", "usage", "tickets", "region"]].copy()
    source["feature_time"] = base + pd.to_timedelta(data.available_at, unit="h")
    source["feature_epoch"] = [int(value.timestamp()) for value in source.feature_time]
    source.to_parquet(repo / "features.parquet", index=False)
    (repo / "feature_store.yaml").write_text(
        "project: classroom\nprovider: local\nregistry: "
        "registry.db\nonline_store:\n  type: sqlite\n  path: "
        "online.db\nentity_key_serialization_version: "
        "3\n"
    )
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
    requests = data[["id", "customer_id", "label", "label_available_at", "cutoff"]].copy()
    requests["event_timestamp"] = base + pd.to_timedelta(data.cutoff, unit="h")
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
    train = retrieved[retrieved.label_available_at <= 180].copy()
    test = retrieved[retrieved.cutoff >= 180].copy()
    assert len(train) == 77 and len(test) == 40 and int(test.label_available_at.max()) <= 240
    for frame in (train, test):
        frame["north"] = (frame.region == "north").astype(float)
    scaler = StandardScaler().fit(train[FEATURES])
    transformed = scaler.transform(train[FEATURES])
    heldout = scaler.transform(test[FEATURES])
    tracker = MlflowClient(tracking_uri="sqlite:///" + str(STATE / "tracking.db"))
    experiment = tracker.create_experiment(
        "local-support-prediction", artifact_location=(STATE / "artifacts").as_uri()
    )
    cards = {}
    for version, strength in (("v1", 1.0), ("v2", 0.5)):
        estimator = LogisticRegression(C=strength, max_iter=200, random_state=17).fit(
            transformed, train.label
        )
        score = float(brier_score_loss(test.label, estimator.predict_proba(heldout)[:, 1]))
        model = {
            "version": version,
            "features": FEATURES,
            "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist(),
            "coefficients": estimator.coef_[0].tolist(),
            "intercept": float(estimator.intercept_[0]),
            "approved_for_local_demo": score <= 0.30,
            "brier": score,
            "feature_schema": "customer-v1",
        }
        assert model["approved_for_local_demo"], "The declared synthetic validation gate failed"
        row = test.iloc[0].to_dict()
        assert (
            abs(probability(model, row) - float(estimator.predict_proba(heldout[[0]])[0, 1]))
            < 1e-12
        )
        directory = STATE / "models" / version
        directory.mkdir(parents=True)
        path = directory / "model.json"
        path.write_text(json.dumps(model, sort_keys=True, allow_nan=False))
        run = tracker.create_run(
            experiment, tags={"model_version": version, "feature_contract": "customer-v1"}
        )
        tracker.log_param(run.info.run_id, "regularization_C", strength)
        tracker.log_metric(run.info.run_id, "heldout_brier", score)
        tracker.log_artifact(run.info.run_id, str(path), "model")
        tracker.set_terminated(run.info.run_id)
        cards[version] = {
            "run_id": run.info.run_id,
            "brier": score,
            "accepted_for_synthetic_demo": True,
        }
    store.materialize(base.to_pydatetime(), clock)
    # Closing the training process checkpoints SQLite state before serving reads it.
    manifest = {
        "owner": owner,
        "training_clock": clock.isoformat(),
        "training_rows": len(train),
        "validation_rows": len(test),
        "feature_rows": len(retrieved),
        "feature_schema": "customer-v1",
        "maximum_feature_age_seconds": 48 * 3600,
        "models": cards,
        "claims": "Synthetic local workflow only; no external production deployment",
    }
    (STATE / "training.json").write_text(json.dumps(manifest, sort_keys=True))
    activate("v1")
    print(json.dumps({"trained": True, "models": cards, "historical_rows": len(retrieved)}))


if __name__ == "__main__":
    main()
