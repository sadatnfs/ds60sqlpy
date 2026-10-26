"""Complete offline worked example. See the matching tutorial for assumptions."""

import hashlib
import json

import numpy as np
from scipy import special
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss


def case_07():
    rng = np.random.default_rng(4007)
    n = 360
    event_time = np.arange(n)
    available = event_time + 3
    x = rng.normal(size=n)
    y = rng.binomial(1, special.expit(1.8 * x))
    cutoff = 240
    train = available <= cutoff
    test = (event_time > cutoff) & (available <= 320)
    assert np.all(available[train] <= cutoff) and not np.any(train & test)
    model = LogisticRegression().fit(x[train, None], y[train])
    prediction = model.predict_proba(x[test, None])[:, 1]
    reference_loss = log_loss(y[test], prediction)
    leaked_available = event_time + 10
    feature_allowed = leaked_available <= event_time
    assert not feature_allowed.any()  # A future-derived label feature is excluded.
    record = {
        "definition": "logistic-one-predictor-v1",
        "label_delay": 3,
        "cutoff": cutoff,
        "train_rows": int(train.sum()),
        "test_rows": int(test.sum()),
        "coefficient": model.coef_.tolist(),
        "intercept": model.intercept_.tolist(),
    }
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    identity = hashlib.sha256(encoded).hexdigest()
    shifted_x = rng.normal(size=500)
    shifted_y = rng.binomial(1, special.expit(-1.8 * shifted_x))
    shifted_loss = log_loss(shifted_y, model.predict_proba(shifted_x[:, None])[:, 1])
    safe_baseline_loss = log_loss(shifted_y, np.full(len(shifted_y), 0.5))
    action = "rollback candidate" if shifted_loss > safe_baseline_loss + 0.1 else "continue review"
    assert action == "rollback candidate" and len(identity) == 64
    result = {
        "artifact_identity": identity,
        "record": record,
        "held_out_log_loss": reference_loss,
        "shifted_log_loss": shifted_loss,
        "baseline_log_loss": safe_baseline_loss,
        "decision": action,
    }
    print("07 scientific workflow evidence:", result)
    return result


def main():
    case_07()


if __name__ == "__main__":
    main()
