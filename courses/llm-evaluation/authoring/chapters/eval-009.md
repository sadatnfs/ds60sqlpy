## A citation marker is not an entailment judgment

An answer may cite a real document while making an unsupported claim. It may also faithfully repeat a false or outdated statement from that document. Evaluation therefore needs several distinct questions: is the answer correct for the task, does each citation support its associated claim, are important claims supported, and was the source available and authorized when the answer was produced?

The Research Support Desk's evidence ledger identifies a claim, a document version and a support label. A claim may need multiple passages jointly, and a passage may support only one part of a compound claim. Splitting an answer into atomic claims is itself an annotation procedure requiring a rubric. The code uses authored atomic claims and authored support labels so that no model is secretly serving as an unquestioned judge.

Define link precision as supported citation links divided by evaluated citation links, and claim coverage as claims with at least one supported link divided by eligible claims. These quantities have different denominators. A response that cites one claim correctly and leaves nine uncited can have perfect link precision with poor coverage. A response with many irrelevant links can have good coverage but low precision.

## Worked case A: reconstruct the support relation

Three claims have three citation links. Two links are supported, and one claim remains uncited. Link precision and claim coverage are both two thirds in this fixture, but that numerical equality is accidental. Adding an unsupported extra citation changes precision without changing which claims are covered.

{{WORKED_A}}

## Worked case B: evidence timing and truth are separate

A document published after the answer's decision cutoff was not available to that historical system. The source gate rejects it even if its content is now correct. A cited but restricted document fails authorization independently. These checks happen before treating the document as eligible evidence.

The example also allows a support label to be true while the claim's truth label is false. This represents faithful repetition of an incorrect source. Such a case needs source-quality or contradiction analysis; it cannot be diagnosed by counting citation markers or support labels alone.

{{WORKED_B}}

## What a judge can and cannot establish

A human or model judge may assist with support assessment, but its errors require their own evaluation. Keep claim segmentation, support scoring and final correctness scoring as separate versions. Use blinded, calibrated examples, disagreement analysis and sensitivity checks. A larger judge model is not a proof oracle, and repeated agreement with itself is not independent validation.

When multiple documents disagree, define the authority and time policy explicitly. Current documentation may supersede an earlier policy; a corrected table may revise a published metric. A provenance record should retain the content digest or version, passage boundaries and retrieval time. A bare URL can later resolve to different text and cannot reconstruct a historical answer on its own.

## Diagnose citation failures

Start with one claim and inspect its exact supporting passage. Check whether the passage states the relevant value, unit, time range and population. A passage about annual revenue does not support a claim about monthly profit merely because both mention the same company. A cited denominator may also differ from the denominator in the question.

Count missing or unjudged support relations separately from negative labels. The helper refuses links for which the fixture has no support judgment. This is deliberately strict: replacing unknown with false or true would silently change the metric's meaning. A real study can use a sampling design for citation assessment, but must then account for that sampling in its estimates.

The offline programs test evidence identity and arithmetic only. They do not read arbitrary websites, run an entailment model or certify the truth of real documents. A deployment packet should preserve the authorized corpus snapshot, claim ledger, support judgments, unresolved contradictions and critical failures alongside its aggregate scores.
