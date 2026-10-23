# nlp-007: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Count documents, not occurrences

Tea appears twice but only in one document, so its document frequency is one. Cup appears once in each of two documents, so its DF is two. This distinction is the basis for the IDF weighting and is independent of the raw within-document counts.

**Expected:** [1,2,1] for [coffee,cup,tea].

## Exercise 2: Match the IDF formula

Different TF-IDF conventions omit one or more of these terms. The reference fixes the exact scikit-learn settings and checks the resulting array, so agreement is about a specified implementation rather than the vague label TF-IDF.

**Expected:** [log(3/2)+1,1,log(3/2)+1] in the verified vocabulary order.

## Exercise 3: Build the normalized rows

The first tea coordinate is twice its IDF because raw TF is two. Dividing by each row's L2 norm changes all nonzero coordinates together. Comparing every coordinate catches vocabulary-order and normalization mistakes that one retrieval score might miss.

**Expected:** Manual dense oracle matches the 2-by-3 sparse result within tolerance.

## Exercise 4: Compute sparse cosine

The query has only the tea coordinate, so the score reads that coordinate from each normalized document. This exact small calculation verifies the sparse API path. It does not establish that the highest lexical score is the best answer for a real user.

**Expected:** First score 2a/sqrt(1+4a^2); second score zero.

## Exercise 5: Handle OOV without refitting

Refitting on the query would alter the column space and make comparisons invalid. The zero vector needs a declared fallback because cosine is not geometrically defined for a zero norm even though sparse dot products return numerical zeros.

**Expected:** Zero nonzero entries and unchanged vocabulary; record an explicit no-known-terms outcome.

## Exercise 6: Change one weighting choice

Sublinear TF reduces the influence of repeated words while leaving IDF unchanged. This controlled comparison shows which part of the representation changed. Select the choice using the downstream task and an honest evaluation split, not from one favorable query.

**Expected:** Tea weight becomes (1+log(2))*a, distinct from 2a.

## Transfer and limits

Bag-of-words representations turn documents into vectors whose coordinates correspond to a fixed vocabulary. A count says how often a term appears in one document. Document frequency says in how many training documents it appears. TF-IDF combines within-document frequency with a corpus-level rarity weight, providing a useful sparse baseline for classification and retrieval.

The unit is one document, not one token or one customer. Repeated occurrences of tea in a document increase term frequency but count only once toward document frequency. Changing the document boundaries therefore changes IDF even if the concatenated text is unchanged. Preserve the corpus definition and fit the vocabulary/IDF only on the training or indexed collection appropriate to the evaluation claim.

This lesson derives the exact smoothing and normalization convention used by a real scikit-learn TfidfVectorizer. TF-IDF is a family of weighting choices, so an undocumented formula can produce a valid-looking vector different from a library's result. We compare every coordinate against a hand-built oracle before using cosine scores.

## Mechanism review and counterexample

A unigram representation ignores order, so dog bites person and person bites dog share the same counts. It can also lose negation, domain synonyms and spelling variants. Character n-grams, word n-grams or other representations may address some failures, but each changes the vocabulary and evaluation contract. A dense embedding is another candidate, not an automatic replacement for a useful lexical baseline.

IDF is not a truth or importance score. A rare typo can get a high weight, while a common domain term can be essential to the task. Inspect tokenization, stopwords and minimum-frequency policies rather than treating every high-IDF term as meaningful. Fitting IDF on an evaluation collection can be appropriate for a clearly transductive retrieval setup, but it cannot be silently described as a training-only inductive experiment.

The reference checks raw counts, IDF values, normalized vectors, cosine, sublinear TF and frozen unknown-token behavior separately. This decomposition helps locate a mismatch: a wrong document frequency differs from a right vector with the wrong normalization or vocabulary order.
