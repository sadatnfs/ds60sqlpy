"""Owned control-plane actions; never expose these as public HTTP endpoints."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime

from common import STATE, activate, ownership

os.environ.update(FEAST_USAGE="False", DO_NOT_TRACK="true")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["activate", "inject-stale", "restore-features"])
    parser.add_argument("--version", choices=["v1", "v2"])
    args = parser.parse_args()
    ownership()
    if args.operation == "activate":
        if args.version is None:
            parser.error("activate requires --version")
        print(json.dumps(activate(args.version)))
        return
    import pandas as pd
    from feast import FeatureStore

    store = FeatureStore(repo_path=str(STATE / "feature_repo"))
    if args.operation == "inject-stale":
        frame = pd.DataFrame(
            {
                "customer_id": [1],
                "feature_time": [datetime.now(UTC)],
                "usage": [20.0],
                "tickets": [2],
                "region": ["south"],
                "feature_epoch": [1],
            }
        )
        store.write_to_online_store(feature_view_name="customer_features", df=frame)
    else:
        data = (
            pd.read_parquet(STATE / "feature_repo/features.parquet")
            .sort_values("feature_time")
            .groupby("customer_id", as_index=False)
            .tail(1)
        )
        # A new publication timestamp is separate from the retained feature-age value.
        data["feature_time"] = pd.Timestamp.now(tz="UTC")
        store.write_to_online_store(feature_view_name="customer_features", df=data)
    print(json.dumps({"operation": args.operation, "owner_verified": True}))


if __name__ == "__main__":
    main()
