"""Real local MLflow runs, flavored models, registry aliases and acceptance gates."""

import hashlib
import importlib.metadata
import json
import os
import tempfile
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow import MlflowClient
from mlflow.models import infer_signature
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from ds60sqlpy.plot_artifacts import publish_report, publish_table

MODEL_NAME = "classroom-decision"


def setup(root):
    # This pad has no repository checkout; source provenance is recorded by the classroom receipt.
    os.environ["GIT_PYTHON_REFRESH"] = "quiet"
    uri = "sqlite:///" + str(root / "tracking.db")
    mlflow.set_tracking_uri(uri)
    mlflow.set_registry_uri(uri)
    client = MlflowClient(tracking_uri=uri, registry_uri=uri)
    experiment = client.create_experiment(
        "explicit-acceptance", artifact_location=(root / "artifacts").as_uri()
    )
    return client, experiment


def train_and_register(client, experiment, kind):
    train = pd.DataFrame({"signal": np.arange(20, dtype=float)})
    train_labels = (train.signal >= 12).astype(int)
    validation = pd.DataFrame({"signal": np.arange(0.25, 20, 0.5)})
    validation_labels = (validation.signal >= 12).astype(int)
    estimator = (
        LogisticRegression(C=1000, random_state=39)
        if kind == "linear"
        else DummyClassifier(strategy="most_frequent")
    )
    model = make_pipeline(StandardScaler(), estimator).fit(train, train_labels)
    predictions = model.predict(validation)
    accuracy = float(accuracy_score(validation_labels, predictions))
    evaluation = {"signal": validation.signal.tolist(), "labels": validation_labels.tolist()}
    evaluation_sha = hashlib.sha256(json.dumps(evaluation, sort_keys=True).encode()).hexdigest()
    requirements = [
        f"{name}=={importlib.metadata.version(name)}"
        for name in ("scikit-learn", "numpy", "pandas", "cloudpickle")
    ]
    created_run = client.create_run(experiment)
    with mlflow.start_run(run_id=created_run.info.run_id) as run:
        mlflow.log_params(
            {
                "candidate_kind": kind,
                "feature_unit": "dimensionless",
                "validation_rows": len(validation),
            }
        )
        mlflow.log_metric("validation_accuracy", accuracy)
        mlflow.set_tag("evaluation_sha256", evaluation_sha)
        info = mlflow.sklearn.log_model(
            sk_model=model,
            name="candidate",
            input_example=train.iloc[:2],
            signature=infer_signature(train, model.predict(train)),
            pip_requirements=requirements,
        )
        version = mlflow.register_model(info.model_uri, MODEL_NAME, await_registration_for=10)
        run_id = run.info.run_id
    stored_run = client.get_run(run_id)
    stored_version = client.get_model_version(MODEL_NAME, str(version.version))
    assert stored_run.data.params["candidate_kind"] == kind
    assert stored_run.data.metrics["validation_accuracy"] == accuracy
    assert stored_version.run_id == run_id
    return {
        "kind": kind,
        "run_id": run_id,
        "model_id": info.model_id,
        "version": str(version.version),
        "validation_accuracy": accuracy,
        "validation_rows": len(validation),
        "evaluation_sha256": evaluation_sha,
        "accepted": accuracy >= 0.9,
        "model_has_real_sklearn_flavor": True,
    }


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        client, experiment = setup(Path(directory))
        candidate = train_and_register(client, experiment, "linear")
        assert candidate["accepted"]
        client.set_registered_model_alias(MODEL_NAME, "champion", candidate["version"])
        selected = client.get_model_version_by_alias(MODEL_NAME, "champion")
        assert (
            str(selected.version) == candidate["version"] and selected.run_id == candidate["run_id"]
        )
        return {
            "candidate": candidate,
            "alias_version": str(selected.version),
            "alias_change_was_explicit": True,
            "serving_process_started": False,
        }


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        client, experiment = setup(Path(directory))
        original = train_and_register(client, experiment, "linear")
        client.set_registered_model_alias(MODEL_NAME, "champion", original["version"])
        challenger = train_and_register(client, experiment, "majority")
        assert not challenger["accepted"] and challenger["version"] != original["version"]
        if challenger["accepted"]:
            client.set_registered_model_alias(MODEL_NAME, "champion", challenger["version"])
        selected = client.get_model_version_by_alias(MODEL_NAME, "champion")
        assert str(selected.version) == original["version"]
        assert challenger["evaluation_sha256"] == original["evaluation_sha256"]
        assert (
            client.get_model_version(MODEL_NAME, challenger["version"]).run_id
            == challenger["run_id"]
        )
        return {
            "original": original,
            "registered_challenger": challenger,
            "retained_champion_version": str(selected.version),
            "registration_succeeded_while_acceptance_failed": True,
        }


def main():
    first, second = example_one(), example_two()
    candidates = [second["original"], second["registered_challenger"]]
    publish_table(
        ["candidate", "registry version", "validation accuracy", "accepted"],
        [
            [row["kind"], row["version"], row["validation_accuracy"], row["accepted"]]
            for row in candidates
        ],
        description="Registered model versions evaluated on the same population",
    )
    publish_report(
        {"case_one": first, "case_two": second},
        description="MLflow run-to-version lineage and explicit alias acceptance",
    )
    print(json.dumps({"case_one": first, "case_two": second}, allow_nan=False))
    print("dme-039: two MLflow registry cases passed")


if __name__ == "__main__":
    main()
