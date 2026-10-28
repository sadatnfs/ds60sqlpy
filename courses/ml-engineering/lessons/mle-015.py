"""mle-015: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Advance the cutoff and recompute maturity and coverage.
# TODO 2: Describe a process where positive outcomes arrive later.
# TODO 3: Explain what a KS alarm establishes.
# TODO 4: State whether a latency summary covers this process or a whole deployment.
# TODO 5: Define what happens after a freshness or schema alarm.
# TODO 6: Describe the limitations of a quantile from five samples.
