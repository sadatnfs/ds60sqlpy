import numpy as np
from sklearn.model_selection import GroupKFold, TimeSeriesSplit
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss, confusion_matrix


def splits_match_use():
    groups = np.repeat(np.arange(6), 2)
    x = np.arange(12)[:, None]
    for train, test in GroupKFold(3).split(x, groups=groups):
        assert set(groups[train]).isdisjoint(groups[test])
    for train, test in TimeSeriesSplit(3).split(x):
        assert train.max() < test.min()
    print("Group identities separated; temporal folds preserve order")


def ranking_vs_probability():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.1, 0.4, 0.6, 0.9])
    distorted = np.sqrt(p)
    assert roc_auc_score(y, p) == roc_auc_score(y, distorted) == 1
    assert not np.isclose(brier_score_loss(y, p), brier_score_loss(y, distorted))
    print(
        "AUC stays 1; Brier:",
        brier_score_loss(y, p),
        brier_score_loss(y, distorted),
        "log loss:",
        log_loss(y, p),
    )


def decisions_and_cost():
    y = np.array([0, 1, 0, 1, 1])
    p = np.array([0.1, 0.3, 0.4, 0.7, 0.9])
    threshold = 2 / (2 + 8)
    predicted = (p > threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    assert (tn, fp, fn, tp) == (1, 1, 0, 3)
    assert 2 * fp + 8 * fn == 2
    print(
        "Precision:", tp / (tp + fp), "recall:", tp / (tp + fn), "realized cost:", 2 * fp + 8 * fn
    )


def paired_losses():
    y = np.array([0.0, 1.0, 2.0, 3.0])
    a = np.array([0.0, 2.0, 2.0, 4.0])
    b = np.array([1.0, 2.0, 3.0, 4.0])
    difference = (a - y) ** 2 - (b - y) ** 2
    assert np.isclose(difference.mean(), -0.5)
    print("Paired squared-loss differences:", difference, "mean:", difference.mean())


def main():
    splits_match_use()
    ranking_vs_probability()
    decisions_and_cost()
    paired_losses()


if __name__ == "__main__":
    main()
