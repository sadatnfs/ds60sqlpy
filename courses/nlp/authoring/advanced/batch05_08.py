from author import author

solution05=r'''
def lemma(word,pos):
    table={("saw","VERB"):"see",("saw","NOUN"):"saw",("studies","NOUN"):"study",("better","ADJ"):"good"}
    return table.get((word.lower(),pos),word.lower())

def toy_tags(tokens):
    result=[]
    for i,word in enumerate(tokens):
        if word.lower()=="saw":result.append("NOUN" if i>0 and tokens[i-1].lower()=="the" else "VERB")
        else:result.append("OTHER")
    return result

def valid_dependency_tree(heads):
    n=len(heads)
    if n==0:return False
    if any(type(h) is not int or h < -1 or h>=n for h in heads):return False
    if heads.count(-1)!=1:return False
    for origin in range(n):
        seen=set();node=origin
        while node!=-1:
            if node in seen:return False
            seen.add(node);node=heads[node]
    return True

def main():
    assert lemma("saw","VERB")=="see" and lemma("saw","NOUN")=="saw"
    assert lemma("studies","NOUN")=="study" and lemma("better","ADJ")=="good"
    assert toy_tags(["I","saw","her"])[1]=="VERB"
    assert toy_tags(["the","saw","broke"])[1]=="NOUN"
    assert toy_tags(["the","old","saw"])[2]=="VERB"  # explicit known failure against NOUN gold
    assert valid_dependency_tree([1,-1,1])
    assert valid_dependency_tree([1,-1,0]) # structurally valid, not semantic proof
    assert not valid_dependency_tree([1,0,-1])
    assert not valid_dependency_tree([-1,-1])
    assert not valid_dependency_tree([2,-1]) and not valid_dependency_tree([])
    print("nlp-005: POS-conditioned lemmas; known old-saw error; structural tree checks passed")

if __name__ == "__main__":
    main()
'''
author(5,
'''Linguistic structure supplies distinctions that a sequence of token IDs does not explain by itself. Morphology concerns word formation and meaningful parts; syntax concerns how words combine into phrases and grammatical relationships. A tokenizer chooses computational units, which may cut across morphemes or combine punctuation. A BPE fragment is therefore not automatically a linguistic root, and a short tokenization is not evidence of correct grammatical analysis.

This lesson uses a few deliberately authored English examples to distinguish stemming, lemmatization, part-of-speech tagging and dependency structure. It does not download a tagger or parser. The small lookup and context rule are intentionally incomplete so you can see what they do, why one counterexample defeats them and which checks establish only structural validity.

A surface form is the observed spelling, such as saw. A lemma is a dictionary-like base form under a grammatical interpretation. Saw as a past-tense verb can have lemma see, while saw as a cutting-tool noun retains lemma saw. The same character string therefore needs context before normalization can safely collapse it.''',
[
('Morphology and the cost of normalization', '''Inflection changes grammatical features without necessarily creating a new dictionary word, as in study and studies. Derivation creates related words with changed category or meaning, as in teach and teacher. These distinctions vary across languages and are not reducible to deleting a final letter. Compounds, irregular forms and spelling changes make simple suffix rules incomplete.

A stemmer applies an algorithmic reduction, often producing a useful retrieval key that is not a valid word. A lemmatizer aims for a lexical base and may need part of speech and morphological features. The lookup studies/NOUN -> study in this lesson is an explicit table entry, not a general English lemmatizer. Better/ADJ -> good demonstrates an irregular relation that cannot be recovered by trimming a suffix.

Choose normalization from the downstream task. Collapsing inflections may improve retrieval recall but remove tense or number distinctions needed for extraction. Preserve the raw word and transformation record so a reviewer can recover what was actually written. A successful lookup is evidence only for a covered entry.'''),
('Part of speech is contextual', '''Part of speech labels a token\'s grammatical role, such as noun, verb or adjective. The inventories and annotation conventions differ between corpora. In I saw her, saw is a verb; in the saw broke, it is a noun. A rule that checks only whether the immediately preceding token is the captures those two examples.

The old saw is a deliberate counterexample. The determiner is separated from saw by an adjective, so the one-token rule incorrectly labels saw as a verb. More local rules can patch this example, but a general solution needs a representation of broader context and representative labeled data. Do not turn a two-example success into a claim that the algorithm understands English grammar.

Tagging errors can propagate into lemmatization and relation extraction. If the noun saw is tagged as a verb, a POS-conditioned lemma table may convert a physical tool into see. Evaluate the combined pipeline and preserve ambiguity when the input does not support a unique interpretation.'''),
('Dependency trees and what a validator can prove', '''A dependency representation links each token to a head token, with a root marking the main organizing predicate under a chosen annotation scheme. For tokens [I,saw,her], heads [1,-1,1] attach I and her to saw, which is the root. Indices refer to token positions, and -1 is the explicit root sentinel in this lesson.

A structural validator checks legal indices, exactly one root and absence of cycles. Following each head chain should eventually reach -1. These conditions establish that the array forms one rooted tree. They do not establish that the attachments or relation labels are linguistically correct. Heads [1,-1,0] also form a tree but attach her to I, which is not the intended analysis of this sentence.

The distinction matters for learned parsers and language-model-generated structures. A schema-valid parse can be wrong. Measure attachment accuracy against an annotation contract, inspect coordination and long-distance dependencies, and account for tokenization alignment. Projectivity is an additional property that some parsing algorithms assume; it is not required by this basic tree validator.''')],
[
('One form, two lemmas','''The pair (saw,VERB) maps to see, while (saw,NOUN) maps to saw. The word alone is insufficient for this table. Store surface, POS and lemma together so the normalization can be audited. A default lowercased fallback means no covered transformation was found, not that a lexicon has confirmed the lemma.'''),
('A minimal-pair rule and its failure','''The handcrafted tagger handles I saw her and the saw broke, then fails on the old saw. The expected gold role in the third phrase is noun, but the rule returns verb. This is a useful error analysis result: it identifies the limited context window rather than hiding the failure by changing the expected label.'''),
('Two trees, one intended reading','''Both [1,-1,1] and [1,-1,0] pass the structural validator for three tokens. The cycle [1,0,-1], two-root array [-1,-1] and out-of-range [2,-1] fail. Structural success is necessary for a usable tree representation, while semantic correctness requires separate evidence.''')],
[
('Retain grammatical context','Implement the four explicit lemma mappings and preserve raw/POS/lemma records.','saw/VERB -> see; saw/NOUN -> saw; studies/NOUN -> study; better/ADJ -> good.','Key the table by both surface and POS.','The table expresses four authored lexical relations. The ambiguous saw entries show why surface-only normalization loses information. Returning a lowercased fallback outside the table is a conservative computational convention, not proof of a true dictionary lemma.'),
('Trace the context rule','Implement the one-token determiner rule for saw in the first two sentences.','I saw her gives VERB; the saw broke gives NOUN.','Inspect the token immediately before saw and handle position zero.','The rule reproduces the authored cases because the determiner is directly adjacent only in the noun example. It is a baseline with a declared context window. It does not infer phrase structure or resolve all uses of saw.'),
('Preserve a known error','Run the old saw and compare with an independently stated NOUN label.','The rule returns VERB, and the error is recorded rather than relabeled as correct.','An intervening adjective defeats immediate-predecessor logic.','The counterexample isolates a specific limitation. Adding a two-token lookback may repair this phrase but still fails broader grammar. The appropriate lesson is to evaluate on new constructions and identify the required context, not to claim one patch completes a tagger.'),
('Validate head indices','Check one-root, range and cycle rules on the supplied arrays.','Accept [1,-1,1]; reject [1,0,-1],[-1,-1],[2,-1] and empty input.','Follow each head chain with a set of visited positions.','A repeated node in one chain is a cycle. Exactly one root plus valid acyclic head chains yields a rooted tree. Negative indices other than -1 must be rejected because Python would otherwise interpret them as valid indexing from the end.'),
('Separate structure from meaning','Compare [1,-1,1] and [1,-1,0] for I saw her.','Both structurally valid; only the first matches the intended head assignment.','Draw the edges and describe the changed attachment.','The validator has no access to a grammatical gold analysis. Passing its checks proves a data-structure invariant, not linguistic accuracy. A parser evaluation must compare token-aligned heads and labels against an appropriate annotation convention.'),
('Choose task-specific normalization','Explain whether tense and number should be collapsed for search versus event extraction.','A concrete policy preserves raw text and names at least one lost distinction for each transformation.','Ask what downstream decision depends on the distinction.','A retrieval system may benefit from matching study and studies, while an event extractor may need tense or participant number. There is no universally harmless cleaning step. The record should retain original spelling and the normalization method so later users know which information remains available.')],
'''
EXAMPLES=[["I","saw","her"],["the","saw","broke"],["the","old","saw"]]

def lemma(word,pos):
    raise NotImplementedError("Implement only the explicit covered mappings")

def valid_dependency_tree(heads):
    raise NotImplementedError("Check indices, one root and cycles")

def main():
    print("Authored language examples loaded. Preserve the known rule failure in your analysis.")

if __name__ == "__main__":
    main()
''',solution05,
['''**Interview: Is stemming a cheaper version of correct lemmatization?** It solves a different normalization problem and may produce nonwords. Its usefulness depends on the task, while lemmatization attempts a lexical interpretation often requiring grammar.''','''**Interview: Why keep a counterexample in the reference?** It teaches the actual capability boundary and protects against claiming a handcrafted rule is a general parser. Expected failure is evidence when it is clearly labeled and independently justified.''','''**Interview: Does one root and no cycle prove a correct parse?** It proves a valid tree shape. Linguistic attachments, labels and token alignment need separate checks against an annotation contract.'''],
['[Jurafsky and Martin, linguistic structure and tagging](https://web.stanford.edu/~jurafsky/slp3/)','[NLTK book, categorizing and tagging words](https://www.nltk.org/book/ch05.html)'])

solution06=r'''
from collections import Counter,defaultdict
import math

TRAIN=[["we","like","tea"],["we","like","coffee"],["they","like","tea"]]
BOS="<BOS>";EOS="<EOS>";UNK="<UNK>"

def fit_bigram(documents,alpha=1.):
    if alpha<=0:raise ValueError("positive smoothing required")
    words={word for doc in documents for word in doc}
    if words & {BOS,EOS,UNK}:raise ValueError("reserved marker in raw input")
    vocabulary=tuple(sorted(words|{EOS,UNK}));counts=defaultdict(Counter)
    for doc in documents:
        sequence=[BOS,*doc,EOS]
        for left,right in zip(sequence,sequence[1:]):counts[left][right]+=1
    return vocabulary,dict(counts),alpha

def probability(model,context,word):
    vocabulary,counts,alpha=model
    if word==BOS:raise ValueError("BOS is not a prediction target")
    context=context if context==BOS or context in vocabulary else UNK
    word=word if word in vocabulary else UNK
    row=counts.get(context,{})
    return (row.get(word,0)+alpha)/(sum(row.values())+alpha*len(vocabulary))

def score(model,tokens):
    if any(token in {BOS,EOS,UNK} for token in tokens):raise ValueError("raw tokens contain markers")
    sequence=[BOS,*tokens,EOS]
    logp=sum(math.log(probability(model,left,right)) for left,right in zip(sequence,sequence[1:]))
    events=len(tokens)+1
    return logp,math.exp(-logp/events),events

def main():
    model=fit_bigram(TRAIN);vocab=model[0]
    assert len(vocab)==7 and BOS not in vocab and {EOS,UNK}<=set(vocab)
    values=[probability(model,BOS,"we"),probability(model,"we","like"),probability(model,"like","tea"),probability(model,"tea",EOS)]
    assert all(math.isclose(a,b) for a,b in zip(values,[.3,1/3,.3,1/3]))
    logp,ppl,events=score(model,["we","like","tea"])
    assert math.isclose(math.exp(logp),.01) and math.isclose(ppl,math.sqrt(10)) and events==4
    for context in [BOS,"we","like",UNK]:assert math.isclose(sum(probability(model,context,w) for w in vocab),1.)
    snapshot=(model[0],repr(model[1]))
    unknown=score(model,["we","like","cocoa"])
    assert math.isfinite(unknown[0]) and "cocoa" not in model[0] and snapshot==(model[0],repr(model[1]))
    assert score(model,[])[2]==1 and math.isclose(score(model,[])[1],10.)
    try:probability(model,BOS,BOS)
    except ValueError:pass
    else:raise AssertionError("BOS predicted")
    print("nlp-006: V=7; joint=.01; four-event perplexity=sqrt(10); OOV and EOS checks passed")

if __name__ == "__main__":
    main()
'''
author(6,
'''A language model assigns probabilities to sequences of language units. An n-gram model approximates the next-token distribution using a limited history. A bigram model uses only the immediately preceding token, making its assumptions and counts easy to inspect. It is a useful baseline and a foundation for understanding the next-token objective used by much larger models.

This lesson trains on three authored sentences: we like tea, we like coffee, and they like tea. The vocabulary contains five observed words plus an end-of-sequence token and an unknown token, for seven possible predictions. A beginning-of-sequence marker provides context but is never predicted. These choices determine the probability denominator and the perplexity calculation, so they are part of the model rather than formatting details.

The implementation learns real conditional count distributions with additive smoothing. It does not contain neural embeddings or attention. A finite probability for an unseen sentence means the smoothing policy assigns it mass, not that the model understands or verifies its meaning.''',
[
('From sequence probability to conditional counts', '''The chain rule writes p(x_1,...,x_T,EOS) as the product of conditional probabilities given the full preceding history. The bigram approximation replaces that history with only the last token. Each sentence begins at BOS and ends with a predicted EOS event. Counts reset at sentence boundaries so the end of one document does not become context for the next.

Without smoothing, maximum-likelihood probability is C(context,word)/C(context). An unseen continuation receives zero probability, which makes an entire sequence probability zero. Additive smoothing with alpha>0 uses (C(context,word)+alpha)/(C(context)+alpha*V). It allocates some probability to every vocabulary item. Larger alpha moves a row closer to uniform, while very small alpha stays near empirical counts.

The unknown token provides a fixed destination for unseen evaluation words. It is included during training even though this tiny corpus has no observed unknown events. A more realistic pipeline may replace rare training words with UNK before counting. That policy changes its learned probability and should be selected without inspecting the final evaluation corpus.'''),
('Derive all four factors', '''BOS has three outgoing observations: we twice and they once. With alpha one and V seven, P(we|BOS)=(2+1)/(3+7)=0.3. Context we appears twice, always followed by like, so P(like|we)=3/9=1/3. Context like has three continuations, tea twice and coffee once, giving P(tea|like)=3/10=0.3. Tea ends a sentence twice, so P(EOS|tea)=3/9=1/3.

Multiplying gives 0.3*(1/3)*0.3*(1/3)=0.01. There are four predicted events, including EOS. Negative average log likelihood is -log(0.01)/4, and perplexity is exp of that quantity, sqrt(10), approximately 3.1623. Excluding EOS from the denominator while including its probability would compute a different and inconsistent statistic.

Perplexity is measured per modeled token event. It cannot be compared casually across different tokenizers, vocabularies, boundary rules or corpora. A low value can reflect duplicated or easy evaluation text rather than useful language understanding.'''),
('Syntax anatomy, stability and diagnostic limits', '''Counter stores next-token counts for one context, and the model keeps a dictionary from contexts to those counters. probability uses get rather than mutating defaultdict lookup during evaluation, so scoring cannot silently add contexts or vocabulary items. The reference snapshots the model before an unknown-word probe and checks that it remains unchanged afterward.

Log probabilities turn the product into a sum, avoiding underflow on longer sequences. Exponentiating the negative average log value produces perplexity only after the correct event count is known. Empty raw input still predicts EOS from BOS under this model, so it contains one prediction event and has perplexity ten. This differs from an API that defines an empty sequence as no scored events; either convention must be explicit.

A bigram can capture local preferences but loses longer context. We do not assert that a low perplexity sentence is factual, grammatical or useful. Evaluate a changed domain, repeated templates and unknown-token rate separately. If every unfamiliar word maps to one UNK, a model can hide important vocabulary distinctions behind a finite but uninformative score.''')],
[
('Follow the training rows','''Count we->like twice, they->like once, like->tea twice, like->coffee once, tea->EOS twice and coffee->EOS once. BOS contributes three sentence starts. The seven prediction targets are coffee, like, tea, they, we, EOS and UNK in a recorded order; BOS is excluded.'''),
('Compute joint likelihood and perplexity','''For we like tea, the four smoothed factors are [0.3,1/3,0.3,1/3]. Their product is 0.01 and perplexity is sqrt(10). A hand calculation provides an independent oracle for the program\'s sum of logs.'''),
('Score an unknown without learning from it','''The evaluation sentence we like cocoa maps cocoa to UNK. Its score remains finite because alpha is positive. The vocabulary and count dictionary must be identical before and after scoring. Finite probability is smoothing behavior, not evidence that cocoa was represented with a learned semantic meaning.''')],
[
('Construct the event vocabulary','Fit the authored sentences with EOS and UNK but no predicted BOS.','Seven prediction targets, five observed words plus EOS/UNK.','Distinguish a context marker from a target token.','The denominator counts possible next-token events, so including BOS would incorrectly allocate mass to a token the model never intends to predict. EOS must be included because ending a sentence is a modeled event. UNK reserves probability for out-of-vocabulary input under the declared mapping policy.'),
('Derive smoothed rows','Calculate the four conditional factors for we like tea at alpha=1.','[0.3,1/3,0.3,1/3].','Use the context-specific outgoing total, not the total number of corpus tokens.','Each row has its own denominator. BOS has three observations, we has two, like has three and tea has two. Adding alpha once per vocabulary target adds seven to each row denominator. Using the grand corpus count would fail normalization and no longer estimate the stated conditional distribution.'),
('Implement log scoring','Return log likelihood, perplexity and predicted-event count.','Joint probability .01, four events and perplexity sqrt(10).','Sum log factors and divide by the count including EOS.','The log representation avoids multiplying many tiny values. The inverse geometric average probability is computed per prediction event. A correct numeric answer needs the boundary convention as well as the formula; reporting only a perplexity without its token unit makes comparisons ambiguous.'),
('Prove normalization','Sum probabilities over the frozen vocabulary for BOS,we,like and UNK.','Each row sums to one within numerical tolerance.','An unseen context has zero counts and a uniform smoothed row.','The additive numerator sums to the observed row total plus alpha*V, exactly matching the denominator. This invariant catches vocabulary and denominator errors. It also verifies the declared unseen-context behavior rather than relying on one plausible sentence score.'),
('Keep evaluation immutable','Score we like cocoa and compare model state before and after.','Finite score; cocoa absent from vocabulary; counts and vocabulary unchanged.','Map unknown targets/contexts to UNK without inserting new keys.','Evaluation should measure a frozen model. Learning vocabulary or transitions from the probe changes the system under test and can make perplexity artificially favorable. The state snapshot makes this boundary observable on the small fixture.'),
('Explain empty and incomparable scores','Score empty raw input and explain why tokenizer or EOS changes invalidate naive perplexity comparisons.','One EOS prediction with perplexity 10; a written comparison lists tokenization, corpus and boundary conventions.','The event sequence for empty text is BOS->EOS.','The model assigns EOS probability one-tenth after BOS because no empty sentence was observed and smoothing allocates one count-equivalent. This is a deliberate convention. A different tokenizer or omission of EOS changes the event space and denominator, so lower perplexity alone does not establish a better model across those changes.')],
'''
TRAIN=[["we","like","tea"],["we","like","coffee"],["they","like","tea"]]

def fit_bigram(documents,alpha=1.):
    raise NotImplementedError("Count sentence-bounded transitions and freeze the vocabulary")

def main():
    print("Three authored sentences loaded. Derive the four likelihood factors before coding.")

if __name__ == "__main__":
    main()
''',solution06,
['''**Interview: Why smooth an n-gram model?** Unseen continuations otherwise receive zero probability and make complete sequences impossible. Smoothing distributes probability beyond observed pairs under an explicit bias assumption; it does not create semantic knowledge.''','''**Interview: Why is BOS excluded from V here?** It is a conditioning marker rather than a predicted event. EOS is predicted and belongs in the denominator. Different conventions are possible, but the probability and evaluation definitions must agree.''','''**Interview: Does lower perplexity mean better factual answers?** It means better average predictive probability on the specified token events. Factuality, grounding and task utility require separate evaluation.'''],
['[Jurafsky and Martin, n-gram language models](https://web.stanford.edu/~jurafsky/slp3/)'])

solution07=r'''
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

TRAIN=["tea tea cup","coffee cup"]

def main():
    vectorizer=TfidfVectorizer(norm="l2",smooth_idf=True,sublinear_tf=False)
    x=vectorizer.fit_transform(TRAIN)
    names=vectorizer.get_feature_names_out().tolist()
    assert names==["coffee","cup","tea"] and x.shape==(2,3)
    a=np.log(3/2)+1
    assert np.allclose(vectorizer.idf_,[a,1,a])
    raw=np.array([[0.,1.,2*a],[a,1.,0.]])
    expected=raw/np.linalg.norm(raw,axis=1,keepdims=True)
    assert np.allclose(x.toarray(),expected)
    query=vectorizer.transform(["tea"])
    score=(x@query.T).toarray().ravel()
    assert np.isclose(score[0],2*a/np.sqrt(1+4*a*a)) and score[1]==0
    before=vectorizer.vocabulary_.copy()
    unknown=vectorizer.transform(["matcha",""])
    assert unknown.nnz==0 and vectorizer.vocabulary_==before
    assert np.allclose(np.sqrt(x.multiply(x).sum(axis=1)).A.ravel(),1.)
    sublinear=TfidfVectorizer(norm=None,smooth_idf=True,sublinear_tf=True).fit(TRAIN)
    weighted=sublinear.transform(["tea tea cup"]).toarray()[0]
    tea=sublinear.vocabulary_["tea"]
    assert np.isclose(weighted[tea],(1+np.log(2))*a)
    print("nlp-007: manual DF/IDF/TF-IDF and sparse cosine match; OOV abstention boundary passed")

if __name__ == "__main__":
    main()
'''
author(7,
'''Bag-of-words representations turn documents into vectors whose coordinates correspond to a fixed vocabulary. A count says how often a term appears in one document. Document frequency says in how many training documents it appears. TF-IDF combines within-document frequency with a corpus-level rarity weight, providing a useful sparse baseline for classification and retrieval.

The unit is one document, not one token or one customer. Repeated occurrences of tea in a document increase term frequency but count only once toward document frequency. Changing the document boundaries therefore changes IDF even if the concatenated text is unchanged. Preserve the corpus definition and fit the vocabulary/IDF only on the training or indexed collection appropriate to the evaluation claim.

This lesson derives the exact smoothing and normalization convention used by a real scikit-learn TfidfVectorizer. TF-IDF is a family of weighting choices, so an undocumented formula can produce a valid-looking vector different from a library\'s result. We compare every coordinate against a hand-built oracle before using cosine scores.''',
[
('Derive the chosen weighting convention', '''Let n be the number of training documents and df_j the number containing term j. With smooth_idf=True, the implementation used here assigns idf_j=log((1+n)/(1+df_j))+1. The natural logarithm and final plus one matter. Raw term frequency multiplies that weight by the count tf_ij; optional sublinear frequency instead uses 1+log(tf_ij) for positive counts.

The two training documents are tea tea cup and coffee cup. Sorted vocabulary order is [coffee,cup,tea]. Coffee and tea each occur in one document, while cup occurs in both. Thus the rare-term weight a is log(3/2)+1, and cup has weight one. Before normalization the rows are [0,1,2a] and [a,1,0].

L2 normalization divides each nonzero row by its Euclidean norm. It removes overall magnitude from cosine comparisons while retaining relative term weighting. The first row norm is sqrt(1+4a^2). A repeated term still changes direction relative to other terms, so normalization does not erase every effect of document length or repetition.'''),
('Read the sparse matrix and API', '''fit_transform learns the vocabulary and IDF from TRAIN and returns a sparse matrix. transform applies those frozen values to a query or held-out document. get_feature_names_out supplies the column mapping. Never interpret coefficient or vector position zero as a particular word without checking that mapping.

A sparse matrix stores nonzero entries rather than a full dense rectangle. This matters when thousands of documents use only a small fraction of a large vocabulary. The worked fixture can safely call toarray because it is only two by three. Converting a real corpus matrix to dense can exhaust memory, so use sparse multiplication and bounded inspection in production.

For normalized nonzero vectors, cosine equals their dot product. The expression X @ query.T produces one score per document. A query with no known terms becomes a zero vector. The computed dot products are all zero, but that is an absence-of-representation case, not evidence that every document is equally irrelevant. A retrieval system should recognize it and choose an explicit fallback or abstention.'''),
('Representation limitations and diagnosis', '''A unigram representation ignores order, so dog bites person and person bites dog share the same counts. It can also lose negation, domain synonyms and spelling variants. Character n-grams, word n-grams or other representations may address some failures, but each changes the vocabulary and evaluation contract. A dense embedding is another candidate, not an automatic replacement for a useful lexical baseline.

IDF is not a truth or importance score. A rare typo can get a high weight, while a common domain term can be essential to the task. Inspect tokenization, stopwords and minimum-frequency policies rather than treating every high-IDF term as meaningful. Fitting IDF on an evaluation collection can be appropriate for a clearly transductive retrieval setup, but it cannot be silently described as a training-only inductive experiment.

The reference checks raw counts, IDF values, normalized vectors, cosine, sublinear TF and frozen unknown-token behavior separately. This decomposition helps locate a mismatch: a wrong document frequency differs from a right vector with the wrong normalization or vocabulary order.''')],
[
('Compute DF and IDF','''For the two authored documents, df(coffee)=1, df(cup)=2 and df(tea)=1. With the chosen smoothed formula, IDF is [a,1,a] where a=log(1.5)+1, about 1.40547. Counting the two tea occurrences as df=2 would incorrectly reduce its IDF.'''),
('Normalize and retrieve','''The first raw weighted row [0,1,2a] becomes that row divided by sqrt(1+4a^2). Query tea becomes [0,0,1]. Their dot product is 2a/sqrt(1+4a^2), while the coffee document has score zero. The score follows the declared lexical representation and does not claim semantic understanding of tea.'''),
('Observe an unsupported query','''Both matcha and an empty query produce zero stored entries under the frozen vocabulary. The vocabulary remains unchanged. A production search endpoint should report or handle this boundary explicitly rather than returning a seemingly meaningful ranking based only on arbitrary tie order.''')],
[
('Count documents, not occurrences','Calculate DF for the three sorted terms from the two-document corpus.','[1,2,1] for [coffee,cup,tea].','Each document contributes at most one to a term\'s DF.','Tea appears twice but only in one document, so its document frequency is one. Cup appears once in each of two documents, so its DF is two. This distinction is the basis for the IDF weighting and is independent of the raw within-document counts.'),
('Match the IDF formula','Implement the stated smoothed IDF and compare with vectorizer.idf_.','[log(3/2)+1,1,log(3/2)+1] in the verified vocabulary order.','Include both smoothing additions and the final plus one.','Different TF-IDF conventions omit one or more of these terms. The reference fixes the exact scikit-learn settings and checks the resulting array, so agreement is about a specified implementation rather than the vague label TF-IDF.'),
('Build the normalized rows','Construct both weighted rows manually and normalize each nonzero row.','Manual dense oracle matches the 2-by-3 sparse result within tolerance.','Normalize after multiplying counts by IDF.','The first tea coordinate is twice its IDF because raw TF is two. Dividing by each row\'s L2 norm changes all nonzero coordinates together. Comparing every coordinate catches vocabulary-order and normalization mistakes that one retrieval score might miss.'),
('Compute sparse cosine','Transform query tea and multiply X by its transpose.','First score 2a/sqrt(1+4a^2); second score zero.','Normalized nonzero vectors turn cosine into a dot product.','The query has only the tea coordinate, so the score reads that coordinate from each normalized document. This exact small calculation verifies the sparse API path. It does not establish that the highest lexical score is the best answer for a real user.'),
('Handle OOV without refitting','Transform matcha and empty text, then compare the vocabulary before/after.','Zero nonzero entries and unchanged vocabulary; record an explicit no-known-terms outcome.','Use transform rather than fit_transform for evaluation queries.','Refitting on the query would alter the column space and make comparisons invalid. The zero vector needs a declared fallback because cosine is not geometrically defined for a zero norm even though sparse dot products return numerical zeros.'),
('Change one weighting choice','Enable sublinear_tf without normalization and inspect the tea weight.','Tea weight becomes (1+log(2))*a, distinct from 2a.','Keep the same fitted corpus, IDF smoothing and column mapping.','Sublinear TF reduces the influence of repeated words while leaving IDF unchanged. This controlled comparison shows which part of the representation changed. Select the choice using the downstream task and an honest evaluation split, not from one favorable query.')],
'''
TRAIN=["tea tea cup","coffee cup"]

def manual_tfidf(documents):
    raise NotImplementedError("Derive counts, DF, IDF and row normalization")

def main():
    print("Two local documents loaded. Keep the training vocabulary frozen for query tests.")

if __name__ == "__main__":
    main()
''',solution07,
['''**Interview: Why can TF-IDF remain useful beside dense embeddings?** It provides an efficient lexical baseline that preserves exact rare terms and is easy to inspect. Domain names and identifiers can favor lexical matching; compare or combine representations using task evidence.''','''**Interview: Is IDF fitted on test text always leakage?** The answer depends on the declared setup. A fixed indexed corpus can be part of a transductive retrieval task, while an inductive classification claim requires train-only fitting. The information boundary must be explicit.''','''**Interview: Why avoid toarray on a real corpus?** Sparse matrices save memory by storing nonzero values. Densifying can allocate documents times vocabulary entries even when almost all are zero. Inspect bounded slices or use sparse operations.'''],
['[scikit-learn text feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction)'])

solution08=r'''
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from scipy.special import logsumexp

X=np.array([[2.,1.],[1.,0.],[0.,2.],[0.,1.]])
Y=np.array([1,1,0,0])

def manual_nb(x,y,alpha=1.,prior=None):
    if np.any(x<0) or alpha<=0:raise ValueError("nonnegative counts and positive alpha required")
    classes=np.unique(y)
    counts=np.array([x[y==label].sum(axis=0) for label in classes])
    likelihood=(counts+alpha)/(counts.sum(axis=1,keepdims=True)+alpha*x.shape[1])
    class_prior=np.array([np.mean(y==label) for label in classes]) if prior is None else np.asarray(prior,dtype=float)
    if np.any(class_prior<=0) or not np.isclose(class_prior.sum(),1):raise ValueError("positive normalized prior required")
    return classes,np.log(likelihood),np.log(class_prior)

def posterior(probe,log_likelihood,log_prior):
    score=np.asarray(probe)@log_likelihood.T+log_prior
    return np.exp(score-logsumexp(score,axis=-1,keepdims=True))

def main():
    classes,ll,lp=manual_nb(X,Y)
    assert classes.tolist()==[0,1]
    assert np.allclose(np.exp(ll),[[1/5,4/5],[4/6,2/6]])
    probe=np.array([[1.,0.]])
    p=posterior(probe,ll,lp)
    assert np.allclose(p,[[3/13,10/13]])
    model=MultinomialNB(alpha=1.).fit(X,Y)
    assert np.allclose(model.feature_log_prob_,ll) and np.allclose(model.predict_proba(probe),p)
    assert np.allclose(posterior([[0.,0.]],ll,lp),[[.5,.5]])
    _,ll2,lp2=manual_nb(X,Y,prior=[.9,.1])
    changed=posterior(probe,ll2,lp2)
    assert changed[0,0]>changed[0,1]
    # Fixed vocabulary [urgent,thanks] cannot represent absent not.
    urgent=np.array([1.,0.]);not_urgent=np.array([1.,0.])
    assert np.array_equal(posterior(urgent,ll,lp),posterior(not_urgent,ll,lp))
    assert np.isclose(np.exp(ll[0]).sum(),1.) and np.isclose(np.exp(ll[1]).sum(),1.)
    print("nlp-008: manual/library parity; posterior [3/13,10/13]; prior and negation boundaries passed")

if __name__ == "__main__":
    main()
'''
author(8,
'''Multinomial Naive Bayes is a compact probabilistic baseline for nonnegative text counts. It models the class prior and the distribution of token events within each class, then combines those pieces with Bayes\' rule. Its conditional-independence assumption is strong, but the resulting classifier can be useful even when the language is not actually generated independently word by word.

The feature order is [urgent,thanks]. Four documents have count rows [2,1],[1,0],[0,2],[0,1] and labels [1,1,0,0]. We derive the fitted probabilities by hand and compare them with a real scikit-learn MultinomialNB. This establishes implementation parity on a known fixture, not a claim of calibrated confidence or deployment accuracy.

Separate the prior probability of a class from the likelihood of tokens under that class. A word can favor an urgent class while a strong nonurgent prior still makes the posterior nonurgent. Class imbalance and the target population therefore matter to the decision, not just the presence of a distinctive keyword.''',
[
('Derive the multinomial likelihood and posterior', '''For class c and vocabulary term j, estimate theta_cj=(N_cj+alpha)/(sum_j N_cj+alpha*V), where N_cj is the total training count in that class and V is vocabulary size. The class prior pi_c can come from document frequencies or a specified target prior. The log score for document counts x is log pi_c+sum_j x_j*log theta_cj. A multinomial coefficient common to all classes cancels when comparing posterior classes for the same document.

Class zero contains total counts [0,3], while class one contains [3,1]. With alpha one and V two, their token probabilities are [1/5,4/5] and [4/6,2/6]. There are two documents in each class, so priors are one-half each. For probe [1,0], unnormalized posterior weights are 0.1 and 1/3. Dividing by their sum yields [3/13,10/13].

The prior counts documents, while likelihood counts token events. Mixing these denominators is a common implementation error. The normalization of each theta row provides an independent check before any posterior is calculated.'''),
('Use logs and verify the actual estimator', '''The model multiplies token probabilities repeatedly, so log-space addition avoids numerical underflow. To normalize scores, subtract logsumexp across classes before exponentiating. logsumexp evaluates the logarithm of the sum of exponentials stably; directly exponentiating very negative log scores can turn every class weight into zero.

In the reference, model.feature_log_prob_ is compared with the hand-computed matrix, and predict_proba is compared with [3/13,10/13]. The class order is checked explicitly as [0,1]. Never assume the first probability column means urgent without reading model.classes_. A classifier can return perfectly valid numbers attached to the wrong labels if the consumer assumes a different order.

An all-zero feature vector has no token evidence, so its posterior equals the prior under this formulation. This can arise from empty text or a completely out-of-vocabulary message. It is not a confident semantic judgment. A production pipeline should identify the no-evidence condition separately from ordinary classification.'''),
('Why naive does not mean harmless', '''Conditional independence assumes token events are independent given the class in the modeled likelihood. Real phrases violate this through grammar, repetition and correlated vocabulary. The assumption can overcount related evidence, producing overconfident probabilities even when the decision boundary is useful. Evaluate probability calibration separately from classification accuracy.

A fixed vocabulary lacking not gives urgent and not urgent the same feature vector. Naive Bayes cannot recover information absent from the representation. Adding bigrams or a richer encoder can help only if training labels and evaluation cover the distinction. The model name is not a substitute for an error analysis.

Changing the class prior to [0.9,0.1] flips the stated urgent-only probe toward class zero, even though the token likelihoods stay fixed. Such a change is a model of a different population or decision setting, not a free accuracy trick. If label prevalence shifts, consider whether the conditional feature distributions also changed before applying a prior adjustment.''')],
[
('Calculate class-conditional word probabilities','''Summing the first two urgent rows gives [3,1], and summing the other rows gives [0,3]. Laplace smoothing adds one to each coordinate. The resulting likelihood rows are [0.2,0.8] for class zero and [2/3,1/3] for class one. Each sums to one.'''),
('Normalize a posterior','''For a single urgent token, prior-times-likelihood is [0.5*0.2,0.5*(2/3)]=[0.1,1/3]. Their normalized values are [3/13,10/13]. The actual library fit must match these values and the intermediate log likelihoods within numerical tolerance.'''),
('Change the prior and expose missing context','''With prior [0.9,0.1], weights become [0.18,1/15], so the same token evidence favors class zero overall. Separately, urgent and not urgent remain indistinguishable if not is outside the feature vocabulary. These are different failure mechanisms: population assumptions versus missing representation.''')],
[
('Aggregate by class','Calculate the two class-by-feature count rows and document priors.','Counts [[0,3],[3,1]] in class order[0,1]; priors [.5,.5].','Count documents for priors and tokens for likelihoods.','The class-zero documents contain three thanks events and no urgent events. Class one contains three urgent and one thanks. Each class contains two documents, so the prior is balanced despite unequal total token counts. Keeping those units separate is essential to the model.'),
('Apply Laplace smoothing','Compute the class token probabilities with alpha=1 and V=2.','Likelihoods [[1/5,4/5],[4/6,2/6]], each summing to one.','Add alpha once per vocabulary term in numerator and denominator.','Smoothing assigns a nonzero urgent probability to class zero despite no observed urgent events there. The denominator is class token total plus alpha times vocabulary size. Using the number of documents instead would not normalize the multinomial token distribution.'),
('Compute stable posteriors','Score probe [1,0] in log space and normalize with logsumexp.','Posterior [3/13,10/13] for classes[0,1].','Start from log prior and add count-weighted log likelihoods.','The two unnormalized weights are 0.1 and one-third. Their sum is 13/30, giving the stated fractions. Logsumexp computes the same normalization without underflow. Matching one argmax alone would miss a wrong probability scale, so compare the full vector.'),
('Verify library parity','Fit MultinomialNB on the exact matrix and compare classes, feature logs and posterior.','All three agree with the independent manual oracle.','Inspect classes_ before assigning column meanings.','The library is an implementation under specified defaults, not an oracle for the task itself. The independent counts and fractions verify that the estimator matches the intended mathematical model. This is stronger than comparing two calls to the same library function.'),
('Inspect prior and empty input','Use an all-zero probe and then change prior to [.9,.1] for the urgent-only probe.','Empty evidence returns prior; changed prior makes class zero more probable.','A zero count vector contributes zero log-likelihood terms.','With no represented token evidence, only the class prior remains. For the changed population prior, the nonurgent prior advantage outweighs the urgent token likelihood ratio. Report this as a modeling assumption and validate whether a prior-only adjustment is justified for the deployment shift.'),
('Expose negation and overconfidence','Compare urgent and not urgent under the fixed two-term vocabulary and explain correlated-word evidence.','Identical represented inputs/posteriors; a written warning distinguishes class accuracy from probability calibration.','A classifier cannot use a distinction erased by its features.','The missing not coordinate makes the messages identical to the model. Conditional-independence violations can also multiply related evidence as if it were independent, yielding extreme probabilities. Richer features and calibration are possible repairs, but they need held-out evaluation rather than a claim that a more complex model automatically understands the text.')],
'''
import numpy as np
X=np.array([[2.,1.],[1.,0.],[0.,2.],[0.,1.]])
Y=np.array([1,1,0,0])

def manual_nb(x,y,alpha=1.):
    raise NotImplementedError("Derive class counts, priors and smoothed log likelihoods")

def main():
    print("Feature order is urgent,thanks. Derive the fractions before comparing a library fit.")

if __name__ == "__main__":
    main()
''',solution08,
['''**Interview: Why can Naive Bayes classify well despite false independence assumptions?** A useful decision boundary can survive imperfect probability modeling. That does not imply its confidence values are calibrated, so evaluate ranking, decisions and probabilities separately.''','''**Interview: Does Laplace smoothing add real observations?** It is a statistical regularization/pseudocount convention. It allocates mass to unseen token events under an assumption, rather than creating new empirical evidence.''','''**Interview: Why inspect class order?** Probability columns follow the estimator\'s class inventory. Misinterpreting the order can reverse a correct prediction without any numerical error in the fitted model.'''],
['[scikit-learn multinomial Naive Bayes](https://scikit-learn.org/stable/modules/naive_bayes.html#multinomial-naive-bayes)'])
