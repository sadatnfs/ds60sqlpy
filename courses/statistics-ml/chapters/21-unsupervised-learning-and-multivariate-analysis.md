# 21. Unsupervised Learning and Multivariate Analysis

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-021`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Unsupervised methods describe structure without a supervised target, but they still optimize an objective chosen by people. A cluster can mean a compact Euclidean region, a dense connected region, a latent probability component or an actionable customer segment. These definitions need not agree, and a visually compelling grouping is not evidence that nature contains that exact partition.

### K-means and mixtures answer different questions

K-means minimizes \(\sum_i\lVert x_i-\mu_{z_i}\rVert_2^2\). Assignment chooses the nearest centroid; updating each centroid to its assigned mean cannot increase that objective. Repeating these steps reaches a local solution, so multiple initializations matter. Euclidean scaling, outliers and a forced number of roughly compact groups shape its output.

A Gaussian mixture instead models \(p(x)=\sum_k\pi_k\mathcal{N}(x\mid\mu_k,\Sigma_k)\). The E-step computes soft posterior component responsibilities; the M-step updates parameters using those weights. Flexible covariances model elongated groups but can collapse around individual points without regularization. Mixture likelihood can improve by adding components even when those components do not correspond to meaningful categories. Compare predictive density, complexity, stability and domain utility.

### Latent dimensions are not always clusters

Factor analysis writes \(x=\Lambda f+\epsilon\) and separates shared covariance from feature-specific noise. PCA minimizes reconstruction error without that noise model. Confirmatory factor analysis imposes a specified loading pattern; identification requires constraints on scales and rotations. A two-dimensional t-SNE or UMAP view is a visualization whose neighborhood construction and optimization can change apparent separation. Global distances, cluster sizes and empty gaps should not be interpreted as calibrated population facts.

For every grouping, ask whether it survives resampling, scaling changes and reasonable parameters, and whether it supports a useful decision. If cluster assignments will govern actions, evaluate those actions directly.

## Methods, mechanisms, and limits

### stat-21-01

**K-means clustering**

Alternate nearest-centroid assignments with mean updates to minimize squared Euclidean distortion. Multiple starts reduce local-optimum sensitivity. Scale choices, outliers and elongated groups can make the resulting partition misleading.

### stat-21-02

**K-medoids clustering**

Choose actual observations as representative centers and optimize a dissimilarity objective. Medoids support non-Euclidean distances and are more robust than means, but exact search is expensive and results still depend on the metric.

### stat-21-03

**Hierarchical clustering**

Build a dendrogram by successive merges or splits using a linkage rule. Single linkage can chain through bridges; complete linkage favors compact groups. Cutting the tree is an additional modeling decision.

### stat-21-04

**DBSCAN**

Connect sufficiently dense neighborhoods using radius and minimum-neighbor settings, labeling isolated points noise. It can recover nonconvex shapes but struggles when densities differ or distance becomes uninformative in high dimensions.

### stat-21-05

**HDBSCAN**

Build and select stable clusters across a density hierarchy rather than one fixed radius. Different implementations and selection settings can differ. Density-based stability does not establish causal or operational meaning.

### stat-21-06

**Gaussian mixture models**

Estimate a weighted sum of Gaussian densities with soft memberships. Covariance structure controls shape and parameter count. Label switching, local optima and collapsing covariance require diagnostics and regularization.

### stat-21-07

**Model-based clustering**

Define groups through a probabilistic mixture and infer latent memberships. The component family is a substantive assumption. A better density approximation may use multiple components within one real-world category.

### stat-21-08

**Spectral clustering**

Construct a similarity graph, use Laplacian eigenvectors, then cluster the embedding. Neighborhood and scale parameters determine connectivity. Disconnected or poorly scaled graphs can dominate the result.

### stat-21-09

**Biclustering**

Identify coherent subsets of rows and columns simultaneously, such as user groups sharing subsets of item interests. The chosen coherence pattern matters; there need not be one global partition of every row and column.

### stat-21-10

**Fuzzy clustering**

Allow membership weights across groups, often optimizing a softened centroid objective. Membership grades depend on the fuzziness parameter and are not automatically calibrated posterior probabilities.

### stat-21-11

**Latent class analysis**

Model categorical responses as mixtures of latent classes, commonly assuming conditional independence within class. Extra classes can absorb violations of that independence, so inferred class count need not reveal true population types.

### stat-21-12

**Latent profile analysis**

Use continuous-response mixture models to characterize latent profiles, often with Gaussian assumptions. Covariance constraints and scaling affect the profiles. Small spurious classes can arise from skewness or outliers.

### stat-21-13

**Factor analysis**

Explain shared covariance through latent factors plus feature-specific error. Rotation and scale constraints determine identification. Factors are mathematical constructs until their interpretation is supported by measurement theory.

### stat-21-14

**Exploratory factor analysis**

Explore loading patterns and factor counts from covariance structure. Rotation aids interpretation but does not make the solution unique. Use independent data or transparent uncertainty before claiming a stable construct structure.

### stat-21-15

**Confirmatory factor analysis**

Specify which variables load on which latent constructs and assess model implications. Good fit does not uniquely verify the proposed construct theory; alternative models can fit similarly and modification indices can overfit.

### stat-21-16

**Canonical correlation analysis**

Find linear combinations of two variable blocks maximizing correlation. High dimension relative to sample size can create spurious canonical correlations. Regularization and held-out evaluation are essential.

### stat-21-17

**Partial least squares**

Construct components oriented toward predictor-outcome covariance, unlike unsupervised PCA. Select component count inside validation. Strong in-sample covariance can still reflect leakage or overfitting.

### stat-21-18

**Multidimensional scaling**

Embed objects so low-dimensional distances approximate supplied dissimilarities. Stress measures fit to that chosen distance structure. Non-Euclidean dissimilarities and low target dimension can force distortions.

### stat-21-19

**t-SNE**

Optimize a neighborhood-preserving probability objective for visualization. Perplexity, seed and optimization affect the map. Cluster gaps, relative sizes and global distances are not reliably comparable without additional analysis.

### stat-21-20

**UMAP**

Build a neighborhood-based fuzzy graph and optimize a low-dimensional representation. Neighbor count and distance settings control local-global tradeoffs. Apparent islands require validation in the original feature space.

### stat-21-21

**Manifold learning**

Assume high-dimensional observations lie near a lower-dimensional nonlinear structure. Neighborhood quality and sampling density govern recovery. Sparse bridges, noise or disconnected components can break the inferred geometry.

### stat-21-22

**Correspondence analysis**

Decompose deviations from independence in a contingency table using chi-square geometry. Rare categories can have high leverage. Row/column map distances require interpretation consistent with the chosen normalization.

### stat-21-23

**Multiple correspondence analysis**

Extend correspondence analysis to several categorical variables through indicator or related tables. Coding, rare levels and redundant indicators influence the geometry. It is not ordinary PCA on arbitrary category numbers.

### stat-21-24

**Cluster validation**

Assess within/between separation, stability, external agreement and usefulness. No single internal score defines correct clustering. A method can score well by imposing a convenient geometry unrelated to the decision.

### stat-21-25

**Cluster stability analysis**

Perturb samples or features, refit, and compare partitions after accounting for label permutation. Stable clusters may be robust summaries; instability can reveal weak structure, overlapping groups or arbitrary parameter choices.

### stat-21-26

**Consensus clustering**

Combine multiple partitions through co-assignment or other consensus rules. This can stabilize shared structure but also preserve common biases. State which algorithms, samples and similarity rules contributed to the consensus.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: derive soft mixture membership

Take a one-dimensional two-component Gaussian mixture with equal weights, means minus one and plus one, and unit variances. At \(x=0\) the component likelihoods are equal, giving responsibility .5 for each. At \(x=1\), the plus-one component has log-likelihood advantage two over the minus-one component, so its responsibility is \(\frac{\exp(2)}{1+\exp(2)}\), about .881. The assignment is graded rather than an absolute declaration of category identity.

The EM algorithm alternates these responsibilities with weighted estimates of component means, covariances and mixing weights. Each exact EM step does not decrease the observed-data likelihood, but it can converge to a local optimum. Multiple starts and regularization matter. In an unconstrained Gaussian mixture, a component can collapse onto one point with variance approaching zero, making likelihood arbitrarily large. A covariance floor prevents that numerical degeneracy but adds a modeling constraint.

Information criteria can compare parameterized mixtures, but a chosen component count is not proof of that many natural populations. A skewed single population may require several Gaussian components to approximate its density. Interpret components through stability, external measurements and the decision they support, rather than assigning a name to every fitted Gaussian automatically.

### Case study: a cluster boundary changes with measurement units

Suppose customers have annual spending measured in dollars and support contacts measured as counts. Squared Euclidean distance on raw columns may be dominated by spending because its numerical scale is much larger. Standardizing gives support contacts comparable variance influence, creating a different segmentation. A robust scaling or a domain-specific cost metric could produce a third partition.

There is no purely algorithmic answer to which partition is correct. If the action is assigning service capacity, contacts may be central. If the action is estimating revenue exposure, spending may deserve dominant weight. The representation, distance and objective should follow that purpose. Report how labels change under reasonable scaling and whether the proposed actions remain sensible.

K-means forces every point into one of K compact regions. DBSCAN can identify dense nonconvex regions and leave noise, but one radius may not suit both sparse and dense populations. Hierarchical clustering exposes nested relationships but the linkage rule can create chains or compact groups. Model selection therefore begins with the desired meaning of a cluster, not simply a grid search over whichever method yields the highest silhouette score.

### Case study: a latent factor is a measurement model

Let two observed features satisfy \(x_1=f+\epsilon_1\) and \(x_2=2f+\epsilon_2\), with \(\operatorname{Var}(f)=1\), independent errors, and error variances .5 and two. Their covariance matrix is [[1.5,2],[2,6]]. The shared latent factor accounts for covariance two, while the diagonal contains both shared and feature-specific variation.

PCA seeks a direction explaining total observed variance, including those unequal noise variances. Factor analysis explicitly separates shared covariance from unique noise under its assumptions. A confirmatory model might constrain which indicators load on a construct, while an exploratory model examines alternative loading structures. Rotation and scale choices mean that factor labels require substantive validation, not merely a mathematically convenient solution.

Measurement invariance becomes important when comparing factor scores across groups. If an item or sensor responds differently to the same latent attribute in different populations, observed score differences can mix real attribute differences with measurement differences. A good overall covariance fit can conceal that problem. Use group-aware diagnostics and explain which comparisons the measurement model supports.

### Case study: validating a segmentation used for action

A marketing team finds four attractive customer clusters and proposes four campaigns. Internal separation is only the first evidence layer. Assess whether clusters recur under bootstrap samples, new time periods and modest preprocessing changes. Compare co-assignment or adjusted partition measures because cluster numbers can permute across fits.

Then ask whether campaign response differs in a useful way. The clustering objective never optimized incremental treatment effects, so distinct clusters need not need distinct actions. A randomized campaign evaluation or another credible causal design can test whether segmentation improves net value beyond a simple baseline. If clusters are unstable but actions are stable, a direct policy model may be preferable. If clusters are stable but actions do not differ, the segmentation may be descriptive rather than prescriptive.

For visualization, use t-SNE or UMAP as exploratory views and inspect several parameter settings. Label apparent islands cautiously, check original-space neighborhoods and avoid measuring global distance on the rendered map as though it were calibrated scientific distance. A visually clean figure is an invitation to investigate, not the final validation of latent population categories.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_21.py](../examples/chapter_21.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_21.py
```

### Means and labels have different identities

K-means finds two obvious compact groups and their exact sample means. Cluster labels may swap across initializations, so adjusted Rand agreement compares partitions without relying on label numbers. Perfect agreement on this clear fixture does not imply stability in overlapping real data.

### Density methods can decline assignment

Three nearby points meet the density requirement while a distant point receives label minus one. Unlike k-means with a fixed number of clusters, DBSCAN can mark noise. The threshold is tied to the units of the distance metric.

### A mixture yields probabilistic component membership

Two tightly separated clouds produce means minus 2.8 and plus 2.8 with near-certain component responsibilities. Each row's responsibilities sum to one. These are probabilities under the fitted mixture, not an independent validation that two scientifically real populations exist.

### Complete executable example

```python
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score

def centroids_and_stability():
    x=np.array([[0.,0.],[0.,1.],[1.,0.],[8.,8.],[8.,9.],[9.,8.]])
    first=KMeans(n_clusters=2,n_init=10,random_state=21).fit(x)
    second=KMeans(n_clusters=2,n_init=10,random_state=22).fit(x)
    assert adjusted_rand_score(first.labels_,second.labels_)==1
    expected=np.array([[1/3,1/3],[25/3,25/3]])
    assert np.allclose(first.cluster_centers_[np.argsort(first.cluster_centers_[:,0])],expected)
    print("Centers:",first.cluster_centers_,"seed agreement:",1.)

def density_and_noise():
    x=np.array([[0.,0.],[.1,0.],[0.,.1],[5.,5.]])
    labels=DBSCAN(eps=.2,min_samples=3).fit_predict(x)
    assert np.all(labels[:3]==labels[0]) and labels[-1]==-1
    print("Density labels:",labels)

def mixture_responsibilities():
    x=np.array([[-3.],[-2.8],[-2.6],[2.6],[2.8],[3.]])
    model=GaussianMixture(n_components=2,random_state=21,reg_covar=1e-4).fit(x)
    responsibilities=model.predict_proba(x)
    assert np.allclose(responsibilities.sum(axis=1),1)
    assert np.all(responsibilities.max(axis=1)>.99)
    assert np.allclose(np.sort(model.means_.ravel()),[-2.8,2.8])
    print("Mixture means:",model.means_.ravel(),"minimum maximum responsibility:",responsibilities.max(axis=1).min())

def main():
    centroids_and_stability();density_and_noise();mixture_responsibilities()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: How do you choose the number of clusters?** Combine the intended use, geometric or probabilistic fit, resampling stability and external evidence. Internal scores favor their own geometry. If no stable useful partition exists, report that rather than forcing a segmentation.

**Interview: Why can t-SNE show islands in continuous data?** Its local neighborhood objective and visualization parameters can create apparent gaps while distorting global geometry. Investigate original-space distances, multiple settings and independent evidence before naming discrete populations.

**Interview: How do PCA and factor analysis differ?** PCA summarizes variance through low-rank reconstruction. Factor analysis models shared covariance plus variable-specific noise. The latter adds measurement-model assumptions and identification constraints rather than simply renaming components.

## Primary sources and official APIs

- [scikit-learn clustering methods and evaluation](https://scikit-learn.org/stable/modules/clustering.html).

- [scikit-learn Gaussian mixtures](https://scikit-learn.org/stable/modules/mixture.html).

## Reading connections

[Previous chapter](20-feature-engineering-and-representation-learning.md) | [Book contents](../README.md) | [Next chapter](22-model-validation-and-predictive-performance.md)
