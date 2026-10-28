# mle-010: explained reference

Use real tracking APIs to bind parameters, metrics, artifacts and terminal outcomes to an owned run.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Bind source identity

Retain a stable source identity and the actual submitted configuration. Do not attach a result from another revision without explaining the difference.

**Expected:** It identifies the implementation used.

## 2. Distinguish metadata and artifacts

The local example places both under owned paths, but deployed stores may use separate systems. Verify both when designing retention and recovery.

**Expected:** The answer separates backend metadata from artifact bytes.

## 3. Record a failure honestly

Retain the reason and subsequent decision. A failed run should not be relabeled successful merely to simplify a dashboard.

**Expected:** The useful observations remain available.

## 4. Inspect artifact content

Validate the file and its identity. Tracking provides lineage plumbing; it does not determine whether the contract is correct.

**Expected:** It matches the intended model interface.

## 5. Avoid ambient routing

Keep ownership and destination explicit in automation. A real shared tracking service needs separately approved credentials and access controls.

**Expected:** It cannot silently select an external workspace.

## 6. Plan reproducibility

Record the relevant versions and selection process. Deterministic fixtures support debugging, but not every training system promises bitwise identity.

**Expected:** It includes data, code, dependencies, randomness and procedure.

## Complete reference

```python
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
```

## Interpretation

Use real tracking APIs to bind parameters, metrics, artifacts and terminal outcomes to an owned run. Verify readback and maintain explicit local routing. The artifact and registry lesson adds the consumer contract needed for serving.
