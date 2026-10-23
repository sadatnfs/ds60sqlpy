# nlp-014: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Implement masked mean

Padding rows are outside the modeled sentence. The deliberately large padded vector makes accidental inclusion obvious. A denominator based on total padded length would also be wrong even if padding values were zero, because it would shrink the representation.

**Expected:** [2,3]; all-padding input raises ValueError.

## Exercise 2: Normalize nonzero vectors

Normalization makes dot product a cosine comparison. The ranking is a consequence of the supplied vectors, so it tests implementation rather than language-model quality. A learned representation requires an independent corpus and evaluation to support semantic claims.

**Expected:** Each result has unit norm and their similarity exceeds the dog/pet alternative.

## Exercise 3: Preserve the order counterexample

This failure follows mathematically from the representation. Increasing nearest-neighbor search accuracy cannot recover an ordering distinction that was discarded before indexing. A contextual or structured representation is a candidate repair that must be tested on role-sensitive examples.

**Expected:** Exactly matching pooled vectors despite different role meaning.

## Exercise 4: Derive contrastive loss

Each row has the same two-score gap, so both losses agree. The stable expression avoids unnecessary exponent overflow. This is one objective calculation, not a training run or a calibration guarantee for relevance probabilities.

**Expected:** Average log(1+exp(-2)), approximately .126928.

## Exercise 5: Change temperature and candidate semantics

A smaller temperature sharpens differences and lowers this fixture's loss because the positives already win. It can worsen other training dynamics or emphasize mislabeled negatives. The candidate set and label quality therefore matter as much as the algebra.

**Expected:** Lower numeric loss on the fixed correctly ordered fixture; written warning that a valid alternative labeled negative changes the learning target.

## Exercise 6: Specify a retrieval handoff

The next stage needs enough provenance to verify the passage, not only a vector score. The toy encoder explicitly lacks an unknown-token strategy and must expose that limit. A production encoder has a tokenizer policy, but successful encoding still does not prove evidence relevance or answer grounding.

**Expected:** Record contains source identity/version/text span/score; unsupported token raises instead of inventing an embedding.

## Transfer and limits

Sentence representations map variable-length text to a fixed-length vector so sentences or documents can be compared efficiently. A vector can support semantic search, clustering or a downstream classifier, but its usefulness depends on how it was constructed and trained. The same cosine function applied to arbitrary vectors does not create semantic understanding.

This lesson uses explicitly handcrafted token vectors to make pooling and retrieval geometry inspectable, plus an exact contrastive-loss calculation. These vectors were chosen by the author and are not learned word embeddings or outputs from a pretrained sentence encoder. The success of the car/automobile example is built into that fixture. The real learning question is how a trained representation acquires and generalizes such relationships.

A bi-encoder maps queries and documents separately, enabling document embeddings to be precomputed and searched. A cross-encoder jointly processes a query-document pair, allowing richer interactions but usually requiring more work per candidate. A practical search system can retrieve with a bi-encoder and rerank a small set with a cross-encoder. Their quality and latency must be measured as separate pipeline stages.

## Mechanism review and counterexample

A semantic score is an association under a representation, not an entailment judgment. A passage about approving a restart can be near a query about a completed restart without proving that any restart occurred. Retrieval should preserve document IDs, dates, access metadata and source spans so later stages can inspect what the text actually supports.

Evaluate recall at a candidate budget before evaluating the final answer. If the required passage is absent from the retrieved set, a downstream generator has no supplied evidence for that part of the task. Conversely, high retrieval recall does not prove that a generator interprets the passages faithfully. The applied LLM route separates these boundaries in grounded-answer evaluation.

A real pretrained sentence model adds learned parameters, its exact tokenizer, pooling convention, model version, training objective and resource requirements. This offline lesson downloads none of them. When using one later, record and cache the complete artifact set deliberately and compare against the TF-IDF baseline from nlp-007 on the same held-out queries.
