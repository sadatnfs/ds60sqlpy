"""mle-007: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Move the declared decision time forward by one day.
# TODO 2: Give a feature timestamp after the decision time.
# TODO 3: Explain why republishing an old value should not automatically reset its data age.
# TODO 4: Request an entity absent from the store and define the response.
# TODO 5: Limit the source interval and verify retrieved state.
# TODO 6: Explain which checks are still needed beyond SDK retrieval.
