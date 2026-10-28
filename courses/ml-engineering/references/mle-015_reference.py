"""mle-015: local, bounded ML engineering investigation."""

import numpy as np
import pandas as pd


def example_one():
    labels = pd.DataFrame(
        {
            "prediction_id": [1, 2, 3, 4],
            "prediction_time": [1, 2, 3, 4],
            "label_available": [3, 7, 5, 8],
            "label": [0, 1, 1, 0],
            "score": [0.1, 0.9, 0.6, 0.2],
        }
    )
    cutoff = 5
    mature = labels[labels.label_available <= cutoff]
    brier = float(np.mean((mature.score - mature.label) ** 2))
    assert mature.prediction_id.tolist() == [1, 3] and abs(brier - 0.085) < 1e-12
    assert len(mature) / len(labels) == 0.5
    return {"mature_prediction_ids": [1, 3], "brier": brier, "label_coverage": 0.5}


def example_two():
    from scipy.stats import ks_2samp

    baseline = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    shifted = baseline + 10
    statistic = float(ks_2samp(baseline, shifted).statistic)
    latencies = np.array([2.0, 3.0, 4.0, 8.0, 15.0])
    assert statistic == 1.0 and float(np.quantile(latencies, 0.95, method="higher")) == 15.0
    return {
        "covariate_shift_statistic": statistic,
        "observed_p95_ms": 15.0,
        "quality_requires_labels": True,
    }


def main():
    print(example_one())
    print(example_two())
    print("mle-015 reference checks passed")


if __name__ == "__main__":
    main()
