"""Lesson-specific key terms for nlp-005 through nlp-024, keyed by lesson number.

author.py renders each entry as a `## Key terms` list after the purpose section.
"""

KEY_TERMS = {
    5: [
        (
            "Morphology",
            "The study of word formation and meaningful word parts. Inflection changes grammatical features, as in study and studies, while derivation forms related words, as in teach and teacher.",
        ),
        (
            "Stemmer",
            "An algorithmic reduction that produces a retrieval key, which need not be a valid word and is not a linguistic root.",
        ),
        (
            "Lemmatizer",
            "A mapping from a surface form to a dictionary-like base form under a grammatical interpretation, so it may need part of speech, as in better as an adjective mapping to good.",
        ),
        (
            "Part of speech",
            "A token's grammatical role in context. Saw is a verb in I saw her and a noun in the saw broke, so a one-token rule fails on the old saw.",
        ),
        (
            "Dependency tree",
            "A structure in which each token points to one head and exactly one root has no head. A validator can prove legal indices, one root and no cycles, but a valid tree can still attach words incorrectly.",
        ),
    ],
    6: [
        (
            "Bigram model",
            "A language model that conditions each next-token probability only on the immediately preceding token, with counts reset at sentence boundaries.",
        ),
        (
            "Additive smoothing",
            "Estimating `(C(context, word) + alpha) / (C(context) + alpha * V)`, which gives every vocabulary item some probability. Larger alpha moves a row closer to uniform.",
        ),
        (
            "Sentence markers",
            "BOS supplies the first context and is never predicted, while EOS is a predicted event that belongs in the perplexity denominator.",
        ),
        (
            "Unknown token",
            "A fixed vocabulary entry that receives probability for unseen evaluation words, so scoring never adds new vocabulary items.",
        ),
        (
            "Perplexity",
            "The exponential of the negative average log probability per predicted event. It is `sqrt(10)` for we like tea here and cannot be compared casually across tokenizers or vocabularies.",
        ),
    ],
    7: [
        (
            "Term frequency",
            "The count of a term within one document; repeated occurrences of tea in a document all count.",
        ),
        (
            "Document frequency",
            "The number of training documents that contain a term at least once, so changing document boundaries changes it.",
        ),
        (
            "Smoothed IDF",
            "The weight `log((1 + n) / (1 + df)) + 1` with the natural logarithm, which is the scikit-learn convention with `smooth_idf=True`.",
        ),
        (
            "L2 normalization",
            "Dividing each nonzero row by its Euclidean norm, so the dot product of two normalized rows equals their cosine similarity.",
        ),
        (
            "Sparse matrix",
            "A matrix that stores only nonzero entries, which matters when each document uses a small fraction of a large vocabulary.",
        ),
    ],
    8: [
        (
            "Multinomial Naive Bayes",
            "A probabilistic classifier for nonnegative token counts that combines a class prior with per-class token probabilities through Bayes' rule.",
        ),
        (
            "Class prior",
            "The probability of a class before token evidence. Changing it to `[0.9, 0.1]` can flip a prediction while the token likelihoods stay fixed.",
        ),
        (
            "Smoothed token probability",
            "The estimate `(N_cj + alpha) / (sum_j N_cj + alpha * V)` of term j within class c, which keeps unseen class-term pairs above zero.",
        ),
        (
            "Conditional independence",
            "The assumption that token events are independent given the class. Correlated phrases violate it and can produce overconfident probabilities.",
        ),
        (
            "Log-sum-exp",
            "A stable computation of the log of a sum of exponentials, used to normalize log scores into posterior probabilities without underflow.",
        ),
    ],
    9: [
        (
            "Log odds",
            "The linear score `z = w^T x + b`. Each coefficient `w_j` changes it by `w_j` per additional occurrence of feature j, holding the other represented features fixed.",
        ),
        (
            "Binary cross-entropy",
            "The loss `-y * log(p) - (1 - y) * log(1 - p)`, which penalizes confident mistakes strongly.",
        ),
        (
            "L2 regularization",
            "A penalty on coefficient magnitude that reduces variance; in scikit-learn a smaller `C` means a stronger penalty.",
        ),
        (
            "Pipeline",
            "A `make_pipeline` chain of `CountVectorizer` and `LogisticRegression`, so the vocabulary is fitted on training text only and then frozen.",
        ),
        (
            "Brier score",
            "The mean squared difference between predicted probability and the 0 or 1 outcome. It mixes calibration and discrimination effects.",
        ),
    ],
    10: [
        (
            "Hidden Markov model",
            "A sequence model with hidden label transitions and observed token emissions, defined by initial, transition and emission probabilities.",
        ),
        (
            "Emission probability",
            "The probability of the observed token under a given state. Rows of the per-position emission array need not sum to one.",
        ),
        (
            "Viterbi recurrence",
            "`D_t(j) = log b_j(x_t) + max_i [D_(t-1)(i) + log a_ij]`, which keeps only the best partial path into each state and needs `O(T K^2)` work.",
        ),
        (
            "Backpointer",
            "The stored best predecessor for each state and position, followed in reverse from the best final state to recover the label path.",
        ),
        (
            "BIO tagging",
            "B-TYPE begins an entity, I-TYPE continues it and O is outside. Under the strict policy here, I-ORG cannot start a sequence or follow O.",
        ),
    ],
    11: [
        (
            "Named-entity recognition",
            "Identifying spans that name people, organizations, locations or other declared types.",
        ),
        (
            "Mention",
            "A typed half-open `[start, end)` span in a particular raw document. Identical names at different positions are different mentions.",
        ),
        (
            "Entity linking",
            "Associating a mention with a canonical entity in a knowledge base, a separate step from finding the span.",
        ),
        (
            "Coreference",
            "Grouping mentions that refer to the same entity within or across texts, such as resolving it to an earlier name.",
        ),
        (
            "Relation extraction",
            "Identifying a typed, directed relationship between mentions, such as which company acquired which. Negated or speculative statements should yield no confirmed relation.",
        ),
    ],
    12: [
        (
            "Co-occurrence matrix",
            "Counts of how often each target word appears with each context feature under a declared window, without crossing document boundaries.",
        ),
        (
            "Pointwise mutual information",
            "`log(C_ij * N / (C_i+ * C_+j))`, which compares an observed co-occurrence count with its expectation under independence.",
        ),
        (
            "Positive PMI",
            "PMI with negative values replaced by zero; zero counts stay zero instead of becoming negative infinity.",
        ),
        (
            "Truncated SVD",
            "A rank-k decomposition whose embedding here is `U_k diag(s_k)`, giving the best least-squares rank-k approximation of the matrix.",
        ),
        (
            "Cosine similarity",
            "The dot product divided by the product of vector norms. It is undefined for a zero vector, so the reference returns `None`.",
        ),
    ],
    13: [
        (
            "Topic",
            "A model component with a pattern of word weights. It is not automatically a real category, and analysts label it after inspecting words and documents.",
        ),
        (
            "Latent semantic analysis",
            "A truncated SVD of a term-document matrix, often TF-IDF. Components can carry negative weights, so coordinates are not probabilities.",
        ),
        (
            "Nonnegative matrix factorization",
            "An approximation of X by the product of nonnegative factors W and H, linking documents to components and components to words, with scaling and permutation ambiguity.",
        ),
        (
            "Latent Dirichlet allocation",
            "A generative probabilistic model in which documents have topic mixtures and topics generate words from topic-specific distributions.",
        ),
        (
            "Component alignment",
            "Matching components across fits, for example by cosine similarity over one vocabulary, because topic indices are arbitrary.",
        ),
    ],
    14: [
        (
            "Bi-encoder",
            "A model that maps queries and documents separately, so document embeddings can be precomputed and searched.",
        ),
        (
            "Masked mean pooling",
            "Averaging token vectors over valid positions only, dividing by the number of valid tokens rather than the padded length.",
        ),
        (
            "Contrastive loss",
            "A batch loss, `-log(exp(S_ii / tau) / sum_j exp(S_ij / tau))`, that pushes each query to score its paired document above the other candidates.",
        ),
        (
            "Temperature",
            "The scale tau that controls how strongly score differences affect the contrastive softmax distribution.",
        ),
        (
            "In-batch false negative",
            "A relevant document that the batch labels as a negative, which teaches the model to push away valid evidence.",
        ),
    ],
    15: [
        (
            "Contextual encoder",
            "A model that gives one token different vectors depending on the surrounding sequence, as with bank near river and bank near money.",
        ),
        (
            "Scaled dot-product attention",
            "Row softmax of `Q K^T / sqrt(d_k)` applied to V, returning one context-mixed vector for each query position.",
        ),
        (
            "Bidirectional attention",
            "Attention in which every valid position can attend to every other valid position. It suits an observed input but would leak future targets in a next-token decoder.",
        ),
        (
            "Padding mask",
            "A mask that stops padded positions from contributing to valid outputs; a large padded vector is a useful negative control.",
        ),
        (
            "Classification head",
            "The output layer that maps a pooled representation to class scores. Here only this logistic head is trained by gradient steps.",
        ),
    ],
    16: [
        (
            "Cross-attention",
            "Attention with decoder queries and encoder keys and values, giving target-length by source-length scores.",
        ),
        (
            "Causal mask",
            "A mask that lets each decoder position attend only to earlier target positions. A source padding mask does not replace it.",
        ),
        (
            "Teacher forcing",
            "Training that feeds the correct shifted target prefix, so decoder input `[BOS, repair]` predicts targets `[repair, EOS]`.",
        ),
        (
            "Beam search",
            "Decoding that keeps a bounded set of partial sequences. Width two finds the coffee path with joint probability 0.4, which greedy decoding misses.",
        ),
        (
            "Extractive summarization",
            "Selecting source spans or sentences rather than generating new wording; the baseline returns a sentence index and abstains without overlap.",
        ),
    ],
    17: [
        (
            "Clipped n-gram precision",
            "Candidate n-gram counts limited to the counts available in the reference, so repetition cannot inflate precision.",
        ),
        (
            "Brevity penalty",
            "`BP = min(1, exp(1 - r / c))` for candidate length `c > 0`, which discourages short candidates with high local precision.",
        ),
        (
            "ROUGE-L",
            "An overlap score built on the longest common subsequence, which preserves order but can skip tokens.",
        ),
        (
            "Atomic claim",
            "One checkable assertion from a generated text, judged separately for source support, such as a claim that a service is ready.",
        ),
        (
            "LLM judge",
            "A model used to score responses. It must be validated against expert or executable checks and must treat the candidate text as data.",
        ),
    ],
    18: [
        (
            "Script",
            "The writing system of a text. A Latin-script message is not automatically English, so script detection and language identification answer different questions.",
        ),
        (
            "Language identification",
            "Predicting a language label from available evidence, with an explicit abstention or mixed-language policy when evidence is tied or absent.",
        ),
        (
            "Tokenization equity",
            "Whether languages or writing systems need very different token budgets to express comparable content.",
        ),
        (
            "Case folding",
            "Aggressive case removal for caseless matching, which maps Straße to strasse and can change code-point length.",
        ),
        (
            "Domain shift",
            "A change in data distribution or word sense within or across languages, such as charge meaning a payment or a battery state.",
        ),
    ],
    19: [
        (
            "Annotation guide",
            "The contract that defines the unit, label inventory, inclusion and exclusion rules, ambiguous cases and abstention policy.",
        ),
        (
            "Raw agreement",
            "The fraction of items on which two raters assign the same label, which can be high merely because one label is common.",
        ),
        (
            "Cohen's kappa",
            "`(p_o - p_e) / (1 - p_e)`, agreement adjusted for the agreement expected from each rater's label frequencies; the six-item fixture gives one-third.",
        ),
        (
            "Adjudication",
            "Creating a final label after review while keeping the original independent judgments immutable.",
        ),
        (
            "Soft label",
            "The fraction of raters favoring a class, such as two-thirds. It records disagreement in the rater population, not the true probability of the class.",
        ),
    ],
    20: [
        (
            "Labeling function",
            "A rule or heuristic that emits class zero, class one or abstain. Abstaining means no applicable evidence, not the negative class.",
        ),
        (
            "Coverage",
            "The fraction of examples that receive at least one non-abstaining label; high coverage does not mean high accuracy.",
        ),
        (
            "Conflict",
            "The fraction of examples that receive both class-zero and class-one votes, reported with a stated denominator.",
        ),
        (
            "Uncertainty sampling",
            "Choosing examples for review where the current model is least certain, such as binary entropy near one-half.",
        ),
        (
            "Diversity constraint",
            "A selection limit, here at most one example per family, that keeps a review batch from filling with near duplicates.",
        ),
    ],
    21: [
        (
            "Future-new-family split",
            "An evaluation that requires both a time cutoff and unseen source families, so a known family's future message is excluded and logged.",
        ),
        (
            "Normalized hash",
            "A hash computed after a declared equivalence policy, here case folding and whitespace collapsing, which finds exact duplicates under that policy only.",
        ),
        (
            "Jaccard similarity",
            "Token-set intersection size divided by union size. Service is ready and service is not ready score three-quarters despite disagreeing.",
        ),
        (
            "Clustered bootstrap",
            "Resampling whole families with replacement so correlated variants stay together when estimating uncertainty.",
        ),
        (
            "Development set",
            "Held-out data used repeatedly for choices such as prompt revisions. It no longer supports a final untouched evaluation claim.",
        ),
    ],
    22: [
        (
            "Inverted index",
            "A map from each term to the IDs of the documents that contain it, which also supplies document frequency.",
        ),
        (
            "BM25",
            "A lexical ranking score in which k1 controls term-frequency saturation and b controls document-length normalization.",
        ),
        (
            "Reciprocal-rank fusion",
            "Combining ranked lists by summing `1 / (k + rank)` over one-based ranks, which avoids adding raw scores with different units.",
        ),
        (
            "nDCG",
            "A ranking metric with graded relevance gains and position discounts, normalized by the ideal ordering under a stated gain convention.",
        ),
        (
            "Access filtering",
            "Restricting the searchable collection to authorized documents before ranking, rather than hoping a later answer omits private text.",
        ),
    ],
    23: [
        (
            "Source version",
            "A record of document ID, version, availability time, validity interval, access scope and content, since a stable ID alone cannot show text changes.",
        ),
        (
            "Snapshot fingerprint",
            "A content hash over records sorted by ID and version with sorted JSON keys. It proves reproducible identity, not truth or approval.",
        ),
        (
            "Eligibility filter",
            "Including a source only when the requesting role is listed and the current time lies within its validity interval.",
        ),
        (
            "Total variation distance",
            "Half the sum of absolute probability differences, 0.3 for `[0.5, 0.5]` versus `[0.8, 0.2]`. It measures distribution movement, not prediction errors.",
        ),
        (
            "Mature label",
            "An outcome label already known at evaluation time. Accuracy uses only mature labels; treating unknown outcomes as negative creates false errors.",
        ),
    ],
    24: [
        (
            "Evidence packet",
            "The auditable output recording ticket ID, predicted category, evidence status, source-identified quoted evidence and a fingerprint of the evidence list.",
        ),
        (
            "Held-out family",
            "A family of related messages kept entirely out of training, here net-b and bill-b, to test transfer beyond memorized templates.",
        ),
        (
            "Identifier contract",
            "Exactly one ticket ID of the form `TKT-` plus three ASCII digits. Longer digit runs and multiple IDs are rejected rather than partially accepted.",
        ),
        (
            "Unsupported vocabulary",
            "The status returned when every message word is out of vocabulary, instead of a label driven only by the class prior.",
        ),
        (
            "Candidate filtering",
            "Checking the trusted role and validity time before lexical scoring, so expired or unauthorized procedures never become evidence.",
        ),
    ],
}
