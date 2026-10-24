import numpy as np
from sklearn.naive_bayes import MultinomialNB
from scipy.special import logsumexp

X = np.array([[2.0, 1.0], [1.0, 0.0], [0.0, 2.0], [0.0, 1.0]])
Y = np.array([1, 1, 0, 0])


def manual_nb(x, y, alpha=1.0, prior=None):
    if np.any(x < 0) or alpha <= 0:
        raise ValueError("nonnegative counts and positive alpha required")
    classes = np.unique(y)
    counts = np.array([x[y == label].sum(axis=0) for label in classes])
    likelihood = (counts + alpha) / (counts.sum(axis=1, keepdims=True) + alpha * x.shape[1])
    class_prior = (
        np.array([np.mean(y == label) for label in classes])
        if prior is None
        else np.asarray(prior, dtype=float)
    )
    if np.any(class_prior <= 0) or not np.isclose(class_prior.sum(), 1):
        raise ValueError("positive normalized prior required")
    return classes, np.log(likelihood), np.log(class_prior)


def posterior(probe, log_likelihood, log_prior):
    score = np.asarray(probe) @ log_likelihood.T + log_prior
    return np.exp(score - logsumexp(score, axis=-1, keepdims=True))


def main():
    classes, ll, lp = manual_nb(X, Y)
    assert classes.tolist() == [0, 1]
    assert np.allclose(np.exp(ll), [[1 / 5, 4 / 5], [4 / 6, 2 / 6]])
    probe = np.array([[1.0, 0.0]])
    p = posterior(probe, ll, lp)
    assert np.allclose(p, [[3 / 13, 10 / 13]])
    model = MultinomialNB(alpha=1.0).fit(X, Y)
    assert np.allclose(model.feature_log_prob_, ll) and np.allclose(model.predict_proba(probe), p)
    assert np.allclose(posterior([[0.0, 0.0]], ll, lp), [[0.5, 0.5]])
    _, ll2, lp2 = manual_nb(X, Y, prior=[0.9, 0.1])
    changed = posterior(probe, ll2, lp2)
    assert changed[0, 0] > changed[0, 1]
    # Fixed vocabulary [urgent,thanks] cannot represent absent not.
    urgent = np.array([1.0, 0.0])
    not_urgent = np.array([1.0, 0.0])
    assert np.array_equal(posterior(urgent, ll, lp), posterior(not_urgent, ll, lp))
    assert np.isclose(np.exp(ll[0]).sum(), 1.0) and np.isclose(np.exp(ll[1]).sum(), 1.0)
    print(
        "nlp-008: manual/library parity; posterior [3/13,10/13]; prior and negation boundaries passed"
    )


if __name__ == "__main__":
    main()
