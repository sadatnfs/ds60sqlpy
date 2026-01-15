# Day 36 — Solutions: Dimensionality Reduction with PCA

We standardize features, fit PCA, and choose the number of components via cumulative explained variance. We also compare PCA before/after scaling and briefly try SelectKBest.

Contents
- Exercise 1: Plot cumulative explained variance and choose K
- Exercise 2: Compare PCA before vs after scaling
- Exercise 3: Try SelectKBest and compare to PCA

---

Setup
```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris
import numpy as np, matplotlib.pyplot as plt
X, y = load_iris(return_X_y=True)
```

Exercise 1 — Cumulative explained variance (scree)
```python
sc = StandardScaler()
Xz = sc.fit_transform(X)

pca = PCA().fit(Xz)  # all components
cum = np.cumsum(pca.explained_variance_ratio_)

plt.plot(range(1, len(cum)+1), cum, marker='o')
plt.axhline(0.95, color='r', ls='--', label='95%')
plt.xlabel('n_components'); plt.ylabel('cumulative explained variance')
plt.title('Scree (cumulative)'); plt.legend(); plt.tight_layout(); plt.show()

k95 = int(np.argmax(cum >= 0.95) + 1)
print({'k_95pct': k95, 'cum': cum})
```
Line-by-line
- Standardize first so features contribute comparably
- PCA().fit gets variance ratios; cumulative sum guides K selection

---

Exercise 2 — PCA before vs after scaling
```python
pca_raw = PCA(n_components=2).fit(X)
X2_raw = pca_raw.transform(X)

pca_z = PCA(n_components=2).fit(Xz)
X2_z  = pca_z.transform(Xz)

f, ax = plt.subplots(1,2, figsize=(8,3))
ax[0].scatter(X2_raw[:,0], X2_raw[:,1], c=y, cmap='tab10', s=15)
ax[0].set_title('PCA on raw features')
ax[1].scatter(X2_z[:,0], X2_z[:,1], c=y, cmap='tab10', s=15)
ax[1].set_title('PCA on standardized features')
plt.tight_layout(); plt.show()
```
Observation
- Without scaling, high-variance features dominate components; scaling often yields more balanced PCs

---

Exercise 3 — SelectKBest vs PCA
```python
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

clf_pca = Pipeline([
    ('sc', StandardScaler()),
    ('pca', PCA(n_components=2, random_state=0)),
    ('lr', LogisticRegression(max_iter=1000))
])

clf_kbest = Pipeline([
    ('sc', StandardScaler()),
    ('k', SelectKBest(score_func=f_classif, k=2)),
    ('lr', LogisticRegression(max_iter=1000))
])

print('PCA acc:', cross_val_score(clf_pca, X, y, cv=5).mean())
print('KBest acc:', cross_val_score(clf_kbest, X, y, cv=5).mean())
```
Notes
- PCA is unsupervised; SelectKBest uses label information
- Pick based on validation performance and downstream interpretability
