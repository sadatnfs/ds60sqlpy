"""mle-011: worked starting point; complete the guide's six changes."""

import hashlib
import os
import tempfile
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
    frame = dataset()
    train = frame[frame.label_available_at <= 180]
    model = fit_pipeline(train)
    import joblib

    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "trusted-model.joblib"
        joblib.dump(model, path)
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        contract = {
            "features": ["usage", "tickets", "region"],
            "schema_version": 1,
            "artifact_sha256": expected,
        }
        assert hashlib.sha256(path.read_bytes()).hexdigest() == contract["artifact_sha256"]
        restored = joblib.load(path)
        sample = frame.iloc[[90]][contract["features"]]
        assert np.allclose(restored.predict_proba(sample), model.predict_proba(sample))
        client, experiment = tracker(Path(d) / "tracking")
        run = client.create_run(experiment)
        client.log_artifact(run.info.run_id, str(path), "model")
        client.create_registered_model("customer-model")
        version = client.create_model_version(
            "customer-model",
            source=f"runs:/{run.info.run_id}/model/{path.name}",
            run_id=run.info.run_id,
        )
        client.set_registered_model_alias("customer-model", "candidate", version.version)
        registered = client.get_model_version_by_alias("customer-model", "candidate")
        assert registered.version == version.version and registered.run_id == run.info.run_id
        client.set_terminated(run.info.run_id)
        return {
            "own_trusted_artifact_round_trip": True,
            "contract": contract,
            "registry_version": registered.version,
            "registry_linked_run": True,
        }


if __name__ == "__main__":
    print(example_one())

# TODO 1: Keep the input field sequence with the artifact.
# TODO 2: Modify the saved model after recording its hash.
# TODO 3: Explain why a matching attacker-supplied hash is insufficient.
# TODO 4: Read the version behind the candidate alias.
# TODO 5: Convert usage hours to minutes without adapting the model.
# TODO 6: List checks needed before moving an accepted serving alias.
