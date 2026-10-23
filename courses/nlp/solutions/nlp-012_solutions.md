# nlp-012: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Count a local window

The middle pet has two cat neighbors, and each outer cat has one pet neighbor. This creates four directed observations, not two undirected pairs. Document the direction convention because another definition can legitimately produce different counts.

**Expected:** Matrix [[0,2],[2,0]] with total four directed context events.

## Exercise 2: Protect document boundaries

Flattening all tokens would treat unrelated boundary words as adjacent. The correct algorithm restarts the window at each document boundary. This is a corpus-contract issue that can materially change learned relationships in a large pipeline.

**Expected:** Separate documents yield zero context events; no cross-document pair is created.

## Exercise 3: Implement finite PPMI

PMI compares joint frequency with independence. Masking positive cells prevents log(0) warnings and defines the positive-PMI boundary explicitly. An all-zero matrix contains no empirical context distribution; returning zeros is a documented representation convention, not an estimate of semantic relationships.

**Expected:** First cell log(80/49); all values finite/nonnegative; zero-count cells and empty matrix remain zero.

## Exercise 4: Handle cosine carefully

A zero vector has no direction, so assigning a numeric cosine can hide an absent representation. The other comparisons follow the dot-product geometry of the authored matrix. They should not be generalized into claims that real words in those roles are synonyms or unrelated.

**Expected:** Positive first-pair similarity, zero cross-group similarity, None for a zero-norm comparison.

## Exercise 5: Inspect rank-two compression

Truncation removes the smallest singular component. In this symmetric fixture that component distinguishes the first two rows, so their remaining directions match. The example makes information loss inspectable and shows why compression quality and downstream semantic quality are different checks.

**Expected:** Positive reconstruction error smaller than the matrix norm; first two reduced rows have cosine one.

## Exercise 6: Test geometric invariance

Orthogonal rotation preserves inner products and norms, so cosine remains unchanged while coordinate values change. This demonstrates non-uniqueness of axes. A vector analogy can still be empirically useful, but its success must be evaluated across representative relations rather than inferred from one coordinate label.

**Expected:** Cosine unchanged; a written explanation rejects unique semantic meaning for one coordinate.

## Transfer and limits

Distributional representations describe a word through the contexts in which it appears. The intuition is that words used in similar contexts may share useful properties. This is a statistical hypothesis about a corpus, not a guarantee of synonymy or factual equivalence. Antonyms often appear in similar contexts, and a rare word's apparent neighborhood can be unstable.

A co-occurrence matrix C has one row per target word and one column per context feature. C_ij counts how often target i appears with context j under a specified window. Changing the context definition changes the model: a symmetric nearby-word window, a directional window and a dependency relation capture different information. Document boundaries must remain explicit so unrelated final and initial words do not become artificial neighbors.

Dense embeddings compress or learn useful representations of these relationships. This lesson constructs actual count-based PPMI vectors and a truncated singular-value decomposition. It does not train word2vec, a contextual transformer or a pretrained semantic model. The exact small matrices make weighting, compression, cosine similarity and geometric invariances visible.

## Mechanism review and counterexample

Singular-value decomposition writes M=U*diag(s)*V_transpose. Retaining the largest k singular values gives a rank-k reconstruction with a precise least-squares approximation property for the matrix. The embedding used here is U_k*diag(s_k), with V_k_transpose used to reconstruct. Other conventions distribute singular-value powers differently and therefore change cosine geometry.

Cosine similarity is the dot product divided by the product of vector norms. It measures direction rather than magnitude and is undefined for a zero vector. The reference returns None for that boundary so missing representation is not mislabeled as meaningful dissimilarity. A normalized dot product and an unnormalized dot product answer different retrieval questions.

Rank-two compression makes the first two fixture rows collinear, losing their small distinction. That is a useful failure case: compression can improve a broad shared pattern while erasing fine-grained information. A rotation of all embeddings preserves dot products and cosine, so an individual coordinate does not have a unique semantic meaning. Analogy arithmetic and nearest neighbors require task-specific validation; an appealing example is not a general semantic guarantee.
