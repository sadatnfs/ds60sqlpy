"""mle-002: local, bounded ML engineering investigation."""

import numpy as np
import pandas as pd


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
    records = [
        {"id": 1, "event_at": 2, "known_at": 3, "value": 10},
        {"id": 2, "event_at": 4, "known_at": 7, "value": 999},
        {"id": 3, "event_at": 8, "known_at": 8, "value": 30},
    ]

    def select(cutoff):
        valid = [r for r in records if r["event_at"] <= cutoff and r["known_at"] <= cutoff]
        return max(valid, key=lambda r: (r["event_at"], r["known_at"]))["value"]

    assert [select(5), select(9)] == [10, 30]
    assert (
        max([r for r in records if r["event_at"] <= 5], key=lambda r: r["event_at"])["value"] == 999
    )
    return {"eligible": [10, 30], "event_only_leak": 999}


def example_two():
    frame = dataset()
    training_cutoff = 180
    mature = frame[(frame.cutoff < training_cutoff) & (frame.label_available_at <= training_cutoff)]
    premature = frame[frame.cutoff < training_cutoff]
    assert len(mature) == 77 and len(premature) == 80
    assert set(premature.id) - set(mature.id) == {77, 78, 79}
    return {"mature_training_rows": 77, "not_yet_known_labels": [77, 78, 79]}


def main():
    print(example_one())
    print(example_two())
    print("mle-002 reference checks passed")


if __name__ == "__main__":
    main()
