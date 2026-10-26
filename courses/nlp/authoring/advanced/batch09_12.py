from author import author

solution09 = r"""
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

TRAIN=["urgent outage","urgent incident","outage incident","thanks resolved","thanks update","resolved update"]
LABELS=np.array([1,1,1,0,0,0])

def fit_classifier(c=1.):
    if c<=0:raise ValueError("C must be positive")
    model=make_pipeline(CountVectorizer(token_pattern=r"(?u)\b\w+\b"),
                        LogisticRegression(C=c,solver="liblinear",random_state=0,max_iter=500))
    return model.fit(TRAIN,LABELS)

def sigmoid(score):
    score=np.asarray(score,dtype=float)
    return np.exp(-np.logaddexp(0.,-score))

def brier(probability,truth):
    p=np.asarray(probability,dtype=float);y=np.asarray(truth,dtype=float)
    if p.shape!=y.shape or p.size==0 or not np.all(np.isfinite(p)):
        raise ValueError("equal nonempty finite arrays required")
    if np.any((p<0)|(p>1)) or np.any((y!=0)&(y!=1)):
        raise ValueError("binary labels and probabilities required")
    return float(np.mean((p-y)**2))

def main():
    x=np.array([2.,1.]);weights=np.array([2.,-1.]);score=x@weights-.5
    assert score==2.5 and np.isclose(sigmoid(score),.9241418199787566)
    model=fit_classifier();vectorizer=model[0]
    heldout=vectorizer.transform(["escalation urgent"])
    assert "escalation" not in vectorizer.vocabulary_ and heldout.shape[1]==6
    assert model.predict(["urgent outage","thanks resolved"]).tolist()==[1,0]
    small=fit_classifier(.1)[1].coef_;large=fit_classifier(10.)[1].coef_
    assert np.linalg.norm(small)<np.linalg.norm(large)
    p=np.array([.2,.4,.8])
    assert (p>=.5).tolist()==[False,False,True]
    assert (p>=.3).tolist()==[False,True,True]
    truth=[1,0,1,0]
    assert np.isclose(brier([.9,.9,.1,.1],truth),.41)
    assert np.isclose(brier([.6,.6,.4,.4],truth),.26)
    unigram=vectorizer.transform(["urgent","not urgent"]).toarray()
    assert np.array_equal(unigram[0],unigram[1])
    bigram=CountVectorizer(ngram_range=(1,2)).fit(["urgent","not urgent"])
    assert "not urgent" in bigram.vocabulary_
    try:brier([1.2],[1])
    except ValueError:pass
    else:raise AssertionError("invalid probability accepted")
    print("nlp-009: logit=2.5; Brier=.41/.26; threshold and negation checks passed")

if __name__ == "__main__":
    main()
"""
author(
    9,
    """A linear text classifier is a useful baseline because its calculation can be inspected from tokens to a score. The input unit here is one short support message and the label indicates whether it belongs to an urgent category. The task is classification under a defined annotation policy, not a claim that a particular word always implies real operational urgency. A customer can quote an urgent message, negate it or use unfamiliar language.

The representation maps each document to a vector x of token counts. A binary logistic model computes z=w_transpose*x+b and p=1/(1+exp(-z)). The coefficient w_j changes the log odds by w_j for one additional occurrence of feature j, conditional on the other represented features. The bias b shifts the baseline score. The model learns these values by minimizing a classification loss plus a regularization penalty, not by counting how often a coefficient agrees with a causal explanation.

Separate three decisions: which features to represent, how to fit a score, and which score threshold triggers an action. A probability of 0.7 and a threshold of 0.8 produce a negative action without changing the probability estimate. Calibration asks whether predictions near 0.7 correspond to roughly 70 percent positives in the relevant population. Good ranking, calibrated probabilities and a useful decision rule are related but distinct properties.""",
    [
        (
            "Notation, loss and regularization",
            """For labels y in {0,1}, binary cross-entropy is -y*log(p)-(1-y)*log(1-p). It penalizes confident mistakes strongly. An L2 penalty discourages large coefficient magnitudes, reducing variance when many correlated token features have little support. In the scikit-learn interface used here, smaller C means stronger regularization. This parameter is not a probability or a universal complexity scale across datasets.

A separable tiny corpus can tempt an unregularized fit toward extreme coefficients. That would make the training messages look certain without establishing confidence on new language. The fixture therefore checks a qualitative effect of regularization, smaller coefficient norm for smaller C, rather than asserting that one setting is universally optimal. Tune C using a held-out development design with document families kept together.

Use numerically stable expressions for sigmoid and log loss. Directly evaluating exp(-z) can overflow for a very negative z. The reference sigmoid uses exp(-logaddexp(0,-z)), where logaddexp computes a stable log-sum-exp. This is a numerical implementation detail with a substantive consequence: finite scores should not become NaN probabilities merely because their magnitude is large.""",
        ),
        (
            "Syntax anatomy and leakage boundaries",
            """make_pipeline chains a CountVectorizer and LogisticRegression so fitting the pipeline fits the vocabulary only on training text. transform applies that frozen vocabulary to held-out text. The unknown token escalation is ignored in this deliberately simple count representation; it must not expand the vocabulary during evaluation. The model\'s feature_names and coefficient positions must remain aligned.

CountVectorizer produces a sparse document-by-feature matrix. A row is a document, a column is a vocabulary item, and an entry is a count. The toy training corpus has six vocabulary items and six documents. This is enough to trace a mechanism, not estimate deployment accuracy. Real splits should hold out related templates, users and time periods when those relationships create dependence.

A pipeline does not automatically solve all leakage. If the documents already include post-resolution phrases unavailable at triage time, a correctly implemented split can still evaluate the wrong information set. Write down when each message fragment and label would be known.""",
        ),
        (
            "Calibration and failure diagnosis",
            """The Brier score is the mean of (p-y)^2 for binary outcomes. It evaluates probability quality, combining calibration and discrimination effects; it is not a pure calibration-only statistic. The reference compares two fixed probability arrays to explain scoring. It does not fit or claim a calibrated model from four observations. A real calibrator needs separate predictions and labels, usually through a held-out or cross-validated procedure that avoids fitting and judging on the same cases.

A bag-of-words model can ignore negation and word order. Because not is absent from the training vocabulary, urgent and not urgent map to the same vector in this fixture. Adding bigrams creates a feature for not urgent, but a feature name alone does not teach the correct label. You still need representative annotated examples and evaluation. Diagnose the error as a representation/training-data problem before increasing optimizer iterations.

Inspect false positives, false negatives, unknown-token rates and performance by text family. A good average score can hide failures on short messages, dialects or newly introduced product names. Coefficients describe the learned representation and corpus, not universal linguistic rules.""",
        ),
    ],
    [
        (
            "Compute a score by hand",
            """For feature order [urgent,thanks], counts [2,1], weights [2,-1] and bias -0.5, z=2*2+1*(-1)-0.5=2.5. The sigmoid is approximately 0.92414. Increasing thanks by one lowers the logit to 1.5; it does not subtract exactly one from the probability because the sigmoid is nonlinear.

```python
import numpy as np
x=np.array([2.,1.]);w=np.array([2.,-1.]);z=x@w-.5
p=np.exp(-np.logaddexp(0.,-z))
print(z,p)
```

Expected: 2.5 and approximately 0.92414. The vector order is part of the contract.""",
        ),
        (
            "Compare decisions and probability loss",
            """Probabilities [0.2,0.4,0.8] yield [false,false,true] at threshold 0.5 and [false,true,true] at 0.3. No retraining is needed to change the action threshold. For labels [1,0,1,0], probabilities [0.9,0.9,0.1,0.1] have Brier score 0.41; the less extreme [0.6,0.6,0.4,0.4] score 0.26. The second array is better on these four labels, but this does not establish population calibration.

```python
p=np.array([.9,.9,.1,.1]);y=np.array([1,0,1,0])
print(np.mean((p-y)**2))
```

Expected: 0.41. Retain labels and probabilities together so the denominator and error units are explicit.""",
        ),
        (
            "Fit a real local baseline",
            """The executable reference fits an actual scikit-learn logistic classifier to six authored messages. It predicts the two unambiguous probes urgent outage and thanks resolved as classes one and zero, and verifies that held-out escalation never enters the training vocabulary. These checks establish the implementation and fixture behavior. They do not create a meaningful test-set accuracy claim from two easy probes.""",
        ),
    ],
    [
        (
            "Trace log odds",
            "Implement a stable sigmoid and evaluate the stated two-feature score.",
            "Logit 2.5 and probability approximately 0.92414182; finite outputs at logits +/-1000.",
            "Compute the dot product before applying the nonlinear function. Use logaddexp for stability.",
            "The count vector contributes four from urgent and minus one from thanks, then the intercept subtracts one-half. The resulting logit is 2.5. Applying a stable sigmoid yields the stated probability. Extreme finite logits approach zero or one without overflowing. This verifies arithmetic and numerical behavior, not a real confidence guarantee.",
        ),
        (
            "Freeze the vocabulary",
            "Fit the six-message classifier and transform escalation urgent without refitting.",
            "Exactly six learned vocabulary terms; escalation absent; two stated probes predicted [1,0].",
            "Use fit on TRAIN and transform on held-out text through one pipeline.",
            "Fitting creates a mapping from training tokens to columns. The evaluation token escalation has no column and is ignored under the declared policy. A fit_transform call on evaluation data would change the representation and invalidate the comparison. The reference checks vocabulary membership directly rather than relying only on final predictions.",
        ),
        (
            "Compare regularization",
            "Fit the same corpus with C=0.1 and C=10 using the same solver/settings.",
            "The C=0.1 coefficient norm is smaller; record both norms and do not call either universally best.",
            "C is inverse regularization strength. Keep all other inputs fixed.",
            "Stronger L2 regularization penalizes large weights, so the small-C solution uses a smaller norm on this fixture. This is a controlled mechanism check. Model selection still needs independent development cases, and the most regularized model need not have the best task performance.",
        ),
        (
            "Separate a threshold",
            "Apply thresholds 0.5 and 0.3 to [0.2,0.4,0.8] with >= semantics.",
            "Actions [false,false,true] and [false,true,true].",
            "Changing a threshold changes decisions, not the stored probabilities.",
            "Only the middle probability lies between the thresholds. The comparison must state whether equality triggers the positive action. In deployment the threshold should follow costs, capacity and calibration evidence, not be selected retrospectively on the final test labels.",
        ),
        (
            "Inspect probability quality",
            "Compute both Brier scores for the four labels and reject probabilities outside [0,1].",
            "Scores 0.41 and 0.26; invalid 1.2 raises ValueError.",
            "Square each probability-label residual, then average over four observations.",
            "The first array makes two highly confident mistakes and two confident correct predictions. Its losses are .01,.81,.81,.01, averaging .41. The second gives .16,.36,.36,.16, averaging .26. This demonstrates a proper scoring calculation; it does not establish that moving every probability toward .5 always improves a model.",
        ),
        (
            "Expose negation loss",
            "Compare frozen unigram features for urgent and not urgent, then inspect an isolated bigram representation.",
            "The frozen unigram rows match; a separately fitted demonstration contains the not urgent bigram.",
            "Inspect feature vectors before inspecting predictions.",
            "The trained vocabulary lacks not, so both probe texts produce the same represented input. A deterministic model must then give the same score. A bigram representation can encode the distinction, but it needs labeled evidence to learn its meaning. Report the limitation rather than pretending a new feature guarantees correct negation handling.",
        ),
    ],
    """
import numpy as np
TRAIN=["urgent outage","urgent incident","outage incident","thanks resolved","thanks update","resolved update"]
LABELS=np.array([1,1,1,0,0,0])

def stable_sigmoid(score):
    raise NotImplementedError("Exercise 1: implement and explain the stable calculation")

def main():
    print("Six local training messages are ready. Implement the six guide tasks in this pad.")

if __name__ == "__main__":
    main()
""",
    solution09,
    [
        """**Interview: Why is logistic regression useful even when a transformer is available?** It is a cheap, inspectable baseline that reveals feature and label problems. A more complex model should demonstrate a relevant improvement under the same data boundary, cost accounting and evaluation design.""",
        """**Interview: Does predict_proba guarantee calibration?** No. It returns the model\'s probability estimate under its fitted formulation. Regularization, selection, distribution shift and misspecification can make those values poorly calibrated; evaluate them on representative held-out labels.""",
        """**Interview: What does a large token coefficient mean?** It changes the model\'s log odds conditional on the represented features. Correlated tokens, vocabulary choices and corpus artifacts affect it. It is not a causal effect of inserting the word into every real message.""",
    ],
    [
        "[scikit-learn logistic regression](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression)",
        "[scikit-learn probability calibration](https://scikit-learn.org/stable/modules/calibration.html)",
    ],
)

solution10 = r"""
import itertools
import numpy as np

def logs(values):
    values=np.asarray(values,dtype=float)
    if np.any(~np.isfinite(values)) or np.any((values<0)|(values>1)):
        raise ValueError("probabilities must be finite and within [0,1]")
    result=np.full(values.shape,-np.inf)
    np.log(values,out=result,where=values>0)
    return result

def viterbi(start,transition,emission):
    start=np.asarray(start,dtype=float);transition=np.asarray(transition,dtype=float)
    emission=np.asarray(emission,dtype=float)
    k=len(start)
    if start.ndim!=1 or transition.shape!=(k,k) or emission.ndim!=2 or emission.shape[1]!=k:
        raise ValueError("incompatible state/sequence shapes")
    if not np.isclose(start.sum(),1) or not np.allclose(transition.sum(axis=1),1):
        raise ValueError("start and transition distributions must normalize")
    ls,lt,le=logs(start),logs(transition),logs(emission)
    if len(emission)==0:return [],0.
    dp=ls+le[0];back=[]
    for t in range(1,len(emission)):
        candidates=dp[:,None]+lt
        previous=np.argmax(candidates,axis=0)
        dp=candidates[previous,np.arange(k)]+le[t]
        back.append(previous)
    state=int(np.argmax(dp));score=float(dp[state])
    if not np.isfinite(score):raise ValueError("no legal nonzero-probability path")
    path=[state]
    for previous in reversed(back):path.append(int(previous[path[-1]]))
    return list(reversed(path)),score

def bio_valid(tags):
    previous="O"
    for tag in tags:
        if tag!="O" and (len(tag)<3 or tag[:2] not in {"B-","I-"}):return False
        if tag.startswith("I-") and previous not in {"B-"+tag[2:],"I-"+tag[2:]}:return False
        previous=tag
    return True

def main():
    start=np.array([.6,.4]);transition=np.array([[.7,.3],[.4,.6]])
    emission=np.array([[.6,.1],[.2,.7]])
    path,score=viterbi(start,transition,emission)
    assert path==[0,1] and np.isclose(np.exp(score),.0756)
    brute=[]
    for candidate in itertools.product(range(2),repeat=2):
        value=start[candidate[0]]*emission[0,candidate[0]]*transition[candidate[0],candidate[1]]*emission[1,candidate[1]]
        brute.append((value,candidate))
    assert max(brute)[1]==tuple(path)
    persistent=np.array([[.99,.01],[.01,.99]])
    second=viterbi([.5,.5],persistent,[[.6,.4],[.2,.7]])
    assert second[0]==[1,1] and np.isclose(np.exp(second[1]),.1386)
    assert viterbi(start,transition,np.empty((0,2)))==([],0.)
    assert viterbi([.5,.5],[[.5,.5],[.5,.5]],[[1.,1.],[1.,1.]])[0]==[0,0]
    try:viterbi(start,transition,[[0.,0.]])
    except ValueError:pass
    else:raise AssertionError("impossible path accepted")
    assert bio_valid(["B-ORG","I-ORG","O"])
    assert not bio_valid(["I-ORG","O"]) and not bio_valid(["B-PER","I-ORG"])
    gold=["B-ORG","I-ORG","O"];pred=["B-ORG","O","O"]
    assert sum(a==b for a,b in zip(gold,pred))/len(gold)==2/3
    print("nlp-010: best paths [0,1]/[1,1]; probabilities .0756/.1386; BIO boundaries passed")

if __name__ == "__main__":
    main()
"""
author(
    10,
    """Sequence labeling assigns a label to every token while accounting for relationships among neighboring labels. Part-of-speech tagging, entity tagging and some segmentation tasks have this shape. A document classifier returns one label for a whole document; a sequence tagger returns an ordered label sequence aligned with tokens. Losing that alignment can make a numerically valid output unusable.

A hidden Markov model separates hidden label transitions from observed token emissions. For labels s_1,...,s_T and observations x_1,...,x_T, its joint probability is pi(s_1)*b_s1(x_1)*product_(t=2)^T a_(s_(t-1),s_t)*b_st(x_t). The initial distribution pi chooses the first state, a describes state transitions, and b describes token likelihood within a state. Conditional independence assumptions make this model tractable but limit its linguistic realism.

Viterbi decoding finds the single highest-probability complete path. It does not compute the marginal probability of each token\'s label, and choosing the most likely label at each position independently can produce a different sequence. This lesson implements the actual dynamic program on tiny authored probability tables, compares it with exhaustive enumeration and then examines BIO entity constraints.""",
    [
        (
            "Derive the recurrence and its complexity",
            """Let D_t(j) be the log probability of the best partial path ending in state j at position t. Initialization is \\(D_1(j)=\\log\\pi_j+\\log b_j(x_1)\\). The recurrence is \\(D_t(j)=\\log b_j(x_t)+\\max_i\\left[D_{t-1}(i)+\\log a_{ij}\\right]\\). Store the maximizing predecessor i for every j and t. After selecting the largest final score, walk those backpointers in reverse to recover the path.

The recurrence keeps only the best partial path ending in each state because future factors depend on the current state, not the whole earlier history. This is the dynamic-programming optimal-substructure argument. It reduces an exponential K^T enumeration to O(T*K^2) work for a dense K-state transition matrix, plus backpointer storage. A sparse transition graph can reduce work further.

Products of many probabilities underflow easily. Summing logs preserves ordering and makes a zero-probability transition negative infinity. The implementation uses np.log with an output buffer and where mask so exact zeros do not produce avoidable warnings. If every final score is negative infinity, it reports no legal path rather than returning an arbitrary argmax index.""",
        ),
        (
            "Interpret arrays and deterministic ties",
            "The emission array in this lesson has one row per observed token position and one column per candidate state. Its entry is the emission probability of that observed token under that state. Rows need not sum to one: they compare different conditional distributions for one observation. By contrast, the initial-state probabilities sum to one, and each transition row sums to one over next states.\n\nThe expression `dp[:,None]+log_transition` broadcasts the previous state scores into a previous-state-by-next-state matrix. `argmax(axis=0)` selects the best predecessor for each next state. The reference chooses the first state index for exact ties, making a repeated fixture deterministic. A different tie convention can yield a different path with the same score; record that policy rather than claiming the path is uniquely preferred.\n\nThe empty observation sequence returns an empty path with log probability zero, corresponding to probability one for an empty product. This is an explicit API convention. Invalid probability ranges, incompatible shapes and impossible observations are rejected separately.",
        ),
        (
            "BIO constraints and the evaluation unit",
            """BIO labeling uses B-TYPE for the beginning of an entity, I-TYPE for a continuation and O outside an entity. Under the strict policy here, I-ORG cannot start a sequence or follow O, and I-ORG cannot continue a B-PER span. Some corpora use different repair or tagging conventions, so a decoder and evaluator must share the same policy.

Illegal transitions can be forbidden by a transition mask in a structured model, but doing so changes the model and its normalization choices. The reference provides a separate strict BIO validator so the constraint is visible without pretending the two-state noun/verb HMM is already a trained named-entity model. A real tagger also needs token-offset alignment, annotation conventions, training data and held-out evaluation.

Token accuracy can conceal entity failure. For gold tags [B-ORG,I-ORG,O] and predictions [B-ORG,O,O], two of three tokens match, yet the two-token entity is not recovered exactly. Entity-level precision/recall should compare complete typed spans, while token metrics can remain diagnostic. This distinction becomes central in the next lesson.""",
        ),
    ],
    [
        (
            "Enumerate two-token paths",
            """Use states N=0 and V=1, initial probabilities [0.6,0.4], transitions [[0.7,0.3],[0.4,0.6]], and emissions [[0.6,0.1],[0.2,0.7]]. The N,V path has probability 0.6*0.6*0.3*0.7=0.0756. N,N gives 0.0504, V,N gives 0.0032, and V,V gives 0.0168. Viterbi must return [0,1] with log score log(0.0756).

This is small enough to enumerate independently, which gives a trustworthy oracle for the dynamic program rather than comparing it with another copy of itself.""",
        ),
        (
            "Show why greedy labels can fail",
            """Change the initial distribution to [0.5,0.5], transitions to [[0.99,0.01],[0.01,0.99]], and emissions to [[0.6,0.4],[0.2,0.7]]. The first token individually favors N and the second favors V, but switching states is expensive. The V,V path has probability 0.5*0.4*0.99*0.7=0.1386 and wins. Independent local choices do not optimize the complete joint probability.""",
        ),
        (
            "Inspect a legal-structure failure",
            """A strict BIO sequence [B-ORG,I-ORG,O] is valid; [I-ORG,O] and [B-PER,I-ORG] are invalid. These are data/label-structure checks, not semantic proof that the words are actually an organization or person. An entity evaluator must additionally compare token spans and types with the annotation contract.""",
        ),
    ],
    [
        (
            "Trace the first column",
            "Compute initialization log scores for the first fixture before any transition.",
            "Exponentiated initial scores are [0.36,0.04].",
            "Multiply initial state probability by the first emission, then take logs.",
            "The N partial path begins with .6*.6=.36 and the V path with .4*.1=.04. These scores include both starting plausibility and observation likelihood. Choosing only the largest emission would omit part of the model. Store one score per ending state rather than one global winner.",
        ),
        (
            "Implement backpointers",
            "Implement Viterbi and decode the first two-token fixture.",
            "Path [0,1], probability 0.0756 and two labels for two observations.",
            "For each next state choose its best predecessor, then trace backward from the final winner.",
            "The N,V path wins after accounting for the transition factor. Backpointers preserve which earlier state produced each final candidate. Returning only the final state loses the sequence. The reference checks the exact probability and alignment length, so a decoder with a correct final label but wrong history cannot pass.",
        ),
        (
            "Compare an independent oracle",
            "Enumerate all four two-state paths and compare the optimum with the decoder; then run the persistent-transition fixture.",
            "First optimum N,V at 0.0756; second optimum V,V at 0.1386.",
            "Use itertools.product for the tiny oracle, not the dynamic-program recurrence.",
            "Exhaustive enumeration independently multiplies the factors for each path. It is feasible only because the fixture is tiny, but it provides a meaningful implementation oracle. The second example demonstrates that selecting each token's favored state independently does not respect sequence transitions.",
        ),
        (
            "Handle boundaries",
            "Test an empty sequence, an all-zero emission row and exact ties.",
            "Empty path/log score 0; impossible row raises ValueError; tied fixture chooses [0,0].",
            "Zero probabilities become negative infinity. Define a tie policy explicitly.",
            "The empty product has probability one under the API convention. A zero likelihood for every state leaves no possible complete path and must not quietly produce state zero. Exact ties are different: several valid optima exist, and first-index argmax gives a deterministic documented choice.",
        ),
        (
            "Validate BIO structure",
            "Implement strict BIO validation for the three stated sequences.",
            "Valid [B-ORG,I-ORG,O]; reject leading I-ORG and a PER-to-ORG continuation.",
            "An I tag needs an immediately preceding B or I of the same type.",
            "The validator checks structural continuity. It does not know the words or whether the entity type is semantically correct. Keeping this boundary explicit avoids confusing a legal label sequence with a good named-entity recognizer. Other corpus conventions require a deliberate alternative policy.",
        ),
        (
            "Compare token and entity evidence",
            "Analyze the gold/predicted three-tag example and explain the exact-span result.",
            "Token accuracy 2/3 but zero exactly recovered two-token ORG entities.",
            "Write the gold and predicted token intervals before computing metrics.",
            "The gold entity covers token positions [0,2), while the predicted entity covers [0,1). They overlap but are not equal typed spans. Exact entity scoring therefore counts a false positive and false negative despite two matching token labels. The evaluation unit must match the extraction use case.",
        ),
    ],
    """
import numpy as np
START=np.array([.6,.4])
TRANSITION=np.array([[.7,.3],[.4,.6]])
EMISSION=np.array([[.6,.1],[.2,.7]])

def viterbi(start,transition,emission):
    raise NotImplementedError("Implement scores and backpointers after a hand trace")

def main():
    print("Two-state probability fixtures loaded. Record your trace and implement the six tasks.")

if __name__ == "__main__":
    main()
""",
    solution10,
    [
        """**Interview: Is Viterbi the same as selecting maximum marginal labels?** No. Viterbi optimizes one complete path. Marginal decoding optimizes a separate posterior label choice at each position and can produce a different or structurally illegal sequence under additional constraints.""",
        """**Interview: Why use logs?** They turn long products into sums and reduce underflow. Exact zero probability becomes negative infinity, which correctly rules out a path. A log transform preserves ordering of positive probabilities.""",
        """**Interview: Does a legal BIO sequence establish entity quality?** It establishes label structure only. The entity can still have wrong boundaries, wrong type or no support in the text. Evaluate complete typed spans and inspect semantic errors.""",
    ],
    [
        "[Jurafsky and Martin, Speech and Language Processing](https://web.stanford.edu/~jurafsky/slp3/)",
        "[CoNLL-2003 named-entity task definition](https://aclanthology.org/W03-0419/)",
    ],
)

solution11 = r"""
import re

def extract_entities(text,lexicon):
    if not isinstance(text,str):raise TypeError("text must be a string")
    if not lexicon:return []
    names=sorted(lexicon,key=lambda name:(-len(name),name))
    if any(not name for name in names):raise ValueError("empty entity name")
    pattern=re.compile(r"(?<!\w)(?:"+"|".join(re.escape(name) for name in names)+r")(?!\w)")
    return [(m.start(),m.end(),lexicon[m.group()],m.group()) for m in pattern.finditer(text)]

def exact_scores(gold,predicted):
    gold=set(gold);predicted=set(predicted)
    tp=len(gold&predicted);fp=len(predicted-gold);fn=len(gold-predicted)
    precision=tp/(tp+fp) if tp+fp else 0.
    recall=tp/(tp+fn) if tp+fn else 0.
    f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.
    return tp,fp,fn,precision,recall,f1

def acquisition(text):
    # Strict authored grammar, not general relation extraction.
    pattern=r"(?P<subject>Acme Labs|Beta Ltd) acquired (?P<object>Acme Labs|Beta Ltd)\."
    match=re.fullmatch(pattern,text)
    if match is None:return None
    return {"subject":match.group("subject"),"predicate":"acquired",
            "object":match.group("object"),"subject_span":match.span("subject"),
            "object_span":match.span("object")}

def main():
    text="Ada joined Acme Labs in Paris."
    lexicon={"Ada":"PER","Acme":"ORG","Acme Labs":"ORG","Paris":"LOC"}
    spans=extract_entities(text,lexicon)
    assert spans==[(0,3,"PER","Ada"),(11,20,"ORG","Acme Labs"),(24,29,"LOC","Paris")]
    assert all(text[start:end]==surface for start,end,kind,surface in spans)
    repeated=extract_entities("Ada met Ada.",{"Ada":"PER"})
    assert [(s,e) for s,e,_,_ in repeated]==[(0,3),(8,11)]
    assert extract_entities("C++ Labs",{"C++ Labs":"ORG"})==[(0,8,"ORG","C++ Labs")]
    gold={('d1',kind,start,end) for start,end,kind,_ in spans}
    pred={('d1','PER',0,3),('d1','ORG',11,15)}
    tp,fp,fn,p,r,f1=exact_scores(gold,pred)
    assert (tp,fp,fn)==(1,1,2) and p==.5 and r==1/3 and f1==.4
    forward=acquisition("Acme Labs acquired Beta Ltd.")
    reverse=acquisition("Beta Ltd acquired Acme Labs.")
    assert forward['subject']==reverse['object'] and forward['object']==reverse['subject']
    assert acquisition("Acme Labs did not acquire Beta Ltd.") is None
    assert acquisition("Rumor: Acme Labs acquired Beta Ltd.") is None
    assert extract_entities("",lexicon)==[]
    print("nlp-011: raw spans, exact F1=.4, directed relations and abstention checks passed")

if __name__ == "__main__":
    main()
"""
author(
    11,
    """An extraction system turns selected pieces of text into structured records. The useful output is not merely a word that looks like a name: it is an entity type, a source location, an identity policy and enough evidence for a reviewer to verify the claim. The unit of analysis here is a typed span in a particular raw document. Two identical names at different positions are different mentions; they may or may not refer to the same real entity.

Named-entity recognition identifies spans such as people, organizations or locations. Entity linking associates a mention with a canonical entity in a knowledge base. Coreference groups mentions referring to the same entity within or across text. Relation extraction identifies a typed relationship between mentions or linked entities. These tasks build on one another but are not interchangeable.

The executable system is an explicitly limited dictionary matcher plus a strict relation grammar over authored examples. It does not claim the general linguistic capability of a trained NER or relation model. Its narrow scope is useful because offsets, overlap, direction, negation and evaluation errors can be inspected exactly before replacing a component with a more flexible model.""",
    [
        (
            "Define a span and preserve its document",
            """A span is a half-open interval [start,end) in a stated representation. Python string indices count Unicode code points, not UTF-8 bytes or grapheme clusters. The interval should slice the unchanged source text to the reported surface string. If normalization changes length, old offsets cannot be applied to the new string without an alignment map. Preserve the original document ID and version alongside offsets.

A record such as (d1,ORG,11,20) means a typed mention in document d1, not an organization identity independent of the document. Entity-level comparison therefore includes document ID, type, start and end. Removing document identity before comparing sets can merge unrelated mentions from different sources. A duplicate predicted record should not create an extra true positive; the reference uses set-based exact mention comparison and documents that convention.

The lexicon contains both Acme and Acme Labs. Sorting candidate strings by decreasing length before constructing alternation makes the longer surface win at the same starting position for this nonoverlapping matcher. This is a deterministic extraction policy, not a universal rule for nested entities. Tasks requiring nested mentions need a different representation and evaluator.""",
        ),
        (
            "Syntax anatomy of an explainable matcher",
            """re.escape converts each lexicon string into a literal regex fragment, so metacharacters in a name such as C++ Labs do not become regex operators. The lookarounds (?<!\\w) and (?!\\w) reject a match embedded inside a longer word-character sequence under Python\'s Unicode regex convention. They are a declared boundary policy, not a complete multilingual word segmenter.

finditer returns match objects with start, end and group. Those three observations are recorded together. The matcher is case-sensitive by design: changing case behavior requires deciding whether the returned span and surface still refer to raw text. Empty names are rejected because an empty regex alternative could match at every position.

Dictionary coverage limits recall. A name absent from the lexicon is not detected, and a known name used in a different sense can create a false positive. The next engineering step is to measure those error categories on representative text, not to relabel the dictionary as a general named-entity model.""",
        ),
        (
            "Relations need direction, scope and uncertainty",
            """A relation is ordered when its meaning is ordered. Acme Labs acquired Beta Ltd differs from Beta Ltd acquired Acme Labs. The reference grammar retains subject and object spans so the role assignment is auditable. It uses fullmatch on one exact affirmative sentence form. A negated statement or a rumor prefix returns no extraction instead of being interpreted as a confirmed acquisition.

Real language adds passive voice, modality, attribution, temporal scope and coreference. Acme may acquire Beta next year does not establish that an acquisition occurred. Ada said it did likewise requires resolving it and understanding what Ada asserted. A broader model must represent uncertainty and provenance rather than force every sentence into a confident relation record.

Abstention is therefore part of the output contract. A missing relation can mean unsupported grammar, insufficient evidence or genuinely no relation, depending on the component. Keep those cases distinct in a production ledger. An empty extractor output should not silently become a verified negative business fact.""",
        ),
        (
            "Evaluate the complete mention",
            """Exact entity precision divides correctly recovered typed spans by predicted typed spans. Recall divides by gold spans. A boundary error can count as both a false positive and false negative even when most tokens match. Relaxed overlap metrics can be useful diagnostics, but they answer a different question and must be labeled separately.

The fixture has three gold entities and two predictions, only one exact. That gives TP=1, FP=1, FN=2, precision=1/2, recall=1/3 and F1=2/(2+1+2)=0.4. Do not report token accuracy as if it measured correct entity extraction. Also inspect errors by type and span length, since short common names can dominate a pooled score.""",
        ),
    ],
    [
        (
            "Locate three mentions",
            """In Ada joined Acme Labs in Paris., Ada occupies [0,3), Acme Labs [11,20), and Paris [24,29). Each span slices the raw string to the exact surface. The shorter lexicon entry Acme does not replace the longer organization at the same position under the declared longest-first policy.""",
        ),
        (
            "Score a near miss exactly",
            """Predict Ada correctly and predict the partial organization Acme at [11,15), omitting Paris. One prediction is correct, one is wrong, and two gold mentions are missing. Exact F1 is 0.4 even though the partial organization overlaps the right text. The boundary error matters when downstream code needs the full organization name.""",
        ),
        (
            "Retain relation direction and abstention",
            """The strict sentence Acme Labs acquired Beta Ltd. yields subject Acme Labs and object Beta Ltd. Reversing the names reverses roles. Acme Labs did not acquire Beta Ltd. and Rumor: Acme Labs acquired Beta Ltd. yield no assertion under this limited grammar. A real system should record why it abstained, not infer that the acquisition is impossible.""",
        ),
    ],
    [
        (
            "Extract raw spans",
            "Implement the dictionary matcher for the three-entity sentence.",
            "Exact spans [0,3),[11,20),[24,29) and correct PER/ORG/LOC types.",
            "Use match objects and verify each raw slice.",
            "The match positions come from the unchanged source. Storing only the surface text would lose provenance and make repeated names ambiguous. The expected intervals use code-point offsets and a half-open end, so text[start:end] reproduces each mention. This invariant should remain even if a learned model later proposes the spans.",
        ),
        (
            "Handle overlap and repetition",
            "Include Acme and Acme Labs in the lexicon; also match Ada met Ada.",
            "Longer organization wins; repeated Ada mentions occupy [0,3) and [8,11).",
            "Sort literal alternatives longest-first and preserve every match location.",
            "Longest-first alternation resolves one local overlap under a nonoverlapping matching policy. Repeated surface forms remain separate mentions because their offsets differ. Neither operation performs entity linking or coreference. A nested-entity task would require returning both compatible spans and changing evaluation accordingly.",
        ),
        (
            "Treat names as data",
            "Match the literal C++ Labs and reject an empty lexicon name.",
            "C++ Labs occupies [0,8); empty names raise a clear error.",
            "Escape regex metacharacters rather than interpolating them as pattern instructions.",
            "The plus signs are part of the organization surface. re.escape prevents them from changing regex repetition semantics. Empty alternatives would match zero-length positions and are rejected before compilation. This is an input-contract test, not a general guarantee against every pathological regex because the pattern here is constructed only from escaped literals.",
        ),
        (
            "Compute entity metrics",
            "Compare the stated three gold mentions with the two predicted mentions.",
            "TP=1,FP=1,FN=2,precision=.5,recall=1/3,F1=.4.",
            "Include document ID, type and both boundaries in each comparison key.",
            "The partial Acme span is not equal to Acme Labs, so it contributes a false positive and leaves the gold organization as a false negative. Paris adds another false negative. Set comparison avoids awarding duplicate predictions extra credit. State the empty-denominator convention if extending the evaluator.",
        ),
        (
            "Extract directed relations",
            "Implement the strict affirmative acquisition grammar and reverse the company order.",
            "Roles reverse exactly; negation and rumor-prefixed sentences abstain.",
            "Use fullmatch and named groups; do not search blindly for the verb.",
            "The grammar deliberately recognizes only one unambiguous surface form. Named groups preserve role direction and raw spans. Fullmatching prevents a rumor prefix from being silently discarded. This raises precision on the authored contract at the cost of recall for paraphrases, which is a measured tradeoff rather than a hidden capability claim.",
        ),
        (
            "Review coreference and scope",
            "Explain why Ada told Bea that she joined Acme Labs cannot be resolved by nearest-name matching alone.",
            "A written ambiguity record identifies Ada/Bea candidates and withholds a confirmed person-organization relation.",
            "Separate mention detection from referent resolution and assertion status.",
            "Both names are plausible antecedents without more context, and syntactic proximity is not a reliable semantic proof. The correct record preserves the sentence and uncertainty. A coreference model can propose candidates, but a domain pipeline needs an abstention or review policy and evaluation on ambiguous examples before promoting a proposal to an established relation.",
        ),
    ],
    """
TEXT="Ada joined Acme Labs in Paris."
LEXICON={"Ada":"PER","Acme":"ORG","Acme Labs":"ORG","Paris":"LOC"}

def extract_entities(text,lexicon):
    raise NotImplementedError("Return auditable raw spans after reading the guide")

def main():
    print(TEXT)
    print("Implement span extraction, exact scoring and the declared relation boundary.")

if __name__ == "__main__":
    main()
""",
    solution11,
    [
        """**Interview: Is a mention the same as an entity?** A mention is a text occurrence with location and type. Linking or coreference associates mentions with an underlying entity and needs additional evidence. Repeated strings alone are not a sufficient identity rule.""",
        """**Interview: Why can high token accuracy coexist with poor NER?** Most tokens may be outside entities, and a one-token boundary error can invalidate a full mention. Score complete typed spans and inspect class imbalance and boundary failures.""",
        """**Interview: Why not simply remove not before extraction?** Negation changes assertion meaning. A normalization rule that deletes it can turn a denied event into a confirmed structured fact. Preserve semantically important context and define an explicit assertion policy.""",
    ],
    [
        "[CoNLL-2003 named-entity evaluation task](https://aclanthology.org/W03-0419/)",
        "[Python regular-expression documentation](https://docs.python.org/3/library/re.html)",
    ],
)

solution12 = r"""
import numpy as np

def cooccurrence(documents,vocabulary,window=1):
    if window<1:raise ValueError("positive context window required")
    index={word:i for i,word in enumerate(vocabulary)}
    if len(index)!=len(vocabulary):raise ValueError("unique vocabulary required")
    matrix=np.zeros((len(index),len(index)),dtype=int)
    for tokens in documents:
        for i,word in enumerate(tokens):
            if word not in index:raise ValueError("unknown word")
            for j in range(max(0,i-window),min(len(tokens),i+window+1)):
                if i!=j:
                    if tokens[j] not in index:raise ValueError("unknown context")
                    matrix[index[word],index[tokens[j]]]+=1
    return matrix

def ppmi(counts):
    counts=np.asarray(counts,dtype=float)
    if counts.ndim!=2 or np.any(~np.isfinite(counts)) or np.any(counts<0):
        raise ValueError("finite nonnegative matrix required")
    total=counts.sum();result=np.zeros_like(counts)
    if total==0:return result
    denominator=counts.sum(axis=1)[:,None]*counts.sum(axis=0)[None,:]
    valid=(counts>0)&(denominator>0)
    result[valid]=np.maximum(0.,np.log(counts[valid]*total/denominator[valid]))
    return result

def cosine(a,b):
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
    if a.shape!=b.shape:raise ValueError("same shape required")
    denominator=np.linalg.norm(a)*np.linalg.norm(b)
    return None if denominator==0 else float(a@b/denominator)

def main():
    c=cooccurrence([["cat","pet","cat"]],["cat","pet"])
    assert c.tolist()==[[0,2],[2,0]]
    assert cooccurrence([["cat"],["pet"]],["cat","pet"]).sum()==0
    counts=np.array([[4.,3.,0.],[3.,4.,0.],[0.,0.,6.]])
    matrix=ppmi(counts)
    assert np.isclose(matrix[0,0],np.log(80/49)) and matrix[0,2]==0
    assert np.all(np.isfinite(matrix)) and np.all(matrix>=0)
    assert cosine(matrix[0],matrix[1])>0 and cosine(matrix[0],matrix[2])==0
    assert cosine([0,0],[1,0]) is None
    u,s,vt=np.linalg.svd(matrix,full_matrices=False)
    embedding=u[:,:2]*s[:2]
    reconstructed=embedding@vt[:2]
    assert np.linalg.norm(matrix-reconstructed)>0 and np.linalg.norm(matrix-reconstructed)<np.linalg.norm(matrix)
    assert np.isclose(cosine(embedding[0],embedding[1]),1.)
    rotation=np.array([[0.,-1.],[1.,0.]])
    assert np.isclose(cosine(embedding[0],embedding[1]),cosine(embedding[0]@rotation,embedding[1]@rotation))
    assert np.all(ppmi(np.zeros((2,2)))==0)
    print("nlp-012: window counts, PPMI, cosine, rank-two projection and rotation checks passed")

if __name__ == "__main__":
    main()
"""
author(
    12,
    """Distributional representations describe a word through the contexts in which it appears. The intuition is that words used in similar contexts may share useful properties. This is a statistical hypothesis about a corpus, not a guarantee of synonymy or factual equivalence. Antonyms often appear in similar contexts, and a rare word\'s apparent neighborhood can be unstable.

A co-occurrence matrix C has one row per target word and one column per context feature. C_ij counts how often target i appears with context j under a specified window. Changing the context definition changes the model: a symmetric nearby-word window, a directional window and a dependency relation capture different information. Document boundaries must remain explicit so unrelated final and initial words do not become artificial neighbors.

Dense embeddings compress or learn useful representations of these relationships. This lesson constructs actual count-based PPMI vectors and a truncated singular-value decomposition. It does not train word2vec, a contextual transformer or a pretrained semantic model. The exact small matrices make weighting, compression, cosine similarity and geometric invariances visible.""",
    [
        (
            "Count the modeled event before normalizing",
            """For a symmetric radius-one window, cat pet cat produces two cat-to-pet and two pet-to-cat directed context observations. The two occurrences of cat are distinct target positions. If cat and pet occur in separate one-token documents, there are no context pairs. Flattening the corpus first would invent cross-document observations and alter the probability model.

The vocabulary fixes row and column identities. A matrix without that mapping is not a reusable model. Unknown tokens need a declared policy; this reference rejects them rather than silently changing dimensions. A production pipeline may map them to an unknown token, skip them or use subword features, but the choice changes the estimated context distribution.

Window size controls a tradeoff between local syntactic patterns and broader topical association, while frequent words can dominate raw counts. Do not assume that a larger window is always better. Select it for a downstream task and hold evaluation families out of vocabulary/context learning when the claim requires inductive generalization.""",
        ),
        (
            "Derive PMI and positive PMI",
            """Let N be the sum of all context-pair counts, C_i+ the row total and C_+j the column total. Pointwise mutual information is \\(\\operatorname{PMI}(i,j)=\\log\\frac{C_{ij}/N}{(C_{i+}/N)(C_{+j}/N)}=\\log\\frac{C_{ij}N}{C_{i+}C_{+j}}\\). It compares observed co-occurrence with the independence expectation. Positive PMI replaces negative values with zero.

A zero count has undefined negative-infinite log ratio, so the implementation explicitly leaves it at zero in the PPMI matrix. An all-zero row remains a zero vector. Do not add an arbitrary epsilon everywhere without recognizing that this changes the estimator. Rare pair estimates can have large positive PMI from little evidence; smoothing or shifted weighting are possible deliberate alternatives.

The fixture count matrix [[4,3,0],[3,4,0],[0,0,6]] totals twenty. Its first cell has expected-independent count 7*7/20=2.45, so PMI is log(4/2.45)=log(80/49). The first two rows share positive contexts, while the third occupies a separate context. These are invented statistical relationships used to demonstrate the calculation, not discovered linguistic facts.""",
        ),
        (
            "Compress with SVD and interpret similarity",
            """Singular-value decomposition writes \\(M=U\\operatorname{diag}(s)V^{\\mathsf T}\\). Retaining the largest k singular values gives a rank-k reconstruction with a precise least-squares approximation property for the matrix. The embedding used here is \\(U_k\\operatorname{diag}(s_k)\\), with V_k_transpose used to reconstruct. Other conventions distribute singular-value powers differently and therefore change cosine geometry.

Cosine similarity is the dot product divided by the product of vector norms. It measures direction rather than magnitude and is undefined for a zero vector. The reference returns None for that boundary so missing representation is not mislabeled as meaningful dissimilarity. A normalized dot product and an unnormalized dot product answer different retrieval questions.

Rank-two compression makes the first two fixture rows collinear, losing their small distinction. That is a useful failure case: compression can improve a broad shared pattern while erasing fine-grained information. A rotation of all embeddings preserves dot products and cosine, so an individual coordinate does not have a unique semantic meaning. Analogy arithmetic and nearest neighbors require task-specific validation; an appealing example is not a general semantic guarantee.""",
        ),
    ],
    [
        (
            "Count contexts with boundaries",
            """cat pet cat within one document produces [[0,2],[2,0]] for vocabulary [cat,pet]. The same words in separate one-token documents produce an all-zero matrix. The difference comes from the defined event space, not normalization. Trace each target position and its allowed neighboring positions before implementing the loops.""",
        ),
        (
            "Calculate one PPMI cell",
            """For counts [[4,3,0],[3,4,0],[0,0,6]], N=20 and the first row/column totals are seven. The first PPMI entry is log(80/49), approximately 0.4902. A zero cross-group count remains zero. The first two rows have positive cosine similarity, while the first and third have cosine zero in this constructed matrix.""",
        ),
        (
            "Observe information lost by rank reduction",
            """A full SVD reconstructs the matrix up to floating tolerance. Keeping two dimensions leaves a positive reconstruction error but reduces it relative to the zero reconstruction. The first two reduced word vectors have cosine one, so the projection no longer distinguishes them by direction. A downstream task needing their subtle difference may prefer a higher rank or another representation.""",
        ),
    ],
    [
        (
            "Count a local window",
            "Implement radius-one co-occurrence for the two-token vocabulary and cat pet cat.",
            "Matrix [[0,2],[2,0]] with total four directed context events.",
            "Count each target position separately and exclude the target itself.",
            "The middle pet has two cat neighbors, and each outer cat has one pet neighbor. This creates four directed observations, not two undirected pairs. Document the direction convention because another definition can legitimately produce different counts.",
        ),
        (
            "Protect document boundaries",
            "Compare one three-token document with separate one-token documents.",
            "Separate documents yield zero context events; no cross-document pair is created.",
            "Loop over documents before positions.",
            "Flattening all tokens would treat unrelated boundary words as adjacent. The correct algorithm restarts the window at each document boundary. This is a corpus-contract issue that can materially change learned relationships in a large pipeline.",
        ),
        (
            "Implement finite PPMI",
            "Compute PPMI for the supplied 3-by-3 counts and an all-zero matrix.",
            "First cell log(80/49); all values finite/nonnegative; zero-count cells and empty matrix remain zero.",
            "Derive row, column and grand totals before taking logs only at positive cells.",
            "PMI compares joint frequency with independence. Masking positive cells prevents log(0) warnings and defines the positive-PMI boundary explicitly. An all-zero matrix contains no empirical context distribution; returning zeros is a documented representation convention, not an estimate of semantic relationships.",
        ),
        (
            "Handle cosine carefully",
            "Compare the first two PPMI rows, the first/third rows and a zero vector.",
            "Positive first-pair similarity, zero cross-group similarity, None for a zero-norm comparison.",
            "Check the denominator before division.",
            "A zero vector has no direction, so assigning a numeric cosine can hide an absent representation. The other comparisons follow the dot-product geometry of the authored matrix. They should not be generalized into claims that real words in those roles are synonyms or unrelated.",
        ),
        (
            "Inspect rank-two compression",
            "Construct U_k times singular values and reconstruct with V_k transpose.",
            "Positive reconstruction error smaller than the matrix norm; first two reduced rows have cosine one.",
            "Keep the same singular-value convention for embedding and reconstruction.",
            "Truncation removes the smallest singular component. In this symmetric fixture that component distinguishes the first two rows, so their remaining directions match. The example makes information loss inspectable and shows why compression quality and downstream semantic quality are different checks.",
        ),
        (
            "Test geometric invariance",
            "Rotate both two-dimensional embeddings by the same orthogonal matrix and compare cosine.",
            "Cosine unchanged; a written explanation rejects unique semantic meaning for one coordinate.",
            "Use a 90-degree rotation and preserve the same transformation for both vectors.",
            "Orthogonal rotation preserves inner products and norms, so cosine remains unchanged while coordinate values change. This demonstrates non-uniqueness of axes. A vector analogy can still be empirically useful, but its success must be evaluated across representative relations rather than inferred from one coordinate label.",
        ),
    ],
    """
import numpy as np
COUNTS=np.array([[4.,3.,0.],[3.,4.,0.],[0.,0.,6.]])

def ppmi(counts):
    raise NotImplementedError("Implement masked PMI from explicit corpus totals")

def main():
    print("The authored context matrix is ready. Trace counts before implementing the six tasks.")

if __name__ == "__main__":
    main()
""",
    solution12,
    [
        """**Interview: Does distributional similarity mean two words have the same meaning?** No. Shared contexts can connect synonyms, antonyms and topical associates. The representation summarizes a corpus and objective; downstream labels or evaluation determine whether a similarity is useful.""",
        """**Interview: Why can rare pairs have misleading PMI?** The ratio can be large when the independence expectation is tiny, even with very little observed evidence. Frequency thresholds or smoothing can improve stability, but they change the estimator and should be validated.""",
        """**Interview: Is a truncated SVD embedding a transformer?** No. It is a matrix factorization of a fixed count-derived representation. It has no contextual attention layers or learned token-by-token encoder, although it is a useful classical baseline.""",
    ],
    [
        "[Mikolov and colleagues, word representations](https://arxiv.org/abs/1301.3781)",
        "[scikit-learn matrix decomposition overview](https://scikit-learn.org/stable/modules/decomposition.html)",
    ],
)
