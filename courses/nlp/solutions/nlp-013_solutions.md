# nlp-013: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Build the corpus matrix

The row unit is a document and the columns are learned terms. A new evaluation word has no fitted coordinate under this vocabulary. Recording the mapping makes subsequent component weights interpretable and prevents accidental comparison of arrays with different word orders.

**Expected:** Four rows with a fixed vocabulary; held-out newplanet does not add a column.

## Exercise 2: Fit and inspect LSA

The low-rank representation preserves some large-scale variation while discarding other directions. A lower reconstruction error than the zero baseline verifies useful matrix approximation on the fixture. It does not establish coherent human topics or a good downstream classifier.

**Expected:** Document coordinates shape(4,2); reconstruction error below the zero-matrix baseline.

## Exercise 3: Fit nonnegative components

Nonnegativity makes each reconstruction additive. The authored corpus separates the two vocabulary groups, so their shared terms load on different components. The factor magnitudes still have scaling ambiguity and are not automatically topic probabilities.

**Expected:** W and H nonnegative; pet and wheel have different dominant component indices.

## Exercise 4: Inspect LDA mixtures

The output is a normalized inferred topic mixture under LDA's generative assumptions. The normalization check catches malformed consumption but does not prove the topics are correct. Topic count, priors and approximate inference all influence the result.

**Expected:** Four rows, two columns and each row sums to one.

## Exercise 5: Align topic identities

The deliberate permutation is a known-answer test for the alignment step. Raw row equality would fail despite identical components. Real stability analysis should also resample documents or vary seeds and inspect imperfect matches, not only this artificial exact case.

**Expected:** Permutation[1,0] and matched similarities[1,1].

## Exercise 6: Write an error-aware topic interpretation

A human label is an interpretation supported by inspected examples, not a latent truth emitted by the estimator. A useful report also shows mixed or poorly represented documents and explains how labels may change after retraining. Treat learned topic features as estimates when they feed later analysis.

**Expected:** A label linked to concrete words/documents, plus limits on uniqueness, coherence and downstream causal meaning.

## Transfer and limits

Topic discovery tries to summarize recurring structure in a document collection without a supplied class label for every document. A topic is a model component with a pattern of word weights or probabilities. It is not automatically a real organizational category, a causal factor or a uniquely defined human concept. Analysts label components after inspecting representative words and documents.

This lesson fits three actual local models to four authored documents: latent semantic analysis through truncated SVD, nonnegative matrix factorization and latent Dirichlet allocation. Their outputs can all be displayed as document-by-component arrays, but the mathematical meanings differ. Confusing those meanings can turn an arbitrary coordinate into an unjustified topic probability.

The corpus intentionally separates pet-related and vehicle-related vocabulary so the fitted behavior is easy to inspect. A successful separation on this constructed corpus is a mechanism demonstration, not evidence that the method will discover reliable topics in messy reviews, support tickets or scientific literature.

## Mechanism review and counterexample

Topic coherence asks whether a component's high-weight words make sense together under a chosen statistical or human criterion. A coherence score can favor common co-occurrence patterns without producing useful distinctions for the application. Inspect top words, representative documents, mixed documents and obvious counterexamples. Compare with simple keyword categories when those already solve the decision problem.

Topic numbers are arbitrary. Topic zero in one fit can correspond to topic one in another. Comparing raw indices across seeds would falsely declare instability. Align components through a matching criterion, such as cosine similarity over the same vocabulary, before comparing. Even aligned components can change meaning when the corpus or preprocessing changes; retain vocabulary and corpus versions.

Do not use estimated topic weights as error-free measurements in later causal or predictive analysis. The topic model was learned from data, may encode sensitive proxies and can change across retraining. A business report should describe the model and its uncertainty, include examples supporting a component label, and avoid naming a cluster after a conclusion the model did not identify.
