from author import author

solution17 = r"""
from collections import Counter
import math

def ngrams(tokens,n):
    if n<1:raise ValueError("positive n required")
    return Counter(tuple(tokens[i:i+n]) for i in range(max(0,len(tokens)-n+1)))

def clipped_precision(candidate,reference,n=1):
    c=ngrams(candidate,n);r=ngrams(reference,n);total=sum(c.values())
    return sum(min(count,r[gram]) for gram,count in c.items())/total if total else 0.

def teaching_bleu(candidate,reference,max_order=2):
    if not candidate:return 0.
    p=[clipped_precision(candidate,reference,n) for n in range(1,max_order+1)]
    if any(value==0 for value in p):return 0.
    bp=min(1.,math.exp(1-len(reference)/len(candidate)))
    return bp*math.exp(sum(math.log(value) for value in p)/max_order)

def lcs_length(a,b):
    table=[[0]*(len(b)+1) for _ in range(len(a)+1)]
    for i,x in enumerate(a,1):
        for j,y in enumerate(b,1):table[i][j]=table[i-1][j-1]+1 if x==y else max(table[i-1][j],table[i][j-1])
    return table[-1][-1]

def main():
    assert clipped_precision("the the the the".split(),"the cat".split())==.25
    assert math.isclose(teaching_bleu("the cat".split(),"the cat sat".split()),math.exp(-.5))
    assert teaching_bleu([],"the cat".split())==0.
    reference="service is not ready".split();candidate="service is ready".split()
    lcs=lcs_length(candidate,reference);p=lcs/len(candidate);r=lcs/len(reference)
    assert lcs==3 and p==1 and r==.75 and math.isclose(2*p*r/(p+r),6/7)
    assert "not" in reference and "not" not in candidate # human-readable contradiction case, not a general entailment detector
    cases=[{"family":"a","supported":True},{"family":"a","supported":False},{"family":"b","supported":False}]
    family_rates=[sum(c['supported'] for c in cases if c['family']==f)/sum(c['family']==f for c in cases) for f in ['a','b']]
    assert family_rates==[.5,0.] and sum(family_rates)/2==.25
    assert lcs_length([],reference)==0
    print("nlp-017: clipped precision=.25; brevity penalty; high-overlap contradiction; family aggregation passed")

if __name__ == "__main__":
    main()
"""
author(
    17,
    """Generated language often has many acceptable answers, so evaluation cannot rely on one exact string. Translation can use synonyms, a summary can select different useful details, and a domain assistant may correctly abstain when evidence is missing. A metric must be chosen for the task and must not receive a stronger interpretation than its calculation supports.

This lesson implements transparent overlap calculations and an exact longest-common-subsequence dynamic program. The BLEU function is explicitly a single-reference, unsmoothed, sentence-level teaching variant with a chosen maximum n-gram order. It is not advertised as a drop-in implementation of a corpus benchmark. The examples expose why high overlap can coexist with a serious factual contradiction.

Separate surface similarity, semantic similarity, source support and user usefulness. A learned semantic metric can recognize paraphrases better than exact overlap, but it is itself a model with training data and failure modes. A model judge adds a rubric and another inference process, not an automatic ground-truth oracle.""",
    [
        (
            "Derive clipped n-gram precision and brevity",
            """An n-gram is a consecutive sequence of n tokens. Modified precision counts candidate n-grams but clips each count to the number available in the reference. If the candidate repeats the four times while the reference contains it once, only one occurrence earns credit. Without clipping, repetition could inflate precision without adding useful content.

The teaching BLEU score combines precision at orders one through N through a geometric mean, then multiplies a brevity penalty. For candidate length c and reference length r, BP=min(1,exp(1-r/c)) when c>0. A short candidate can have perfect local precision by omitting difficult content; the penalty discourages that shortcut. An empty candidate returns zero under our explicit convention.

Zero precision at one included order makes the unsmoothed geometric mean zero. Real benchmark implementations use defined corpus aggregation, tokenization, multiple-reference and smoothing conventions. Report the complete configuration when comparing published scores. Averaging this toy sentence score is not automatically equivalent to corpus BLEU.""",
        ),
        (
            "ROUGE, subsequences and semantic failure",
            """Recall-oriented overlap asks how much reference content is recovered. ROUGE-N variants count n-gram overlap, while ROUGE-L uses longest common subsequence structure. A subsequence preserves order but can skip tokens; it differs from a contiguous substring. Dynamic programming compares prefixes and reuses smaller longest-subsequence results.

For reference service is not ready and candidate service is ready, the longest common subsequence has length three. Precision is one, recall three-quarters and the symmetric F1 is six-sevenths. Yet removing not reverses the central assertion. The metric is behaving exactly as defined while missing the task\'s most important error.

A semantic metric may reduce sensitivity to paraphrases, but it can still overlook negation, numbers, names or domain-specific qualifications. Evaluate these minimal pairs deliberately. Do not use one average score to erase a known catastrophic error category merely because most words match.""",
        ),
        (
            "Human and model judgments as measured instruments",
            """A human rubric should name observable criteria such as factual support, required content, numerical accuracy, citation validity and appropriate abstention. Include examples of borderline cases and preserve independent ratings before adjudication. Blind system identity and randomize response order when comparing alternatives so presentation does not dominate the result.

An LLM judge must be evaluated against representative expert or executable checks. It may prefer longer answers, share the generator\'s misconception or be manipulated by text inside the answer. Treat the candidate response as data to score, not as instructions to change the rubric. A judge explanation is an artifact to inspect, not proof that its rating is correct.

Sampling units matter. Several paraphrases of the same source question are correlated. Report case-family results and use family-level resampling when that matches the generalization target. Tuning prompts or metrics repeatedly on final evaluation cases turns them into development data. Preserve a genuinely held-out acceptance set and record the evaluator version.""",
        ),
        (
            "An end-to-end review of a generated status summary",
            """Suppose a source says a service is not ready and a repair is scheduled. A generated summary says the service is ready after repair. It shares many words, sounds coherent and could receive a favorable generic fluency score. A task-specific review identifies an unsupported completion claim and a reversed readiness state.

The evaluation packet should retain the source snapshot, generated text, atomic claims, support judgments and scoring rationale. A correction should target the failure mechanism, such as evidence interpretation or instruction following, and be retested on new related cases. Improving the overlap score alone is not a repair for the unsupported claim.""",
        ),
    ],
    [
        (
            "Prevent repetition from earning extra credit",
            """Candidate the the the the has four unigram occurrences, while reference the cat contains only one matching the. Clipping gives one match out of four and precision 0.25. This counterexample verifies the count mechanism independently of a complete metric implementation.""",
        ),
        (
            "Penalize a truncated exact prefix",
            """Candidate the cat matches both its unigrams and its one bigram in reference the cat sat, so both precisions are one. Its length is two versus three, giving BP=exp(-0.5) and the same final teaching BLEU score, about 0.60653. Perfect local overlap did not recover all reference content.""",
        ),
        (
            "Keep a high-scoring contradiction visible",
            """The candidate service is ready gets ROUGE-L-style F1 six-sevenths against service is not ready, yet reverses the meaning. The reference records this explicit human-understandable failure. It does not pretend that searching for the token not is a general factuality evaluator.""",
        ),
    ],
    [
        (
            "Implement clipped precision",
            "Count unigram overlap for the repeated-the candidate.",
            "Precision .25, not1.",
            "Clip each candidate count by its reference count.",
            "Only one occurrence of the can be credited because the reference contains one. The remaining repetitions contribute to the denominator without extra matches. This prevents a simple repetition exploit but does not make overlap a semantic metric.",
        ),
        (
            "Derive the brevity penalty",
            "Score the cat against the cat sat with maximum order2 and no smoothing.",
            "Both precisions1; BP and score exp(-.5).",
            "Candidate length is2 and reference length3.",
            "The geometric mean is one because every candidate n-gram appears in the reference. The brevity penalty reduces the result for omitted content. This example isolates length handling from n-gram matching and documents the exact teaching convention.",
        ),
        (
            "Implement longest common subsequence",
            "Compute LCS and P/R/F1 for the readiness minimal pair.",
            "LCS3, precision1, recall.75, F1=6/7.",
            "Compare token prefixes in a dynamic-programming table.",
            "A subsequence can skip not while preserving the other words in order. The resulting high score is mathematically correct under the metric. It demonstrates a limitation of the metric rather than a coding defect to be fixed by changing expected values.",
        ),
        (
            "Document semantic failure",
            "Write a source-support judgment for the same minimal pair.",
            "The candidate contradicts readiness; a high overlap score is retained alongside the failure label.",
            "Identify the atomic status claim and its negation.",
            "The answer changes not ready into ready, reversing the source. A useful evaluator must detect or escalate this error independently of overlap. A handcrafted negation check on this one sentence is not a general entailment model, so its scope must remain explicit.",
        ),
        (
            "Aggregate at the right unit",
            "Use family a outcomes[true,false] and family b outcome[false].",
            "Family rates[.5,0] and equal-family mean.25; explain why row mean1/3 answers a different weighting question.",
            "Decide whether documents, variants or families are the evaluation unit.",
            "Equal-family averaging prevents the family with more variants from receiving more weight merely because it was expanded. Row-level weighting can be appropriate for a different target population, but the choice must be stated. Confidence intervals should preserve the same dependence unit.",
        ),
        (
            "Specify an evaluation packet",
            "Design a rubric and record for a source-grounded generated summary.",
            "Record includes task/source/version/output/atomic support labels/metric config/rater or judge identity and an abstention case.",
            "Separate fluency, overlap, support and usefulness rather than collapsing them silently.",
            "The packet makes both scores and judgments reproducible. It should include unsupported and contradictory examples, preserve disagreements and keep final acceptance families out of prompt tuning. A high average cannot override a critical failure category without an explicit decision rule.",
        ),
    ],
    """
REFERENCE="service is not ready".split()
CANDIDATE="service is ready".split()

def clipped_precision(candidate,reference,n=1):
    raise NotImplementedError("Implement clipped counts and a declared empty policy")

def main():
    print("Overlap and contradiction fixtures loaded. Do not treat a high score as factual support.")

if __name__ == "__main__":
    main()
""",
    solution17,
    [
        """**Interview: Why can two correct summaries have low overlap?** They may choose different valid wording or content granularity. Overlap measures lexical correspondence under a reference convention, not all acceptable meanings.""",
        """**Interview: Why not replace every metric with an LLM judge?** A judge introduces its own biases, domain errors and sensitivity to presentation. Validate it on representative expert or executable checks and retain critical objective tests.""",
        """**Interview: What must accompany a BLEU score?** Tokenization, reference handling, n-gram order, smoothing, corpus/sentence aggregation and evaluation data identity. Otherwise the number may not be comparable.""",
    ],
    [
        "[Papineni and colleagues, BLEU](https://aclanthology.org/P02-1040/)",
        "[Lin, ROUGE](https://aclanthology.org/W04-1013/)",
        "[Sellam and colleagues, BLEURT](https://aclanthology.org/2020.acl-main.704/)",
    ],
)

solution18 = r"""
import unicodedata
import numpy as np

def narrow_language_hint(text):
    words=set(text.lower().split())
    english=len(words & {"the","is"});spanish=len(words & {"el","es"})
    if english==spanish:return None
    return "en" if english>spanish else "es"

def strip_marks(text):
    return "".join(ch for ch in unicodedata.normalize("NFD",text) if unicodedata.category(ch)!="Mn")

def main():
    text="服务正常"
    assert len(text)==4 and len(text.encode("utf-8"))==12 and len(text.split())==1
    assert narrow_language_hint("the service is ready")=="en"
    assert narrow_language_hint("el servicio es correcto")=="es"
    assert narrow_language_hint("bank") is None and narrow_language_hint("the servicio es ready") is None
    assert strip_marks("résumé")=="resume" and "résumé"!="resume"
    assert "İ".lower()=="i\u0307" and len("İ".lower())==2
    assert "Straße".casefold()=="strasse"
    english=np.array([1]*9+[0]);spanish=np.array([1,0])
    pooled=(english.sum()+spanish.sum())/(len(english)+len(spanish))
    macro=(english.mean()+spanish.mean())/2
    assert np.isclose(pooled,5/6) and macro==.7
    print("nlp-018: codepoint/byte/whitespace differences; ambiguous-language abstention; slice metrics passed")

if __name__ == "__main__":
    main()
"""
author(
    18,
    """Multilingual NLP must distinguish language, script, locale, domain and the individual task. A Latin-script message is not automatically English, a short word can belong to several languages, and one document can mix languages. A system that accepts Unicode text may still tokenize, represent and evaluate some languages poorly. Coverage, efficiency and task quality are separate claims.

This lesson uses local strings to inspect encoding lengths, normalization effects, a deliberately narrow language-hint rule and subgroup aggregation. It does not download or claim a multilingual language identifier or translation model. The small rule recognizes only a few authored cue words and explicitly abstains when evidence is tied or absent.

Domain shift can occur within one language as well as across languages. Charge may concern a payment, an electrical battery or an accusation. A model trained on one domain can assign the wrong sense in another while every token is familiar. Evaluate the actual target population and retain uncertainty rather than assuming shared vocabulary implies shared meaning.""",
    [
        (
            "Representation cost is not a language-quality metric",
            """The string 服务正常 has four Unicode code points and twelve UTF-8 bytes, while whitespace splitting returns one item. None of those counts is a universal count of linguistic words or deployed-model tokens. A model tokenizer may split it differently. Context-window and cost comparisons should use the exact tokenizer and a task-matched amount of information.

Tokenization equity concerns whether languages or writing systems require very different token budgets to express comparable content. More tokens can reduce available context or increase cost, but a shorter encoding is not by itself better semantic quality. Compare task performance, latency and token budgets together, and avoid treating translation length as a perfect control for meaning.

Code-point offsets also differ from byte offsets and grapheme boundaries. Combining marks can make one visible letter occupy more than one code point. Preserve original text and explicit offset conventions when multilingual extraction must return evidence spans.""",
        ),
        (
            "Normalization can erase distinctions",
            """Canonical normalization can reconcile equivalent Unicode encodings, but accent stripping and case folding are additional transformations with semantic consequences. Removing marks maps résumé to resume, collapsing distinct English word forms in this example. Casefold maps German Straße to strasse. Standard lowercasing of the single code point İ produces i plus a combining dot, changing code-point length.

These are not reasons to avoid every normalization. They are reasons to choose a policy from the task, retain raw text and keep alignment metadata when offsets matter. Search may intentionally broaden matching, while named-entity extraction or legal text comparison may require preserving distinctions. A global ASCII-cleaning rule is especially inappropriate when it deletes the writing system itself.

Locale-sensitive behavior can differ from a language-neutral Unicode operation. Record the library/runtime and normalization sequence used by a pipeline. A transformation should be tested on representative scripts and edge cases rather than only on English ASCII fixtures.""",
        ),
        (
            "Transfer and evaluation across populations",
            """A language identifier predicts a language label from available evidence; it should have an unknown or mixed-language policy when the task requires one. A script detector answers a different question. The toy cue rule labels the service is ready as English and el servicio es correcto as Spanish, but bank has no evidence and the mixed cue sentence produces a tie. Those abstentions are correct under its narrow contract.

Cross-lingual transfer may use multilingual pretraining, parallel data, translated supervision or aligned embeddings. Each introduces assumptions about label meaning and representation equivalence. A translated benchmark can preserve translation artifacts rather than the real distribution of user text. Have qualified reviewers inspect label and rubric equivalence, especially for sentiment, politeness, entities and culturally specific categories.

Report performance by language/domain and enough information about sample size. In the fixture, English accuracy is 0.9 on ten cases and Spanish accuracy 0.5 on two. Pooled accuracy is 10/12, about .8333, while equal-language macro accuracy is .7. Neither is universally correct; they correspond to different population weights. The pooled number hides the weaker small-language slice if reported alone.""",
        ),
        (
            "A domain-shift investigation",
            """Suppose a classifier trained on payment complaints flags every message containing charge as billing-related. Battery charge is low exposes a new sense. Inspect source domain, tokenization, context and label definitions before deciding whether to adapt weights. A prompt, retrieval context or a small supervised adaptation can address different failure mechanisms, but each needs held-out target-domain cases.

Keep source and target data identities, annotate ambiguous examples and evaluate whether an abstention fallback is preferable to confident misclassification. Do not infer a person\'s nationality or demographic traits from the language or name in a message. The task is processing the text under a declared contract.""",
        ),
    ],
    [
        (
            "Count three different representations",
            """服务正常 has four code points, twelve UTF-8 bytes and one whitespace-separated segment. The mismatch demonstrates why word, character, byte and model-token counts should not be used interchangeably. The code checks only these literal representations, not a linguistic segmentation claim.""",
        ),
        (
            "Observe a lossy transformation",
            """Accent stripping maps résumé to resume. Lowercasing İ yields two code points, i and a combining dot, while casefolding Straße gives strasse. An offset or exact-match pipeline must account for those changes rather than applying old positions to transformed text.""",
        ),
        (
            "Compare slice and pooled metrics",
            """Nine of ten English examples and one of two Spanish examples are correct. Pooled accuracy is five-sixths, but the equally weighted language mean is .7. The small Spanish sample also has much greater uncertainty. Report counts and slice results so a favorable aggregate cannot obscure the limitation.""",
        ),
    ],
    [
        (
            "Measure representation units",
            "Count code points, UTF-8 bytes and whitespace segments for the supplied Chinese string.",
            "Counts4,12,1 respectively, with no claim that whitespace identifies linguistic words.",
            'Use len(text),len(text.encode("utf-8")) and len(text.split()) separately.',
            "Each count measures a different object. A model's tokenizer is another transformation and must be measured directly when context budgets matter. The example prevents a common mistake of comparing languages using an English-specific whitespace definition.",
        ),
        (
            "Retain ambiguous language",
            "Implement the narrow cue rule and test English,Spanish,bank and the mixed cue sentence.",
            "en,es,None,None under the declared cue inventory.",
            "Ties and zero evidence should abstain.",
            "The rule has no general language-model capability. Its explicit unknown output is preferable to inventing a label from a short ambiguous string. A production identifier requires broader data and a confidence/mixture policy validated for the intended text lengths and domains.",
        ),
        (
            "Trace normalization loss",
            "Apply mark removal to résumé and compare with the original resume string.",
            "Both transformed strings equal resume although raw strings differ.",
            "Separate canonical normalization from intentionally deleting marks.",
            "The transformation can help broad search but destroys a distinction. Preserve raw values and state the purpose. Treating this as universally harmless cleaning can create incorrect merges, labels or evidence spans.",
        ),
        (
            "Check length-changing case operations",
            "Inspect lowercased İ and casefolded Straße.",
            "i plus combining dot has length2; Straße casefolds to strasse.",
            "Print repr and code points rather than relying only on appearance.",
            "A visible character can map to multiple code points, so indices in the transformed string do not necessarily identify the same raw span. The operation is defined by Unicode/runtime behavior and is not a substitute for a locale-specific linguistic policy.",
        ),
        (
            "Report language slices",
            "Compute pooled and equal-language accuracy from the two sample arrays.",
            "English.9,Spanish.5,pooled5/6,macro.7 with counts10 and2.",
            "Choose weights from the target population, then show the slices.",
            "The pooled result weights English five times as heavily because of sample size. Macro averaging gives each language equal influence. Both need an explicit interpretation and uncertainty; neither justifies extrapolating the two-case Spanish result as a precise population rate.",
        ),
        (
            "Design target-domain evidence",
            "Analyze charge in payment versus battery messages and propose a held-out transfer evaluation.",
            "A plan includes target labels, ambiguous cases, source/target family separation and an abstention policy.",
            "Identify whether the failure comes from meaning, representation or missing knowledge.",
            "Shared spelling does not guarantee shared semantics. A useful adaptation experiment starts with reviewed target-domain examples and a baseline, then changes the implicated component. Evaluate regressions in the original domain and avoid using the final target test set for repeated prompt or weight tuning.",
        ),
    ],
    """
TEXT="服务正常"
PROBES=["the service is ready","el servicio es correcto","bank","the servicio es ready"]

def language_hint(text):
    raise NotImplementedError("Implement only the declared cue rule with abstention")

def main():
    print("Unicode and domain-shift fixtures loaded. Preserve raw strings and unknown outcomes.")

if __name__ == "__main__":
    main()
""",
    solution18,
    [
        """**Interview: Does Unicode support imply multilingual quality?** It establishes an encoding capability. Tokenization efficiency, representation learning, label validity and task performance require separate evidence.""",
        """**Interview: Why can a language-neutral normalization be harmful?** It can erase accents, change length or collapse forms important to the task. Preserve raw text and choose transformations from the intended use.""",
        """**Interview: Which is better, pooled or macro accuracy?** They weight populations differently. Choose the target weighting deliberately and report slice counts and uncertainty so neither aggregate hides a critical weakness.""",
    ],
    [
        "[Unicode normalization standard](https://www.unicode.org/reports/tr15/)",
        "[Jurafsky and Martin, multilingual language processing](https://web.stanford.edu/~jurafsky/slp3/)",
    ],
)

solution19 = r"""
import numpy as np
from sklearn.metrics import cohen_kappa_score

def binary_agreement(a,b):
    a=np.asarray(a);b=np.asarray(b)
    if a.shape!=b.shape or a.ndim!=1 or not a.size or np.any((a!=0)&(a!=1)) or np.any((b!=0)&(b!=1)):
        raise ValueError("equal nonempty binary label arrays required")
    observed=float(np.mean(a==b))
    expected=float(a.mean()*b.mean()+(1-a.mean())*(1-b.mean()))
    return observed,None if expected==1 else (observed-expected)/(1-expected)

def entropy(probability):
    p=np.asarray(probability,dtype=float)
    if np.any((p<0)|(p>1)):raise ValueError("probabilities required")
    out=np.zeros_like(p);mask=(p>0)&(p<1)
    out[mask]=-p[mask]*np.log(p[mask])-(1-p[mask])*np.log(1-p[mask])
    return out

def main():
    a=np.array([1,1,0,0,1,0]);b=np.array([1,0,0,0,1,1])
    observed,kappa=binary_agreement(a,b)
    assert np.isclose(observed,2/3) and np.isclose(kappa,1/3)
    assert np.isclose(kappa,cohen_kappa_score(a,b))
    first=np.array([1]*99+[0]);second=np.array([1]*98+[0,1])
    high,k=binary_agreement(first,second)
    assert high==.98 and k<0
    ratings=np.array([[1,1,0],[1,1,1],[0,0,0]])
    soft=ratings.mean(axis=1)
    assert np.allclose(soft,[2/3,1,0]) and entropy(soft)[0]>0 and np.all(entropy(soft)[1:]==0)
    original=tuple(int(x) for x in ratings[0])
    adjudication={"item_id":"a","original_ratings":original,"final_label":1,"reason":"rubric criterion C with quoted evidence"}
    assert adjudication["original_ratings"]==(1,1,0) and len(adjudication["reason"])>0
    assert binary_agreement([1,1],[1,1])==(1.,None)
    print("nlp-019: manual/library kappa; prevalence counterexample; soft labels and preserved adjudication passed")

if __name__ == "__main__":
    main()
"""
author(
    19,
    """Labels are measurements created by people, rules or models under an annotation contract. They are not automatically error-free truth. A sentiment label can depend on whose sentiment is being described, an entity boundary can depend on a corpus convention, and an urgency label can depend on an operational threshold. Improving a model before clarifying the label can optimize the wrong target more efficiently.

An annotation guide should define the unit, label inventory, inclusion/exclusion rules, ambiguous cases and an abstention or uncertainty policy. It should include counterexamples, not only easy positive examples. Annotators need the same source context that the eventual task requires, and that context must not contain information unavailable at the intended prediction time.

This lesson calculates agreement, preserves disagreement through soft labels and demonstrates an auditable adjudication record. The examples use invented binary judgments to expose mathematical behavior. Agreement measures consistency among raters under a procedure; they do not establish that the procedure measures the right construct.""",
    [
        (
            "Derive raw agreement and kappa",
            """Raw agreement is the fraction of items on which two raters assign the same label. Cohen\'s kappa adjusts it relative to agreement expected from the raters\' marginal label frequencies: kappa=(p_o-p_e)/(1-p_e). For binary labels, p_e=p_A*p_B+(1-p_A)*(1-p_B), where p_A and p_B are each rater\'s positive-label fractions.

In the six-item fixture, the raters agree on four items and each uses positive labels half the time. Thus p_o=2/3, p_e=1/2 and kappa=1/3. The program compares this hand calculation with scikit-learn. A negative kappa means observed agreement is below this marginal-frequency baseline, not necessarily that the raters intentionally disagree.

If both raters assign the same single category to every item, p_e=1 and the formula has a zero denominator. The reference returns None for kappa while preserving raw agreement one. This is an explicit undefined-result policy rather than silently returning a misleading numeric score.""",
        ),
        (
            "Prevalence and disagreement need interpretation",
            """A highly imbalanced label distribution can yield high raw agreement and low or negative kappa. In the hundred-item example both raters label 99 items positive, but disagree on two items. Raw agreement is .98 while the chance baseline is .9802, giving slightly negative kappa. The example shows why one statistic cannot summarize annotation quality without the confusion pattern and label prevalence.

Disagreement can arise from unclear instructions, missing context, ambiguous language, expertise differences or a genuinely subjective construct. Investigate examples before deciding to remove annotators or force consensus. High agreement can also occur when everyone follows the same flawed shortcut. External validity and construct definition remain separate questions.

For span or ordinal tasks, binary kappa may not be appropriate. Specify matching tolerance or ordinal distance and choose a measure aligned with that structure. Multiple raters, missing ratings and clustered documents also require methods and uncertainty estimates suited to the annotation design.""",
        ),
        (
            "Adjudication and soft labels",
            """Adjudication creates a final label after review, but the original independent judgments should remain immutable. Store item identity, original ratings, final decision, rationale, evidence and rubric version. Replacing the original disagreement with the final label before calculating agreement would manufacture a misleading consistency result.

A soft label can retain the fraction of raters favoring a class, such as two-thirds for ratings [1,1,0]. It may represent disagreement or uncertainty under the sampled rater population, not necessarily the true probability that the statement is objectively positive. Entropy quantifies dispersion of the binary proportion: zero at unanimous zero/one and larger near one-half.

Training on soft labels can preserve ambiguity, but it also encodes who the annotators were and how they interpreted the task. If labels are used for a safety-critical or operational decision, define how uncertainty affects abstention or review. Do not infer that majority vote is always the correct resolution.""",
        ),
        (
            "Build an annotation study that can improve",
            """Pilot the guide on representative examples, collect independent labels, inspect disagreement and revise ambiguous rules. Keep a record of which cases informed rubric development, then evaluate the revised process on new items. Split by document family when near-duplicate sentences share context.

A language model can propose labels or explanations, but model-assisted annotation changes the measurement process. Human reviewers may anchor on the suggestion, making apparent agreement less independent. Compare assisted and unassisted judgments when the distinction matters, and preserve the proposal separately from the accepted label. The same principle applies to using one model to label data for another model\'s evaluation.""",
        ),
    ],
    [
        (
            "Reproduce a kappa calculation",
            """Rater arrays [1,1,0,0,1,0] and [1,0,0,0,1,1] agree on four of six items. Their positive fractions are both one-half, so chance agreement is one-half and kappa one-third. The reference checks both this derivation and library parity.""",
        ),
        (
            "Inspect a prevalence counterexample",
            """Both hundred-item raters use 99 positive labels, but their one negative labels occur on different items. They agree on 98 percent of items, slightly below the 98.02 percent marginal-frequency baseline. A headline of 98 percent agreement alone would conceal the lack of agreement on the rare negative category.""",
        ),
        (
            "Keep ambiguity and a review trail",
            """Three rating rows [1,1,0],[1,1,1],[0,0,0] yield soft labels [2/3,1,0]. Only the first has positive binary entropy. An adjudicated final label for that first item is stored beside the original tuple and rationale, preserving the fact that the initial measurement was disputed.""",
        ),
    ],
    [
        (
            "Define the annotation unit",
            "Write a binary urgency rubric with a source-context boundary and one ambiguous case.",
            "A concrete unit, two label definitions, abstention/review rule and a counterexample.",
            "Specify what evidence an annotator may use and what the label is intended to measure.",
            "A useful rubric makes disagreement diagnosable. It distinguishes a quoted urgent phrase from an actual urgent request and states how missing context is handled. The exact operational criteria depend on the application; the task is to make them inspectable rather than assume a word has a universal label.",
        ),
        (
            "Calculate agreement manually",
            "Compute raw agreement, marginal expected agreement and kappa for the six-item arrays.",
            "2/3,1/2,1/3 respectively, matching the library.",
            "Count matching positions and each rater's positive fraction separately.",
            "The numerator removes the agreement implied by marginal category usage, while the denominator rescales the remaining possible agreement. Comparing with the independent arithmetic catches a library-call or label-alignment mistake. The statistic still says nothing by itself about construct validity.",
        ),
        (
            "Explain the imbalanced case",
            "Calculate the hundred-item prevalence counterexample.",
            "Raw agreement.98 but kappa slightly below zero.",
            "Both positive fractions are.99, so p_e=.99^2+.01^2.",
            "The raters agree on the common category but disagree on the rare exceptions. The chance-adjusted score reflects that pattern. Inspecting the confusion table and category-specific behavior is more informative than choosing whichever single statistic looks favorable.",
        ),
        (
            "Retain soft labels",
            "Compute proportions and entropy for the three three-rater rows.",
            "Soft labels[2/3,1,0]; positive entropy only for the disputed row.",
            "Handle probabilities zero and one without log-zero warnings.",
            "The proportions summarize this rater panel's judgments. Entropy describes their dispersion, not a calibrated probability of objective truth. A downstream use should preserve that interpretation and consider whether disagreement reflects ambiguity, measurement error or differing legitimate perspectives.",
        ),
        (
            "Preserve adjudication evidence",
            "Create a final-label record without changing the independent ratings.",
            "Original(1,1,0),final label1,rationale and item identity retained.",
            "Keep proposal, independent ratings and final decision as separate fields.",
            "Adjudication resolves a workflow decision while preserving its history. Replacing all raw ratings with the final value would erase the evidence needed to improve the guide or audit consistency. Include the rubric version and source evidence when extending the record.",
        ),
        (
            "Handle undefined agreement",
            "Evaluate two identical all-positive arrays and design a follow-up annotation sample.",
            "Raw agreement1,kappa undefined/None; follow-up includes rare and ambiguous categories.",
            "The denominator is zero when expected agreement is one.",
            "An undefined statistic should remain visible rather than be coerced into perfect reliability. The sample contains no category variation, so it cannot reveal how raters distinguish cases. A better follow-up deliberately includes relevant difficult cases while preserving a separate representative sample for population estimates.",
        ),
    ],
    """
A=[1,1,0,0,1,0]
B=[1,0,0,0,1,1]

def agreement(a,b):
    raise NotImplementedError("Compute observed and marginal-expected agreement with an undefined policy")

def main():
    print("Independent ratings loaded. Preserve them when adding adjudication.")

if __name__ == "__main__":
    main()
""",
    solution19,
    [
        """**Interview: Does high interrater agreement prove valid labels?** It proves consistency under the measured procedure. Raters can share an invalid definition or shortcut, so construct validity and external evidence remain necessary.""",
        """**Interview: Why preserve original labels after adjudication?** They reveal ambiguity and process weaknesses. Replacing them with consensus destroys the data used to measure independent agreement.""",
        """**Interview: What does a soft label mean?** It can summarize rater disagreement under a defined panel. It is not automatically the true probability of a factual class and should be interpreted with the annotation design.""",
    ],
    [
        "[scikit-learn Cohen kappa](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html)",
        "[Jurafsky and Martin, annotation and evaluation](https://web.stanford.edu/~jurafsky/slp3/)",
    ],
)

solution20 = r"""
import numpy as np

def weak_summary(labels):
    a=np.asarray(labels)
    if a.ndim!=2 or not len(a) or np.any(~np.isin(a,[-1,0,1])):raise ValueError("2D weak labels in -1,0,1 required")
    covered=np.any(a!=-1,axis=1)
    conflict=np.any(a==0,axis=1)&np.any(a==1,axis=1)
    positive=np.sum(a==1,axis=1);negative=np.sum(a==0,axis=1)
    votes=np.where(positive>negative,1,np.where(negative>positive,0,-1))
    return covered,conflict,votes

def uncertainty(probabilities):
    p=np.asarray(probabilities,dtype=float)
    if np.any((p<0)|(p>1)) or np.any(~np.isfinite(p)):raise ValueError("finite probabilities required")
    h=np.zeros_like(p);mask=(p>0)&(p<1)
    h[mask]=-p[mask]*np.log(p[mask])-(1-p[mask])*np.log(1-p[mask])
    return h

def diverse_batch(probabilities,families,budget):
    if len(probabilities)!=len(families) or budget<0:raise ValueError("aligned families and nonnegative budget required")
    order=np.argsort(-uncertainty(probabilities),kind="stable")
    selected=[];seen=set()
    for i in order:
        if len(selected)==budget:break
        if families[i] not in seen:selected.append(int(i));seen.add(families[i])
    return selected

def main():
    labels=np.array([[1,1,-1],[0,-1,0],[1,0,-1],[-1,-1,-1]])
    covered,conflict,votes=weak_summary(labels)
    assert covered.tolist()==[1,1,1,0] and conflict.tolist()==[0,0,1,0]
    assert covered.mean()==.75 and conflict.mean()==.25 and votes.tolist()==[1,0,-1,-1]
    assert weak_summary([[1,1,0]])[2].tolist()==[1]
    assert weak_summary([[1,0]])[2].tolist()==[-1] # collapse duplicated rule family
    p=np.array([.5,.6,.95,.1]);families=['a','a','b','c']
    assert np.argsort(-uncertainty(p),kind="stable")[:2].tolist()==[0,1]
    assert diverse_batch(p,families,2)==[0,3] and diverse_batch(p,families,0)==[]
    gold_ids={'g1','g2'};queried_ids={'q1','q2'}
    assert gold_ids.isdisjoint(queried_ids)
    print("nlp-020: coverage=.75,conflict=.25; tie abstention; correlated votes and diverse query selection passed")

if __name__ == "__main__":
    main()
"""
author(
    20,
    """Weak supervision creates noisy training signals from rules, heuristics, databases or model suggestions when full manual annotation is expensive. Active learning chooses which examples to send for labeling next. They address different parts of the data problem: weak supervision expands label supply, while active learning allocates a limited review budget. Neither makes an independently labeled evaluation set unnecessary.

A labeling function can emit class zero, class one or abstain. Abstention means the rule has no applicable evidence under its scope, not that the example belongs to a negative class. Multiple rules can overlap, conflict or share the same underlying cue. Treating three correlated versions of one rule as three independent experts can exaggerate confidence.

The executable reference implements transparent majority voting with tie abstention and uncertainty/diversity selection. It does not implement Snorkel\'s learned label model or claim to estimate rule accuracies from unlabeled data. That distinction keeps the limitations of a simple baseline visible before introducing a probabilistic weak-supervision system.""",
    [
        (
            "Measure coverage and conflict before combining",
            """Coverage is the fraction of examples receiving at least one non-abstaining label. Conflict is the fraction receiving both class-zero and class-one votes. State the denominator: conflict among all examples differs from conflict among covered examples. In the four-row fixture, three rows are covered and one conflicts, giving .75 coverage and .25 overall conflict, or one-third among covered rows.

Majority voting counts positive and negative labels but ignores abstentions. Equal counts return abstain under the declared policy. An all-abstaining row also returns abstain, but its reason differs from a conflict tie. A production ledger should retain both the aggregate label and the underlying rule outputs so these cases can be diagnosed separately.

A high coverage number does not mean high accuracy. A rule can label every example incorrectly, and a conflicting rule can sometimes be the more informative one. Use a reviewed development sample to inspect rule behavior, and reserve independent gold evaluation data for the final model.""",
        ),
        (
            "Correlations and learned label models",
            """Suppose two labeling functions both look for the same urgent keyword and a third uses a different contextual signal. Votes [1,1,0] favor one only because the duplicated cue is counted twice. Collapsing the duplicate family gives [1,0], a tie. This does not prove which label is correct; it exposes dependence in the evidence.

Probabilistic label models attempt to estimate source accuracies and sometimes dependencies under specific assumptions. They can improve over majority voting, but identifiability and model misspecification matter. An LLM-generated label is another noisy source, and repeated prompts to the same model may share errors. Do not assume that more synthetic labels or more agreeing model calls create independent evidence.

If weak labels train a downstream classifier, evaluate the classifier on independently reviewed examples. Agreement with its own labeling functions only measures imitation. Preserve the rule versions and source provenance because a changed heuristic changes the effective training target.""",
        ),
        (
            "Active learning and the sampling bias it creates",
            """Uncertainty sampling selects examples near a current decision boundary, using entropy, margin or another score. For binary probability p, entropy is -p*log(p)-(1-p)*log(1-p), largest at one-half. Uncertainty is model-dependent: a confidently wrong out-of-domain example may never be selected, while noise near the boundary can consume the budget repeatedly.

Diversity constraints can prevent a batch from containing many near-duplicate documents from one family. The reference ranks by entropy and accepts at most one example per family until the budget is filled. This is a simple deterministic selection policy, not an optimal information-gain algorithm. A different task may need representative sampling, rare-class coverage or cost-aware review.

Actively selected labels are not a representative test sample. Evaluating only on queried hard cases can make performance appear worse, while evaluating on chosen easy cases can make it appear better. Keep a separate representative gold set or use an appropriate sampling-aware analysis. Record which examples were selected by which policy at each iteration.""",
        ),
        (
            "A measured weak-to-strong workflow",
            """Start with an annotation guide and a small independent reviewed set. Write labeling functions with narrow documented scopes, inspect coverage/conflict and evaluate their errors. Train a baseline on weak labels, then use uncertainty and diversity to propose a bounded review batch from a pool disjoint from final evaluation. Reviewers should see the source evidence and know whether labels were model-assisted.

After each iteration, retrain and compare on unchanged acceptance cases plus deliberately added regression cases. Measure annotation cost, class coverage and task utility, not only label volume. Stop when the marginal information gain no longer justifies the review effort or when the dominant issue is a label definition or data-collection gap rather than model uncertainty.""",
        ),
    ],
    [
        (
            "Read a weak-label matrix",
            """Rows [1,1,-1],[0,-1,0],[1,0,-1],[-1,-1,-1] produce majority outputs [1,0,-1,-1]. The third row abstains because of a tie and the fourth because no rule applies. Three rows are covered and one conflicts. Keep those reasons distinct.""",
        ),
        (
            "Expose duplicated evidence",
            """Votes [1,1,0] appear to favor class one, but the first two rules may be copies of the same cue. Grouping them as one source yields [1,0], which abstains. Neither result is ground truth; the difference identifies a dependence assumption that a naive vote ignored.""",
        ),
        (
            "Select uncertainty with a family budget",
            """Probabilities [0.5,0.6,0.95,0.1] make the first two examples most uncertain. Both belong to family a, so a one-per-family budget selects indices zero and three instead. The choice trades raw uncertainty for diversity and must be evaluated as a labeling policy, not a final classifier metric.""",
        ),
    ],
    [
        (
            "Compute weak-label diagnostics",
            "Calculate covered and conflicting rows in the supplied matrix.",
            "Coverage.75,overall conflict.25 and conflict among covered1/3.",
            "Define the denominator before reporting a percentage.",
            "Coverage identifies any non-abstaining source, while conflict requires at least one zero and one one. The third row is the only conflict. Reporting .25 or one-third without naming the denominator would make two correct calculations look inconsistent.",
        ),
        (
            "Implement tie-aware voting",
            "Aggregate the four rows without treating -1 as a class vote.",
            "Outputs[1,0,-1,-1].",
            "Compare positive and negative vote counts; tie returns abstain.",
            "Abstentions contribute no class evidence. A tie and no coverage share the output sentinel but should retain different diagnostic flags. A production consumer must not coerce -1 into class zero or a negative array index.",
        ),
        (
            "Inspect source correlation",
            "Compare votes[1,1,0] with collapsed source-family votes[1,0].",
            "Majority1 becomes abstain, with a written explanation of duplicated evidence.",
            "Ask which rules use independent information.",
            "The numerical change shows how repetition of one cue can dominate a naive vote. It does not establish that collapsing is always the best statistical model. A learned label model needs assumptions and validation for source dependence and accuracy.",
        ),
        (
            "Rank uncertainty",
            "Compute binary entropy for probabilities[.5,.6,.95,.1].",
            "Top two uncertainty indices[0,1]; p=.5 has maximum entropy.",
            "Handle p=0 and1 without log-zero warnings.",
            "Entropy measures uncertainty under the current predicted distribution. It does not directly measure expected labeling value or detect every confidently wrong outlier. The selection rule is a heuristic whose behavior should be inspected by class and domain.",
        ),
        (
            "Enforce diversity and budget",
            "Select two examples with families[a,a,b,c], at most one per family.",
            "Selected indices[0,3]; budget0 returns an empty batch.",
            "Walk the uncertainty order and skip already represented families.",
            "The second-most-uncertain item is skipped because its family is already present. Index three is more uncertain than index two, so it fills the second slot. The explicit budget and stable ordering make the policy reproducible, but not universally optimal.",
        ),
        (
            "Protect independent evaluation",
            "Design a weak-label/active-review experiment with disjoint query and gold IDs.",
            "A written split and provenance ledger prevent reviewed pool cases from silently becoming the final acceptance set.",
            "Separate development labels from representative held-out evaluation.",
            "Active selection changes the distribution of labeled examples. A final score on that selected pool answers a different question from expected deployment performance. Keep a representative gold set or use a justified sampling-aware analysis, and record rule/model versions so changes in supervision are auditable.",
        ),
    ],
    """
LABELS=[[1,1,-1],[0,-1,0],[1,0,-1],[-1,-1,-1]]
PROBABILITIES=[.5,.6,.95,.1]
FAMILIES=["a","a","b","c"]

def weak_summary(labels):
    raise NotImplementedError("Keep coverage, conflict and aggregate votes separate")

def main():
    print("Weak-label and query-pool fixtures loaded. Preserve a separate gold evaluation set.")

if __name__ == "__main__":
    main()
""",
    solution20,
    [
        """**Interview: Are many agreeing labeling functions strong evidence?** Only after considering their accuracy and dependence. Several functions can repeat one flawed cue and create a misleading majority.""",
        """**Interview: Can active-learning examples serve as an ordinary test set?** They were selected by a model-dependent policy and are generally not representative. Use independent evaluation or a justified design-aware analysis.""",
        """**Interview: What does the reference omit from a learned weak-supervision system?** It uses transparent voting and diagnostics, not a probabilistic estimate of source accuracy/dependence. A label-model implementation would require additional assumptions and validation.""",
    ],
    [
        "[Ratner and colleagues, Snorkel and weak supervision](https://arxiv.org/abs/1711.10160)",
        "[Settles, Active Learning Literature Survey](https://burrsettles.com/pub/settles.activelearning.pdf)",
    ],
)
