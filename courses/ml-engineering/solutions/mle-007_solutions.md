# mle-007: explained reference

Populate a real online feature store and enforce a consumer freshness contract.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change the decision clock

State whether the maximum is inclusive. Keep the boundary test with the policy so future changes are visible.

**Expected:** The first value reaches the boundary and the second remains stale.

## 2. Reject future metadata

A negative age is not evidence of very fresh data. Investigate clock skew or an incorrect timestamp definition.

**Expected:** The age check rejects it.

## 3. Separate publication and observation

Keep the timestamp that the policy actually measures. Changing only publication metadata can hide stale information.

**Expected:** The answer retains the measurement/availability clock.

## 4. Handle missing entities

Use a declared fallback, abstention or failure. Record coverage and avoid comparing scores from different missingness policies without explanation.

**Expected:** Missing inputs do not silently become observed zeros.

## 5. Inspect materialization scope

Use owned state and known fixtures before applying a materialization command to a durable environment. Do not infer completeness from the command name.

**Expected:** The selected versions are explained.

## 6. Test serving separately

Bind the feature contract to the model, validate inputs and test the actual serving interface. The next lessons build those boundaries.

**Expected:** They include schema, transformation and model-version consistency.

## Complete reference

```python
"""mle-007: local, bounded ML engineering investigation."""

import os
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd


def configure_local_tools():
    os.environ.update(
        FEAST_USAGE="False",
        DO_NOT_TRACK="true",
        MLFLOW_ENABLE_TELEMETRY="false",
        MLFLOW_DISABLE_AGENT_HINT="1",
        DBT_SEND_ANONYMOUS_USAGE_STATS="false",
    )


def make_store(directory):
    configure_local_tools()
    from feast import Entity, FeatureStore, FeatureView, Field, FileSource, ValueType
    from feast.types import Float32, Int64

    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    (root / "feature_store.yaml").write_text(
        "project: classroom\nprovider: local\nregistry: "
        "registry.db\nonline_store:\n  type: sqlite\n  path: "
        "online.db\nentity_key_serialization_version: "
        "3\n"
    )
    stamps = pd.to_datetime(["2024-01-01", "2024-01-03", "2024-01-01"], utc=True)
    data = pd.DataFrame(
        {
            "customer_id": [1, 1, 2],
            "feature_time": stamps,
            "usage": [10.0, 20.0, 5.0],
            "tickets": [1, 2, 3],
            "feature_epoch": [int(t.timestamp()) for t in stamps],
        }
    )
    data.to_parquet(root / "features.parquet", index=False)
    customer = Entity(name="customer", join_keys=["customer_id"], value_type=ValueType.INT64)
    view = FeatureView(
        name="customer_features",
        entities=[customer],
        ttl=timedelta(days=30),
        schema=[
            Field(name="usage", dtype=Float32),
            Field(name="tickets", dtype=Int64),
            Field(name="feature_epoch", dtype=Int64),
        ],
        source=FileSource(path=str(root / "features.parquet"), timestamp_field="feature_time"),
    )
    store = FeatureStore(repo_path=str(root))
    store.apply([customer, view])
    return store


def online_case(directory):
    store = make_store(directory)
    store.materialize(datetime(2023, 12, 31, tzinfo=UTC), datetime(2024, 1, 4, tzinfo=UTC))
    data = store.get_online_features(
        features=["customer_features:usage", "customer_features:feature_epoch"],
        entity_rows=[{"customer_id": 1}, {"customer_id": 2}],
    ).to_dict()
    return store, data


def example_one():
    with tempfile.TemporaryDirectory() as d:
        store, data = online_case(Path(d) / "features")
        try:
            assert data["usage"] == [20.0, 5.0]
            assert (Path(d) / "features/online.db").exists()
            return {"online_usage": data["usage"], "real_sqlite_materialization": True}
        finally:
            store.teardown()


def example_two():
    with tempfile.TemporaryDirectory() as d:
        store, data = online_case(Path(d) / "features")
        try:
            decision = int(datetime(2024, 1, 4, tzinfo=UTC).timestamp())
            max_age = 2 * 86400
            ages = [decision - int(value) for value in data["feature_epoch"]]
            accepted = [0 <= age <= max_age for age in ages]
            assert ages == [86400, 259200] and accepted == [True, False]
            return {
                "ages_seconds": ages,
                "freshness_decisions": accepted,
                "retrieval_does_not_replace_consumer_freshness_policy": True,
            }
        finally:
            store.teardown()


def main():
    print(example_one())
    print(example_two())
    print("mle-007 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Populate a real online feature store and enforce a consumer freshness contract. Test missing, stale, future and boundary values, then connect only accepted features to the model interface. Preserve the declared clock when moving from a fixed fixture to a running service.
