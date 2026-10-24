import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

TRAIN = [
    "urgent outage",
    "urgent incident",
    "outage incident",
    "thanks resolved",
    "thanks update",
    "resolved update",
]
LABELS = np.array([1, 1, 1, 0, 0, 0])


def fit_classifier(c=1.0):
    if c <= 0:
        raise ValueError("C must be positive")
    model = make_pipeline(
        CountVectorizer(token_pattern=r"(?u)\b\w+\b"),
        LogisticRegression(C=c, solver="liblinear", random_state=0, max_iter=500),
    )
    return model.fit(TRAIN, LABELS)


def sigmoid(score):
    score = np.asarray(score, dtype=float)
    return np.exp(-np.logaddexp(0.0, -score))


def brier(probability, truth):
    p = np.asarray(probability, dtype=float)
    y = np.asarray(truth, dtype=float)
    if p.shape != y.shape or p.size == 0 or not np.all(np.isfinite(p)):
        raise ValueError("equal nonempty finite arrays required")
    if np.any((p < 0) | (p > 1)) or np.any((y != 0) & (y != 1)):
        raise ValueError("binary labels and probabilities required")
    return float(np.mean((p - y) ** 2))


def main():
    x = np.array([2.0, 1.0])
    weights = np.array([2.0, -1.0])
    score = x @ weights - 0.5
    assert score == 2.5 and np.isclose(sigmoid(score), 0.9241418199787566)
    model = fit_classifier()
    vectorizer = model[0]
    heldout = vectorizer.transform(["escalation urgent"])
    assert "escalation" not in vectorizer.vocabulary_ and heldout.shape[1] == 6
    assert model.predict(["urgent outage", "thanks resolved"]).tolist() == [1, 0]
    small = fit_classifier(0.1)[1].coef_
    large = fit_classifier(10.0)[1].coef_
    assert np.linalg.norm(small) < np.linalg.norm(large)
    p = np.array([0.2, 0.4, 0.8])
    assert (p >= 0.5).tolist() == [False, False, True]
    assert (p >= 0.3).tolist() == [False, True, True]
    truth = [1, 0, 1, 0]
    assert np.isclose(brier([0.9, 0.9, 0.1, 0.1], truth), 0.41)
    assert np.isclose(brier([0.6, 0.6, 0.4, 0.4], truth), 0.26)
    unigram = vectorizer.transform(["urgent", "not urgent"]).toarray()
    assert np.array_equal(unigram[0], unigram[1])
    bigram = CountVectorizer(ngram_range=(1, 2)).fit(["urgent", "not urgent"])
    assert "not urgent" in bigram.vocabulary_
    try:
        brier([1.2], [1])
    except ValueError:
        pass
    else:
        raise AssertionError("invalid probability accepted")
    print("nlp-009: logit=2.5; Brier=.41/.26; threshold and negation checks passed")


if __name__ == "__main__":
    main()
