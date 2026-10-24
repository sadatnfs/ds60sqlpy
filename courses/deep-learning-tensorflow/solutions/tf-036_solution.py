"""tf-036: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf


def verify():
    # Exercise 1: Build a literal model bundle
    weights = np.array([[2.0], [-1.0]], dtype="float32")
    schema = {"features": ["a", "b"], "dtype": "float32", "width": 2}
    model = tf.keras.Sequential(
        [tf.keras.Input(shape=(2,)), tf.keras.layers.Dense(1, use_bias=False)]
    )
    model.layers[0].set_weights([weights])
    np.testing.assert_array_equal(model(np.array([[3, 4]], dtype="float32")).numpy(), [[2]])

    # Exercise 2: Freeze and hash a split manifest
    import hashlib, json

    split = {"train": ["a", "b"], "test": ["c", "d"]}
    payload = json.dumps(split, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(payload).hexdigest()
    assert not set(split["train"]) & set(split["test"]) and len(digest) == 64

    # Exercise 3: Catch tampered lineage
    changed = {"train": ["a", "b"], "test": ["c", "e"]}
    other = hashlib.sha256(
        json.dumps(changed, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert other != digest

    # Exercise 4: Block incompatible schemas
    incoming = {"features": ["a", "b", "c"], "dtype": "float32", "width": 3}
    assert incoming != schema

    # Exercise 5: Make the decision fail closed
    gates = {"prediction": True, "split": True, "restart": None, "schema": True}
    assert not all(value is True for value in gates.values())
    gates.update(restart=True, schema=False)
    assert not all(value is True for value in gates.values())

    # Exercise 6: Retain a rollback decision
    record = {
        "candidate": "v2",
        "previous": "v1",
        "holdout_count": 2,
        "decision": "go" if all(v is True for v in gates.values()) else "no-go",
        "limits": ["synthetic fixture only"],
    }
    assert (
        record["decision"] == "no-go"
        and record["previous"] == "v1"
        and record["holdout_count"] == 2
    )
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
