import numpy as np


def cooccurrence(documents, vocabulary, window=1):
    if window < 1:
        raise ValueError("positive context window required")
    index = {word: i for i, word in enumerate(vocabulary)}
    if len(index) != len(vocabulary):
        raise ValueError("unique vocabulary required")
    matrix = np.zeros((len(index), len(index)), dtype=int)
    for tokens in documents:
        for i, word in enumerate(tokens):
            if word not in index:
                raise ValueError("unknown word")
            for j in range(max(0, i - window), min(len(tokens), i + window + 1)):
                if i != j:
                    if tokens[j] not in index:
                        raise ValueError("unknown context")
                    matrix[index[word], index[tokens[j]]] += 1
    return matrix


def ppmi(counts):
    counts = np.asarray(counts, dtype=float)
    if counts.ndim != 2 or np.any(~np.isfinite(counts)) or np.any(counts < 0):
        raise ValueError("finite nonnegative matrix required")
    total = counts.sum()
    result = np.zeros_like(counts)
    if total == 0:
        return result
    denominator = counts.sum(axis=1)[:, None] * counts.sum(axis=0)[None, :]
    valid = (counts > 0) & (denominator > 0)
    result[valid] = np.maximum(0.0, np.log(counts[valid] * total / denominator[valid]))
    return result


def cosine(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("same shape required")
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    return None if denominator == 0 else float(a @ b / denominator)


def main():
    c = cooccurrence([["cat", "pet", "cat"]], ["cat", "pet"])
    assert c.tolist() == [[0, 2], [2, 0]]
    assert cooccurrence([["cat"], ["pet"]], ["cat", "pet"]).sum() == 0
    counts = np.array([[4.0, 3.0, 0.0], [3.0, 4.0, 0.0], [0.0, 0.0, 6.0]])
    matrix = ppmi(counts)
    assert np.isclose(matrix[0, 0], np.log(80 / 49)) and matrix[0, 2] == 0
    assert np.all(np.isfinite(matrix)) and np.all(matrix >= 0)
    assert cosine(matrix[0], matrix[1]) > 0 and cosine(matrix[0], matrix[2]) == 0
    assert cosine([0, 0], [1, 0]) is None
    u, s, vt = np.linalg.svd(matrix, full_matrices=False)
    embedding = u[:, :2] * s[:2]
    reconstructed = embedding @ vt[:2]
    assert np.linalg.norm(matrix - reconstructed) > 0 and np.linalg.norm(
        matrix - reconstructed
    ) < np.linalg.norm(matrix)
    assert np.isclose(cosine(embedding[0], embedding[1]), 1.0)
    rotation = np.array([[0.0, -1.0], [1.0, 0.0]])
    assert np.isclose(
        cosine(embedding[0], embedding[1]), cosine(embedding[0] @ rotation, embedding[1] @ rotation)
    )
    assert np.all(ppmi(np.zeros((2, 2))) == 0)
    print("nlp-012: window counts, PPMI, cosine, rank-two projection and rotation checks passed")


if __name__ == "__main__":
    main()
