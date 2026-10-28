"""mle-010: local, bounded ML engineering investigation."""

import hashlib
import json
import os
import tempfile
from pathlib import Path


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
    with tempfile.TemporaryDirectory() as d:
        client, experiment = tracker(Path(d) / "tracking")
        run = client.create_run(
            experiment, tags={"data_contract": "customer-v1", "source": "synthetic"}
        )
        run_id = run.info.run_id
        client.log_param(run_id, "threshold", "0.5")
        client.log_metric(run_id, "brier", 0.2)
        manifest = {
            "feature_order": ["usage", "tickets", "region"],
            "data_sha256": digest([1, 2, 3]),
        }
        path = Path(d) / "manifest.json"
        path.write_text(json.dumps(manifest))
        client.log_artifact(run_id, str(path), "evidence")
        client.set_terminated(run_id)
        loaded = client.get_run(run_id)
        assert loaded.info.status == "FINISHED" and loaded.data.metrics["brier"] == 0.2
        assert client.list_artifacts(run_id, "evidence")[0].path == "evidence/manifest.json"
        return {
            "status": loaded.info.status,
            "metrics": loaded.data.metrics,
            "artifact_recorded": True,
        }


def example_two():
    with tempfile.TemporaryDirectory() as d:
        client, experiment = tracker(Path(d) / "tracking")
        run = client.create_run(experiment)
        client.log_metric(run.info.run_id, "training_loss", 0.1)
        client.set_terminated(run.info.run_id, status="FAILED")
        loaded = client.get_run(run.info.run_id)
        assert loaded.info.status == "FAILED" and loaded.data.metrics["training_loss"] == 0.1
        return {
            "failed_run_retains_observations": True,
            "successful_metric_is_not_successful_workflow": True,
        }


def main():
    print(example_one())
    print(example_two())
    print("mle-010 reference checks passed")


if __name__ == "__main__":
    main()
