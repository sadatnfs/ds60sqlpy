"""llm-013: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def verify():
    # Exercise 1: Construct next-token pairs
    ids = np.array([2, 5, 7, 3])
    inputs = ids[:-1]
    labels = ids[1:]
    np.testing.assert_array_equal(inputs, [2, 5, 7])
    np.testing.assert_array_equal(labels, [5, 7, 3])

    # Exercise 2: Expose identity labels
    copied = inputs.copy()
    assert np.count_nonzero(copied != labels) == 3

    # Exercise 3: Detect exact duplicates
    import hashlib

    train = {"a": "alpha beta"}
    valid = {"copy": "alpha beta"}
    hash_text = lambda text: hashlib.sha256(text.encode()).hexdigest()
    assert {hash_text(t) for t in train.values()} & {hash_text(t) for t in valid.values()}

    # Exercise 4: Detect family leakage
    families = {"a": "F", "b": "F", "c": "G"}
    assert {families["a"]} & {families["b"]} == {"F"}

    # Exercise 5: Freeze a vocabulary
    vocab = {"alpha": 0, "beta": 1}
    before = dict(vocab)
    unknown = vocab.get("gamma", -1)
    assert unknown == -1 and vocab == before

    # Exercise 6: Count active targets
    documents = [[2, 5, 7, 3], [8, 3]]
    pairs = [(a, b) for doc in documents for a, b in zip(doc[:-1], doc[1:])]
    assert len(pairs) == 4 and (3, 8) not in pairs
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
