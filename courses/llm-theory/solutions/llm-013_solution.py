"""llm-013: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def verify():
    # Worked example A: Construct next-token pairs
    ids = np.array([2, 5, 7, 3])
    inputs = ids[:-1]
    labels = ids[1:]
    np.testing.assert_array_equal(inputs, [2, 5, 7])
    np.testing.assert_array_equal(labels, [5, 7, 3])

    # Worked example B: Expose identity labels
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

    # Exercise 1: Shift a batch of two sequences
    batch = np.array([[4, 1, 6, 2, 9], [3, 3, 8, 0, 5]])
    x_in = batch[:, :-1]
    y_out = batch[:, 1:]
    assert x_in.shape == y_out.shape == (2, 4)
    np.testing.assert_array_equal(y_out, [[1, 6, 2, 9], [3, 8, 0, 5]])

    # Exercise 2: Predict a partly hidden label bug
    row = batch[1]
    copied_row = row[:-1]
    target_row = row[1:]
    assert int(np.count_nonzero(copied_row == target_row)) == 1
    assert int(np.count_nonzero(copied_row != target_row)) == 3
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
