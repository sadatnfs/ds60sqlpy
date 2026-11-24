# ruff: noqa: E501
"""Exercise-specific Verify lines for nlp-005 to nlp-024, keyed by (lesson number, exercise number).

Each line names the check a learner can run or inspect, instead of repeating the expected text.
"""

VERIFY = {
    (
        5,
        1,
    ): "Assert each (form, POS) key returns its lemma, so saw/VERB and saw/NOUN give different results, and that the raw form is still stored beside the lemma.",
    (
        5,
        2,
    ): "Print the label the rule assigns to saw in both sentences; the determiner the must be the only cue that switches VERB to NOUN.",
    (
        5,
        3,
    ): "Check that the result record keeps the rule's VERB output next to the independent NOUN label and marks it as an error instead of overwriting either value.",
    (
        5,
        4,
    ): "Assert that exactly one of the five head arrays passes and that each rejected array fails a named rule: two roots, an out-of-range head, a cycle or no tokens.",
    (
        5,
        5,
    ): "Check that both arrays pass the structural validator and that only [1, -1, 1] attaches her to saw, so validity and meaning are reported separately.",
    (
        5,
        6,
    ): "Check that the written policy keeps the raw token, names a distinction lost for search and one for event extraction, and states when each collapse is acceptable.",
    (
        6,
        1,
    ): "Assert the vocabulary has 7 entries, contains EOS and UNK, and excludes BOS, which is only ever a context.",
    (
        6,
        2,
    ): "Recompute each factor as (count + 1)/(row total + 7) from the training rows and assert the four values match 0.3, 1/3, 0.3 and 1/3.",
    (
        6,
        3,
    ): "Assert that the exponentiated log likelihood is close to 0.01, the event count is 4 including EOS, and perplexity equals \\(\\sqrt{10}\\), about 3.1623.",
    (
        6,
        4,
    ): "For each of the four contexts, assert the probabilities over all 7 targets sum to 1 within 1e-12.",
    (
        6,
        5,
    ): "Copy the counts and vocabulary before scoring, then assert both are unchanged afterwards and that cocoa was scored through UNK.",
    (
        6,
        6,
    ): "Assert the empty input yields exactly one EOS event with perplexity 10, and check that the written comparison names tokenization, corpus and boundary conventions.",
    (
        7,
        1,
    ): "Count documents containing each term, not occurrences: assert tea has document frequency 1 although it appears twice.",
    (
        7,
        2,
    ): "Assert `vectorizer.idf_` matches \\(\\log\\frac{1+n}{1+\\mathrm{df}}+1\\) element by element in `get_feature_names_out()` order.",
    (
        7,
        3,
    ): "Assert every row of the manual dense oracle has unit L2 norm and matches the sparse transform within 1e-12.",
    (
        7,
        4,
    ): "Assert the first score equals \\(\\frac{2a}{\\sqrt{1+4a^2}}\\) with \\(a=\\log\\frac{3}{2}+1\\) and that the second is exactly 0 because coffee cup lacks tea.",
    (
        7,
        5,
    ): "Assert both transformed rows have nnz == 0 and that vocabulary_ is identical before and after, then record the no-known-terms outcome.",
    (
        7,
        6,
    ): "Assert the unnormalized tea weight equals \\((1+\\log 2)a\\) and differs from \\(2a\\), showing that `sublinear_tf` changes term-frequency scaling.",
    (
        8,
        1,
    ): "Assert the count rows follow the class order [0, 1] and that the priors come from document counts, not token counts.",
    (
        8,
        2,
    ): "Assert each likelihood row sums to 1 and that the zero count in class 0 becomes 1/5 rather than 0.",
    (
        8,
        3,
    ): "Assert the logsumexp posterior equals [3/13, 10/13] and sums to 1 without exponentiating large negative logs directly.",
    (
        8,
        4,
    ): "Compare classes_, feature_log_prob_ and predict_proba from MultinomialNB with the manual oracle and assert all three agree within 1e-12.",
    (
        8,
        5,
    ): "Assert the all-zero probe's posterior equals the prior exactly, and that the prior [0.9, 0.1] makes class 0 more probable for the urgent-only probe.",
    (
        8,
        6,
    ): "Assert the represented rows and posteriors for urgent and not urgent are identical, and check that the written note separates accuracy from calibration.",
    (
        9,
        1,
    ): "Assert \\(\\sigma(2.5)\\approx 0.92414182\\) and that the sigmoid at \\(\\pm 1000\\) returns finite values near 1 and 0 without overflow warnings.",
    (
        9,
        2,
    ): "Assert the fitted vocabulary has six terms, escalation is absent after transform, and the two stated probes predict [1, 0].",
    (
        9,
        3,
    ): "Print both coefficient norms and assert the C = 0.1 norm is the smaller one under identical solver settings.",
    (
        9,
        4,
    ): "Assert the 0.5 actions are [False, False, True] and the 0.3 actions are [False, True, True], with a score equal to the threshold counted as positive.",
    (
        9,
        5,
    ): "Assert the two Brier scores are 0.41 and 0.26 and that a probability of 1.2 raises ValueError before any score is computed.",
    (
        9,
        6,
    ): "Assert the frozen unigram rows for urgent and not urgent are equal, then check that the separately fitted bigram vectorizer contains not urgent.",
    (
        10,
        1,
    ): "Assert the exponentiated initialization column equals [0.36, 0.04], computed from start and first-emission probabilities only.",
    (
        10,
        2,
    ): "Assert the decoded path is [0, 1], its probability is 0.0756 and the backpointer trace returns one label per observation.",
    (
        10,
        3,
    ): "Enumerate all four paths and assert the decoder's optimum equals the enumerated maximum for both fixtures: N, V at 0.0756 and V, V at 0.1386.",
    (
        10,
        4,
    ): "Assert the empty sequence returns an empty path with log score 0, the all-zero emission row raises ValueError and the tied fixture returns [0, 0].",
    (
        10,
        5,
    ): "Assert [B-ORG, I-ORG, O] validates while a leading I-ORG and an ORG continuation after B-PER are both rejected.",
    (
        10,
        6,
    ): "Assert token accuracy is 2/3 while exact two-token ORG entity recall is 0, and record why the span metric is stricter.",
    (
        11,
        1,
    ): "Assert each returned span slices the raw sentence back to its mention text and carries the expected PER, ORG or LOC type.",
    (
        11,
        2,
    ): "Assert Acme Labs wins over the nested Acme and that both Ada mentions are returned at [0, 3) and [8, 11).",
    (
        11,
        3,
    ): "Assert the escaped pattern matches C++ Labs at [0, 8) and that an empty lexicon name raises a clear error.",
    (
        11,
        4,
    ): "Assert TP 1, FP 1 and FN 2 from exact span-and-type matching, then precision 0.5, recall 1/3 and F1 0.4.",
    (
        11,
        5,
    ): "Assert reversing the company order swaps acquirer and acquired, and that the negated and rumor-prefixed sentences return no relation.",
    (
        11,
        6,
    ): "Check that the ambiguity record lists both Ada and Bea as candidates for she and that no confirmed person-organization relation is emitted.",
    (
        12,
        1,
    ): "Assert the co-occurrence matrix equals [[0, 2], [2, 0]] and that its total is 4 directed context events.",
    (
        12,
        2,
    ): "Assert the separate one-token documents produce an all-zero matrix, so no pair crosses a document boundary.",
    (
        12,
        3,
    ): "Assert the first PPMI cell equals log(80/49), every value is finite and nonnegative, and zero-count cells and the empty matrix stay 0.",
    (
        12,
        4,
    ): "Assert the first pair's cosine is positive, the cross-group cosine is 0, and a zero-norm row returns None rather than NaN.",
    (
        12,
        5,
    ): "Assert the rank-two reconstruction error is positive and below the matrix norm, and that the first two reduced rows have cosine 1.",
    (
        12,
        6,
    ): "Assert cosine is unchanged after the same orthogonal rotation is applied to both vectors, and check the note that one coordinate has no fixed meaning.",
    (
        13,
        1,
    ): "Assert the matrix has four rows, the vocabulary order is fixed, and transforming newplanet adds no column.",
    (
        13,
        2,
    ): "Assert the document coordinates have shape (4, 2) and that the reconstruction error is below the error of predicting all zeros.",
    (
        13,
        3,
    ): "Assert W and H have no negative entries and that pet and wheel load most heavily on different components.",
    (13, 4): "Assert the LDA document-topic matrix has shape (4, 2) and that every row sums to 1.",
    (
        13,
        5,
    ): "Assert the alignment between H and its reversed rows is permutation [1, 0] with matched cosine similarities [1, 1].",
    (
        13,
        6,
    ): "Check that the topic label cites concrete top words and source documents and states what remains unproven about uniqueness, coherence and causal meaning.",
    (
        14,
        1,
    ): "Assert the masked mean over the two valid rows is [2, 3] and that an all-padding mask raises ValueError.",
    (
        14,
        2,
    ): "Assert both pooled vectors have unit norm and that their cosine exceeds the dog/pet comparison.",
    (
        14,
        3,
    ): "Assert the pooled vectors for dog bites person and person bites dog are exactly equal, exposing the lost word order.",
    (
        14,
        4,
    ): "Assert each row loss equals \\(\\log(1+e^{-2})\\) and that their average is about 0.126928.",
    (
        14,
        5,
    ): "Assert the loss at temperature 0.5 is lower on this correctly ordered fixture, and check the written false-negative example.",
    (
        14,
        6,
    ): "Check that the result record names source identity, version, text span and score, and assert that an unknown-token query raises.",
    (
        15,
        1,
    ): "Assert each attention row sums to 1 and that bank's second output coordinate changes sign between the river and money contexts.",
    (
        15,
        2,
    ): "Assert the valid outputs match the unpadded run, the padded-key weights are 0 and the padded query output is 0.",
    (
        15,
        3,
    ): "Assert the training loss starts at log 2 and ends below 0.1, and that the training predictions are [0, 1, 0, 1].",
    (
        15,
        4,
    ): "Assert the masked loss equals \\(\\log(1+e^{-2})\\) and does not change when the logits at the -100 positions are altered.",
    (
        15,
        5,
    ): "Assert both the all-padding encoder input and the all-ignored label batch raise ValueError with a clear message.",
    (
        15,
        6,
    ): "Check that the evaluation plan names held-out families, the exact tokenizer and pooling identity, a lexical baseline and subgroup and truncation slices.",
    (
        16,
        1,
    ): "Assert [repair] produces inputs [BOS, repair] and targets [repair, EOS], and that empty output produces [BOS] and [EOS].",
    (
        16,
        2,
    ): "Assert the two weights sum to 1 and the output equals \\([10p, 20(1-p)]\\) with \\(p=\\sigma(1/\\sqrt{2})\\).",
    (
        16,
        3,
    ): "Assert the masked output is exactly [10, 0] and that marking every source position invalid raises.",
    (
        16,
        4,
    ): "Assert width one returns tea, EOS with probability 0.3 and width two returns coffee, EOS with probability 0.4.",
    (
        16,
        5,
    ): "Assert the service query returns sentence index 0 unchanged and the refund query returns None.",
    (
        16,
        6,
    ): "Check that the written account separates teacher-forced loss, autoregressive rollout, search score and factual support for one wrong first token.",
    (
        17,
        1,
    ): "Assert the clipped count for the repeated the is capped at its reference count, giving precision 0.25 rather than 1.",
    (
        17,
        2,
    ): "Assert both n-gram precisions are 1 and that the brevity penalty and the final score both equal \\(e^{-0.5}\\).",
    (
        17,
        3,
    ): "Assert the LCS length is 3 and that precision 1, recall 0.75 and F1 6/7 follow from it.",
    (
        17,
        4,
    ): "Check that the record keeps the high overlap score and adds a contradiction label supported by the source sentence.",
    (
        17,
        5,
    ): "Assert family rates [0.5, 0] with equal-family mean 0.25, and report the row mean 1/3 as a different weighting.",
    (
        17,
        6,
    ): "Check that the record includes task, source, version, output, atomic support labels, metric configuration, rater or judge identity and an abstention case.",
    (
        18,
        1,
    ): "Assert len(text) == 4, len(text.encode('utf-8')) == 12 and len(text.split()) == 1 for the Chinese string.",
    (
        18,
        2,
    ): "Assert the cue rule returns en, es, None and None, abstaining on bank and on the mixed-cue sentence.",
    (
        18,
        3,
    ): "Assert the mark-stripped forms of résumé and resume are equal while the raw strings differ.",
    (
        18,
        4,
    ): "Assert 'İ'.lower() has length 2 (i plus a combining dot) and 'Straße'.casefold() == 'strasse'.",
    (
        18,
        5,
    ): "Assert per-language accuracies 0.9 and 0.5, pooled 5/6 and macro 0.7, and report the counts 10 and 2 beside them.",
    (
        18,
        6,
    ): "Check that the transfer plan names target labels, ambiguous charge cases, source/target family separation and an abstention policy.",
    (
        19,
        1,
    ): "Check that the rubric defines the annotation unit, both labels, an abstention or review rule and one counterexample near the boundary.",
    (
        19,
        2,
    ): "Assert raw agreement 2/3, expected agreement 1/2 and kappa 1/3, and that cohen_kappa_score matches within 1e-12.",
    (
        19,
        3,
    ): "Assert raw agreement 0.98 and a kappa slightly below 0 for the hundred-item prevalence case.",
    (
        19,
        4,
    ): "Assert the soft labels are [2/3, 1, 0] and that entropy is positive only for the disputed first row.",
    (
        19,
        5,
    ): "Assert the adjudication record keeps the original ratings (1, 1, 0) unchanged beside final label 1, its rationale and the item ID.",
    (
        19,
        6,
    ): "Assert raw agreement 1 and kappa None for the all-positive arrays, and check that the follow-up sample includes rare and ambiguous categories.",
    (
        20,
        1,
    ): "Assert coverage 0.75, overall conflict 0.25 and conflict 1/3 among covered rows, treating -1 as an abstention.",
    (20, 2): "Assert the votes are [1, 0, -1, -1], with ties and all-abstain rows returning -1.",
    (
        20,
        3,
    ): "Assert the raw votes [1, 1, 0] give 1 while the collapsed family votes [1, 0] give an abstention.",
    (
        20,
        4,
    ): "Assert the two highest-entropy indices are [0, 1] and that p = 0.5 attains the maximum binary entropy.",
    (
        20,
        5,
    ): "Assert the selection is [0, 3], no family appears twice and budget 0 returns an empty list.",
    (
        20,
        6,
    ): "Check that the experiment ledger keeps query and gold IDs disjoint and records each reviewed item's provenance.",
    (
        21,
        1,
    ): "Assert the two normalized hashes are equal while the original strings are unchanged and still differ.",
    (
        21,
        2,
    ): "Assert the token-set Jaccard of ready and not ready is 0.75, then record that the two status claims contradict.",
    (21, 3): "Assert train `[a1, a2, b1]`, test `[c1]` and excluded `[b2]` for cutoff 2.",
    (
        21,
        4,
    ): "Assert every training time precedes every test time, train and test families are disjoint, and the learned transforms are listed as training-only.",
    (21, 5): "Assert the equal-family mean is 2/15 and the row-weighted mean is 0.2.",
    (
        21,
        6,
    ): "Assert two runs with the same seed return identical quantiles inside [-0.1, 0.3], and check that the claim is limited to three families.",
    (
        22,
        1,
    ): "Assert router's postings are {d0, d1} and that its term frequency and document frequency are stored separately.",
    (
        22,
        2,
    ): "Assert the implementation matches the explicit BM25 formula for d0 and that d0 > d1 > d2 = 0.",
    (
        22,
        3,
    ): "Assert every score for unseen is 0, and check that the application reports no lexical evidence instead of a top result.",
    (
        22,
        4,
    ): "Assert b ranks first with score 1/62 + 1/61 and that a ranking containing a duplicate ID is rejected.",
    (
        22,
        5,
    ): "Assert MRR 0.5 and nDCG (7/log2(3) + 3/2)/(7 + 3/log2(3)) for the ranking [d2, d0, d1].",
    (
        22,
        6,
    ): "Assert only d0 appears after restricting the corpus, and check that the handoff records source version and support limits.",
    (
        23,
        1,
    ): "Assert ops at time 10 receives only policy version 2, while an unknown role or time 30 receives no records.",
    (
        23,
        2,
    ): "Assert reversing the record order leaves the hash unchanged and editing one text field changes it.",
    (
        23,
        3,
    ): "Assert the total variation distance is 0.3 and that negative, nonfinite and zero-total count vectors are rejected.",
    (
        23,
        4,
    ): "Assert two mature cases with accuracy 1, and that the all-unknown batch reports count 0 and no accuracy.",
    (
        23,
        5,
    ): "Assert the stored text is unchanged and inert, and that only the declared synthetic email pattern is replaced.",
    (
        23,
        6,
    ): "Check that the incident record separates the observed failure, hypothesis, authorized action and verified recovery, with versions and acceptance evidence.",
    (
        24,
        1,
    ): "Assert the training and held-out family sets are disjoint and that the two held-out labels match the network and billing probes.",
    (
        24,
        2,
    ): "Assert TKT-301 is returned canonically and that the missing, multiple and four-digit variants each raise ValueError.",
    (
        24,
        3,
    ): "Assert the represented probes receive their expected labels and the botanical specimen message is reported as unsupported vocabulary.",
    (
        24,
        4,
    ): "Assert exactly one record, network version 2, is returned for ops at time 10 with the approval-rule quote unchanged and the old version absent.",
    (
        24,
        5,
    ): "Assert the billing role and time 30 both return insufficient evidence and malformed IDs raise parser errors, with no stale or unauthorized quote.",
    (
        24,
        6,
    ): "Check that the packet's evidence hash and component identities let a reviewer reproduce parsing, prediction, source eligibility and quote provenance.",
}
