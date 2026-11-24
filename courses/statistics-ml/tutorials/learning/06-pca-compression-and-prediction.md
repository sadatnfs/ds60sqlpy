# PCA can reconstruct almost everything and lose the answer

Tutorial ID: `statistics-learning-006`. Prerequisites: `statistics-learning-001`, `statistics-learning-003`, `statistics-020`. Complete example: [learning_06.py](examples/learning_06.py).

## Key terms

- **Singular value decomposition:** The factorization \(X=U\Sigma V^{\mathsf T}\) of centered data whose columns of \(V\) give orthonormal loading directions.
- **Component scores:** The coordinates \(Z=XV_k\) of each centered row on the first \(k\) loading directions.
- **Reconstruction error:** The squared distance between the centered data and its rank-\(k\) reconstruction, equal to the sum of the discarded squared singular values.
- **Standardization:** Rescaling features to a common scale using training statistics, which changes the reconstruction cost and therefore the principal directions.
- **Variance ratio:** The share of total input variance a component retains, which measures compression and says nothing about predicting the outcome.

## Write the reconstruction problem

Center each feature using training means. For centered \(X\), the singular value decomposition \(X=U\Sigma V^{\mathsf T}\) supplies orthonormal loading directions. Retain the first \(k\) columns of \(V\), compute scores \(Z=XV_k\), and reconstruct \(\widehat X=ZV_k^{\mathsf T}\). Add the training means to return to the original coordinates.

The squared reconstruction error is the sum of the discarded squared singular values. The sample variance of component \(j\) is \(s_j^2/(n-1)\). PCA therefore optimizes an input reconstruction loss; it never sees the outcome labels in that optimization.

## A hand-checkable predictive counterexample

The dataset has a large nuisance feature ranging from -100 to 100. For each nuisance value, create two rows with second features -.1 and +.1. The target is zero for -.1 and one for +.1. Balanced sign pairs make the columns exactly uncorrelated. The nuisance has far more variance but no information that distinguishes the two labels at any given value.

Raw PCA's first component retains more than 99.99% of input variance and drops the second column. Its reconstruction MSE is .005 averaged over both columns: every row loses squared signal .01, while the first coordinate is reconstructed exactly. The code checks the corresponding sum-of-squared-discarded-singular-values identity.

A logistic model using that single component has accuracy .5 on new balanced sign pairs. A scaled model using both features has accuracy one in this deliberately separable noiseless task. This is an extreme construction to expose the distinction between compression and prediction, not a claim about typical dataset performance.

## Change the units

Standardizing both features gives them equal sample variance, so the two PCA variance ratios are .5 and .5. There is then no uniquely preferred individual first direction: the equal-eigenvalue subspace admits rotations. Component signs are also arbitrary; flipping both a loading and its scores preserves reconstruction.

Raw units and standardized units encode different reconstruction costs. If an error of one dollar and one visit have different consequences, equal variance does not automatically mean equal practical importance. Choose scaling based on the model geometry and scientific target, and explain it in the result.

## Choose dimension inside the learning procedure

A variance threshold is a compression rule. If the goal is prediction, select the PCA-plus-model pipeline using development validation, with means, scales and directions fitted only inside training folds. Supervised alternatives such as partial least squares use labels, making that separation even more important. Fitting the transformation once on all data before CV exposes held-out information even if the final estimator is fit correctly.

Add noise or nearly tied directions to investigate stability. Compare aligned subspaces rather than demanding that every loading maintain the same sign and orientation. Reconstruction error on new observations can reveal shift, but good reconstruction does not establish calibration or causal relevance.

**Answered discussion: Should we always standardize before PCA?** No. Standardization is a substantive geometry choice. It prevents raw numeric scale from dominating, but can amplify low-variance measurement noise. Compare defensible representations under the intended downstream task.

## Worked example: PCA by hand with the SVD

The counterexample in `examples/learning_06.py` can be decomposed with three lines of NumPy, which makes the reconstruction identity checkable without any library wrapper.

```python
import numpy as np

nuisance = np.linspace(-100, 100, 100)
x = np.column_stack([np.repeat(nuisance, 2), np.tile([-0.1, 0.1], 100)])
centered = x - x.mean(axis=0)
_, s, vt = np.linalg.svd(centered, full_matrices=False)
print("singular values:", np.round(s, 3))
var = s**2 / (len(x) - 1)
print(f"variance per component: {var[0]:.1f} and {var[1]:.4f}")
scores = centered @ vt[:1].T
lost = np.sum((centered - scores @ vt[:1]) ** 2)
print(f"discarded squared error={lost:.3f}  s_2^2={s[1] ** 2:.3f}")
```

```text
singular values: [824.703   1.414]
variance per component: 3417.8 and 0.0101
discarded squared error=2.000  s_2^2=2.000
```

The two singular values are 824.703 and 1.414, so the first component carries a variance of 3417.8 and the second only 0.0101. Dropping the second component loses a squared error of exactly 2.000, which equals \(s_2^2\): each of the 200 rows loses its \(\pm0.1\) coordinate, and \(200\times0.01=2\). Dividing by the 400 matrix entries gives the reconstruction MSE of 0.005 that the guide reports. Every number here is about inputs; the label column never enters.

## Worked example: choose the dimension by prediction

Now let cross-validation pick the number of components inside the pipeline, once on raw units and once after scaling.

```python
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

nuisance = np.linspace(-100, 100, 100)
x = np.column_stack([np.repeat(nuisance, 2), np.tile([-0.1, 0.1], 100)])
y = np.tile([0, 1], 100)
for scaled in (False, True):
    steps = [StandardScaler()] if scaled else []
    pipe = make_pipeline(*steps, PCA(), LogisticRegression())
    search = GridSearchCV(
        pipe, {"pca__n_components": [1, 2]}, cv=StratifiedKFold(5, shuffle=True, random_state=6)
    ).fit(x, y)
    means = np.round(search.cv_results_["mean_test_score"], 3)
    print(f"scaled={scaled}: CV accuracy for k=1,2 -> {means.tolist()}")
```

```text
scaled=False: CV accuracy for k=1,2 -> [0.38, 1.0]
scaled=True: CV accuracy for k=1,2 -> [0.745, 1.0]
```

On raw units, one component scores 0.38, no better than guessing, and two components score 1.0; the search therefore keeps the low-variance direction that a 99.99% variance threshold would discard. After scaling, one component scores 0.745. Both scaled directions have equal variance, so the first component is an arbitrary rotation that mixes the nuisance and the signal, and its usefulness depends on that accident. Because the scaler and PCA live inside the pipeline, each fold learns its own means, scales and loadings, so the comparison respects the fold boundary.

## Checks before using components downstream

Print the singular values, not only cumulative variance, and look for near ties that make loadings unstable. Fit PCA only on training folds. Compare the downstream metric across several dimensions rather than fixing \(k\) by a variance rule. When components feed a report, align signs to a reference and describe subspaces, since loadings can flip between refits.

Continue to [full validation](07-validation-as-a-procedure.md). Existing detailed practice: [Python Day 36](../../../../python/ds-60day/companion-guides/day36_dimensionality_reduction_pca.md). Reference: [scikit-learn decomposition](https://scikit-learn.org/stable/modules/decomposition.html).
