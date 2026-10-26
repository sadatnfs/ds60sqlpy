"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
import pandas as pd


def seasonal_design(t):
    t = np.asarray(t)
    return np.column_stack(
        [np.ones(len(t)), t, np.sin(2 * np.pi * t / 12), np.cos(2 * np.pi * t / 12)]
    )


def case_03():
    rng = np.random.default_rng(2703)
    t = np.arange(60)
    series = np.array(
        [
            10
            + level
            + trend * t
            + 3 * np.sin(2 * np.pi * t / 12)
            + rng.normal(scale=0.4, size=len(t))
            for level, trend in ((0, 0.1), (4, 0.2), (-2, 0.05))
        ]
    )
    baseline_losses, model_losses = [], []
    for origin in range(24, 55, 6):
        train = np.arange(origin - 1)  # Label at t becomes available at t+2.
        future = np.arange(origin, origin + 3)
        assert np.max(train + 2) <= origin
        for values in series:
            beta = np.linalg.lstsq(seasonal_design(train), values[train], rcond=None)[0]
            forecast = seasonal_design(future) @ beta
            baseline = values[train[-1]]
            model_losses.extend((forecast - values[future]) ** 2)
            baseline_losses.extend((baseline - values[future]) ** 2)
    assert np.mean(model_losses) < np.mean(baseline_losses)
    revisions = pd.DataFrame(
        {"event": [10, 10, 11], "available": [12, 20, 13], "value": [1, 99, 2]}
    )
    asof = (
        revisions[revisions.available <= 15]
        .sort_values("available")
        .drop_duplicates("event", keep="last")
    )
    assert asof.set_index("event").loc[10, "value"] == 1
    result = {
        "rolling_model_rmse": np.sqrt(np.mean(model_losses)),
        "rolling_last_value_rmse": np.sqrt(np.mean(baseline_losses)),
        "forecast_count": len(model_losses),
        "asof_values": asof.value.tolist(),
    }
    print("03 vintage-aware forecasting:", result)
    return result


def main():
    case_03()


if __name__ == "__main__":
    main()
