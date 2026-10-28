"""Embedding lookup, positions and a deliberately separate retrieval representation."""

import numpy as np


def example_one():
    embedding = np.array([[0.0, 0.0], [1.0, 2.0], [3.0, -1.0], [-2.0, 4.0]])
    positions = np.array([[0.0, 0.0], [0.1, 0.2], [0.2, 0.4]])
    ids = np.array([1, 2, 1])
    token_vectors = embedding[ids]
    hidden = token_vectors + positions
    np.testing.assert_array_equal(token_vectors[0], token_vectors[2])
    np.testing.assert_allclose(hidden, [[1.0, 2.0], [3.1, -0.8], [1.2, 2.4]])
    print("Token lookup rows:\n", token_vectors)
    print("Position-aware input:\n", hidden)
    assert embedding.nbytes == 64


def example_two():
    embedding = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    first = embedding[[1, 2, 1]].mean(axis=0)
    second = embedding[[1, 1, 2]].mean(axis=0)
    np.testing.assert_array_equal(first, second)
    cosine = float(first @ second / (np.linalg.norm(first) * np.linalg.norm(second)))
    assert abs(cosine - 1) < 1e-12
    print("Mean pooling lost order; cosine", cosine)
    document_vectors = np.array([[0.8, 0.2], [0.1, 0.9]])
    query = np.array([0.9, 0.1])
    scores = (
        document_vectors
        @ query
        / (np.linalg.norm(document_vectors, axis=1) * np.linalg.norm(query))
    )
    assert int(scores.argmax()) == 0
    print("Separate hand-authored retrieval-space scores:", scores)
    print("These fixture vectors do not establish semantic retrieval quality.")


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
