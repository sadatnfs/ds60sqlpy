# nlp-021: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Define normalized identity

The hash confirms equality of the normalized representation, not semantic equivalence in every task. Preserving raw text lets a reviewer inspect information intentionally discarded by the policy.

**Expected:** Equal normalized hashes while original strings remain unchanged.

## Exercise 2: Expose a near-duplicate trap

Three shared tokens and four union tokens produce .75. The missing negation changes meaning far more than its one-token contribution suggests. A near-duplicate detector should not automatically merge these records as equivalent evidence.

**Expected:** Similarity.75 despite a contradictory status claim.

## Exercise 3: Build the combined split

The split enforces two claims at once. Retaining the exclusion list explains why a future record is absent. A different known-family forecasting target could legitimately include b2, but that would be a separately labeled evaluation.

**Expected:** Train[a1,a2,b1],test[c1],excluded[b2].

## Exercise 4: Assert pipeline boundaries

The evidence boundary includes every learned preprocessing stage. Source metadata also protects against near-duplicate demonstrations and retrieval curation leaking answers. Record the complete fitting procedure, not only a train_test_split call.

**Expected:** Both invariants hold; vocabulary/IDF/calibration/tuning are explicitly inside training/development.

## Exercise 5: Compute paired family differences

Different row counts make the flattened result emphasize positive families. Neither average is intrinsically wrong, but each answers a different question. The comparison should retain paired case identities and state its weighting.

**Expected:** Equal-family2/15 versus row-weighted.2.

## Exercise 6: Bootstrap and qualify uncertainty

The resampling unit preserves the dependence represented by family grouping. Reproducibility is checked through the seed, while statistical credibility still depends on enough representative independent families. A toy interval is a mechanism demonstration, not a release guarantee. The future-new-family fixture also excludes b2 explicitly because its family appeared before the cutoff. Report that exclusion alongside the one remaining test family. A reviewer should see that stricter leakage control reduced the available evidence, rather than interpreting a clean split as proof that the dataset is now large enough. Collecting more independent future families is a different remedy from generating more paraphrases of c1.

**Expected:** Identical quantiles under the same seed; support within[-.1,.3]; no strong population claim from three families.

## Transfer and limits

Text evaluation is especially vulnerable to hidden dependence. One source document can generate many paragraphs, paraphrases, translations, summaries or ticket updates. Randomly placing these rows in different splits can make a model appear to generalize while it recognizes a template or sees nearly the same evidence twice. The statistical unit must match the deployment question.

Exact duplicate detection, near-duplicate detection, family grouping and time-aware splitting solve related but different problems. A hash can identify the same normalized bytes, a similarity score can propose related text, and provenance can establish that several records came from one underlying source. None should be silently substituted for the others.

The reference builds a tiny provenance-aware split and a family-level paired bootstrap. It exposes a semantic near miss with high token overlap and shows how row weighting differs from equal-family weighting. These mechanisms support an honest evaluation design; a five-document fixture cannot establish a stable deployment performance interval.

## Mechanism review and counterexample

For paired systems, compute a per-case loss or success difference on the same cases. When variants share a family, aggregate or resample at the family level rather than treating every variant as independent. A clustered bootstrap samples families with replacement and carries their within-family information together.

The fixture family mean differences are .2,-.1,.3, giving equal-family mean \(\frac{2}{15}\). Flattening all six rows instead gives .2 because the positive families contain more variants. These are different estimands. The bootstrap uses a fixed seed for reproducibility, but three families are far too few for a strong population uncertainty claim.

Report the number of independent families, variation across them, weighting convention and uncertainty method. A narrow row-level interval can be a symptom of duplicated evidence rather than high confidence in generalization.
