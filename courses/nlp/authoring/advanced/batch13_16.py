from author import author

solution13 = r"""
import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.decomposition import TruncatedSVD,NMF,LatentDirichletAllocation

DOCS=["cat kitten pet","dog puppy pet","car wheel road","truck wheel road"]

def aligned_similarity(a,b):
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
    if a.shape!=b.shape:raise ValueError("same topic and vocabulary dimensions required")
    an=np.linalg.norm(a,axis=1,keepdims=True);bn=np.linalg.norm(b,axis=1,keepdims=True)
    if np.any(an==0) or np.any(bn==0):raise ValueError("nonzero topics required")
    similarity=(a/an)@(b/bn).T
    rows,cols=linear_sum_assignment(-similarity)
    return cols,similarity[rows,cols]

def main():
    vectorizer=CountVectorizer();counts=vectorizer.fit_transform(DOCS)
    tfidf=TfidfTransformer().fit_transform(counts)
    lsa=TruncatedSVD(n_components=2,random_state=0).fit(tfidf)
    z=lsa.transform(tfidf)
    assert z.shape==(4,2)
    reconstructed=z@lsa.components_
    assert np.linalg.norm(tfidf.toarray()-reconstructed)<np.linalg.norm(tfidf.toarray())
    assert np.allclose((-z)@(-lsa.components_),reconstructed)
    nmf=NMF(n_components=2,init="nndsvda",random_state=0,max_iter=1000)
    w=nmf.fit_transform(counts);h=nmf.components_
    assert np.all(w>=0) and np.all(h>=0) and w.shape==(4,2)
    pet=vectorizer.vocabulary_["pet"];wheel=vectorizer.vocabulary_["wheel"]
    assert np.argmax(h[:,pet])!=np.argmax(h[:,wheel])
    lda=LatentDirichletAllocation(n_components=2,learning_method="batch",max_iter=30,random_state=0)
    proportions=lda.fit_transform(counts)
    assert proportions.shape==(4,2) and np.allclose(proportions.sum(axis=1),1.)
    cols,scores=aligned_similarity(h,h[::-1])
    assert cols.tolist()==[1,0] and np.allclose(scores,1.)
    before=vectorizer.vocabulary_.copy()
    heldout=vectorizer.transform(["newplanet pet"])
    assert "newplanet" not in before and vectorizer.vocabulary_==before and heldout.shape[1]==counts.shape[1]
    print("nlp-013: actual LSA/NMF/LDA shapes and constraints; permutation-aligned topic comparison passed")

if __name__ == "__main__":
    main()
"""
author(
    13,
    """Topic discovery tries to summarize recurring structure in a document collection without a supplied class label for every document. A topic is a model component with a pattern of word weights or probabilities. It is not automatically a real organizational category, a causal factor or a uniquely defined human concept. Analysts label components after inspecting representative words and documents.

This lesson fits three actual local models to four authored documents: latent semantic analysis through truncated SVD, nonnegative matrix factorization and latent Dirichlet allocation. Their outputs can all be displayed as document-by-component arrays, but the mathematical meanings differ. Confusing those meanings can turn an arbitrary coordinate into an unjustified topic probability.

The corpus intentionally separates pet-related and vehicle-related vocabulary so the fitted behavior is easy to inspect. A successful separation on this constructed corpus is a mechanism demonstration, not evidence that the method will discover reliable topics in messy reviews, support tickets or scientific literature.""",
    [
        (
            "Compare three objectives before comparing plots",
            """LSA applies a low-rank linear decomposition to a term-document representation, often TF-IDF. It seeks a useful approximation in a vector space, and components can have positive or negative weights. A document coordinate is not inherently a probability. Flipping the sign of a component and its document coordinates leaves the reconstruction unchanged, which already shows why a coordinate label is not unique.

NMF approximates a nonnegative matrix X by W*H with W and H constrained nonnegative. W associates documents with components, while H associates components with words. The additive representation can be easier to inspect, but the factors have scaling and permutation ambiguities. Multiplying one W column by a positive constant and dividing the corresponding H row by the same constant preserves the product. Normalizing a row for display does not retroactively make it a posterior probability.

LDA is a generative probabilistic model: documents have topic mixtures, and topic assignments generate words from topic-specific distributions. Dirichlet priors control mixture behavior, while approximate inference estimates latent quantities. It uses count events under a bag-of-words assumption. Fitting LDA directly to arbitrary signed features would not match that model. The normalized document-topic output has a probabilistic interpretation conditional on the model and inference approximation.""",
        ),
        (
            "Syntax anatomy and the fitted corpus boundary",
            """CountVectorizer fixes word columns from DOCS. TfidfTransformer derives a weighted representation for the LSA example, while NMF and LDA here receive the nonnegative count matrix. TruncatedSVD avoids centering a sparse matrix, which differs from ordinary centered PCA. n_components=2 chooses a model capacity; it is not a discovered fact that the world contains exactly two topics.

fit_transform estimates the model and document representations together on the training collection. transform applies the fixed vocabulary or model to new documents. The held-out word newplanet must not enter the vocabulary during this step. If the intended task is exploratory analysis of one fixed corpus, fitting that corpus can be appropriate; if claiming generalization to future documents, preserve a separate future or family-level evaluation.

The reference checks shapes, nonnegative factors, normalized LDA rows and reconstruction improvement against a zero approximation. These are computational invariants. They do not prove coherent or useful topics. Convergence warnings, sensitivity to initialization and tiny effective sample size are important diagnostics rather than messages to suppress automatically.""",
        ),
        (
            "Evaluate coherence, stability and analytical use",
            """Topic coherence asks whether a component\'s high-weight words make sense together under a chosen statistical or human criterion. A coherence score can favor common co-occurrence patterns without producing useful distinctions for the application. Inspect top words, representative documents, mixed documents and obvious counterexamples. Compare with simple keyword categories when those already solve the decision problem.

Topic numbers are arbitrary. Topic zero in one fit can correspond to topic one in another. Comparing raw indices across seeds would falsely declare instability. Align components through a matching criterion, such as cosine similarity over the same vocabulary, before comparing. Even aligned components can change meaning when the corpus or preprocessing changes; retain vocabulary and corpus versions.

Do not use estimated topic weights as error-free measurements in later causal or predictive analysis. The topic model was learned from data, may encode sensitive proxies and can change across retraining. A business report should describe the model and its uncertainty, include examples supporting a component label, and avoid naming a cluster after a conclusion the model did not identify.""",
        ),
    ],
    [
        (
            "Inspect the same corpus through three models",
            """The documents are cat kitten pet, dog puppy pet, car wheel road and truck wheel road. The reference fits real two-component SVD, NMF and LDA models. It checks the corresponding document-array shape (4,2), nonnegativity where required and LDA row sums of one. These properties are different contracts even though all three arrays have the same dimensions.""",
        ),
        (
            "Demonstrate non-unique coordinates",
            """If Z contains LSA document coordinates and H its components, then (-Z)*(-H)=Z*H. The reconstruction is unchanged while every coordinate sign flips. Likewise, reversing NMF topic order and the corresponding weights changes labels but not the represented model. Numerical component identity is not semantic identity.""",
        ),
        (
            "Align a permuted fit",
            """The reference deliberately reverses the two NMF component rows, computes pairwise cosine similarity and solves a maximum-similarity assignment. The match is [1,0] with similarity one for both pairs. This validates the alignment mechanism on a known permutation; real retrained topics can have genuinely imperfect matches.""",
        ),
    ],
    [
        (
            "Build the corpus matrix",
            "Fit a count vocabulary on the four authored documents and retain its column mapping.",
            "Four rows with a fixed vocabulary; held-out newplanet does not add a column.",
            "Inspect get_feature_names_out and use transform for the probe.",
            "The row unit is a document and the columns are learned terms. A new evaluation word has no fitted coordinate under this vocabulary. Recording the mapping makes subsequent component weights interpretable and prevents accidental comparison of arrays with different word orders.",
        ),
        (
            "Fit and inspect LSA",
            "Fit two-component TruncatedSVD on TF-IDF and reconstruct the matrix.",
            "Document coordinates shape(4,2); reconstruction error below the zero-matrix baseline.",
            "Use transform output times components_ without claiming probability meaning.",
            "The low-rank representation preserves some large-scale variation while discarding other directions. A lower reconstruction error than the zero baseline verifies useful matrix approximation on the fixture. It does not establish coherent human topics or a good downstream classifier.",
        ),
        (
            "Fit nonnegative components",
            "Fit two-component NMF on counts and inspect pet and wheel loadings.",
            "W and H nonnegative; pet and wheel have different dominant component indices.",
            "Use a deterministic initialization and record convergence behavior.",
            "Nonnegativity makes each reconstruction additive. The authored corpus separates the two vocabulary groups, so their shared terms load on different components. The factor magnitudes still have scaling ambiguity and are not automatically topic probabilities.",
        ),
        (
            "Inspect LDA mixtures",
            "Fit actual two-topic LDA to the count matrix and inspect document mixtures.",
            "Four rows, two columns and each row sums to one.",
            "Use count events rather than signed LSA coordinates.",
            "The output is a normalized inferred topic mixture under LDA's generative assumptions. The normalization check catches malformed consumption but does not prove the topics are correct. Topic count, priors and approximate inference all influence the result.",
        ),
        (
            "Align topic identities",
            "Compare H with its reversed row order using cosine and assignment.",
            "Permutation[1,0] and matched similarities[1,1].",
            "Match across the shared vocabulary before comparing numeric topic IDs.",
            "The deliberate permutation is a known-answer test for the alignment step. Raw row equality would fail despite identical components. Real stability analysis should also resample documents or vary seeds and inspect imperfect matches, not only this artificial exact case.",
        ),
        (
            "Write an error-aware topic interpretation",
            "Label one component using top words and source documents, then state what remains unproven.",
            "A label linked to concrete words/documents, plus limits on uniqueness, coherence and downstream causal meaning.",
            "Keep the component ID, corpus version and human label separate.",
            "A human label is an interpretation supported by inspected examples, not a latent truth emitted by the estimator. A useful report also shows mixed or poorly represented documents and explains how labels may change after retraining. Treat learned topic features as estimates when they feed later analysis.",
        ),
    ],
    """
DOCS=["cat kitten pet","dog puppy pet","car wheel road","truck wheel road"]

def fit_and_compare(documents):
    raise NotImplementedError("Fit the three specified models and inspect their different contracts")

def main():
    print("Four authored documents loaded. Keep numerical component IDs separate from human labels.")

if __name__ == "__main__":
    main()
""",
    solution13,
    [
        """**Interview: Are NMF weights topic probabilities?** Not by the factorization alone. They are nonnegative factors with scaling ambiguity. A display normalization is a useful convention but does not change the original optimization into a probabilistic generative model.""",
        """**Interview: Why align topics across runs?** Component indices and some coordinate conventions are arbitrary. Compare matched components over the same vocabulary before attributing a difference to instability.""",
        """**Interview: How would you assess topic usefulness?** Inspect representative and counterexample documents, coherence and stability, then evaluate the actual downstream decision. A low reconstruction loss or attractive word cloud is insufficient.""",
    ],
    [
        "[Blei, Ng and Jordan, Latent Dirichlet Allocation](https://jmlr.org/papers/v3/blei03a.html)",
        "[scikit-learn decomposition APIs](https://scikit-learn.org/stable/modules/decomposition.html)",
    ],
)

solution14 = r"""
import numpy as np
from scipy.special import logsumexp

VECTORS={"car":np.array([1.,0.,0.]),"automobile":np.array([.9,.1,0.]),
         "repair":np.array([.8,.2,0.]),"dog":np.array([0.,0.,1.]),
         "pet":np.array([0.,.1,.9]),"bites":np.array([.2,.2,.2]),
         "person":np.array([.4,.4,.4])}

def pooled(tokens):
    if not tokens:raise ValueError("empty token sequence")
    if any(token not in VECTORS for token in tokens):raise ValueError("unknown token")
    value=np.mean([VECTORS[token] for token in tokens],axis=0)
    norm=np.linalg.norm(value)
    if norm==0:raise ValueError("zero representation")
    return value/norm

def masked_mean(values,mask):
    values=np.asarray(values,dtype=float);mask=np.asarray(mask,dtype=bool)
    if values.ndim!=2 or mask.shape!=(len(values),) or not mask.any():raise ValueError("nonempty valid-token mask required")
    return values[mask].mean(axis=0)

def contrastive_loss(scores,temperature=1.):
    scores=np.asarray(scores,dtype=float)
    if scores.ndim!=2 or scores.shape[0]!=scores.shape[1] or temperature<=0:raise ValueError("square scores and positive temperature required")
    scaled=scores/temperature
    return float(np.mean(logsumexp(scaled,axis=1)-np.diag(scaled)))

def main():
    docs=[pooled(["car","repair"]),pooled(["dog","pet"])]
    query=pooled(["automobile","repair"])
    scores=np.array(docs)@query
    assert scores[0]>scores[1] and np.isclose(np.linalg.norm(query),1.)
    assert np.allclose(pooled(["dog","bites","person"]),pooled(["person","bites","dog"]))
    values=np.array([[1.,2.],[3.,4.],[100.,100.]])
    assert np.allclose(masked_mean(values,[1,1,0]),[2.,3.])
    score_matrix=np.array([[3.,1.],[1.,3.]])
    assert np.isclose(contrastive_loss(score_matrix),np.log1p(np.exp(-2)))
    assert contrastive_loss(score_matrix,.5)<contrastive_loss(score_matrix,1.)
    try:pooled(["unknown"])
    except ValueError:pass
    else:raise AssertionError("unknown word silently encoded")
    try:masked_mean(values,[0,0,0])
    except ValueError:pass
    else:raise AssertionError("all-padding mean accepted")
    print("nlp-014: explicit pooled geometry, masked mean, contrastive loss and order-loss counterexample passed")

if __name__ == "__main__":
    main()
"""
author(
    14,
    """Sentence representations map variable-length text to a fixed-length vector so sentences or documents can be compared efficiently. A vector can support semantic search, clustering or a downstream classifier, but its usefulness depends on how it was constructed and trained. The same cosine function applied to arbitrary vectors does not create semantic understanding.

This lesson uses explicitly handcrafted token vectors to make pooling and retrieval geometry inspectable, plus an exact contrastive-loss calculation. These vectors were chosen by the author and are not learned word embeddings or outputs from a pretrained sentence encoder. The success of the car/automobile example is built into that fixture. The real learning question is how a trained representation acquires and generalizes such relationships.

A bi-encoder maps queries and documents separately, enabling document embeddings to be precomputed and searched. A cross-encoder jointly processes a query-document pair, allowing richer interactions but usually requiring more work per candidate. A practical search system can retrieve with a bi-encoder and rerank a small set with a cross-encoder. Their quality and latency must be measured as separate pipeline stages.""",
    [
        (
            "Pooling, masks and representation geometry",
            """Given token vectors h_1,...,h_T, mean pooling computes their average over valid positions. Padding is an implementation convenience and should not contribute unless the model explicitly treats it as content. A masked mean divides by the number of valid positions, not the padded sequence length. An all-padding input has no valid mean and should raise or return an explicit unsupported result.

After pooling, L2 normalization maps a nonzero vector to unit length. Dot products then equal cosine similarity. Without normalization, large vector norms can influence scores, which may or may not match the training objective. The index metric, query normalization and document normalization must agree with the trained representation contract.

Mean pooling of fixed token vectors ignores order. Dog bites person and person bites dog use the same multiset and therefore get identical means, despite different event roles. A contextual encoder can make token vectors depend on surrounding words before pooling, but merely averaging static vectors does not solve the problem. Keep this counterexample in evaluation rather than hiding it behind a synonym probe.""",
        ),
        (
            "Contrastive learning and negative examples",
            """Contrastive training encourages a query to score its relevant partner above alternatives. For a batch of paired examples with score matrix S, one common row loss is -log[exp(S_ii/tau)/sum_j exp(S_ij/tau)]. The temperature tau scales how strongly score differences affect the distribution. logsumexp computes the denominator stably.

With scores [[3,1],[1,3]] and temperature one, each correct-pair probability is exp(3)/(exp(3)+exp(1)), and average loss is log(1+exp(-2)), about 0.12693. Reducing temperature to one-half lowers the loss on these already correctly ordered scores. It does not prove better generalization or calibrated relevance probabilities.

Negative selection matters. If a batch contains two equally valid documents for a query but labels only one as positive, the other becomes a false negative and training pushes useful content away. Easy random negatives can produce excellent training loss while failing difficult near-miss retrieval. Construct negatives and evaluation candidates from the deployment task, preserving source-family separation.""",
        ),
        (
            "From vector search to supported evidence",
            """A semantic score is an association under a representation, not an entailment judgment. A passage about approving a restart can be near a query about a completed restart without proving that any restart occurred. Retrieval should preserve document IDs, dates, access metadata and source spans so later stages can inspect what the text actually supports.

Evaluate recall at a candidate budget before evaluating the final answer. If the required passage is absent from the retrieved set, a downstream generator has no supplied evidence for that part of the task. Conversely, high retrieval recall does not prove that a generator interprets the passages faithfully. The applied LLM route separates these boundaries in grounded-answer evaluation.

A real pretrained sentence model adds learned parameters, its exact tokenizer, pooling convention, model version, training objective and resource requirements. This offline lesson downloads none of them. When using one later, record and cache the complete artifact set deliberately and compare against the TF-IDF baseline from nlp-007 on the same held-out queries.""",
        ),
    ],
    [
        (
            "Pool a declared synonym fixture",
            """The handcrafted car vector is [1,0,0], automobile [0.9,0.1,0] and repair [0.8,0.2,0]. Mean-pooling and normalization make automobile repair closer to car repair than to dog pet. This is a numerical geometry demonstration whose semantic relationship was supplied by the author, not discovered by a trained model.""",
        ),
        (
            "Exclude padding and expose order loss",
            """Vectors [1,2] and [3,4] with a padded [100,100] row and mask [1,1,0] average to [2,3]. Including padding would produce a very different result. Separately, reversing dog and person around bites leaves a static mean unchanged. Correct masking and semantic adequacy are different checks.""",
        ),
        (
            "Calculate a contrastive objective",
            """Scores three on the diagonal and one off the diagonal yield loss log(1+exp(-2)) at temperature one. The loss compares each positive to the candidate negatives in its row. Changing the candidate set or temperature changes the objective even if the encoder vectors stay fixed.""",
        ),
    ],
    [
        (
            "Implement masked mean",
            "Average the three-row fixture using only the two valid positions.",
            "[2,3]; all-padding input raises ValueError.",
            "Select valid rows and divide by their count.",
            "Padding rows are outside the modeled sentence. The deliberately large padded vector makes accidental inclusion obvious. A denominator based on total padded length would also be wrong even if padding values were zero, because it would shrink the representation.",
        ),
        (
            "Normalize nonzero vectors",
            "Pool and normalize the authored car/repair and automobile/repair sequences.",
            "Each result has unit norm and their similarity exceeds the dog/pet alternative.",
            "State that the token vectors are handcrafted, then compute the geometry.",
            "Normalization makes dot product a cosine comparison. The ranking is a consequence of the supplied vectors, so it tests implementation rather than language-model quality. A learned representation requires an independent corpus and evaluation to support semantic claims.",
        ),
        (
            "Preserve the order counterexample",
            "Compare dog bites person with person bites dog under static mean pooling.",
            "Exactly matching pooled vectors despite different role meaning.",
            "Addition is commutative, so the token multiset determines the mean.",
            "This failure follows mathematically from the representation. Increasing nearest-neighbor search accuracy cannot recover an ordering distinction that was discarded before indexing. A contextual or structured representation is a candidate repair that must be tested on role-sensitive examples.",
        ),
        (
            "Derive contrastive loss",
            "Compute row-wise loss for scores[[3,1],[1,3]] at temperature1.",
            "Average log(1+exp(-2)), approximately .126928.",
            "Subtract the positive score from each row logsumexp.",
            "Each row has the same two-score gap, so both losses agree. The stable expression avoids unnecessary exponent overflow. This is one objective calculation, not a training run or a calibration guarantee for relevance probabilities.",
        ),
        (
            "Change temperature and candidate semantics",
            "Repeat at temperature.5 and explain a false-negative document case.",
            "Lower numeric loss on the fixed correctly ordered fixture; written warning that a valid alternative labeled negative changes the learning target.",
            "Scale the whole score row before normalization.",
            "A smaller temperature sharpens differences and lowers this fixture's loss because the positives already win. It can worsen other training dynamics or emphasize mislabeled negatives. The candidate set and label quality therefore matter as much as the algebra.",
        ),
        (
            "Specify a retrieval handoff",
            "Write a result record for a retrieved passage and reject an unknown-token query in the toy encoder.",
            "Record contains source identity/version/text span/score; unsupported token raises instead of inventing an embedding.",
            "Keep retrieval association separate from claim support.",
            "The next stage needs enough provenance to verify the passage, not only a vector score. The toy encoder explicitly lacks an unknown-token strategy and must expose that limit. A production encoder has a tokenizer policy, but successful encoding still does not prove evidence relevance or answer grounding.",
        ),
    ],
    """
import numpy as np
VALUES=np.array([[1.,2.],[3.,4.],[100.,100.]])
MASK=np.array([True,True,False])

def masked_mean(values,mask):
    raise NotImplementedError("Implement the valid-position denominator")

def main():
    print("Pooling and score fixtures are ready. Do not download or claim a pretrained encoder.")

if __name__ == "__main__":
    main()
""",
    solution14,
    [
        """**Interview: Why can a semantic retriever return an unsupported answer source?** Similarity measures representation closeness, not entailment of a particular claim. Preserve the passage and provenance, then evaluate whether it actually supports the answer.""",
        """**Interview: What does temperature change in contrastive loss?** It rescales score differences before softmax, changing sharpness and gradient behavior. A lower loss on fixed scores is not proof of better generalization.""",
        """**Interview: Why keep a lexical baseline?** Exact identifiers and rare domain phrases can be handled well by TF-IDF or BM25. Dense representations should demonstrate complementary or better task performance under the same candidate and evaluation conditions.""",
    ],
    [
        "[Reimers and Gurevych, Sentence-BERT](https://aclanthology.org/D19-1410/)",
        "[Jurafsky and Martin, vector semantics and retrieval](https://web.stanford.edu/~jurafsky/slp3/)",
    ],
)

solution15 = r"""
import numpy as np
from scipy.special import expit,logsumexp

EMBED={"bank":np.array([1.,0.]),"river":np.array([0.,1.]),"money":np.array([0.,-1.])}

def encode(values,valid):
    x=np.asarray(values,dtype=float);mask=np.asarray(valid,dtype=bool)
    if x.ndim!=2 or mask.shape!=(len(x),) or not mask.any():raise ValueError("valid positions required")
    scores=x@x.T/np.sqrt(x.shape[1])
    scores=np.where(mask[None,:],scores,-np.inf)
    weights=np.exp(scores-logsumexp(scores,axis=1,keepdims=True))
    output=weights@x
    output[~mask]=0.
    return output,weights

def pooled(tokens):
    x=np.array([EMBED[token] for token in tokens]);h,_=encode(x,np.ones(len(x),dtype=bool))
    return h.mean(axis=0)

def tag_loss(logits,labels):
    logits=np.asarray(logits,dtype=float);labels=np.asarray(labels,dtype=int)
    valid=labels!=-100
    if logits.ndim!=2 or labels.shape!=(len(logits),) or not valid.any():raise ValueError("supervised positions required")
    if np.any((labels[valid]<0)|(labels[valid]>=logits.shape[1])):raise ValueError("invalid label")
    chosen=logits[valid];target=labels[valid]
    return float(np.mean(logsumexp(chosen,axis=1)-chosen[np.arange(len(chosen)),target]))

def main():
    river=np.array([EMBED["bank"],EMBED["river"]]);money=np.array([EMBED["bank"],EMBED["money"]])
    hr,wr=encode(river,[1,1]);hm,_=encode(money,[1,1])
    assert hr[0,1]>0 and hm[0,1]<0 and not np.allclose(hr[0],hm[0])
    assert np.allclose(wr.sum(axis=1),1.)
    padded=np.vstack([river,[99.,99.]])
    hp,wp=encode(padded,[1,1,0])
    assert np.allclose(hp[:2],hr) and np.allclose(wp[:2,2],0.) and np.all(hp[2]==0)
    data=np.array([pooled(tokens) for tokens in [["bank","river"],["bank","money"],["river","bank"],["money","bank"]]])
    y=np.array([0.,1.,0.,1.]);w=np.zeros(2);b=0.
    before=float(np.mean(np.logaddexp(0.,data@w+b)-y*(data@w+b)))
    for _ in range(400):
        error=expit(data@w+b)-y
        w-=.3*(data.T@error/len(y));b-=.3*error.mean()
    after=float(np.mean(np.logaddexp(0.,data@w+b)-y*(data@w+b)))
    assert after<.1 and after<before and ((data@w+b)>=0).astype(int).tolist()==[0,1,0,1]
    logits=np.array([[2.,0.],[99.,-99.],[0.,2.],[-99.,99.]])
    labels=np.array([0,-100,1,-100])
    loss=tag_loss(logits,labels);changed=logits.copy();changed[[1,3]]*=100
    assert np.isclose(loss,np.log1p(np.exp(-2))) and np.isclose(tag_loss(changed,labels),loss)
    for operation in [lambda: encode([[1.,0.]],[False]),lambda: tag_loss([[1.,0.]],[-100])]:
        try:operation()
        except ValueError:pass
        else:raise AssertionError("absent supervision was accepted")
    print("nlp-015: contextual bank states, padding invariance, actual tiny head training and masked tagging loss passed")

if __name__ == "__main__":
    main()
"""
author(
    15,
    """A contextual encoder produces a different vector for a token depending on the surrounding sequence. This addresses a limitation of fixed word vectors: bank near river and bank near money can be represented differently. The encoder can then supply features to a document classifier or a token-level tagging head. The representation, output head and training objective are separate components.

The reference implements a genuine bidirectional scaled dot-product attention calculation in NumPy, followed by actual gradient training of a tiny logistic classification head. The token embeddings and attention projections are deliberately fixed and handcrafted. This is not pretrained BERT, not a complete transformer stack and not evidence of real word-sense accuracy. Its purpose is to expose context mixing, padding masks, pooling and supervised loss alignment with exact checks.

A real pretrained encoder adds learned token/position embeddings, multiple attention heads, feed-forward blocks, residual connections, normalization and pretraining over a corpus. Fine-tuning can update the encoder and head together or freeze some components. Those choices change cost, capacity and generalization and require task-specific held-out evaluation.""",
    [
        (
            "Trace bidirectional attention and its dimensions",
            """Let X have shape T by d, one row per token. In a general attention layer, Q=X*W_Q, K=X*W_K and V=X*W_V. Scores Q*K_transpose/sqrt(d_k) form a T-by-T matrix. A row softmax converts scores into weights over key positions, and multiplying by V returns one contextual vector for each query position.

The toy encoder uses identity projections, so Q=K=V=X. It allows every valid position to attend to every other valid position. This bidirectional structure is suitable for encoding an already observed input sentence. It would leak future targets in an autoregressive next-token decoder unless a causal mask were added. The meaning of future therefore depends on the task: all words in an input document may be known, while future generated output tokens are not.

Stable normalization subtracts logsumexp along the key-position axis. Applying softmax along the feature axis would produce a different operation even if the code ran. Verify that each valid query row\'s attention weights sum to one and that masked key positions receive zero probability.""",
        ),
        (
            "Padding, pooling and subword alignment",
            """Padding makes variable-length sequences fit a rectangular batch. The key mask prevents padded vectors from contributing to valid token outputs. The reference additionally zeros the outputs at padded query positions and excludes them from pooling. A deliberately large padded vector is a useful negative control: if adding it changes the valid outputs, masking is wrong.

For document classification, a pooled vector enters a classification head. Mean pooling should divide by the number of valid tokens. Other encoders use a designated classification token, but its representation and training history matter; selecting the first row of an arbitrary untrained encoder is not automatically equivalent.

For token tagging, word annotations may need alignment to subword pieces. One policy supervises only the first piece and masks the others; another propagates labels with a documented rule. The reference uses -100 as an ignored-label sentinel and selects valid rows before indexing target columns. Indexing all labels first would accidentally treat a negative sentinel as a Python negative index or raise an unrelated error.""",
        ),
        (
            "Train a head without overstating the experiment",
            """The four examples contain bank/river and bank/money in both orders. The handcrafted vectors already encode a useful separation, and the attention layer pools it into two-dimensional features. A logistic head begins with zero weights, predicts one-half for every example and has cross-entropy log two. Gradient steps update only the head, reducing the loss and recovering all four training labels.

This is a real optimization loop, but the task is deliberately constructed and has no independent natural-language test set. Report it as a training-mechanism check. Do not claim that lower training loss proves the encoder learned semantic disambiguation or that performance generalizes to bank account, riverbank, multilingual usage or quoted text.

A meaningful encoder comparison would hold out document families, use the exact tokenizer and pooling contract, compare a linear lexical baseline, inspect ambiguous cases and measure entity/document-level outcomes. It would also report truncation and subgroup effects, since long inputs and rare vocabulary can behave differently from short clean examples.""",
        ),
    ],
    [
        (
            "Make one token depend on its neighbor",
            """Bank has fixed vector [1,0], river [0,1] and money [0,-1]. In the two-token attention calculation, the bank output gets a positive second coordinate with river and a negative one with money. The difference comes from weighted context values. Its semantic interpretation was built into the authored vectors, so the test verifies the attention mechanism rather than learned linguistic knowledge.""",
        ),
        (
            "Add a dangerous padding vector",
            """Append [99,99] but mark it invalid. Valid-token outputs must remain identical, valid rows assign zero weight to the padded key, and the padded output is zeroed. This tests a meaningful failure mode: a mask that only removes padding from the final average can still allow it to contaminate earlier attention.""",
        ),
        (
            "Train and mask two different heads",
            """The document head is actually optimized for 400 deterministic gradient steps and must reduce loss below 0.1 on its four training examples. Separately, tagging logits with labels [0,-100,1,-100] score only two positions. Changing ignored-position logits by a factor of one hundred must leave tag loss unchanged. These are different supervision contracts.""",
        ),
    ],
    [
        (
            "Implement contextual attention",
            "Compute scaled scores, row-normalized weights and contextual outputs for both bank contexts.",
            "Bank's second output coordinate changes sign with river versus money.",
            "Trace the T-by-T score matrix and normalize over keys.",
            "The token's own vector is unchanged, but its output mixes values from the whole valid sequence. The context difference therefore appears in its output. Because the embeddings are handcrafted, this is an algebraic demonstration of contextualization rather than evidence of pretrained language understanding.",
        ),
        (
            "Prove padding invariance",
            "Append [99,99] with an invalid mask and compare valid outputs.",
            "Original valid outputs unchanged; padded-key weights zero; padded query output zero.",
            "Mask keys before softmax, then define how padded query outputs are consumed.",
            "Removing padding only after attention is too late if valid queries already attended to it. The large vector makes contamination easy to detect. The reference checks both attention weights and final representations, providing stronger evidence than a shape-only assertion.",
        ),
        (
            "Train the document head",
            "Fit the tiny logistic head on four pooled contextual fixtures.",
            "Loss decreases from log2 to below.1 and training predictions [0,1,0,1].",
            "Use the cross-entropy gradient X_transpose*(p-y)/n and keep the encoder fixed.",
            "This performs actual parameter updates and verifies the objective numerically. The constructed features make the problem easy, so the result is explicitly a training receipt. It does not replace a held-out natural-language evaluation or demonstrate that the fixed encoder parameters were learned.",
        ),
        (
            "Mask subword supervision",
            "Compute tagging cross-entropy with labels[0,-100,1,-100].",
            "Loss log(1+exp(-2)); changing ignored logits does not alter it.",
            "Select valid positions before using labels as column indices.",
            "The ignored sentinel is not a class ID. Filtering it first prevents invalid indexing and makes the loss denominator equal the number of supervised positions. A real tokenizer alignment record must explain why each piece is supervised or ignored.",
        ),
        (
            "Reject missing supervision",
            "Test all-padding encoder input and all-ignored tagging labels.",
            "Both raise clear ValueError instead of returning a meaningless average.",
            "Check that at least one valid position exists before normalization.",
            "An empty valid set makes mean pooling or average supervised loss undefined. Returning zero could make a broken batch appear to train perfectly. The explicit error distinguishes an absent signal from a genuine low loss.",
        ),
        (
            "Design a real encoder evaluation",
            "Specify held-out families, exact tokenizer/pooling identity and ambiguous bank probes.",
            "A written plan separates training fit, lexical baseline, contextual task quality and subgroup/truncation errors.",
            "Start from the claim you would want to make about deployment.",
            "A real evaluation needs examples not constructed from the same handcrafted geometry. Hold out related documents, compare the baseline fairly and inspect whether context changes the intended task output. Record model/tokenizer versions and reject a claim of pretrained quality from this toy layer alone.",
        ),
    ],
    """
import numpy as np
RIVER=np.array([[1.,0.],[0.,1.]])
MONEY=np.array([[1.,0.],[0.,-1.]])

def encode(values,valid):
    raise NotImplementedError("Implement bidirectional attention with a real key mask")

def main():
    print("Handcrafted attention fixtures loaded. This is not a pretrained encoder.")

if __name__ == "__main__":
    main()
""",
    solution15,
    [
        """**Interview: Why can an encoder use future input words while a decoder cannot use future targets?** The complete input sentence is observed for an encoding task. Future generated target tokens are unknown at inference. Masks must reflect the task\'s information set, not a generic slogan about time.""",
        """**Interview: Does pooling remove the need for padding masks inside attention?** No. A padded key can alter valid token representations before pooling. Mask it at the attention boundary and then use a valid-position pooling rule.""",
        """**Interview: What did the tiny head actually learn?** It learned a classification boundary over fixed handcrafted contextual features. It did not pretrain the encoder or establish generalization to natural language.""",
    ],
    [
        "[Devlin and colleagues, BERT](https://aclanthology.org/N19-1423/)",
        "[Vaswani and colleagues, Attention Is All You Need](https://proceedings.neurips.cc/paper/7181-attention-is-all-you-need)",
    ],
)

solution16 = r"""
import math
import numpy as np
from scipy.special import logsumexp

TRANSITIONS={"<BOS>":{"tea":.6,"coffee":.4},"tea":{"<EOS>":.5,"sugar":.5},"coffee":{"<EOS>":1.},"sugar":{"<EOS>":1.}}

def cross_attention(query,keys,values,valid):
    q=np.asarray(query,dtype=float);k=np.asarray(keys,dtype=float);v=np.asarray(values,dtype=float);mask=np.asarray(valid,dtype=bool)
    if q.ndim!=2 or k.ndim!=2 or v.ndim!=2 or q.shape[1]!=k.shape[1] or len(k)!=len(v) or mask.shape!=(len(k),) or not mask.any():raise ValueError("compatible nonempty source required")
    score=q@k.T/np.sqrt(k.shape[1]);score=np.where(mask[None,:],score,-np.inf)
    weights=np.exp(score-logsumexp(score,axis=1,keepdims=True))
    return weights@v,weights

def shifted_targets(tokens):
    if any(token in {"<BOS>","<EOS>"} for token in tokens):raise ValueError("raw target contains markers")
    return ["<BOS>",*tokens],[*tokens,"<EOS>"]

def beam_search(width,max_steps=3):
    if width<1 or max_steps<1:raise ValueError("positive search budget required")
    beam=[(0.,())]
    for _ in range(max_steps):
        candidates=[]
        for score,path in beam:
            if path and path[-1]=="<EOS>":candidates.append((score,path));continue
            last=path[-1] if path else "<BOS>"
            for token,p in TRANSITIONS[last].items():candidates.append((score+math.log(p),path+(token,)))
        beam=sorted(candidates,key=lambda item:(-item[0],item[1]))[:width]
    completed=[item for item in beam if item[1] and item[1][-1]=="<EOS>"]
    if not completed:raise ValueError("no completed sequence within budget")
    return completed[0]

def extractive_summary(sentences,query):
    words=set(query.lower().split())
    if not sentences:return None
    scores=[len(words & set(sentence.lower().replace(".","").split())) for sentence in sentences]
    best=max(range(len(sentences)),key=lambda i:(scores[i],-i))
    return None if scores[best]==0 else (best,sentences[best])

def main():
    decoder,targets=shifted_targets(["repair"])
    assert decoder==["<BOS>","repair"] and targets==["repair","<EOS>"]
    assert shifted_targets([])==(["<BOS>"],["<EOS>"])
    out,weights=cross_attention([[1.,0.]],[[1.,0.],[0.,1.]],[[10.,0.],[0.,20.]],[1,1])
    p=1/(1+np.exp(-1/np.sqrt(2)))
    assert np.allclose(out,[[10*p,20*(1-p)]]) and np.allclose(weights.sum(axis=1),1.)
    masked,_=cross_attention([[1.,0.]],[[1.,0.],[0.,1.]],[[10.,0.],[0.,20.]],[1,0])
    assert np.allclose(masked,[[10.,0.]])
    greedy=beam_search(1);beam=beam_search(2)
    assert greedy[1]==("tea","<EOS>") and math.isclose(math.exp(greedy[0]),.3)
    assert beam[1]==("coffee","<EOS>") and math.isclose(math.exp(beam[0]),.4)
    sentences=["The service is unavailable.","A repair is scheduled."]
    summary=extractive_summary(sentences,"service")
    assert summary==(0,sentences[0]) and extractive_summary(sentences,"refund") is None
    print("nlp-016: shifted targets, source attention, greedy/beam .3/.4 and extractive provenance checks passed")

if __name__ == "__main__":
    main()
"""
author(
    16,
    """Sequence-to-sequence learning predicts an output sequence conditioned on an input sequence. Translation, summarization and structured generation fit this pattern, but each has a different success contract. A translation should preserve meaning, a summary should preserve important claims and qualifications, and extraction should respect a schema and source evidence. Fluent output alone cannot establish any of those properties.

An encoder represents the source, and a decoder predicts target tokens conditional on the source and prior target tokens. Cross-attention lets each decoder position consult source representations. During teacher-forced training, the decoder receives the correct earlier target tokens. During generation it receives its own earlier predictions, creating a mismatch when those predictions are wrong.

This offline chapter implements exact cross-attention arithmetic, target shifting and bounded greedy/beam search over an authored probability table. It also provides an honestly labeled extractive summary baseline. It does not train a pretrained encoder-decoder or claim that a keyword-selected sentence is a generative summarizer.""",
    [
        (
            "Separate three information paths",
            """Encoder self-attention combines source positions that are already observed. Decoder self-attention combines only earlier target positions under a causal mask. Cross-attention uses decoder queries with encoder keys and values, allowing generated positions to focus on relevant source content. These operations can share the same matrix formula but have different Q, K and V origins and different masks.

If Q has target-length by hidden-dimension shape and K has source-length by hidden-dimension shape, Q*K_transpose yields target-length by source-length scores. Multiplying their normalized weights by source values returns a target-position representation. Mask source padding before softmax. A source attention mask does not replace the decoder\'s causal target mask.

The simple example uses one decoder query [1,0], two source keys [1,0] and [0,1], and values [10,0] and [0,20]. The weights depend on scaled key compatibility, while the values are what gets mixed. Confusing keys with values can yield plausible dimensions but a different computation.""",
        ),
        (
            "Teacher forcing and output alignment",
            """For raw target [repair], the decoder input is [BOS,repair] and the prediction targets are [repair,EOS]. At the first position the model sees BOS and predicts repair; at the second it sees the correct prefix repair and predicts ending. Feeding the unshifted target at the same position leaks the answer into its own input.

For a masked-attention decoder such as a Transformer, teacher forcing lets target positions be computed in parallel during training because the correct shifted target sequence is available and the causal mask enforces prefix-only access. Teacher forcing does not remove the sequential hidden-state dependency of a recurrent decoder. At inference those correct prefixes do not exist yet. A wrong first token changes later conditioning and can lead to compounding errors. This is one reason low teacher-forced loss and good autoregressive task performance need separate evaluation.

Padding and response masks determine which target positions contribute to loss. EOS is a meaningful supervised event, while padding is usually ignored. Empty raw output still needs an ending decision under the convention here. Record tokenizer and special-token identities; manually inserting a string called BOS is not equivalent to a pretrained model\'s actual token ID and chat template.""",
        ),
        (
            "Decoding searches probabilities, not truth",
            """Greedy decoding chooses the largest next-token probability at each step. Beam search retains a bounded set of promising partial sequences and can find a higher-probability complete sequence, but it is still approximate and depends on width, stopping and scoring rules. Length normalization or penalties change the search objective and should be explicit.

The authored table gives tea probability .6 and coffee .4 at the first step. Tea then ends with probability .5, so greedy tea->EOS has joint probability .3. Coffee ends with probability one, giving .4. A width-two beam retains coffee long enough to discover the better complete path. This is a search counterexample, not evidence that coffee is a better real-world answer.

Higher model likelihood does not establish factual support or summary usefulness. A model can assign high probability to a common but incorrect statement. A production decoder needs bounded output and stop behavior, and a task evaluator must check meaning, evidence and required content separately from the search score.""",
        ),
        (
            "Summarization and provenance",
            """Extractive summarization selects source spans or sentences. Abstractive summarization generates new wording and can combine information across passages, which adds flexibility and risk of unsupported claims. The reference baseline selects a source sentence by query-word overlap and returns its original index and text. It abstains when there is no overlap.

Selecting a sentence exactly avoids inventing new words but does not guarantee a good summary. It may omit a qualification in another sentence, choose an outdated statement or overemphasize repeated query terms. A generated summary can additionally reverse negation or imply causality absent from the source. Evaluate coverage, factual support and usefulness with representative documents and multiple valid references where appropriate.

Preserve source identity, offsets and the selection/generation configuration. A later assistant should be able to show why a sentence or claim was included. Cross-attention weights are internal model computations, not a substitute for an external citation-support check.""",
        ),
    ],
    [
        (
            "Shift one target correctly",
            """Raw target [repair] becomes decoder input [BOS,repair] and targets [repair,EOS]. The two arrays have equal lengths but different content at every aligned prediction position. Empty raw output becomes one BOS input and one EOS target. These small checks catch a leakage bug before training any large model.""",
        ),
        (
            "Calculate cross-attention",
            """The query/key dot products are one and zero, scaled by sqrt(2). The first source receives probability p=1/(1+exp(-1/sqrt(2))), about 0.66976. The resulting value is [10p,20(1-p)]. If the second source is masked, the output becomes exactly [10,0].""",
        ),
        (
            "Compare search and a grounded baseline",
            """Greedy search returns tea,EOS with probability .3, while beam width two returns coffee,EOS with .4. Separately, the extractive baseline answers query service with the exact source sentence The service is unavailable. It does not turn a scheduled repair into a claim that the service has recovered. The search and extraction examples establish different mechanisms.""",
        ),
    ],
    [
        (
            "Build teacher-forced inputs",
            "Implement target shifting for [repair] and empty raw output.",
            "[BOS,repair] versus[repair,EOS]; empty becomes[BOS] versus[EOS].",
            "Current target must not appear at the same decoder-input position.",
            "The shift ensures each prediction conditions only on previous target tokens. EOS remains a prediction event, making stopping part of the learned sequence contract. Reject raw reserved markers so the helper cannot accidentally create duplicated or ambiguous boundary tokens.",
        ),
        (
            "Trace cross-attention dimensions",
            "Compute the one-query, two-source weighted output.",
            "Weights sum to one; output[10p,20(1-p)] with p=sigmoid(1/sqrt2).",
            "Queries choose compatibility; values supply the mixed representation.",
            "The score matrix has one target row and two source columns. Stable softmax normalizes over source positions. Multiplying by values produces the stated two-dimensional output. This exact fixture detects wrong-axis normalization and confusing key/value roles.",
        ),
        (
            "Mask source padding",
            "Mark the second source invalid and repeat the calculation.",
            "Output exactly[10,0]; an all-invalid source raises.",
            "Apply the mask to scores before softmax.",
            "The masked source must contribute zero weight even if its value is large or relevant-looking. An all-invalid source cannot supply a meaningful normalized context and is rejected rather than producing NaNs or an invented average.",
        ),
        (
            "Expose greedy search failure",
            "Run width-one and width-two bounded search on the authored table.",
            "Greedy tea,EOS probability.3; beam coffee,EOS probability.4.",
            "Compare complete sequence probability, not only the first-token choice.",
            "The locally best first token has a weaker continuation. Retaining the alternative lets beam search find the larger joint probability. The result depends on the fixed score and stopping conventions and does not imply that wider beams always improve task quality.",
        ),
        (
            "Preserve extractive provenance",
            "Select a sentence for service and test an unsupported refund query.",
            "Return index0 and the unchanged unavailable sentence; refund returns None.",
            "Keep the source list and tie rule explicit.",
            "The baseline returns source text rather than generating a new claim. Its abstention marks no lexical support under its scoring rule, not proof that the corpus contains no semantic answer. Evaluate coverage and semantic relevance separately before using it as a real summarizer.",
        ),
        (
            "Explain generation error propagation",
            "Describe what changes after an incorrect first generated token and how a summary can reverse a qualification.",
            "A concrete account separates teacher-forced loss, autoregressive rollout, search score and factual support.",
            "Follow the next conditional distribution after the changed prefix.",
            "At inference the model conditions on its own prefix, so later distributions can differ from those seen under correct training prefixes. A high-likelihood continuation can still be unsupported by the source. Acceptance therefore needs generated task evaluation, not only training loss or attention visualization.",
        ),
    ],
    """
TARGET=["repair"]
SENTENCES=["The service is unavailable.","A repair is scheduled."]

def shifted_targets(tokens):
    raise NotImplementedError("Separate decoder input from prediction targets")

def main():
    print("Sequence and source fixtures loaded. Label the search table and extraction baseline honestly.")

if __name__ == "__main__":
    main()
""",
    solution16,
    [
        """**Interview: Why is teacher forcing not the same as generation?** Training conditions on correct previous targets, while generation conditions on model outputs. The mismatch can compound errors and requires separate rollout evaluation.""",
        """**Interview: Does beam search guarantee a better summary?** It optimizes an approximate model-score search under chosen penalties and budgets. Better probability is not necessarily better factuality, coverage or user utility.""",
        """**Interview: Is an extractive summary automatically faithful?** Its selected text is present in the source, but selection can omit qualifications or combine context misleadingly. Preserve provenance and assess the complete meaning.""",
    ],
    [
        "[Cho and colleagues, encoder-decoder learning](https://aclanthology.org/D14-1179/)",
        "[Vaswani and colleagues, attention architectures](https://proceedings.neurips.cc/paper/7181-attention-is-all-you-need)",
    ],
)
