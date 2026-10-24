import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score


def centroids_and_stability():
    x = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [8.0, 8.0], [8.0, 9.0], [9.0, 8.0]])
    first = KMeans(n_clusters=2, n_init=10, random_state=21).fit(x)
    second = KMeans(n_clusters=2, n_init=10, random_state=22).fit(x)
    assert adjusted_rand_score(first.labels_, second.labels_) == 1
    expected = np.array([[1 / 3, 1 / 3], [25 / 3, 25 / 3]])
    assert np.allclose(first.cluster_centers_[np.argsort(first.cluster_centers_[:, 0])], expected)
    print("Centers:", first.cluster_centers_, "seed agreement:", 1.0)


def density_and_noise():
    x = np.array([[0.0, 0.0], [0.1, 0.0], [0.0, 0.1], [5.0, 5.0]])
    labels = DBSCAN(eps=0.2, min_samples=3).fit_predict(x)
    assert np.all(labels[:3] == labels[0]) and labels[-1] == -1
    print("Density labels:", labels)


def mixture_responsibilities():
    x = np.array([[-3.0], [-2.8], [-2.6], [2.6], [2.8], [3.0]])
    model = GaussianMixture(n_components=2, random_state=21, reg_covar=1e-4).fit(x)
    responsibilities = model.predict_proba(x)
    assert np.allclose(responsibilities.sum(axis=1), 1)
    assert np.all(responsibilities.max(axis=1) > 0.99)
    assert np.allclose(np.sort(model.means_.ravel()), [-2.8, 2.8])
    print(
        "Mixture means:",
        model.means_.ravel(),
        "minimum maximum responsibility:",
        responsibilities.max(axis=1).min(),
    )


def main():
    centroids_and_stability()
    density_and_noise()
    mixture_responsibilities()


if __name__ == "__main__":
    main()
