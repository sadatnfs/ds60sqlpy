## Retrieval defines what ranking can possibly accomplish

A recommender commonly separates candidate generation from ranking. Retrieval selects a manageable set of items from a larger universe. A ranker then orders those candidates using richer signals. The second stage cannot recover a relevant item that the first stage omitted. This simple ceiling is easy to hide when evaluation starts after candidate selection.

Define a query or user, an eligible item universe, a relevance horizon and a candidate budget. For a set of relevant items \(R\) and the first \(k\) candidates \(C_k\), retrieval recall is \(|R\cap C_k|/|R|\). The denominator requires a stated relevance set. Unobserved items are not automatically irrelevant, especially when the logging system exposed only a small subset.

This tutorial uses item sets and Jaccard similarity, \(J(U,V)=|U\cap V|/|U\cup V|\), to make candidate construction inspectable. It is a baseline mechanism, not a claim that set similarity is a production recommendation strategy for every catalog.

## Worked case 1: generate candidates from known history

User a has interacted with i1 and i2. Two neighboring users share one of those items and contribute i3 or i4. The program computes similarity from their sets and adds each neighbor's similarity to unseen candidate items. A deterministic item-ID tie-breaker produces a reproducible order when scores are equal.

At a candidate budget of two, relevant item i4 is retrieved, while i5 is omitted. Even a perfect ranker over those two candidates cannot recommend i5. This is the reason to report retrieval recall separately from ranking quality. A combined system can improve its ranker while leaving the most important bottleneck unchanged.

The fixture treats the available histories as a complete fixed input. In a temporal evaluation, only interactions available before the query should enter those histories. An item's future popularity, a later user action or a revised eligibility flag must not be used to reconstruct an earlier candidate set. A train/test split of individual rows can violate this even when the resulting code never reads a column named target.

## Worked case 2: define a cold-start policy

A user with no history has no meaningful Jaccard neighborhood in this baseline. The program uses a separate popularity ranking as an explicit cold-start policy. That policy can be inspected and evaluated for users with sparse or missing histories instead of being hidden inside a default zero-score tie-breaker.

Popularity has its own biases. It reflects prior exposure, eligibility and the behavior of the logging system. A new item may have no chance to become popular because it has never been shown. A policy can use metadata, exploration or other information to address that problem, but those methods need appropriate evaluation and operational constraints.

An empty relevant set also requires a policy. Returning a recall of zero or one without explanation can distort averages. The example assumes a nonempty relevance set for its exact checks. A real evaluation should report how such queries are handled and whether they represent missing labels, genuine absence of relevant items or an incompatible task definition.

## Build a temporal retrieval evaluation

Construct each query with the item universe and user history available at its timestamp. Keep eligibility rules, exclusion of already-consumed items, tie-breaking and candidate budget identical across compared methods. Record both failures to retrieve and failures to rank retrieved relevant items. If the item universe is sampled, state the sampling scheme because sampled-candidate metrics can differ substantially from full-catalog metrics.

Latency, memory and freshness constrain retrieval. A stale but fast index and a fresh but unavailable service have different practical consequences. Evaluate update behavior and failure fallbacks separately from relevance. A model's offline score cannot establish that its index or feature pipeline meets the decision deadline.

Do not equate a binary historical interaction with preference. A click may reflect position, exposure or curiosity. A missing click can mean that the item was never visible. Later tutorials examine pairwise objectives and logged-policy evaluation so that these labels are not silently treated as randomized observations.

## Answered scientific discussion

**Why can NDCG look excellent while the system misses useful items?** NDCG computed only over a filtered candidate set can reward a good ordering within that set. It says little about relevant items removed before scoring.

**What should a retrieval report contain?** State query construction, eligibility, time boundaries, candidate size, recall, cold-start coverage and operational constraints. Compare against transparent baselines. The program establishes exact behavior for a tiny candidate mechanism; a larger system needs both scientific evaluation and measured serving evidence.
