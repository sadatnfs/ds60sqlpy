# Day 36 — Dimensionality Reduction with PCA (Companion Guide)

## Learning objectives
- Understand variance, covariance, eigenvectors, and principal components
- Standardize features and fit PCA; interpret explained variance
- Use PCA for compression, denoising, and visualization

## Why this matters
High-dimensional data can be noisy and redundant. PCA finds orthogonal directions of maximum variance, simplifying models and revealing structure.

## Mental models
- PCA rotates the coordinate system to align axes with directions of greatest variance
- Components are ordered by explained variance; the first few often capture most signal

## Core concepts and examples
### Preprocessing and fit
```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

X_scaled = StandardScaler().fit_transform(X)
pca = PCA(n_components=0.95, random_state=0)  # keep 95% variance
X_pca = pca.fit_transform(X_scaled)
print(pca.explained_variance_ratio_.cumsum())
```

### Choosing components
- Cumulative explained variance plot (scree)
- Keep enough components to capture most variance without overcompressing

### Inverse transform (denoising)
```python
X_recon = pca.inverse_transform(X_pca)  # approximate original in reduced subspace
```

### Visualization
```python
import matplotlib.pyplot as plt
plt.scatter(X_pca[:,0], X_pca[:,1], c=y, cmap='tab10', s=20, alpha=0.8)
plt.xlabel('PC1'); plt.ylabel('PC2'); plt.title('PCA Projection')
```

## Common pitfalls
- Skipping scaling: features with larger scales dominate components
- Interpreting components causally; they are linear combinations for variance, not meaning
- Using PCA before train/test split incorrectly; fit scaler and PCA within a Pipeline

## Practice exercises
1) Plot cumulative explained variance and choose k components
2) Compare classifier performance with/without PCA
3) Reconstruct a few samples from reduced space and compute reconstruction error

## Further reading
- PCA: https://scikit-learn.org/stable/modules/decomposition.html#pca
- Explained variance: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
