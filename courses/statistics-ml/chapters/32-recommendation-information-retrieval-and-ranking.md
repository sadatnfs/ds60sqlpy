# 32. Recommendation, Information Retrieval, and Ranking

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-032`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Recommendation and retrieval turn a large candidate universe into a small ordered set that someone can act on. A two-stage system usually retrieves a manageable candidate set, then ranks it using richer features. Candidate recall limits the ranker: an excellent ranking model cannot recover a useful item that never reached its input. Evaluation should therefore distinguish candidate generation, ordering and the complete user experience.

### Observed feedback is selected feedback

A user can click only an item they were shown, and high positions receive more attention. A missing interaction is not equivalent to a dislike. Training directly on clicks can reproduce the previous system's exposure pattern and amplify popular items. Log which candidates were eligible, which were shown, positions, timestamps and any randomized propensities needed for counterfactual evaluation.

### From representations to scores

Matrix factorization approximates a user-item score by \(p_{u}^{\mathsf T}\cdot q_{i}\), where p_u and q_i are learned latent vectors. Content models instead derive features from item or user attributes. A two-tower model generalizes this with separate encoders so item vectors can be precomputed and searched efficiently. That architectural efficiency constrains interactions: a final ranker can add features unavailable to a simple dot-product retrieval stage.

### Ranking metrics encode a user model

Reciprocal rank values the position of the first relevant result. Average precision rewards finding multiple relevant results early. NDCG discounts lower positions and supports graded relevance, normalized by the best ordering for the judged candidate set. State the gain convention: exponential gains \(2^{\mathrm{relevance}}-1\) and direct relevance gains are both used, but their numbers differ. A metric name without its cutoff, gain convention and query averaging rule is incomplete.

### Build a realistic evaluation population

Hold out future interactions or whole new users/items according to the deployment question. Construct candidates from what was available at that time, not from a later catalogue. Randomly sampled negatives can make ranking artificially easy and change the meaning of the metric. Report cold-start performance, exposure distribution, latency and diversity alongside average relevance. When business outcomes matter, an online randomized comparison can test effects that offline label rankings cannot establish.

### A concrete search case

For a knowledge search product, retrieval should find documents containing the needed evidence, while ranking should put usable documents near the top. A highly similar but outdated document can score well and still harm the task. Define freshness and access constraints before scoring. If a generated answer follows retrieval, assess whether the answer used the evidence correctly as a separate end-to-end step. Optimizing vector similarity alone is not a complete success criterion.

## Methods, mechanisms, and limits

### stat-32-01

**Collaborative filtering**

Collaborative filtering learns from patterns of interaction among users and items, assuming useful preference structure is shared. Neighborhood and latent-factor methods express this in different ways. Sparse feedback and exposure bias limit what can be inferred about unobserved pairs. A popular item may appear broadly preferred because it was broadly shown. Validate on future opportunities and retain a fallback for users or items with no interaction history.

### stat-32-02

**Content-based recommendation**

Content-based recommendation uses attributes such as text, categories or product features to match a user's interests with items. It can handle new items if their features are available, but may over-specialize around past preferences and miss complementary interests. Feature quality and temporal availability matter. Evaluate whether the system recommends useful alternatives rather than merely near-duplicates of previously consumed content.

### stat-32-03

**Matrix factorization**

Matrix factorization represents a user-item matrix through lower-dimensional factors, often minimizing observed-entry loss plus regularization. Missing entries should not be silently treated as observed zeros. Latent dimensions capture predictive interaction structure but generally lack unique semantic interpretation because rotations preserve dot products. Rank, regularization and the feedback loss should be selected using deployment-like validation.

### stat-32-04

**Implicit-feedback models**

Implicit-feedback models use clicks, views or purchases as evidence of preference while distinguishing preference from confidence in that evidence. A non-click can mean no exposure, insufficient attention or genuine disinterest. Weighting and negative sampling define the training objective and can strongly alter results. Record sampling rules so evaluation can distinguish ranking among sampled negatives from ranking the real eligible catalogue.

### stat-32-05

**Factorization machines**

Factorization machines model pairwise feature interactions through low-rank latent vectors, allowing sparse categorical features to share statistical strength. They can combine user, item and contextual features beyond a simple matrix. The factorized interaction constraint reduces parameter count but may miss higher-order structure. Leakage through post-outcome context or identifiers remains possible even with an otherwise regularized model.

### stat-32-06

**Two-tower retrieval models**

Two-tower retrieval encodes a query/user and an item separately, then compares their vectors with a score such as a dot product. Item vectors can be precomputed, enabling fast search over large catalogues. Training negatives and score temperature influence what similarity means. Features requiring joint query-item processing generally belong in a later ranker, and stale item embeddings can create training-serving mismatch.

### stat-32-07

**Nearest-neighbor retrieval**

Nearest-neighbor retrieval returns candidates closest under a defined distance or similarity. Cosine similarity compares direction after normalization, while dot product also reflects vector magnitude. The chosen metric must match training and indexing conventions. Exact nearest neighbors are exact only for that representation, not for human relevance, so evaluate candidate recall against task-specific judgments.

### stat-32-08

**Approximate nearest-neighbor search**

Approximate nearest-neighbor search trades exactness for speed and memory efficiency through structures such as quantization or navigable graphs. Index parameters control recall-latency tradeoffs. Measure recall against an exact search baseline on representative queries, including new or rare item regions. A fast index with poor candidate recall sets a hard ceiling on the downstream ranker.

### stat-32-09

**Learning-to-rank objectives**

Learning-to-rank objectives optimize scores using pointwise, pairwise or listwise training signals. A pointwise relevance model need not optimize the final top-k metric, while metric-oriented surrogates introduce other assumptions and complexity. Keep query groups intact during splitting and compute features at serving time. Label quality, candidate construction and exposure bias often dominate the choice of optimizer.

### stat-32-10

**Pairwise ranking**

Pairwise ranking trains a preferred item to score above a less preferred item, using losses such as logistic loss on score differences. The sampled pair distribution determines which errors matter. Exhaustive pair construction can overweight queries with many judged items. Pairwise consistency does not automatically yield calibrated relevance scores or optimal diversity, and ties require a defined policy.

### stat-32-11

**Listwise ranking**

Listwise ranking optimizes a distribution or metric surrogate over an entire candidate list. It can reflect competition among items and position-sensitive objectives more directly than independent scoring. Training lists must resemble serving lists, and incomplete relevance judgments complicate normalization. List length, negative sampling and loss weighting influence both statistical efficiency and the practical target.

### stat-32-12

**NDCG**

NDCG sums discounted gains for a ranked list and divides by the ideal ordering's sum. With exponential gain, \(\mathrm{DCG}=\sum_r\frac{2^{\mathrm{rel}_r}-1}{\log_2(r+1)}\); other conventions use direct gains. Define the cutoff, handling of all-zero relevance and ties. Normalizing per query supports comparison but can give a small easy query the same weight as a high-value difficult one.

### stat-32-13

**Mean reciprocal rank**

Mean reciprocal rank averages \(\frac{1}{r}\) for the first relevant result in each query, with zero when none is found. It matches tasks where one useful answer is sufficient. It ignores relevance after the first hit, so it is unsuitable as the sole measure when several documents are needed. Specify the retrieval cutoff and treatment of queries with no relevant catalogue item.

### stat-32-14

**Mean average precision**

Mean average precision averages precision at each relevant hit, then averages across queries. It rewards retrieving many relevant items near the top, unlike reciprocal rank's first-hit focus. The denominator depends on the judged relevant set, which may be incomplete. Different handling of unjudged documents or cutoffs changes the result, so the evaluation collection and conventions belong in the report.

### stat-32-15

**Position bias**

Position bias arises because users examine high-ranked items more often, making clicks a mixture of relevance and exposure. Swapping positions or other randomized interventions can identify examination effects under assumptions. A click-through improvement can result from presentation rather than better relevance. Debiasing methods require credible propensities or a defensible user model, not only an inverse-rank weight chosen by convenience.

### stat-32-16

**Counterfactual ranking evaluation**

Counterfactual ranking evaluation estimates a new ranking policy's value from logs generated by another policy. Importance weighting requires support: actions favored by the new policy must have had positive logging probability. Rare exposures create high variance, and deterministic logging can make some comparisons unidentified. Report clipping or self-normalization and the estimand they approximate, with randomized evidence when feasible.

### stat-32-17

**Diversity-aware recommendation**

Diversity-aware recommendation balances relevance with coverage of categories, intents or viewpoints. Re-ranking can penalize redundant items or optimize a set-level objective. The definition of diversity must match user value rather than an arbitrary embedding distance. Measure the relevance tradeoff and subgroup experience, because a globally diverse list can still be unhelpful to a particular query.

### stat-32-18

**Novelty and serendipity**

Novelty describes how unfamiliar an item is to a user, while serendipity additionally requires unexpected usefulness. Low popularity alone is not proof of either. Evaluation may require user history, subjective judgments or downstream utility. Excessive novelty can reduce relevance, while a relevance-only system can repeatedly recommend obvious items. Define the intended balance before selecting a metric.

### stat-32-19

**Cold-start recommendation**

Cold-start recommendation handles new users or items with little interaction evidence. Content features, onboarding questions, contextual priors and limited exploration offer different bridges. Test by holding out entire new entities, preserving the catalogue and information available at their arrival. Warm-start validation cannot establish cold-start capability, and uncertainty should inform conservative or exploratory fallbacks.

### stat-32-20

**Feedback-loop analysis**

Feedback loops occur when recommendations change exposure, behavior and the future training data. Repeatedly amplifying already popular items can narrow the observed preference distribution. Randomized exploration, exposure logging and policy-aware evaluation help distinguish learning from self-reinforcement. Monitor long-term user value and catalogue coverage, because short-term clicks can improve while future information quality and diversity deteriorate.

## Worked Python demonstrations

Complete offline program: [chapter_32.py](../examples/chapter_32.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_32.py
```

### Separate representation quality from search approximation

Three unit vectors produce exact query dot products [1,0.8,0]. An approximate candidate set containing items one and two recovers only one of the exact top two, giving recall@2 of one-half. This measures index approximation relative to the vector score; whether the vectors encode useful relevance is a separate evaluation.

### Compute three ranking objectives

The graded relevance values [3,2,0] are returned in order [0-relevance,3-relevance,2-relevance]. The example explicitly uses exponential gains for NDCG. Binary hits at ranks two and three give reciprocal rank one-half and average precision \(\frac{\frac{1}{2}+\frac{2}{3}}{2}=\frac{7}{12}\). Each metric emphasizes a different aspect of the ordered result.

### See why clicks mix preference with exposure

Two equally relevant items have underlying relevance probability 0.4, but examination probabilities one and one-quarter. Their expected click rates are 0.4 and 0.1. Dividing by the known examination probabilities recovers equal relevance in this exact model. Real logs require estimated or randomized propensities and uncertainty; the calculation does not justify assuming the model is true.

### Complete executable example

```python
import numpy as np

def exact_retrieval():
    query=np.array([1.,0.]);items=np.array([[1.,0.],[.8,.6],[0.,1.]])
    scores=items@query;order=np.argsort(-scores,kind="stable")
    assert order.tolist()==[0,1,2] and np.allclose(scores,[1.,.8,0.])
    approximate=np.array([1,2]);true_top2=set(order[:2])
    recall=len(true_top2 & set(approximate))/2
    assert recall==.5
    print("Exact order:",order,"example approximate recall@2:",recall)

def ranking_metrics():
    relevance=np.array([3.,2.,0.]);order=np.array([2,0,1])
    discount=np.log2(np.arange(2,5))
    dcg=np.sum((2**relevance[order]-1)/discount)
    ideal=np.sum((2**np.sort(relevance)[::-1]-1)/discount)
    ndcg=dcg/ideal
    binary=np.array([0,1,1]);hits=np.flatnonzero(binary)+1
    reciprocal=1/hits[0];ap=np.mean(np.arange(1,len(hits)+1)/hits)
    assert 0<ndcg<1 and reciprocal==.5 and np.isclose(ap,7/12)
    print("Exponential-gain NDCG:",ndcg,"reciprocal rank:",reciprocal,"AP:",ap)

def exposure_adjustment():
    # Same underlying relevance .4, examination probabilities 1 and .25.
    expected_click=np.array([.4,.1]);examination=np.array([1.,.25])
    recovered=expected_click/examination
    assert np.allclose(recovered,[.4,.4])
    print("Expected clicks:",expected_click,"propensity-adjusted relevance:",recovered)

def main():
    exact_retrieval();ranking_metrics();exposure_adjustment()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Why can the best ranker fail in production?** Candidate generation may omit useful items, feature values may differ at serving time, or labels may reflect the old policy's exposure. Evaluate the full pipeline and preserve the candidate and information sets used by the real system.

**Interview: When would MRR and MAP disagree?** MRR rewards the first relevant result and ignores later hits. MAP rewards finding all judged relevant results early. A system optimized for one-answer lookup can differ from one supporting multi-document research, so select the metric from the task.

**Interview: Can inverse-propensity weighting evaluate any new policy?** No. It requires support under the logging policy and credible propensities. Near-zero probabilities create unstable weights, and zero probabilities make the missing comparison unidentified without additional assumptions or new exploration.

## Primary sources and official APIs

- [Manning, Raghavan and Schutze, evaluation of ranked retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)

- [scikit-learn NDCG API and gain conventions](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html)

## Reading connections

[Previous chapter](31-network-and-graph-analysis.md) | [Book contents](../README.md) | [Next chapter](33-deep-learning-language-and-generative-modeling.md)
