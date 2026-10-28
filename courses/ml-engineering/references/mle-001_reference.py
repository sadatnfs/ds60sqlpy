"""mle-001: local, bounded ML engineering investigation."""

import hashlib
import json

import numpy as np
import pandas as pd


def digest(data):
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


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


def example_one():
    contract = {
        "unit": "one customer decision",
        "prediction_time": "cutoff",
        "feature_columns": ["usage", "tickets", "region"],
        "label": "label",
        "label_horizon_hours": 4,
        "decision": "offer optional support",
        "owner": "learning team",
    }
    frame = dataset()
    assert frame["id"].is_unique and all(
        name in frame.columns for name in contract["feature_columns"]
    )
    assert "label" not in contract["feature_columns"]
    assert (frame["label_available_at"] > frame["cutoff"]).all()
    return {"contract": contract, "records": len(frame), "contract_hash": digest(contract)}


def example_two():
    dependencies = {
        "validate": set(),
        "features": {"validate"},
        "train": {"features"},
        "evaluate": {"train"},
        "publish": {"evaluate"},
    }
    completed = {"validate", "features", "train"}
    ready = sorted(
        name
        for name, parents in dependencies.items()
        if name not in completed and parents <= completed
    )
    assert ready == ["evaluate"] and "publish" not in ready
    return {"ready": ready, "publication_requires_evaluation": True}


def main():
    print(example_one())
    print(example_two())
    print("mle-001 reference checks passed")


if __name__ == "__main__":
    main()
