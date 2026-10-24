import numpy as np


def graph_bookkeeping():
    a = np.array(
        [[0.0, 1.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0], [1.0, 1.0, 0.0, 1.0], [0.0, 0.0, 1.0, 0.0]]
    )
    degree = a.sum(axis=1)
    assert np.array_equal(a, a.T) and degree.tolist() == [2.0, 2.0, 3.0, 1.0]
    assert degree.sum() == 2 * 4
    print("Undirected degrees:", degree, "edges:", degree.sum() / 2)


def pagerank():
    a = np.array(
        [[0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [1.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 0.0]]
    )
    p = np.zeros_like(a)
    for i, row in enumerate(a):
        p[i] = row / row.sum() if row.sum() else np.full(4, 0.25)
    r = np.full(4, 0.25)
    alpha = 0.85
    for _ in range(200):
        r = alpha * p.T @ r + (1 - alpha) * np.full(4, 0.25)
    residual = np.max(np.abs(r - (alpha * p.T @ r + (1 - alpha) * np.full(4, 0.25))))
    assert np.allclose(p.sum(axis=1), 1.0) and np.isclose(r.sum(), 1.0) and residual < 1e-12
    assert r[2] > r[0]
    print("PageRank:", r, "fixed-point residual:", residual)


def past_only_link_feature():
    past = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    common = int(past[0] @ past[2])
    assert common == 1 and past[0, 2] == 0
    future = past.copy()
    future[0, 2] = future[2, 0] = 1
    assert future[0, 2] == 1 and past[0, 2] == 0
    print("Past common neighbors for future pair (0,2):", common)


def main():
    graph_bookkeeping()
    pagerank()
    past_only_link_feature()


if __name__ == "__main__":
    main()
