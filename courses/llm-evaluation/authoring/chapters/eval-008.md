## Locate the failure in the pipeline

A retrieval-augmented assistant selects candidate documents, ranks some of them, forms a context and generates an answer. Failure at one stage can be hidden by success at another. A correct answer does not prove that retrieval was adequate, because a model may know the answer independently. A relevant retrieved passage does not prove that the generated answer used it correctly.

Define the candidate corpus and the query population before choosing a ranking metric. A relevance judgment is conditional on a query, a document version and a rubric. It is not a permanent property of a document. An evaluation based on a judgment pool sees only the documents that were judged; relevant documents outside the pool can change recall and ideal rankings.

For a query with a known nonempty relevant set \(G\), recall at \(k\) is the fraction of \(G\) appearing in the first \(k\) distinct results. Reciprocal rank uses the first relevant position. With graded relevance \(r_j\), a common discounted gain is

\[
\operatorname{DCG}@k=\sum_{j=1}^{k}\frac{2^{r_j}-1}{\log_2(j+1)}.
\]

Normalized DCG divides by the ideal DCG obtained by sorting the known relevance grades. The gain convention and discount base are part of the metric definition. These examples use nonnegative integer grades and reject unjudged documents instead of silently assigning them zero relevance. The scikit-learn function discounts the relevance values it receives directly. To reproduce this exponential-gain convention with that API, supply `2**grade - 1` as its relevance values in the same document order. Comparing raw-grade and exponential-gain nDCG without naming the difference changes the metric.

## Worked case A: a strong top ranking

The corpus has three relevant documents with grades 3,2,1 and one irrelevant document. Returning the grade 3 and grade 2 documents first gives recall two thirds at depth two, reciprocal rank one and nDCG one. Perfect nDCG at this cutoff does not imply complete recall, because an ideal top two still omits a third relevant document.

{{WORKED_A}}

## Worked case B: weak retrieval can have a nonzero first hit

The second ranking begins with an irrelevant document followed by a grade 1 document. Reciprocal rank is one half, but the discounted gain is small relative to the ideal top two. A single first-hit measure misses this difference in graded utility. Repeating one highly relevant document is rejected, because duplicate entries should not count as additional retrieved evidence.

{{WORKED_B}}

## Averaging queries and handling missing judgments

Macro-averaging gives each query equal weight. Traffic-weighted averaging represents a different population. Multiple paraphrases from a family can also create dependence and unequal representation. The sampling and uncertainty rules from earlier units apply to ranking metrics just as they apply to answer correctness.

A query with no known relevant documents has an undefined recall denominator and zero ideal DCG. The helper returns explicit missing values for that case. This policy prevents a zero from being mistaken for evidence of a poor retriever or a one from being mistaken for a perfect one. A study may adopt another documented convention, but it should report how many queries fall into that category.

Judgment pooling can favor systems whose retrieved documents helped form the pool. Add new candidates for blinded relevance assessment when a different retriever discovers new material. Explain how the pool was constructed and consider sensitivity to unjudged documents. Do not use a silently incomplete gold set to claim exhaustive recall.

## Connect retrieval to the final decision

Measure latency, memory, update freshness and access policy alongside ranking quality. A retriever that returns a forbidden document is unacceptable even if the document is relevant. Keep pre-retrieval authorization and post-retrieval evidence checks distinct. Later units evaluate claim support and abstention after retrieval.

The programs operate on authored relevance tables and ordered identifiers. They do not call a search engine or evaluate a live vector database. Their exact counts make the definitions and invalid-input policies visible before using a larger system. To transfer the method, retain the query/corpus snapshot, all ranked IDs, judgments, tie rule and query weights so another analyst can reconstruct every aggregate.
