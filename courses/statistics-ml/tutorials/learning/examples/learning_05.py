"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def case_05():
    # Balanced sign pairs make signal exactly orthogonal to the large nuisance.
    nuisance = np.linspace(-100, 100, 100)
    x = np.column_stack([np.repeat(nuisance, 2), np.tile([-0.1, 0.1], 100)])
    y = np.tile([0, 1], 100)
    test_x = np.column_stack([np.repeat(np.linspace(-95, 95, 40), 2), np.tile([-0.1, 0.1], 40)])
    test_y = np.tile([0, 1], 40)
    pca = PCA(n_components=1).fit(x)
    reconstruction = pca.inverse_transform(pca.transform(x))
    pca_model = make_pipeline(PCA(n_components=1), LogisticRegression()).fit(x, y)
    full_model = make_pipeline(StandardScaler(), LogisticRegression()).fit(x, y)
    assert pca.explained_variance_ratio_[0] > 0.9999
    assert pca_model.score(test_x, test_y) == 0.5 and full_model.score(test_x, test_y) == 1
    assert np.isclose(np.mean((x - reconstruction) ** 2), 0.005)
    centered = x - x.mean(axis=0)
    singular = np.linalg.svd(centered, compute_uv=False)
    assert np.isclose(np.sum((x - reconstruction) ** 2), singular[1] ** 2)
    scaled = PCA().fit(StandardScaler().fit_transform(x))
    result = {
        "raw_retained_variance": pca.explained_variance_ratio_[0],
        "reconstruction_mse": np.mean((x - reconstruction) ** 2),
        "pca_test_accuracy": pca_model.score(test_x, test_y),
        "full_test_accuracy": full_model.score(test_x, test_y),
        "scaled_variance_ratios": scaled.explained_variance_ratio_.tolist(),
    }
    print("05 compression versus prediction:", result)
    return result


def main():
    case_05()


if __name__ == "__main__":
    main()
