"""mle-010: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Add a source revision or digest tag to a run.
# TODO 2: Explain where a metric and a model file are stored conceptually.
# TODO 3: Keep a failed status after a downstream step rejects the candidate.
# TODO 4: Read the manifest and check its declared feature order.
# TODO 5: Explain why the example sets local URIs explicitly.
# TODO 6: List what else is needed to reproduce a trained model.
