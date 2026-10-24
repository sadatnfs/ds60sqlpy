import numpy as np


def pca_geometry():
    x = np.array([[1.0, 2.0], [2.0, 4.0], [3.0, 6.0], [4.0, 8.0]])
    mean = x.mean(axis=0)
    centered = x - mean
    u, s, vt = np.linalg.svd(centered, full_matrices=False)
    scores = centered @ vt[:1].T
    reconstruction = scores @ vt[:1] + mean
    variance = s * s / (len(x) - 1)
    assert np.allclose(reconstruction, x) and np.isclose(variance[0] / variance.sum(), 1.0)
    assert np.isclose(abs(vt[0] @ np.array([1.0, 2.0]) / np.sqrt(5)), 1.0)
    print("PCA loading:", vt[0], "explained ratio:", variance[0] / variance.sum())


def scaling_and_leakage():
    train = np.array([0.0, 2.0, 4.0])
    test = np.array([100.0])
    train_mean = train.mean()
    train_sd = train.std(ddof=0)
    transformed = (test - train_mean) / train_sd
    leaked_mean = np.concatenate([train, test]).mean()
    assert train_mean == 2 and leaked_mean == 26.5 and transformed[0] > 50
    print(
        "Training-only mean:",
        train_mean,
        "leaked mean:",
        leaked_mean,
        "held-out z:",
        transformed[0],
    )


def target_and_time_encoding():
    labels = np.array([0.0, 1.0, 0.0, 1.0])
    naive_unique_category = labels.copy()
    leave_one_out = np.array([np.delete(labels, i).mean() for i in range(4)])
    assert np.array_equal(naive_unique_category, labels)
    assert not np.array_equal(leave_one_out, labels)
    values = np.array([10.0, 20.0, 30.0, 40.0])
    lagged_mean = np.array([np.nan] + [values[:i].mean() for i in range(1, 4)])
    assert np.allclose(lagged_mean[1:], [10, 15, 20])
    print(
        "Naive unique-category encoding:",
        naive_unique_category,
        "fallback without own label:",
        leave_one_out,
    )
    print("Strictly prior expanding means:", lagged_mean)


def main():
    pca_geometry()
    scaling_and_leakage()
    target_and_time_encoding()


if __name__ == "__main__":
    main()
