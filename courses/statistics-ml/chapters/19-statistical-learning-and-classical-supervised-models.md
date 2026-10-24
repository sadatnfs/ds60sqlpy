# 19. Statistical Learning and Classical Supervised Models

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-019`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Supervised learning maps observed features to an unknown outcome using examples where the outcome is known. Empirical risk is average training loss. Generalization is performance on the deployment distribution, which is not guaranteed by minimizing training loss. Model selection therefore combines the structure of the data, sample size, feature availability, computational cost and independent evaluation.

### Trees and random forests from first principles

A regression tree chooses a feature and threshold that reduce within-leaf squared error. Each leaf predicts its training outcome mean. A classification tree similarly reduces an impurity such as Gini, \(1-\sum_k p_k^2\), or entropy. Trees handle nonlinearities and interactions without requiring a linear predictor, but greedy early splits can change dramatically after small data perturbations. Depth and minimum leaf size control local complexity.

Bagging averages trees fitted to bootstrap samples. If B tree errors have variance \({\sigma}^{2}\) and common correlation rho, their average has variance \(\sigma^2\left[\rho+\frac{1-\rho}{B}\right]\). More trees reduce the uncorrelated part, but the correlated part remains. Random forests additionally sample candidate features at splits to reduce correlation, possibly weakening individual trees. Tune leaf size, feature sampling and depth using appropriate validation; adding trees mainly stabilizes the ensemble. Out-of-bag evaluation reuses bootstrap exclusion, but does not repair temporal or group leakage.

### Gradient boosting and XGBoost

Boosting constructs \(F_m(x)=F_{m-1}(x)+\eta h_m(x)\), where h_m approximates the negative gradient of the loss with respect to current predictions. For half squared error, that gradient is the residual y-F. Small learning rates and limited tree complexity spread improvement across stages. For classification, updates occur on a score such as log odds, not by simply adding probabilities. Early stopping must monitor data separate from final evaluation.

XGBoost is a particular regularized tree-boosting system. Its second-order local objective uses first derivatives g_i and second derivatives h_i. A leaf with summed derivatives G,H and L2 penalty lambda has optimal weight \(\frac{-G}{H+\lambda}\). A candidate split compares the regularized scores of its children with the parent and subtracts a leaf-complexity cost. This explains why tiny low-information leaves are penalized. Missing-value routing, sampling, histogram approximations and implementation choices affect behavior. The book demonstrates this objective with NumPy; the optional `xgboost` package is not required or imported.

### Choose a model through failure modes

Nearest neighbors need a meaningful scaled distance and degrade in high dimensions. Naive Bayes can classify effectively despite imperfect independence but may produce extreme uncalibrated probabilities. Margin methods need kernel and scaling choices. Tree ensembles are strong tabular baselines but usually extrapolate poorly beyond trained feature ranges. Neural and transfer models can exploit richer representations while increasing optimization and distribution-shift risks. Start with an honest simple baseline and use measured incremental value to justify complexity.

## Methods, mechanisms, and limits

### stat-19-01

**Empirical risk minimization**

Minimize average observed loss over a model class. Training improvement can reflect memorization, so the risk target must be evaluated separately. Sampling and label availability define whose errors the objective actually emphasizes.

### stat-19-02

**Regularized risk minimization**

Add a complexity penalty to training loss or constrain the model class. Regularization trades some fit for stability. Its strength depends on feature scale, sample size and the loss normalization used by the implementation.

### stat-19-03

**Bias–variance tradeoff**

For squared loss, prediction error decomposes into irreducible noise, squared bias and variance under a specified sampling setup. More flexible models often reduce bias while increasing variability, but the pattern is not universally monotonic.

### stat-19-04

**Overfitting**

A model captures sample-specific noise or leakage and performs worse on relevant unseen data. Diagnose through honest validation, learning curves and duplicate/group checks. A train-test gap alone does not identify which mechanism caused it.

### stat-19-05

**Underfitting**

A model cannot represent useful signal or is constrained too strongly. Both training and validation loss may remain high. Better features or appropriate flexibility help only after ruling out noisy targets and misaligned loss.

### stat-19-06

**Nearest-neighbor methods**

Predict from nearby training observations under a chosen metric. Standardization, irrelevant dimensions and neighborhood size strongly affect results. Local support is essential; distance does not establish causal similarity.

### stat-19-07

**Naive Bayes**

Factorize feature likelihoods conditionally on class and combine them with class priors. Violated dependence can double-count evidence and distort probabilities. Classification ranking may remain useful despite that mismatch.

### stat-19-08

**Linear discriminant analysis**

Assume Gaussian class distributions sharing a covariance matrix, yielding linear boundaries. Covariance estimation becomes unstable with many features relative to samples. Scaling and shrinkage can affect robustness.

### stat-19-09

**Quadratic discriminant analysis**

Allow class-specific Gaussian covariance matrices, yielding quadratic boundaries. This increases flexibility and parameter count. Sparse classes may have singular or poorly estimated covariance and need regularization.

### stat-19-10

**Decision trees**

Recursively split predictors to improve a loss or impurity criterion. Leaves summarize training outcomes. Greedy splitting is unstable and can overfit small leaves; impurity importance favors variables with many possible splits.

### stat-19-11

**Bagging**

Average base learners trained on bootstrap resamples. It especially helps unstable estimators such as trees. Highly correlated base errors limit the variance reduction available from additional members.

### stat-19-12

**Random forests**

Combine bootstrap sampling and randomized candidate features to diversify trees. Evaluate grouped or temporal data with matching splits. Forest predictions are averages of local training responses and are poor at unconstrained extrapolation.

### stat-19-13

**Extremely randomized trees**

Randomize split thresholds more strongly, often across the whole training sample by default. Extra randomness can reduce variance but increase bias. Implementation sampling defaults differ from a conventional random forest.

### stat-19-14

**Gradient boosting**

Fit weak learners to negative loss gradients and add shrunken updates. The loss determines the residual-like target. Learning rate, stage count and learner complexity interact and require joint validation.

### stat-19-15

**Boosted decision trees**

Use shallow or regularized trees as additive boosting components. They capture interactions through repeated partitions. Tree depth limits each component's interaction structure; the number of stages controls aggregate flexibility.

### stat-19-16

**AdaBoost**

Increase emphasis on misclassified cases through sequential weighting or additive exponential-loss fitting. Mislabeled outliers can receive excessive attention. Learning rate and base learner complexity affect both robustness and margin behavior.

### stat-19-17

**Support vector machines**

Optimize a margin-based objective with slack penalties, optionally in a kernel feature space. Scale features and tune regularization carefully. Margin scores are not calibrated probabilities without additional estimation.

### stat-19-18

**Kernel methods**

Replace explicit feature products with a positive-semidefinite similarity function. Kernel choice encodes smoothness and geometry. A similarity matrix that is not a valid kernel may violate the intended optimization assumptions.

### stat-19-19

**Kernel ridge regression**

Solve squared-error regression with L2 regularization in a kernel space. It can model nonlinear smooth relationships but standard exact fitting requires a dense sample-by-sample matrix, limiting large-data scalability.

### stat-19-20

**Gaussian process regression**

Condition a kernel-defined Gaussian prior on observed outcomes to obtain mean and covariance predictions. Noise and kernel assumptions determine uncertainty; optimized hyperparameters alone do not guarantee calibrated intervals.

### stat-19-21

**Multilayer perceptrons**

Compose affine transformations and nonlinear activations, optimized by gradient methods. Scaling, architecture and regularization matter. Convergence warnings, seed sensitivity and limited tabular data can make a simpler baseline preferable.

### stat-19-22

**Multitask learning**

Share parameters or representations across related tasks. Transfer helps when shared structure is real and can hurt when tasks conflict. Measure each task's performance rather than only a pooled average.

### stat-19-23

**Multioutput learning**

Predict several outcomes with a shared model or coordinated estimators. Joint modeling can exploit dependence, but a wrapper fitting independent models does not necessarily learn cross-output structure.

### stat-19-24

**Learning to rank**

Optimize order-related losses across query-specific candidates. Group queries in validation and evaluate position-sensitive utility. A low pointwise regression loss does not guarantee the correct ordering of important pairs.

### stat-19-25

**Cost-sensitive learning**

Weight errors or training observations according to consequences. Altered class weights can change probability interpretation. Separate learning a risk score from choosing an operational threshold where feasible.

### stat-19-26

**Positive–unlabeled learning**

Learn with confirmed positives and unlabeled cases containing both classes. Identification depends on how positives become labeled or on class-prior information. Treating every unlabeled case as negative can bias the model.

### stat-19-27

**Semi-supervised learning**

Use unlabeled data with assumptions connecting feature structure to labels, such as cluster smoothness. Unlabeled examples can hurt when that assumption is wrong or their distribution differs from the labeled target population.

### stat-19-28

**Active learning**

Select observations for labeling to reduce useful uncertainty. Log the acquisition mechanism and evaluate on representative data. Focusing exclusively on uncertain cases can miss unexplored regions and distort ordinary evaluation.

### stat-19-29

**Transfer learning**

Reuse a representation or parameters from a source task, then adapt or evaluate on the target. Shared appearance does not guarantee transferable mechanisms. Negative transfer and source-data leakage need explicit checks.

### stat-19-30

**Domain adaptation**

Adjust learning across source and target distributions under a stated shift assumption. Covariate reweighting presumes a stable conditional outcome mechanism and overlap; it cannot fix arbitrary concept change.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: derive the bias-variance tradeoff at one input

Fix a deployment input x and write its future outcome as \(Y=f(x)+\epsilon\), with mean-zero noise independent of the training sample. Different possible training samples produce different fitted predictions f_hat(x). Expanding \(\mathbb{E}[(Y-\widehat{f}(x))^2]\) gives \(\operatorname{Var}(\epsilon)+\bigl[\mathbb{E}[\widehat{f}(x)]-f(x)\bigr]^2+\operatorname{Var}(\widehat{f}(x))\). The cross terms vanish under these assumptions. The decomposition concerns repeated training samples and squared loss at a fixed input, not three numbers that can be read directly from one train-test split.

A shallow tree can have high approximation bias if the response changes smoothly in several dimensions. A deep tree can track local detail but vary substantially when a few training rows change. Bagging primarily addresses that instability. Regularization or a simpler model can reduce variability even while increasing bias. If the labels are systematically wrong, however, the apparent irreducible error term is conditional on that measurement process and should not be treated as a law of nature.

Learning curves help distinguish some practical patterns. If training loss is tiny and validation loss improves with more independent data, variance may be limiting. If both are poor, feature quality or model capacity may be limiting. If random splits look excellent but future splits fail, distribution change or leakage may dominate. These are diagnostic hypotheses, not one-to-one interpretations of curve shape.

### Case study: why feature randomness helps a forest

Suppose one strong predictor dominates every tree's first split. Bootstrap samples differ, but nearly every tree builds a similar structure and makes similar mistakes in the same region. Averaging many nearly identical errors gives little variance reduction. Restricting candidate features at each split forces some trees to explore alternative predictors, reducing error correlation at a possible cost to individual tree strength.

This tradeoff explains why the feature-sampling parameter is not merely a speed setting. Too few candidates can make trees weak when only a few features contain signal; too many can make them strongly correlated. Minimum leaf size controls how local a response average becomes, while the number of trees stabilizes the average of the chosen base-learning procedure. A forest with thousands of trees can remain biased, leaked or poorly calibrated.

Out-of-bag prediction uses trees that did not bootstrap-sample a particular row. That gives convenient internal evaluation for appropriately independent rows, but related rows can still appear in a tree's training sample. A patient's other visits or a customer's duplicated record can leak information into its out-of-bag prediction. Use grouped or temporal external validation for the actual deployment task, even if the out-of-bag score looks reassuring.

Impurity-based importance accumulates training split improvements and can favor variables with many candidate splits. Held-out permutation importance asks a different question: how much predictive performance suffers when one feature is disrupted. Correlated alternatives, unrealistic perturbations and subgroup differences complicate both. Importance should explain model reliance, not be relabeled as causal effect.

### Case study: one boosting split and its regularization cost

For half squared error, \(g_i=\widehat{y}_i-y_i\) and \(h_{i}=1\). Suppose a parent leaf contains residual gradients summing to zero, while a candidate split creates children with G_L=-6,H_L=3 and G_R=6,H_R=3. With \(\lambda=1\), optimal child weights are +1.5 and -1.5. The parent weight is zero. The second-order improvement before a split penalty is one-half times \([\frac{36}{4}+\frac{36}{4}-\frac{0}{7}]\), or nine.

If the leaf-complexity penalty gamma exceeds nine, the split is not worthwhile under this local objective. If gamma is smaller, the split may be accepted, then the learning rate further shrinks its contribution to the ensemble. This makes the regularization parameters concrete: lambda shrinks leaf magnitudes and gamma discourages additional leaves. They are not substitutes for independent validation or a correct loss.

For logistic loss, \(h_i=p_i(1-p_i)\), so confident predictions can have small curvature. Newton-style updates must be controlled when curvature is tiny or labels are unusual. Real implementations include further constraints and numerical safeguards. The compact formula teaches the optimization mechanism without claiming that a few NumPy lines reproduce XGBoost's full training system.

### Case study: choose between linear, tree and kernel baselines

A tabular problem with mostly additive smooth effects may be served well by regularized regression or a GAM. A tree ensemble can capture thresholds and interactions with less feature construction, but its predictions outside observed ranges are usually piecewise constant. A kernel method can provide smooth nonlinear behavior but may require costly sample-by-sample matrices and careful scaling. These are structural differences, not a universal ranking.

Compare the candidates under the same data boundary, tuning budget and decision metric. Fit imputation and scaling inside each relevant pipeline, use the same held-out customers or dates, and include a simple constant or historical baseline. Inspect where the winner improves: common cases, rare failures, new entities or only noisy corners. A tiny aggregate gain may not justify added latency, complexity or loss of interpretability.

For transfer learning and semi-supervised methods, document the source of extra information. Unlabeled data can hurt if the assumed cluster structure does not align with labels, and a pretrained representation can carry evaluation contamination or a mismatched domain. An active-learning acquisition policy changes the distribution of labeled examples. Keep a representative evaluation set whose selection process does not reward the model for choosing easy or favorable labels.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_19.py](../examples/chapter_19.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_19.py
```

### A tree searches for useful partitions

Six points form two constant outcome regions. A depth-one tree chooses threshold 2.5 and predicts both regions exactly. This illustrates squared-error reduction without implying a one-split tree can generalize every dataset or infer a causal threshold.

### Averaging cannot remove shared error

The forest correctly predicts the two obvious regions of a tiny deterministic step function. Separately, the variance formula with \(\rho=0.3\) and sigma-squared four decreases from 1.48 at ten members to 1.228 at 100, approaching a floor of 1.2. Feature randomization seeks to lower that correlation floor.

### Boost residuals, not labels repeatedly

The initial mean prediction is three everywhere with MSE nine. A stump fits residuals minus three and plus three; adding half the fitted residual reduces MSE to 2.25. The learning rate deliberately takes a smaller corrective step.

### Understand a regularized boosting leaf

Summed gradients minus three, summed Hessians two and lambda one imply leaf weight one. The code checks that the local objective decreases and its derivative vanishes. This is the mathematical core of a Newton-style leaf update, not a reimplementation of the complete XGBoost library.

### Complete executable example

```python
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor


def split_geometry():
    x = np.arange(6, dtype=float)[:, None]
    y = np.array([0.0, 0.0, 0.0, 6.0, 6.0, 6.0])
    stump = DecisionTreeRegressor(max_depth=1, random_state=19).fit(x, y)
    assert np.allclose(stump.predict(x), y)
    assert np.isclose(stump.tree_.threshold[0], 2.5)
    print(
        "Stump split:",
        stump.tree_.threshold[0],
        "training MSE:",
        np.mean((stump.predict(x) - y) ** 2),
    )


def forest_and_variance():
    x = np.linspace(0, 1, 80)[:, None]
    y = np.where(x[:, 0] < 0.5, 0.0, 2.0)
    forest = RandomForestRegressor(n_estimators=40, max_depth=3, random_state=19, n_jobs=1).fit(
        x, y
    )
    predictions = forest.predict([[0.1], [0.9]])
    assert np.allclose(predictions, [0.0, 2.0])
    rho, sigma2 = 0.3, 4.0
    variance = lambda b: sigma2 * (rho + (1 - rho) / b)
    assert variance(100) < variance(10) and variance(100) > rho * sigma2
    print(
        "Forest predictions:",
        predictions,
        "ensemble variance B10/B100:",
        variance(10),
        variance(100),
    )


def boosting_update():
    x = np.arange(6, dtype=float)[:, None]
    y = np.array([0.0, 0.0, 0.0, 6.0, 6.0, 6.0])
    current = np.full(len(y), y.mean())
    residual = y - current
    tree = DecisionTreeRegressor(max_depth=1, random_state=19).fit(x, residual)
    updated = current + 0.5 * tree.predict(x)
    before = np.mean((y - current) ** 2)
    after = np.mean((y - updated) ** 2)
    assert before == 9 and after == 2.25
    print("One half-step boosting MSE:", before, "to", after)


def second_order_leaf():
    g = np.array([-2.0, -1.0])
    h = np.ones(2)
    penalty = 1.0
    weight = -g.sum() / (h.sum() + penalty)
    objective = lambda w: g.sum() * w + 0.5 * (h.sum() + penalty) * w * w
    assert weight == 1 and objective(weight) < objective(0)
    assert np.isclose(g.sum() + (h.sum() + penalty) * weight, 0)
    print("Regularized Newton leaf weight:", weight)


def main():
    split_geometry()
    forest_and_variance()
    boosting_update()
    second_order_leaf()


if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Why does a random forest usually improve on one deep tree?** Averaging reduces instability when trees make partly different errors. Bootstrap samples and feature subsampling encourage that diversity. Correlated error remains, so more trees cannot fix missing signal, leakage or a wrong target.

**Interview: How does boosting differ from bagging?** Bagging trains perturbed models largely independently and averages them. Boosting adds models sequentially to improve a current loss, using gradients or related reweighting. Its stage count and learning rate form an optimization and regularization tradeoff.

**Interview: What distinguishes XGBoost from generic gradient boosting?** It is a particular system combining regularized tree objectives, derivative-based split and leaf calculations, and scalable implementation strategies. Naming the package is not a model-selection argument; compare it with simpler baselines on the deployment split.

**Interview: Can a forest extrapolate a rising trend beyond training values?** Standard regression-tree leaves average observed outcomes, so predictions typically flatten outside learned partitions. A linear or structured trend model may extrapolate more coherently when that scientific assumption is defensible.

## Primary sources and official APIs

- [scikit-learn ensemble methods](https://scikit-learn.org/stable/modules/ensemble.html).

- [Chen and Guestrin, XGBoost: A Scalable Tree Boosting System](https://arxiv.org/abs/1603.02754).

- [XGBoost objective and boosted-tree tutorial](https://xgboost.readthedocs.io/en/stable/tutorials/model.html).

## Reading connections

[Previous chapter](18-bayesian-statistics-and-probabilistic-modeling.md) | [Book contents](../README.md) | [Next chapter](20-feature-engineering-and-representation-learning.md)
