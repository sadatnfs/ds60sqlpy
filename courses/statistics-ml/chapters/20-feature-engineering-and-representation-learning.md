# 20. Feature Engineering and Representation Learning

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-020`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

A feature is a measurement available when a decision is made. Its transformation may change numerical conditioning, model assumptions and leakage risk. Fit preprocessing on training data, apply the fitted transformation to held-out data, and keep all learned preprocessing inside the validation pipeline. A correct transformation applied at the wrong time is still leakage.

### Derive PCA as reconstruction

Center X by subtracting training column means and compute \(X=U\Sigma V^{\mathsf T}\). The first k right singular vectors form loading directions V_k; scores are X V_k. Reconstruct with scores times V_k-transpose and add the training means. This minimizes squared reconstruction error among rank-k linear approximations. Explained variances are \(\frac{s_j^2}{n-1}\), so retained variance ratios follow directly from singular values.

PCA maximizes variance, not predictive value, independence or causal relevance. A low-variance feature can strongly predict the target. Raw-unit PCA lets large-scale features dominate; standardized PCA answers a correlation-scale question instead. Component signs are arbitrary, and nearly tied singular values make individual directions unstable even when the subspace is stable. Select dimension inside the training process and evaluate the downstream task.

### Encoding and temporal availability

One-hot encoding preserves nominal categories without inventing order. Target encoding replaces a category with an outcome summary, but using each row's own label can leak almost the entire target for rare categories. Cross-fitted encodings and smoothing toward a training prior reduce this problem. Rolling features must use only values available before the prediction timestamp; a centered window or same-day final total can expose future information.

Representations should be judged by downstream usefulness and stability, not merely attractive geometry. Reconstruction can preserve nuisance variation, and contrastive objectives can amplify whatever the positive/negative pairing policy defines. The data construction is part of the model.

## Methods, mechanisms, and limits

### stat-20-01

**Scaling and standardization**

Standardization subtracts a training mean and divides by a training scale. It helps distance and penalized methods; it does not make a distribution normal. Preserve fitted parameters and handle zero-variance columns explicitly.

### stat-20-02

**Categorical encoding**

One-hot, ordinal and other encodings impose different structures. Choose ordinal codes only when ordering is meaningful. Handle unseen categories through a declared policy rather than refitting preprocessing on evaluation data.

### stat-20-03

**Target encoding**

Estimate category outcome summaries using only training information appropriate to each row. Smoothing and cross-fitting control rare-category leakage. Evaluation labels must never influence category statistics.

### stat-20-04

**Feature hashing**

Map feature names into a fixed number of buckets, often with signed contributions. Hashing bounds memory and handles new categories, but collisions mix signals and make direct feature interpretation harder.

### stat-20-05

**Interaction feature construction**

Create products or joint indicators to represent combined effects. The number of interactions grows rapidly. Domain-guided construction and regularization help avoid sparse accidental patterns and unstable interpretation.

### stat-20-06

**Temporal feature engineering**

Construct lagged, rolling and recency features from point-in-time available history. Distinguish event time from ingestion time and define window boundaries. A future-corrected record is not automatically historically available.

### stat-20-07

**Feature selection**

Select features within each training fold so evaluation remains independent. Selection can improve stability and cost but may discard weak joint signals. Include the selection procedure in model comparison.

### stat-20-08

**Filter methods**

Rank features using marginal statistics such as association or mutual information. This is cheap but can miss interaction-only predictors and retain redundant ones. Fit thresholds without using the final test labels.

### stat-20-09

**Wrapper methods**

Search feature subsets by repeatedly fitting the predictive model. This accounts for model interactions but is computationally expensive and prone to selection overfitting without nested validation.

### stat-20-10

**Embedded selection**

Use model fitting itself to select or downweight features, such as L1 penalties. Selection depends on scaling, regularization and correlated alternatives. A zero coefficient does not establish scientific irrelevance.

### stat-20-11

**Mutual information**

Mutual information is the expected log ratio of joint to product-marginal densities. It detects more than linear dependence but requires careful estimation, especially for continuous high-dimensional variables and small samples.

### stat-20-12

**Principal component analysis**

Project centered data onto directions of maximum variance using eigenvectors or SVD. Choose scaling and retained dimensions intentionally. High explained variance does not guarantee retaining the features needed for prediction.

### stat-20-13

**Independent component analysis**

Recover statistically independent components under assumptions such as linear mixing and non-Gaussian sources. Scale and permutation are not identified. Independence is stronger than PCA's uncorrelatedness.

### stat-20-14

**Nonnegative matrix factorization**

Factor a nonnegative matrix into nonnegative basis and coefficient matrices. This encourages additive parts, often useful for counts or intensities. Factorization remains nonunique and can converge to local optima.

### stat-20-15

**Sparse coding**

Represent observations with sparse coefficients over a dictionary. The sparsity penalty controls reconstruction-complexity tradeoffs. Different dictionaries can explain the same data, limiting literal component interpretation.

### stat-20-16

**Dictionary learning**

Learn reusable basis elements jointly with representation coefficients. Overcomplete dictionaries can model rich structure but need constraints and regularization. Evaluate stability rather than assuming every learned atom is meaningful.

### stat-20-17

**Autoencoders**

Train an encoder and decoder to reconstruct inputs through a bottleneck or regularization. A powerful decoder can learn nuisance detail; good reconstruction does not guarantee task-relevant or causal representations.

### stat-20-18

**Contrastive learning**

Bring designated positive pairs closer relative to negatives under a contrastive objective. Augmentations and negative sampling define invariances and possible biases. False negatives can push semantically similar observations apart.

### stat-20-19

**Metric learning**

Learn a distance using pair or triplet supervision. The supervision must reflect useful similarity for deployment. A metric can overfit identities or groups and fail under new acquisition conditions.

### stat-20-20

**Embeddings**

Map entities into vectors through a chosen learning objective. Distance and arithmetic properties depend on that objective and training data. Embedding proximity is not an intrinsic scientific relationship.

### stat-20-21

**Feature stability analysis**

Repeat selection or representation fitting under resampling and compare retained features or aligned subspaces. Low stability can expose correlated alternatives or insufficient data. Stable features can still be systematically biased.

### stat-20-22

**Representation leakage analysis**

Probe whether representations encode labels, future information or sensitive identities unavailable or inappropriate at deployment. A downstream train-test split cannot repair representations trained with leaked evaluation information.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: derive the first principal component numerically

For rows (1,2),(2,4),(3,6),(4,8), the column means are (2.5,5). The sample covariance is \([[\frac{5}{3},\frac{10}{3}],[\frac{10}{3},\frac{20}{3}]]\). Its trace is \(\frac{25}{3}\), the total sample variance. The vector \(\frac{(1,2)}{\sqrt{5}}\) is an eigenvector with eigenvalue \(\frac{25}{3}\), and its orthogonal direction has eigenvalue zero. Every centered observation lies on the first direction, so one component reconstructs the data exactly.

The loading vector tells how original coordinates combine into a component. The score is each row's projection onto that direction. A sign-flipped loading and sign-flipped scores reconstruct the same matrix, so component signs have no intrinsic meaning. With two nearly equal eigenvalues, even orientations within their shared subspace can rotate substantially across samples. Compare subspaces or align components before interpreting instability as a changed phenomenon.

If the second column's units are changed from meters to millimeters, its raw variance grows by a million and raw PCA changes accordingly. Standardizing both columns uses a correlation-scale geometry instead. Neither is automatically correct: raw-unit PCA might be appropriate if physical magnitude defines reconstruction cost, while standardized PCA gives each variable equal initial variance. State the loss implicit in the scaling decision.

### Case study: high explained variance can discard the target

Imagine one feature with large random variation unrelated to the outcome and another with tiny variation that almost perfectly determines the outcome. PCA ranks the first feature highly because it explains input variance. A one-component representation can therefore preserve nearly all input variance while destroying most predictive information.

Selecting the number of components by a variance threshold is a compression rule, not a supervised performance guarantee. If prediction is the goal, tune the PCA-plus-model pipeline inside development validation. Partial least squares uses outcome relationships when constructing components, but that makes leakage prevention even more important. Fit every supervised transformation using only the appropriate training labels.

Feature selection has the same selection-boundary issue. A univariate correlation screen performed before cross-validation has already used held-out labels, even if the downstream regression is fit separately in every fold. Nested validation must include the screen, transformation and model choice. An apparently harmless feature-engineering notebook can be the true source of a surprisingly high model score.

### Case study: rare categories and target encoding

A category with 100 observations provides a more stable outcome mean than a category with one. A simple smoothed encoding is (sum of category outcomes + lambda*global_mean)/(category_count+lambda). Lambda controls shrinkage toward the training population mean. This addresses variance, but if a row contributes its own label to its encoding, direct leakage remains, especially when category_count is small.

Use fold-wise encodings for training rows, fitting category summaries on other folds, then fit a final encoder on all training data for future observations. Keep customer or time groups intact when constructing folds. New categories need an explicit fallback, often the training global mean or a hierarchical parent category. Do not recompute encodings from validation or test labels to avoid missing-category errors.

The target statistic itself may drift. A product category's historical conversion rate can change after a pricing intervention, and a category name can indirectly identify a customer or event. Check point-in-time correctness and label availability. Cross-fitting prevents one form of leakage but does not turn an unstable behavioral summary into a timeless feature.

### Case study: embeddings for semantic retrieval

A text embedding maps a document or query to a vector learned under a representation objective. Cosine similarity can support candidate retrieval for a subject-matter assistant, but similarity is not factual entailment. A passage that shares vocabulary may contradict the requested claim, describe an obsolete version or refer to a different entity. Retrieval quality must be measured with relevant judgments and downstream answer support.

For supervised classification, frozen embeddings can be a useful baseline before fine-tuning a large model. Split documents by source, author, customer or time where those relationships matter, and remove near duplicates across boundaries. A representation trained on the evaluation corpus can expose future or target information even if the classifier itself is fit cleanly.

For retrieval-augmented generation, provenance and access controls must travel with the retrieved chunk. The feature pipeline should preserve document identity, version, section boundaries and retrieval timestamps. A model-generated narrative about the retrieved data does not establish a statistical relationship; numerical claims should come from a verified calculation with a defined denominator and analysis design.

### Choose a representation by its invariances

PCA retains large linear variation. ICA seeks independent non-Gaussian sources under a mixing model. NMF favors additive nonnegative parts. An autoencoder learns what its reconstruction objective rewards, while contrastive learning defines similarity through positive pairs, negative sampling and augmentations. These are different assumptions about which changes should matter.

If an image augmentation removes a small defect, a contrastive objective may learn to ignore the very signal the inspection task needs. If text chunks are paired by document rather than factual content, the embedding may encode style or source identity. Inspect the data construction and evaluate useful invariances directly. A compact representation is valuable only when it preserves the information the decision requires.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_20.py](../examples/chapter_20.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_20.py
```

### Recover a rank-one dataset exactly

The second column is twice the first, so centered rank is one. The first PCA component captures all variance and reconstructs every observation. The loading is parallel to (1,2), with either sign allowed. This checks the optimization geometry and avoids treating an arbitrary sign flip as a different scientific result.

### A holdout must not move the training origin

Training values have mean two. Including a future value 100 changes it to 26.5. The transformation would then use information from evaluation to alter every training coordinate. A large held-out z-score is useful evidence of distribution shift and should not be hidden by refitting on the test set.

### Features must respect label and time boundaries

If every category is unique, a same-row target mean equals the outcome exactly. The leave-one-out global fallback removes the row's own label but remains only a tiny illustration; real category encoders require fold-aware training and smoothing. The temporal example excludes the current row and produces historical means 10,15,20.

### Complete executable example

```python
import numpy as np

def pca_geometry():
    x=np.array([[1.,2.],[2.,4.],[3.,6.],[4.,8.]])
    mean=x.mean(axis=0);centered=x-mean
    u,s,vt=np.linalg.svd(centered,full_matrices=False)
    scores=centered@vt[:1].T
    reconstruction=scores@vt[:1]+mean
    variance=s*s/(len(x)-1)
    assert np.allclose(reconstruction,x) and np.isclose(variance[0]/variance.sum(),1.)
    assert np.isclose(abs(vt[0]@np.array([1.,2.])/np.sqrt(5)),1.)
    print("PCA loading:",vt[0],"explained ratio:",variance[0]/variance.sum())

def scaling_and_leakage():
    train=np.array([0.,2.,4.]);test=np.array([100.])
    train_mean=train.mean();train_sd=train.std(ddof=0)
    transformed=(test-train_mean)/train_sd
    leaked_mean=np.concatenate([train,test]).mean()
    assert train_mean==2 and leaked_mean==26.5 and transformed[0]>50
    print("Training-only mean:",train_mean,"leaked mean:",leaked_mean,"held-out z:",transformed[0])

def target_and_time_encoding():
    labels=np.array([0.,1.,0.,1.])
    naive_unique_category=labels.copy()
    leave_one_out=np.array([np.delete(labels,i).mean() for i in range(4)])
    assert np.array_equal(naive_unique_category,labels)
    assert not np.array_equal(leave_one_out,labels)
    values=np.array([10.,20.,30.,40.])
    lagged_mean=np.array([np.nan]+[values[:i].mean() for i in range(1,4)])
    assert np.allclose(lagged_mean[1:],[10,15,20])
    print("Naive unique-category encoding:",naive_unique_category,"fallback without own label:",leave_one_out)
    print("Strictly prior expanding means:",lagged_mean)

def main():
    pca_geometry();scaling_and_leakage();target_and_time_encoding()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Does retaining 95% PCA variance retain 95% predictive information?** No. PCA never sees the target and can discard a low-variance direction that predicts it strongly. Validate the full PCA-plus-model pipeline on the intended split.

**Interview: Why can target encoding create a perfect training model?** Rare categories can encode their own labels. Cross-fitting and smoothing reduce that direct leakage, while independent validation measures whether the category relationship generalizes.

**Interview: When is standardization inappropriate?** It is not always necessary for tree splits and can obscure meaningful absolute scales. The choice should follow the model geometry and question. If used, fit it only on training data and preserve its parameters for serving.

## Applied LLM companion

For implementation of text representations and domain assistants, continue with the [applied LLM course](../../llm-applied/guides/llm-applied-001.md). Representation similarity supports retrieval; it does not itself establish factual support or causal effects.

## Primary sources and official APIs

- [scikit-learn matrix factorization and PCA](https://scikit-learn.org/stable/modules/decomposition.html).

- [scikit-learn target encoder and cross-fitting](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.TargetEncoder.html).

## Reading connections

[Previous chapter](19-statistical-learning-and-classical-supervised-models.md) | [Book contents](../README.md) | [Next chapter](21-unsupervised-learning-and-multivariate-analysis.md)
