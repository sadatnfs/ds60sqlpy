# 30. Spatial and Spatiotemporal Statistics

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-030`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Spatial statistics starts with the fact that nearby or connected observations may share causes, exposures and measurement errors. A map is not simply a scatterplot with two extra predictors. The definition of neighborhood, spatial support and sampling design changes what can be learned. A point sensor, a census area and an average over a grid cell describe different observational units even at the same coordinates.

### Make the neighborhood explicit

A spatial weights matrix W records which observations influence or are compared with which others. Entries can represent shared borders, distance bands or nearest neighbors. Row normalization changes the scale and interpretation of spatial lags. Islands with no neighbors, asymmetric nearest-neighbor links and distance units need explicit handling. A result obtained under one W is conditional on that definition rather than a universal property of the map.

For centered values z_i=y_i-ybar, global Moran I is n/S0 times (z_transpose*W*z)/(z_transpose*z), where S0 is the sum of all weights. Neighboring similar deviations increase the numerator. Its reference distribution depends on the null and weights; under common randomization assumptions the expectation is -1/(n-1), not automatically zero. Local statistics ask a different multiple-comparison question.

### Distinguish interpolation from causal explanation

Kriging predicts a spatial process from a covariance model and sampled locations. Its uncertainty is conditional on that model, sampling and fitted parameters. A spatial regression relates outcomes to covariates while representing residual or outcome dependence. Neither automatically identifies a causal effect of changing a location-level exposure. Unmeasured spatial confounding and ecological aggregation remain substantive threats.

### Validation must match geographic use

Randomly holding out individual nearby points often creates an easy interpolation test because training sensors surround the held-out sensor. Deployment to a new region is an extrapolation problem and needs spatially separated validation, possibly combined with time blocks. Report distance from test observations to training support and compare performance across geographic regimes. A model that is excellent inside an instrumented city may fail at its boundary.

### A practical case: neighborhood demand

Suppose service calls are aggregated by administrative districts. First distinguish call counts from population-adjusted rates and account for unequal exposure. Map missing reporting separately from true zeros. Explore residual spatial association after known drivers are included, and test sensitivity to district definitions and neighbor matrices. If the intended action targets individual households, district-level associations do not automatically identify household-level effects. Aggregate predictions and uncertainty should respect the support on which the model was fitted.

## Methods, mechanisms, and limits

### stat-30-01

**Spatial autocorrelation**

Spatial autocorrelation is dependence among values at related locations. Positive association often means nearby values are similar, but the relevant relation may be road connectivity or shared borders rather than Euclidean distance. Shared covariates can generate the pattern without direct interaction. Inspect association in both raw outcomes and model residuals, and state the neighborhood matrix and spatial support.

### stat-30-02

**Moran’s I**

Moran I compares cross-products of centered neighboring values with total centered variation, scaled by the weight sum. Its magnitude depends on the weights and does not universally lie between minus one and one. Permutation inference conditions on a specified randomization null. A significant global result says some spatial structure exists under that null, not which locations are responsible or why.

### stat-30-03

**Geary’s C**

Geary C uses squared differences between neighboring values rather than centered cross-products, making it sensitive to local contrasts. Under standard scaling, values below one suggest positive spatial association and above one suggest negative association. The weights, variance estimate and randomization scheme remain consequential. It complements Moran I but is not simply the same statistic with a different name.

### stat-30-04

**Local spatial association statistics**

Local spatial association statistics identify locations contributing to clustering or outlier patterns, such as high-high or high-low configurations. The location's value and its spatial lag both matter. Mapping many local p-values introduces multiplicity and spatial dependence in testing. A highlighted region is a candidate pattern under the chosen neighborhood definition, not a confirmed hotspot mechanism.

### stat-30-05

**Variograms**

A semivariogram describes half the expected squared difference between process values separated by lag h. The nugget, sill and range summarize measurement/microscale variation, long-lag variability and correlation distance in common models. Directional differences indicate anisotropy. Empirical bins have unequal pair counts and dependence, so fitting a smooth variogram is a modeling step with uncertainty, not merely connecting points.

### stat-30-06

**Kriging**

Kriging forms a weighted predictor from sampled values using a covariance or variogram model. Ordinary kriging constrains weights to sum to one when the mean is unknown but constant. Weights need not be positive, and predictions can overshoot observed values. Uncertainty depends on the assumed covariance and parameter estimates; sparse spatial support and misspecification can make nominal kriging variance optimistic.

### stat-30-07

**Gaussian random fields**

A Gaussian random field specifies jointly Gaussian values over locations with a mean function and covariance kernel. The kernel encodes smoothness, correlation length and possibly anisotropy. Positive definiteness is required for a valid joint distribution. Gaussian assumptions simplify conditioning but may poorly represent heavy tails, sharp boundaries or constrained outcomes without transformation or a hierarchical observation model.

### stat-30-08

**Conditional autoregressive models**

Conditional autoregressive models specify each area's distribution conditional on neighboring areas, often creating a sparse precision matrix. They are useful for areal smoothing and hierarchical disease or demand models. Intrinsic versions can be improper without constraints, and the adjacency graph controls borrowing. A smoothed map can conceal abrupt real boundaries if the neighborhood prior is too strong.

### stat-30-09

**Simultaneous autoregressive models**

Simultaneous autoregressive models define a joint relation involving a spatial weight matrix, with dependence induced through an inverse such as (I-rho*W)^(-1). Parameter restrictions ensure the system is well defined. Different placements of the spatial term yield different interpretations. The same numerical rho means little without the normalization and spectrum of W.

### stat-30-10

**Spatial lag models**

A spatial lag model includes neighboring outcomes through y=rho*W*y+X*beta+epsilon. Because y appears on both sides, ordinary least squares generally does not estimate the model correctly. A covariate change can propagate through the spatial multiplier, so beta alone is not the total marginal effect. Distinguish direct, indirect and total impacts under the specified model.

### stat-30-11

**Spatial error models**

A spatial error model places dependence in unobserved disturbances, such as epsilon=lambda*W*epsilon+u. It addresses residual covariance rather than explicitly modeling outcome spillovers. Similar-looking fit improvements can therefore imply different substantive stories. Choosing spatial error over spatial lag should involve mechanism and diagnostics, not only whichever coefficient is significant.

### stat-30-12

**Geographically weighted regression**

Geographically weighted regression estimates local coefficients using distance-weighted nearby observations. Bandwidth governs the bias-variance tradeoff and can make local estimates highly unstable where support is sparse. Correlated covariates and multiple local fits complicate interpretation. A coefficient map suggests spatial heterogeneity under the smoothing design; it does not by itself prove distinct causal effects in each neighborhood.

### stat-30-13

**Spatial point processes**

Spatial point processes model random event locations and sometimes marks such as severity. Intensity describes expected events per unit area, while interaction describes attraction or inhibition beyond intensity variation. A homogeneous Poisson process assumes constant intensity and independent counts in disjoint regions. A clustered map may reflect varying exposure rather than event-to-event attraction.

### stat-30-14

**Log-Gaussian Cox processes**

A log-Gaussian Cox process lets point-process intensity equal exp(Z(s)) for a latent Gaussian field Z. This creates flexible positive intensity and clustering through latent spatial variation. Fitting must separate covariate-driven exposure from unexplained field structure and account for observation windows. Fine grids or numerical approximations can be expensive and influence inferred small-scale patterns.

### stat-30-15

**Spatial scan statistics**

Spatial scan statistics compare candidate regions with an outside reference to detect unusually high or low event rates. The scan searches many overlapping windows, so the null calibration must include that search. Population denominators, window size limits and shape assumptions affect findings. A detected region is a statistical cluster, and causal investigation requires additional evidence.

### stat-30-16

**Geostatistics**

Geostatistics studies spatially continuous processes, emphasizing covariance, variograms and interpolation from sampled locations. Sampling design and measurement support determine what the observations represent. Preferential sampling, where sensors are placed because values are expected to be extreme, can bias naive inference. A mathematically smooth prediction surface should not hide unsampled gaps or claim resolution unsupported by the data.

### stat-30-17

**Small-area estimation**

Small-area estimation borrows information across areas to improve estimates where direct samples are sparse. Models combine survey/design information, auxiliary covariates and area-level or unit-level effects. Shrinkage reduces variance but introduces model dependence and can pull unusual areas toward a common pattern. Report model-based uncertainty and benchmark constraints when estimates must agree with trusted aggregate totals.

### stat-30-18

**Spatiotemporal models**

Spatiotemporal models combine location and time dependence, possibly through separable covariance, dynamic spatial fields or transition models. A separable kernel assumes a particular interaction structure and may miss moving fronts or changing correlation ranges. Validation should hold out future periods and new locations as appropriate. Time-varying coverage and sensor replacement can masquerade as process dynamics.

### stat-30-19

**Modifiable areal unit problem**

The modifiable areal unit problem means statistical summaries and associations change when spatial observations are aggregated using different boundaries or scales. Both zoning and scale matter. A district correlation can reverse or disappear under another valid partition without any individual value changing. Align the unit with the decision and conduct sensitivity analysis rather than treating administrative boundaries as neutral.

### stat-30-20

**Spatial confounding**

Spatial confounding occurs when an exposure and unmeasured spatial processes vary together, making their effects hard to separate. Adding a flexible spatial random effect can also compete with the exposure for the same variation. Model adjustment does not automatically identify a causal exposure effect. State the estimand, sampling support and identifying assumptions, and examine sensitivity to spatial scale and prior structure.

## Worked Python demonstrations

Complete offline program: [chapter_30.py](../examples/chapter_30.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_30.py
```

### See the neighborhood enter the statistic

Four values [1,1,3,3] lie on a chain with adjacent undirected links. Centering gives [-1,-1,1,1]. The weighted cross-product is two, total squared deviation four, and the weight sum six, giving Moran I=(4/6)*(2/4)=1/3. Changing the links changes the statistic even though the observations remain identical.

### Solve a tiny ordinary-kriging system

Sensors at zero and two observe one and three. With a symmetric exponential covariance and target one, the unbiasedness-constrained system gives weights one-half each and prediction two. The appended row enforces weights summing to one; the last unknown is a Lagrange multiplier. The printed variance is conditional on the chosen covariance, not an empirical guarantee.

### Change boundaries without changing people

Grouping adjacent values produces area means [1,3], while mixing one low and one high value in each area produces [2,2]. Both preserve the grand mean two, but the apparent between-area inequality disappears under the second partition. This is a concrete support effect, not a coding error.

### Complete executable example

```python
import numpy as np

def moran_and_variogram():
    y=np.array([1.,1.,3.,3.]);w=np.zeros((4,4))
    for i in range(3):w[i,i+1]=w[i+1,i]=1.
    z=y-y.mean();moran=len(y)/w.sum()*(z@w@z)/(z@z)
    semivariance=.5*np.mean(np.diff(y)**2)
    assert np.isclose(moran,1/3) and np.isclose(semivariance,2/3)
    print("Chain Moran I:",moran,"lag-one semivariance:",semivariance)

def ordinary_kriging():
    locations=np.array([0.,2.]);target=1.;observed=np.array([1.,3.])
    covariance=np.exp(-np.abs(locations[:,None]-locations[None,:]))
    k=np.exp(-np.abs(locations-target))
    system=np.block([[covariance,np.ones((2,1))],[np.ones((1,2)),np.zeros((1,1))]])
    solution=np.linalg.solve(system,np.r_[k,1.]);weights=solution[:2]
    prediction=weights@observed
    variance=1-weights@k-solution[2]
    assert np.allclose(weights,[.5,.5]) and np.isclose(prediction,2.) and variance>0
    print("Kriging weights, prediction, conditional variance:",weights,prediction,variance)

def aggregation_support():
    individual=np.array([1.,1.,3.,3.])
    neighboring=np.array([individual[:2].mean(),individual[2:].mean()])
    mixed=np.array([individual[[0,2]].mean(),individual[[1,3]].mean()])
    assert neighboring.tolist()==[1.,3.] and mixed.tolist()==[2.,2.]
    assert neighboring.mean()==mixed.mean()==2.
    print("Two boundary choices:",neighboring,mixed,"same global mean")

def main():
    moran_and_variogram();ordinary_kriging();aggregation_support()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Why is random row validation often optimistic for spatial models?** Nearby training points can reveal almost the same latent field as a held-out point. If deployment targets a new region, block or distance-separated validation better matches the information gap. Report the geographic support rather than only a score.

**Interview: Can a significant Moran statistic explain the cause of clustering?** No. It describes association under a chosen weights matrix and null model. Shared exposures, sampling, boundaries and direct interactions can all create the pattern. Explanation requires covariates, design and substantive evidence.

**Interview: Why can a kriging prediction be outside the observed range?** Kriging weights satisfy covariance and unbiasedness conditions, not necessarily positivity. Overshoot can be mathematically consistent with the model. Whether it is acceptable depends on support constraints, covariance fit and the application.

## Primary sources and official APIs

- [PySAL spatial exploratory-analysis API](https://pysal.org/esda/stable/api.html)

- [PySAL spatial autocorrelation user guide](https://pysal.org/esda/stable/user-guide/index.html)

## Reading connections

[Previous chapter](29-anomaly-detection-changepoints-and-statistical-process-control.md) | [Book contents](../README.md) | [Next chapter](31-network-and-graph-analysis.md)
