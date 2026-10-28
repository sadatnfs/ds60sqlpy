"""Actual Feast retrieval versus an independent two-clock availability oracle."""

import json
import tempfile
from datetime import timedelta
from pathlib import Path

import pandas as pd
from feast import Entity, FeatureStore, FeatureView, Field, FileSource, ValueType
from feast.types import Float32

from ds60sqlpy.plot_artifacts import publish_report, publish_table


def fixtures():
    features = pd.DataFrame(
        {
            "account_id": [1, 1, 1, 2, 3],
            "feature_time": pd.to_datetime(
                ["2026-01-01", "2026-01-01", "2026-01-03", "2026-01-01", "2026-01-01"], utc=True
            ),
            "known_at": pd.to_datetime(
                [
                    "2026-01-01T01:00Z",
                    "2026-01-04T00:00Z",
                    "2026-01-03T01:00Z",
                    None,
                    "2026-01-01T00:00Z",
                ],
                utc=True,
            ),
            "value": [10.0, 99.0, 20.0, 5.0, 3.5],
        }
    )
    requests = pd.DataFrame(
        {
            "request_id": list(range(1, 10)),
            "account_id": [1, 1, 99, 1, 1, 2, 1, 3, 3],
            "event_timestamp": pd.to_datetime(
                [
                    "2026-01-02",
                    "2026-01-04",
                    "2026-01-02",
                    "2025-12-01",
                    "2026-03-01",
                    "2026-01-02",
                    "2026-01-01",
                    "2026-01-08T00:00:00Z",
                    "2026-01-08T00:00:00.000001Z",
                ],
                utc=True,
                format="ISO8601",
            ),
        }
    )
    return features, requests


def oracle(features, requests):
    # Use plain aware datetime and an explicit scan, independently of the
    # store's dataframe join, deduplication and backend filtering code.
    answer = []
    for request in requests.itertuples(index=False):
        moment = request.event_timestamp.to_pydatetime()
        candidates = []
        for feature in features.itertuples(index=False):
            if feature.account_id != request.account_id or pd.isna(feature.known_at):
                continue
            event = feature.feature_time.to_pydatetime()
            known = feature.known_at.to_pydatetime()
            if moment - timedelta(days=7) <= event <= moment and known <= moment:
                candidates.append((event, known, float(feature.value)))
        answer.append(None if not candidates else max(candidates)[2])
    return answer


def make_store(directory, features):
    directory.mkdir()
    (directory / "feature_store.yaml").write_text(
        "project: ml_lifecycle\nprovider: local\nregistry: registry.db\n"
        "online_store:\n  type: sqlite\n  path: online.db\n"
        "entity_key_serialization_version: 3\n"
    )
    path = directory / "features.parquet"
    features.to_parquet(path, index=False)
    account = Entity(name="account", join_keys=["account_id"], value_type=ValueType.INT64)
    view = FeatureView(
        name="account_values",
        entities=[account],
        ttl=timedelta(days=7),
        schema=[Field(name="value", dtype=Float32)],
        source=FileSource(
            path=str(path), timestamp_field="feature_time", created_timestamp_column="known_at"
        ),
    )
    store = FeatureStore(repo_path=str(directory))
    store.apply([account, view])
    return store


def retrieve(store, requests, enforce_known_time):
    retrieved = store.get_historical_features(
        entity_df=requests,
        features=["account_values:value"],
        filter_by_created_timestamp=enforce_known_time,
    ).to_df()
    assert retrieved.request_id.is_unique
    assert set(retrieved.request_id) <= set(requests.request_id)
    restored = requests.merge(
        retrieved[["request_id", "value"]], on="request_id", how="left", validate="1:1"
    ).sort_values("request_id")
    assert len(restored) == len(requests)
    return [None if pd.isna(value) else float(value) for value in restored.value]


def example_one():
    features, requests = fixtures()
    requests = requests.iloc[:2].copy()
    with tempfile.TemporaryDirectory() as temporary:
        store = make_store(Path(temporary) / "store", features)
        try:
            default = retrieve(store, requests, False)
            available = retrieve(store, requests, True)
        finally:
            store.teardown()
    expected = oracle(features, requests)
    assert default == [99.0, 20.0]
    assert available == expected == [10.0, 20.0]
    return {
        "default_event_time_only": default,
        "known_time_cutoff": available,
        "independent_oracle": expected,
        "future_correction_detected": default[0] != expected[0],
    }


def example_two():
    features, requests = fixtures()
    with tempfile.TemporaryDirectory() as temporary:
        store = make_store(Path(temporary) / "store", features)
        try:
            values = retrieve(store, requests, True)
        finally:
            store.teardown()
    assert (
        values
        == oracle(features, requests)
        == [10.0, 20.0, None, None, None, None, None, 3.5, None]
    )
    return {
        "request_ids": requests.request_id.tolist(),
        "values": values,
        "requested_rows": 9,
        "retained_rows": len(values),
        "missing_values": values.count(None),
        "null_known_time_was_not_assumed_available": values[5] is None,
    }


def main():
    first, second = example_one(), example_two()
    publish_table(
        ["request_id", "available value"],
        [
            [identity, value]
            for identity, value in zip(second["request_ids"], second["values"], strict=True)
        ],
        description="Authoritative requests retained in actual Feast known-time retrieval",
    )
    publish_report(
        {"case_one": first, "case_two": second},
        description="Actual Feast default and availability cutoff with an independent oracle",
    )
    print(json.dumps({"case_one": first, "case_two": second}, allow_nan=False))
    print("dme-034: two point-in-time cases passed")


if __name__ == "__main__":
    main()
