# nlp-011: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Extract raw spans

The match positions come from the unchanged source. Storing only the surface text would lose provenance and make repeated names ambiguous. The expected intervals use code-point offsets and a half-open end, so text[start:end] reproduces each mention. This invariant should remain even if a learned model later proposes the spans.

**Expected:** Exact spans [0,3),[11,20),[24,29) and correct PER/ORG/LOC types.

## Exercise 2: Handle overlap and repetition

Longest-first alternation resolves one local overlap under a nonoverlapping matching policy. Repeated surface forms remain separate mentions because their offsets differ. Neither operation performs entity linking or coreference. A nested-entity task would require returning both compatible spans and changing evaluation accordingly.

**Expected:** Longer organization wins; repeated Ada mentions occupy [0,3) and [8,11).

## Exercise 3: Treat names as data

The plus signs are part of the organization surface. re.escape prevents them from changing regex repetition semantics. Empty alternatives would match zero-length positions and are rejected before compilation. This is an input-contract test, not a general guarantee against every pathological regex because the pattern here is constructed only from escaped literals.

**Expected:** C++ Labs occupies [0,8); empty names raise a clear error.

## Exercise 4: Compute entity metrics

The partial Acme span is not equal to Acme Labs, so it contributes a false positive and leaves the gold organization as a false negative. Paris adds another false negative. Set comparison avoids awarding duplicate predictions extra credit. State the empty-denominator convention if extending the evaluator.

**Expected:** TP=1,FP=1,FN=2,precision=.5,recall=1/3,F1=.4.

## Exercise 5: Extract directed relations

The grammar deliberately recognizes only one unambiguous surface form. Named groups preserve role direction and raw spans. Fullmatching prevents a rumor prefix from being silently discarded. This raises precision on the authored contract at the cost of recall for paraphrases, which is a measured tradeoff rather than a hidden capability claim.

**Expected:** Roles reverse exactly; negation and rumor-prefixed sentences abstain.

## Exercise 6: Review coreference and scope

Both names are plausible antecedents without more context, and syntactic proximity is not a reliable semantic proof. The correct record preserves the sentence and uncertainty. A coreference model can propose candidates, but a domain pipeline needs an abstention or review policy and evaluation on ambiguous examples before promoting a proposal to an established relation.

**Expected:** A written ambiguity record identifies Ada/Bea candidates and withholds a confirmed person-organization relation.

## Transfer and limits

An extraction system turns selected pieces of text into structured records. The useful output is not merely a word that looks like a name: it is an entity type, a source location, an identity policy and enough evidence for a reviewer to verify the claim. The unit of analysis here is a typed span in a particular raw document. Two identical names at different positions are different mentions; they may or may not refer to the same real entity.

Named-entity recognition identifies spans such as people, organizations or locations. Entity linking associates a mention with a canonical entity in a knowledge base. Coreference groups mentions referring to the same entity within or across text. Relation extraction identifies a typed relationship between mentions or linked entities. These tasks build on one another but are not interchangeable.

The executable system is an explicitly limited dictionary matcher plus a strict relation grammar over authored examples. It does not claim the general linguistic capability of a trained NER or relation model. Its narrow scope is useful because offsets, overlap, direction, negation and evaluation errors can be inspected exactly before replacing a component with a more flexible model.

## Mechanism review and counterexample

Exact entity precision divides correctly recovered typed spans by predicted typed spans. Recall divides by gold spans. A boundary error can count as both a false positive and false negative even when most tokens match. Relaxed overlap metrics can be useful diagnostics, but they answer a different question and must be labeled separately.

The fixture has three gold entities and two predictions, only one exact. That gives TP=1, FP=1, FN=2, precision=1/2, recall=1/3 and F1=2/(2+1+2)=0.4. Do not report token accuracy as if it measured correct entity extraction. Also inspect errors by type and span length, since short common names can dominate a pooled score.
