# mle-006: explained reference

Qualify a real feature-store retrieval against independent temporal and coverage checks.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Inspect registered schema

Check names, types, timestamp field and TTL. A registered view does not prove that its source history is scientifically valid.

**Expected:** They match the declared local contract.

## 2. Move a request cutoff

Verify the precise boundary and preserve the request identifier. Different request times can legitimately retrieve different versions.

**Expected:** The selected value changes from 10 to 20.

## 3. Test no history

Validate unique request keys and left-join retrieval back onto the original requests. Report missingness and coverage before training or scoring.

**Expected:** It remains in the authoritative request population.

## 4. Test expiration

Retain the request and an explicit unavailable status. A different TTL is a contract change that needs justification.

**Expected:** Its selected feature is unavailable under the policy.

## 5. Review late availability

Use appropriately versioned feature snapshots or an explicit availability policy, and test a late-known fixture independently. Do not assume created-time metadata automatically enforces every bitemporal rule.

**Expected:** The answer identifies known-time history.

## 6. Separate local and deployed capability

A deployed store needs its own access, ownership, scaling and operational qualification. Preserve these local values as mechanism evidence only.

**Expected:** It runs a local Feast registry and retrieval, without a cloud service.

## Complete reference

```python
"""mle-006: local, bounded ML engineering investigation."""

import os
import tempfile
from datetime import timedelta
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


def historical(store):
    requests = pd.DataFrame(
        {
            "request_id": [1, 2, 3],
            "customer_id": [1, 1, 2],
            "event_timestamp": pd.to_datetime(["2024-01-02", "2024-01-04", "2024-01-02"], utc=True),
        }
    )
    return (
        store.get_historical_features(
            entity_df=requests, features=["customer_features:usage", "customer_features:tickets"]
        )
        .to_df()
        .sort_values("request_id")
    )


def example_one():
    with tempfile.TemporaryDirectory() as d:
        store = make_store(Path(d) / "features")
        try:
            result = historical(store)
            assert result.usage.tolist() == [10.0, 20.0, 5.0]
            assert result.request_id.tolist() == [1, 2, 3]
            assert len(store.list_feature_views()) == 1
            return {"historical_usage": result.usage.tolist(), "registered_feature_views": 1}
        finally:
            store.teardown()


def example_two():
    with tempfile.TemporaryDirectory() as d:
        store = make_store(Path(d) / "features")
        try:
            requests = pd.DataFrame(
                {
                    "request_id": [1, 2, 3],
                    "customer_id": [1, 1, 1],
                    "event_timestamp": pd.to_datetime(
                        ["2024-01-02", "2023-12-01", "2024-03-01"], utc=True
                    ),
                }
            )
            retrieved = store.get_historical_features(
                entity_df=requests, features=["customer_features:usage"]
            ).to_df()
            assert retrieved.request_id.is_unique
            assert set(retrieved.request_id) <= set(requests.request_id)
            # Restore the authoritative request population, including unmatched/expired rows.
            result = requests.merge(
                retrieved[["request_id", "usage"]], on="request_id", how="left", validate="1:1"
            ).sort_values("request_id")
            assert len(result) == len(requests) == 3
            assert result.usage.iloc[0] == 10.0 and result.usage.iloc[1:].isna().all()
            return {
                "requested_rows": 3,
                "retrieval_returned_rows": len(retrieved),
                "normalized_rows": 3,
                "nulls_for_unknown_or_expired": int(result.usage.isna().sum()),
                "before_history_or_outside_ttl_missing": True,
            }
        finally:
            store.teardown()


def main():
    print(example_one())
    print(example_two())
    print("mle-006 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Qualify a real feature-store retrieval against independent temporal and coverage checks. Preserve every requested decision, retain unavailable values explicitly and distinguish local API execution from external production guarantees.
