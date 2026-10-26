# PCA can reconstruct almost everything and lose the answer

Tutorial ID: `statistics-learning-006`. Prerequisites: `statistics-learning-001`, `statistics-learning-003`, `statistics-020`. Complete example: [learning_05.py](examples/learning_05.py).

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

Continue to [full validation](07-validation-as-a-procedure.md). Existing detailed practice: [Python Day 36](../../../../python/ds-60day/companion-guides/day36_dimensionality_reduction_pca.md). Reference: [scikit-learn decomposition](https://scikit-learn.org/stable/modules/decomposition.html).
